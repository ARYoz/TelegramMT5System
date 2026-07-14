from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


class Direction(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class GroupConfig:
    chat_id: int
    provider: str
    strategy: str | None
    strategy_version: str | None
    enabled: bool


@dataclass(frozen=True)
class TelegramMessage:
    chat_id: int
    message_id: int
    text: str
    received_at: datetime


@dataclass(frozen=True)
class ParsedLeg:
    direction: Direction
    symbol: str
    lot: float
    entry: float | None = None
    sl: float | None = None
    tp: float | None = None


@dataclass(frozen=True)
class ParsedSignal:
    signal_id: str
    signal_uuid: str
    provider: str
    chat_id: int
    strategy: str
    strategy_version: str
    legs: tuple[ParsedLeg, ...]
    raw_text: str


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    direction: Direction
    lot: float
    sl: float | None
    tp: float | None
    magic: int
    comment: str
    signal_id: str
    signal_uuid: str
    provider: str
    leg_index: int


@dataclass
class SentOrder:
    request: OrderRequest
    ticket: int | None
    retcode: int | None
    error: str | None = None


@dataclass
class FastPathTimings:
    telegram_received: datetime
    parse_done: datetime | None = None
    build_done: datetime | None = None
    orders_sent: datetime | None = None


@dataclass
class FastPathResult:
    ok: bool
    signal_id: str | None
    signal_uuid: str | None
    provider: str | None
    chat_id: int | None
    strategy: str | None
    orders: list[SentOrder] = field(default_factory=list)
    timings: FastPathTimings | None = None
    skip_reason: str | None = None
    error: str | None = None

    def to_smart_path_payload(self) -> dict[str, Any]:
        """Minimal payload handed off AFTER all orders are sent."""
        return {
            "ok": self.ok,
            "signal_id": self.signal_id,
            "signal_uuid": self.signal_uuid,
            "provider": self.provider,
            "chat_id": self.chat_id,
            "strategy": self.strategy,
            "orders": [
                {
                    "ticket": o.ticket,
                    "symbol": o.request.symbol,
                    "direction": o.request.direction.value,
                    "lot": o.request.lot,
                    "sl": o.request.sl,
                    "tp": o.request.tp,
                    "comment": o.request.comment,
                    "magic": o.request.magic,
                    "retcode": o.retcode,
                    "error": o.error,
                }
                for o in self.orders
            ],
            "timings": {
                "telegram_received": self.timings.telegram_received.isoformat()
                if self.timings
                else None,
                "parse_done": self.timings.parse_done.isoformat()
                if self.timings and self.timings.parse_done
                else None,
                "build_done": self.timings.build_done.isoformat()
                if self.timings and self.timings.build_done
                else None,
                "orders_sent": self.timings.orders_sent.isoformat()
                if self.timings and self.timings.orders_sent
                else None,
            },
            "skip_reason": self.skip_reason,
            "error": self.error,
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_signal_ids() -> tuple[str, str]:
    uid = str(uuid.uuid4())
    return uid[:8], uid
