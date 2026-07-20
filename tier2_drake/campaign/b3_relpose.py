"""B3 — synthetic relative-pose DInEKF baseline.  ** WIP — DESIGN INCOMPLETE **

DO NOT cite numbers from this driver in any table. Status 2026-07-20: two real
bugs found and fixed during bring-up (systematic v*tau along-track pull from
comparing current measurements against delayed estimates; neighbor-frame
residual applied un-transported — the 10-20 m lever mis-rotates corrections).
A third, structural defect remains: the load-yaw derivation theta_L = phi - ray
assumes vessels sit radially on their attach rays, which the settled fan does
not (sigma != ray at the operating point). The load derivation needs the joint
geometric solve over the full cable spread. Best-yet: err 16.8 m vs record
0.183 m — NOT a valid competitor measurement.

Original design notes (plan §3.1/D7; QD2's granted sensor):

The competitor architecture the BHT novelty premise is measured against: vessels
estimate their OWN poses on the comms graph using odometry dead-reckoning plus a
1 Hz relative SE(2) sensor (sigma = 0.1 m, 0.1 m, 1 deg — plan §3.4, B3 only),
then derive the load pose geometrically:

  world cable angle   phi_j = psi_j + sigma_i,j        (own yaw + body cable angle)
  load yaw            theta_L = mean_j wrap(phi_j - ray_j)   (deployment knowledge:
                      the attach-ray angles ray_j, the same knowledge the record's
                      fan-hold controller declares)
  load position       p_L = mean over OWN + received fixes of p_j - l*u(phi_j)

Exchange (1 Hz, same comms fabric): own pose estimate + own (phi, fix) — so the
relative sensor corrects the vessel graph, and the load derivation pools fixes.
Beacon (agent 0, 5 Hz, post t_on): load-pose fix inverted through own geometry
to an own-pose update.

Scope, disclosed: run as an OFFLINE REPLAY over logged sensor streams
(log_sensors=True runs); relative poses synthesized from truth_hi + declared
noise; comms delay tau applied to exchanged estimates; ANEES column N/A in v1
(the derived G-hat has no principled composite covariance yet).
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np

from tier1_sheaf.core.se2 import SE2, Log, Exp, inv
from tier2_drake.harbor import attachment_and_start, ScenarioConfig
from tier2_drake.campaign.b1_true import run_logged          # logged-stream runner
from tier2_drake.blind_harbor.s1 import CFG

OUT = "/workspaces/Anholonomy/tier2_drake/results/s1/b3_relpose.json"
REL_R = np.diag([0.1 ** 2, 0.1 ** 2, np.radians(1.0) ** 2])
REL_HZ_TICKS = 100                                       # 1 Hz on the 100 Hz grid


def _wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def b3_replay(cfg, L, seed):
    N = cfg["N"]
    l = cfg["l"]
    ts, truth = L["ts"], L["truth"]
    rng = np.random.default_rng(np.random.SeedSequence([seed, 23]))
    scen = ScenarioConfig(N=N, cable_len=l, formation=cfg.get("formation", "fan"),
                          front_arc=cfg.get("front_arc", 1.15),
                          perturb=cfg.get("perturb", 0.0))
    _, starts, rays = attachment_and_start(scen)
    lag = int(round(cfg["tau"] / 0.01))                  # comms delay in ticks

    X = [SE2(starts[j][2], np.array(starts[j][:2])) for j in range(N)]
    P = [np.diag([0.05, 0.05, 0.01]) for _ in range(N)]
    Q = np.diag([2e-4, 2e-4, 5e-6])
    sig_i = [0.0] * N                                    # direction low-pass
    warm = [False] * N
    hist = []                                            # (X list, fix list) per tick

    est_G, est_t = [], []
    for kr in range(1, len(ts)):
        k = kr - 1
        t = ts[kr]
        if k % 2 == 0:                                   # 50 Hz odometry dead-reckon
            for j in range(N):
                z = L["odom"][j][kr]
                X[j] = X[j] @ Exp(0.02 * np.array([z[0], z[1], z[2]]))
                P[j] = P[j] + Q * 0.02
        if k % 5 == 1:                                   # 20 Hz direction channel
            for j in range(N):
                zd, kap = L["dirs"][j][kr]
                if kap > 0:
                    if not warm[j]:
                        sig_i[j], warm[j] = zd, True
                    else:
                        sig_i[j] += 0.3 * _wrap(zd - sig_i[j])
        if k % REL_HZ_TICKS == 2:                        # 1 Hz relative-pose graph
            # DELAY-CONSISTENT update: the innovation lives entirely at t - tau
            # (measurement synthesized THEN, both estimates from history THEN);
            # the correction transports to now through the odometry composition
            # (first-order in tau). Comparing a current measurement against a
            # delayed estimate injects a systematic v*tau along-track pull every
            # exchange and diverges [measured: err 217 m].
            idx = kr - lag
            if 0 <= idx < len(hist):
                kd = idx
                for j in range(N):
                    for src in ((j - 1) % N, (j + 1) % N):
                        Xt_j = SE2(truth[kd, 5 + 3 * j], truth[kd, 3 + 3 * j:5 + 3 * j])
                        Xt_s = SE2(truth[kd, 5 + 3 * src], truth[kd, 3 + 3 * src:5 + 3 * src])
                        z_rel = Log(inv(Xt_j) @ Xt_s) + rng.multivariate_normal(
                            np.zeros(3), REL_R)
                        X_own_then, P_own_then = hist[idx][j]
                        X_nb_then, P_nb_then = hist[idx][src]
                        # OWN-frame residual: X_meas_own = X_nb * Exp(-z_rel);
                        # expressing the residual in the neighbor frame and
                        # applying it un-transported mis-rotates the correction
                        # by the 10-20 m inter-vessel lever [measured: 279 m]
                        r = Log(inv(X_own_then) @ X_nb_then @ Exp(-z_rel))
                        S = P_own_then + P_nb_then + REL_R
                        K = P_own_then @ np.linalg.inv(S)
                        X[j] = X[j] @ Exp(K @ r)
                        IK = np.eye(3) - K
                        P[j] = IK @ P[j] @ IK.T + K @ (P_nb_then + REL_R) @ K.T
        if k % 20 == 2:                                  # 5 Hz beacon (agent 0)
            b = L["beacon"][kr]
            if b[3] > 0.5:
                # load fix -> own-pose fix through own cable geometry
                phi = np.arctan2(X[0].mat[1, 0] if hasattr(X[0], "mat") else X[0][1, 0],
                                 X[0][0, 0]) + sig_i[0]
                pv = np.array([b[0] + l * np.cos(phi), b[1] + l * np.sin(phi)])
                zX = SE2(np.arctan2(X[0][1, 0], X[0][0, 0]), pv)  # position fix only
                r = Log(inv(X[0]) @ zX)
                Rb = np.diag([0.05 ** 2 + (l * np.radians(1)) ** 2] * 2 + [1e6])
                S = P[0] + Rb
                K = P[0] @ np.linalg.inv(S)
                X[0] = X[0] @ Exp(K @ r)
                IK = np.eye(3) - K
                P[0] = IK @ P[0] @ IK.T + K @ Rb @ K.T
        hist.append([(X[j].copy(), P[j].copy()) for j in range(N)])

        if kr % 10 == 0:                                 # 10 Hz: derive G-hat per agent
            Gs = []
            for j in range(N):
                psi = np.arctan2(X[j][1, 0], X[j][0, 0])
                phi = psi + sig_i[j]
                pL = X[j][:2, 2] - l * np.array([np.cos(phi), np.sin(phi)])
                thL = _wrap(phi - rays[j])
                Gs.append(SE2(thL, pL))
            est_G.append(Gs); est_t.append(t)
    return np.array(est_t), est_G


def metrics(cfg, L, est_t, est_G):
    ts, truth = L["ts"], L["truth"]
    N = cfg["N"]
    errs, D_all, drift = [], [], []
    for jj, t in enumerate(est_t):
        kr = int(round(t / 0.01))
        if kr >= len(ts):
            continue
        G_true = SE2(truth[kr, 2], truth[kr, 0:2])
        e = [Log(est_G[jj][i] @ inv(G_true)) for i in range(N)]
        if t >= cfg["eval_from"]:
            errs.append(np.mean([np.linalg.norm(x) for x in e]))
            D_all.append(np.mean([np.sum((e[i] - e[j]) ** 2)
                                  for i in range(N) for j in range(i + 1, N)]))
        if 0.6 * cfg["t_on"] <= t < cfg["t_on"]:
            drift.append(np.mean([np.linalg.norm(x[:2]) for x in e]))
    return float(np.mean(errs)), float(np.mean(D_all)), float(np.mean(drift))


if __name__ == "__main__":
    cfg = dict(CFG, log_sensors=True)
    rows = []
    for seed in range(3):
        L = run_logged(cfg, seed)
        est_t, est_G = b3_replay(cfg, L, seed)
        er, D, dr = metrics(cfg, L, est_t, est_G)
        rows.append(dict(seed=seed, err=er, D=D, drift=dr))
        print(f"seed {seed}: |err|={er:.4f}  D={D:.4e}  pre-anchor drift={dr:.2f} m")
    agg = dict(arm="B3 relative-pose DInEKF (1 Hz, 0.1 m/1deg; offline replay v1)",
               err=float(np.mean([r["err"] for r in rows])),
               D=float(np.mean([r["D"] for r in rows])),
               drift=float(np.mean([r["drift"] for r in rows])), per_seed=rows)
    json.dump(agg, open(OUT, "w"), indent=1)
    print("written", OUT)
