"""tau=0.05 grid point for D2 (plan grid {0.05..1.6}) — turn arm + straight control."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, subprocess, numpy as np
from concurrent.futures import ProcessPoolExecutor

CODE = """
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics, m5_amplitude
rng = np.random.default_rng({form})
cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), turn_bias={tb},
           turn_amp={ta}, tau=0.05, formation="fan",
           front_arc={front_arc}, perturb={perturb})
out = run_seed(cfg, {seed})
print(f"RESULT {{floor_metrics(cfg, out):.6e}} {{m5_amplitude(cfg, out):.6e}}")
"""

def cell(args):
    kind, form, seed = args
    rng = np.random.default_rng(form)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    tb, ta = (0.03, 0.02) if kind == "d2" else (0.0, 0.0)
    code = CODE.format(form=form, front_arc=fa, perturb=pe, seed=seed, tb=tb, ta=ta)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd="/workspaces/Anholonomy", timeout=900)
    for l in r.stdout.splitlines():
        if l.startswith("RESULT"):
            D, M5 = map(float, l.split()[1:3])
            return dict(kind=kind, tau=0.05, form=form, seed=seed, D=D, M5=M5)
    return dict(kind=kind, tau=0.05, form=form, seed=seed, D=None,
                err=(r.stdout + r.stderr)[-150:])

GRID = ([("d2", f, s) for f in range(12) for s in range(4)]
        + [("straight", f, s) for f in range(12) for s in range(2)])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID))
    ok = [r for r in res if r["D"] is not None]
    print(f"{len(ok)}/{len(GRID)} ok")
    for kind in ("d2", "straight"):
        v = [r["D"] for r in ok if r["kind"] == kind]
        print(f"{kind}: D={np.mean(v):.4e} (n={len(v)})")
    print(f"M5 at 0.05: {np.mean([r['M5'] for r in ok if r['kind']=='d2']):.4e}")
    out = "/workspaces/Anholonomy/tier2_drake/results/s1/d2_tau005.json"
    json.dump(res, open(out, "w"), indent=1)
    print("written", out)
