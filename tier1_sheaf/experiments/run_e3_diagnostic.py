"""Run the E3 diagnostic, persist committed results, render the figure.

Output (under results/):
  e3_diagnostic.csv   — every arm's per-tau D_ss and fitted slope
  e3_diagnostic.png   — log-log D_ss(tau) for the diagnostic arms

These rows replace plan §4.1's "(inferred)" table with executed numbers.
"""
from __future__ import annotations

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier1_sheaf.experiments.e3_diagnostic import run, slope, GEN, SYM, TAUS

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)
SEEDS = range(6)

ARMS = [
    ("A2/generic  noise ON",  GEN, dict(fuse_rule="A2")),
    ("A2/generic  noise OFF", GEN, dict(fuse_rule="A2", noise_on=False)),
    ("A2/generic  eta=0",     GEN, dict(fuse_rule="A2", eta_on=False, noise_on=False)),
    ("A2/generic  path graph", GEN, dict(fuse_rule="A2", topology="path", noise_on=False)),
    ("paper rule  noise OFF",  GEN, dict(fuse_rule="paper", noise_on=False)),
    ("A2/symmetric noise ON",  SYM, dict(fuse_rule="A2")),
    ("A2/symmetric noise OFF", SYM, dict(fuse_rule="A2", noise_on=False)),
]


def main():
    rows = []
    curves = {}
    for label, sh, kw in ARMS:
        sl, mu = slope(sh, TAUS, SEEDS, **kw)
        curves[label] = mu
        rows.append((label, sl, *mu))
        flag = "  <- machine-zero (no floor)" if (np.nanmin(mu) < 1e-20) else ""
        print(f"{label:26s} slope={sl:8.4f}{flag}")

    with open(os.path.join(OUT, "e3_diagnostic.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "fitted_slope"] + [f"D_ss@tau={t}" for t in TAUS])
        w.writerows(rows)

    # figure: the two curves that carry the argument, plus the machine-zero floor
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    styles = {
        "A2/generic  noise ON":  ("#b2182b", "o-", 2.2),
        "A2/generic  eta=0":     ("#ef8a62", "s--", 1.8),
        "A2/generic  path graph": ("#fddbc7", "^:", 1.6),
        "paper rule  noise OFF":  ("#2166ac", "D-", 2.0),
        "A2/symmetric noise OFF": ("#1b7837", "v-", 2.0),
    }
    for label, (col, ls, lw) in styles.items():
        mu = np.array(curves[label])
        mu_plot = np.clip(mu, 1e-31, None)
        ax.loglog(TAUS, mu_plot, ls, color=col, lw=lw, ms=5, label=label)
    guide = curves["A2/generic  noise ON"][-1] * (np.array(TAUS) / TAUS[-1]) ** 2
    ax.loglog(TAUS, guide, "k--", lw=0.8, alpha=0.6, label="slope-2 guide")
    ax.set_xlabel(r"latency $\tau$ (s)")
    ax.set_ylabel(r"steady-state disagreement $D_{ss}$")
    ax.set_title("E3 diagnostic: the pilot's slope-2 is a per-edge artifact, not the holonomy floor\n"
                 r"(survives $\eta=0$; paper rule & symmetric-deterministic $\to$ machine zero)",
                 fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "e3_diagnostic.png"), dpi=150, bbox_inches="tight")
    print(f"\nwrote {OUT}/e3_diagnostic.csv and e3_diagnostic.png")


if __name__ == "__main__":
    main()
