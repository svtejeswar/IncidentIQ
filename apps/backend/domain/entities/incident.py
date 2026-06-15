from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.value_objects.severity import Severity


@dataclass
class Incident:
    id: UUID
    document_id: UUID
    title: str
    description: str
    root_cause: str | None
    resolution: str | None
    impact: str | None
    preventive_actions: list[str]
    affected_services: list[str]
    severity: Severity
    occurred_at: datetime | None
    created_at: datetime

    @property
    def has_resolution(self) -> bool:
        return bool(self.resolution)

    @property
    def is_high_severity(self) -> bool:
        return self.severity in {Severity.CRITICAL, Severity.HIGH}
