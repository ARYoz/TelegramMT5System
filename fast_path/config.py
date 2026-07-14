from __future__ import annotations

import json
from pathlib import Path

from fast_path.models import GroupConfig


class GroupsConfig:
    def __init__(self, groups: dict[int, GroupConfig]) -> None:
        self._groups = groups

    @classmethod
    def load(cls, path: str | Path) -> "GroupsConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        groups: dict[int, GroupConfig] = {}
        for item in data.get("groups", []):
            cfg = GroupConfig(
                chat_id=int(item["chat_id"]),
                provider=str(item["provider"]),
                strategy=item.get("strategy"),
                strategy_version=item.get("strategy_version"),
                enabled=bool(item.get("enabled", True)),
            )
            groups[cfg.chat_id] = cfg
        return cls(groups)

    def get(self, chat_id: int) -> GroupConfig | None:
        return self._groups.get(chat_id)

    def enabled_chat_ids(self) -> list[int]:
        return [g.chat_id for g in self._groups.values() if g.enabled]

    def all_groups(self) -> list[GroupConfig]:
        return list(self._groups.values())
