"""Edge weights — plan §3.1: w_e = SERIES information (Def 4.1, pinned Q6a)."""
from __future__ import annotations

import numpy as np

__all__ = ["iota", "w_series"]


def iota(sigma: float, sigma_i: float) -> float:
    """Per-agent direction-channel information ι_j ∝ cos²(σ_i)·sec⁴(σ).

    Shape-dependent factor only; the proportionality constant is Q6b (open) and
    cancels in normalized weight comparisons. Small floor guards the sec⁴ pole.
    """
    return float(np.cos(sigma_i) ** 2 / (np.cos(sigma) ** 4 + 1e-12))


def w_series(iota_i: float, iota_j: float) -> float:
    """Series information: (1/ι_i + 1/ι_j)⁻¹ — Def 4.1 [SPEC]."""
    return 1.0 / (1.0 / max(iota_i, 1e-12) + 1.0 / max(iota_j, 1e-12))
