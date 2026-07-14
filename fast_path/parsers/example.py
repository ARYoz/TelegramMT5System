from __future__ import annotations

import re

from fast_path.models import (
    Direction,
    GroupConfig,
    ParsedLeg,
    ParsedSignal,
    TelegramMessage,
    new_signal_ids,
)
from fast_path.parser import StrategyParser

# Example format (replace per real group):
# BUY XAUUSD 0.01 SL 2300 TP 2350
_PATTERN = re.compile(
    r"^(BUY|SELL)\s+([A-Z0-9.]+)\s+([0-9.]+)"
    r"(?:\s+SL\s+([0-9.]+))?"
    r"(?:\s+TP\s+([0-9.]+))?",
    re.IGNORECASE | re.MULTILINE,
)


class ExampleParser(StrategyParser):
    name = "example"

    def parse(
        self, message: TelegramMessage, group: GroupConfig
    ) -> ParsedSignal | None:
        match = _PATTERN.search(message.text.strip())
        if not match:
            return None

        direction = Direction.BUY if match.group(1).upper() == "BUY" else Direction.SELL
        symbol = match.group(2).upper()
        lot = float(match.group(3))
        sl = float(match.group(4)) if match.group(4) else None
        tp = float(match.group(5)) if match.group(5) else None

        signal_id, signal_uuid = new_signal_ids()
        version = group.strategy_version or "1.0"

        return ParsedSignal(
            signal_id=signal_id,
            signal_uuid=signal_uuid,
            provider=group.provider,
            chat_id=group.chat_id,
            strategy=group.strategy or self.name,
            strategy_version=version,
            legs=(ParsedLeg(direction=direction, symbol=symbol, lot=lot, sl=sl, tp=tp),),
            raw_text=message.text,
        )
