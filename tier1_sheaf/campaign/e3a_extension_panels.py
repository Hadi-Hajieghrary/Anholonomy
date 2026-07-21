"""E3a extension panels — the four-panel figure cited by the L-CSS letter
(fig:ext) and T-CNS §VIII (fig:f4aext). Committed generator [audit catch
2026-07-21: the original figure shipped without one, contradicting the
package-integrity claim].

Panels (matching the papers' captions):
  (a) fitted slope across the 20 formation draws — formation-invariant;
  (b) per-draw remainder constant sup_tau ||R||/tau^3 over 220 draws;
  (c) the C15 zero-commutator pairs: ||[C_i,C_j]|| and ||C_i - C_j|| at
      >= 1 rad separation — the level-set class, machine zero;
  (d) coefficient ratio measured/leading -> 1 as tau -> 0.

Importing tier1_sheaf.campaign.paper_artifacts replays the e3a_extension
draw sequence seed-exactly and ASSERTS it against the committed JSON, then
exposes slopes/sups/pair_bank — this figure cannot drift from the record.
Regenerate with: python e3a_extension_panels.py
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier1_sheaf.campaign.paper_artifacts import (slopes, sups, pair_bank,
                                                  ext, XI, TAUS)
from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                        holonomy_amplitude_m2)
from tier1_sheaf.core.shapes import conjugated_generator

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.2))
(a, b), (c, d) = ax

# (a) formation-invariant slope
ref = 1.9992678569271
dev = (np.array(slopes) - ref) * 1e13
a.plot(range(1, 21), dev, "o", color="#1565c0")
a.axhline((np.mean(slopes) - ref) * 1e13, color="#2e7d32", lw=1.0)
a.set_ylim(-4, 4)
a.set_xlabel("formation draw")
a.set_ylabel("slope $-$ 1.9992678569271\n($\\times 10^{-13}$)")
a.set_title(f"(a) order is formation-invariant:\n"
            f"{np.mean(slopes):.10f} $\\pm$ {np.std(slopes):.1e}")

# (b) remainder constants
b.plot(range(1, len(sups) + 1), sups, ".", ms=3, color="#455a64", alpha=0.7)
for v, lab, cc in [(ext["remainder_constant"]["sup"], "sup 0.0133", "#c62828"),
                   (ext["remainder_constant"]["p95"], "p95 0.011", "#e65100"),
                   (ext["remainder_constant"]["median"], "median 0.005",
                    "#2e7d32")]:
    b.axhline(v, color=cc, lw=1.0, ls="--")
    b.annotate(lab, (228, v + 0.0002), fontsize=6.5, color=cc, va="bottom")
b.set_xlim(0, 265)
b.set_xlabel("shape draw")
b.set_ylabel("$\\sup_\\tau\\Vert R\\Vert/\\tau^3$")
b.set_title("(b) uniform $O(\\tau^3)$ remainder, 220 draws")

# (c) the C15 level-set pairs
seps = [p["sep"] for p in ext["C15"]]
comm = [max(p["comm"], 1e-19) for p in ext["C15"]]
dC = []
for p in ext["C15"]:
    Ci = conjugated_generator(p["shapes"][0], p["shapes"][1], XI)
    Cj = conjugated_generator(p["shapes"][2], p["shapes"][3], XI)
    dC.append(max(np.linalg.norm(Ci - Cj), 1e-19))
x = np.arange(len(seps))
c.bar(x - 0.18, comm, 0.36, color="#1565c0",
      label="$\\Vert[C_i,C_j]\\Vert$")
c.bar(x + 0.18, dC, 0.36, color="#2e7d32", label="$\\Vert C_i-C_j\\Vert$")
c.set_yscale("log"); c.set_ylim(1e-19, 1e-12)
c.axhline(1e-15, color="#90a4ae", lw=0.8, ls=":")
c.annotate("machine precision", (0.0, 1.6e-15), fontsize=6.5, color="#607d8b")
c.set_xticks(x)
c.set_xticklabels([f"{s:.2f}" for s in seps], fontsize=7)
c.set_xlabel("pair shape separation (rad, all $\\geq 1$)")
c.set_title("(c) C15: zero-commutator pairs have\n$C_i = C_j$ — the level-set "
            "class")
c.legend(fontsize=6.5, loc="upper right")

# (d) coefficient ratio -> 1
rat_med, rat_lo, rat_hi = [], [], []
for t in TAUS[:4]:
    r = []
    for (si, sj) in pair_bank[:60]:
        K = np.linalg.norm(two_agent_commutator(si, sj, XI))
        r.append(holonomy_amplitude_m2(si, sj, XI, t) / (t ** 2 * K))
    rat_med.append(np.median(r))
    rat_lo.append(np.percentile(r, 5)); rat_hi.append(np.percentile(r, 95))
d.fill_between(TAUS[:4], rat_lo, rat_hi, color="#90caf9", alpha=0.5)
d.plot(TAUS[:4], rat_med, "o-", color="#1565c0")
d.axhline(1.0, color="k", lw=0.9, ls="--")
d.set_xticks(TAUS[:4]); d.set_xticklabels([f"{t:g}" for t in TAUS[:4]])
d.set_xlabel("$\\tau$")
d.set_ylabel("measured / $\\tau^2\\Vert[C_i,C_j]\\Vert$")
d.set_title("(d) coefficient ratio $\\to$ 1 as $\\tau\\to0$\n(60 draws; 5–95% "
            "band)")

fig.tight_layout()
for e in ("pdf", "png"):
    fig.savefig(os.path.join(RES, f"e3a_extension_panels.{e}"),
                bbox_inches="tight", dpi=200 if e == "png" else None)
print("wrote e3a_extension_panels.pdf/png (committed generator)")
