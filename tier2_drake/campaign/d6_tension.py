"""D6 — the information channel IS the force (plan §5.4; T2-C6; A10 stated as
a model assumption).

Part 2 (dose-response, the stronger evidence): unequal thrust (1.3/1.1/1.0/
0.9/0.7 -> large tension spread) makes per-agent tension a covariate; regress
per-agent shape RMSE and tr Sigma_shape on time-averaged T_j^2 (the A10 Fisher
proxy). Tension is MEASURED offline as the per-vessel Newton residual along the
cable direction (thrust analytic post-ramp; declared linear drag; accelerations
by central difference of the logged velocities).
Part 1 (ablation): Def 4.1 series information weights ON vs consensus-only
(w=1), matched seeds; Delta tr Sigma_shape and Delta shape-RMSE with bootstrap
CIs. NOTE: weights use the geometric information factor iota (Def 4.1's shape
factor); the kappa ~ T^2 constant is Q6b (open) — captioned "consistent with
the conjectured monotone dependence", never "proves".
Falsifiers: Part 1 Delta CI includes 0 => T2-C6 falls. Part 2 slope
non-negative (CI) => Fisher-weight model wrong for this plant; reported.
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor

import estimator_core as ec
from tier2_drake.blind_harbor.s1 import CFG, run_seed
from tier2_drake.harbor import ScenarioConfig, attachment_and_start

OUT = "/workspaces/Anholonomy/tier2_drake/results/s1/d6_tension.json"
TSC = (1.3, 1.1, 1.0, 0.9, 0.7)
BASE = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), tau=0.4,
            thrust_scale=TSC)


def true_shapes(truth_row, attach, N, l):
    """Offline (sigma, sigma_i) per agent from logged poses (sensors._truth math)."""
    thL = truth_row[2]
    R = np.array([[np.cos(thL), -np.sin(thL)], [np.sin(thL), np.cos(thL)]])
    out = []
    for j in range(N):
        pv = truth_row[3 + 3 * j:5 + 3 * j]
        psi = truth_row[5 + 3 * j]
        aw = truth_row[0:2] + R @ attach[j][:2]
        d = pv - aw
        sig = np.arctan2(d[1], d[0]) - thL
        sig_i = thL - psi + sig
        out.append((sig, sig_i))
    return out


def tensions(ts, tq, attach, scen, tsc, N):
    """Per-agent Newton-residual tension along the cable, eval-window mean."""
    dt = ts[1] - ts[0]
    T = np.zeros((len(ts), N))
    for j in range(N):
        p = tq[:, 3 + 3 * j:5 + 3 * j]
        psi = tq[:, 5 + 3 * j]
        iv = 3 * (N + 1)                          # v block offset: q is 3(N+1)
        v = tq[:, iv + 3 + 3 * j:iv + 5 + 3 * j]
        a = np.gradient(v, dt, axis=0)
        thL = tq[:, 2]
        aw = tq[:, 0:2] + np.stack(
            [np.cos(thL) * attach[j][0] - np.sin(thL) * attach[j][1],
             np.sin(thL) * attach[j][0] + np.cos(thL) * attach[j][1]], axis=1)
        u = aw - p
        u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
        F_thr = scen.thrust * tsc[j] * np.stack([np.cos(psi), np.sin(psi)], axis=1)
        F_drag = -scen.drag_lin_asv * v
        resid = scen.asv_mass * a - F_thr - F_drag
        T[:, j] = np.einsum("ij,ij->i", resid, u)
    return T


def one(args):
    seed, weights = args
    cfg = dict(BASE, weights=weights)
    out = run_seed(cfg, seed)
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = cfg["N"]
    scen = ScenarioConfig(N=N, cable_len=cfg["l"], thrust=800.0)
    attach, _, _ = attachment_and_start(scen)
    ks = np.where(ts >= cfg["eval_from"])[0]
    Tm = tensions(ts, tq, attach, scen, TSC, N)[ks].mean(axis=0)
    rmse = np.zeros(N); trS = np.zeros(N)
    for k in ks:
        st_true = true_shapes(tq[k], attach, N, cfg["l"])
        for j in range(N):
            s_est = ests[j][k][ec.SL_S]
            e = np.array(st_true[j]) - s_est
            e = (e + np.pi) % (2 * np.pi) - np.pi
            rmse[j] += np.sum(e ** 2)
            P = ec.unvech(ests[j][k][ec.SL_P])
            trS[j] += P[3, 3] + P[4, 4]
    rmse = np.sqrt(rmse / len(ks)); trS /= len(ks)
    return dict(seed=seed, weights=weights, T=Tm.tolist(),
                rmse=rmse.tolist(), trS=trS.tolist())


if __name__ == "__main__":
    grid = [(s, w) for s in range(25) for w in ("series", "A3")]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, grid))
    json.dump(rows, open(OUT, "w"), indent=1)

    # Part 2: dose-response on the series arm (per plan: tension as covariate)
    ser = [r for r in rows if r["weights"] == "series"]
    T2 = np.array([t ** 2 for r in ser for t in r["T"]])
    RM = np.array([x for r in ser for x in r["rmse"]])
    TS = np.array([x for r in ser for x in r["trS"]])
    rng = np.random.default_rng(101)
    for name, Y in (("shape-RMSE", RM), ("tr Sigma_shape", TS)):
        sl = np.polyfit(T2, Y, 1)[0]
        bs = []
        for _ in range(3000):
            i = rng.integers(0, len(T2), len(T2))
            bs.append(np.polyfit(T2[i], Y[i], 1)[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"Part2 {name} vs T^2 slope: {sl:.3e} [{lo:.3e}, {hi:.3e}]  "
              f"(prediction negative; falsifier: non-negative CI)")
    # Part 1: paired ablation
    a3 = {r["seed"]: r for r in rows if r["weights"] == "A3"}
    dR = [np.mean(r["rmse"]) - np.mean(a3[r["seed"]]["rmse"]) for r in ser]
    dS = [np.mean(r["trS"]) - np.mean(a3[r["seed"]]["trS"]) for r in ser]
    for name, d in (("Delta shape-RMSE (series - w1)", dR),
                    ("Delta tr Sigma_shape", dS)):
        bs = [np.mean(rng.choice(d, len(d))) for _ in range(3000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"Part1 {name}: {np.mean(d):.3e} [{lo:.3e}, {hi:.3e}]  "
              f"(falsifier: CI includes 0 => T2-C6 falls)")
    print("written", OUT)
