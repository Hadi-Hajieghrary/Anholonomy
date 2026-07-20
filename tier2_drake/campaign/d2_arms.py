"""A1/A2 diagnostic arms on the D2 grid (pre-registered; variance-attribution figure).
A1 = naive consensus (identity edge maps); A2 = un-conjugated transport ablation.
Same turn maneuver, formations, and seeds as production D2; 2 seeds per cell.
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, subprocess, numpy as np
from concurrent.futures import ProcessPoolExecutor

TAUS = [0.1, 0.2, 0.4, 0.8, 1.6]
N_FORM, N_SEED = 12, 2

CODE = """
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics
rng = np.random.default_rng({form})
cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), turn_bias=0.03,
           turn_amp=0.02, tau={tau}, formation="fan", fuse_rule="{rule}",
           front_arc={front_arc}, perturb={perturb})
out = run_seed(cfg, {seed})
print(f"RESULT {{floor_metrics(cfg, out):.6e}}")
"""

def cell(args):
    rule, tau, form, seed = args
    rng = np.random.default_rng(form)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    code = CODE.format(rule=rule, form=form, tau=tau, front_arc=fa, perturb=pe, seed=seed)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd="/workspaces/Anholonomy", timeout=900)
    for l in r.stdout.splitlines():
        if l.startswith("RESULT"):
            return dict(kind=rule, tau=tau, form=form, seed=seed, D=float(l.split()[1]))
    return dict(kind=rule, tau=tau, form=form, seed=seed, D=None,
                err=(r.stdout + r.stderr)[-150:])

GRID = [(r, t, f, s) for r in ("A1", "A2") for t in TAUS
        for f in range(N_FORM) for s in range(N_SEED)]

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(cell, GRID))
    ok = [r for r in res if r["D"] is not None]
    print(f"{len(ok)}/{len(GRID)} ok")
    out = "/workspaces/Anholonomy/tier2_drake/results/s1/d2_a1_a2_arms.json"
    json.dump(res, open(out, "w"), indent=1)
    for rule in ("A1", "A2"):
        print(rule, [f"{t}: {np.mean([r['D'] for r in ok if r['kind']==rule and r['tau']==t]):.3e}"
                     for t in TAUS])
    print("written", out)
