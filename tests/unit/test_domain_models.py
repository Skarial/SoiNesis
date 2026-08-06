from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from soinesis.domain.models import MemoryType, Observation, SourceType


def test_received_information_is_not_direct_experience() -> None:
    with pytest.raises(ValidationError):
        Observation(
            id="observation_1",
            agent_id="agent_1",
            cycle_id="cycle_1",
            source_type=SourceType.JORDAN_INPUT,
            raw_content="Le projet s'appelle SoiNesis.",
            received_at=datetime(2026, 8, 6, tzinfo=UTC),
            confidence=1.0,
            is_direct_experience=True,
        )


def test_memory_type_values_are_explicit() -> None:
    assert MemoryType.RECEIVED_INFORMATION.value == "RECEIVED_INFORMATION"
