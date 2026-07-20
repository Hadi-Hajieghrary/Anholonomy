"""(F) Fuse — plan §3.1; the PAPER rule (Q1 = (a)), executed-composite form.

SPEC CLARIFICATION (recorded; see WS-0 report). sim_design.tex:52–57 displays
    G̃ = Ĝ_{j'}(t−τ) · Exp(τ · Ad_{m(ŝ_{j'})⁻¹ m(ŝ_j)} ζ̂_j)
against messages carrying Ĝ. But the pilot — whose behavior the EXECUTED
frozen-shape null characterizes — packs boat poses H = Ĝ·m(ŝ) and unpacks with
m(ŝ_pkt)⁻¹; the packing conjugation composes with the displayed transport as
    Ad(m_B^pkt) · Ad(m_B^pkt⁻¹ m_A) = Ad(m_A),
so the sender's shape TELESCOPES OUT exactly (frozen or moving), leaving
    G̃ = Ĝ_{j'}(t−a) · Exp(a · Ad_{m(ŝ_j)} ζ̂_j) = Ĝ_{j'}(t−a) · Exp(a · ξ̂_j):
fast-forward the stale load-pose estimate with the RECEIVER'S OWN current
load-twist estimate. This is the composite whose null (D_ss ≈ 1e-29 at frozen
shapes) was executed, and the rule implemented here on Ĝ-packets. The floor's
mechanism under motion is the staleness of ŝ inside ξ̂ — plan §0.3.

α = κ·Δ_c is INJECTED by the harness (never a literal here; plan §3.3).
Returns a FusionRecord logging the APPLIED TRANSPORT — what makes D3/M5
(closed-loop holonomy amplitude, PROV) measurable. WS-0 scope: paper rule only;
no CI ω search, no rules registry (they land at M-FAB). Pure function.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from tier1_sheaf.core.se2 import Exp, Log, inv
from tier1_sheaf.core.shapes import Ad_m
from .state import FilterState

__all__ = ["FusionRecord", "fuse_paper", "bias_schmidt_update"]


@dataclass
class FusionRecord:
    """One fuse event: everything D3/M5 and the 𝒫-assert need, nothing else."""
    t: float                  # receiver filter time at consumption
    sender: int
    realized_age: float       # measured stamp age (s) — THE fit regressor (plan §5.2)
    transport_log: np.ndarray  # (3,) se(2) log of the applied fast-forward transport
    residual: np.ndarray      # (3,) r = Log(Ĝ⁻¹ G̃)


def fuse_paper(state: FilterState, G_nb: np.ndarray, s_nb: np.ndarray,
               realized_age: float, zeta_self: np.ndarray, alpha: float,
               w: float, sender: int) -> tuple[FilterState, FusionRecord]:
    """Paper fusion rule, executed-composite form: transport = a·Ad_{m(ŝ_self)}ζ̂_self.

    s_nb (the packet's shape) is carried for the record/consistency layer; it
    cancels out of the transport by the telescoping identity documented above.
    """
    xi_self = Ad_m(state.s[0], state.s[1], state.l) @ np.asarray(zeta_self, dtype=float)
    transport = realized_age * xi_self
    G_tilde = G_nb @ Exp(transport)
    r = Log(inv(state.G) @ G_tilde)
    G_new = state.G @ Exp(alpha * w * r)

    out = state.replace(G=G_new)
    rec = FusionRecord(t=state.t, sender=sender, realized_age=float(realized_age),
                       transport_log=transport.copy(), residual=r.copy())
    return out, rec


def bias_schmidt_update(state: FilterState, r, R_nb) -> FilterState:
    """Schmidt-type bias update from the fusion residual [DESIGN, declared].

    Model: r ~ e_G(self) - e_G(nb) + transport noise: z = H e + v, H = [I3 0...],
    R = P_nb,G + a^2 Q_tau. The G-correction keeps the SPEC'd fixed gain
    alpha = kappa*Delta_c (Def 6.1(c)); the bias rows get their Kalman gain via
    the JOSEPH form (consistent for any suboptimal gain):
        K = [0_3; 0_2; K_b],  K_b = P[5:7, 0:3] (P_G + R)^-1,
        P <- (I-KH) P (I-KH)^T + K R K^T.
    """
    r = np.asarray(r, dtype=float)
    R_nb = np.asarray(R_nb, dtype=float)
    # SENSOR-bias rows (β, b) ONLY. m_v is deliberately EXCLUDED from fusion
    # feeding [DESIGN, measured]: the paper-rule residual under moving shapes
    # carries a deterministic per-edge transport component (the floor mechanism
    # itself, fan-patterned ±0.1 m/s) that mis-attributes into m_v and destabilizes
    # the network. m_v is updated ONLY by the beacon (absolute information for an
    # absolute-drift state; unit-tested convergent).
    S = state.P[:3, :3] + R_nb
    K_b = state.P[5:7, :3] @ np.linalg.inv(S)               # (2,3): β, b rows only
    d = K_b @ r
    K = np.zeros((8, 3))
    K[5:7, :] = K_b
    H = np.hstack([np.eye(3), np.zeros((3, 5))])
    IKH = np.eye(8) - K @ H
    P_new = IKH @ state.P @ IKH.T + K @ R_nb @ K.T
    P_new = 0.5 * (P_new + P_new.T)
    return state.replace(P=P_new, beta=state.beta + float(d[0]),
                         bg=state.bg + float(d[1])).clamp_biases()
