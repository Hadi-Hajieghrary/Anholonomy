"""Matched-config coefficient ratio, Drake side (plan §6).
Default fan, tau=0.4, 25 seeds turn + 25 straight. Also extracts the measured
operating shapes (mean s-hat per agent) that define the Tier-1 matched config."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics
import estimator_core as ec

BASE = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), tau=0.4)

def one(args):
    seed, turn = args
    cfg = dict(BASE, turn_bias=0.03 if turn else 0.0, turn_amp=0.02 if turn else 0.0)
    out = run_seed(cfg, seed)
    D = floor_metrics(cfg, out)
    shapes = None
    if turn and seed == 0:
        ts, ests = out["ts"], out["ests"]
        ks = np.where(ts >= cfg["eval_from"])[0]
        shapes = [[float(np.mean([ests[i][k][ec.SL_S][c] for k in ks]))
                   for c in (0, 1)] for i in range(cfg["N"])]
    return dict(seed=seed, turn=turn, D=D, shapes=shapes)

if __name__ == "__main__":
    grid = [(s, True) for s in range(25)] + [(s, False) for s in range(25)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(one, grid))
    turn = [r["D"] for r in res if r["turn"]]
    stra = [r["D"] for r in res if not r["turn"]]
    shapes = next(r["shapes"] for r in res if r["shapes"])
    print(f"turn D:     {np.mean(turn):.4e} (n={len(turn)})")
    print(f"straight D: {np.mean(stra):.4e} (n={len(stra)})")
    print(f"excess:     {np.mean(turn)-np.mean(stra):.4e}")
    print("operating shapes (mean s-hat):", np.round(shapes, 3).tolist())
    json.dump(dict(turn=turn, straight=stra, shapes=shapes),
              open("/workspaces/Anholonomy/tier2_drake/results/s1/matched_drake.json", "w"),
              indent=1)
    print("written matched_drake.json")
