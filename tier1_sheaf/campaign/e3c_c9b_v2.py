"""C9b re-analysis v2: per-seed storage; absolute-excess fit dD = D(eps)-D(0)
(the Drake D4 estimator); points with non-positive bootstrap excess dropped,
never clamped."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier1_sheaf.experiments.e3c_symmetry import dss_cell, EPS

TAUS = [0.2, 0.4, 0.8]

def cell(args):
    e, t, s = args
    return (e, t, s, dss_cell(e, t, s, Tend=90.0))

if __name__ == "__main__":
    grid = [(e, t, s) for e in EPS for t in TAUS for s in range(30)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, grid, chunksize=8))
    pool = {}
    for e, t, s, D in res:
        pool.setdefault((e, t), []).append(D)
    out = {f"{e}_{t}": v for (e, t), v in pool.items()}
    json.dump(out, open("/workspaces/Anholonomy/tier1_sheaf/results/e3c_c9b_seeds.json", "w"))
    rng = np.random.default_rng(41)
    for t in TAUS:
        base = np.array(pool[(0.0, t)])
        dD = np.array([np.mean(pool[(e, t)]) - base.mean() for e in EPS[1:]])
        ok = dD > 0
        sl = np.polyfit(np.log(np.array(EPS[1:])[ok]), np.log(dD[ok]), 1)[0]
        bs = []
        for _ in range(3000):
            b0 = np.mean(rng.choice(base, 30))
            d = np.array([np.mean(rng.choice(pool[(e, t)], 30)) - b0 for e in EPS[1:]])
            m = d > 0
            if m.sum() >= 3:
                bs.append(np.polyfit(np.log(np.array(EPS[1:])[m]), np.log(d[m]), 1)[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        dropped = int((~ok).sum())
        print(f"tau={t}: dD values {['%.2e' % x for x in dD]} (dropped {dropped})")
        print(f"  C9b absolute-excess eps-slope: {sl:.2f} [{lo:.2f}, {hi:.2f}]  "
              f"(prediction 2 {'IN' if lo <= 2 <= hi else 'NOT in'} CI; n_boot={len(bs)})")
