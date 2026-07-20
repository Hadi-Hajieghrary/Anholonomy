"""D2 CONTROL ARMS (pre-registered protocol, plan §4.2/R3 + §5.4 D2 arm (c)).

straight-tow: SAME formations/seeds as production D2, turn_bias=turn_amp=0.
Purpose: (1) pin D0 (the tau-independent noise component) in situ;
         (2) the mechanism check — arm (c) falsifier: straight floor NOT >= 10x
             below the turn arm at tau=0.4 => motion x curvature story retracted.
Then refit p on the turn-arm data with D0 pinned (the protocol's floor-dominated fit).
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
cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), turn_bias=0.0,
           turn_amp=0.0, tau={tau}, formation="fan",
           front_arc={front_arc}, perturb={perturb})
out = run_seed(cfg, {seed})
print(f"RESULT {{floor_metrics(cfg, out):.6e}}")
"""


def cell(args):
    tau, form, seed = args
    rng = np.random.default_rng(form)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    code = CODE.format(form=form, tau=tau, front_arc=fa, perturb=pe, seed=seed)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd="/workspaces/Anholonomy", timeout=900)
    for l in r.stdout.splitlines():
        if l.startswith("RESULT"):
            return dict(kind="straight", tau=tau, form=form, seed=seed,
                        D=float(l.split()[1]))
    return dict(kind="straight", tau=tau, form=form, seed=seed, D=None,
                err=(r.stdout + r.stderr)[-150:])


GRID = [(t, f, s) for t in TAUS for f in range(N_FORM) for s in range(N_SEED)]

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID))
    ok = [r for r in res if r["D"] is not None]
    print(f"{len(ok)}/{len(GRID)} ok")
    out = "/workspaces/Anholonomy/tier2_drake/results/s1/d2_straight_control.json"
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)

    # per-tau straight means = the in-situ D0 curve
    prod = [r for r in json.load(open(
        "/workspaces/Anholonomy/tier2_drake/results/s1/production_d2_d4_v2.json"))
        if r["kind"] == "d2" and r.get("D")]
    print("tau   straight-D      turn-D        ratio")
    d0s = {}
    for t in TAUS:
        ds = np.mean([r["D"] for r in ok if r["tau"] == t])
        dt = np.mean([r["D"] for r in prod if r["tau"] == t])
        d0s[t] = ds
        print(f"{t:4}  {ds:.4e}  {dt:.4e}  {dt/ds:6.1f}x")
    print(f"mechanism check (arm c falsifier, tau=0.4): turn/straight = "
          f"{np.mean([r['D'] for r in prod if r['tau']==0.4])/d0s[0.4]:.1f}x  (>=10x required)")

    # protocol refit: D0 pinned from the straight arm's tau->0 end
    D0 = np.mean([r["D"] for r in ok if r["tau"] in (0.1, 0.2)])
    m = np.array([np.mean([r["D"] for r in prod if r["tau"] == t]) for t in TAUS])
    excess = m - D0
    print(f"pinned D0 (straight, tau<=0.2): {D0:.4e}")
    if np.all(excess > 0):
        # floor-dominated regime = points where excess > D0
        mask = excess > D0
        p = np.polyfit(np.log(np.array(TAUS)[mask]), np.log(excess[mask]), 1)[0]
        print(f"protocol p (D0-pinned, floor-dominated pts {mask.sum()}): {p:.3f}")
        # seed-level bootstrap of the pinned refit
        rng = np.random.default_rng(3)
        ps = []
        st = {t: [r["D"] for r in ok if r["tau"] == t] for t in TAUS}
        pr = {t: [r["D"] for r in prod if r["tau"] == t] for t in TAUS}
        for _ in range(2000):
            d0b = np.mean([np.mean(rng.choice(st[t], len(st[t]))) for t in (0.1, 0.2)])
            mb = np.array([np.mean(rng.choice(pr[t], len(pr[t]))) for t in TAUS])
            eb = mb - d0b
            mk = eb > max(d0b, 1e-12)
            if mk.sum() >= 3 and np.all(eb[mk] > 0):
                ps.append(np.polyfit(np.log(np.array(TAUS)[mk]), np.log(eb[mk]), 1)[0])
        if ps:
            lo, med, hi = np.percentile(ps, [2.5, 50, 97.5])
            print(f"protocol p bootstrap: {med:.3f}  [{lo:.3f}, {hi:.3f}]  "
                  f"(2 {'IN' if lo <= 2 <= hi else 'NOT in'} CI)")
    print("written", out)
