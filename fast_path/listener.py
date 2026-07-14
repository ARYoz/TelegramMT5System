from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

from telethon import TelegramClient, events

from fast_path.config import GroupsConfig
from fast_path.models import TelegramMessage, utc_now
from fast_path.pipeline import FastPathPipeline

logger = logging.getLogger(__name__)


class TelegramListener:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str,
        groups: GroupsConfig,
        pipeline: FastPathPipeline,
    ) -> None:
        self._groups = groups
        self._pipeline = pipeline
        self._client = TelegramClient(session_name, api_id, api_hash)
        self._chat_ids = groups.enabled_chat_ids()

    async def start(self) -> None:
        await self._client.start()
        logger.info("Telegram connected. Listening to %s chats", len(self._chat_ids))

        @self._client.on(events.NewMessage(chats=self._chat_ids))
        async def handler(event: events.NewMessage.Event) -> None:
            text = event.message.message or ""
            if not text.strip():
                return

            message = TelegramMessage(
                chat_id=int(event.chat_id),
                message_id=int(event.message.id),
                text=text,
                received_at=event.message.date or utc_now(),
            )
            if message.received_at.tzinfo is None:
                message = TelegramMessage(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=message.text,
                    received_at=message.received_at.replace(tzinfo=timezone.utc),
                )

            # Fast Path only — hand off to Smart Path after pipeline returns
            result = await asyncio.to_thread(self._pipeline.run, message)
            from smart_path.hook import enqueue_after_send

            asyncio.create_task(enqueue_after_send(result.to_smart_path_payload()))

            if result.ok:
                logger.info(
                    "Fast Path OK signal=%s orders=%s",
                    result.signal_id,
                    len(result.orders),
                )
            elif result.skip_reason:
                logger.debug("Skipped chat=%s: %s", message.chat_id, result.skip_reason)
            else:
                logger.warning("Fast Path failed: %s", result.error)

        await self._client.run_until_disconnected()

    async def stop(self) -> None:
        await self._client.disconnect()


def build_listener(pipeline: FastPathPipeline, groups: GroupsConfig) -> TelegramListener:
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session = os.getenv("TELEGRAM_SESSION", "telegram_mt5")
    return TelegramListener(api_id, api_hash, session, groups, pipeline)
