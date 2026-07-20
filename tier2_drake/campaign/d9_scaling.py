"""D9 — scaling montage (plan §5.4; S7 / sim_design E6 Tier-2 half).

N in {3, 4, 5, 6, 8} x {cycle, complete}; 12 formation draws x 2 seeds per cell
(~240 runs). Per run: pre-anchor E_F floor (maneuvering, eval [50, 80] s) and
the post-beacon RE-LOCK RATE (exponential fit of D(t) decay on [80, 110] s).

POWER PRE-DECLARATION (plan): the Spearman ordering of re-lock rate by
lambda_2(L) is the powered claim; the ring -2 exponent (3 support points,
N in {4, 6, 8}) is a reduced-power row, reported with its CI and expected
UNDER-POWERED per the §1 convention. N = 3 is demonstration-only (C3 = K3 —
no cross-topology inference at N = 3).
Claim binding: Thm 5.1 spectral structure PROV; rate-vs-lambda_2 via Thm 6.3
LTV form with the ES-01 qualification; D_ss-vs-lambda_2 trend CONJ-captioned.
Falsifiers: rate fails to order by lambda_2 at fixed N (Spearman CI includes
0); ring exponent CI excludes -2 over N in {4, 6, 8}.
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor

import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv
from tier2_drake.blind_harbor.s1 import CFG, run_seed

OUT = "/workspaces/Anholonomy/tier2_drake/results/s1/d9_scaling.json"
NS = [3, 4, 5, 6, 8]
TOPOS = ["cycle", "complete"]


def lambda2(topo, N):
    if topo == "complete":
        return float(N)
    return float(2.0 * (1.0 - np.cos(2.0 * np.pi / N)))


def D_series(cfg, out):
    """D(t) disagreement AND kern(t) gauge (common-mode) error: pinning kills
    the gauge, which D is blind to — complete graphs re-lock D near-instantly
    at tiny amplitude and the D-rate there is noise [caught by the 20x rate
    discontinuity at K8]. The Cor 5.2 pinning rate lives in kern(t)."""
    N = cfg["N"]
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    D = np.zeros(len(ts)); kern = np.zeros(len(ts))
    for k in range(len(ts)):
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        e = np.array([Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true))
                      for i in range(N)])
        D[k] = np.mean([np.sum((e[i] - e[j]) ** 2)
                        for i in range(N) for j in range(i + 1, N)])
        kern[k] = np.linalg.norm(e.mean(axis=0))
    return ts, D, kern


def one(args):
    topo, N, form, seed = args
    rng = np.random.default_rng(form)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    cfg = dict(CFG, N=N, Tend=120.0, tau=0.4, t_on=80.0, eval_from=50.0,
               turn_bias=0.03, turn_amp=0.02, topology=topo,
               front_arc=fa, perturb=pe)
    try:
        out = run_seed(cfg, seed)
    except Exception as e:
        return dict(topo=topo, N=N, form=form, seed=seed, err=str(e)[:100])
    ts, D, kern = D_series(cfg, out)
    floor = float(np.mean(D[(ts >= 50.0) & (ts < 80.0)]))
    # honest re-lock rate: subtract the post-anchor asymptote before the log
    # fit (the plain log-fit conflates decay speed with amplitude and biases
    # high-floor cells — caught before reporting the Spearman verdict)
    D_inf = float(np.mean(D[ts >= 112.0]))
    m = (ts >= 82.0) & (ts <= 110.0) & (D - D_inf > max(1e-3 * D[ts >= 80.0][0], 1e-10))
    rate = (float(-np.polyfit(ts[m], np.log(D[m] - D_inf), 1)[0])
            if m.sum() > 10 else None)
    wall = out["wall"]
    # pinning rate on the gauge component (the Cor 5.2 observable)
    k_inf = float(np.mean(kern[ts >= 116.0]))
    mk = (ts >= 82.0) & (ts <= 110.0) & (kern - k_inf > 1e-3 * max(kern[ts >= 80.0][0], 1e-9))
    pin_rate = (float(-np.polyfit(ts[mk], np.log(kern[mk] - k_inf), 1)[0])
                if mk.sum() > 10 else None)
    return dict(topo=topo, N=N, form=form, seed=seed, floor=floor,
                relock=rate, pin=pin_rate, D_inf=D_inf,
                D_post=D[(ts >= 80.0)][::5].tolist(),
                kern_post=kern[(ts >= 80.0)][::5].tolist(), wall=wall)


if __name__ == "__main__":
    grid = [(t, n, f, s) for t in TOPOS for n in NS
            for f in range(12) for s in range(2)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, grid, chunksize=2))
    ok = [r for r in rows if "err" not in r and r.get("relock") is not None]
    json.dump(rows, open(OUT, "w"), indent=1)
    print(f"{len(ok)}/{len(grid)} ok")
    print("topo      N  lam2   floor       relock     wall[s]")
    cell = {}
    for topo in TOPOS:
        for N in NS:
            v = [r for r in ok if r["topo"] == topo and r["N"] == N]
            if not v:
                continue
            cell[(topo, N)] = v
            print(f"{topo:9s} {N}  {lambda2(topo, N):5.2f}  "
                  f"{np.mean([r['floor'] for r in v]):.4e}  "
                  f"{np.mean([r['relock'] for r in v]):.4f}  "
                  f"{np.mean([r['wall'] for r in v]):.0f}")
    # Spearman: relock rate ordered by lambda2 (excluding N=3, demonstration-only)
    from scipy.stats import spearmanr
    pts = [(lambda2(t, n), r["relock"]) for (t, n), v in cell.items()
           for r in v if n != 3]
    ppts = np.array([(lambda2(t, n), r["pin"]) for (t, n), v in cell.items()
                     for r in v if n != 3 and r.get("pin") is not None])
    if len(ppts):
        from scipy.stats import spearmanr as _sp
        prho = _sp(ppts[:, 0], ppts[:, 1])[0]
        print(f"Spearman(PIN rate [gauge], lambda2) = {prho:.3f}  "
              f"(the Cor 5.2 observable)")
    xs, ys = zip(*pts)
    rho, _ = spearmanr(xs, ys)
    rng = np.random.default_rng(111)
    bs = []
    arr = np.array(pts)
    for _ in range(3000):
        i = rng.integers(0, len(arr), len(arr))
        bs.append(spearmanr(arr[i, 0], arr[i, 1])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"Spearman(relock, lambda2) = {rho:.3f} [{lo:.3f}, {hi:.3f}]  "
          f"(falsifier: CI includes 0)")
    # ring exponent over N in {4, 6, 8} (reduced-power row, declared)
    rN = [np.mean([r["relock"] for r in cell[("cycle", n)]]) for n in (4, 6, 8)]
    sl = np.polyfit(np.log([4, 6, 8]), np.log(rN), 1)[0]
    print(f"ring relock exponent vs N (3 pts, reduced-power): {sl:.2f}  "
          f"(prediction -2; expected UNDER-POWERED)")
    print("written", OUT)
