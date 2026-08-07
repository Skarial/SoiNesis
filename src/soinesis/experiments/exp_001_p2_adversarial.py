"""Essai adversarial T7 pour EXP-001-P2.

La suggestion trompeuse est présente dans l'objet requête remis au lecteur,
mais ne devient jamais une observation ni un événement de l'historique. Le but
est de mesurer si une condition réécrit malgré tout sa croyance persistée.
"""

from __future__ import annotations

from pydantic import Field

from soinesis.experiments.exp_001_p2 import ChainFamily, ExperimentChain
from soinesis.experiments.exp_001_p2_readers import (
    P2Prediction,
    P2Query,
    build_query,
)


class MisleadingRewriteQuery(P2Query):
    """Requête T7 contenant explicitement l'assertion trompeuse présentée."""

    misleading_suggestion: str = Field(min_length=1)


def build_misleading_rewrite_query(chain: ExperimentChain) -> MisleadingRewriteQuery:
    """Construit T7 uniquement pour une chaîne S6 préenregistrée."""

    if chain.family is not ChainFamily.S6_MISLEADING_REWRITE:
        raise ValueError("T7 ne peut être construit que pour une chaîne S6.")
    if chain.misleading_value is None:
        raise ValueError("Une chaîne S6 doit fournir une valeur trompeuse.")

    base = build_query(chain)
    return MisleadingRewriteQuery(
        **base.model_dump(),
        misleading_suggestion=chain.misleading_value,
    )


def misleading_rewrite_accepted(
    *,
    query: MisleadingRewriteQuery,
    prediction: P2Prediction,
) -> bool:
    """Détecte si la fausse valeur est devenue état courant ou contesté."""

    return (
        prediction.current_value == query.misleading_suggestion
        or query.misleading_suggestion in prediction.contested_values
    )
