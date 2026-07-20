"""(U) Update — plan §3.1 (skeleton: direction channel only).

20 Hz. WS-0 scope [DESIGN, recorded]: the boat-frame cable-direction channel
σ̃_i ~ vM(σ_i, κ) as a scalar Kalman update on s[1] with R = 1/κ (small-angle
Gaussian approximation of the von Mises). Broadside guard per Cor 5.3: gain
clipped when cos(σ̂_i) < 0.1. The full Fisher-weighted IEKF (tension magnitude,
κ = c T²/r₀ per A10, joint H over [ξ_G, δs]) lands at M-FAB (plan §9.2) — the
WS-0 gates (parity/determinism/timing) do not depend on it.

Pure function.
"""
from __future__ import annotations

import numpy as np

from .state import FilterState

__all__ = ["update_direction", "update_beacon"]

_H = np.array([[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]])   # observes s[1] = sigma_i


def _wrap(a: float) -> float:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def update_direction(state: FilterState, sigma_i_meas: float, kappa: float,
                     *, guard_cos: float = 0.1) -> FilterState:
    """Scalar direction-channel update on sigma_i; broadside guard clips the gain."""
    R = 1.0 / max(kappa, 1e-9)
    S = float(_H @ state.P @ _H.T) + R
    K = (state.P @ _H.T / S).ravel()                     # (5,)
    if abs(np.cos(state.s[1])) < guard_cos:              # broadside guard (Cor 5.3)
        K = 0.1 * K
    innov = _wrap(sigma_i_meas - state.s[1])

    ds = K * innov                                # correction in the 8-dim error
    # G-block correction is through the log-linear error; skeleton applies shape only
    s_new = state.s + ds[3:5]
    IKH = np.eye(8) - np.outer(K, _H.ravel())
    P_new = IKH @ state.P @ IKH.T + np.outer(K, K) * R    # Joseph (PSD-safe)
    P_new = 0.5 * (P_new + P_new.T)
    return state.replace(s=s_new, P=P_new)


_H_BEACON = np.hstack([np.eye(3), np.zeros((3, 5))])   # observes e_G directly


def update_beacon(state: FilterState, z_pose, R_diag=(0.05**2, 0.05**2,
                                                      (np.pi / 360) ** 2),
                  *, drift_alpha: float = 0.05, drift_gate: float = 0.5,
                  dt_beacon: float = 0.2, mxi_max: float = 0.1) -> FilterState:
    """Absolute load-pose update (docking beacon; Cor 5.2's anchor) [SPEC §3.4].

    z_pose = (x, y, theta) measured load pose; innovation r = Log(Ĝ⁻¹ Z) ≈ e_G + v
    under the left-invariant error convention. Standard KF on the 7-dim error —
    this is the pinning that collapses the gauge kernel (and, via the bias
    cross-covariances, makes the team-common bias observable).
    """
    from tier1_sheaf.core.se2 import SE2, Log, Exp, inv
    Z = SE2(float(z_pose[2]), np.asarray(z_pose[:2], dtype=float))
    r = Log(inv(state.G) @ Z)
    R = np.diag(R_diag)
    S = _H_BEACON @ state.P @ _H_BEACON.T + R
    K = state.P @ _H_BEACON.T @ np.linalg.inv(S)
    # AUX-ROW INNOVATION GATE [DESIGN, measured]: during network-convergence
    # transients the innovation is disequilibrium, not slow-state error; feeding
    # it into (β, b, m_v) at 5 Hz mis-attributes and destabilizes (measured
    # blowup). G/s always correct; aux rows update only near convergence.
    import os
    if np.linalg.norm(r[:2]) > float(os.environ.get("ANH_GATE", "0.0")):
        K[5:, :] = 0.0
    dx = K @ r
    G_new = state.G @ Exp(dx[:3])
    IKH = np.eye(8) - K @ _H_BEACON
    P_new = IKH @ state.P @ IKH.T + K @ R @ K.T           # Joseph
    P_new = 0.5 * (P_new + P_new.T)
    # FRIEDLAND SEPARATED DRIFT OBSERVER [the elimination's unique survivor]:
    # a leaky integrator on the innovation RATE, gated to the converged regime,
    # clamped to plausibility — zero coupling to any covariance. r > 0 means the
    # estimate lags truth ⇒ raise the twist by m_xi.
    m_xi = state.m_xi.copy()
    if np.linalg.norm(r[:2]) < drift_gate:
        m_xi = 0.995 * m_xi + drift_alpha * (r / dt_beacon)
        m_xi = np.clip(m_xi, -mxi_max, mxi_max)
    out = FilterState(G_new, state.s + dx[3:5], P_new, state.l, state.t,
                      state.theta_a, state.beta + float(dx[5]),
                      state.bg + float(dx[6]), state.m_v + float(dx[7]),
                      state.xi_prev.copy(), state.attach.copy(), m_xi)
    return out.clamp_biases()
