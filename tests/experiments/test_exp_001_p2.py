from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    EventKind,
    load_datasets,
)

DATASETS = Path("data/exp-001-p2/datasets-v1.json")
DATASET_SHA256 = "FFE17B73F8072E38358CCFC3AEFCE0F0A36AD8E67F696172A88FBED1FFCBB2CD"


def test_p2_dataset_file_is_frozen() -> None:
    digest = hashlib.sha256(DATASETS.read_bytes()).hexdigest().upper()
    assert digest == DATASET_SHA256


def test_p2_dataset_shape_matches_preregistered_protocol() -> None:
    datasets = load_datasets(DATASETS)

    assert len(datasets) == 5
    assert sum(len(dataset.events) for dataset in datasets) == 240

    for dataset in datasets:
        assert len(dataset.events) == 48
        assert len(dataset.chains) == 12
        assert Counter(chain.family for chain in dataset.chains) == Counter(
            {family: 2 for family in ChainFamily}
        )
        assert all(len(chain.events) == 4 for chain in dataset.chains)


def test_p2_events_are_globally_interleaved() -> None:
    for dataset in load_datasets(DATASETS):
        for chain in dataset.chains:
            positions = [event.stream_position for event in chain.events]
            assert positions == sorted(positions)
            assert all(
                later - earlier >= 2
                for earlier, later in zip(positions, positions[1:], strict=True)
            )


def test_p2_sources_are_balanced_and_memory_types_are_semantic() -> None:
    expected_source_counts = Counter(
        {
            SourceType.JORDAN_INPUT: 16,
            SourceType.EXTERNAL_TOOL: 16,
            SourceType.DEDUCTION: 16,
        }
    )

    for dataset in load_datasets(DATASETS):
        assert Counter(event.source_type for event in dataset.events) == expected_source_counts
        for event in dataset.events:
            expected_memory_type = (
                MemoryType.DEDUCTION
                if event.source_type is SourceType.DEDUCTION
                else MemoryType.RECEIVED_INFORMATION
            )
            assert event.memory_type is expected_memory_type


def test_p2_family_semantics_are_frozen() -> None:
    datasets = load_datasets(DATASETS)

    for dataset in datasets:
        by_family: dict[ChainFamily, list[tuple[EventKind, ...]]] = {}
        for chain in dataset.chains:
            by_family.setdefault(chain.family, []).append(
                tuple(event.kind for event in chain.events)
            )

        assert set(by_family) == set(ChainFamily)
        assert all(len(patterns) == 2 for patterns in by_family.values())

        for chain in dataset.chains:
            if chain.family is ChainFamily.S6_MISLEADING_REWRITE:
                assert chain.misleading_value is not None
            else:
                assert chain.misleading_value is None
