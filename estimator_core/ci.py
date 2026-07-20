"""Covariance Intersection on the load block — plan §3.1, sim_design.tex:57.

P_G⁻¹ ← ω P_G⁻¹ + (1−ω) (P_nb,G + a²·Q_τ)⁻¹,   ω = argmin trace(P_fused)
over a 19-point grid (plan §9.2 names Brent if the grid ever binds). The
neighbor block is inflated by the transport-age uncertainty a²Q_τ before
intersection; the transport conjugation of P_nb is second-order at these error
magnitudes and CI is conservative by construction [DESIGN, documented].
"""
from __future__ import annotations

import numpy as np

__all__ = ["ci_fuse_G", "Q_TAU"]

# transport-age inflation [DESIGN, measured]: the lateral component is the CI
# floor-setter — five mutually-correlated optimistic covariances intersect each
# epoch (Rem 6.4), so Q_TAU must carry the measured lateral mismatch
# (Friedland: 0.05-0.07 m/s persistent) or CI clamps P_y below the true error.
Q_TAU = np.diag([5.0e-3, 6.0e-2, 1.0e-3])
_OMEGAS = np.linspace(0.05, 0.95, 19)


def ci_fuse_G(P: np.ndarray, P_nb_G: np.ndarray, realized_age: float):
    """CI on the 3x3 G-block of the 5x5 P. Returns (P_new, omega)."""
    PG = P[:3, :3]
    P_other = P_nb_G + realized_age ** 2 * Q_TAU
    PG_inv = np.linalg.inv(PG)
    PO_inv = np.linalg.inv(P_other)
    best = (None, np.inf, 0.5)
    for w in _OMEGAS:
        Pf = np.linalg.inv(w * PG_inv + (1.0 - w) * PO_inv)
        tr = float(np.trace(Pf))
        if tr < best[1]:
            best = (Pf, tr, float(w))
    # CI + DECORRELATION [measured; the textbook decentralized form].
    # Naive block replacement breaks PSD (Schur); congruence scaling is PSD-safe
    # but dynamically compounds the G↔aux cross terms at the fuse rate (measured
    # 1.5 → 273 blowup). CI's own premise is that correlations are unknown —
    # so after intersecting the G-block, the G↔aux cross-covariances are ZEROED.
    # PSD by construction (block-diagonal of PSD blocks); aux states couple to G
    # only through Φ between fusions and their own gated updates.
    Pf = 0.5 * (best[0] + best[0].T)
    P_new = P.copy()
    P_new[:3, :3] = Pf
    P_new[:3, 3:] = 0.0
    P_new[3:, :3] = 0.0
    return P_new, best[2]