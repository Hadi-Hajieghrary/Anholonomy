"""F5 — symmetry figure (T-CNS §VIII fig E3c; also shipped by the RA-L
companion). Two objects, two panels, never mixed [plan §4.3]:
  (a) amplitude object (C9b'): ||[C_i,C_j]|| first-order in eps (PASSED 1.006);
  (b) closed-loop floor excess (C9b, [CONJ] regime): drawn with the
      ADJUDICATED seed-paired estimator — falsifier MET, slope 1.58
      [1.44, 1.84] at every tau (2 and 1 both excluded; single-power model
      mis-specified: segment slopes rise 1.2 -> 2.1).

Replaces the pre-adjudication rendering that displayed the retired UNPAIRED
CI [0.43, 2.89] with 'not falsified' — the ledger (docs/ral_package.md C9b)
rules that estimator UNDER-POWERED ('adjudicates nothing') and the paired
verdict MET. [audit catch 2026-07-21]

Reads only committed records: e3c_symmetry.json, e3c_c9b_seeds.json.
Regenerate with: python f5_symmetry_fig.py
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
sym = json.load(open(os.path.join(RES, "e3c_symmetry.json")))
seeds = json.load(open(os.path.join(RES, "e3c_c9b_seeds.json")))
paired = seeds["_paired_estimator"]

plt.rcParams.update({"font.size": 9, "axes.titlesize": 10})
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6))

# (a) amplitude object — C9b'
eps = np.array(sym["C9bp_amplitude"]["eps"])
amp = np.array(sym["C9bp_amplitude"]["amp"])
slope = sym["C9bp_amplitude"]["slope"]
m = eps > 0
a.loglog(eps[m], amp[m], "^-", color="#1a6b8a", ms=7,
         label=f"$\\Vert[C_i,C_j]\\Vert$ — slope {slope:.3f}")
a.loglog(eps[m], amp[m][0] * (eps[m] / eps[m][0]), ":", color="#999")
a.annotate("$\\propto\\epsilon$", (0.12, amp[m][0] * (0.12 / eps[m][0]) * 1.25),
           color="#999", fontsize=10)
a.set_xlabel("$\\epsilon$  (departure from the symmetric class)")
a.set_ylabel("$\\Vert[C_i,C_j]\\Vert$")
a.set_title("(a) amplitude object — C9b$'$: first-order in $\\epsilon$\n"
            "(base commutator exactly zero) — PASSED")
a.legend(loc="upper left")
a.grid(True, which="both", alpha=0.25)

# (b) closed-loop floor excess — C9b, paired estimator (adjudicated verdict)
taus = ["0.2", "0.4", "0.8"]
cols = ["#b3452c", "#8a6d1a", "#4c5a1e"]
eps_grid = sorted({float(k.split("_")[0]) for k in sym["C9b_dss"]})
for t, c in zip(taus, cols):
    base = sym["C9b_dss"][f"0.0_{t}"]["mean"]
    ex = [(e, sym["C9b_dss"][f"{e:g}_{t}"]["mean"] - base)
          for e in eps_grid if e > 0 and f"{e:g}_{t}" in sym["C9b_dss"]]
    xs, ys = zip(*ex)
    pr = paired[t]
    b.loglog(xs, ys, "o-", color=c, ms=6,
             label=f"$\\tau$={t}: paired slope {pr['slope']:.2f} "
                   f"[{pr['ci'][0]:.2f}, {pr['ci'][1]:.2f}]")
xs = np.array([e for e in eps_grid if e > 0])
b.loglog(xs, ys[-1] * (xs / xs[-1]) ** 2, ":", color="#999")
b.annotate("$\\propto\\epsilon^2$ (conjectured)", (0.06, 2.2e-3),
           color="#999", fontsize=10)
b.set_xlabel("$\\epsilon$")
b.set_ylabel("$D_{ss}(\\epsilon) - D_{ss}(0)$")
b.set_title("(b) closed-loop floor excess — C9b [CONJ]:\nfalsifier MET — "
            "seed-paired slope 1.58 [1.44, 1.84], 2 and 1 excluded")
b.legend(loc="upper left", fontsize=8)
b.grid(True, which="both", alpha=0.25)

fig.text(0.5, -0.14,
         "Two objects, two panels, never mixed (plan §4.3). Panel (a) is the "
         "theorem-adjacent amplitude; panel (b) is the conjectured $D_{ss}$ "
         "regime under the ADJUDICATED seed-paired estimator (the unpaired CI "
         "is under-powered and adjudicates nothing; segment slopes rise "
         "1.2$\\to$2.1 — a linear+quadratic mixture the registered single-power "
         "model mis-specifies). Robust suppression (jitter 20%, drops 10%): "
         "2.75$\\times$ [1.94, 3.89] ratio of arm means — the $\\geq$10$\\times$ "
         "falsifier TRIPS; large symmetric protection lives on the amplitude "
         "object only (31$\\times$ Drake, exact 0 Tier-1).",
         ha="center", fontsize=8, style="italic", color="#555", wrap=True)

for ext_ in ("pdf", "png"):
    fig.savefig(os.path.join(RES, f"f5_symmetry.{ext_}"), bbox_inches="tight",
                dpi=200 if ext_ == "png" else None)
print("wrote f5_symmetry.pdf/png (paired-verdict rendering)")
