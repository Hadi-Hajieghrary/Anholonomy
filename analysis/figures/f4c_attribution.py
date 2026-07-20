"""F4c — the variance-attribution figure (pre-registered outcome ladder §10 R2 item ii).

What makes up closed-loop disagreement, arm by arm, on the Drake plant:
  paper rule / turn      p=1.18  — the record
  paper rule / straight  19-21x below — motion excitation (mechanism check)
  A1 naive consensus     flat 5.8e-3 — agreement by groupthink (ANEES 62, drift 8.4 m)
  A2 un-conjugated       p=1.75, 1.7x -> 8.2x worse with tau — transport is load-bearing
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/workspaces/Anholonomy/tier2_drake/results/s1/"
TAUS = np.array([0.1, 0.2, 0.4, 0.8, 1.6])

prod = [r for r in json.load(open(BASE + "production_d2_d4_v2.json"))
        if r["kind"] == "d2" and r.get("D")]
arms = [r for r in json.load(open(BASE + "d2_a1_a2_arms.json")) if r.get("D")]
ctl = [r for r in json.load(open(BASE + "d2_straight_control.json")) if r.get("D")]
t05 = [r for r in json.load(open(BASE + "d2_tau005.json")) if r.get("D")]

def mean_curve(rows, kind=None, taus=TAUS):
    sel = rows if kind is None else [r for r in rows if r["kind"] == kind]
    return np.array([np.mean([r["D"] for r in sel if r["tau"] == t]) for t in taus])

TAUS6 = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
paper = mean_curve(prod + [r for r in t05 if r["kind"] == "d2"], taus=TAUS6)
a1 = mean_curve(arms, "A1")
a2 = mean_curve(arms, "A2")
straight = mean_curve(ctl + [dict(r, kind="x") for r in t05 if r["kind"] == "straight"],
                      taus=TAUS6)

fig, ax = plt.subplots(figsize=(7.0, 5.4), dpi=160)
ax.loglog(TAUS, a2, "D-", color="#8a2f1d", ms=6, lw=1.8,
          label=r"A2 un-conjugated transport — $p=1.75$; $1.7\to8.2\times$ worse with $\tau$")
ax.loglog(TAUS6, paper, "o-", color="#1a6b8a", ms=6, lw=2.2,
          label=r"paper rule, turn arm — $p=1.08\,[1.05,1.10]$ full grid (the record)")
ax.loglog(TAUS, a1, "s-", color="#77776a", ms=6, lw=1.6,
          label=r"A1 naive consensus — flat $5.8\mathrm{e}{-3}$ (groupthink: ANEES 62, drift 8.4 m)")
ax.loglog(TAUS6, straight, "o--", color="#1a6b8a", ms=4, lw=1.2, alpha=0.55, mfc="none",
          label=r"paper rule, straight tow — $19\text{–}21\times$ below (motion excitation)")

ax.annotate("transport compensation\nis load-bearing (C18)",
            xy=(0.8, 6.125e-1), xytext=(0.5, 1.15e-2),
            arrowprops=dict(arrowstyle="->", color="#8a2f1d", lw=1.2),
            fontsize=9, color="#8a2f1d")
ax.annotate("agreement is cheap;\nbeing right is not",
            xy=(0.4, 5.797e-3), xytext=(0.75, 1.6e-3),
            arrowprops=dict(arrowstyle="->", color="#55554a", lw=1.2),
            fontsize=9, color="#55554a")

ax.set_xlabel(r"staleness / delay  $\tau$  [s]")
ax.set_ylabel(r"steady-state disagreement  $D_{ss}$")
ax.set_title("Variance attribution: what makes up closed-loop disagreement", fontsize=12)
ax.legend(fontsize=8, loc="upper left", framealpha=0.95)
ax.grid(True, which="both", alpha=0.25)
fig.text(0.5, 0.005,
         "All arms: N=5 pentagon tow, matched formation draws and maneuver; A1/A2 per the pre-registered arm list.\n"
         "A1's low D is not success — it agrees on a mis-calibrated estimate (baselines table). Reported per outcome ladder §10 R2.",
         ha="center", fontsize=7, style="italic", color="#555")
fig.tight_layout(rect=(0, 0.04, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(BASE + f"f4c_variance_attribution.{ext}")
print("written f4c_variance_attribution.png/pdf")
