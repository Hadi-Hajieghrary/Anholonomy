"""E3a — the deterministic error-transport holonomy amplitude (the PROV floor test).

This is the experiment the pilot should have been. Thm 7.2 [thm:floor] proves
    || log Hol(gamma_c) || = O(tau^2),   Hol built from the conjugated error
generators C_j = Ad_{m(s_j)} ad_xi Ad_{m(s_j)}^{-1}. We measure that amplitude on
the m=2 round-trip walk (Q1 = (c): the theorem lives at error-transport level).

Contrast with pilot D_ss (results/e3_diagnostic.png): D_ss is stochastic, CONJ, and
FAILS the theorem's switch-offs (survives eta=0). The amplitude here is deterministic,
PROV, and must VANISH under each switch-off — that is what makes it the theorem's object.

Predictions (plan §2, §3 C7a/C9a/C13):
  * generic shapes:   slope 2  (PROV)
  * symmetric s_i=s_j: amplitude == 0 identically (Cor 7.3), floor is O(tau^3)
  * switch-offs eta=0, xi=0, tau->0: amplitude -> machine zero  (C13)
  * coefficient at m=2: || log Hol || / tau^2 -> ||[C_i,C_j]||  as tau->0  (C8, Q3 alpha=1)
"""
from __future__ import annotations

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier1_sheaf.sheaf.holonomy import holonomy_amplitude_m2, two_agent_commutator

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)

# A generic pair (distinct shapes) and a symmetric pair (identical shapes).
GEN_I, GEN_J = (0.4, 0.3), (0.9, -0.5)
SYM_I, SYM_J = (0.5, 0.2), (0.5, 0.2)
XI = np.array([0.4, 0.0, 0.12])          # common load twist (v, 0, eta)
XI_NOETA = np.array([0.4, 0.0, 0.0])     # eta = 0 switch-off
XI_ZERO = np.array([0.0, 0.0, 0.0])      # xi = 0 switch-off
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
MACHINE_ZERO = 1e-14


def amp_curve(shape_i, shape_j, xi):
    return np.array([holonomy_amplitude_m2(shape_i, shape_j, xi, t) for t in TAUS])


def fit_slope(taus, amp):
    good = amp > MACHINE_ZERO
    if good.sum() < 2:
        return float("nan")
    return float(np.polyfit(np.log(taus[good]), np.log(amp[good]), 1)[0])


def main():
    arms = {
        "generic":            amp_curve(GEN_I, GEN_J, XI),
        "symmetric (s_i=s_j)": amp_curve(SYM_I, SYM_J, XI),
        "generic, eta=0":     amp_curve(GEN_I, GEN_J, XI_NOETA),
        "generic, xi=0":      amp_curve(GEN_I, GEN_J, XI_ZERO),
    }
    slopes = {k: fit_slope(TAUS, v) for k, v in arms.items()}

    # coefficient check (C8, m=2): ||log Hol||/tau^2 -> ||[C_i,C_j]|| as tau->0
    comm_norm = float(np.linalg.norm(two_agent_commutator(GEN_I, GEN_J, XI)))
    ratio_smallest_tau = arms["generic"][0] / TAUS[0] ** 2

    print("=== E3a: deterministic holonomy amplitude ||log Hol||, m=2 round trip ===")
    for k, v in arms.items():
        amax = float(np.max(v))
        tag = "  <- machine zero (switch-off holds)" if amax < MACHINE_ZERO else ""
        print(f"  {k:22s} slope={slopes[k]:7.4f}   max||logHol||={amax:.3e}{tag}")
    print(f"\n  C8 coefficient (m=2): ||logHol||/tau^2 at tau={TAUS[0]} = {ratio_smallest_tau:.6f}")
    print(f"                        ||[C_i,C_j]||               = {comm_norm:.6f}"
          f"   (ratio {ratio_smallest_tau/comm_norm:.4f}, -> 1 as tau->0)")

    with open(os.path.join(OUT, "e3a_amplitude.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "fitted_slope"] + [f"amp@tau={t}" for t in TAUS])
        for k, v in arms.items():
            w.writerow([k, slopes[k], *v])

    # figure F4a
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    styles = {
        "generic":            ("#b2182b", "o-"),
        "symmetric (s_i=s_j)": ("#1b7837", "v-"),
        "generic, eta=0":     ("#ef8a62", "s--"),
        "generic, xi=0":      ("#2166ac", "D:"),
    }
    for k, (col, ls) in styles.items():
        v = np.clip(arms[k], 1e-20, None)
        lab = f"{k}  (slope {slopes[k]:.2f})" if not np.isnan(slopes[k]) else f"{k}  (→0)"
        ax.loglog(TAUS, v, ls, color=col, lw=2, ms=5, label=lab)
    guide = arms["generic"][-1] * (TAUS / TAUS[-1]) ** 2
    ax.loglog(TAUS, guide, "k--", lw=0.8, alpha=0.6, label="slope-2 guide")
    ax.set_xlabel(r"latency $\tau$ (s)")
    ax.set_ylabel(r"holonomy amplitude $\|\log\mathrm{Hol}(\gamma_c)\|$")
    ax.set_title("F4a — E3a: the PROV latency-curvature floor (Thm 7.2, error transport)\n"
                 r"slope 2 for generic shapes; vanishes under every switch-off ($\eta=0$, $\xi=0$, symmetric)",
                 fontsize=9.5)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.25, which="both")
    ax.set_ylim(1e-6, None)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "e3a_amplitude.png"), dpi=150, bbox_inches="tight")
    print(f"\nwrote {OUT}/e3a_amplitude.csv and e3a_amplitude.png")
    return slopes, arms


if __name__ == "__main__":
    main()
