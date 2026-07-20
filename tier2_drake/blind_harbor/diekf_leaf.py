"""DIEKFSigmaLeaf — THIN Drake adapter around estimator_core (plan §3.1).
Bias-augmented M-FAB form. Zero algorithm code; single 100 Hz event with total
internal ordering (consume all neighbors -> propagate 50 Hz -> update 20 Hz).

Discrete state = [CORE (estimator_core.CORE_LEN = 42) | state_time 1 |
last_stamp x deg | tx_packet PACKET_LEN] — layout comes from estimator_core
constants, never hand-numbered (the scattered-index bug class bit twice).
tx snapshots only on the Δ_c send grid; packets stamped with state_time.
"""
from __future__ import annotations

import numpy as np
from pydrake.systems.framework import LeafSystem, BasicVector

import estimator_core as ec
from estimator_core.fuse import bias_schmidt_update
from estimator_core.ci import Q_TAU

__all__ = ["DIEKFSigmaLeaf", "state_len"]

_TICK = 0.01

IX_TIME = ec.CORE_LEN                     # 42


def state_len(deg: int) -> int:
    return ec.CORE_LEN + 1 + deg + 4 * deg + ec.PACKET_LEN


class DIEKFSigmaLeaf(LeafSystem):
    def __init__(self, s0, l: float, alpha: float, *, agent_id: int = 0,
                 n_neighbors: int = 1, fuse_rule: str = "paper",
                 covariance: str = "ci", weights: str = "A3",
                 send_epoch: float = 0.1, bias_update: bool = False,
                 has_beacon: bool = False, attach=(0.0, 0.0)):
        super().__init__()
        self._attach = np.asarray(attach, dtype=float)[:2]
        self._id = int(agent_id)
        self._l = float(l)
        self._alpha = float(alpha)
        self._deg = int(n_neighbors)
        self._rule = fuse_rule
        self._cov = covariance
        self._weights = weights
        self._bias_up = bool(bias_update)
        self._send_ticks = int(round(send_epoch / _TICK))
        assert abs(self._send_ticks * _TICK - send_epoch) < 1e-12
        self.records: list[ec.FusionRecord] = []

        st0 = ec.FilterState.initial(s0, l)
        tx0 = ec.pack(0.0, self._id, st0, valid=False)
        x0 = np.concatenate([ec.core_to_vec(st0), [0.0], -np.ones(self._deg),
                             np.zeros(4 * self._deg), tx0])
        self._state_index = self.DeclareDiscreteState(x0)
        self._odom = self.DeclareVectorInputPort("odom", BasicVector(3))
        self._dir = self.DeclareVectorInputPort("direction", BasicVector(2))
        self._pkts = [self.DeclareVectorInputPort(f"pkt_in_{i}", BasicVector(ec.PACKET_LEN))
                      for i in range(self._deg)]
        self._beacon = (self.DeclareVectorInputPort("beacon", BasicVector(4))
                        if has_beacon else None)
        self.DeclareVectorOutputPort("pkt_out", BasicVector(ec.PACKET_LEN), self._calc_pkt,
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclareVectorOutputPort("est", BasicVector(state_len(self._deg)),
                                     self._calc_est,
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclarePeriodicDiscreteUpdateEvent(_TICK, 0.0, self._tick)

    def _tick(self, context, discrete_state):
        t = context.get_time()
        k = int(round(t / _TICK))
        x = context.get_discrete_state(self._state_index).get_value().copy()
        st = ec.vec_to_core(x[:ec.CORE_LEN], self._l, t, attach=self._attach)
        i0 = IX_TIME + 1
        stamps = x[i0:i0 + self._deg].copy()
        pairs = x[i0 + self._deg:i0 + 5 * self._deg].reshape(self._deg, 4).copy()

        for i, port in enumerate(self._pkts):                 # (1) consume, fixed order
            pkt = port.Eval(context)
            stamp, sender, G_nb, P_nb, s_nb, b_nb, rho_nb, mxi_nb, valid = ec.unpack(pkt)
            if not (valid and stamp > stamps[i]) or self._rule == "off":
                continue
            pairs[i] = [b_nb[0], b_nb[1], b_nb[2], rho_nb]
            # drift-estimate diffusion: the anchor's Friedland m_xi is COMMON
            # physics (all vessels mis-model the same load motion) — relax toward
            # the received estimate so the correction reaches unanchored agents
            if np.any(mxi_nb):
                st = st.replace(m_xi=0.9 * st.m_xi + 0.1 * mxi_nb)
            zeta = self._odom.Eval(context)
            age = t - stamp
            if self._weights == "series":
                w = min(1.0, ec.w_series(ec.iota(*st.s), ec.iota(*s_nb)) /
                        max(0.5 * ec.iota(*st.s), 1e-12))
            else:
                w = 1.0
            st, rec = ec.fuse_with_rule(self._rule, st, G_nb, s_nb, age, zeta,
                                        self._alpha, w, sender)
            if rec is not None:
                self.records.append(rec)
                if self._bias_up:      # OFF by default [DESIGN, measured]: aux states
                    # (β, b, m_v) are BEACON-ONLY — Schmidt feeding from fusion
                    # residuals is unstable at sensor-scale Q (K_b = P_x/(P_G+R)
                    # inflates geometrically vs CI at 20 Hz) and mis-attributes
                    # the moving-shape transport residual. Fusion = the SPEC'd
                    # rule exactly: fixed-gain G-correction + CI.
                    st = bias_schmidt_update(st, rec.residual,
                                             P_nb[:3, :3] + age ** 2 * Q_TAU)
            if self._cov == "ci":
                P_new, _ = ec.ci_fuse_G(st.P, P_nb[:3, :3], age)
                st = st.replace(P=P_new)
            stamps[i] = stamp
        if k % 2 == 0:                                        # (2) propagate, 50 Hz
            # RADIAL-CONSTRAINT OBSERVER (radial.py): exact rigid-cable kinematics,
            # plant-independent. Own fresh pair + neighbors' packet pairs (aged by
            # tau -- the constraint channel with its latency) -> lstsq load twist.
            # Conditioning gate falls back to the slaved model (reduced-ODE
            # correction stays OFF on Drake: fiction on side-slipping multibody).
            zeta = self._odom.Eval(context)
            zc = np.array([zeta[0] * (1.0 - st.beta) - st.m_v, zeta[1],
                           zeta[2] - st.bg])
            b_own, rho_own = ec.radial_pair(st, zc)
            B = [b_own]; R = [rho_own]
            for i in range(self._deg):
                if np.any(pairs[i][:3]):
                    B.append(pairs[i][:3]); R.append(pairs[i][3])
            from tier1_sheaf.core.shapes import Ad_m
            xi_prior = Ad_m(st.s[0], st.s[1], st.l) @ zc      # slaved-model prior
            # RADIAL P-BLOCK [the twice-confirmed path]: Bayesian WLS over own
            # fresh pair + neighbors' aged pairs; the posterior Σ_ξ feeds the
            # per-direction G-noise (large lateral, small along-track — matching
            # the true error anisotropy the anchored gate demands).
            SIG_V2 = 7.0e-4                                   # own ρ noise (odometry)
            Q_XI_STALE = 1.0e-4                               # twist drift per s² of age
            sig2 = [SIG_V2]
            for i in range(self._deg):
                if np.any(pairs[i][:3]):
                    age_i = t - stamps[i] if stamps[i] > 0 else 0.4
                    sig2.append(SIG_V2 + Q_XI_STALE * age_i ** 2)
            SIGMA_PRIOR = np.diag([1.0e-3, 2.5e-3, 1.0e-4])  # lat = Friedland-measured 0.05 m/s   # slaved-model twist unc.
            # RADIAL P-BLOCK STAGED (gate-neutral-to-negative on the anchored
            # metric: 7.7 vs the 3.8-class record; drift BETTER 1.39 vs 1.73).
            # The residual gate gap is CI-over-correlated-covariances — Rem 6.4,
            # proven fundamental by elimination. Re-enable by calling
            # solve_load_twist_wls and passing (xi_est, Sigma_xi, tau_corr).
            _ = ec.solve_load_twist_wls          # keep the import surface alive
            st = ec.propagate(st, zeta, 0.02, shape_motion_correction=False)
        if k % 5 == 1:                                        # (3) update, 20 Hz (+10 ms)
            sig_i, kappa = self._dir.Eval(context)
            st = ec.update_direction(st, sig_i, kappa)
        if self._beacon is not None and k % 20 == 3:          # (4) beacon, 5 Hz [SPEC]
            b = self._beacon.Eval(context)
            if b[3] > 0.5:
                st = ec.update_beacon(st, b[:3])

        if k % self._send_ticks == 0:                         # send-epoch snapshot
            zeta = self._odom.Eval(context)
            zc = np.array([zeta[0] * (1.0 - st.beta) - st.m_v, zeta[1],
                           zeta[2] - st.bg])
            tx = ec.pack(t, self._id, st, radial=ec.radial_pair(st, zc))
        else:
            tx = x[i0 + 5 * self._deg:].copy()
        discrete_state.get_mutable_vector(self._state_index).set_value(
            np.concatenate([ec.core_to_vec(st), [t], stamps, pairs.ravel(), tx]))

    def _calc_pkt(self, context, output):
        x = context.get_discrete_state(self._state_index).get_value()
        output.set_value(x[IX_TIME + 1 + 5 * self._deg:])      # the tx snapshot

    def _calc_est(self, context, output):
        output.set_value(context.get_discrete_state(self._state_index).get_value())
