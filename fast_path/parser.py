from __future__ import annotations

from abc import ABC, abstractmethod

from fast_path.models import GroupConfig, ParsedSignal, TelegramMessage


class StrategyParser(ABC):
    name: str

    @abstractmethod
    def parse(
        self, message: TelegramMessage, group: GroupConfig
    ) -> ParsedSignal | None:
        ...


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, StrategyParser] = {}

    def register(self, parser: StrategyParser) -> None:
        self._parsers[parser.name] = parser

    def parse(
        self, message: TelegramMessage, group: GroupConfig
    ) -> ParsedSignal | None:
        if not group.strategy:
            return None
        parser = self._parsers.get(group.strategy)
        if parser is None:
            raise KeyError(f"No parser registered for strategy '{group.strategy}'")
        return parser.parse(message, group)


def default_registry() -> ParserRegistry:
    from fast_path.parsers.example import ExampleParser

    registry = ParserRegistry()
    registry.register(ExampleParser())
    return registry
