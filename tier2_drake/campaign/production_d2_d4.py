"""PRODUCTION D2 + D4 (plan §5.4, §8): the campaign centerpiece.

D2: tau {0.1..1.6} x 12 formation draws x 4 seeds (>=48 draws/point);
    FORMATION = the inferential unit -> cluster bootstrap (2000) for slope CIs;
    both metrics per run: D_ss (CONJ floor) and M5 (PROV amplitude, D3).
D4: epsilon-ladder off the TRUE symmetric class (parallel + graded perturb),
    eps {0, .05, .1, .2, .4} x tau=0.4 x 6 seeds.
Formation draw law [DESIGN, declared]: front_arc ~ U(0.7, 1.3),
perturb ~ U(-0.15, 0.15), drawn by formation id (reproducible).
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, subprocess, numpy as np
from concurrent.futures import ProcessPoolExecutor

TAUS = [0.1, 0.2, 0.4, 0.8, 1.6]
N_FORM, N_SEED = 12, 4
EPS = [0.0, 0.05, 0.1, 0.2, 0.4]

CODE = """
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics, m5_amplitude
rng = np.random.default_rng({form})
cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), turn_bias=0.03,
           turn_amp=0.02, tau={tau}, formation="{formation}",
           front_arc={front_arc}, perturb={perturb})
out = run_seed(cfg, {seed})
print(f"RESULT {{floor_metrics(cfg, out):.6e}} {{m5_amplitude(cfg, out):.6e}}")
"""

def cell(args):
    kind, tau, form, seed, eps = args
    if kind == "d2":
        rng = np.random.default_rng(form)
        fa, pe, formation = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15)), "fan"
    else:
        fa, pe, formation = 1.15, eps, "parallel"
    code = CODE.format(form=form, tau=tau, formation=formation,
                       front_arc=fa, perturb=pe, seed=seed)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd="/workspaces/Anholonomy", timeout=900)
    for l in r.stdout.splitlines():
        if l.startswith("RESULT"):
            D, M5 = map(float, l.split()[1:3])
            return dict(kind=kind, tau=tau, form=form, seed=seed, eps=eps, D=D, M5=M5)
    return dict(kind=kind, tau=tau, form=form, seed=seed, eps=eps, D=None,
                err=(r.stdout + r.stderr)[-150:])

GRID = ([("d2", t, f, s, None) for t in TAUS for f in range(N_FORM) for s in range(N_SEED)]
        + [("d4", 0.4, 100 + i, s, e) for i, e in enumerate(EPS) for s in range(6)])

def cluster_slope(res, key):
    """Cluster bootstrap over FORMATIONS of the MANDATED mixture fit
    D = D0 + C*tau^p (plan §8.2/R3 — naive log-log is banned)."""
    from scipy.optimize import curve_fit
    forms = sorted({r["form"] for r in res})
    lut = {(f, t): [r[key] for r in res if r["form"] == f and r["tau"] == t and r.get(key)]
           for f in forms for t in TAUS}
    f_mix = lambda t, D0, C, p: D0 + C * np.power(t, p)
    slopes = []
    rng = np.random.default_rng(0)
    for _ in range(2000):
        pick = rng.choice(forms, size=len(forms), replace=True)
        m = np.array([np.mean([v for f in pick for v in lut[(f, t)]]) for t in TAUS])
        try:
            (_, _, pexp), _ = curve_fit(f_mix, np.array(TAUS), m,
                                        p0=(m[0] * 0.8, m[-1] / 1.6 ** 2, 2.0),
                                        maxfev=5000)
            slopes.append(pexp)
        except Exception:
            pass
    return np.percentile(slopes, [2.5, 50, 97.5])

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=12) as ex:
        res = list(ex.map(cell, GRID))
    ok = [r for r in res if r.get("D")]
    d2 = [r for r in ok if r["kind"] == "d2"]
    print(f"{len(ok)}/{len(GRID)} ok  (d2: {len(d2)}/240)")
    for t in TAUS:
        Ds = [r["D"] for r in d2 if r["tau"] == t]
        Ms = [r["M5"] for r in d2 if r["tau"] == t]
        print(f"tau={t:>4}: D={np.mean(Ds):.3e} (n={len(Ds)})  M5={np.mean(Ms):.3e}")
    lo, med, hi = cluster_slope(d2, "D")
    print(f"D2 D_ss  exponent p (mixture fit, cluster bootstrap): {med:.3f}  [{lo:.3f}, {hi:.3f}]")
    lo, med, hi = cluster_slope(d2, "M5")
    print(f"D3 M5    exponent p (mixture fit, cluster bootstrap): {med:.3f}  [{lo:.3f}, {hi:.3f}]")
    print("--- D4 eps-ladder (tau=0.4, parallel base) ---")
    for e in EPS:
        Ds = [r["D"] for r in ok if r["kind"] == "d4" and r["eps"] == e]
        print(f"eps={e:>4}: D={np.mean(Ds):.3e}  (n={len(Ds)})")
    json.dump(res, open("/workspaces/Anholonomy/tier2_drake/results/s1/production_d2_d4_v2.json", "w"), indent=1)
    print("written production_d2_d4_v2.json")
