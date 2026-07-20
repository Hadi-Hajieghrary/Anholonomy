"""T1-E2 — contraction, subspace-resolved (plan §4.1; C6, C19; PROV LTV/frozen; F8).

Frozen shapes, noise OFF (the executed-null regime: fusion residuals are exactly
the disagreement signal). Step-perturb each agent's G-hat by Exp(delta_j)
(random directions, common norm), then fit the exponential decay of the gauge
complement ||e_perp||(t).

Tested prediction (C6): rate(kappa) - mu has UNIT SLOPE in kappa*lambda_2, with
mu calibrated at kappa=0 (measurement-only rate, DISCLOSED AS FITTED — the
identity line is anchored, not predicted). Falsifier: slope < 0.5 either topology.
C19: log-linearity residual exponent vs ||delta|| over 3 decades (predict 2).

ES-01 qualification: whole-vector rates only in this v1 (the per-subspace
projection onto mu's domain vs the consensus subspace is the stretch cell); the
caption carries Thm 6.3's LTV/frozen hedge verbatim.
"""
from __future__ import annotations

import json
import numpy as np

import estimator_core as ec
from tier1_sheaf.core.se2 import Exp, Log, inv
from tier2_drake.blind_harbor.sensors import KAPPA_DIR

OUT = "/workspaces/Anholonomy/tier1_sheaf/results/e2_contraction.json"

DC = 0.05
SHAPES = np.array([[-0.55, -0.55], [-0.28, -0.28], [0.0, 0.0],
                   [0.28, 0.28], [0.55, 0.55]])           # frozen fan, N=5
XI = np.array([0.8, 0.0, 0.12])                            # frozen load twist


def edges_of(topology: str, N: int = 5):
    if topology == "cycle":
        return [(i, (i + 1) % N) for i in range(N)]
    return [(i, j) for i in range(N) for j in range(i + 1, N)]   # complete


def lambda2(topology: str, N: int = 5) -> float:
    E = edges_of(topology, N)
    L = np.zeros((N, N))
    for i, j in E:
        L[i, i] += 1; L[j, j] += 1; L[i, j] -= 1; L[j, i] -= 1
    return float(np.sort(np.linalg.eigvalsh(L))[1])


def run(topology: str, kappa: float, delta_norm: float, seed: int,
        *, Tend: float = 30.0, dt: float = 0.02, use_meas: bool = True):
    """Perturb at t=0, integrate the deterministic error dynamics, return the
    complement-decay trace ||e_perp||(t) at the send epochs."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 17]))
    N = len(SHAPES)
    l = 1.0
    sts = [ec.FilterState.initial(SHAPES[j].copy(), l) for j in range(N)]
    zetas = [np.linalg.solve(__import__("tier1_sheaf.core.shapes", fromlist=["Ad_m"])
                             .Ad_m(*SHAPES[j], l), XI) for j in range(N)]
    # truth reference
    G = np.eye(3)
    # perturb each agent independently, common norm
    for j in range(N):
        d = rng.standard_normal(3); d *= delta_norm / np.linalg.norm(d)
        sts[j] = sts[j].replace(G=sts[j].G @ Exp(d))
    alpha = kappa * DC
    E = edges_of(topology)
    directed = E + [(b, a) for (a, b) in E]
    steps = int(round(Tend / dt))
    per = int(round(DC / dt))
    trace_t, trace_e = [], []
    for k in range(steps):
        t = k * dt
        # deterministic propagate (exact odometry, frozen shapes)
        for j in range(N):
            sts[j] = ec.propagate(sts[j], zetas[j], dt, shape_motion_correction=False)
        G = G @ Exp(dt * XI)
        if use_meas and k % 2 == 1:                      # 20 Hz-ish direction channel
            for j in range(N):
                sts[j] = ec.update_direction(sts[j], SHAPES[j][1], KAPPA_DIR)
        if k % per == 0 and alpha > 0:
            snaps = [(sts[j].G.copy(), sts[j].s.copy()) for j in range(N)]
            for (a, b) in directed:
                G_nb, s_nb = snaps[b]
                sts[a], _ = ec.fuse_with_rule("paper", sts[a], G_nb, s_nb,
                                              DC, zetas[a], alpha, 1.0, b)
        if k % per == 0:
            errs = np.array([Log(sts[j].G @ inv(G)) for j in range(N)])
            e_perp = errs - errs.mean(axis=0)
            trace_t.append(t)
            trace_e.append(float(np.linalg.norm(e_perp)))
    return np.array(trace_t), np.array(trace_e)


def fit_rate(tt, ee):
    """Exponential decay rate over the resolvable transient (down to 1e-6)."""
    good = ee > 1e-9
    if good.sum() < 4:
        return float("nan"), float("nan")
    lo = ee[good] > max(ee[good][-1], 1e-8) * 3.0
    sel = good.copy(); sel[good] &= lo
    if sel.sum() < 4:
        sel = good
    coef = np.polyfit(tt[sel], np.log(ee[sel]), 1)
    resid = float(np.sqrt(np.mean((np.log(ee[sel]) - np.polyval(coef, tt[sel])) ** 2)))
    return float(-coef[0]), resid


def main(seeds: int = 50):
    from concurrent.futures import ProcessPoolExecutor
    KAPPAS = [0.0, 0.5, 1.0, 2.0]                        # 4x range incl. mu-calibration
    res = {"lambda2": {t: lambda2(t) for t in ("cycle", "complete")}}
    grid = [(topo, kap, s) for topo in ("cycle", "complete")
            for kap in KAPPAS for s in range(seeds)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rates = list(ex.map(_rate_cell, grid, chunksize=8))
    pool = {}
    for (topo, kap, s), r in zip(grid, rates):
        if np.isfinite(r):
            pool.setdefault((topo, kap), []).append(r)
    res["rates"] = {f"{t}_{k}": dict(mean=float(np.mean(v)), sd=float(np.std(v)),
                                     n=len(v)) for (t, k), v in pool.items()}
    # C6: rate - mu vs kappa*lambda2, unit-slope test (mu = rate at kappa 0)
    xs, ys = [], []
    for topo in ("cycle", "complete"):
        mu = np.mean(pool[(topo, 0.0)])
        for kap in KAPPAS[1:]:
            xs.append(kap * res["lambda2"][topo])
            ys.append(np.mean(pool[(topo, kap)]) - mu)
        res[f"mu_{topo}"] = float(mu)
    slope = float(np.polyfit(xs, ys, 1)[0])
    res["C6_slope"] = slope
    res["C6_points"] = list(zip(map(float, xs), map(float, ys)))
    print(f"lambda2: {res['lambda2']}   mu: cycle={res['mu_cycle']:.3f} "
          f"complete={res['mu_complete']:.3f}")
    print(f"C6 rate-vs-kappa*lambda2 slope = {slope:.3f}  "
          f"(falsifier: < 0.5 => C6 falsified)")
    # C19: log-linearity residual vs ||delta|| over 3 decades (cycle, kappa=1)
    DELTAS = [5e-3, 5e-2, 5e-1]
    resids = []
    for dn in DELTAS:
        rs = []
        for s in range(12):
            tt, ee = run("cycle", 1.0, dn, s)
            _, resid = fit_rate(tt, ee)
            rs.append(resid)
        resids.append(float(np.mean(rs)))
    c19 = float(np.polyfit(np.log(DELTAS), np.log(np.maximum(resids, 1e-12)), 1)[0])
    res["C19_residuals"] = dict(deltas=DELTAS, resid=resids, exponent=c19)
    print(f"C19 log-linearity residuals {['%.2e' % r for r in resids]} "
          f"exponent = {c19:.2f}  (predict 2; falsifier: CI excludes [1.8, 2.2])")
    json.dump(res, open(OUT, "w"), indent=1)
    print("written", OUT)


def _rate_cell(args):
    topo, kap, s = args
    tt, ee = run(topo, kap, 0.5 / (5 ** 0.5), s)         # per-agent norm; ||stack|| ~ 0.5
    r, _ = fit_rate(tt, ee)
    return r


if __name__ == "__main__":
    main()
