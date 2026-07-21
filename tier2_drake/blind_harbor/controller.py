"""Controller split — plan §3.1: HydroDrag + Thruster (plant-side BY CLASS) and
the sensor-driven EstController (subject to the truth-isolation lint).

HydroDrag: drag forces on every body — physics, legitimately reads plant state.
Thruster:  applies each vessel's commanded (surge force, yaw moment) along its
           TRUE hull axis — physics (a thruster pushes where the hull points);
           the COMMAND carries no truth.
EstController (per agent): commands from SENSORS ONLY — surge = ramped nominal;
           yaw moment u = +k_align·sin(σ̃_i) (weathervane toward the measured
           cable direction; sign: σ_i = θ_load − θ_asv + σ, so raising θ_asv
           lowers σ_i).
"""
from __future__ import annotations

import numpy as np
from pydrake.systems.framework import LeafSystem, BasicVector
from pydrake.common.value import Value
from pydrake.math import RigidTransform
from pydrake.multibody.math import SpatialForce, SpatialVelocity
from pydrake.multibody.plant import ExternallyAppliedSpatialForce

__all__ = ["HydroDrag", "Thruster", "EstController", "PLANT_SIDE_CLASSES"]


class HydroDrag(LeafSystem):
    """Linear drag on load + vessels. Plant-side by class (lint-exempt)."""

    def __init__(self, cfg, load_idx, asv_idxs, gust=None):
        super().__init__()
        self._cfg = cfg
        self._load = load_idx
        self._asvs = asv_idxs
        # gust = (agent_idx, t_start, t_end, Fy_world): a scripted lateral
        # environmental force on one vessel (D10(c) broadside set piece).
        # Plant-side physics by class — truth-free information flow.
        self._gust = tuple(gust) if gust is not None else None
        self._V_in = self.DeclareAbstractInputPort(
            "body_spatial_velocities", Value([SpatialVelocity()]))
        self.DeclareAbstractOutputPort(
            "spatial_forces", lambda: Value([ExternallyAppliedSpatialForce()]),
            self._calc)

    def _calc(self, context, output):
        cfg = self._cfg
        Vs = self._V_in.Eval(context)
        forces = []

        def drag(idx, c_lin, c_ang):
            V = Vs[int(idx)]
            easf = ExternallyAppliedSpatialForce()
            easf.body_index = idx
            easf.p_BoBq_B = np.zeros(3)
            easf.F_Bq_W = SpatialForce(
                np.array([0.0, 0.0, -c_ang * V.rotational()[2]]),
                -c_lin * V.translational())
            forces.append(easf)

        drag(self._load, cfg.drag_lin_load, cfg.drag_ang_load)
        for ai in self._asvs:
            drag(ai, cfg.drag_lin_asv, cfg.drag_ang_asv)
        if self._gust is not None:
            gi, t0, t1, fy = self._gust
            t = context.get_time()
            if t0 <= t <= t1:
                easf = ExternallyAppliedSpatialForce()
                easf.body_index = self._asvs[int(gi)]
                easf.p_BoBq_B = np.zeros(3)
                easf.F_Bq_W = SpatialForce(np.zeros(3), np.array([0.0, fy, 0.0]))
                forces.append(easf)
        output.set_value(forces)


class Thruster(LeafSystem):
    """Applies commanded (surge N, yaw N·m) per vessel along the TRUE hull axis.

    Plant-side by class: reading the pose to EXPRESS a body-fixed thrust in world
    coordinates is physics, not information flow — the command is truth-free.
    Input: commands (2N,) = [surge_0, yaw_0, surge_1, yaw_1, ...].
    """

    def __init__(self, asv_idxs):
        super().__init__()
        self._asvs = asv_idxs
        self._X_in = self.DeclareAbstractInputPort("body_poses", Value([RigidTransform()]))
        self._u = self.DeclareVectorInputPort("commands", BasicVector(2 * len(asv_idxs)))
        self.DeclareAbstractOutputPort(
            "spatial_forces", lambda: Value([ExternallyAppliedSpatialForce()]),
            self._calc)

    def _calc(self, context, output):
        Xs = self._X_in.Eval(context)
        u = self._u.Eval(context)
        forces = []
        for k, ai in enumerate(self._asvs):
            X = Xs[int(ai)]
            th = np.arctan2(X.rotation().matrix()[1, 0], X.rotation().matrix()[0, 0])
            surge, yaw = u[2 * k], u[2 * k + 1]
            easf = ExternallyAppliedSpatialForce()
            easf.body_index = ai
            easf.p_BoBq_B = np.zeros(3)
            easf.F_Bq_W = SpatialForce(
                np.array([0.0, 0.0, yaw]),
                surge * np.array([np.cos(th), np.sin(th), 0.0]))
            forces.append(easf)
        output.set_value(forces)


class EstController(LeafSystem):
    """Per-agent sensor-driven commands: [surge, yaw]. NO plant inputs (linted).

    Fan-holding heading control [DESIGN]: hold the DEPLOYED fan heading θ_ref
    (declared deployment knowledge) using the gyro-integrated own heading θ̂_a —
    pure sensor-side. Pure weathervaning is degenerate (any σ with σ_i = 0 is an
    equilibrium; the ramp transient collapses the fan — measured); holding the
    fan selects the towing equilibrium. Small cable-alignment trim on σ̃_i.
    """

    def __init__(self, thrust_nom: float, thrust_ramp: float, k_heading: float,
                 theta_ref: float, theta_a0: float, *, k_cable: float = 100.0,
                 turn_bias: float = 0.0, turn_amp: float = 0.0,
                 turn_freq: float = 0.05, dogleg=None, decel=None):
        super().__init__()
        self._nom = float(thrust_nom)
        self._ramp = float(thrust_ramp)
        self._kh = float(k_heading)
        self._kc = float(k_cable)
        self._ref = float(theta_ref)
        # persistent-turn maneuver [plan §5.3]: the fan reference rotates at
        # η_ref(t) = bias + amp·sin(freq·t) — never vanishing when bias > amp;
        # shapes must keep moving for the floor cells (D2's premise)
        self._tb, self._ta, self._tf = float(turn_bias), float(turn_amp), float(turn_freq)
        # dogleg = (t_start, duration, angle): smooth heading schedule for the
        # hero transit (plan §7.1 two legs + one 60-deg turn); composes with the
        # persistent-turn terms (normally zero in the hero config)
        self._dogleg = tuple(float(x) for x in dogleg) if dogleg is not None else None
        # decel = (t_start, duration, factor): docking-approach thrust ramp-down
        # (hero v2 — physically extends the beacon convergence window)
        self._decel = tuple(float(x) for x in decel) if decel is not None else None
        self._odom = self.DeclareVectorInputPort("odom", BasicVector(3))
        self._dir = self.DeclareVectorInputPort("direction", BasicVector(2))
        self._state_index = self.DeclareDiscreteState(np.array([theta_a0]))
        self.DeclareVectorOutputPort("command", BasicVector(2), self._calc,
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclarePeriodicDiscreteUpdateEvent(0.02, 0.0, self._tick)

    def _tick(self, context, discrete_state):
        th = context.get_discrete_state(self._state_index).get_value()[0]
        th += self._odom.Eval(context)[2] * 0.02              # gyro integration, 50 Hz
        discrete_state.get_mutable_vector(self._state_index).set_value([th])

    def _calc(self, context, output):
        t = context.get_time()
        th_a = context.get_discrete_state(self._state_index).get_value()[0]
        sig_i = self._dir.Eval(context)[0]
        # integrated turn reference: ref(t) = ref0 + bias·t + (amp/freq)(1−cos(freq·t))
        ref_t = self._ref + self._tb * t + (
            (self._ta / self._tf) * (1.0 - np.cos(self._tf * t)) if self._tf > 0 else 0.0)
        if self._dogleg is not None:
            t1, dur, ang = self._dogleg
            u = min(max((t - t1) / dur, 0.0), 1.0)
            ref_t += ang * 0.5 * (1.0 - np.cos(np.pi * u))
        err = (ref_t - th_a + np.pi) % (2 * np.pi) - np.pi
        surge = self._nom * min(1.0, t / self._ramp)
        if self._decel is not None:
            t0, dur, fac = self._decel
            u = min(max((t - t0) / dur, 0.0), 1.0)
            surge *= 1.0 - (1.0 - fac) * 0.5 * (1.0 - np.cos(np.pi * u))
        yaw = self._kh * err + self._kc * np.sin(sig_i)
        output.set_value([surge, yaw])


PLANT_SIDE_CLASSES = (HydroDrag, Thruster)     # lint-exempt BY CLASS (plan §3.3)
