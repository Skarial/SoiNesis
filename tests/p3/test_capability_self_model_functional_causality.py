from datetime import UTC, datetime, timedelta
from pathlib import Path

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilitySelfModelInitializationService,
    CapabilitySelfModelRevisionService,
    CapabilitySelfModelRevisionStatus,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateService,
    SelfAttributeCapabilityDecisionService,
    SelfAttributeCapabilityEstimateProvider,
    SignificantSelfRevisionPolicy,
)
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
)
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 8, 16, 0, tzinfo=UTC)


class SequentialIdentifiers:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def new(self, prefix: str) -> str:
        next_value = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = next_value
        return f"{prefix}-{next_value}"


def test_performance_to_self_model_to_decision_is_functionally_causal(tmp_path: Path) -> None:
    """La décision C change seulement après consolidation du nouvel attribut."""
    database = SQLiteDatabase(tmp_path / "functional-causality.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    estimator = DecayedBetaEstimator(lambda_=0.9)
    decision_policy = CapabilityDecisionPolicy()
    identifiers = SequentialIdentifiers()
    CapabilitySelfModelInitializationService(
        unit_of_work_factory=factory,
        estimator=estimator,
        clock=FixedClock(),
        identifiers=identifiers,
    ).initialize(agent_id="agent-1", capability_key="ALPHA")
    decision_service = SelfAttributeCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=SelfAttributeCapabilityEstimateProvider(),
        decision_policy=decision_policy,
    )

    with factory() as unit_of_work:
        initial_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    assert initial_attribute is not None
    initial_decision = decision_service.decide(
        boundary=CapabilityHistoryBoundary(
            agent_id="agent-1",
            capability_key="ALPHA",
            trial_id="trial-initial-decision",
            cycle_id="cycle-initial-decision",
            sequence_index=0,
        )
    )
    assert initial_decision.estimate.estimated_success == 0.60
    assert initial_decision.action is CapabilityAction.VERIFY

    update_service = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    )
    observed_at = datetime(2026, 8, 8, 17, 0, tzinfo=UTC)
    for sequence_index in range(7):
        performance = CapabilityPerformanceObservation(
            id=f"performance-{sequence_index}",
            agent_id="agent-1",
            trial_id=f"trial-{sequence_index}",
            cycle_id=f"cycle-{sequence_index}",
            sequence_index=sequence_index,
            capability_key="ALPHA",
            intrinsic_success=True,
            observed_at=observed_at + timedelta(minutes=sequence_index),
            source_type=SourceType.DIRECT_ENVIRONMENT,
        )
        with factory() as unit_of_work:
            unit_of_work.capability_performances.add(performance)
            unit_of_work.commit()
        update_service.process(performance_id=performance.id)

    with factory() as unit_of_work:
        attribute_before_revision = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        meta_before_revision = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    assert attribute_before_revision is not None
    assert attribute_before_revision == initial_attribute
    assert meta_before_revision is not None
    assert meta_before_revision.state.estimated_success >= 0.80
    next_boundary = CapabilityHistoryBoundary(
        agent_id="agent-1",
        capability_key="ALPHA",
        trial_id="trial-next-decision",
        cycle_id="cycle-next-decision",
        sequence_index=7,
    )
    decision_before_revision = decision_service.decide(boundary=next_boundary)
    assert decision_before_revision.estimate.estimated_success == 0.60
    assert decision_before_revision.action is CapabilityAction.VERIFY

    revision = CapabilitySelfModelRevisionService(
        unit_of_work_factory=factory,
        estimator=estimator,
        revision_policy=SignificantSelfRevisionPolicy(decision_policy=decision_policy),
        clock=FixedClock(),
        identifiers=identifiers,
    ).revise(agent_id="agent-1", capability_key="ALPHA")

    with factory() as unit_of_work:
        attribute_after_revision = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    assert revision.status is CapabilitySelfModelRevisionStatus.REVISED
    assert attribute_after_revision is not None
    assert attribute_after_revision != initial_attribute
    decision_after_revision = decision_service.decide(boundary=next_boundary)
    assert (
        decision_after_revision.estimate.estimated_success
        == meta_before_revision.state.estimated_success
    )
    assert decision_after_revision.action is CapabilityAction.DIRECT
