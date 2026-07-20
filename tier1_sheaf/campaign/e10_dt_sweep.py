"""T1-E10 — integrator refinement (plan §4.0(vi), QD5 grid {0.001,0.0025,0.005,0.01}).
Falsifier: excess-exponent CIs disjoint across dt."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier1_sheaf.experiments.e3b_floor import run

DTS = [0.001, 0.0025, 0.005, 0.01]
TAUS = [0.1, 0.2, 0.4, 0.8, 1.6]

def cell(args):
    dt, tau, seed, arm = args
    kw = dict(Tend=90.0, dt=dt)
    if arm == "straight":
        kw["eta_profile"] = "straight"
    return (dt, tau, seed, arm, run(tau, 0, seed, **kw))

GRID = ([(dt, t, s, "turn") for dt in DTS for t in TAUS for s in range(10)]
        + [(dt, t, s, "straight") for dt in DTS for t in TAUS for s in range(4)])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID, chunksize=4))
    pool = {}
    for dt, t, s, arm, D in res:
        pool.setdefault((dt, t, arm), []).append(D)
    out = {}
    rng = np.random.default_rng(71)
    for dt in DTS:
        ex_ = np.array([np.mean(pool[(dt, t, "turn")]) - np.mean(pool[(dt, t, "straight")])
                        for t in TAUS])
        sl = np.polyfit(np.log(TAUS), np.log(ex_), 1)[0]
        bs = []
        for _ in range(2000):
            e = np.array([np.mean(rng.choice(pool[(dt, t, "turn")], 10))
                          - np.mean(rng.choice(pool[(dt, t, "straight")], 4)) for t in TAUS])
            if np.all(e > 0):
                bs.append(np.polyfit(np.log(TAUS), np.log(e), 1)[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[str(dt)] = dict(exponent=[float(lo), float(sl), float(hi)],
                            excess=[float(x) for x in ex_])
        print(f"dt={dt}: excess exponent {sl:.3f} [{lo:.3f}, {hi:.3f}]  "
              f"excess@0.4={ex_[2]:.3e}")
    json.dump(out, open("/workspaces/Anholonomy/tier1_sheaf/results/e10_dt_sweep.json", "w"),
              indent=1)
    print("written e10_dt_sweep.json")
