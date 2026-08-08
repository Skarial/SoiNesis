"""Objets purs du domaine pour l'estimation de capacités propres."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from soinesis.domain.models import DomainModel, SourceType


class SelfAttributeType(StrEnum):
    """Type minimal d'attribut de soi couvert par la tranche P3 DEV."""

    CAPABILITY = "CAPABILITY"


class EstimateSource(StrEnum):
    """Origine cognitive autorisée d'une estimation de capacité."""

    FIXED_BASELINE = "FIXED_BASELINE"
    RAW_HISTORY = "RAW_HISTORY"
    SELF_ATTRIBUTE = "SELF_ATTRIBUTE"


class CapabilityAction(StrEnum):
    """Stratégies disponibles pour agir selon une capacité estimée."""

    DIRECT = "DIRECT"
    VERIFY = "VERIFY"
    HELP = "HELP"


class CapabilityPerformanceObservation(DomainModel):
    """Preuve brute d'une performance autonome déjà observée."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    intrinsic_success: bool = Field(strict=True)
    observed_at: datetime
    source_type: SourceType


class MetacognitiveCapabilityState(DomainModel):
    """État statistique de travail, distinct du SelfModel consolidé."""

    alpha: float = Field(gt=0.0, allow_inf_nan=False)
    beta: float = Field(gt=0.0, allow_inf_nan=False)
    lambda_: float = Field(gt=0.0, le=1.0, allow_inf_nan=False)

    @property
    def estimated_success(self) -> float:
        """Retourner la moyenne courante de la distribution Beta."""
        return self.alpha / (self.alpha + self.beta)


class CapabilitySelfAttribute(DomainModel):
    """Représentation consolidée minimale d'une capacité dans le SelfModel."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    attribute_type: SelfAttributeType = SelfAttributeType.CAPABILITY
    capability_key: str = Field(min_length=1)
    estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)


class CapabilityEstimate(DomainModel):
    """Estimation publique fournie à la politique de décision."""

    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    source: EstimateSource


class CapabilityDecision(DomainModel):
    """Décision et utilités calculées depuis une estimation autorisée."""

    estimate: CapabilityEstimate
    action: CapabilityAction
    direct_utility: float = Field(allow_inf_nan=False)
    verify_utility: float = Field(allow_inf_nan=False)
    help_utility: float = Field(allow_inf_nan=False)
