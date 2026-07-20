"""B1-TRUE — centralized joint filter over ALL agents' raw sensor streams (plan D7).

Offline replay over logged sensors (log_sensors=True build variant). The oracle
grants relative to the decentralized DIEKF-Sigma record:
  (i)  zero comms latency: all 5 radial pairs FRESH every 50 Hz tick
       (the record's neighbors arrive tau-stale through packets);
  (ii) one shared estimate: D == 0 by construction;
  (iii) exact WLS twist covariance driving P (the radial P-block path in
       ec.propagate(xi_est=, Sigma_xi=) — staged off decentralized because CI made
       it gate-negative; centralization removes exactly that pathology).
Scope, stated: per-agent bias states unestimated (the record's aux states are
beacon-only anyway); attach=(0,0) matching the record config. So this bounds the
INFORMATION advantage of centralization, not bias-modeling.

Timing: log rows are PRE-tick snapshots (WS-0), so row kr holds the tick-(kr-1)
write: odom fresh iff (kr-1)%2==0, direction iff (kr-1)%5==1, beacon iff
(kr-1)%20==2 (and valid).
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
import numpy as np
from numpy.linalg import inv as npinv

import estimator_core as ec
from estimator_core.radial import solve_load_twist_wls
from tier2_drake.blind_harbor.s1 import CFG, build_s1
from tier2_drake.blind_harbor.lint import truth_isolation_lint
from tier1_sheaf.core.se2 import SE2, Log, inv
from pydrake.systems.analysis import Simulator

SIG_V2 = 7.0e-4                                # own-rho noise (leaf constant)
SIGMA_PRIOR = np.diag([1.0e-3, 2.5e-3, 1.0e-4])  # slaved-model twist unc. (leaf)
DIR_GAIN = 0.3                                 # sigma_i low-pass at 20 Hz
# The WLS posterior captures measurement noise only; the sigma-chain systematic
# (gyro-bias-integrated theta_a rotating every B row) is unmodeled. Without a
# process floor P starves, the beacon gain vanishes, and the filter diverges
# confidently [measured: |err| 22 m]. Floor = the record's declared Q_WHITE_G
# mapped to twist intensity via tau_corr (=2, propagate default).
from estimator_core.propagate import Q_WHITE_G
SIGMA_FLOOR = np.diag(Q_WHITE_G) / 2.0


def run_logged(cfg, seed):
    diagram, plant, leaves, logs, starts, scen = build_s1(cfg, seed)
    truth_isolation_lint(diagram, plant)
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    lj = plant.GetJointByName("load_joint")
    lj.set_translation(pc, [0.0, 0.0]); lj.set_rotation(pc, 0.0)
    for i in range(cfg["N"]):
        aj = plant.GetJointByName(f"asv_{i}_joint")
        x, y, yaw = starts[i]
        aj.set_translation(pc, [x, y]); aj.set_rotation(pc, yaw)
    sim = Simulator(diagram, ctx)
    sim.Initialize(); sim.AdvanceTo(cfg["Tend"])
    root = sim.get_context()
    g = lambda name: logs[name].FindLog(root).data().T
    return dict(
        ts=logs["truth_hi"].FindLog(root).sample_times(),
        truth=g("truth_hi"),
        odom=[g(f"odom_{i}") for i in range(cfg["N"])],
        dirs=[g(f"dir_{i}") for i in range(cfg["N"])],
        beacon=g("beacon_0"),
        starts=starts,
    )


def b1_replay(cfg, L):
    N = cfg["N"]
    ts, truth = L["ts"], L["truth"]
    st = ec.FilterState.initial(np.array([L["starts"][0][2], 0.0]), cfg["l"])
    theta_a = np.array([L["starts"][i][2] for i in range(N)])
    sigma_i = np.array([L["starts"][i][2] for i in range(N)])  # warm-started below
    warm = np.zeros(N, dtype=bool)

    est_G, est_P, est_t = [], [], []
    for kr in range(1, len(ts)):
        k = kr - 1                                  # tick that wrote this row
        t = ts[kr]
        if k % 5 == 1:                              # 20 Hz direction rows
            for i in range(N):
                z, kap = L["dirs"][i][kr]
                if kap > 0:
                    if not warm[i]:
                        sigma_i[i], warm[i] = z, True
                    else:
                        d = (z - sigma_i[i] + np.pi) % (2 * np.pi) - np.pi
                        sigma_i[i] += DIR_GAIN * d
        if k % 2 == 0:                              # 50 Hz: WLS solve + propagate
            yaw_G = np.arctan2(st.G[1, 0], st.G[0, 0])
            B, R, S2 = [], [], []
            for i in range(N):
                if not warm[i]:
                    continue
                sig = sigma_i[i] + theta_a[i] - yaw_G      # same-instant identity
                z = L["odom"][i][kr]
                B.append([np.cos(sig), np.sin(sig), 0.0])
                R.append(z[0] * np.cos(sigma_i[i]) + z[1] * np.sin(sigma_i[i]))
                S2.append(SIG_V2)
            zeta0 = L["odom"][0][kr]
            if len(B) >= 3:
                # fresh SLAVED-MODEL prior each tick, exactly as the leaf does —
                # chaining xi_prev feeds m_xi back through the prior (eta has no
                # radial information: B[:,2]=0 at attach=(0,0)) and integrates it
                # into a -1.3 rad/s runaway [measured]
                from tier1_sheaf.core.shapes import Ad_m
                sig0 = sigma_i[0] + theta_a[0] - yaw_G
                prior = Ad_m(sig0, sigma_i[0], cfg["l"]) @ zeta0
                xi, Sx = solve_load_twist_wls(np.array(B), np.array(R),
                                              prior, SIGMA_PRIOR, np.array(S2))
                st = ec.propagate(st, zeta0, 0.02, shape_motion_correction=False,
                                  xi_est=xi, Sigma_xi=Sx + SIGMA_FLOOR)
            else:
                st = ec.propagate(st, zeta0, 0.02, shape_motion_correction=False)
            theta_a += 0.02 * np.array([L["odom"][i][kr][2] for i in range(N)])
            # keep the central s-channel on agent 0's chain (used only by clamp/aux)
            yaw_G = np.arctan2(st.G[1, 0], st.G[0, 0])
            st = st.replace(s=np.array([sigma_i[0] + theta_a[0] - yaw_G, sigma_i[0]]))
        if k % 20 == 2:                             # 5 Hz beacon row (agent 0)
            b = L["beacon"][kr]
            if b[3] > 0.5:
                st = ec.update_beacon(st, b[:3])
        if kr % 10 == 0:                            # store at 10 Hz for metrics
            est_G.append(st.G.copy()); est_P.append(st.P[:3, :3].copy())
            est_t.append(t)
    return np.array(est_t), est_G, est_P


def metrics(cfg, L, est_t, est_G, est_P):
    ts, truth = L["ts"], L["truth"]
    anees, errs, drift_pre = [], [], []
    for j, t in enumerate(est_t):
        kr = int(round(t / 0.01))
        if kr >= len(ts):
            continue
        G_true = SE2(truth[kr, 2], truth[kr, 0:2])
        e = Log(est_G[j] @ inv(G_true))
        if t >= cfg["eval_from"]:
            anees.append(float(e @ np.linalg.solve(est_P[j], e)) / 3.0)
            errs.append(np.linalg.norm(e))
        if 0.6 * cfg["t_on"] <= t < cfg["t_on"]:
            drift_pre.append(np.linalg.norm(e[:2]))
    return float(np.mean(anees)), float(np.mean(errs)), float(np.mean(drift_pre))


if __name__ == "__main__":
    cfg = dict(CFG, log_sensors=True)
    rows = []
    for seed in range(3):
        L = run_logged(cfg, seed)
        est_t, est_G, est_P = b1_replay(cfg, L)
        a, e, dr = metrics(cfg, L, est_t, est_G, est_P)
        rows.append(dict(seed=seed, anchored=a, err=e, drift=dr))
        print(f"seed {seed}: anchored ANEES={a:7.3f}  |err|={e:.4f}  "
              f"pre-anchor drift={dr:.2f} m  (D=0 by construction)")
    agg = dict(arm="B1-true centralized WLS (zero-latency, exact Sigma)",
               anchored=float(np.mean([r["anchored"] for r in rows])),
               perp=None, D=0.0,
               drift=float(np.mean([r["drift"] for r in rows])),
               err=float(np.mean([r["err"] for r in rows])), per_seed=rows)
    out = "/workspaces/Anholonomy/tier2_drake/results/s1/b1_true.json"
    json.dump(agg, open(out, "w"), indent=1)
    print("written", out)
