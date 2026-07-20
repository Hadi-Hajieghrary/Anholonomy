"""F4b-overlay (CONJ panel of the capstone): Tier-1 E3b vs Drake D2 excess floors.

Mandated caption (CaptionRegistry literal, plan §6): "Tier-1/Tier-2 agreement on
the conjectured steady-state floor ([ES §10(ii)]). Panel (a) separately tests the
leading-order, deterministic holonomy amplitude of Thm 7.2 in both tiers."
Adjudication carried on the panel: both tiers exclude the conjectured order 2.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R1 = "/workspaces/Anholonomy/tier1_sheaf/results"
R2 = "/workspaces/Anholonomy/tier2_drake/results/s1"
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])

t1 = [r for r in json.load(open(f"{R1}/e3b_production.json")) if r["D"] is not None]
d2 = [r for r in json.load(open(f"{R2}/production_d2_d4_v2.json"))
      if r["kind"] == "d2" and r.get("D")]
t05 = [r for r in json.load(open(f"{R2}/d2_tau005.json")) if r.get("D")]
ctl = [r for r in json.load(open(f"{R2}/d2_straight_control.json")) if r.get("D")]

e1 = np.array([np.mean([r["D"] for r in t1 if r["arm"] == "paper" and r["tau"] == t])
               - np.mean([r["D"] for r in t1 if r["arm"] == "frozen" and r["tau"] == t])
               for t in TAUS])
p2pool = {t: [r["D"] for r in d2 if r["tau"] == t] for t in TAUS[1:]}
p2pool[0.05] = [r["D"] for r in t05 if r["kind"] == "d2"]
c2pool = {t: [r["D"] for r in ctl if r["tau"] == t] for t in TAUS[1:]}
c2pool[0.05] = [r["D"] for r in t05 if r["kind"] == "straight"]
e2 = np.array([np.mean(p2pool[t]) - np.mean(c2pool[t]) for t in TAUS])

fig, ax = plt.subplots(figsize=(7.0, 5.2), dpi=160)
C1, C2 = "#1a6b8a", "#b3452c"
ax.loglog(TAUS, e1, "^-", color=C1, ms=7, lw=1.9,
          label=r"Tier-1 reduced plant, E3b — excess $p=1.10\,[1.08,1.13]$")
ax.loglog(TAUS, e2, "o-", color=C2, ms=7, lw=1.9,
          label=r"Drake multibody, D2 — excess $p=1.08\,[1.05,1.10]$")
g = np.array([0.05, 1.6])
ax.loglog(g, e1[1] * (g / TAUS[1]), ":", color="#666", lw=1, alpha=0.7)
ax.annotate(r"$\propto\tau$", (1.7, e1[1] * 16), color="#666", fontsize=11)
ax.loglog(g, 0.3 * e1[1] * (g / TAUS[1]) ** 2, ":", color="#999", lw=1, alpha=0.7)
ax.annotate(r"$\propto\tau^{2}$ (conjectured)", (0.35, 0.3 * e1[1] * 0.10),
            color="#999", fontsize=9)

ax.text(0.03, 0.97,
        "pre-registered equivalence test:\n"
        r"$p_{T1}-p_{Drake}=+0.023\ [-0.012,+0.057]\subset[-0.2,+0.2]$"
        "\n→ exponents EQUIVALENT; conjectured order 2\n"
        "excluded on both plants (C7b falsified at these scales)",
        transform=ax.transAxes, fontsize=8.5, va="top",
        bbox=dict(fc="white", ec="#ccc", alpha=0.9))
ax.set_xlabel(r"staleness / delay  $\tau$  [s]")
ax.set_ylabel(r"$D_{ss}$ excess over measured control  [SE(2) log norm$^2$]")
ax.set_title("F4b-overlay: one estimator, two independent plants, one exponent",
             fontsize=12)
ax.legend(fontsize=9, loc="lower right", framealpha=0.95)
ax.grid(True, which="both", alpha=0.25)
fig.text(0.5, 0.005,
         "Tier-1/Tier-2 agreement on the conjectured steady-state floor ([ES §10(ii)]). Panel (a) separately tests the\n"
         "leading-order, deterministic holonomy amplitude of Thm 7.2 in both tiers. Coefficient-ratio comparison\n"
         "awaits the matched-config mapping (§6); the exponent claim is config-free.",
         ha="center", fontsize=7, style="italic", color="#555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"{R2}/f4b_overlay.{ext}")
print("written f4b_overlay.png/pdf")
