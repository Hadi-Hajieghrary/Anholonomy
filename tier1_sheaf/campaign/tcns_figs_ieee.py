"""T-CNS section VIII figures --- ONE plot per figure, IEEE journal style.
Every figure is a single axes at IEEE single-column width, produced from the
committed campaign JSONs. Outputs -> tier1_sheaf/results/artifacts/ieee/.
"""
import sys, os, json, csv
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
from analysis.ieee_style import apply_ieee, COLW, cyc, color, save
apply_ieee()

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
OUT = os.path.join(RES, "artifacts", "ieee")
os.makedirs(OUT, exist_ok=True)


def F(h=None):
    return plt.subplots(figsize=(COLW, h or COLW * 0.75))


def out(fig, name):
    save(fig, os.path.join(OUT, name)); print("wrote", name)


# --- plant diagram (single, C5) --------------------------------------------
def fig_plant():
    fig, ax = F(COLW * 0.85); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyBboxPatch((-0.4, -0.28), 0.8, 0.56, boxstyle="round,pad=0.05",
                 fc="#37474f", ec="k")); ax.text(0, 0, "$G$", color="w",
                 ha="center", va="center", fontsize=8)
    N = 5; ang = 0.5 * np.linspace(-1, 1, N); tips = []
    for j, sg in enumerate(ang):
        att = np.array([np.cos(sg), np.sin(sg)]) * 0.5
        tip = np.array([np.cos(sg), np.sin(sg)]) * 1.9; tips.append(tip)
        ax.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63", lw=1.0)
        tri = np.array([[0.2, 0], [-0.13, 0.1], [-0.13, -0.1]])
        c, s = np.cos(sg), np.sin(sg)
        ax.add_patch(Polygon(tri @ np.array([[c, -s], [s, c]]).T + tip,
                     closed=True, fc=color(j), ec="k", lw=0.5))
    for i in range(N):
        j = (i + 1) % N
        ax.plot([tips[i][0], tips[j][0]], [tips[i][1], tips[j][1]], "--",
                color=color(0), lw=0.7, alpha=0.7)
    ax.text(0.1, -1.25, "$s_j=(\\sigma_j,\\sigma_{i,j})$, cable $l$; $C_5$ comms",
            fontsize=7, ha="center")
    ax.set_xlim(-0.9, 2.4); ax.set_ylim(-1.5, 1.5)
    ax.set_title("Reduced plant: $N{=}5$ tow with $C_5$ communication")
    out(fig, "tcns_plant")


# --- E1 gauge trails + errors (from anim_gauge) ----------------------------
def _gauge():
    from tier1_sheaf.experiments.anim_gauge import simulate
    return simulate()


def fig_gauge_trails():
    tt, te, Dh, gh, ts, tb = _gauge(); ts = np.asarray(ts); N = len(te[0])
    kb = int(np.argmax(ts >= tb))
    truth = np.array([[T[0, 2], T[1, 2]] for T in tt])
    est = np.array([[[te[k][j][0, 2], te[k][j][1, 2]] for j in range(N)]
                    for k in range(len(ts))])
    fig, ax = F(COLW * 0.85)
    ax.plot(truth[:, 0], truth[:, 1], "-", color="k", lw=1.6, label="load truth")
    for j in range(N):
        ax.plot(est[:kb, j, 0], est[:kb, j, 1], "-", color=color(j), lw=0.9)
        ax.plot(est[kb:, j, 0], est[kb:, j, 1], "--", color=color(j), lw=0.9)
        ax.plot(est[kb, j, 0], est[kb, j, 1], "*", color=color(j), ms=7, mec="k")
    ax.plot([], [], "-", color="0.5", label="estimates (pre-beacon)")
    ax.plot([], [], "--", color="0.5", label="post-beacon")
    ax.set_aspect("equal"); ax.set_xlabel("$x$"); ax.set_ylabel("$y$")
    ax.set_title("E1: estimates drift as a group off truth, snap at beacon")
    ax.legend(fontsize=6)
    out(fig, "tcns_gauge_trails")


def fig_gauge_errors():
    tt, te, Dh, gh, ts, tb = _gauge(); ts = np.asarray(ts)
    fig, ax = F()
    ax.semilogy(ts, np.maximum(gh, 1e-4), "-", color=color(1),
                label="gauge error (vs truth)")
    ax.semilogy(ts, np.maximum(Dh, 1e-4), "--", color=color(0),
                label="disagreement $D$ (vs each other)")
    ax.axvline(tb, color="#c9a227", ls=":", lw=1.0)
    ax.annotate("beacon", (tb - 1, 4e-4), fontsize=6.5, ha="right", color="#8d6e00")
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("error"); ax.set_ylim(1e-4, 30)
    ax.set_title("$D$ runs an order of magnitude below the gauge error")
    ax.legend(fontsize=6.5, loc="lower left")
    out(fig, "tcns_gauge_errors")


# --- E1 spectrum (REAL sheaf Laplacian; no fabricated fallback) -------------
def fig_e1_spectrum():
    # Genuine gauge spectrum, computed from the sheaf Laplacian on the triangle
    # config of tier1_sheaf/experiments/e1_gauge.py (which asserts dim ker = 3).
    # No hardcoded fallback: if the operator regresses, the asserts fail loudly
    # rather than shipping fabricated eigenvalues.
    from tier1_sheaf.sheaf.laplacian import sheaf_laplacian
    SHAPES = [(0.4, 0.3), (0.9, -0.5), (-0.7, 0.6)]
    EDGES = [(0, 1), (1, 2), (2, 0)]
    L, _, _ = sheaf_laplacian(SHAPES, EDGES, weights=[1.0, 1.0, 1.0], l=1.0)
    ev = np.sort(np.linalg.eigvalsh(L))
    Lp = L.copy(); Lp[0:3, 0:3] += 1.0 * np.eye(3)   # Cor. pinning: one full-rank anchor
    evp = np.sort(np.linalg.eigvalsh(Lp))
    assert int((np.abs(ev) < 1e-9).sum()) == 3, "E1: gauge kernel dim != 3"
    assert int((np.abs(evp) < 1e-9).sum()) == 0, "E1: anchor did not remove the gauge"
    fig, ax = F()
    idx = np.arange(len(ev)); flo = 1e-16
    ax.bar(idx - 0.19, np.maximum(ev, flo), width=0.38, color=color(0),
           edgecolor="k", lw=0.3, label="unanchored")
    ax.bar(idx + 0.19, np.maximum(evp, flo), width=0.38, color=color(1),
           edgecolor="k", lw=0.3, label="one anchor (Cor.)")
    ax.set_yscale("log"); ax.set_ylim(1e-17, 30)
    ax.axhspan(1e-17, 1e-11, color="0.88", zorder=0)
    ax.annotate("$\\dim\\ker L_\\mathcal{F}=3$\n(the $SE(2)$ gauge)", (-0.2, 4e-14),
                fontsize=6, va="center", ha="left")
    ax.set_xlabel("mode index"); ax.set_ylabel("$\\lambda(L_\\mathcal{F})$")
    ax.set_xticks(idx)
    ax.legend(fontsize=6, loc="upper left", frameon=False, bbox_to_anchor=(0.02, 0.98))
    ax.set_title("E1 gauge spectrum: three zeros, one anchor removes them")
    out(fig, "tcns_e1_spectrum")


# --- amplitude (shared with L-CSS) -----------------------------------------
def fig_amplitude():
    rows = list(csv.reader(open(os.path.join(RES, "e3a_amplitude.csv"))))
    TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
    gen = np.array([float(x) for x in next(r for r in rows[1:] if r[0] == "generic")[2:8]])
    eta0 = np.array([float(x) for x in next(r for r in rows[1:]
                     if r[0].startswith("generic, eta=0"))[2:8]])
    fig, ax = F()
    ax.loglog(TAUS, gen, "o-", color=color(0), label="measured (slope 1.999)")
    ax.loglog(TAUS, gen[0] * (TAUS / TAUS[0]) ** 2, ":", color="k", label="$\\tau^2$")
    ax.loglog(TAUS, np.maximum(eta0, 1e-18), "s--", color=color(2),
              label="switch-offs (machine zero)")
    ax.set_ylim(1e-18, 3); ax.set_xlabel("$\\tau$ (s)")
    ax.set_ylabel("$\\|\\log\\mathrm{Hol}\\|$")
    ax.set_title("E3a amplitude: slope 1.999, coeff 1.0000")
    ax.legend(fontsize=6.5, loc="lower right")
    out(fig, "tcns_amplitude")


# --- 20 formations overlaid ------------------------------------------------
def fig_formations():
    from tier1_sheaf.campaign.formation_sweep_movie import forms, slopes
    fig, ax = F(COLW * 0.85); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyBboxPatch((-0.3, -0.2), 0.6, 0.4, boxstyle="round,pad=0.04",
                 fc="#37474f", ec="k", zorder=3))
    for idx, (si, sj) in enumerate(forms):
        for (sig, sgi) in (si, sj):
            tip = np.array([np.cos(sig), np.sin(sig)]) * 1.7
            ax.plot([0.4 * np.cos(sig), tip[0]], [0.4 * np.sin(sig), tip[1]],
                    "-", color=color(0), lw=0.5, alpha=0.35)
            ax.plot(*tip, ".", color=color(1), ms=2, alpha=0.6)
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
    ax.set_title(f"E3a: 20 formations overlaid; slope "
                 f"{np.mean(slopes):.4f} for every one")
    out(fig, "tcns_formations")


# --- D_ss floor figure (f4b tier-1) ----------------------------------------
def _e3b():
    return json.load(open(os.path.join(RES, "e3b_production.json")))


def fig_f4b():
    runs = _e3b(); taus = [0.1, 0.2, 0.4, 0.8]
    fig, ax = F()
    for arm, c, m, lab in [("paper", color(0), "o", "paper rule"),
                           ("straight", color(1), "s", "straight tow ($D_0$)"),
                           ("frozen", color(2), "^", "frozen shapes")]:
        med = [np.median([r["D"] for r in runs if r["arm"] == arm
                          and abs(r["tau"] - t) < 1e-9]) for t in taus]
        ax.loglog(taus, med, marker=m, color=c, label=lab)
    ax.loglog(taus, np.array(taus) ** 2 * 0.4, ":", color="k", label="$\\tau^2$ guide")
    ax.set_xlabel("$\\tau$ (s)"); ax.set_ylabel("$D_{ss}$")
    ax.set_title("E3b floor [CONJ]: excess slope 1.101 [1.076,1.125],\n"
                 "order 2 falsified at these scales")
    ax.legend(fontsize=6.3, loc="lower right")
    out(fig, "tcns_f4b")


def fig_dss_cdf():
    runs = _e3b(); arms = [("paper", "paper rule"), ("A1", "A1 (no comp.)"),
                           ("A2", "A2 (unconj.)"), ("straight", "straight ($D_0$)"),
                           ("frozen", "frozen")]
    fig, ax = F(); sty = cyc()
    for arm, lab in arms:
        D = np.sort([r["D"] for r in runs if r["arm"] == arm
                     and abs(r["tau"] - 0.4) < 1e-9])
        if len(D):
            s = next(sty)
            ax.step(np.maximum(D, 1e-32), np.arange(1, len(D) + 1) / len(D),
                    where="post", color=s["color"], ls=s["linestyle"], label=lab)
    ax.set_xscale("log"); ax.set_xlabel("$D_{ss}$ at $\\tau=0.4$")
    ax.set_ylabel("empirical CDF")
    ax.set_title("E3b per-run $D_{ss}$ by arm [CONJ regime]")
    ax.legend(fontsize=6, loc="upper left")
    out(fig, "tcns_dss_cdf")


def fig_dss_box():
    runs = _e3b(); taus = [0.1, 0.2, 0.4, 0.8]
    data = [[r["D"] for r in runs if r["arm"] == "paper" and abs(r["tau"] - t) < 1e-9]
            for t in taus]
    fig, ax = F()
    bp = ax.boxplot(data, tick_labels=[f"{t}" for t in taus], widths=0.5,
                    showfliers=False, patch_artist=True)
    for p in bp["boxes"]:
        p.set_facecolor("#b3cde3")
    ax.set_yscale("log"); ax.set_xlabel("$\\tau$ (s)")
    ax.set_ylabel("$D_{ss}$ (paper rule)")
    ax.set_title("E3b paper-rule spread across seeds/formations")
    out(fig, "tcns_dss_box")


def fig_ladder():
    runs = _e3b(); arms = ["paper", "A1", "A2", "straight", "frozen"]
    labs = ["paper", "A1 no-comp", "A2 unconj", "straight", "frozen"]
    taus = [0.1, 0.2, 0.4, 0.8]; cmap = plt.cm.viridis(np.linspace(0.15, 0.85, 4))
    fig, ax = F(); w = 0.18
    for i, t in enumerate(taus):
        m = [np.median([r["D"] for r in runs if r["arm"] == a
                        and abs(r["tau"] - t) < 1e-9]) for a in arms]
        ax.bar(np.arange(len(arms)) + (i - 1.5) * w, m, w, color=cmap[i],
               label=f"$\\tau={t}$")
    ax.set_yscale("log"); ax.set_xticks(range(len(arms)))
    ax.set_xticklabels(labs, fontsize=6, rotation=12)
    ax.set_ylabel("median $D_{ss}$")
    ax.set_title("E3b arms [CONJ]: A1 below paper (ordering inversion)")
    ax.legend(fontsize=6, ncol=2)
    out(fig, "tcns_ladder")


# --- floor dynamics --------------------------------------------------------
def fig_floor_dyn():
    from tier1_sheaf.campaign import floor_protocol_movie as fpm
    taus = [0.1, 0.2, 0.4, 0.8]
    runs = {t: (fpm.runs[t] if t in fpm.runs else fpm.run_traced(t)) for t in taus}
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(taus)))
    fig, ax = F()
    for t, c in zip(taus, cmap):
        rt, rD = runs[t][0], runs[t][1]
        ax.semilogy(rt, np.maximum(rD, 1e-6), "-", color=c, label=f"$\\tau={t}$")
        ax.plot(rt[-1], np.mean(rD[int(0.7 * len(rD)):]), "o", color=c, ms=3)
    ax.axvspan(0.7 * rt[-1], rt[-1], color="0.92", zorder=0)
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("$D(t)$"); ax.set_ylim(1e-6, 1)
    ax.set_title("E3b: $D(t)\\to D_{ss}$ [CONJ regime], higher for larger $\\tau$")
    ax.legend(fontsize=6, ncol=2, loc="lower right")
    out(fig, "tcns_floor_dyn")


# --- robust box (E3c) ------------------------------------------------------
def fig_robust():
    d = json.load(open(os.path.join(RES, "e3c_robust.json")))
    g, s = np.array(d["generic"]), np.array(d["symmetric"])
    fig, ax = F()
    bp = ax.boxplot([g, s], tick_labels=["generic", "symmetric"], widths=0.5,
                    showfliers=False, patch_artist=True)
    for p, c in zip(bp["boxes"], ["#fbb4ae", "#ccebc5"]):
        p.set_facecolor(c)
    ax.set_ylabel("$D_{ss}$ at $\\tau=0.4$ (robust arm)")
    ax.set_title("C9c TRIPS: 2.75$\\times$ [1.94,3.89] $<$ registered 10$\\times$\n"
                 "(jitter 20\\% + drops 10\\%, outside class $\\mathcal{P}$)")
    out(fig, "tcns_robust")


# --- symmetry f5 split -----------------------------------------------------
def fig_f5_amp():
    sym = json.load(open(os.path.join(RES, "e3c_symmetry.json")))
    eps = np.array(sym["C9bp_amplitude"]["eps"]); amp = np.array(sym["C9bp_amplitude"]["amp"])
    m = eps > 0; fig, ax = F()
    ax.loglog(eps[m], amp[m], "^-", color=color(0),
              label=f"slope {sym['C9bp_amplitude']['slope']:.3f}")
    ax.loglog(eps[m], amp[m][0] * (eps[m] / eps[m][0]), ":", color="k", label="$\\propto\\epsilon$")
    ax.set_xlabel("$\\epsilon$ (departure from symmetric class)")
    ax.set_ylabel("$\\|[C_i,C_j]\\|$")
    ax.set_title("C9b$'$ amplitude: first-order in $\\epsilon$ (PASSED)")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "tcns_f5_amp")


def fig_f5_floor():
    sym = json.load(open(os.path.join(RES, "e3c_symmetry.json")))
    paired = json.load(open(os.path.join(RES, "e3c_c9b_seeds.json")))["_paired_estimator"]
    epsg = sorted({float(k.split("_")[0]) for k in sym["C9b_dss"]})
    fig, ax = F()
    for t, c in zip(["0.2", "0.4", "0.8"], [color(1), color(4), color(2)]):
        base = sym["C9b_dss"][f"0.0_{t}"]["mean"]
        xs = [e for e in epsg if e > 0 and f"{e:g}_{t}" in sym["C9b_dss"]]
        ys = [sym["C9b_dss"][f"{e:g}_{t}"]["mean"] - base for e in xs]
        pr = paired[t]
        ax.loglog(xs, ys, "o-", color=c,
                  label=f"$\\tau$={t}: {pr['slope']:.2f} [{pr['ci'][0]:.2f},{pr['ci'][1]:.2f}]")
    xa = np.array(xs)
    ax.loglog(xa, ys[-1] * (xa / xa[-1]) ** 2, ":", color="k", label="$\\propto\\epsilon^2$")
    ax.set_xlabel("$\\epsilon$"); ax.set_ylabel("$D_{ss}(\\epsilon)-D_{ss}(0)$")
    ax.set_title("C9b floor [CONJ]: paired slope 1.58,\nfalsifier MET (2 and 1 excluded)")
    ax.legend(fontsize=6, loc="upper left")
    out(fig, "tcns_f5_floor")


# --- contraction (E2): xy portrait + decay ---------------------------------
def _contr():
    from tier1_sheaf.campaign.contraction_movie import data, SHAPES
    return data, len(SHAPES)


def fig_contraction_xy():
    data, N = _contr(); fig, ax = F(COLW * 0.85)
    for topo, mk, lab in [("cycle", "o", "$C_5$"), ("complete", "s", "$K_5$")]:
        tt, comp, pn = data[topo]
        for j in range(N):
            ax.plot(comp[:, j, 0], comp[:, j, 1], "-",
                    color=(color(0) if topo == "cycle" else color(1)),
                    lw=0.7, alpha=0.7)
        ax.plot(comp[0, 0, 0], comp[0, 0, 1], mk,
                color=(color(0) if topo == "cycle" else color(1)), ms=4, label=lab)
    ax.plot(0, 0, "k+", ms=11, mew=1.5)
    ax.set_aspect("equal"); ax.set_xlim(-0.45, 0.45); ax.set_ylim(-0.45, 0.45)
    ax.set_xlabel("$e_{\\perp,x}$"); ax.set_ylabel("$e_{\\perp,y}$")
    ax.set_title("E2: gauge-complement error spirals to consensus")
    ax.legend(fontsize=6.5)
    out(fig, "tcns_contraction_xy")


def fig_contraction_decay():
    data, N = _contr(); fig, ax = F()
    for topo, c, ls in [("cycle", color(0), "-"), ("complete", color(1), "--")]:
        tt, comp, pn = data[topo]
        ax.semilogy(tt, np.maximum(pn, 1e-9), ls, color=c, label=topo)
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("$\\|e_\\perp\\|$")
    ax.set_title("E2 decay rate grows with $\\kappa\\lambda_2$ (C6, slope 1.403)")
    ax.legend(fontsize=6.5)
    out(fig, "tcns_contraction_decay")


# --- dt invariance (E10) ---------------------------------------------------
def fig_dt():
    d = json.load(open(os.path.join(RES, "e10_dt_sweep.json")))
    dts = sorted(d.keys(), key=float)
    lo = [d[k]["exponent"][0] for k in dts]; mid = [d[k]["exponent"][1] for k in dts]
    hi = [d[k]["exponent"][2] for k in dts]
    fig, ax = F(); x = np.arange(len(dts))
    ax.fill_between([-0.5, len(dts) - 0.5], max(lo), min(hi), color="#ccebc5",
                    label=f"shared band [{max(lo):.3f},{min(hi):.3f}]")
    ax.errorbar(x, mid, yerr=[np.array(mid) - lo, np.array(hi) - mid], fmt="o",
                color=color(0), capsize=2)
    ax.set_xticks(x); ax.set_xticklabels([f"{float(k):g}" for k in dts])
    ax.set_xlabel("integrator step $\\Delta t$ (s)")
    ax.set_ylabel("fitted $D_{ss}$ exponent $p$")
    ax.set_title("E10: numerics invariance over $10\\times$ $\\Delta t$")
    ax.legend(fontsize=6.5)
    out(fig, "tcns_dt")


# --- topology bar (E6) -----------------------------------------------------
def fig_topology():
    d = json.load(open(os.path.join(RES, "e6_topology.json")))
    items = sorted(((k, v) for k, v in d.items() if isinstance(v, dict)),
                   key=lambda kv: kv[1]["lambda2"])
    x = np.arange(len(items))
    fig, ax = F()
    ax.bar(x - 0.19, [v["D02"] for _, v in items], 0.38, color=color(0),
           label="$\\tau=0.2$")
    ax.bar(x + 0.19, [v["D08"] for _, v in items], 0.38, color=color(1),
           hatch="//", label="$\\tau=0.8$")
    ax.set_yscale("log"); ax.set_xticks(x)
    ax.set_xticklabels([f"{k.split('_')[0][:4]}$_{k.split('_')[1]}$\n"
                        f"$\\lambda_2${v['lambda2']:.2f}" for k, v in items],
                       fontsize=5, rotation=0)
    ax.set_ylabel("$D_{ss}$")
    ax.set_title("E6 (C10): connectivity suppresses the floor at moderate $\\tau$")
    ax.legend(fontsize=6.5)
    out(fig, "tcns_topology")


# --- architecture diagram --------------------------------------------------
def fig_arch():
    fig, ax = plt.subplots(figsize=(COLW * 2, COLW * 0.75)); ax.axis("off")
    boxes = [(0.01, 0.55, "odometry 50\\,Hz\ndir 20\\,Hz", "#e3f2fd"),
             (0.22, 0.55, "InEKF propagate\n(slaved twist)", "#fff3e0"),
             (0.22, 0.12, "direction update\n($\\kappa_{dir}$)", "#fff3e0"),
             (0.45, 0.33, "sheaf fusion (paper):\n$\\rho{=}\\mathrm{Ad}_m{\\circ}\\pi_L$,\nage $\\tau$", "#e8f5e9"),
             (0.68, 0.55, "neighbor packets\n$\\tau$-stale", "#ede7f6"),
             (0.68, 0.12, "beacon (1 agent)\nCor. 5.2", "#fce4ec"),
             (0.87, 0.33, "$\\hat G_j$", "#eceff1")]
    for x, y, lab, fc in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 0.15, 0.22, boxstyle="round,pad=0.01",
                     fc=fc, ec="#455a64", transform=ax.transAxes))
        ax.text(x + 0.075, y + 0.11, lab, transform=ax.transAxes, fontsize=6,
                ha="center", va="center")
    for p, q in [((0.16, 0.66), (0.22, 0.66)), ((0.16, 0.6), (0.22, 0.23)),
                 ((0.37, 0.62), (0.45, 0.5)), ((0.37, 0.23), (0.45, 0.44)),
                 ((0.68, 0.62), (0.6, 0.5)), ((0.68, 0.23), (0.6, 0.44)),
                 ((0.6, 0.44), (0.87, 0.44))]:
        ax.annotate("", xy=q, xytext=p, xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color="#455a64", lw=0.8))
    ax.text(0.01, 0.02, "LOCAL sensing $\\cdot$ $\\tau$-stale SHARED estimates "
            "$\\cdot$ one ABSOLUTE beacon (truth-isolation linted)",
            transform=ax.transAxes, fontsize=6, color="#455a64")
    out(fig, "tcns_arch")


# --- contraction rate f8 ---------------------------------------------------
def fig_f8():
    d = json.load(open(os.path.join(RES, "e2_contraction.json")))
    rates = d["rates"]; lam = d["lambda2"]
    fig, ax = F()
    for topo, c, mk in [("cycle", color(0), "o"), ("complete", color(1), "s")]:
        ks = [0.0, 0.5, 1.0, 2.0]
        x = [k * lam[topo] for k in ks]
        y = [rates[f"{topo}_{k}"]["mean"] - rates[f"{topo}_0.0"]["mean"] for k in ks]
        ax.plot(x, y, marker=mk, color=c, label=topo)
    xl = np.array([0, max(2.0 * lam["complete"], 2.0 * lam["cycle"])])
    ax.plot(xl, xl, ":", color="k", label="unit slope")
    ax.set_xlabel("$\\kappa\\lambda_2$"); ax.set_ylabel("rate $-\\mu$")
    ax.set_title("E2 contraction: rate $\\propto\\kappa\\lambda_2$ (slope 1.403)")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "tcns_f8")


if __name__ == "__main__":
    for f in [fig_plant, fig_gauge_trails, fig_gauge_errors, fig_e1_spectrum,
              fig_amplitude, fig_formations, fig_f4b, fig_dss_cdf, fig_dss_box,
              fig_ladder, fig_floor_dyn, fig_robust, fig_f5_amp, fig_f5_floor,
              fig_contraction_xy, fig_contraction_decay, fig_dt, fig_topology,
              fig_arch, fig_f8]:
        try:
            f()
        except Exception as e:
            print("FAIL", f.__name__, repr(e)[:200])
    print("T-CNS IEEE figures done")
