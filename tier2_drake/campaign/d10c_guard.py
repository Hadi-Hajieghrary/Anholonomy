"""D10(c) — broadside guard-save set piece (plan §5.4; characterization,
OUTSIDE protocol class P; Cor 5.3 monotonicity conjectured, captioned so).
Scripted lateral gust (3500 N, [30,50] s) on agent 2 drives its cable toward
broadside; paired seeds guard-ON vs guard-OFF. Metrics: min cos(sigma_i) reached,
max D excursion, re-lock time (D back within 2x pre-gust median), divergence
(D > 10x pre-gust at Tend)."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
import estimator_core as ec
from tier1_sheaf.core.se2 import Log, inv
from tier2_drake.blind_harbor.s1 import CFG, run_seed

def one(args):
    guard, seed = args
    cfg = dict(CFG, Tend=90.0, t_on=float("inf"), tau=0.4,
               gust=(2, 30.0, 50.0, 3500.0), guard=guard)
    out = run_seed(cfg, seed)
    ts, ests = out["ts"], out["ests"]
    N = cfg["N"]
    D = np.zeros(len(ts))
    for k in range(len(ts)):
        Gs = [ests[i][k][ec.SL_G].reshape(3, 3) for i in range(N)]
        D[k] = np.mean([np.sum(Log(inv(Gs[i]) @ Gs[j]) ** 2)
                        for i in range(N) for j in range(i + 1, N)])
    pre = float(np.median(D[(ts > 20) & (ts < 30)]))
    exc = float(np.max(D[(ts >= 30) & (ts <= 70)]))
    after = np.where((ts > 50) & (D < 2 * pre))[0]
    relock = float(ts[after[0]] - 50.0) if len(after) else None
    diverged = bool(np.mean(D[ts > 85]) > 10 * pre)
    return dict(guard=guard, seed=seed, pre=pre, exc=exc,
                relock=relock, diverged=diverged)

if __name__ == "__main__":
    grid = [(g, s) for g in (True, False) for s in range(10)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, grid))
    json.dump(rows, open("/workspaces/Anholonomy/tier2_drake/results/s1/d10c_guard.json", "w"), indent=1)
    for g in (True, False):
        v = [r for r in rows if r["guard"] == g]
        rl = [r["relock"] for r in v if r["relock"] is not None]
        print(f"guard={'ON ' if g else 'OFF'}: excursion {np.mean([r['exc'] for r in v]):.3e}  "
              f"relock {np.mean(rl) if rl else float('nan'):.1f} s (n={len(rl)}/10)  "
              f"diverged {sum(r['diverged'] for r in v)}/10")
    print("written d10c_guard.json")
