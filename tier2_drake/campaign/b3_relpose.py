"""B3 — synthetic relative-pose DInEKF baseline.  ** WIP — DESIGN INCOMPLETE **

DO NOT cite numbers from this driver in any table. Status 2026-07-20: two real
bugs found and fixed during bring-up (systematic v*tau along-track pull from
comparing current measurements against delayed estimates; neighbor-frame
residual applied un-transported — the 10-20 m lever mis-rotates corrections).
Progress log: v4 installed the joint geometric solve (closed-form 2D Kabsch
over attach-point fixes — removes the radial-ray assumption; 16.8 -> 3.18 m);
v5 added the beacon yaw constraint via psi = theta_L + sigma - sigma_i
(3.18 -> 2.06 m). DIAGNOSIS (isolation run, perfect vessel poses + measured
sigma_i): the DERIVATION alone errs 1.50 m — the l = 12 m cable-angle lever
amplifies sigma_i noise/lag through every fix; the pose graph contributes only
~0.5 m. CONCLUSION for the D7 design session: a competitive B3 needs its own
principled load-state filter (Kalman-weighted direction channel) on top of the
vessel graph — i.e., it must re-derive the constraint-channel design under
test, which is itself a thesis-relevant observation. Best-yet: err 2.06 m vs
record 0.183 m — NOT a valid competitor measurement yet.

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
    attach, starts, rays = attachment_and_start(scen)
    lag = int(round(cfg["tau"] / 0.01))                  # comms delay in ticks

    X = [SE2(starts[j][2], np.array(starts[j][:2])) for j in range(N)]
    P = [np.diag([0.05, 0.05, 0.01]) for _ in range(N)]
    Q = np.diag([2e-4, 2e-4, 5e-6])
    sig_i = [0.0] * N                                    # direction low-pass
    warm = [False] * N
    hist = []                                            # (X list, fix list) per tick

    est_G, est_t = [], []
    kf_G = [None] * N; kf_P = [None] * N; kf_prev = [None] * N
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
                # load fix -> own-pose fix through own cable geometry:
                # position from the attach point + cable direction; YAW from the
                # identity psi = theta_L + sigma - sigma_i with sigma computed
                # from the beacon's load pose and own estimated position (the
                # unconstrained-yaw variant lets agent 0's yaw random-walk and
                # rotates every Kabsch fix it contributes [measured: 3.2 m])
                thL_b = float(b[2])
                Rb2 = np.array([[np.cos(thL_b), -np.sin(thL_b)],
                                [np.sin(thL_b), np.cos(thL_b)]])
                attach_w = np.asarray(b[:2]) + Rb2 @ attach[0][:2]
                d = X[0][:2, 2] - attach_w
                sigma0 = np.arctan2(d[1], d[0]) - thL_b
                psi0 = thL_b + sigma0 - sig_i[0]
                phi = psi0 + sig_i[0]
                pv = attach_w + l * np.array([np.cos(phi), np.sin(phi)])
                zX = SE2(psi0, pv)
                r = Log(inv(X[0]) @ zX)
                Rb = np.diag([0.05 ** 2 + (l * np.radians(1)) ** 2] * 2 +
                             [np.radians(2.0) ** 2])
                S = P[0] + Rb
                K = P[0] @ np.linalg.inv(S)
                X[0] = X[0] @ Exp(K @ r)
                IK = np.eye(3) - K
                P[0] = IK @ P[0] @ IK.T + K @ Rb @ K.T
        hist.append([(X[j].copy(), P[j].copy()) for j in range(N)])

        if kr % 10 == 0:                                 # 10 Hz: derive G-hat per agent
            # + per-agent KF smoothing over the Kabsch fixes [the diagnosed
            # sigma_i-lever remedy]: predict with a constant-twist model,
            # update with the Kabsch fix; R from the fix spread.
            # JOINT GEOMETRIC SOLVE (fixes the radial-assumption defect): each
            # agent's cable gives one attach-point fix f_j = p_v_j - l*u(phi_j),
            # which must equal p_L + R(theta_L) a_j. With the neighbors' (tau-
            # delayed) exchanged fixes, (p_L, theta_L) is closed-form 2D Kabsch
            # over known correspondences a_j <-> f_j.
            idxd = max(kr - lag, 0)
            Gs = []
            for j in range(N):
                mem = [j, (j - 1) % N, (j + 1) % N]
                fs, as_ = [], []
                for m in mem:
                    Xm, _ = (hist[idxd][m] if m != j and idxd < len(hist)
                             else (X[m], None))
                    psim = np.arctan2(Xm[1, 0], Xm[0, 0])
                    phim = psim + sig_i[m]
                    fs.append(Xm[:2, 2] - l * np.array([np.cos(phim), np.sin(phim)]))
                    as_.append(attach[m][:2])
                F = np.array(fs); A = np.array(as_)
                Fc, Ac = F - F.mean(0), A - A.mean(0)
                H = Ac.T @ Fc
                thL = np.arctan2(H[1, 0] - H[0, 1], H[0, 0] + H[1, 1])
                Rm = np.array([[np.cos(thL), -np.sin(thL)],
                               [np.sin(thL), np.cos(thL)]])
                pL = F.mean(0) - Rm @ A.mean(0)
                Gs.append(SE2(thL, pL))
            # KF pass: G_kf[j] <- predict(const twist) then blend toward Kabsch fix
            if not hasattr(b3_replay, "_kf"):
                pass
            if kf_G[0] is None:
                for j in range(N):
                    kf_G[j] = Gs[j]; kf_P[j] = np.diag([1.0, 1.0, 0.2])
                    kf_prev[j] = Gs[j]
            else:
                for j in range(N):
                    xi_hat = Log(inv(kf_prev[j]) @ Gs[j]) / 1.0   # per-second fix twist (10 Hz->1 s window handled by blend)
                    kf_prev[j] = Gs[j]
                    kf_P[j] = kf_P[j] + np.diag([2e-3, 2e-3, 5e-4])
                    Rfix = np.diag([0.35 ** 2, 0.35 ** 2, 0.05 ** 2])
                    r = Log(inv(kf_G[j]) @ Gs[j])
                    K = kf_P[j] @ np.linalg.inv(kf_P[j] + Rfix)
                    kf_G[j] = kf_G[j] @ Exp(K @ r)
                    IK = np.eye(3) - K
                    kf_P[j] = IK @ kf_P[j] @ IK.T + K @ Rfix @ K.T
            est_G.append([kf_G[j].copy() for j in range(N)]); est_t.append(t)
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
