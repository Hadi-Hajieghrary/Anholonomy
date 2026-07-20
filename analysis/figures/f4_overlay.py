"""F4 cross-tier overlay — the R9 capstone figure.

Three measured exponents on one tau-axis, with honest epistemic labels:
  * Tier-1 error-transport holonomy amplitude  ||Log Hol||  ~ tau^2.00  [PROV, Thm 7.2 leading order]
  * Tier-2 (Drake) state-level transport mismatch  M5       ~ tau^1.00  [measured; first-order state defect]
  * Tier-2 (Drake) steady-state disagreement floor D_ss     ~ tau^1.73  [CONJ regime; mixture fit]

CAPTION DISCIPLINE: the D_ss curve is NOT a validation of Thm 7.2 (which is
leading-order/deterministic); the tau^2 curve is the theorem's object.
"""
import csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/workspaces/Anholonomy"

# ---- Tier-1 E3a (generic arm) ----
with open(f"{ROOT}/tier1_sheaf/results/e3a_amplitude.csv") as fh:
    rows = list(csv.reader(fh))
hdr = rows[0]
t1_taus = np.array([float(h.split("=")[1]) for h in hdr[2:]])
gen = next(r for r in rows[1:] if r[0] == "generic")
t1_slope = float(gen[1])
t1_amp = np.array([float(v) for v in gen[2:]])

# ---- Tier-2 production v2 + straight-tow control ----
res = [r for r in json.load(open(f"{ROOT}/tier2_drake/results/s1/production_d2_d4_v2.json"))
       if r["kind"] == "d2" and r.get("D")]
ctl = [r for r in json.load(open(f"{ROOT}/tier2_drake/results/s1/d2_straight_control.json"))
       if r.get("D")]
t05 = [r for r in json.load(open(f"{ROOT}/tier2_drake/results/s1/d2_tau005.json"))
       if r.get("D")]
res += [r for r in t05 if r["kind"] == "d2"]
ctl += [dict(r, kind="straight") for r in t05 if r["kind"] == "straight"]
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
d_mean = np.array([np.mean([r["D"] for r in res if r["tau"] == t]) for t in TAUS])
m5_mean = np.array([np.mean([r["M5"] for r in res if r["tau"] == t]) for t in TAUS])
c_mean = np.array([np.mean([r["D"] for r in ctl if r["tau"] == t]) for t in TAUS])
# formation spread band on D_ss (12 per-formation means at each tau)
d_lo, d_hi = [], []
for t in TAUS:
    fm = [np.mean([r["D"] for r in res if r["tau"] == t and r["form"] == f]) for f in range(12)]
    d_lo.append(np.percentile(fm, 10)); d_hi.append(np.percentile(fm, 90))

fig, ax = plt.subplots(figsize=(7.0, 5.2), dpi=160)
C1, C2, C3 = "#1a6b8a", "#b3452c", "#5a5f2d"

ax.fill_between(TAUS, d_lo, d_hi, color=C2, alpha=0.18, lw=0,
                label=r"$D_{ss}$ formation spread (10–90%, 12 draws)")
ax.loglog(TAUS, d_mean, "o-", color=C2, ms=6, lw=1.8,
          label=r"Drake $D_{ss}$, turn arm — $p=1.08\,[1.05,1.10]$, full grid ($D_0$ measured; conjectured 2: falsified at these scales)")
ax.loglog(TAUS, c_mean, "o--", color=C2, ms=4, lw=1.1, alpha=0.55, mfc="none",
          label=r"Drake $D_{ss}$, straight-tow control — $19\text{–}21\times$ below (mechanism check passed)")
ax.loglog(TAUS, m5_mean, "s-", color=C3, ms=6, lw=1.8,
          label=r"Drake round-trip transport defect — $p=1.00$ (estimate-mismatch dominated)")
ax.loglog(t1_taus, t1_amp, "^-", color=C1, ms=6, lw=1.8,
          label=rf"Tier-1 $\|\mathrm{{Log\,Hol}}\|$ — $p={t1_slope:.2f}$  [PROV, Thm 7.2; Tier-1 data]")

# guide slopes anchored near the data
g = np.array([0.1, 1.6])
ax.loglog(g, 0.55 * m5_mean[0] * (g / TAUS[0]) ** 1, ":", color=C3, lw=1, alpha=0.7)
ax.loglog(g, 0.45 * t1_amp[1] * (g / t1_taus[1]) ** 2, ":", color=C1, lw=1, alpha=0.7)
ax.annotate(r"$\propto\tau$", (1.7, 0.55 * m5_mean[0] * 16), color=C3, fontsize=11)
ax.annotate(r"$\propto\tau^{2}$", (1.7, 0.45 * t1_amp[1] * 256), color=C1, fontsize=11)

ax.set_xlabel(r"staleness / delay  $\tau$  [s]")
ax.set_ylabel("steady-state amplitude  [SE(2) log norm]")
ax.set_title("Cross-tier overlay: three distinct objects, three measured exponents",
             fontsize=12)
ax.legend(fontsize=7.5, loc="lower right", framealpha=0.95)
ax.grid(True, which="both", alpha=0.25)
fig.text(0.5, 0.005,
         "Thm 7.2 is leading-order and deterministic — its object is the τ² curve (Tier-1, PROV). The closed-loop D_ss\n"
         "conjecture (order 2) is falsified at these scales per the pre-registered protocol (C7b-Drake, reported per §10 R2):\n"
         "with D₀ measured in situ by the straight-tow control, disagreement is first-order estimate-mismatch dominated.",
         ha="center", fontsize=7, style="italic", color="#555")
fig.tight_layout(rect=(0, 0.045, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"{ROOT}/tier2_drake/results/s1/f4_cross_tier_overlay.{ext}")
print("written f4_cross_tier_overlay.png/pdf")
print("tier1 slope:", t1_slope)
