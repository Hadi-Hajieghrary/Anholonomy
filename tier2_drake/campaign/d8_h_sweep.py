"""D8 — Drake h-sweep (plan §5.4 D8(i), v1: h in {0.5, 1, 2} ms; 0.25 ms deferred
for runtime, disclosed). Central column tau in {0.1, 0.4, 1.6}; excess exponent
per h must have overlapping CIs (falsifier: disjoint)."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, subprocess, numpy as np
from concurrent.futures import ProcessPoolExecutor

CODE = """
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics
cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), turn_bias={tb},
           turn_amp={ta}, tau={tau}, h={h})
out = run_seed(cfg, {seed})
print(f"RESULT {{floor_metrics(cfg, out):.6e}}")
"""

HS = [5.0e-4, 1.0e-3, 2.0e-3]
TAUS = [0.1, 0.4, 1.6]

def cell(args):
    h, tau, seed, arm = args
    tb, ta = (0.03, 0.02) if arm == "turn" else (0.0, 0.0)
    code = CODE.format(h=h, tau=tau, seed=seed, tb=tb, ta=ta)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd="/workspaces/Anholonomy", timeout=1800)
    for l in r.stdout.splitlines():
        if l.startswith("RESULT"):
            return (h, tau, seed, arm, float(l.split()[1]))
    return (h, tau, seed, arm, None)

GRID = ([(h, t, s, "turn") for h in HS for t in TAUS for s in range(10)]
        + [(h, t, s, "straight") for h in HS for t in TAUS for s in range(4)])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID, chunksize=2))
    pool = {}
    for h, t, s, arm, D in res:
        if D is not None:
            pool.setdefault((h, t, arm), []).append(D)
    rng = np.random.default_rng(81)
    out = {}
    for h in HS:
        ex_ = np.array([np.mean(pool[(h, t, "turn")]) - np.mean(pool[(h, t, "straight")])
                        for t in TAUS])
        sl = np.polyfit(np.log(TAUS), np.log(ex_), 1)[0]
        bs = []
        for _ in range(2000):
            e = np.array([np.mean(rng.choice(pool[(h, t, "turn")], 10))
                          - np.mean(rng.choice(pool[(h, t, "straight")], 4)) for t in TAUS])
            if np.all(e > 0):
                bs.append(np.polyfit(np.log(TAUS), np.log(e), 1)[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[str(h)] = dict(exponent=[float(lo), float(sl), float(hi)],
                           excess=[float(x) for x in ex_])
        print(f"h={h*1e3:.2g} ms: excess exponent {sl:.3f} [{lo:.3f}, {hi:.3f}]  "
              f"excess@0.4={ex_[1]:.3e}")
    json.dump(out, open("/workspaces/Anholonomy/tier2_drake/results/s1/d8_h_sweep.json", "w"),
              indent=1)
    print("written d8_h_sweep.json")
