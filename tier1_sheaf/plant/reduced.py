"""Tier-1 reduced plant — plan §3.1 tier1_sheaf/plant/, sim_design.tex:24–33.

State (g_L; s_1..s_N) ∈ SE(2) × T^{2N}. Taut-mode reduced kinematics [SPEC]:
    ġ_L = g_L ξ̂,  ξ = (v, 0, η)
    σ̇^{(j)}   = (v / h_i^{(j)}) sin(σ_i^{(j)} − σ^{(j)}) − η
    σ̇_i^{(j)} = (v / h_i^{(j)}) sin(σ_i^{(j)} − σ^{(j)}) − η_j
    h_i^{(j)} = −l_j cos σ_i^{(j)}
Integrator [SPEC sim_design:33]: Crouch–Grossman Lie–Euler for g_L
(g ← g Exp(Δt ξ)), RK4 for shapes, Δt = 0.01 s (T1-E10 sweeps it).
Noise [SPEC plan §6.8 ref]: Euler–Maruyama — deterministic step + √(Q Δt)·n;
twist diffusion Q_ξ = diag(1e-4, 1e-5, 1e-5), shape diffusion 1e-5 I₂
(sim_design:31). Shape controller [SPEC sim_design:61 + [DESIGN] feedforward]:
    η_j = η + k_p (σ^ref_j − σ^{(j)}),  k_p = 1.5
the load-rate feedforward η is a [DESIGN] addition (the literal :61 form without
it leaves the relative angle w = σ_i − σ undamped through turns); boundedness is
gated by test_shapes_bounded_through_turn, not asserted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from tier1_sheaf.core.se2 import Exp

__all__ = ["ReducedConfig", "ReducedPlant", "eta_persistent_turn"]

Q_XI = np.array([1.0e-4, 1.0e-5, 1.0e-5])     # twist diffusion  [SPEC sim_design:31]
Q_S = 1.0e-5                                   # shape diffusion (per angle)


def eta_persistent_turn(t: float, *, bias=0.15, amp=0.10, freq=0.05) -> float:
    """|η| ∈ [0.05, 0.25] rad/s, never vanishing (plan §5.3 persistent_turn)."""
    return bias + amp * np.sin(freq * t)


@dataclass
class ReducedConfig:
    N: int
    l: float                       # cable length (m) — REQUIRED, no default (plan §3.5)
    dt: float = 0.01               # plant step [SPEC]; E10 sweeps it
    v_ref: float = 0.8             # m/s (within [0.3, 1.2], sim_design:30)
    k_p: float = 1.5               # shape controller gain [SPEC sim_design:61]
    noise_on: bool = True
    eta_profile: str = "persistent_turn"   # or "straight"


class ReducedPlant:
    """Truth-side reduced plant. step() advances one Δt; fully seeded."""

    def __init__(self, cfg: ReducedConfig, s0: np.ndarray, seed: int):
        assert s0.shape == (cfg.N, 2), "s0 = (N,2) array of (sigma, sigma_i)"
        self.cfg = cfg
        self.G = np.eye(3)
        self.s = s0.astype(float).copy()
        self.s_ref = s0[:, 0].astype(float).copy()      # σ reference = initial formation
        self.t = 0.0
        self.rng = np.random.default_rng(np.random.SeedSequence([seed, 11]))

    # -- references ----------------------------------------------------------
    def eta_ref(self, t: float) -> float:
        if self.cfg.eta_profile == "straight":
            return 0.0
        if self.cfg.eta_profile == "drake_maneuver":
            # the D2 Drake maneuver reference (turn_bias=0.03, turn_amp=0.02,
            # freq=0.05) — the matched-config profile (plan §6); feasible at
            # l=12, v=0.9: eta_max*l/v = 0.67 < 1
            return 0.03 + 0.02 * np.sin(0.05 * t)
        return eta_persistent_turn(t)

    def controls(self, t: float):
        """(v, η, η_1..η_N) — shape controller on TRUE shapes (truth side)."""
        v = self.cfg.v_ref
        eta = self.eta_ref(t)
        eta_j = eta + self.cfg.k_p * (self.s_ref - self.s[:, 0])
        return v, eta, eta_j

    # -- dynamics ------------------------------------------------------------
    def _sdot(self, s: np.ndarray, v: float, eta: float, eta_j: np.ndarray) -> np.ndarray:
        sig, sig_i = s[:, 0], s[:, 1]
        h_i = -self.cfg.l * np.cos(sig_i)
        common = (v / h_i) * np.sin(sig_i - sig)
        return np.stack([common - eta, common - eta_j], axis=1)

    def step(self):
        cfg = self.cfg
        dt = cfg.dt
        v, eta, eta_j = self.controls(self.t)

        # RK4 on shapes  [SPEC]
        f = lambda s: self._sdot(s, v, eta, eta_j)
        k1 = f(self.s)
        k2 = f(self.s + 0.5 * dt * k1)
        k3 = f(self.s + 0.5 * dt * k2)
        k4 = f(self.s + dt * k3)
        self.s = self.s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

        # CG Lie–Euler on g_L with EM twist noise  [SPEC]
        xi = np.array([v, 0.0, eta])
        if cfg.noise_on:
            xi_step = dt * xi + np.sqrt(Q_XI * dt) * self.rng.standard_normal(3)
            self.s += np.sqrt(Q_S * dt) * self.rng.standard_normal((cfg.N, 2))
        else:
            xi_step = dt * xi
        self.G = self.G @ Exp(xi_step)
        self.t += dt
        return self

    # -- observables the harness/sensors read --------------------------------
    def body_twists(self, t=None):
        """Per-agent TRUE body twist: ζ_j = Ad_{m}^{-1} ξ + vee(m^{-1} ṁ).

        The slaved part alone is NOT what an odometer measures — the vessel also
        moves with the shape rates (the term the estimator's Path-A correction
        removes). ṁ from the same shape ODEs step() integrates.
        """
        from tier1_sheaf.core.shapes import Ad_m
        tt = self.t if t is None else t
        v, eta, eta_j = self.controls(tt)
        xi = np.array([v, 0.0, eta])
        sdot = self._sdot(self.s, v, eta, eta_j)
        out = []
        for k, (sig, sig_i) in enumerate(self.s):
            slaved = np.linalg.solve(Ad_m(sig, sig_i, self.cfg.l), xi)
            sd, sdi = sdot[k]
            phi = sig - sig_i
            tdot = self.cfg.l * sd * np.array([-np.sin(sig), np.cos(sig)])
            c, s_ = np.cos(-phi), np.sin(-phi)
            v_rel = np.array([c * tdot[0] - s_ * tdot[1], s_ * tdot[0] + c * tdot[1]])
            out.append(slaved + np.array([v_rel[0], v_rel[1], sd - sdi]))
        return np.stack(out)
