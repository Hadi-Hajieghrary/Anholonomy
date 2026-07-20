"""F4a-overlay (PROV panel of the capstone): the error-transport holonomy
amplitude — Thm 7.2's object — measured on both plants.

This panel MAY name Thm 7.2, with its registered hedge: leading-order,
deterministic. Tier-1: E3a (analytic shapes). Drake: D3 (generators built from
the estimator's own closed-loop shape/twist states, l = 12 m).
"""
import csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R1 = "/workspaces/Anholonomy/tier1_sheaf/results"
R2 = "/workspaces/Anholonomy/tier2_drake/results/s1"

with open(f"{R1}/e3a_amplitude.csv") as fh:
    rows = list(csv.reader(fh))
t1_taus = np.array([float(h.split("=")[1]) for h in rows[0][2:]])
gen = next(r for r in rows[1:] if r[0] == "generic")
t1_amp = np.array([float(v) for v in gen[2:]])
t1_slope = float(gen[1])

d3 = json.load(open(f"{R2}/d3_amplitude.json"))
TAUS = np.array(d3["taus"])
fan = d3["arms"]["fan"]
par = d3["arms"]["parallel"]

fig, ax = plt.subplots(figsize=(7.0, 5.2), dpi=160)
C1, C2 = "#1a6b8a", "#b3452c"
ax.fill_between(TAUS, fan["amp_p10"], fan["amp_p90"], color=C2, alpha=0.15, lw=0,
                label="Drake per-edge spread (10–90%)")
ax.loglog(TAUS, fan["amp_mean"], "o-", color=C2, ms=6, lw=1.9,
          label=rf"Drake D3, fan — slope {fan['slope']:.3f}; coef check amp/$\tau^2\|[C_i,C_j]\|$ = {fan['coef_ratio_at_min_tau']:.4f}")
ax.loglog(TAUS, par["amp_mean"], "s--", color=C2, ms=5, lw=1.3, alpha=0.6, mfc="none",
          label=r"Drake D3, parallel — coefficient $31\times$ suppressed (achieved-$\varepsilon$, Cor 7.3)")
ax.loglog(t1_taus, t1_amp, "^-", color=C1, ms=6, lw=1.9,
          label=rf"Tier-1 E3a, generic — slope {t1_slope:.3f}; switch-offs machine zero")
g = np.array([0.05, 1.6])
ax.loglog(g, 0.35 * t1_amp[1] * (g / t1_taus[1]) ** 2, ":", color="#888", lw=1)
ax.annotate(r"$\propto\tau^{2}$", (1.05, 0.35 * t1_amp[1] * 300), color="#888", fontsize=11)
ax.text(0.03, 0.97,
        "Drake $\\eta$=0 switch-off: $[C_i,C_j] \\equiv 0$ exactly (C13)\n"
        "Tier-1 switch-offs ($\\eta$=0, $\\xi$=0, $s_i$=$s_j$): machine zero",
        transform=ax.transAxes, fontsize=8.5, va="top",
        bbox=dict(fc="white", ec="#ccc", alpha=0.9))
ax.set_xlabel(r"staleness / delay  $\tau$  [s]")
ax.set_ylabel(r"$\|\mathrm{Log\,Hol}\|$  (error-transport holonomy amplitude)")
ax.set_title("F4a-overlay: Thm 7.2's object on two independent plants", fontsize=12)
ax.legend(fontsize=8, loc="lower right", framealpha=0.95)
ax.grid(True, which="both", alpha=0.25)
fig.text(0.5, 0.005,
         "Thm 7.2 (leading-order, deterministic; PROV): ‖Log Hol‖ = O(τ²), holonomy built from the conjugated error\n"
         "generators. Drake generators use the estimator's own closed-loop shape/twist states (l = 12 m); the τ-law is the\n"
         "theorem's prediction — the measured content is the coefficient, the switch-offs, and the O(τ³) departure.",
         ha="center", fontsize=7, style="italic", color="#555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"{R2}/f4a_overlay.{ext}")
print("written f4a_overlay.png/pdf")
