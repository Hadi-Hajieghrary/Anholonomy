"""(P) Propagate — plan §3.1, [ES] Def 6.1(a); bias-augmented.

50 Hz. Measured odometry is CORRECTED by the estimated biases:
    ζ̂ = [v_m·(1 − β̂), v_sway, ω_m − b̂]
then ξ̂ = Ad_{m(ŝ)} ζ̂, Ĝ ← Ĝ Exp(Δt ξ̂), θ̂_a += (ω_m − b̂)Δt, and σ̂ is
reconstructed from the trivialization identity (same instant as yaw(Ĝ)).

Error propagation (left-invariant, first order): residual twist error from bias
errors Δ = [v δβ, 0, δb] enters the G-error as −Δt·Ad_m·Δ ⇒
    Φ[0:3, 5] = −Δt·Ad_m·[v_m, 0, 0]ᵀ,  Φ[0:3, 6] = −Δt·Ad_m·[0, 0, 1]ᵀ.
Q is WHITE sensor noise only (the biases now carry themselves): surge σ²Δt,
sway, gyro white; Q_β ≈ 0 (fixed/run), Q_b = gyro-bias RW intensity (§3.4).
Pure function.
"""
from __future__ import annotations

import numpy as np

from tier1_sheaf.core.se2 import Exp, Ad, inv
from tier1_sheaf.core.shapes import Ad_m
from .state import FilterState

__all__ = ["propagate", "body_twist"]

# G process noise [DESIGN, declared] = white sensor noise (§3.4: surge 1.4e-5,
# sway 2e-6, gyro 2.4e-7) + REDUCED-MODEL MISMATCH intensity. The trivialization
# ξ̂ = Ad_m ζ̂ is exact only under taut slaved kinematics; the multibody plant
# side-slips (measured deterministic drift ≈ 4% of distance). That mismatch is
# PLANT PHYSICS and must live in Q_G — never laundered into the sensor-bias
# states (which are clamped to spec range).
# With the m_v state carrying the along-track mismatch, Q_G returns near
# sensor-derived + a residual lateral/yaw mismatch allowance [DESIGN]:
import os
Q_WHITE_G = tuple(float(x) for x in os.environ.get(
    "ANH_QG", "4.0e-2,2.0e-2,1.0e-3").split(","))   # record: declared mismatch ceiling
Q_S = (2.0e-5, 2.0e-5)
Q_BETA = 1.0e-10                # fixed-per-run scale bias: (near) constant
Q_BG = 3.0e-8                   # (0.01°/s/√s)² gyro-bias random walk
Q_MV = float(os.environ.get("ANH_QMV", "1.0e-7"))   # mismatch RW [DESIGN; sweep-best]


def body_twist(v_surge: float, v_sway: float, omega: float) -> np.ndarray:
    return np.array([v_surge, v_sway, omega])


def propagate(state: FilterState, zeta_meas: np.ndarray, dt: float,
              *, shape_motion_correction: bool = True,
              xi_est: np.ndarray = None, Sigma_xi: np.ndarray = None,
              tau_corr: float = 2.0) -> FilterState:
    zm = np.asarray(zeta_meas, dtype=float)
    zeta = np.array([zm[0] * (1.0 - state.beta) - state.m_v, zm[1], zm[2] - state.bg])

    yaw_G = np.arctan2(state.G[1, 0], state.G[0, 0])
    sigma_hat = state.s[1] + state.theta_a - yaw_G          # same-instant identity
    s_used = np.array([sigma_hat, state.s[1]])
    theta_a_new = state.theta_a + zeta[2] * dt

    # --- MODEL CORRECTION [Path A, exact kinematics] ---------------------
    # Exact identity: xi_L = Ad_{T(a)} Ad_{m(s)} (zeta - zeta_rel), where
    # zeta_rel = vee(m^-1 dm/dt) is the shape-motion twist. zeta_rel is computed
    # from the REDUCED SHAPE ODEs (sim_design:25-30) — model-side, no noisy
    # differentiation: common C = (v/h_i) sin(sigma_i - sigma), sigma_dot = C - eta,
    # sigma_i_dot = C - omega; eta, v taken from the previous xi (one 50 Hz step
    # of lag on a cm/s-scale correction).
    sig, sig_i = s_used
    h_i = -state.l * np.cos(sig_i)
    if not np.any(state.xi_prev):        # cold start: bootstrap from the slaved estimate
        state = state.replace(xi_prev=Ad_m(sig, sig_i, state.l) @ zeta)
    v_prev, eta_prev = state.xi_prev[0], state.xi_prev[2]
    C = ((v_prev / h_i) * np.sin(sig_i - sig)
         if (shape_motion_correction and abs(h_i) > 1e-6) else 0.0)
    sigma_dot = C - eta_prev
    phi = sig - sig_i
    c_p, s_p = np.cos(-phi), np.sin(-phi)
    tdot = state.l * sigma_dot * np.array([-np.sin(sig), np.cos(sig)])
    v_rel = np.array([c_p * tdot[0] - s_p * tdot[1], s_p * tdot[0] + c_p * tdot[1]])
    zeta_rel = (np.array([v_rel[0], v_rel[1], zeta[2] - eta_prev])
                if shape_motion_correction else np.zeros(3))
    A = Ad_m(sig, sig_i, state.l)
    xi_att = A @ (zeta - zeta_rel)
    # attach-point lever: Ad_{T(a)} = [[I, Ja],[0,1]], Ja = (a_y, -a_x)
    ax, ay = state.attach
    xi = np.array([xi_att[0] + ay * xi_att[2],
                   xi_att[1] - ax * xi_att[2],
                   xi_att[2]])
    if xi_est is not None:               # radial-constraint observer (radial.py)
        xi = np.asarray(xi_est, dtype=float)
    xi = xi + state.m_xi                 # Friedland separated drift correction
    step = Exp(dt * xi)
    G_new = state.G @ step

    Phi = np.eye(8)
    Phi[:3, :3] = Ad(inv(step))
    Phi[:3, 5] = -dt * (A @ np.array([zm[0], 0.0, 0.0]))    # dG/dβ coupling
    Phi[:3, 6] = -dt * (A @ np.array([0.0, 0.0, 1.0]))      # dG/db coupling
    Phi[:3, 7] = -dt * (A @ np.array([1.0, 0.0, 0.0]))      # dG/dm_v coupling
    Q = np.diag([*Q_WHITE_G, *Q_S, Q_BETA, Q_BG, Q_MV]) * dt
    if Sigma_xi is not None:
        # radial P-block: replace the blanket G-noise with the WLS posterior's
        # per-direction twist uncertainty. δξ is correlated over ~tau_corr s
        # (mismatch persistence), so intensity = tau_corr·Σ_ξ  [DESIGN, declared].
        Q[:3, :3] = tau_corr * np.asarray(Sigma_xi, dtype=float) * dt
    P_new = Phi @ state.P @ Phi.T + Q
    P_new = 0.5 * (P_new + P_new.T)

    out = FilterState(G_new, s_used, P_new, state.l, state.t + dt,
                      theta_a_new, state.beta, state.bg, state.m_v,
                      xi.copy(), state.attach.copy(), state.m_xi.copy())
    return out.clamp_biases()
