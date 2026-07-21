"""Static paper artifacts for the L-CSS letter and T-CNS §VIII (Tier-1 ONLY).

Every panel is generated from persisted campaign JSONs or from deterministic
re-computation that is ASSERTED against them (same seed, same consume order as
tier1_sheaf/campaign/e3a_extension.py). No Drake data enters this script — the
flagship §VIII split is Tier-1 only [papers/README.md].

Epistemic guards baked in:
  * D_ss panels carry the CONJ tag in-figure; nothing here captions a D_ss fit
    as validating Thm 7.2 (the theorem's object is the E3a amplitude).
  * Falsified / tripped rows are drawn as falsified (red), never dressed.

Outputs -> tier1_sheaf/results/artifacts/*.{pdf,png}
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Circle
from scipy.linalg import logm

from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                        error_transport_holonomy_m2,
                                        holonomy_amplitude_m2)
from tier1_sheaf.core.shapes import conjugated_generator

ROOT = "/workspaces/Anholonomy"
RES = os.path.join(ROOT, "tier1_sheaf", "results")
OUT = os.path.join(RES, "artifacts")
os.makedirs(OUT, exist_ok=True)

XI = np.array([0.4, 0.0, 0.12])
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])

plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
                     "legend.fontsize": 7.5, "figure.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False})

PASS_C, FAIL_C, TRIP_C, EXPL_C = "#2e7d32", "#c62828", "#e65100", "#546e7a"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=220)
    plt.close(fig)
    print("wrote", name)


# ----------------------------------------------------------------------------
# 0. Deterministic replay of the e3a_extension draw sequence (seed 2026, same
#    consume order) so the figure data BIT-MATCHES the persisted JSON.
# ----------------------------------------------------------------------------
ext = json.load(open(os.path.join(RES, "e3a_extension.json")))
rng = np.random.default_rng(2026)

def draw_shape(margin=0.10):
    while True:
        sig = rng.uniform(-1.2, 1.2)
        sig_i = rng.uniform(-1.2, 1.2)
        if abs(np.cos(sig_i)) > margin and abs(np.cos(sig)) > margin:
            return (float(sig), float(sig_i))

slopes = []
for f in range(20):
    si, sj = draw_shape(), draw_shape()
    amps = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in TAUS])
    if amps.min() > 1e-14:
        slopes.append(float(np.polyfit(np.log(TAUS), np.log(amps), 1)[0]))
assert np.allclose(slopes, ext["formation_cluster"]["slopes"], atol=1e-12), \
    "formation-cluster replay diverged from persisted e3a_extension.json"

sups, pair_bank = [], []
for d in range(220):
    si, sj = draw_shape(), draw_shape()
    pair_bank.append((si, sj))
    K = two_agent_commutator(si, sj, XI)
    per_tau = []
    for t in TAUS[:4]:
        H = error_transport_holonomy_m2(si, sj, XI, t)
        per_tau.append(np.linalg.norm(logm(H) - t ** 2 * K) / t ** 3)
    sups.append(max(per_tau))
assert abs(max(sups) - ext["remainder_constant"]["sup"]) < 1e-12, \
    "remainder-constant replay diverged from persisted e3a_extension.json"
print(f"replay asserts pass: 20 slopes, 220 sups (sup={max(sups):.6f})")


# ----------------------------------------------------------------------------
# 1. lcss_schematic — problem definition + notation (a); loop concept (b).
# ----------------------------------------------------------------------------
def fig_schematic():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.9))
    a.set_aspect("equal"); a.axis("off")
    a.set_title("(a) shapes, frames, and the trivialization")
    # load
    a.add_patch(FancyBboxPatch((-0.55, -0.35), 1.1, 0.7,
                boxstyle="round,pad=0.06", fc="#37474f", ec="k", zorder=3))
    a.annotate("$G$", (-0.28, -0.1), color="w", ha="center", fontsize=10, zorder=4)
    a.annotate("load pose $G\\in SE(2)$", (-1.5, 0.62), fontsize=8, zorder=4)
    a.annotate("", xy=(0.95, 0.0), xytext=(0.0, 0.0),
               arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2), zorder=5)
    a.annotate("", xy=(0.0, 0.95), xytext=(0.0, 0.0),
               arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2), zorder=5)
    a.annotate("$x_L$", (1.0, -0.06), fontsize=8)
    a.annotate("$y_L$", (0.06, 0.95), fontsize=8)
    # two agents on cables
    for (sig, col, lab) in [(0.55, "#1565c0", "i"), (-0.35, "#b71c1c", "j")]:
        att = np.array([np.cos(sig), np.sin(sig)]) * 0.62
        tip = np.array([np.cos(sig), np.sin(sig)]) * 2.1
        a.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63", lw=1.4)
        hd = sig + (0.5 if lab == "i" else -0.4)      # vessel heading != cable
        tri = np.array([[0.28, 0], [-0.18, 0.13], [-0.18, -0.13]])
        c, s = np.cos(hd), np.sin(hd)
        R = np.array([[c, -s], [s, c]])
        P = tri @ R.T + tip
        a.add_patch(Polygon(P, closed=True, fc=col, ec="k", zorder=4))
        a.annotate(f"agent ${lab}$", tip + np.array([0.1, 0.25]), color=col,
                   fontsize=8)
        if lab == "i":
            # sigma: cable direction at the LOAD (from x_L); sigma_i: cable
            # direction in the VESSEL frame (from the hull axis) — two
            # coordinates of ONE agent's shape s_i = (sigma, sigma_i)
            a.annotate("$\\sigma$", tip * 0.38 + np.array([0.05, 0.10]),
                       fontsize=9, color="#4e342e")
            a.annotate("$\\sigma_i$", tip + np.array([-0.42, -0.30]),
                       fontsize=9, color="#4e342e")
            hull = tip + 0.55 * np.array([np.cos(hd), np.sin(hd)])
            a.plot([tip[0], hull[0]], [tip[1], hull[1]], ":", color=col, lw=1.0)
    a.annotate("cable length $l$", (0.55, -1.15), fontsize=8, color="#4e342e")
    a.annotate("$m(\\sigma,\\sigma_i)=(R(\\sigma-\\sigma_i),\\ l(\\cos\\sigma,\\sin\\sigma))$",
               (-1.35, -1.85), fontsize=9)
    a.set_xlim(-1.6, 3.1); a.set_ylim(-2.1, 2.4)
    # (b) the commutator loop
    b.set_aspect("equal"); b.axis("off")
    b.set_title("(b) the non-closing error-transport loop")
    pts = {"P0": (0, 0), "P1": (1.6, 0.25), "P2": (1.9, 1.55), "P3": (0.35, 1.35)}
    legs = [("P0", "P1", "$e^{\\tau C_i}$"), ("P1", "P2", "$e^{\\tau C_j}$"),
            ("P2", "P3", "$e^{-\\tau C_i}$")]
    for p, q, lab in legs:
        b.annotate("", xy=pts[q], xytext=pts[p],
                   arrowprops=dict(arrowstyle="-|>", color="#1565c0", lw=1.6,
                                   connectionstyle="arc3,rad=0.12"))
        mid = (np.array(pts[p]) + np.array(pts[q])) / 2
        b.annotate(lab, mid + np.array([-0.12, 0.14]), fontsize=9, color="#1565c0")
    endp = (-0.28, 0.42)
    b.annotate("", xy=endp, xytext=pts["P3"],
               arrowprops=dict(arrowstyle="-|>", color="#1565c0", lw=1.6,
                               connectionstyle="arc3,rad=0.12"))
    b.annotate("$e^{-\\tau C_j}$", (-0.35, 0.95), fontsize=9, color="#1565c0")
    b.annotate("", xy=pts["P0"], xytext=endp,
               arrowprops=dict(arrowstyle="-|>", color=FAIL_C, lw=2.0))
    b.annotate("$\\log\\mathrm{Hol}=\\tau^2[C_i,C_j]+O(\\tau^3)$",
               (-0.9, -0.5), fontsize=9.5, color=FAIL_C)
    for p in pts.values():
        b.add_patch(Circle(p, 0.035, fc="k", zorder=5))
    b.add_patch(Circle(endp, 0.035, fc=FAIL_C, zorder=5))
    b.set_xlim(-1.2, 2.4); b.set_ylim(-0.8, 2.0)
    save(fig, "lcss_schematic")


# ----------------------------------------------------------------------------
# 2. theorem_map — statement dependency map + proof roadmap (shared by both).
# ----------------------------------------------------------------------------
def fig_theorem_map():
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    ax.axis("off")
    B = {  # name -> (x, y, label, tag)
        "L31": (0.06, 0.78, "Lem 3.1\ntrivialization\n$m(\\sigma,\\sigma_i)$", "P"),
        "L32": (0.06, 0.42, "Lem 3.2\nedge maps\nshape-only", "P"),
        "SHF": (0.27, 0.60, "Estimation sheaf\nstalks $\\mathfrak{se}(2)\\oplus\\mathbb{R}^2$\n$\\rho=\\mathrm{Ad}_m\\circ\\pi_L$, $w_e$", "D"),
        "T51": (0.48, 0.82, "Thm 5.1 gauge\n$\\ker L_F\\cong\\mathfrak{se}(2)$", "P"),
        "C52": (0.68, 0.90, "Cor 5.2\npinning", "P"),
        "C53": (0.68, 0.72, "Cor\ninheritance", "P"),
        "T63": (0.48, 0.52, "Thm 6.3 contraction\nrate $\\mu+\\kappa\\lambda_2-c_A$", "P"),
        "L71": (0.27, 0.20, "Lem 7.1\nBCH collection", "P"),
        "T72": (0.52, 0.20, "Thm 7.2 floor\n$\\log\\mathrm{Hol}=\\tau^2\\Sigma\\alpha_k[C,C']+O(\\tau^3)$\nleading-order, deterministic", "P"),
        "C73": (0.80, 0.28, "Cor 7.3\nsymmetry class", "P"),
        "DSS": (0.80, 0.08, "$D_{ss}$ stochastic floor\nsharp constants", "C"),
    }
    E = [("L31", "SHF"), ("L32", "SHF"), ("SHF", "T51"), ("T51", "C52"),
         ("T51", "C53"), ("SHF", "T63"), ("L31", "L71"), ("L71", "T72"),
         ("SHF", "T72"), ("T72", "C73"), ("T72", "DSS")]
    tagc = {"P": ("#e8f5e9", PASS_C), "C": ("#fbe9e7", TRIP_C), "D": ("#eceff1", "#37474f")}
    for k, (x, y, lab, tg) in B.items():
        fc, ec = tagc[tg]
        ax.add_patch(FancyBboxPatch((x - 0.005, y - 0.06), 0.17, 0.13,
                     boxstyle="round,pad=0.012", fc=fc, ec=ec, lw=1.2,
                     transform=ax.transAxes, zorder=3))
        ax.text(x + 0.08, y + 0.005, lab, transform=ax.transAxes, fontsize=6.8,
                ha="center", va="center", zorder=4)
    for p, q in E:
        x0, y0 = B[p][0] + 0.165, B[p][1]
        x1, y1 = B[q][0] - 0.005, B[q][1]
        sty = "-|>" if B[q][2][:6] != "$D_{ss" else "-|>"
        ls = "-" if B[q][3] != "C" else "--"
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle=sty, color="#607d8b", lw=1.1,
                                    linestyle=ls,
                                    connectionstyle="arc3,rad=0.08"))
    ax.text(0.02, 0.97, "solid green = [PROVEN]  ·  dashed/red = [CONJECTURAL] "
            "(sharp constants, stochastic steady state — a different object from "
            "the Thm 7.2 amplitude)", transform=ax.transAxes, fontsize=7,
            color="#37474f", va="top")
    save(fig, "theorem_map")


# ----------------------------------------------------------------------------
# 3. lcss_commutator_heatmap — ||[C(s_ref), C(s)]|| over the shape plane; the
#    zero locus is the LEVEL SET of s -> C(s; xi): the C15 protected class.
# ----------------------------------------------------------------------------
def fig_heatmap():
    # s_ref = the first C15 zero-commutator pair's first shape (persisted in
    # e3a_extension.json); its level PARTNER is the pair's second shape.
    s_ref = tuple(ext["C15"][0]["shapes"][:2])
    partner_seed = tuple(ext["C15"][0]["shapes"][2:])
    n = 241
    sig = np.linspace(-np.pi, np.pi, n)
    sgi = np.linspace(-np.pi, np.pi, n)
    Z = np.zeros((n, n))
    Cr = conjugated_generator(s_ref[0], s_ref[1], XI)
    for a, x in enumerate(sig):
        for b, y in enumerate(sgi):
            C = conjugated_generator(x, y, XI)
            Z[b, a] = np.linalg.norm(Cr @ C - C @ Cr)
    # polish every grid-local basin: the zero set is DISCRETE — exactly s_ref
    # and one partner shape over the whole torus [probed, this script's repo]
    from scipy.optimize import minimize
    f = lambda s: np.linalg.norm(
        (lambda C: Cr @ C - C @ Cr)(conjugated_generator(s[0], s[1], XI)))
    zeros = []
    for a in range(1, n - 1):
        for b in range(1, n - 1):
            if Z[a, b] == Z[a-1:a+2, b-1:b+2].min() and Z[a, b] < 1e-2:
                r = minimize(f, [sig[b], sgi[a]], method="Nelder-Mead",
                             options={"xatol": 1e-13, "fatol": 1e-15,
                                      "maxiter": 4000})
                if r.fun < 1e-9:
                    zeros.append((round(float(r.x[0]), 6),
                                  round(float(r.x[1]), 6)))
    zeros = sorted(set(zeros))
    assert len(zeros) == 2, f"expected the discrete 2-point level set, got {zeros}"
    partner = min(zeros, key=lambda z: np.hypot(z[0] - partner_seed[0],
                                                z[1] - partner_seed[1]))
    dC = np.linalg.norm(conjugated_generator(*partner, XI) - Cr)
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    im = ax.pcolormesh(sig, sgi, np.log10(np.maximum(Z, 1e-17)),
                       cmap="viridis", shading="auto", rasterized=True)
    ax.plot(*s_ref, marker="*", ms=12, color="w", mec="k", ls="none",
            label="$s_{\\mathrm{ref}}$")
    ax.plot(*partner, marker="o", ms=8, mfc="none", mec="w", mew=1.8, ls="none",
            label="level partner: $C=C_{\\mathrm{ref}}$")
    ax.legend(loc="upper left", fontsize=6.5, framealpha=0.25, labelcolor="w")
    ax.set_xlabel("$\\sigma$"); ax.set_ylabel("$\\sigma_i$")
    ax.set_title("$\\log_{10}\\Vert[C(s_{\\mathrm{ref}}),C(s)]\\Vert$")
    fig.colorbar(im, ax=ax, shrink=0.9)
    json.dump({"s_ref": list(s_ref), "grid_n": n, "domain": "[-pi,pi]^2",
               "zeros": [list(z) for z in zeros],
               "partner": list(partner),
               "partner_sep": float(np.hypot(partner[0] - s_ref[0],
                                             partner[1] - s_ref[1])),
               "partner_dC": float(dC),
               "z_max": float(Z.max())},
              open(os.path.join(OUT, "commutator_heatmap_meta.json"), "w"),
              indent=1)
    save(fig, "lcss_commutator_heatmap")


# ----------------------------------------------------------------------------
# 4. lcss_remainder_stats — CDF of R/tau^3 (220 draws) + slope histogram (20).
# ----------------------------------------------------------------------------
def fig_remainder():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5))
    xs = np.sort(sups); ys = np.arange(1, len(xs) + 1) / len(xs)
    a.step(xs, ys, where="post", color="#1565c0", lw=1.5)
    for v, lab in [(ext["remainder_constant"]["median"], "median"),
                   (ext["remainder_constant"]["p95"], "p95"),
                   (ext["remainder_constant"]["sup"], "sup")]:
        a.axvline(v, color="#90a4ae", lw=0.9, ls=":")
        a.annotate(f"{lab}\n{v:.4f}", (v, 0.06), fontsize=7, rotation=90,
                   va="bottom", ha="right", color="#455a64")
    a.set_xlabel("$\\sup_\\tau \\Vert R(\\tau,s)\\Vert/\\tau^3$ per draw")
    a.set_ylabel("empirical CDF")
    a.set_title("(a) remainder constant, 220 shape draws")
    b.hist(slopes, bins=12, color="#1565c0", alpha=0.85)
    b.axvline(2.0, color=FAIL_C, lw=1.2, ls="--")
    b.annotate("exact order 2", (2.0, b.get_ylim()[1] * 0.9), color=FAIL_C,
               fontsize=8, ha="right", rotation=90)
    mu, sd = np.mean(slopes), np.std(slopes)
    b.set_title(f"(b) fitted slope, 20 formations: {mu:.4f} $\\pm$ {sd:.1e}")
    b.set_xlabel("log–log slope of $\\Vert\\log\\mathrm{Hol}\\Vert$ vs $\\tau$")
    b.set_ylabel("count")
    save(fig, "lcss_remainder_stats")


# ----------------------------------------------------------------------------
# 5. lcss_bound_tightness — measured vs leading-order prediction.
# ----------------------------------------------------------------------------
def fig_bound():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.6))
    pred, meas, tt = [], [], []
    for (si, sj) in pair_bank[:60]:
        K = np.linalg.norm(two_agent_commutator(si, sj, XI))
        for t in TAUS[:4]:
            pred.append(t ** 2 * K)
            meas.append(holonomy_amplitude_m2(si, sj, XI, t))
            tt.append(t)
    pred, meas, tt = map(np.array, (pred, meas, tt))
    for t, col in zip(TAUS[:4], plt.cm.viridis(np.linspace(0.15, 0.9, 4))):
        m = tt == t
        a.loglog(pred[m], meas[m], "o", ms=2.5, color=col, alpha=0.7,
                 label=f"$\\tau={t}$")
    lo, hi = pred.min() * 0.7, pred.max() * 1.5
    a.loglog([lo, hi], [lo, hi], "k--", lw=1.0, label="prediction $=$ measured")
    a.legend(loc="upper left", ncol=1)
    a.set_xlabel("leading order $\\tau^2\\Vert[C_i,C_j]\\Vert$")
    a.set_ylabel("measured $\\Vert\\log\\mathrm{Hol}\\Vert$")
    a.set_title("(a) tightness, 60 draws $\\times$ 4 $\\tau$")
    ratios = {t: [] for t in TAUS[:4]}
    for p, m, t in zip(pred, meas, tt):
        ratios[t].append(m / p)
    med = [np.median(ratios[t]) for t in TAUS[:4]]
    p95 = [np.percentile(ratios[t], 95) for t in TAUS[:4]]
    p05 = [np.percentile(ratios[t], 5) for t in TAUS[:4]]
    b.fill_between(TAUS[:4], p05, p95, color="#90caf9", alpha=0.5,
                   label="5–95% band (width $<2\\times10^{-4}$)")
    b.plot(TAUS[:4], med, "o-", color="#1565c0", label="median")
    b.axhline(1.0, color="k", lw=0.9, ls="--")
    b.set_xticks(TAUS[:4])
    b.set_xticklabels([f"{t:g}" for t in TAUS[:4]])
    b.set_xlabel("$\\tau$"); b.set_ylabel("measured / leading order")
    b.set_title("(b) the $O(\\tau^3)$ gap closes as $\\tau\\to0$")
    b.legend(fontsize=6.5)
    json.dump({"n_pairs": 60, "taus": list(TAUS[:4]),
               "ratio_median": [float(x) for x in med],
               "ratio_p95": [float(x) for x in p95]},
              open(os.path.join(OUT, "bound_tightness_meta.json"), "w"), indent=1)
    save(fig, "lcss_bound_tightness")


# ----------------------------------------------------------------------------
# 6. lcss_domain_boundary — where the tau^2 leading order stops describing.
# ----------------------------------------------------------------------------
def fig_domain():
    si, sj = (0.55, 0.15), (-0.35, -0.7)
    K = np.linalg.norm(two_agent_commutator(si, sj, XI))
    ts = np.geomspace(0.05, 12.0, 60)
    amp = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in ts])
    lead = ts ** 2 * K
    rel = np.abs(amp - lead) / lead
    knee = float(ts[np.argmax(rel > 0.10)]) if (rel > 0.10).any() else np.inf
    assert np.isfinite(knee), "10% departure must be on the plotted range"
    # observed (exploratory): the RELATIVE departure is pair-independent —
    # probed identical to 3 digits across three unrelated shape pairs
    fig, ax = plt.subplots(figsize=(3.6, 2.7))
    ax.loglog(ts, amp, "o-", ms=3, color="#1565c0", label="measured")
    ax.loglog(ts, lead, "--", color="#455a64", label="$\\tau^2\\Vert[C_i,C_j]\\Vert$")
    ax.axvline(knee, color=FAIL_C, lw=1.1, ls=":")
    ax.annotate(f"10% departure\n$\\tau\\approx{knee:.2f}$", (knee * 1.1, amp[0] * 2),
                fontsize=7.5, color=FAIL_C)
    ax.set_xlabel("$\\tau$"); ax.set_ylabel("$\\Vert\\log\\mathrm{Hol}\\Vert$")
    ax.set_title("outside the leading-order domain")
    ax.legend(loc="lower right")
    json.dump({"shapes": [si, sj], "knee_tau_10pct": knee,
               "commutator_norm": float(K)},
              open(os.path.join(OUT, "domain_boundary_meta.json"), "w"), indent=1)
    save(fig, "lcss_domain_boundary")


# ----------------------------------------------------------------------------
# 7. t1_falsifier_forest — every adjudicated Tier-1 falsifier, verdicts drawn
#    as adjudicated (source: docs/ral_package.md ledger; evidence files named).
# ----------------------------------------------------------------------------
def fig_forest():
    rows = [  # (label, lo, mid, hi, ref descr, refspec, verdict, color)
        ("C7a amplitude slope\n(e3a_amplitude.csv)", min(slopes), np.mean(slopes),
         max(slopes), ("line", 2.0), "PASSED", PASS_C),
        ("C9b$'$ amplitude $\\epsilon$-exp\n(e3c_symmetry.json)", None, 1.006,
         None, ("line", 1.0), "PASSED", PASS_C),
        ("C6 contraction slope\n(e2_contraction.json)", None, 1.403, None,
         ("thresh_lo", 0.5), "PASSED", PASS_C),
        ("E10 $\\Delta t$-invariance exp.\n(e10_dt_sweep.json)", 1.185, 1.2205,
         1.256, ("none", None), "PASSED (shared CI band)", PASS_C),
        ("C19 remainder order\n(e2_contraction.json)", 2.32, 2.48, 2.65,
         ("band", (1.8, 2.2)), "TRIPPED (favorable: faster)", TRIP_C),
        ("C7b closed-loop $D_{ss}$ $p$ [CONJ]\n(e3b_production.json)", 1.076,
         1.101, 1.125, ("line", 2.0), "FALSIFIED at these scales", FAIL_C),
        ("C9b $D_{ss}$ $\\epsilon$-exp, paired [CONJ]\n(e3c_c9b_seeds.json)",
         1.44, 1.58, 1.84, ("line", 2.0), "falsifier MET (mixture)", FAIL_C),
        ("C9c robust suppression $\\times$\n(e3c_robust.json)", 1.94, 2.75, 3.89,
         ("thresh_hi", 10.0), "TRIPS ($<10\\times$)", FAIL_C),
    ]
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    for k, (lab, lo, mid, hi, ref, verdict, col) in enumerate(rows):
        y = len(rows) - 1 - k
        kind, rv = ref
        if kind == "line":
            ax.plot([rv, rv], [y - 0.32, y + 0.32], color="#90a4ae", lw=1.0, ls="--")
        elif kind == "band":
            ax.fill_betweenx([y - 0.32, y + 0.32], rv[0], rv[1],
                             color="#cfd8dc", alpha=0.7)
        elif kind in ("thresh_lo", "thresh_hi"):
            ax.plot([rv, rv], [y - 0.32, y + 0.32], color="#90a4ae", lw=1.0, ls=":")
        if lo is not None:
            ax.plot([lo, hi], [y, y], color=col, lw=2.2)
            ax.plot([lo, lo], [y - 0.12, y + 0.12], color=col, lw=1.6)
            ax.plot([hi, hi], [y - 0.12, y + 0.12], color=col, lw=1.6)
        ax.plot(mid, y, "o", ms=5, color=col)
        ax.annotate(verdict, (10.6, y), fontsize=7, color=col, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(0.4, 40)
    ax.set_xlabel("estimate (95% CI where declared) — log scale; grey = "
                  "registered reference/threshold")
    ax.set_title("Tier-1 falsifier ledger, adjudicated verdicts as registered")
    save(fig, "t1_falsifier_forest")


# ----------------------------------------------------------------------------
# 8. tcns_dss_dist — CDF + box of per-run D_ss by arm (E3b, 1584 runs) [CONJ].
# ----------------------------------------------------------------------------
def fig_dss():
    runs = json.load(open(os.path.join(RES, "e3b_production.json")))
    tau_ref = 0.4
    arms = ["paper", "A1", "A2", "straight", "frozen"]
    labels = {"paper": "paper rule", "A1": "A1 (no $\\mathrm{Ad}$)",
              "A2": "A2 (stale frame)", "straight": "straight tow ($D_0$)",
              "frozen": "frozen+noise-off"}
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.6))
    cols = plt.cm.tab10(np.linspace(0, 0.5, len(arms)))
    for arm, col in zip(arms, cols):
        D = np.sort([r["D"] for r in runs
                     if r["arm"] == arm and abs(r["tau"] - tau_ref) < 1e-9])
        if len(D) == 0:
            continue
        a.step(np.maximum(D, 1e-32), np.arange(1, len(D) + 1) / len(D),
               where="post", color=col, lw=1.4, label=f"{labels[arm]} (n={len(D)})")
    a.set_xscale("log"); a.set_xlabel(f"$D_{{ss}}$ at $\\tau={tau_ref}$")
    a.set_ylabel("empirical CDF"); a.legend(loc="upper left", fontsize=6.5)
    a.set_title("(a) per-run $D_{ss}$ CDF by arm")
    data, ticks = [], []
    for arm in arms:
        for t in [0.1, 0.2, 0.4, 0.8]:
            pass
    for t in [0.1, 0.2, 0.4, 0.8]:
        data.append([r["D"] for r in runs
                     if r["arm"] == "paper" and abs(r["tau"] - t) < 1e-9])
        ticks.append(f"{t}")
    bp = b.boxplot(data, tick_labels=ticks, widths=0.55, showfliers=False,
                   patch_artist=True)
    for p in bp["boxes"]:
        p.set_facecolor("#bbdefb")
    b.set_yscale("log")
    b.set_xlabel("$\\tau$"); b.set_ylabel("$D_{ss}$ (paper rule)")
    b.set_title("(b) paper-rule spread across seeds/forms")
    fig.text(0.5, -0.16, "$D_{ss}$ is the stochastic steady-state object "
             "[CONJECTURAL regime] — measured, not a test of Thm 7.2.",
             ha="center", fontsize=7.5, color="#37474f")
    save(fig, "tcns_dss_dist")


# ----------------------------------------------------------------------------
# 9. tcns_ladder_bars — switch-off / transport-rule ablation, medians by arm.
# ----------------------------------------------------------------------------
def fig_ladder():
    runs = json.load(open(os.path.join(RES, "e3b_production.json")))
    arms = ["paper", "A1", "A2", "straight", "frozen"]
    labels = ["paper rule", "A1 no-$\\mathrm{Ad}$", "A2 stale-frame",
              "straight tow ($\\eta{=}0$)", "frozen shapes\n(noise on)"]
    taus = [0.1, 0.2, 0.4, 0.8]
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    w = 0.18
    cols = plt.cm.viridis(np.linspace(0.15, 0.85, len(taus)))
    meds = {}
    for i, t in enumerate(taus):
        m = []
        for arm in arms:
            v = [r["D"] for r in runs
                 if r["arm"] == arm and abs(r["tau"] - t) < 1e-9]
            m.append(np.median(v) if v else np.nan)
        meds[t] = m
        x = np.arange(len(arms)) + (i - 1.5) * w
        ax.bar(x, m, width=w, color=cols[i], label=f"$\\tau={t}$")
    ax.set_yscale("log")
    ax.set_ylim(8e-4, 0.9)
    ax.set_xticks(range(len(arms)))
    ax.set_xticklabels(labels, fontsize=7, rotation=10)
    ax.set_ylabel("median $D_{ss}$")
    ax.legend(fontsize=6.5, ncol=2, loc="upper right")
    ax.set_title("E3b arms — median $D_{ss}$ [CONJ]. A1 below paper: the "
                 "Tier-1\nordering inversion (C18) — $D_{ss}$ never ranks rules",
                 fontsize=8)
    # the noise-off frozen NULL (D~6e-30, e3b regression probe) is reported in
    # text, not plotted: it is 27 orders below the axis
    json.dump({str(t): [None if not np.isfinite(v) else float(v) for v in meds[t]]
               for t in taus},
              open(os.path.join(OUT, "ladder_medians.json"), "w"), indent=1)
    save(fig, "tcns_ladder_bars")


# ----------------------------------------------------------------------------
# 10. tcns_topology — E6: connectivity vs floor (exploratory, C10).
# ----------------------------------------------------------------------------
def fig_topology():
    d = json.load(open(os.path.join(RES, "e6_topology.json")))
    items = sorted(((k, v) for k, v in d.items() if isinstance(v, dict)),
                   key=lambda kv: kv[1]["lambda2"])
    names = [k.replace("_", " $N{=}$") for k, _ in items]
    lam = [v["lambda2"] for _, v in items]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    x = np.arange(len(items))
    ax.bar(x - 0.19, [v["D02"] for _, v in items], width=0.38,
           color="#1565c0", label="$\\tau=0.2$")
    ax.bar(x + 0.19, [v["D08"] for _, v in items], width=0.38,
           color="#e65100", label="$\\tau=0.8$")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n$\\lambda_2$={l:.2f}" for n, l in zip(names, lam)],
                       fontsize=6.2)
    ax.set_ylabel("$D_{ss}$")
    ax.legend()
    ax.set_title("C10 (exploratory): connectivity suppresses the floor at "
                 "moderate $\\tau$; benefit collapses at high $\\tau$")
    save(fig, "tcns_topology")


# ----------------------------------------------------------------------------
# 11. tcns_dt_invariance — E10: exponent CI vs integrator step.
# ----------------------------------------------------------------------------
def fig_dt():
    d = json.load(open(os.path.join(RES, "e10_dt_sweep.json")))
    dts = sorted(d.keys(), key=float)
    lo = [d[k]["exponent"][0] for k in dts]
    mid = [d[k]["exponent"][1] for k in dts]
    hi = [d[k]["exponent"][2] for k in dts]
    band_lo, band_hi = max(lo), min(hi)
    fig, ax = plt.subplots(figsize=(3.8, 2.5))
    x = np.arange(len(dts))
    ax.fill_between([-0.5, len(dts) - 0.5], band_lo, band_hi,
                    color="#c8e6c9", alpha=0.8,
                    label=f"shared band [{band_lo:.3f}, {band_hi:.3f}]")
    ax.errorbar(x, mid, yerr=[np.array(mid) - lo, np.array(hi) - mid],
                fmt="o", color="#1565c0", capsize=3)
    ax.set_xticks(x); ax.set_xticklabels([f"{float(k):g}" for k in dts])
    ax.set_xlabel("integrator step $\\Delta t$ (s)")
    ax.set_ylabel("fitted $D_{ss}$ exponent $p$")
    ax.set_title("E10: numerics invariance over a 10$\\times$ $\\Delta t$ range")
    ax.legend(fontsize=7)
    save(fig, "tcns_dt_invariance")


# ----------------------------------------------------------------------------
# 12. tcns_robust — E3c robust arm: protection outside protocol class P.
# ----------------------------------------------------------------------------
def fig_robust():
    d = json.load(open(os.path.join(RES, "e3c_robust.json")))
    g, s = np.array(d["generic"]), np.array(d["symmetric"])
    fig, ax = plt.subplots(figsize=(3.2, 2.5))
    bp = ax.boxplot([g, s], tick_labels=["generic fan", "symmetric class"],
                    widths=0.5, patch_artist=True, showfliers=False)
    for p, c in zip(bp["boxes"], ["#ffcdd2", "#c8e6c9"]):
        p.set_facecolor(c)
    for arr, x in [(g, 1), (s, 2)]:
        ax.plot(np.full(len(arr), x) + np.random.default_rng(0).uniform(
            -0.08, 0.08, len(arr)), arr, ".", ms=3, color="#455a64", alpha=0.6)
    ax.set_ylabel("$D_{ss}$ at $\\tau=0.4$ (robust arm)")
    ax.set_title("C9c TRIPS: 2.75$\\times$ [1.94, 3.89] $<$ the registered "
                 "10$\\times$\n(jitter 20% + drops 10%: outside class "
                 "$\\mathcal{P}$)", fontsize=7.5)
    save(fig, "tcns_robust")


# ----------------------------------------------------------------------------
# 13. tcns_plant + tcns_architecture — problem definition; method pipeline.
# ----------------------------------------------------------------------------
def fig_plant():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.8))
    for ax, topo, ttl in [(a, "cycle", "(a) reduced plant, $C_5$ comms"),
                          (b, "complete", "(b) same plant, $K_5$ comms")]:
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(ttl)
        ax.add_patch(FancyBboxPatch((-0.4, -0.28), 0.8, 0.56,
                     boxstyle="round,pad=0.05", fc="#37474f", ec="k", zorder=3))
        ax.annotate("$G$", (0, 0), color="w", ha="center", va="center",
                    fontsize=10, zorder=4)
        N = 5
        ang = 0.5 * np.linspace(-1.0, 1.0, N)
        tips = []
        for j, sg in enumerate(ang):
            att = np.array([np.cos(sg), np.sin(sg)]) * 0.5
            tip = np.array([np.cos(sg), np.sin(sg)]) * 1.9
            tips.append(tip)
            ax.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63",
                    lw=1.2)
            tri = np.array([[0.2, 0], [-0.13, 0.1], [-0.13, -0.1]])
            c, s = np.cos(sg), np.sin(sg)
            R = np.array([[c, -s], [s, c]])
            ax.add_patch(Polygon(tri @ R.T + tip, closed=True,
                                 fc=plt.cm.tab10(j / 10), ec="k", zorder=4))
        edges = ([(i, (i + 1) % N) for i in range(N)] if topo == "cycle" else
                 [(i, j) for i in range(N) for j in range(i + 1, N)])
        for (i, j) in edges:
            ax.plot([tips[i][0], tips[j][0]], [tips[i][1], tips[j][1]],
                    "--", color="#1565c0", lw=0.9, alpha=0.75, zorder=2)
        ax.annotate("$s_j=(\\sigma_j,\\sigma_{i,j})$, cable $l$",
                    (0.1, -1.35), fontsize=8)
        ax.set_xlim(-0.9, 2.5); ax.set_ylim(-1.6, 1.6)
    save(fig, "tcns_plant")


def fig_architecture():
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.axis("off")
    boxes = [
        (0.01, 0.62, 0.17, "odometry $\\tilde\\zeta_j$ @ 50 Hz\n(gyro+wheel, "
         "bias walk)", "#e3f2fd"),
        (0.01, 0.22, 0.17, "cable direction $\\tilde\\sigma_{i,j}$\n@ 20 Hz",
         "#e3f2fd"),
        (0.23, 0.55, 0.17, "left-invariant\npropagation on $SE(2)$\n(slaved twist "
         "$\\zeta_j$)", "#fff3e0"),
        (0.23, 0.15, 0.17, "direction update\n($\\kappa_{dir}$)", "#fff3e0"),
        (0.44, 0.38, 0.21, "sheaf fusion (paper rule):\n$\\rho=\\mathrm{Ad}_m\\circ"
         "\\pi_L$, weights $w_e$\nexecuted composite, age $\\tau$", "#e8f5e9"),
        (0.70, 0.62, 0.14, "neighbor packets\n$(\\hat G_k,\\hat s_k)$, "
         "$\\tau$-stale", "#ede7f6"),
        (0.70, 0.15, 0.14, "beacon pin\n(one agent, Cor 5.2)", "#fce4ec"),
        (0.87, 0.38, 0.12, "$\\hat G_j$ load-pose\nestimate", "#eceff1"),
    ]
    for (x, y, w, lab, fc) in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, 0.24, boxstyle="round,pad=0.015",
                     fc=fc, ec="#455a64", transform=ax.transAxes))
        ax.text(x + w / 2, y + 0.12, lab, transform=ax.transAxes, fontsize=6.6,
                ha="center", va="center")
    arrows = [((0.16, 0.74), (0.22, 0.70)), ((0.16, 0.34), (0.22, 0.27)),
              ((0.39, 0.67), (0.45, 0.55)), ((0.39, 0.27), (0.45, 0.45)),
              ((0.70, 0.70), (0.62, 0.58)), ((0.70, 0.27), (0.62, 0.42)),
              ((0.64, 0.50), (0.87, 0.50))]
    for p, q in arrows:
        ax.annotate("", xy=q, xytext=p, xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color="#455a64", lw=1.2))
    ax.text(0.01, 0.02, "information availability: LOCAL = odometry + cable "
            "direction (per agent) · SHARED = $\\tau$-stale neighbor estimates "
            "on the graph · ABSOLUTE = one beacon at one agent (nothing else "
            "touches truth — linted)", transform=ax.transAxes, fontsize=6.8,
            color="#37474f")
    save(fig, "tcns_architecture")


if __name__ == "__main__":
    fig_schematic()
    fig_theorem_map()
    fig_heatmap()
    fig_remainder()
    fig_bound()
    fig_domain()
    fig_forest()
    fig_dss()
    fig_ladder()
    fig_topology()
    fig_dt()
    fig_robust()
    fig_plant()
    fig_architecture()
    print("all Tier-1 paper artifacts written to", OUT)
