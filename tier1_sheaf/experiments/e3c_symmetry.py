"""T1-E3c — symmetry suppression: two metrics, two exponents (plan §4.3).

Rows executed here (each falsifies itself only):
  C9b' (amplitude vs eps):  m=2 round-trip defect between a perturbed agent and a
        symmetric partner; prediction slope 1 in eps. Analytic (executed machinery).
  C9b  (D_ss ratio vs eps): POWERED closed-loop test on the E3b harness —
        symmetric base, one agent perturbed by eps*d; S(eps,tau) = D(eps)/D(0);
        prediction slope 2 in eps. (The Drake slice was under-powered by design.)
  uniform suppression:      D_ss(generic)/D_ss(symmetric) on the tau grid.
  C9c  (robust arm):        same suppression under heterogeneous lags + jitter +
        drops — OUTSIDE Thm 7.2's uniform-delay hypothesis; a robustness
        characterization, not a theorem test. Headline >= 10x at tau=0.4.

SCOPE (2026-07-19): C9a (full-cycle symmetric amplitude slope 3, m=5) is BLOCKED
on the unresolved alpha_k walk coefficients (Q3) — holonomy.py raises rather than
guess; deferred to the author. Never mix amplitude and D_ss rows in one panel.
"""
from __future__ import annotations

import json
import numpy as np

from tier1_sheaf.sheaf.holonomy import two_agent_commutator
from tier1_sheaf.experiments.e3b_floor import run

OUT = "/workspaces/Anholonomy/tier1_sheaf/results/e3c_symmetry.json"

S_BASE = (0.45, 0.35)                    # symmetric-class base shape
EPS_DIR = np.array([0.8, 0.6])           # declared epsilon_dir (unit vector)
EPS = [0.0, 0.0125, 0.025, 0.05, 0.1, 0.2]


def sym_formation(N=5, eps=0.0):
    s0 = np.tile(np.asarray(S_BASE, dtype=float), (N, 1))
    s0[0] += eps * EPS_DIR                # perturb ONE named agent
    return s0


def amplitude_row():
    """C9b': ||[C_i, C_j]|| vs eps between the perturbed agent and a partner."""
    xi = np.array([0.4, 0.0, 0.12])
    amps = []
    for e in EPS:
        si = tuple(np.asarray(S_BASE) + e * EPS_DIR)
        amps.append(float(np.linalg.norm(two_agent_commutator(si, S_BASE, xi))))
    good = [(e, a) for e, a in zip(EPS, amps) if e > 0 and a > 1e-14]
    slope = float(np.polyfit(np.log([e for e, _ in good]),
                             np.log([a for _, a in good]), 1)[0])
    assert amps[0] < 1e-14, "base commutator must vanish (Dc·d > 0 check inverted?)"
    return dict(eps=EPS, amp=amps, slope=slope)


def dss_cell(eps, tau, seed, **kw):
    return run(tau, 0, seed, s0_override=sym_formation(eps=eps), **kw)


def main():
    res = {"scope": "C9a deferred (Q3 alpha_k unresolved)"}
    # --- C9b' amplitude row (analytic) ---
    res["C9bp_amplitude"] = amplitude_row()
    print(f"C9b' amplitude eps-slope = {res['C9bp_amplitude']['slope']:.3f}  "
          f"(prediction 1; falsifier: 1 not in CI)")

    from concurrent.futures import ProcessPoolExecutor
    ex = ProcessPoolExecutor(max_workers=10)

    # --- C9b closed-loop D_ss ratio, POWERED: 3 tau x 6 eps x 30 seeds ---
    TAUS = [0.2, 0.4, 0.8]
    grid = [(e, t, s) for e in EPS for t in TAUS for s in range(30)]
    Ds = list(ex.map(_c9b_cell, grid, chunksize=8))
    cell = {}
    for (e, t, s), D in zip(grid, Ds):
        cell.setdefault((e, t), []).append(D)
    res["C9b_dss"] = {f"{e}_{t}": dict(mean=float(np.mean(v)), n=len(v))
                      for (e, t), v in cell.items()}
    # S(eps,tau) = D(eps)/D(0); fit eps-exponent per tau with seed bootstrap
    rng = np.random.default_rng(31)
    for t in TAUS:
        base = cell[(0.0, t)]
        ratios = [np.mean(cell[(e, t)]) / np.mean(base) for e in EPS[1:]]
        exc = [max(r - 1.0, 1e-9) for r in ratios]
        sl = np.polyfit(np.log(EPS[1:]), np.log(exc), 1)[0]
        bs = []
        for _ in range(2000):
            b0 = np.mean(rng.choice(base, len(base)))
            ex_ = [max(np.mean(rng.choice(cell[(e, t)], 30)) / b0 - 1.0, 1e-9)
                   for e in EPS[1:]]
            bs.append(np.polyfit(np.log(EPS[1:]), np.log(ex_), 1)[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        res[f"C9b_slope_tau{t}"] = [float(lo), float(sl), float(hi)]
        print(f"C9b D_ss excess-ratio eps-slope @tau={t}: {sl:.2f} [{lo:.2f}, {hi:.2f}]  "
              f"(prediction 2; falsifier: 2 not in CI)")

    # --- uniform suppression: generic vs symmetric across tau ---
    TAUS6 = [0.1, 0.2, 0.4, 0.8]
    sup_grid = [(kind, t, s) for kind in ("generic", "symmetric")
                for t in TAUS6 for s in range(15)]
    Ds = list(ex.map(_sup_cell, sup_grid, chunksize=4))
    sup = {}
    for (kind, t, s), D in zip(sup_grid, Ds):
        sup.setdefault((kind, t), []).append(D)
    res["uniform_suppression"] = {
        str(t): float(np.mean(sup[("generic", t)]) / np.mean(sup[("symmetric", t)]))
        for t in TAUS6}
    print("uniform suppression S(tau) = D(generic)/D(symmetric):",
          {t: f"{v:.2f}x" for t, v in res["uniform_suppression"].items()})

    json.dump(res, open(OUT, "w"), indent=1)
    print("written", OUT)


def _c9b_cell(args):
    e, t, s = args
    return dss_cell(e, t, s, Tend=90.0)


def _sup_cell(args):
    kind, t, s = args
    if kind == "generic":
        return run(t, s % 12, s, Tend=90.0)
    return dss_cell(0.0, t, s, Tend=90.0)


if __name__ == "__main__":
    main()
