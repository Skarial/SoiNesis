"""Adaptateurs système par défaut."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidIdentifierGenerator:
    def new(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"
