"""Objets purs du domaine pour l'estimation de capacités propres."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

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


class CapabilityHistoryBoundary(DomainModel):
    """Point public du cycle courant bornant une lecture au passé causal."""

    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    sequence_index: int = Field(ge=0, strict=True)


class CapabilityPerformanceObservation(DomainModel):
    """Preuve brute d'une performance autonome déjà observée."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    sequence_index: int = Field(ge=0, strict=True)
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


class VersionedMetacognitiveCapabilityState(DomainModel):
    """Enveloppe persistable d'un état statistique courant et versionné."""

    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    version: int = Field(ge=1, strict=True)
    state: MetacognitiveCapabilityState


class CapabilitySelfAttribute(DomainModel):
    """Représentation consolidée minimale d'une capacité dans le SelfModel."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    attribute_type: SelfAttributeType = SelfAttributeType.CAPABILITY
    capability_key: str = Field(min_length=1)
    estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    self_model_version_id: str = Field(min_length=1)
    attribute_version: int = Field(ge=1, strict=True)
    previous_attribute_id: str | None = Field(default=None, min_length=1)
    created_at: datetime

    @model_validator(mode="after")
    def validate_version_chain(self) -> CapabilitySelfAttribute:
        """Exiger un prédécesseur exactement après la première version."""
        if self.attribute_version == 1 and self.previous_attribute_id is not None:
            raise ValueError("La première version d'un attribut ne peut pas avoir de prédécesseur.")
        if self.attribute_version > 1 and self.previous_attribute_id is None:
            raise ValueError(
                "Une version ultérieure d'un attribut doit référencer son prédécesseur."
            )
        if self.previous_attribute_id == self.id:
            raise ValueError("Un attribut ne peut pas être son propre prédécesseur.")
        return self


class SelfModelVersion(DomainModel):
    """Version globale logique minimale d'un SelfModel persistant."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    version: int = Field(ge=1, strict=True)
    previous_version_id: str | None = Field(default=None, min_length=1)
    created_at: datetime

    @model_validator(mode="after")
    def validate_version_chain(self) -> SelfModelVersion:
        """Préserver une chaîne append-only cohérente dès le modèle."""
        if self.version == 1 and self.previous_version_id is not None:
            raise ValueError("La première version du SelfModel ne peut pas avoir de prédécesseur.")
        if self.version > 1 and self.previous_version_id is None:
            raise ValueError(
                "Une version ultérieure du SelfModel doit référencer son prédécesseur."
            )
        if self.previous_version_id == self.id:
            raise ValueError("Une version du SelfModel ne peut pas être son propre prédécesseur.")
        return self


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
