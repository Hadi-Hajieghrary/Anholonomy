"""FilterState for the DIEKF-Σ — plan §3.1, bias-augmented (M-FAB completion).

Pure NumPy, ZERO Drake imports. Error coordinates: [ξ_G (3), δs (2), δβ (1), δb (1)]
→ P ∈ S⁷₊. β = surge scale bias, b = gyro bias (per §3.4 sensor spec: β ~ N(0,1%)
fixed per run; b random-walks). The D1 finding that mandated this: per-run fixed
biases give χ²-distributed NEES across seeds under constant Q (18× spread measured);
estimating them online is the standard remedy.

CENTRAL LAYOUT (single source of truth — the scattered-index bug class bit twice):
core vector = [vec(G) 9 | s 2 | vech(P) 28 | theta_a 1 | beta 1 | bg 1] = CORE_LEN 42.
Leaf-specific extras (state_time, stamps, tx) append AFTER the core.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

__all__ = ["FilterState", "vech", "unvech", "VECH_IDX", "NERR", "NVECH", "IX_MV",
           "CORE_LEN", "SL_G", "SL_S", "SL_P", "IX_THETA", "IX_BETA", "IX_BG", "SL_XIPREV", "SL_MXI",
           "core_to_vec", "vec_to_core"]

NERR = 8                                  # error state: [xi_G 3, ds 2, dbeta, db, dm_v]
VECH_IDX = [(i, j) for i in range(NERR) for j in range(i, NERR)]
NVECH = len(VECH_IDX)                     # 28

SL_G = slice(0, 9)
SL_S = slice(9, 11)
SL_P = slice(11, 11 + NVECH)
IX_THETA = 11 + NVECH
IX_BETA = IX_THETA + 1
IX_BG = IX_BETA + 1
IX_MV = IX_BG + 1
SL_XIPREV = slice(IX_MV + 1, IX_MV + 4)   # previous load-twist estimate (model aux)
SL_MXI = slice(IX_MV + 4, IX_MV + 7)      # Friedland separated drift correction (aux)
CORE_LEN = IX_MV + 7


def vech(P: np.ndarray) -> np.ndarray:
    """Symmetric NERRxNERR -> NVECH vector (upper triangle, row-major)."""
    return np.array([P[i, j] for (i, j) in VECH_IDX])


def unvech(v: np.ndarray) -> np.ndarray:
    P = np.zeros((NERR, NERR))
    for k, (i, j) in enumerate(VECH_IDX):
        P[i, j] = v[k]
        P[j, i] = v[k]
    return P


@dataclass
class FilterState:
    """One agent's DIEKF-Σ belief. l (cable length, m) is required — no default.

    theta_a: bias-corrected gyro-integrated own heading. σ̂ is RECONSTRUCTED each
    propagate via the trivialization identity σ̂ = σ̂_i + θ̂_a − yaw(Ĝ).
    beta: estimated surge scale bias; bg: estimated gyro bias.
    """
    G: np.ndarray            # (3,3) SE(2) homogeneous
    s: np.ndarray            # (2,)  (sigma, sigma_i)
    P: np.ndarray            # (7,7) covariance on [xi_G, ds, dbeta, db]
    l: float                 # cable length (m) — REQUIRED
    t: float = 0.0
    theta_a: float = 0.0
    beta: float = 0.0
    bg: float = 0.0
    m_v: float = 0.0         # along-track velocity MISMATCH (m/s) — bounded plausibility
    xi_prev: np.ndarray = None   # (3,) previous ξ̂ (model aux for the shape-ODE ζ_rel)
    attach: np.ndarray = None    # (2,) attach-point offset in the load frame (constant)
    m_xi: np.ndarray = None      # (3,) FRIEDLAND separated drift correction (load-frame
                                 # additive twist; estimated by beacon-innovation rates,
                                 # DECOUPLED from all fusion-cycle covariances)

    def __post_init__(self):
        if self.xi_prev is None:
            self.xi_prev = np.zeros(3)
        if self.attach is None:
            self.attach = np.zeros(2)
        if self.m_xi is None:
            self.m_xi = np.zeros(3)

    def copy(self) -> "FilterState":
        return FilterState(self.G.copy(), self.s.copy(), self.P.copy(), self.l,
                           self.t, self.theta_a, self.beta, self.bg, self.m_v,
                           self.xi_prev.copy(), self.attach.copy(), self.m_xi.copy())

    def replace(self, **kw) -> "FilterState":
        """Copy with fields replaced — USE THIS instead of positional re-construction."""
        out = self.copy()
        for k, v in kw.items():
            setattr(out, k, v)
        return out

    def clamp_biases(self, beta_max: float = 0.03, bg_max: float = 5.0e-3,
                     mv_max: float = 0.0) -> "FilterState":
        """Clamp bias estimates to the SENSOR SPEC's own range [DESIGN, declared].

        β is a sensor property (§3.4: β ~ N(0, 1%)) — |β̂| ≤ 3σ = 3%. Without the
        clamp, deterministic model mismatch launders itself into β̂ via persistent
        beacon innovations (integrator wind-up; measured: β̂ → 19%). Mismatch
        belongs in Q_G (declared), not in a sensor-bias state.
        """
        out = self.copy()
        out.beta = float(np.clip(out.beta, -beta_max, beta_max))
        out.bg = float(np.clip(out.bg, -bg_max, bg_max))
        # m_v DISABLED (mv_max = 0) [measured]: a scalar velocity-mismatch state
        # cannot represent the shape-dependent reduced-model error, and near the
        # innovation-gate boundary it wanders to its bound on some seeds
        # (46-100 ANEES outliers). The mismatch story lives in the RADIAL
        # observer (staged) and the declared Q — not in this state.
        out.m_v = float(np.clip(out.m_v, -mv_max, mv_max))
        return out

    @staticmethod
    def initial(s0, l: float, *, P0_G: float = 1e-4, P0_s: float = 4e-2,
                P0_beta: float = 1e-4, P0_bg: float = 1e-8, P0_mv: float = 9e-4,
                theta_a0=None) -> "FilterState":
        """theta_a0 defaults to σ0 − σ_i0 (trivialization identity at yaw(G)=0).
        P0_beta = (1%)² per §3.4; P0_mv = (3 cm/s)² prior on model mismatch."""
        s0 = np.asarray(s0, dtype=float).copy()
        th0 = float(s0[0] - s0[1]) if theta_a0 is None else float(theta_a0)
        P = np.diag([P0_G, P0_G, P0_G, P0_s, P0_s, P0_beta, P0_bg, P0_mv]).astype(float)
        return FilterState(np.eye(3), s0, P, float(l), 0.0, th0, 0.0, 0.0, 0.0)

    @staticmethod
    def initial_at(s0, l: float, attach, **kw) -> "FilterState":
        """initial() + the agent's attach-point offset (production path)."""
        st = FilterState.initial(s0, l, **kw)
        st.attach = np.asarray(attach, dtype=float)[:2].copy()
        return st


def core_to_vec(st: FilterState) -> np.ndarray:
    v = np.empty(CORE_LEN)
    v[SL_G] = st.G.ravel()
    v[SL_S] = st.s
    v[SL_P] = vech(st.P)
    v[IX_THETA] = st.theta_a
    v[IX_BETA] = st.beta
    v[IX_BG] = st.bg
    v[IX_MV] = st.m_v
    v[SL_XIPREV] = st.xi_prev
    v[SL_MXI] = st.m_xi
    return v


def vec_to_core(v: np.ndarray, l: float, t: float, attach=(0.0, 0.0)) -> FilterState:
    v = np.asarray(v, dtype=float)
    return FilterState(v[SL_G].reshape(3, 3).copy(), v[SL_S].copy(),
                       unvech(v[SL_P]), float(l), float(t),
                       float(v[IX_THETA]), float(v[IX_BETA]), float(v[IX_BG]),
                       float(v[IX_MV]), v[SL_XIPREV].copy(),
                       np.asarray(attach, dtype=float)[:2].copy(), v[SL_MXI].copy())
