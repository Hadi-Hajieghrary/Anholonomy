"""Quasistatic tension + the BINDING TautCertificate — plan §3.1/§3.6.

[OBS] Prop 3.3 quasistatic balance with linear drag: T cos σ = γ v ⇒ per agent
    T_j = γ · v · cos(σ_i^{(j)}) / cos²(σ^{(j)})
γ (drag coefficient) has NO value in any project document (Q6c); it is pinned
HERE from the Drake plant's physical scale [DESIGN, QD3-consistent]: chosen so
the nominal transit (v = 0.8 m/s, nominal shapes) produces T ≈ 2.5 kN — the
executed Tier-2 steady tension (2.56 kN at N=4). Every use of γ cites this pin.

TautCertificate [SPEC plan §3.6]: min_j T_j(t) < 5 N flags the sample; a theorem
cell with > 1 % flagged time in its measurement window is EXCLUDED (listed in
the manifest with counts) — never silently dropped.
"""
from __future__ import annotations

import numpy as np

__all__ = ["pin_gamma", "tensions", "TautCertificate", "T_MIN"]

T_MIN = 5.0            # N  [SPEC sim_design:32]
T_NOMINAL = 2.5e3      # N — the Drake-scale pin (QD3): executed 2.56 kN @ N=4


def pin_gamma(s_nominal: np.ndarray, v_nominal: float) -> float:
    """γ such that the mean nominal tension equals T_NOMINAL. [DESIGN, Q6c pin]"""
    sig, sig_i = s_nominal[:, 0], s_nominal[:, 1]
    mean_factor = float(np.mean(v_nominal * np.cos(sig_i) / np.cos(sig) ** 2))
    assert mean_factor > 0, "nominal formation must have positive mean tension factor"
    return T_NOMINAL / mean_factor


def tensions(s: np.ndarray, v: float, gamma: float) -> np.ndarray:
    """T_j = γ v cos(σ_i) / cos²(σ) — quasistatic [OBS]."""
    return gamma * v * np.cos(s[:, 1]) / np.cos(s[:, 0]) ** 2


class TautCertificate:
    """Accumulates per-sample taut verdicts; reports the flagged fraction."""

    def __init__(self):
        self.n = 0
        self.flagged = 0

    def check(self, T: np.ndarray) -> bool:
        ok = bool(np.min(T) >= T_MIN)
        self.n += 1
        self.flagged += (not ok)
        return ok

    @property
    def flagged_fraction(self) -> float:
        return self.flagged / max(self.n, 1)

    def verdict(self, max_fraction: float = 0.01) -> dict:
        return {"samples": self.n, "flagged": self.flagged,
                "flagged_fraction": self.flagged_fraction,
                "valid": self.flagged_fraction <= max_fraction}
