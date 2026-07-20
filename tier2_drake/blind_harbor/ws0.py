"""WS-0 walking skeleton — plan §5.1, milestone 1.

One ASV + pentagon + 1 cable on the existing plant; minimal estimator_core P/U/F
inside DIEKFSigmaLeaf; VectorRingDelay in loopback (self-edge); parquet + manifest.

Gates (hard):
  (a) bit-identical parquet on replay (same config+seed, fresh build);
  (b) adapter parity <= 1e-12 vs the open-loop NumPy core on the logged streams;
  (c) wall-clock per simulated second measured and recorded.

Run: python3 -m tier2_drake.blind_harbor.ws0
"""
from __future__ import annotations

import hashlib
import json
import os
import time

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from pydrake.systems.analysis import Simulator
from pydrake.systems.framework import DiagramBuilder
from pydrake.systems.primitives import LogVectorOutput

import estimator_core as ec
from tier2_drake.harbor import ScenarioConfig, build_scenario, set_initial_state
from tier2_drake.blind_harbor.comms import VectorRingDelay, T_C
from tier2_drake.blind_harbor.sensors import SensorSuite
from tier2_drake.blind_harbor.diekf_leaf import DIEKFSigmaLeaf, state_len

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results", "ws0")

CFG = dict(master_seed=42, Tend=30.0, tau=0.4, l=12.0, kappa_gain=2.0,
           send_epoch=0.1, noise_on=True)


def build_ws0(cfg):
    """The WS-0 diagram: scene + sensors + estimator + loopback ring."""
    from pydrake.multibody.plant import AddMultibodyPlantSceneGraph
    from tier2_drake.harbor import (_planar_box_body, _planar_disk_body,
                                    attachment_and_start, TowController)

    scen = ScenarioConfig(N=1, cable_len=cfg["l"])
    builder = DiagramBuilder()
    plant, _sg = AddMultibodyPlantSceneGraph(builder, time_step=scen.dt)
    load = _planar_disk_body(plant, "load", scen.load_mass, scen.load_radius,
                             np.array([0.20, 0.28, 0.38, 1.0]))
    asv = _planar_box_body(plant, "asv_0", scen.asv_mass, scen.asv_len, scen.asv_wid,
                           np.array([0.75, 0.28, 0.22, 1.0]))
    attach, starts, _ = attachment_and_start(scen)
    plant.AddDistanceConstraint(load, attach[0], asv, np.zeros(3), scen.cable_len)
    plant.mutable_gravity_field().set_gravity_vector([0, 0, 0])
    plant.Finalize()

    ctrl = builder.AddSystem(TowController(plant, scen, load.index(), [asv.index()]))
    builder.Connect(plant.get_body_spatial_velocities_output_port(),
                    ctrl.GetInputPort("body_spatial_velocities"))
    builder.Connect(plant.get_body_poses_output_port(), ctrl.GetInputPort("body_poses"))
    builder.Connect(ctrl.GetOutputPort("spatial_forces"),
                    plant.get_applied_spatial_force_input_port())

    sensors = builder.AddSystem(SensorSuite(cfg["master_seed"], 0, load.index(),
                                            asv.index(), attach[0], noise_on=cfg["noise_on"]))
    builder.Connect(plant.get_body_poses_output_port(), sensors.GetInputPort("body_poses"))
    builder.Connect(plant.get_body_spatial_velocities_output_port(),
                    sensors.GetInputPort("body_spatial_velocities"))

    alpha = cfg["kappa_gain"] * cfg["send_epoch"]             # derived, never a literal
    s0 = np.array([starts[0][2], 0.0])                        # crude shape prior (WS-0)
    leaf = builder.AddSystem(DIEKFSigmaLeaf(s0, cfg["l"], alpha))
    builder.Connect(sensors.GetOutputPort("odom"), leaf.GetInputPort("odom"))
    builder.Connect(sensors.GetOutputPort("direction"), leaf.GetInputPort("direction"))

    k_delay = int(round(cfg["tau"] / T_C))
    ring = builder.AddSystem(VectorRingDelay(k_delay))
    builder.Connect(leaf.GetOutputPort("pkt_out"), ring.GetInputPort("pkt_in"))
    builder.Connect(ring.GetOutputPort("pkt_out"), leaf.GetInputPort("pkt_in_0"))

    logs = {
        "est": LogVectorOutput(leaf.GetOutputPort("est"), builder, 0.01),
        "odom": LogVectorOutput(sensors.GetOutputPort("odom"), builder, 0.01),
        "direction": LogVectorOutput(sensors.GetOutputPort("direction"), builder, 0.01),
        "pkt": LogVectorOutput(ring.GetOutputPort("pkt_out"), builder, 0.01),
    }
    diagram = builder.Build()
    return diagram, plant, leaf, logs, starts


def run_once(cfg, tag):
    t0 = time.perf_counter()
    diagram, plant, leaf, logs, starts = build_ws0(cfg)
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    lj = plant.GetJointByName("load_joint")
    lj.set_translation(pc, [0.0, 0.0]); lj.set_rotation(pc, 0.0)
    aj = plant.GetJointByName("asv_0_joint")
    x, y, yaw = starts[0]
    aj.set_translation(pc, [x, y]); aj.set_rotation(pc, yaw)

    sim = Simulator(diagram, ctx)
    sim.Initialize()
    sim.AdvanceTo(cfg["Tend"])
    wall = time.perf_counter() - t0

    data = {}
    for name, sink in logs.items():
        log = sink.FindLog(sim.get_context())
        data[name] = (log.sample_times().copy(), log.data().T.copy())

    os.makedirs(OUT, exist_ok=True)
    tables = {}
    for name, (ts, arr) in data.items():
        cols = {"t": ts}
        for j in range(arr.shape[1]):
            cols[f"c{j}"] = arr[:, j]
        tables[name] = pa.table(cols)
    path = os.path.join(OUT, f"ws0_{tag}.parquet")
    pq.write_table(tables["est"], path)                       # gate (a) hashes est
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()

    manifest = dict(cfg=cfg, tag=tag, sha256=digest, wall_s=wall,
                    sim_s=cfg["Tend"], realtime_factor=wall / cfg["Tend"],
                    n_fusion_records=len(leaf.records))
    with open(os.path.join(OUT, f"manifest_{tag}.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    return data, digest, wall, leaf


def replay_parity(cfg, data):
    """Gate (b): drive estimator_core open-loop with the logged streams.

    Log-alignment model (established empirically, first-error = Q_G[0]*dt
    fingerprint): LogVectorOutput rows at t_k are PRE-tick snapshots — est[k]
    is the state BEFORE tick k, and row k carries exactly the upstream values
    tick k consumed (post-tick-(k-1) under pre-update semantics). Replay
    therefore runs tick k on row-k inputs and compares against est[k+1].
    """
    ts, est = data["est"]
    _, odom = data["odom"]
    _, dirn = data["direction"]
    _, pkt = data["pkt"]
    alpha = cfg["kappa_gain"] * cfg["send_epoch"]

    st = ec.vec_to_core(est[0, :ec.CORE_LEN], cfg["l"], 0.0)   # pre-tick-0 core
    last_stamp = est[0, ec.CORE_LEN + 1]                       # stamps follow state_time
    pair = np.zeros(4)                                          # single neighbor

    worst = 0.0
    for k in range(len(ts) - 1):
        t = round(k * 0.01, 10)
        stamp, sender, G_nb, P_nb, s_nb, b_nb, rho_nb, mxi_nb, valid = ec.unpack(pkt[k])
        if valid and stamp > last_stamp:
            age = t - stamp
            pair = np.array([b_nb[0], b_nb[1], b_nb[2], rho_nb])
            if np.any(mxi_nb):
                st = st.replace(m_xi=0.9 * st.m_xi + 0.1 * mxi_nb)
            st, rec = ec.fuse_paper(st, G_nb, s_nb, age, odom[k], alpha, 1.0, sender)
            P_new, _ = ec.ci_fuse_G(st.P, P_nb[:3, :3], age)   # mirror the leaf's CI
            st = st.replace(P=P_new)
            last_stamp = stamp
        if k % 2 == 0:
            zeta = odom[k]
            zc = np.array([zeta[0] * (1.0 - st.beta) - st.m_v, zeta[1],
                           zeta[2] - st.bg])
            b_own, rho_own = ec.radial_pair(st, zc)
            B = [b_own]; R = [rho_own]
            if np.any(pair[:3]):
                B.append(pair[:3]); R.append(pair[3])
            from tier1_sheaf.core.shapes import Ad_m
            xi_prior = Ad_m(st.s[0], st.s[1], st.l) @ zc      # slaved-model prior
            SIG_V2 = 7.0e-4
            Q_XI_STALE = 1.0e-4
            sig2 = [SIG_V2]
            if np.any(pair[:3]):
                sig2.append(SIG_V2 + Q_XI_STALE * 0.4 ** 2)
            SIGMA_PRIOR = np.diag([1.0e-3, 2.5e-3, 1.0e-4])  # lat = Friedland-measured 0.05 m/s
            # RADIAL P-BLOCK STAGED (gate-neutral-to-negative on the anchored
            # metric: 7.7 vs the 3.8-class record; drift BETTER 1.39 vs 1.73).
            # The residual gate gap is CI-over-correlated-covariances — Rem 6.4,
            # proven fundamental by elimination. Re-enable by calling
            # solve_load_twist_wls and passing (xi_est, Sigma_xi, tau_corr).
            _ = ec.solve_load_twist_wls          # keep the import surface alive
            st = ec.propagate(st, zeta, 0.02, shape_motion_correction=False)
        if k % 5 == 1:
            st = ec.update_direction(st, dirn[k][0], dirn[k][1])
        ref = est[k + 1]
        err = float(np.max(np.abs(ec.core_to_vec(st) - ref[:ec.CORE_LEN])))
        worst = max(worst, err)
    return worst


def main():
    print("=== WS-0 walking skeleton (plan §5.1) ===")
    data1, h1, wall1, leaf1 = run_once(CFG, "run1")
    data2, h2, wall2, _ = run_once(CFG, "run2")

    ok_a = (h1 == h2)
    print(f"gate (a) bit-identical parquet: {'PASS' if ok_a else 'FAIL'}  ({h1[:16]}…)")

    worst = replay_parity(CFG, data1)
    ok_b = worst <= 1e-12
    print(f"gate (b) adapter parity: {'PASS' if ok_b else 'FAIL'}  worst |Δ| = {worst:.3e}")

    rt = wall1 / CFG["Tend"]
    print(f"gate (c) wall-clock: {wall1:.1f} s for {CFG['Tend']:.0f} s sim "
          f"=> {rt:.2f}x real-time at N=1 (recorded; threshold 12x applies at N=5)")
    print(f"fusion records: {len(leaf1.records)}  "
          f"(realized ages: {sorted({round(r.realized_age, 3) for r in leaf1.records[:200]})})")
    assert ok_a and ok_b, "WS-0 gate failure"
    print("WS-0: ALL GATES PASS")


if __name__ == "__main__":
    main()
