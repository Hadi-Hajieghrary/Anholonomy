"""Shared single-plot IEEE figures used by both the L-CSS letter and T-CNS
section VIII: the statement-dependency map and the Tier-1 falsifier forest.
Each is a single axes. Outputs -> tier1_sheaf/results/artifacts/ieee/.
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from analysis.ieee_style import apply_ieee, COLW, DBLW, save
apply_ieee()
from tier1_sheaf.campaign.paper_artifacts import slopes   # replay-asserted

OUT = "/workspaces/Anholonomy/tier1_sheaf/results/artifacts/ieee"
os.makedirs(OUT, exist_ok=True)
PASS_C, FAIL_C, TRIP_C = "#009E73", "#c62828", "#D55E00"


def fig_theorem_map():
    fig, ax = plt.subplots(figsize=(DBLW, DBLW * 0.42))
    ax.axis("off")
    B = {
        "L31": (0.02, 0.74, "Lem 3.1\ntrivialization", "P"),
        "L32": (0.02, 0.40, "Lem 3.2\nedge maps", "P"),
        "SHF": (0.21, 0.57, "Estimation sheaf\n$\\rho{=}\\mathrm{Ad}_m{\\circ}\\pi_L$", "D"),
        "T51": (0.42, 0.80, "Thm 5.1 gauge\n$\\ker L_F{\\cong}\\mathfrak{se}(2)$", "P"),
        "C52": (0.64, 0.88, "Cor 5.2\npinning", "P"),
        "T63": (0.42, 0.50, "Thm 6.3\ncontraction", "P"),
        "L71": (0.21, 0.20, "Lem 7.1\nBCH", "P"),
        "T72": (0.46, 0.20, "Thm 7.2 floor\n$\\tau^2[C,C']{+}O(\\tau^3)$", "P"),
        "C73": (0.72, 0.30, "Cor 7.3\nsymmetry", "P"),
        "DSS": (0.74, 0.08, "$D_{ss}$ floor\n(sharp const.)", "C"),
    }
    E = [("L31", "SHF"), ("L32", "SHF"), ("SHF", "T51"), ("T51", "C52"),
         ("SHF", "T63"), ("L31", "L71"), ("L71", "T72"), ("SHF", "T72"),
         ("T72", "C73"), ("T72", "DSS")]
    tc = {"P": ("#e6f4ea", PASS_C), "C": ("#fdecea", FAIL_C), "D": ("#eceff1", "#455a64")}
    for k, (x, y, lab, tg) in B.items():
        fc, ec = tc[tg]
        ax.add_patch(FancyBboxPatch((x, y - 0.06), 0.16, 0.12,
                     boxstyle="round,pad=0.01", fc=fc, ec=ec, lw=0.8,
                     ls="--" if tg == "C" else "-", transform=ax.transAxes))
        ax.text(x + 0.08, y, lab, transform=ax.transAxes, fontsize=6,
                ha="center", va="center")
    for p, q in E:
        ax.annotate("", xy=(B[q][0], B[q][1]), xytext=(B[p][0] + 0.16, B[p][1]),
                    xycoords=ax.transAxes, arrowprops=dict(
                        arrowstyle="-|>", color="#607d8b", lw=0.7,
                        ls="--" if B[q][3] == "C" else "-",
                        connectionstyle="arc3,rad=0.06"))
    ax.text(0.02, 0.98, "green = [proven] $\\cdot$ dashed red = [conjectural] "
            "($D_{ss}$, a different object from the Thm 7.2 amplitude)",
            transform=ax.transAxes, fontsize=6, va="top", color="#455a64")
    save(fig, os.path.join(OUT, "theorem_map"))
    print("wrote theorem_map")


def fig_forest():
    rows = [
        ("C7a amplitude slope", min(slopes), np.mean(slopes), max(slopes),
         ("line", 2.0), "PASSED", PASS_C),
        ("C9b$'$ amp $\\epsilon$-exp", None, 1.006, None, ("line", 1.0),
         "PASSED", PASS_C),
        ("C6 contraction slope", None, 1.403, None, ("thr", 0.5), "PASSED", PASS_C),
        ("E10 $\\Delta t$-invar.", 1.185, 1.2205, 1.256, ("none", None),
         "PASSED", PASS_C),
        ("C19 remainder order", 2.32, 2.48, 2.65, ("band", (1.8, 2.2)),
         "TRIPPED (faster)", TRIP_C),
        ("C7b $D_{ss}$ $p$ [CONJ]", 1.076, 1.101, 1.125, ("line", 2.0),
         "FALSIFIED", FAIL_C),
        ("C9b $\\epsilon$-exp [CONJ]", 1.44, 1.58, 1.84, ("line", 2.0),
         "falsifier MET", FAIL_C),
        ("C9c robust $\\times$", 1.94, 2.75, 3.89, ("thr", 10.0), "TRIPS", FAIL_C),
    ]
    fig, ax = plt.subplots(figsize=(DBLW, DBLW * 0.42))
    for k, (lab, lo, mid, hi, ref, verdict, c) in enumerate(rows):
        y = len(rows) - 1 - k
        kind, rv = ref
        if kind == "line":
            ax.plot([rv, rv], [y - 0.3, y + 0.3], color="0.6", lw=0.7, ls="--")
        elif kind == "band":
            ax.fill_betweenx([y - 0.3, y + 0.3], rv[0], rv[1], color="0.85")
        elif kind == "thr":
            ax.plot([rv, rv], [y - 0.3, y + 0.3], color="0.6", lw=0.7, ls=":")
        if lo is not None:
            ax.plot([lo, hi], [y, y], color=c, lw=1.6)
            for e in (lo, hi):
                ax.plot([e, e], [y - 0.1, y + 0.1], color=c, lw=1.2)
        else:
            ax.annotate("(point est.)", (mid * 1.2, y), fontsize=5, color="0.5",
                        va="center")
        ax.plot(mid, y, "o", ms=4, color=c)
        ax.annotate(verdict, (11, y), fontsize=6, color=c, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=6)
    ax.set_xscale("log"); ax.set_xlim(0.4, 42)
    ax.set_xlabel("estimate (95\\% CI where declared); grey = registered "
                  "reference/threshold")
    ax.set_title("Tier-1 falsifier ledger, verdicts as adjudicated")
    save(fig, os.path.join(OUT, "t1_falsifier_forest"))
    print("wrote t1_falsifier_forest")


if __name__ == "__main__":
    fig_theorem_map()
    fig_forest()
