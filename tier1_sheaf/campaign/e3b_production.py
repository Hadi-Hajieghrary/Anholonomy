"""T1-E3b PRODUCTION (plan §4.2): the Tier-1 dynamic floor campaign.

Arms:
  paper x persistent_turn   6 tau x 12 forms x 10 seeds   (primary)
  paper x straight          6 tau x 12 x 3                (D0 control)
  paper x frozen(+noise)    6 tau x 12 x 3                (pure-noise floor, no shape motion)
  A1, A2 x persistent_turn  6 tau x 12 x 3                (diagnostics)

Analysis per the pre-registered protocol: D0 MEASURED from the frozen/straight
controls (never fitted); per-tau matched excess; run-level + formation-cluster
bootstraps; falsifier: 2 not in p's CI (generic arm) => C7b falsified (Tier-1).
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor

from tier1_sheaf.experiments.e3b_floor import run

TAUS = [0.05, 0.1, 0.2, 0.4, 0.8, 1.6]
OUT = "/workspaces/Anholonomy/tier1_sheaf/results/e3b_production.json"


def cell(args):
    arm, tau, form, seed = args
    kw = dict(fuse_rule="paper", eta_profile="persistent_turn", frozen=False)
    if arm == "straight":
        kw["eta_profile"] = "straight"
    elif arm == "frozen":
        kw["frozen"] = True
    elif arm in ("A1", "A2"):
        kw["fuse_rule"] = arm
    try:
        D = run(tau, form, seed, **kw)
        return dict(arm=arm, tau=tau, form=form, seed=seed, D=D)
    except Exception as e:
        return dict(arm=arm, tau=tau, form=form, seed=seed, D=None, err=str(e)[:120])


GRID = ([("paper", t, f, s) for t in TAUS for f in range(12) for s in range(10)]
        + [(a, t, f, s) for a in ("straight", "frozen", "A1", "A2")
           for t in TAUS for f in range(12) for s in range(3)])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID, chunksize=8))
    ok = [r for r in res if r["D"] is not None]
    print(f"{len(ok)}/{len(GRID)} ok")
    json.dump(res, open(OUT, "w"), indent=1)

    def curve(arm):
        return {t: [r["D"] for r in ok if r["arm"] == arm and r["tau"] == t]
                for t in TAUS}

    paper, straight, frozen = curve("paper"), curve("straight"), curve("frozen")
    a1, a2 = curve("A1"), curve("A2")
    print("tau     paper       straight    frozen      A1          A2")
    for t in TAUS:
        print(f"{t:5} {np.mean(paper[t]):.4e} {np.mean(straight[t]):.4e} "
              f"{np.mean(frozen[t]):.4e} {np.mean(a1[t]):.4e} {np.mean(a2[t]):.4e}")

    T = np.array(TAUS)
    # raw slope + protocol excess over the frozen control (pure-noise floor)
    pm = np.array([np.mean(paper[t]) for t in TAUS])
    fz = np.array([np.mean(frozen[t]) for t in TAUS])
    stc = np.array([np.mean(straight[t]) for t in TAUS])
    print(f"raw paper slope: {np.polyfit(np.log(T), np.log(pm), 1)[0]:.3f}")
    for name, ctrl in (("frozen", fz), ("straight", stc)):
        ex_ = pm - ctrl
        if np.all(ex_ > 0):
            print(f"excess-over-{name} slope: "
                  f"{np.polyfit(np.log(T), np.log(ex_), 1)[0]:.3f}")
    # run-level bootstrap of the excess-over-frozen exponent
    rng = np.random.default_rng(9)
    ps, ps_cl = [], []
    for _ in range(4000):
        e = np.array([np.mean(rng.choice(paper[t], len(paper[t])))
                      - np.mean(rng.choice(frozen[t], len(frozen[t]))) for t in TAUS])
        if np.all(e > 0):
            ps.append(np.polyfit(np.log(T), np.log(e), 1)[0])
    lo, med, hi = np.percentile(ps, [2.5, 50, 97.5])
    print(f"E3b excess exponent (run-level): {med:.3f} [{lo:.3f}, {hi:.3f}]  "
          f"(conjectured 2 {'IN' if lo <= 2 <= hi else 'NOT in'} CI)")
    # formation-cluster bootstrap (plan §8.2)
    pf = {(t, f): [r["D"] for r in ok if r["arm"] == "paper" and r["tau"] == t
                   and r["form"] == f] for t in TAUS for f in range(12)}
    ff = {(t, f): [r["D"] for r in ok if r["arm"] == "frozen" and r["tau"] == t
                   and r["form"] == f] for t in TAUS for f in range(12)}
    for _ in range(2000):
        pick = rng.choice(12, 12, replace=True)
        e = np.array([np.mean([v for f in pick for v in pf[(t, f)]])
                      - np.mean([v for f in pick for v in ff[(t, f)]]) for t in TAUS])
        if np.all(e > 0):
            ps_cl.append(np.polyfit(np.log(T), np.log(e), 1)[0])
    lo, med, hi = np.percentile(ps_cl, [2.5, 50, 97.5])
    print(f"E3b excess exponent (formation-cluster): {med:.3f} [{lo:.3f}, {hi:.3f}]")
    print("written", OUT)
