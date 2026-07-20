"""S1 — end-to-end GNSS-denied closed loop, N = 5, cycle graph (plan §5.1 M-FAB).

Full pipeline: plant + HydroDrag/Thruster (plant-side) + per-agent SensorSuite →
EstController (sensor-driven steering) and DIEKFSigmaLeaf (paper rule, CI), with
the comms fabric (per-directed-edge VectorRingDelay on the cycle graph).

M-FAB gates: (i) truth-isolation lint green on the built diagram; (ii) closed
loop runs with cables taut (|dist − L| within SAP tolerance); (iii) determinism;
(iv) D1-pilot ANEES on the gauge complement reported over ≥ 6 seeds.

Run: python3 -m tier2_drake.blind_harbor.s1
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
from pydrake.systems.analysis import Simulator
from pydrake.systems.framework import DiagramBuilder, LeafSystem
from pydrake.systems.primitives import LogVectorOutput
from pydrake.common.value import Value
from pydrake.multibody.plant import (AddMultibodyPlantSceneGraph,
                                     ExternallyAppliedSpatialForce)

import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv
from tier2_drake.harbor import (ScenarioConfig, _planar_box_body, _planar_disk_body,
                                attachment_and_start)
from tier2_drake.blind_harbor.comms import VectorRingDelay, T_C
from tier2_drake.blind_harbor.sensors import SensorSuite
from tier2_drake.blind_harbor.diekf_leaf import DIEKFSigmaLeaf, state_len
from tier2_drake.blind_harbor.controller import HydroDrag, Thruster, EstController
from tier2_drake.blind_harbor.lint import truth_isolation_lint

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results", "s1")

# Tend/t_on sized to the MEASURED pinning-diffusion rate (Cor 5.2: lambda_min
# becomes the rate; network tau ~ 21 s with one 5 Hz anchor vs 4 unanchored
# agents): anchor at 30 s, gate after ~4.8 tau of anchored time (t >= 114 s).
CFG = dict(N=5, Tend=130.0, tau=0.4, l=12.0, kappa_gain=2.0, send_epoch=0.1,
           t_on=30.0, eval_from=114.0, fuse_rule="paper", all_beacons=False,
           turn_bias=0.0, turn_amp=0.0)   # floor cells set turn_bias>0 (maneuver)


class ForceConcat(LeafSystem):
    """Concatenate two ExternallyAppliedSpatialForce lists (plant takes one port)."""

    def __init__(self):
        super().__init__()
        self._a = self.DeclareAbstractInputPort(
            "a", Value([ExternallyAppliedSpatialForce()]))
        self._b = self.DeclareAbstractInputPort(
            "b", Value([ExternallyAppliedSpatialForce()]))
        self.DeclareAbstractOutputPort(
            "combined", lambda: Value([ExternallyAppliedSpatialForce()]),
            lambda c, o: o.set_value(list(self._a.Eval(c)) + list(self._b.Eval(c))))


def build_s1(cfg, master_seed: int):
    # thrust sized for steady v ≈ 0.9 m/s: 5F = (drag_load + 5·drag_asv)·v
    # keeps the tow inside sim_design's declared envelope v ∈ [0.3, 1.2] m/s
    scen = ScenarioConfig(N=cfg["N"], cable_len=cfg["l"], thrust=800.0,
                          formation=cfg.get("formation", "fan"),
                          front_arc=cfg.get("front_arc", 1.15),
                          perturb=cfg.get("perturb", 0.0),
                          dt=cfg.get("h", 1.0e-3))
    N = cfg["N"]
    builder = DiagramBuilder()
    plant, _sg = AddMultibodyPlantSceneGraph(builder, time_step=scen.dt)
    load = _planar_disk_body(plant, "load", scen.load_mass, scen.load_radius,
                             np.array([0.20, 0.28, 0.38, 1.0]))
    asvs = [_planar_box_body(plant, f"asv_{i}", scen.asv_mass, scen.asv_len,
                             scen.asv_wid, np.array([0.75, 0.28, 0.22, 1.0]))
            for i in range(N)]
    attach, starts, angles = attachment_and_start(scen)
    for i in range(N):
        plant.AddDistanceConstraint(load, attach[i], asvs[i], np.zeros(3), scen.cable_len)
    plant.mutable_gravity_field().set_gravity_vector([0, 0, 0])
    plant.Finalize()

    hydro = builder.AddSystem(HydroDrag(scen, load.index(), [b.index() for b in asvs]))
    hydro.set_name("hydro_drag")
    thr = builder.AddSystem(Thruster([b.index() for b in asvs]))
    thr.set_name("thruster")
    cat = builder.AddSystem(ForceConcat())
    builder.Connect(plant.get_body_spatial_velocities_output_port(),
                    hydro.GetInputPort("body_spatial_velocities"))
    builder.Connect(plant.get_body_poses_output_port(), thr.GetInputPort("body_poses"))
    builder.Connect(hydro.GetOutputPort("spatial_forces"), cat.GetInputPort("a"))
    builder.Connect(thr.GetOutputPort("spatial_forces"), cat.GetInputPort("b"))
    builder.Connect(cat.GetOutputPort("combined"),
                    plant.get_applied_spatial_force_input_port())

    # per-agent stacks
    alpha = cfg["kappa_gain"] * cfg["send_epoch"]
    from pydrake.systems.primitives import Multiplexer
    sensors, leaves, ctrls = [], [], []
    t_on = cfg["t_on"]                          # Q8 t_on [DESIGN, declared]
    for i in range(N):
        b_on = t_on if (i == 0 or cfg.get("all_beacons")) else float("inf")
        sens = builder.AddSystem(SensorSuite(master_seed, i, load.index(),
                                             asvs[i].index(), attach[i], noise_on=True,
                                             beacon_t_on=b_on))
        sens.set_name(f"sensors_{i}")
        builder.Connect(plant.get_body_poses_output_port(), sens.GetInputPort("body_poses"))
        builder.Connect(plant.get_body_spatial_velocities_output_port(),
                        sens.GetInputPort("body_spatial_velocities"))
        tsc = cfg.get("thrust_scale") or (1.0,) * N
        ctrl = builder.AddSystem(EstController(scen.thrust * tsc[i], scen.thrust_ramp,
                                               scen.k_align, theta_ref=starts[i][2],
                                               theta_a0=starts[i][2],
                                               turn_bias=cfg.get("turn_bias", 0.0),
                                               turn_amp=cfg.get("turn_amp", 0.0),
                                               dogleg=cfg.get("dogleg")))
        ctrl.set_name(f"est_controller_{i}")
        builder.Connect(sens.GetOutputPort("direction"), ctrl.GetInputPort("direction"))
        builder.Connect(sens.GetOutputPort("odom"), ctrl.GetInputPort("odom"))
        s0 = np.array([starts[i][2], 0.0])
        leaf = builder.AddSystem(DIEKFSigmaLeaf(s0, cfg["l"], alpha, agent_id=i,
                                                n_neighbors=2,
                                                fuse_rule=cfg.get("fuse_rule", "paper"),
                                                covariance="ci", weights="A3",
                                                has_beacon=(i == 0 or bool(cfg.get("all_beacons")))))
        # NOTE: attach deliberately NOT passed yet — the lever+σ̂-reconstruction
        # interplay produced indefinite P [measured]; enable with the radial
        # observer's P-consistency block next session.
        leaf.set_name(f"diekf_{i}")
        builder.Connect(sens.GetOutputPort("odom"), leaf.GetInputPort("odom"))
        builder.Connect(sens.GetOutputPort("direction"), leaf.GetInputPort("direction"))
        if i == 0 or cfg.get("all_beacons"):
            builder.Connect(sens.GetOutputPort("beacon"), leaf.GetInputPort("beacon"))
        sensors.append(sens); leaves.append(leaf); ctrls.append(ctrl)

    mux = builder.AddSystem(Multiplexer([2] * N))
    for i in range(N):
        builder.Connect(ctrls[i].GetOutputPort("command"), mux.get_input_port(i))
    builder.Connect(mux.get_output_port(0), thr.GetInputPort("commands"))

    # comms fabric: cycle graph, one ring per DIRECTED edge; receiver port order
    # [from (j-1) mod N, from (j+1) mod N] — fixed, deterministic
    k_delay = int(round(cfg["tau"] / T_C))
    for j in range(N):
        for slot, src in enumerate(((j - 1) % N, (j + 1) % N)):
            ring = builder.AddSystem(VectorRingDelay(k_delay))
            ring.set_name(f"ring_{src}_to_{j}")
            builder.Connect(leaves[src].GetOutputPort("pkt_out"), ring.GetInputPort("pkt_in"))
            builder.Connect(ring.GetOutputPort("pkt_out"), leaves[j].GetInputPort(f"pkt_in_{slot}"))

    logs = {"truth": LogVectorOutput(plant.get_state_output_port(), builder, 0.1)}
    for i in range(N):
        logs[f"est_{i}"] = LogVectorOutput(leaves[i].GetOutputPort("est"), builder, 0.1)
    if cfg.get("log_sensors"):
        # raw sensor streams for offline baseline replays (B1-true, B3) — logged at
        # the sensor tick (100 Hz base) so odom 50 Hz / dir 20 Hz / beacon 5 Hz rows
        # are all captured; consumers decimate by the k%-pattern in sensors._tick
        for i in range(N):
            logs[f"odom_{i}"] = LogVectorOutput(sensors[i].GetOutputPort("odom"), builder, 0.01)
            logs[f"dir_{i}"] = LogVectorOutput(sensors[i].GetOutputPort("direction"), builder, 0.01)
            logs[f"beacon_{i}"] = LogVectorOutput(sensors[i].GetOutputPort("beacon"), builder, 0.01)
        logs["truth_hi"] = LogVectorOutput(plant.get_state_output_port(), builder, 0.01)
    diagram = builder.Build()
    return diagram, plant, leaves, logs, starts, scen


def run_seed(cfg, master_seed: int):
    diagram, plant, leaves, logs, starts, scen = build_s1(cfg, master_seed)
    truth_isolation_lint(diagram, plant)                      # gate (i), every build
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    lj = plant.GetJointByName("load_joint")
    lj.set_translation(pc, [0.0, 0.0]); lj.set_rotation(pc, 0.0)
    for i in range(cfg["N"]):
        aj = plant.GetJointByName(f"asv_{i}_joint")
        x, y, yaw = starts[i]
        aj.set_translation(pc, [x, y]); aj.set_rotation(pc, yaw)
    sim = Simulator(diagram, ctx)
    t0 = time.perf_counter()
    sim.Initialize(); sim.AdvanceTo(cfg["Tend"])
    wall = time.perf_counter() - t0

    root = sim.get_context()
    truth = logs["truth"].FindLog(root)
    tq = truth.data().T                                       # [q; v] columns
    ts = truth.sample_times()
    ests = [logs[f"est_{i}"].FindLog(root).data().T for i in range(cfg["N"])]
    return dict(ts=ts, truth=tq, ests=ests, wall=wall,
                records=[l.records for l in leaves])


def anees_and_disagreement(cfg, out):
    """D1/D5 metrics per the AUTHOR RULING (covariance-of-record): the GATED
    quantity is ANCHORED full-state ANEES — agent 0 carries the docking beacon
    from t_on = 0.7T (Cor 5.2's single anchor pins the gauge, making full-state
    consistency well-posed); evaluated on the anchored window, all agents (the
    anchor propagates through fusion). Complement-ANEES stays as the ONE-SIDED
    sanity bound (≤ 1.3) and the conservative gap is the reported Rem 6.4
    demonstration. Gauge drift reported pre-anchor.
    """
    N = cfg["N"]
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    T = cfg["Tend"]

    def errs_at(k):
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        return np.array([Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true))
                         for i in range(N)])

    anch, comp, D_all, drift_pre = [], [], [], []
    dof_corr = N / (N - 1.0)
    for k in np.where(ts >= cfg["eval_from"])[0]:
        errs = errs_at(k)
        mean_e = errs.mean(axis=0)
        for i in range(N):
            P_G = ec.unvech(ests[i][k][ec.SL_P])[:3, :3]
            anch.append(float(errs[i] @ np.linalg.solve(P_G, errs[i])) / 3.0)
            e = errs[i] - mean_e
            comp.append(dof_corr * float(e @ np.linalg.solve(P_G, e)) / 3.0)
        D_all.append(np.mean([np.sum((errs[i] - errs[j]) ** 2)
                              for i in range(N) for j in range(i + 1, N)]))
    for k in np.where((ts >= 0.6 * cfg["t_on"]) & (ts < cfg["t_on"]))[0]:
        drift_pre.append(float(np.linalg.norm(errs_at(k).mean(axis=0)[:2])))
    return (float(np.mean(anch)), float(np.mean(comp)), float(np.mean(D_all)),
            float(np.mean(drift_pre)))


def main(seeds=6):
    os.makedirs(OUT, exist_ok=True)
    res = []
    for seed in range(seeds):
        out = run_seed(CFG, seed)
        anees, comp, D, drift = anees_and_disagreement(CFG, out)
        rt = out["wall"] / CFG["Tend"]
        res.append(dict(seed=seed, anees_anchored=anees, anees_perp=comp, D=D,
                        gauge_drift_pre_m=drift, realtime=rt))
        print(f"seed {seed}: ANEES_anchored={anees:7.3f} (GATED)  perp={comp:.3f} (sanity)  "
              f"pre-anchor drift={drift:4.2f} m  {rt:.2f}x RT")
    A = np.array([r["anees_anchored"] for r in res])
    C = np.array([r["anees_perp"] for r in res])
    verdict = dict(seeds=seeds, anees_anchored_mean=float(A.mean()),
                   anees_anchored_per_seed=A.tolist(),
                   anees_perp_mean=float(C.mean()), perp_sanity_le_1p3=bool(C.mean() <= 1.3),
                   gauge_drift_pre_m=[r["gauge_drift_pre_m"] for r in res],
                   gate="[0.8, 5.0] ANCHORED (author-ruled 2026-07-18: Rem 6.4 + the "
                        "measured elimination table justify the ceiling — CI over "
                        "mutually-correlated covariances is structurally optimistic; "
                        "no decentralized CI filter without cross-covariance "
                        "bookkeeping reaches [0.8,1.3] under realistic mismatch)",
                   in_gate=bool(0.8 <= A.mean() <= 5.0), lint="green",
                   note=("gated = anchored full-state ANEES (beacon on agent 0, "
                         "Cor 5.2 pinning); the ceiling is theorem-anchored, not "
                         "tuned — see the covariance-architecture elimination"))
    with open(os.path.join(OUT, "s1_verdict.json"), "w") as f:
        json.dump(verdict, f, indent=1)
    print(f"\nS1/D1-pilot (ANCHORED per author ruling): mean = {A.mean():.3f}  "
          f"gate [0.8, 5.0] (ruled) -> {'IN' if verdict['in_gate'] else 'OUT (reported, R4)'}  |  "
          f"perp sanity {C.mean():.3f} <= 1.3: {verdict['perp_sanity_le_1p3']}")


if __name__ == "__main__":
    main()


def floor_metrics(cfg, out):
    """Floor-cell metrics (GNSS-denied, no anchor): D_ss on the eval window +
    the per-edge m=2 holonomy amplitude from FusionRecords is computed offline."""
    N = cfg["N"]
    ts, ests = out["ts"], out["ests"]
    D_all = []
    for k in np.where(ts >= cfg["eval_from"])[0]:
        Gs = [ests[i][k][ec.SL_G].reshape(3, 3) for i in range(N)]
        D_all.append(np.mean([np.sum(Log(inv(Gs[i]) @ Gs[j]) ** 2)
                              for i in range(N) for j in range(i + 1, N)]))
    return float(np.mean(D_all))


def m5_amplitude(cfg, out):
    """D3/M5: closed-loop holonomy amplitude from the LOGGED applied transports.

    Per adjacent pair (i, j), each i<-j fuse event is matched with the nearest
    j<-i event; the m=2 round-trip holonomy Hol = Exp(T_i)·Exp(T_j) and its
    log-norm is the PROV amplitude (Thm 7.2's own object — leading-order,
    deterministic; measured here under closed-loop noise: "consistent with").
    Mean over the eval window.
    """
    from tier1_sheaf.core.se2 import Exp as _E, Log as _L
    N = cfg["N"]
    t0 = cfg["eval_from"]
    amps = []
    for i in range(N):
        j = (i + 1) % N
        ev_ij = [(r.t, r.transport_log) for r in out["records"][i]
                 if r.sender == j and r.t >= t0]
        ev_ji = [(r.t, r.transport_log) for r in out["records"][j]
                 if r.sender == i and r.t >= t0]
        if not ev_ij or not ev_ji:
            continue
        tj = np.array([e[0] for e in ev_ji])
        for t_i, T_i in ev_ij:
            k = int(np.argmin(np.abs(tj - t_i)))
            if abs(tj[k] - t_i) > 0.2:
                continue
            # the m=2 closed-walk DEFECT: forward transport composed with the
            # INVERSE of the return transport — identity iff the two agents'
            # applied transports agree (the sum form scales as 2aξ and is
            # meaningless — measured slope exactly 1, the fingerprint)
            Hol = _E(T_i) @ _E(-ev_ji[k][1])
            amps.append(np.linalg.norm(_L(Hol)))
    return float(np.mean(amps)) if amps else float("nan")
