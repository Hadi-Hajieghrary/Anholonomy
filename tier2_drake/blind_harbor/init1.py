"""INIT-1 — shape bootstrap from the tension-direction channel (plan §5.1, wk 2).

ŝ₀ estimation during a declared 10 s straight-tow calibration segment (before
the GNSS-denial clock): σ̂_i = circular mean of the 20 Hz direction channel;
σ̂ = formation prior (the deployed fan angle — deployment knowledge, declared).
Gate: median ŝ error < 2°, max < 5°, across 50 seeds × N ∈ {4, 5}.

Run: python3 -m tier2_drake.blind_harbor.init1
"""
from __future__ import annotations

import json
import os
import numpy as np
from pydrake.systems.analysis import Simulator
from pydrake.systems.framework import DiagramBuilder
from pydrake.systems.primitives import LogVectorOutput
from pydrake.multibody.plant import AddMultibodyPlantSceneGraph

from tier2_drake.harbor import (ScenarioConfig, _planar_box_body, _planar_disk_body,
                                attachment_and_start, TowController)
from tier2_drake.blind_harbor.sensors import SensorSuite

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results", "init1")

T_CAL = 10.0          # the declared calibration segment (s)


def build_scene_with_sensors(N: int, master_seed: int):
    scen = ScenarioConfig(N=N, thrust_frame="body_weathervane")
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

    ctrl = builder.AddSystem(TowController(plant, scen, load.index(),
                                           [b.index() for b in asvs]))
    builder.Connect(plant.get_body_spatial_velocities_output_port(),
                    ctrl.GetInputPort("body_spatial_velocities"))
    builder.Connect(plant.get_body_poses_output_port(), ctrl.GetInputPort("body_poses"))
    builder.Connect(ctrl.GetOutputPort("spatial_forces"),
                    plant.get_applied_spatial_force_input_port())

    logs = []
    for i in range(N):
        sens = builder.AddSystem(SensorSuite(master_seed, i, load.index(),
                                             asvs[i].index(), attach[i], noise_on=True))
        builder.Connect(plant.get_body_poses_output_port(), sens.GetInputPort("body_poses"))
        builder.Connect(plant.get_body_spatial_velocities_output_port(),
                        sens.GetInputPort("body_spatial_velocities"))
        logs.append((LogVectorOutput(sens.GetOutputPort("direction"), builder, 0.05),
                     LogVectorOutput(sens.GetOutputPort("odom"), builder, 0.02)))
    diagram = builder.Build()
    return diagram, plant, logs, starts, angles, scen, attach


def truth_shapes(plant, pc, attach_pts, N):
    """(sigma, sigma_i) per agent from plant poses (same convention as sensors)."""
    lj = plant.GetJointByName("load_joint")
    xL = np.array(lj.get_translation(pc)); thL = lj.get_rotation(pc)
    Rl = np.array([[np.cos(thL), -np.sin(thL)], [np.sin(thL), np.cos(thL)]])
    out = []
    for i in range(N):
        aj = plant.GetJointByName(f"asv_{i}_joint")
        xA = np.array(aj.get_translation(pc)); thA = aj.get_rotation(pc)
        d = xA - (xL + Rl @ np.asarray(attach_pts[i])[:2])
        sigma = np.arctan2(d[1], d[0]) - thL
        sigma_i = thL - thA + sigma
        out.append((sigma, sigma_i))
    return np.array(out)


def one_run(N: int, seed: int):
    diagram, plant, logs, starts, angles, scen, attach = build_scene_with_sensors(N, seed)
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    lj = plant.GetJointByName("load_joint")
    lj.set_translation(pc, [0.0, 0.0]); lj.set_rotation(pc, 0.0)
    for i in range(N):
        aj = plant.GetJointByName(f"asv_{i}_joint")
        x, y, yaw = starts[i]
        aj.set_translation(pc, [x, y]); aj.set_rotation(pc, yaw)
    sim = Simulator(diagram, ctx); sim.Initialize(); sim.AdvanceTo(T_CAL)

    pcc = plant.GetMyContextFromRoot(sim.get_context())
    s_true = truth_shapes(plant, pcc, attach, N)

    errs = []
    for i in range(N):
        dir_log, odom_log = logs[i]
        log = dir_log.FindLog(sim.get_context())
        arr = log.data().T           # columns [sigma_i_meas, kappa]
        ts = log.sample_times()
        good = (ts > 0.6 * T_CAL) & (arr[:, 1] > 0)  # settled window, valid channel
        samples = arr[good, 0]
        sig_i_hat = np.arctan2(np.mean(np.sin(samples)), np.mean(np.cos(samples)))
        # refined sigma (plan: 'formation prior refined by 20 Hz updates'):
        # theta_asv-hat = deployed yaw + integral of the measured gyro (declared
        # calibration knowledge, pre-denial); sigma = theta_asv - theta_load + sigma_i
        olog = odom_log.FindLog(sim.get_context())
        om = olog.data().T[:, 2]                     # measured yaw rate at 50 Hz
        theta_asv_hat = starts[i][2] + np.sum(om) * 0.02
        sig_hat = theta_asv_hat - 0.0 + sig_i_hat    # theta_load(0) = 0 declared
        e_sig = abs((sig_hat - s_true[i, 0] + np.pi) % (2 * np.pi) - np.pi)
        e_sig_i = abs((sig_i_hat - s_true[i, 1] + np.pi) % (2 * np.pi) - np.pi)
        errs.append((np.degrees(e_sig), np.degrees(e_sig_i)))
    return np.array(errs)            # (N, 2) degrees


def main(seeds=50):
    os.makedirs(OUT, exist_ok=True)
    all_errs = {}
    for N in (4, 5):
        E = np.concatenate([one_run(N, s) for s in range(seeds)], axis=0)
        all_errs[N] = E
        med = np.median(E, axis=0); mx = np.max(E, axis=0)
        print(f"N={N}: median err (deg)  sigma={med[0]:.3f}  sigma_i={med[1]:.3f} | "
              f"max  sigma={mx[0]:.3f}  sigma_i={mx[1]:.3f}")
    med_all = np.median(np.vstack(list(all_errs.values())), axis=0)
    max_all = np.max(np.vstack(list(all_errs.values())), axis=0)
    ok = (med_all < 2.0).all() and (max_all < 5.0).all()
    verdict = dict(median_deg=dict(sigma=float(med_all[0]), sigma_i=float(med_all[1])),
                   max_deg=dict(sigma=float(max_all[0]), sigma_i=float(max_all[1])),
                   seeds=seeds, gate="median<2deg, max<5deg", passed=bool(ok))
    with open(os.path.join(OUT, "init1_verdict.json"), "w") as f:
        json.dump(verdict, f, indent=1)
    print(f"INIT-1 gate: {'PASS' if ok else 'FAIL'}  "
          f"(median {med_all.round(3)}, max {max_all.round(3)} deg)")
    if not ok:
        print("contingency (pre-declared): promote the cable-angle sensor into the "
              "default suite and document in both papers — never silently tune.")
    return ok


if __name__ == "__main__":
    main()
