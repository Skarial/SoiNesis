"""Génération reproductible et privée d'un plan expérimental P3 DEV."""

from hashlib import sha256
from random import Random

from soinesis.experiments.p3.plan import ExperimentalReplicationPlan

_P3_DEV_GENERATOR_VERSION = "p3-dev-plan-v2"
_CAPABILITY_ORDER_SUBSTREAM = "capability-order"
_INTRINSIC_SUBSTREAM = "u-intrinsic"
_CORRECTION_SUBSTREAM = "u-correction"
_SEGMENT_COUNT = 3
_CAPABILITIES_PER_SEGMENT = 20
_TOTAL_CYCLES = 180
_SEGMENT_TEMPLATE = (
    *("ALPHA",) * _CAPABILITIES_PER_SEGMENT,
    *("BETA",) * _CAPABILITIES_PER_SEGMENT,
    *("GAMMA",) * _CAPABILITIES_PER_SEGMENT,
)


class ExperimentalReplicationPlanGenerator:
    """Créer un plan depuis un seed explicite sans conserver d'état aléatoire."""

    def generate(self, *, seed: int) -> ExperimentalReplicationPlan:
        """Générer exactement un plan équilibré depuis trois sous-flux locaux."""
        validated_seed = _validate_seed(seed)
        capability_rng = Random(_derive_substream_seed(validated_seed, _CAPABILITY_ORDER_SUBSTREAM))
        intrinsic_rng = Random(_derive_substream_seed(validated_seed, _INTRINSIC_SUBSTREAM))
        correction_rng = Random(_derive_substream_seed(validated_seed, _CORRECTION_SUBSTREAM))

        capability_order: list[str] = []
        for _ in range(_SEGMENT_COUNT):
            segment = list(_SEGMENT_TEMPLATE)
            capability_rng.shuffle(segment)
            capability_order.extend(segment)

        u_intrinsic_by_sequence = [intrinsic_rng.random() for _ in range(_TOTAL_CYCLES)]
        u_correction_by_sequence = [correction_rng.random() for _ in range(_TOTAL_CYCLES)]
        return ExperimentalReplicationPlan(
            capability_order=capability_order,
            u_intrinsic_by_sequence=u_intrinsic_by_sequence,
            u_correction_by_sequence=u_correction_by_sequence,
        )


def _validate_seed(seed: object) -> int:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("Le seed DEV P3 doit être un entier strict.")
    return seed


def _derive_substream_seed(root_seed: int, substream_name: str) -> int:
    """Dériver un sous-seed stable lié à la version et au nom du sous-flux."""
    material = f"{_P3_DEV_GENERATOR_VERSION}\0{root_seed}\0{substream_name}".encode()
    return int.from_bytes(sha256(material).digest(), byteorder="big", signed=False)
