from __future__ import annotations

import logging

from fast_path.builder import OrderBuilder
from fast_path.config import GroupsConfig
from fast_path.models import FastPathResult, FastPathTimings, TelegramMessage, utc_now
from fast_path.order_engine import OrderEngine
from fast_path.parser import ParserRegistry

logger = logging.getLogger(__name__)


class FastPathPipeline:
    """
    Critical path only:
    Telegram message → Parser → Builder → Order Engine → MT5
    """

    def __init__(
        self,
        groups: GroupsConfig,
        parsers: ParserRegistry,
        builder: OrderBuilder,
        engine: OrderEngine,
    ) -> None:
        self._groups = groups
        self._parsers = parsers
        self._builder = builder
        self._engine = engine

    @property
    def engine(self) -> OrderEngine:
        return self._engine

    def run(self, message: TelegramMessage) -> FastPathResult:
        timings = FastPathTimings(telegram_received=message.received_at)

        group = self._groups.get(message.chat_id)
        if group is None:
            return FastPathResult(
                ok=False,
                signal_id=None,
                signal_uuid=None,
                provider=None,
                chat_id=message.chat_id,
                strategy=None,
                timings=timings,
                skip_reason="unknown_chat",
            )

        if not group.enabled:
            return FastPathResult(
                ok=False,
                signal_id=None,
                signal_uuid=None,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=group.strategy,
                timings=timings,
                skip_reason="group_disabled",
            )

        if not group.strategy:
            return FastPathResult(
                ok=False,
                signal_id=None,
                signal_uuid=None,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=None,
                timings=timings,
                skip_reason="no_strategy_assigned",
            )

        try:
            signal = self._parsers.parse(message, group)
        except Exception as exc:
            logger.exception("Parser error provider=%s", group.provider)
            return FastPathResult(
                ok=False,
                signal_id=None,
                signal_uuid=None,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=group.strategy,
                timings=timings,
                error=str(exc),
            )

        timings.parse_done = utc_now()

        if signal is None:
            return FastPathResult(
                ok=False,
                signal_id=None,
                signal_uuid=None,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=group.strategy,
                timings=timings,
                skip_reason="parse_no_match",
            )

        orders = self._builder.build(signal)
        timings.build_done = utc_now()

        if not orders:
            return FastPathResult(
                ok=False,
                signal_id=signal.signal_id,
                signal_uuid=signal.signal_uuid,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=group.strategy,
                timings=timings,
                skip_reason="no_orders_built",
            )

        try:
            sent = self._engine.send_all(orders)
        except Exception as exc:
            logger.exception("Order engine error signal=%s", signal.signal_id)
            return FastPathResult(
                ok=False,
                signal_id=signal.signal_id,
                signal_uuid=signal.signal_uuid,
                provider=group.provider,
                chat_id=message.chat_id,
                strategy=group.strategy,
                timings=timings,
                error=str(exc),
            )

        timings.orders_sent = utc_now()

        ok = any(o.ticket for o in sent)
        return FastPathResult(
            ok=ok,
            signal_id=signal.signal_id,
            signal_uuid=signal.signal_uuid,
            provider=group.provider,
            chat_id=message.chat_id,
            strategy=group.strategy,
            orders=sent,
            timings=timings,
            error=None if ok else "all_orders_failed",
        )
