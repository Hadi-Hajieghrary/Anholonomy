"""SensorSuite — plan §3.4, WS-0 subset: odometry (surge+sway+gyro) and the
boat-frame cable-direction channel. Tension magnitude + beacon land at M-FAB.

Truth comes from plant ports (sensors are the sanctioned plant readers — the
truth-isolation rule forbids ESTIMATOR/CONTROLLER reads, not sensor reads).
RNG: numpy Generator held as instance state, seeded SeedSequence([master, agent,
stream]); advances only inside the single periodic event, so runs are
deterministic for a fixed event schedule (gate (a) verifies bit-identity).
"""
from __future__ import annotations

import numpy as np
from pydrake.systems.framework import LeafSystem, BasicVector
from pydrake.common.value import Value
from pydrake.math import RigidTransform
from pydrake.multibody.math import SpatialVelocity

__all__ = ["SensorSuite", "KAPPA_DIR"]

# WS-0 fixed direction-channel concentration: sd = 1 deg  (A10's kappa = c T^2/r_0
# calibration is QD3, lands at M-FAB with the tension-magnitude channel)
KAPPA_DIR = 1.0 / np.radians(1.0) ** 2


class SensorSuite(LeafSystem):
    """One agent's sensors on one 100 Hz event with internal 50/20 Hz dispatch.

    Outputs (ZOH between their update ticks):
      odom (3):      [v_surge~, v_sway~, omega~]   updated on 50 Hz ticks (k even)
      direction (2): [sigma_i~, kappa]             updated on 20 Hz ticks (k = 1 mod 5)
    """

    def __init__(self, master_seed: int, agent: int, load_body_index, asv_body_index,
                 attach_local, *, noise_on: bool = True,
                 beacon_t_on: float = float("inf")):
        super().__init__()
        self._rng = np.random.default_rng(np.random.SeedSequence([master_seed, agent, 7]))
        self._noise_on = noise_on
        self._load_idx = int(load_body_index)
        self._asv_idx = int(asv_body_index)
        self._attach = np.asarray(attach_local, dtype=float)[:2]   # load-frame attach point
        self._bias_beta = float(self._rng.normal(0.0, 0.01)) if noise_on else 0.0
        self._gyro_bias = 0.0

        self._X_in = self.DeclareAbstractInputPort("body_poses", Value([RigidTransform()]))
        self._V_in = self.DeclareAbstractInputPort("body_spatial_velocities",
                                                   Value([SpatialVelocity()]))
        self._beacon_t_on = float(beacon_t_on)
        # discrete state: [odom 3, direction 2, beacon 4 (x, y, th, valid)]
        self._state_index = self.DeclareDiscreteState(9)
        self.DeclareVectorOutputPort("odom", BasicVector(3),
                                     lambda c, o: o.set_value(
                                         c.get_discrete_state(self._state_index).get_value()[:3]),
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclareVectorOutputPort("direction", BasicVector(2),
                                     lambda c, o: o.set_value(
                                         c.get_discrete_state(self._state_index).get_value()[3:5]),
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclareVectorOutputPort("beacon", BasicVector(4),
                                     lambda c, o: o.set_value(
                                         c.get_discrete_state(self._state_index).get_value()[5:9]),
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclarePeriodicDiscreteUpdateEvent(0.01, 0.0, self._tick)

    # -- truth helpers -------------------------------------------------------
    def _truth(self, context):
        Xs = self._X_in.Eval(context)
        Vs = self._V_in.Eval(context)
        X_asv = Xs[self._asv_idx]
        X_load = Xs[self._load_idx]
        V_asv = Vs[self._asv_idx]
        # body twist of the ASV in its own frame
        R = X_asv.rotation().matrix()[:2, :2]
        v_world = V_asv.translational()[:2]
        v_body = R.T @ v_world
        omega = V_asv.rotational()[2]
        # angles: sigma = CABLE angle in the LOAD frame, measured from the ATTACH
        # POINT (the physical cable direction; the reduced model's per-agent frame
        # is the attach point, a fixed load-frame offset composed into m(s));
        # theta_asv = theta_load + sigma - sigma_i => sigma_i = theta_load - theta_asv + sigma
        th_load = np.arctan2(X_load.rotation().matrix()[1, 0], X_load.rotation().matrix()[0, 0])
        th_asv = np.arctan2(X_asv.rotation().matrix()[1, 0], X_asv.rotation().matrix()[0, 0])
        Rl = np.array([[np.cos(th_load), -np.sin(th_load)], [np.sin(th_load), np.cos(th_load)]])
        attach_world = X_load.translation()[:2] + Rl @ self._attach
        d_world = X_asv.translation()[:2] - attach_world
        sigma = np.arctan2(d_world[1], d_world[0]) - th_load
        sigma_i = th_load - th_asv + sigma
        return v_body, omega, sigma, sigma_i

    def _tick(self, context, discrete_state):
        x = context.get_discrete_state(self._state_index).get_value().copy()
        v_body, omega, sigma, sigma_i = self._truth(context)
        k = int(round(context.get_time() / 0.01))             # tick index from time
        if k % 2 == 0:                                  # 50 Hz odometry
            if self._noise_on:
                n_v = self._rng.normal(0.0, 0.01 + 0.02 * abs(v_body[0]))
                n_s = self._rng.normal(0.0, 0.01)
                self._gyro_bias += self._rng.normal(0.0, np.radians(0.01)) * np.sqrt(0.02)
                n_w = self._rng.normal(0.0, np.radians(0.2))
                x[0] = v_body[0] * (1.0 + self._bias_beta) + n_v
                x[1] = v_body[1] + n_s
                x[2] = omega + self._gyro_bias + n_w
            else:
                x[0:3] = [v_body[0], v_body[1], omega]
        if k % 5 == 1:                                        # 20 Hz direction (+10 ms offset)
            noise = self._rng.normal(0.0, 1.0 / np.sqrt(KAPPA_DIR)) if self._noise_on else 0.0
            x[3] = sigma_i + noise
            x[4] = KAPPA_DIR
        if k % 20 == 2 and context.get_time() >= self._beacon_t_on:   # 5 Hz beacon [SPEC]
            Xs = self._X_in.Eval(context)
            XL = Xs[self._load_idx]
            thL = np.arctan2(XL.rotation().matrix()[1, 0], XL.rotation().matrix()[0, 0])
            if self._noise_on:
                x[5] = XL.translation()[0] + self._rng.normal(0.0, 0.05)
                x[6] = XL.translation()[1] + self._rng.normal(0.0, 0.05)
                x[7] = thL + self._rng.normal(0.0, np.radians(0.5))
            else:
                x[5:8] = [XL.translation()[0], XL.translation()[1], thL]
            x[8] = 1.0
        discrete_state.get_mutable_vector(self._state_index).set_value(x)
