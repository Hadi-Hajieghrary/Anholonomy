"""D10(b) — packet loss + jitter robustness (plan §5.4; OUTSIDE protocol class P).
Characterization only (no falsifier): graceful degradation of the floor and of
anchored consistency vs loss p in {0, 0.1, 0.3} x jitter {0, 8 ticks = 20% tau}.
Red-flag rule: anchored ANEES > 3x its p=0 value persisting -> reported."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics, anees_and_disagreement

def floor_cell(args):
    p, J, s = args
    cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), tau=0.4,
               turn_bias=0.03, turn_amp=0.02, drop_p=p, jitter_ticks=J)
    return ("floor", p, J, s, floor_metrics(cfg, run_seed(cfg, s)), None)

def gate_cell(args):
    p, J, s = args
    cfg = dict(CFG, drop_p=p, jitter_ticks=J)          # M-FAB config (Tend=130, t_on=30)
    a, c, D, dr = anees_and_disagreement(cfg, run_seed(cfg, s))
    return ("anees", p, J, s, D, a)

GRID = ([(p, J, s) for p in (0.0, 0.1, 0.3) for J in (0, 8) for s in range(8)],
        [(p, 0, s) for p in (0.0, 0.1, 0.3) for s in range(6)])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(floor_cell, GRID[0], chunksize=2)) \
             + list(ex.map(gate_cell, GRID[1], chunksize=2))
    out = [dict(kind=k, p=p, J=J, seed=s, D=D, anees=a) for k, p, J, s, D, a in rows]
    json.dump(out, open("/workspaces/Anholonomy/tier2_drake/results/s1/d10b_loss.json", "w"), indent=1)
    print("kind   p    J   D           anees")
    for k in ("floor", "anees"):
        for p in (0.0, 0.1, 0.3):
            for J in ((0, 8) if k == "floor" else (0,)):
                v = [r for r in out if r["kind"] == k and r["p"] == p and r["J"] == J]
                if v:
                    an = np.mean([r["anees"] for r in v]) if k == "anees" else float("nan")
                    print(f"{k:6s} {p:.1f}  {J}   {np.mean([r['D'] for r in v]):.4e}  {an:.2f}")
    print("written d10b_loss.json")
