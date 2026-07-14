from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from fast_path.builder import OrderBuilder
from fast_path.config import GroupsConfig
from fast_path.listener import build_listener
from fast_path.order_engine import OrderEngine
from fast_path.parser import default_registry
from fast_path.pipeline import FastPathPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def build_pipeline() -> FastPathPipeline:
    config_path = os.getenv("GROUPS_CONFIG", "config/groups.json")
    groups = GroupsConfig.load(config_path)
    magic = int(os.getenv("MT5_MAGIC", "20260714"))
    terminal_path = os.getenv("MT5_PATH") or None

    return FastPathPipeline(
        groups=groups,
        parsers=default_registry(),
        builder=OrderBuilder(magic=magic),
        engine=OrderEngine(magic=magic, terminal_path=terminal_path),
    )


async def main() -> None:
    load_dotenv()

    required = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        logger.error("Missing env vars: %s — copy .env.example to .env", ", ".join(missing))
        sys.exit(1)

    pipeline = build_pipeline()
    config_path = os.getenv("GROUPS_CONFIG", "config/groups.json")
    groups = GroupsConfig.load(config_path)
    listener = build_listener(pipeline, groups)

    engine = pipeline.engine
    engine.connect()
    try:
        await listener.start()
    finally:
        engine.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
