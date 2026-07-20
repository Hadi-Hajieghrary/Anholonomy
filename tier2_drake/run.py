"""Run an N-vessel transit, recover cable tensions analytically, log everything.

Tension recovery (plan §3.2.2): from the constrained dynamics M v̇ + C v = τ_app + Jᵀλ
with J v = 0 ⇒ J v̇ + J̇ v = 0, eliminate v̇ to get
    λ = −(J M⁻¹ Jᵀ)⁻¹ [ J̇v + J M⁻¹ (τ_app − C v) ],   T_k = −λ_k  (≥0 ⇔ taut).
All terms come from documented MultibodyPlant queries — no private solver field.
Gravity is zero (planar), so τ_g = 0.
"""
from __future__ import annotations

import numpy as np
from pydrake.systems.analysis import Simulator
from pydrake.multibody.tree import JacobianWrtVariable

from tier2_drake.harbor import (
    ScenarioConfig, build_scenario, set_initial_state, TowController)


def _cable_jacobian_and_bias(plant, pc, info):
    """Assemble J (Ncable x nv) and J̇v (Ncable,) for the distance constraints."""
    cfg = info["cfg"]
    W = plant.world_frame()
    load_frame = info["load"].body_frame()
    N = cfg.N
    nv = plant.num_velocities()
    J = np.zeros((N, nv))
    Jdotv = np.zeros(N)
    for k in range(N):
        asv_frame = info["asvs"][k].body_frame()
        p_attach = info["attach"][k]                       # in load frame
        # world positions of the two cable endpoints
        p_asv_W = plant.CalcPointsPositions(pc, info["asvs"][k].body_frame(),
                                            np.zeros(3), W).ravel()
        p_att_W = plant.CalcPointsPositions(pc, load_frame, p_attach, W).ravel()
        d = p_asv_W - p_att_W
        dist = np.linalg.norm(d)
        dhat = d / dist
        # translational Jacobians of each endpoint (3 x nv)
        Jp_asv = plant.CalcJacobianTranslationalVelocity(
            pc, JacobianWrtVariable.kV, asv_frame, np.zeros(3), W, W)
        Jp_att = plant.CalcJacobianTranslationalVelocity(
            pc, JacobianWrtVariable.kV, load_frame, p_attach, W, W)
        J[k, :] = dhat @ (Jp_asv - Jp_att)
        # bias terms J̇v of each endpoint
        av_asv = plant.CalcBiasTranslationalAcceleration(
            pc, JacobianWrtVariable.kV, asv_frame, np.zeros(3), W, W).ravel()
        av_att = plant.CalcBiasTranslationalAcceleration(
            pc, JacobianWrtVariable.kV, load_frame, p_attach, W, W).ravel()
        v = plant.GetVelocities(pc)
        dvel = (Jp_asv - Jp_att) @ v
        # J̇v along the cable = dhat·(bias accel diff) + (ḋhat·relative vel)
        ddot = dvel / dist
        dhat_dot = (dvel - (dvel @ dhat) * dhat) / dist
        Jdotv[k] = dhat @ (av_asv - av_att) + dhat_dot @ dvel
    return J, Jdotv


def _applied_generalized_forces(plant, pc, info, ctrl, ctrl_ctx):
    """Map the controller's ExternallyAppliedSpatialForce list to tau_app (nv,)."""
    forces = ctrl.GetOutputPort("spatial_forces").Eval(ctrl_ctx)
    tau = np.zeros(plant.num_velocities())
    for f in forces:
        body = plant.get_body(f.body_index)
        Js = plant.CalcJacobianSpatialVelocity(
            pc, JacobianWrtVariable.kV, body.body_frame(), f.p_BoBq_B,
            plant.world_frame(), plant.world_frame())            # 6 x nv
        wrench = np.concatenate([f.F_Bq_W.rotational(), f.F_Bq_W.translational()])
        tau += Js.T @ wrench
    return tau


def tensions(plant, pc, info, ctrl, ctrl_ctx):
    J, Jdotv = _cable_jacobian_and_bias(plant, pc, info)
    M = plant.CalcMassMatrix(pc)
    Cv = plant.CalcBiasTerm(pc)
    tau = _applied_generalized_forces(plant, pc, info, ctrl, ctrl_ctx)
    Minv = np.linalg.inv(M)
    A = J @ Minv @ J.T
    b = Jdotv + J @ Minv @ (tau - Cv)
    lam = -np.linalg.solve(A, b)
    return -lam                                              # T_k = -lambda_k


def run_transit(cfg: ScenarioConfig, Tend=40.0, log_dt=0.1):
    diagram, plant, sg, info = build_scenario(cfg)
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    set_initial_state(plant, pc, info)
    sim = Simulator(diagram, ctx)
    sim.Initialize()
    ctrl = next(s for s in diagram.GetSystems() if isinstance(s, TowController))

    ts, load_pose, asv_pose, ten = [], [], [], []
    t = 0.0
    while t <= Tend + 1e-9:
        sim.AdvanceTo(t)
        root = sim.get_context()
        pcc = plant.GetMyContextFromRoot(root)
        ctrl_ctx = ctrl.GetMyContextFromRoot(root)
        lj = plant.GetJointByName("load_joint")
        load_pose.append([*lj.get_translation(pcc), lj.get_rotation(pcc)])
        aps = []
        for i in range(cfg.N):
            aj = plant.GetJointByName(f"asv_{i}_joint")
            aps.append([*aj.get_translation(pcc), aj.get_rotation(pcc)])
        asv_pose.append(aps)
        ten.append(tensions(plant, pcc, info, ctrl, ctrl_ctx))
        ts.append(t)
        t += log_dt
    return {
        "t": np.array(ts),
        "load": np.array(load_pose),          # (T,3): x,y,yaw
        "asv": np.array(asv_pose),            # (T,N,3)
        "tension": np.array(ten),             # (T,N)
        "attach": np.array([a[:2] for a in info["attach"]]),
        "cfg": cfg,
    }
