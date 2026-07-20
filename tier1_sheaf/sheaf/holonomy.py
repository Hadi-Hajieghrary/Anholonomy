"""The latency-curvature floor: leading holonomy amplitude  [ES §7], Thm 7.2.

Thm 7.2 (leading order, deterministic — PROV):
    log Hol(gamma_c) = tau^2 * sum_k alpha_k [C_{j_k}, C_{j_{k+1}}] + O(tau^3),
with C_j(s_j; xi) = Ad_{m(s_j)} ad_xi Ad_{m(s_j)}^{-1} the conjugated generator.

EPISTEMIC BOUNDARY (see plan §2, [[anholonomy-floor-epistemic-trap]]):
  * This amplitude ||log Hol|| = O(tau^2) is PROVED and deterministic. It is the
    object E3a measures.
  * The stochastic steady-state disagreement D_ss is a DIFFERENT object, tagged
    CONJ in [ES §10(ii)]. Do NOT identify a D_ss slope with this theorem.
  * The alpha_k are stated as "explicit combinatorial" in [ES] but appear nowhere
    (Q3). At m = 2 the closed-walk product reduces to a single commutator
    (alpha_1 - alpha_2)[C_1, C_2]; the m > 2 coefficients are unresolved. Functions
    here that need alpha_k for m > 2 raise NotImplementedError rather than guess.

Cor 7.3 (symmetry protection — PROV): if all agents on the cycle share the same
shape pair, [C_i, C_j]|_{s_i=s_j} = 0 and the tau^2 term cancels (floor O(tau^3)).
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm, logm

from ..core.shapes import conjugated_generator, commutator, DEFAULT_L

__all__ = [
    "two_agent_commutator", "leading_amplitude_m2", "generators_on_cycle",
    "error_transport_holonomy_m2", "holonomy_amplitude_m2",
]


def generators_on_cycle(shapes, xi, l: float = DEFAULT_L):
    """The conjugated generators C_j for each agent on a cycle."""
    return [conjugated_generator(sig, sigi, xi, l) for (sig, sigi) in shapes]


def two_agent_commutator(shape_i, shape_j, xi, l: float = DEFAULT_L) -> np.ndarray:
    """[C_i, C_j] for two agents under common load twist xi.

    Vanishes iff the two shape pairs give equal conjugated generators (Cor 7.3);
    in particular it vanishes when shape_i == shape_j.
    """
    Ci = conjugated_generator(shape_i[0], shape_i[1], xi, l)
    Cj = conjugated_generator(shape_j[0], shape_j[1], xi, l)
    return commutator(Ci, Cj)


def leading_amplitude_m2(shape_i, shape_j, xi, tau, l: float = DEFAULT_L) -> float:
    """||log Hol|| to leading order for the m = 2 closed walk (there-and-back).

    Uses the unit coefficient (alpha_1 - alpha_2) = 1 pending the author's alpha_k
    table (Q3); if that table differs, scale accordingly. Returns tau^2 * ||[C_i,C_j]||
    in the Frobenius norm — the leading-order prediction E3a's full holonomy converges to.
    """
    K = two_agent_commutator(shape_i, shape_j, xi, l)
    return float(tau ** 2 * np.linalg.norm(K))


def error_transport_holonomy_m2(shape_i, shape_j, xi, tau, l: float = DEFAULT_L) -> np.ndarray:
    """Full (all-orders) error-transport holonomy of the m = 2 round-trip walk.

    [TUT] ex:roundtrip: "the simplest closed communication circuit is one edge
    traversed both ways." The error transport over one lag is exp(tau * C_j) on
    se(2) (the Jacobi propagator [ES §7]); the round-trip holonomy is the group
    commutator

        Hol = exp(tau C_i) exp(tau C_j) exp(-tau C_i) exp(-tau C_j),

    whose logarithm is tau^2 [C_i, C_j] + O(tau^3) (Lemma 7.1). This is the object
    Thm 7.2 bounds — an ERROR transport, deterministic — NOT the pilot's state-level
    D_ss. Uses a dense matrix exponential (fine for measuring an amplitude; the
    symbolic O(tau^2) leading term is proved separately in V5/V6).
    """
    Ci = conjugated_generator(shape_i[0], shape_i[1], xi, l)
    Cj = conjugated_generator(shape_j[0], shape_j[1], xi, l)
    return expm(tau * Ci) @ expm(tau * Cj) @ expm(-tau * Ci) @ expm(-tau * Cj)


def holonomy_amplitude_m2(shape_i, shape_j, xi, tau, l: float = DEFAULT_L) -> float:
    """||log Hol(gamma_c)||_F for the m = 2 round-trip — the PROV amplitude E3a fits.

    Deterministic; O(tau^2) by Thm 7.2; vanishes identically when [C_i,C_j] = 0
    (symmetry Cor 7.3, or eta = 0, or xi = 0), which is the switch-off battery C13.
    """
    Hol = error_transport_holonomy_m2(shape_i, shape_j, xi, tau, l)
    return float(np.linalg.norm(logm(Hol).real))
