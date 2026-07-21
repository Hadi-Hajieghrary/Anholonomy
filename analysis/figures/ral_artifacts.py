"""Static paper artifacts for the RA-L Blind Harbor companion.

Every quantitative panel is drawn from persisted campaign records
(tier2_drake/results/s1/*.json, *.npz) — nothing is re-simulated here.
Ledger verdicts are drawn AS ADJUDICATED (docs/ral_package.md): falsified rows
red, tripped rows orange; B1 is the record's own zero-latency all-to-all limit
("reference", never "oracle"); every ANEES number carries its horizon.

Outputs -> tier2_drake/results/s1/artifacts/*.{pdf,png}
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Circle

S1 = "/workspaces/Anholonomy/tier2_drake/results/s1"
OUT = os.path.join(S1, "artifacts")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
                     "legend.fontsize": 7.5, "figure.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False})
PASS_C, FAIL_C, TRIP_C = "#2e7d32", "#c62828", "#e65100"

ARM_LABEL = {"B1lim": "B1$^{lim}$ (record's zero-latency\nall-to-all limit)",
             "paper": "DIEKF-$\\Sigma$ (paper rule)",
             "B2": "B2 naive consensus", "B0": "B0 dead-reckon"}
ARM_COL = {"B1lim": "#455a64", "paper": "#1565c0", "B2": "#e65100",
           "B0": "#c62828"}


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=220)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------
# 1. ral_scenario — motivating problem + geometry + staleness timing.
# ---------------------------------------------------------------------------
def fig_scenario():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.9),
                               gridspec_kw={"width_ratios": [1.35, 1]})
    a.set_aspect("equal"); a.axis("off")
    a.set_title("(a) the Blind Harbor Transit", y=0.98)
    # dogleg reference path: leg 1 along x, 60 deg turn, leg 2
    t1 = np.linspace(0, 60, 40)
    p1 = np.stack([t1, np.zeros_like(t1)], 1)
    th = np.linspace(0, np.pi / 3, 30)
    Rr = 18.0
    c0 = p1[-1] + np.array([0, Rr])
    arc = c0 + Rr * np.stack([np.sin(th), -np.cos(th)], 1)
    t2 = np.linspace(0, 38, 30)
    d2 = np.array([np.cos(np.pi / 3), np.sin(np.pi / 3)])
    p2 = arc[-1] + t2[:, None] * d2[None, :]
    path = np.vstack([p1, arc, p2])
    # channel banks: normal offsets of the path (the banks FOLLOW the dogleg)
    tang = np.gradient(path, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    for sgn in (+1, -1):
        bank = path + sgn * 14.0 * nrm
        outer = path + sgn * 22.0 * nrm
        a.fill(np.r_[bank[:, 0], outer[::-1, 0]],
               np.r_[bank[:, 1], outer[::-1, 1]], color="#d7ccc8", lw=0)
    a.plot(path[:, 0], path[:, 1], "--", color="#607d8b", lw=1.2)
    # tow on leg 1 (heading +x)
    pos = p1[22]
    a.add_patch(Polygon(np.array([[-3, -2], [3, -2], [3, 2], [-3, 2]]) + pos,
                        closed=True, fc="#37474f", ec="k", zorder=4))
    for ang in np.linspace(-0.55, 0.55, 5):
        tip = pos + np.array([np.cos(ang), np.sin(ang)]) * 12
        a.plot([pos[0], tip[0]], [pos[1], tip[1]], "-", color="#8d6e63", lw=0.9)
        a.add_patch(Circle(tip, 1.1, fc="#1565c0", ec="k", lw=0.5, zorder=4))
    # beacon at dock, range-limited
    dock = p2[-1] + d2 * 4
    a.add_patch(Circle(dock, 2.2, fc="#c9a227", ec="k", zorder=4))
    a.add_patch(Circle(dock, 24, fc="none", ec="#c9a227", ls=":", lw=1.2))
    a.annotate("docking beacon\n(acquired only\nnear the dock)",
               dock + np.array([-52, 2]), fontsize=7, color="#8d6e00")
    a.annotate("60$°$ dogleg", (arc[12, 0] + 4, arc[12, 1] - 9), fontsize=7,
               color="#607d8b")
    a.annotate("GNSS-denied: odometry + cable sensing only",
               (-4, -26), fontsize=7, color="#4e342e")
    a.set_xlim(-8, 120); a.set_ylim(-30, 66)
    # (b) staleness timing ladder
    b.axis("off"); b.set_title("(b) information staleness")
    rows = [("own odometry", "50 Hz", 0.86, "#1565c0"),
            ("own cable direction", "20 Hz", 0.70, "#1565c0"),
            ("neighbor estimates", "$\\tau$-stale (0.05–1.6 s)", 0.54, "#e65100"),
            ("beacon (one agent)", "5 Hz, dock only", 0.38, "#c9a227")]
    for lab, rate, y, col in rows:
        b.annotate(lab, (0.02, y), xycoords="axes fraction", fontsize=8)
        b.annotate(rate, (0.62, y), xycoords="axes fraction", fontsize=8,
                   color=col)
        b.plot([0.02, 0.97], [y - 0.045, y - 0.045], "-", color="#eceff1",
               lw=0.8, transform=b.transAxes)
    b.annotate("the price of staleness:\nerror-transport holonomy "
               "$\\propto\\tau^2$ [PROVEN, both plants]\nclosed-loop floor: "
               "measured slope $\\approx$1.08 [CONJ regime]",
               (0.02, 0.08), xycoords="axes fraction", fontsize=7.5,
               color="#37474f")
    save(fig, "ral_scenario")


# ---------------------------------------------------------------------------
# 2. ral_architecture — DIEKF-Sigma pipeline with the truth-isolation split.
# ---------------------------------------------------------------------------
def fig_architecture():
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    ax.axis("off")
    ax.fill_betweenx([0.0, 1.0], 0.0, 0.30, color="#efebe9", alpha=0.7)
    ax.text(0.15, 0.955, "PLANT SIDE (Drake multibody)", ha="center",
            fontsize=7.5, color="#4e342e", transform=ax.transAxes)
    ax.text(0.66, 0.955, "ESTIMATOR SIDE (sensors only — truth-isolation lint)",
            ha="center", fontsize=7.5, color="#1b5e20", transform=ax.transAxes)
    boxes = [
        (0.01, 0.60, 0.14, "barge + $N$ ASVs,\ncables (distance\nconstr., "
         "tension)", "#d7ccc8"),
        (0.01, 0.18, 0.14, "HydroDrag +\nThruster (plant-\nside BY CLASS)",
         "#d7ccc8"),
        (0.17, 0.40, 0.12, "sensor models:\nodom 50 Hz, dir\n20 Hz, beacon\n"
         "5 Hz @ dock", "#ffe0b2"),
        (0.33, 0.62, 0.15, "InEKF propagate\n(left-invariant, slaved\ntwist via "
         "$\\mathrm{Ad}_{T(a)}$)", "#fff3e0"),
        (0.33, 0.16, 0.15, "direction update +\nbroadside guard\n($Q_G$ declared)",
         "#fff3e0"),
        (0.51, 0.40, 0.20, "executed-composite fusion\n$T=H_{stale}\\,"
         "m(\\hat s_j)^{-1}\\mathrm{Exp}(\\tau\\hat\\xi)$\n(frozen-shape exact)",
         "#e8f5e9"),
        (0.74, 0.64, 0.12, "comms fabric\n(drops, jitter,\ntopology)", "#ede7f6"),
        (0.74, 0.16, 0.12, "beacon update\n(agent 0, Cor 5.2)", "#fce4ec"),
        (0.88, 0.40, 0.11, "$\\hat G_i$, CI-fused\ncovariance", "#eceff1"),
    ]
    for (x, y, w, lab, fc) in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, 0.26, boxstyle="round,pad=0.015",
                     fc=fc, ec="#455a64", transform=ax.transAxes))
        ax.text(x + w / 2, y + 0.13, lab, transform=ax.transAxes, fontsize=6.3,
                ha="center", va="center")
    arrows = [((0.14, 0.73), (0.22, 0.60)), ((0.14, 0.31), (0.22, 0.45)),
              ((0.28, 0.53), (0.33, 0.70)), ((0.28, 0.45), (0.33, 0.30)),
              ((0.48, 0.70), (0.53, 0.55)), ((0.48, 0.30), (0.53, 0.48)),
              ((0.80, 0.64), (0.68, 0.58)), ((0.80, 0.42), (0.86, 0.48)),
              ((0.74, 0.30), (0.66, 0.40)), ((0.70, 0.52), (0.88, 0.52))]
    for p, q in arrows:
        ax.annotate("", xy=q, xytext=p, xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color="#455a64", lw=1.1))
    ax.text(0.01, 0.02, "commands are truth-free; the only state the estimator "
            "sees crosses through the sensor models (linted by class).",
            transform=ax.transAxes, fontsize=6.8, color="#37474f")
    save(fig, "ral_architecture")


# ---------------------------------------------------------------------------
# 3+4. trajectory + timeseries from the recorded hero dogleg npz (450 s).
# ---------------------------------------------------------------------------
def fig_hero_series():
    z = np.load(os.path.join(S1, "hero_dogleg_series.npz"))
    ts, D, kern, tq = z["ts"], z["D"], z["kern"], z["truth"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9),
                               gridspec_kw={"width_ratios": [1.15, 1]})
    a.plot(tq[:, 0], tq[:, 1], "-", color="#37474f", lw=1.6, label="load (truth)")
    for i in range(5):
        a.plot(tq[:, 3 + 3 * i], tq[:, 4 + 3 * i], "-", lw=0.7,
               color=plt.cm.tab10(i / 10), alpha=0.75)
    k_turn = (ts >= 200) & (ts <= 260)
    a.plot(tq[k_turn, 0], tq[k_turn, 1], "-", color=TRIP_C, lw=2.4,
           label="60$°$ dogleg (200–260 s)")
    k_b = ts >= 410
    a.plot(tq[k_b, 0], tq[k_b, 1], "-", color="#c9a227", lw=2.4,
           label="beacon window (410 s $\\to$)")
    a.plot(tq[0, 0], tq[0, 1], "o", color="k", ms=4)
    a.set_aspect("equal")
    a.set_xlabel("x (m)"); a.set_ylabel("y (m)")
    a.set_title("(a) recorded transit truth: barge + 5 ASVs")
    a.legend(fontsize=6.5, loc="upper left")
    b.semilogy(ts, np.maximum(D, 1e-7), "-", color="#1565c0", lw=1.2,
               label="disagreement $D(t)$")
    b.semilogy(ts, np.maximum(kern, 1e-7), "-", color="#7b1fa2", lw=1.2,
               label="gauge-kernel component")
    b.axvspan(200, 260, color="#ffe0b2", alpha=0.6)
    b.axvline(410, color="#c9a227", ls="--", lw=1.2)
    b.annotate("turn", (215, 8), fontsize=7.5, color=TRIP_C)
    b.annotate("beacon;\npin shock in $D$\n(D9 anti-ordering)", (405, 3e-5),
               fontsize=6.5, color="#8d6e00", ha="right")
    b.set_xlabel("t (s)"); b.set_ylim(1e-7, 60)
    b.set_title("(b) the maneuver excites disagreement;\nthe beacon kills the "
                "gauge, not the disagreement", fontsize=8.5)
    b.legend(fontsize=6.5, loc="lower left")
    save(fig, "ral_hero_series")


# ---------------------------------------------------------------------------
# 5. ral_agent_errors — S1-horizon per-agent anatomy (gain starvation is a
#    LONG-horizon phenomenon; here the anchored agent converges — the contrast
#    row for the D7 disclosure).
# ---------------------------------------------------------------------------
def fig_agent_errors():
    z = np.load(os.path.join(S1, "hero_series.npz"))
    ts, errs = z["ts"], z["errs"]
    # the beacon is wired to agent 0 BY BUILD (s1.py: i == 0); an argmin
    # heuristic misidentifies it from end-sample noise [audit catch]
    anch = 0
    fig, ax = plt.subplots(figsize=(4.2, 2.7))
    for i in range(errs.shape[1]):
        if i == anch:
            continue
        ax.semilogy(ts, np.maximum(errs[:, i], 1e-4), "-", lw=0.9,
                    color=plt.cm.tab10(i / 10), alpha=0.8)
    ax.semilogy(ts, np.maximum(errs[:, anch], 1e-4), "-", lw=2.0, color="#c9a227",
                label=f"anchored agent {anch} (beacon from 30 s)")
    ax.axvline(30, color="#c9a227", ls="--", lw=1.0)
    ax.set_xlabel("t (s)"); ax.set_ylabel("$\\Vert\\mathrm{Log}(\\hat G G^{-1})"
                                          "\\Vert$")
    ax.set_title("per-agent load-pose error, S1 horizon (130 s):\nanchor "
                 "propagates through fusion — at THIS horizon", fontsize=8.5)
    ax.legend(fontsize=7)
    save(fig, "ral_agent_errors")


# ---------------------------------------------------------------------------
# 6. ral_scorecard_stats — 50-transit distributions + win counts.
# ---------------------------------------------------------------------------
def fig_scorecard():
    d = json.load(open(os.path.join(S1, "d7_scorecard.json")))
    arms = ["B1lim", "paper", "B2", "B0"]
    pm = {a: np.array(sorted(r["pm"] for r in d if r["arm"] == a)) for a in arms}
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.7))
    bp = a.boxplot([pm[x] for x in arms],
                   tick_labels=["B1$^{lim}$", "paper", "B2", "B0"],
                   widths=0.55, patch_artist=True, showfliers=True)
    for p, x in zip(bp["boxes"], arms):
        p.set_facecolor(ARM_COL[x]); p.set_alpha(0.45)
    a.set_yscale("log")
    a.set_ylabel("fleet-mean dock error (m)")
    a.set_title("(a) 50 seeded transits per arm")
    for x in arms:
        b.step(pm[x], np.arange(1, 51) / 50, where="post", color=ARM_COL[x],
               lw=1.5, label=ARM_LABEL[x].replace("\n", " "))
    b.axvline(0.5, color="k", ls=":", lw=1.0)
    b.annotate("0.5 m docking spec (0% all arms\nat plan-faithful acquisition)",
               (0.34, 1.01), fontsize=6.0, ha="left", va="bottom",
               annotation_clip=False)
    b.set_xscale("log")
    b.set_xlabel("fleet-mean dock error (m)"); b.set_ylabel("CDF over seeds")
    b.legend(fontsize=6, loc="upper left")
    b.set_title("(b) per-seed CDF — ordering holds seed-wise")
    # win counts vs paper on pm (paired by seed)
    by_seed = {a: {r["seed"]: r["pm"] for r in d if r["arm"] == a} for a in arms}
    wins = {a: sum(1 for s in by_seed["paper"]
                   if by_seed["paper"][s] < by_seed[a][s]) for a in ("B2", "B0")}
    loss_b1 = sum(1 for s in by_seed["paper"]
                  if by_seed["paper"][s] > by_seed["B1lim"][s])
    b.legend(fontsize=5.6, loc="lower right", framealpha=0.9)
    fig.text(0.5, -0.17, f"seed-paired wins (fleet-mean): paper beats B2 in "
             f"{wins['B2']}/50 and B0 in {wins['B0']}/50; the zero-latency "
             f"limit beats paper in {loss_b1}/50 — staleness is the price.",
             ha="center", fontsize=7.5, color="#37474f")
    json.dump({"wins_vs_B2": wins["B2"], "wins_vs_B0": wins["B0"],
               "B1lim_beats_paper": loss_b1},
              open(os.path.join(OUT, "scorecard_wins.json"), "w"), indent=1)
    save(fig, "ral_scorecard_stats")


# ---------------------------------------------------------------------------
# 7. ral_v2_seeds — hero v2 per-seed outcomes: best/median/worst, honest.
# ---------------------------------------------------------------------------
def fig_v2_seeds():
    v2 = json.load(open(os.path.join(S1, "hero_v2_ensemble.json")))
    order = np.argsort([r["pm"] for r in v2])
    pms = np.array([v2[i]["pm"] for i in order])
    pas = np.array([v2[i]["pa"] for i in order])
    seeds = [v2[i]["seed"] for i in order]
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    x = np.arange(len(v2))
    ax.bar(x - 0.2, pms, width=0.4, color="#1565c0", label="fleet mean")
    ax.bar(x + 0.2, pas, width=0.4, color="#c9a227",
           label="anchored agent (gain-starved)")
    ax.axhline(0.5, color="k", ls=":", lw=1.0)
    ax.annotate("0.5 m spec", (len(v2) - 3.6, 0.54), fontsize=7)
    for tag, idx in (("best", 0), ("median", len(v2) // 2), ("worst", len(v2) - 1)):
        ax.annotate(tag, (idx, max(pms[idx], pas[idx]) + 0.12), fontsize=7,
                    ha="center", color="#37474f")
    ax.set_xticks(x); ax.set_xticklabels(seeds, fontsize=6.5)
    ax.set_xlabel("seed (sorted by fleet mean)")
    ax.set_ylabel("dock position error (m)")
    med = float(np.median(pms))
    ax.set_title(f"hero v2 (decelerating approach), 12 seeds:\nfleet-mean "
                 f"median {med:.2f} m, 17% $<$ 0.5 m — spec unmet;\nanchored "
                 f"agent worse than fleet mean on 11/12 (gain starvation)",
                 fontsize=8)
    ax.legend(fontsize=7)
    save(fig, "ral_v2_seeds")


# ---------------------------------------------------------------------------
# 8. ral_forest — Drake falsifier ledger, two scales (exponents/ratios | CIs
#    on differences and correlations).
# ---------------------------------------------------------------------------
def fig_forest():
    left = [  # log-scale: exponents & ratios
        ("D3 amplitude slope\n(d3_amplitude.json)", None, 2.000, None,
         ("line", 2.0), "PASSED", PASS_C),
        ("D3 coefficient\n(d3_amplitude.json)", None, 1.0000, None,
         ("band", (0.9, 1.1)), "PASSED", PASS_C),
        ("Cor 7.3 protection $\\times$\n(d3_amplitude.json)", None, 31.0, None,
         ("none", None), "PASSED (achieved-$\\epsilon$)", PASS_C),
        ("C7b-Drake $D_{ss}$ $p$ [CONJ]\n(production_d2_d4_v2)", 1.054, 1.077,
         1.102, ("line", 2.0), "FALSIFIED at these scales", FAIL_C),
        ("§6 excess-coef ratio\n(matched_drake/t1)", 3.97, 5.04, 6.19,
         ("band", (1 / 1.3, 1.3)), "DISAGREES $\\times$5 (1 rung run)", FAIL_C),
        ("C18 A2 degradation $\\times$\n(d2_a1_a2_arms.json)", 1.7, None, 8.2,
         ("line", 1.0), "PASSED (range over $\\tau$)", PASS_C),
    ]
    right = [  # linear scale: differences & correlations
        ("§6 exponent diff\n(f4b_overlay)", -0.012, 0.023, 0.057,
         ("band", (-0.2, 0.2)), "EQUIVALENT", PASS_C),
        ("D6 tension $\\Delta$RMSE (m)\n(d6_tension.json)", -0.0109, -0.0084,
         -0.0058, ("line", 0.0), "Part 1 PASSES", PASS_C),
        ("D9 pin-rate $\\rho$ vs $\\lambda_2$\n(d9_scaling.json; point est.,\n"
         "no CI registered)", None, 0.04,
         None, ("line", 0.0), "falsifier FIRES (anchor-limited)", FAIL_C),
        ("D9 re-lock $\\rho$\n(d9_scaling.json)", -0.65, -0.51, -0.36,
         ("line", 0.0), "ANTI-ORDERS (stiff consensus)", TRIP_C),
    ]
    fig, (aL, aR) = plt.subplots(1, 2, figsize=(7.8, 3.0),
                                 gridspec_kw={"width_ratios": [1.15, 1],
                                              "wspace": 0.85})

    def panel(ax, rows, xscale, xlim, note_x):
        for k, (lab, lo, mid, hi, ref, verdict, col) in enumerate(rows):
            y = len(rows) - 1 - k
            kind, rv = ref
            if kind == "line":
                ax.plot([rv, rv], [y - 0.3, y + 0.3], color="#90a4ae", lw=1.0,
                        ls="--")
            elif kind == "band":
                ax.fill_betweenx([y - 0.3, y + 0.3], rv[0], rv[1],
                                 color="#cfd8dc", alpha=0.7)
            if lo is not None and hi is not None:
                ax.plot([lo, hi], [y, y], color=col, lw=2.2)
                for e in (lo, hi):
                    ax.plot([e, e], [y - 0.1, y + 0.1], color=col, lw=1.6)
            if mid is not None:
                ax.plot(mid, y, "o", ms=5, color=col)
            ax.annotate(verdict, (note_x, y), fontsize=6.2, color=col,
                        va="center")
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=6.2)
        if xscale == "log":
            ax.set_xscale("log")
        ax.set_xlim(*xlim)

    panel(aL, left, "log", (0.5, 4000), 45)
    panel(aR, right, "lin", (-0.8, 1.55), 0.62)
    aL.set_xlabel("exponents / ratios (log)")
    aR.set_xlabel("differences / correlations")
    fig.suptitle("Drake falsifier ledger — verdicts as adjudicated "
                 "(docs/ral_package.md)", fontsize=9, y=1.02)
    save(fig, "ral_forest")


# ---------------------------------------------------------------------------
# 9. ral_robustness — D10(b) loss/jitter + D10(c) guard envelope, honest.
# ---------------------------------------------------------------------------
def fig_robustness():
    d = json.load(open(os.path.join(S1, "d10b_loss.json")))
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 2.6),
                               gridspec_kw={"wspace": 0.35})
    for J, col, lab in ((0, "#1565c0", "drops only (J=0)"),
                        (8, "#7b1fa2", "drops + jitter (J=8)")):
        ps, mean, sd = [], [], []
        for p in (0.0, 0.1, 0.3):
            v = [r["D"] for r in d
                 if r["kind"] == "floor" and r["p"] == p and r["J"] == J]
            ps.append(p); mean.append(np.mean(v)); sd.append(np.std(v))
        a.errorbar(ps, mean, yerr=sd, fmt="o-", color=col, capsize=3, label=lab)
    a.set_xlabel("packet-drop probability $p$")
    a.set_ylabel("floor $D_{ss}$")
    a.set_title("(a) D10(b): graceful — +13% @ $p$=0.1,\n+45% @ $p$=0.3; "
                "ANEES in-gate (4.23, 130 s)", fontsize=7.5)
    a.legend(fontsize=7)
    g = json.load(open(os.path.join(S1, "d10c_guard.json")))
    env = g["envelope_probe"]
    forces = sorted(env.keys(), key=float)
    x = np.arange(len(forces))
    b.bar(x - 0.18, [env[f]["min_cos_sigma_i_true"] for f in forces], 0.36,
          color="#37474f", label="true min $\\cos\\sigma_i$")
    b.bar(x + 0.18, [env[f]["min_cos_sigma_i_hat"] for f in forces], 0.36,
          color="#e65100", label="estimated $\\hat\\sigma_i$")
    b.set_xticks(x)
    b.set_xticklabels([f"{float(f):.0f} N gust" for f in forces])
    b.set_ylabel("closest broadside approach")
    b.set_title("(b) D10(c): $\\hat\\sigma_i$ LAGS true broadside —\nguard "
                "unexercised (ON$\\,\\equiv\\,$OFF)", fontsize=7.5)
    b.legend(fontsize=7)
    save(fig, "ral_robustness")


# ---------------------------------------------------------------------------
# 10. ral_failure_taxonomy — the four adverse findings, causes, remedies.
# ---------------------------------------------------------------------------
def fig_taxonomy():
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.axis("off")
    cards = [
        (0.01, "docking spec unmet:\n0% $<$ 0.5 m, all arms\n(incl. B1$^{lim}$)",
         "cause: approach GEOMETRY —\nbeacon window too short at\ntransit speed",
         "remedy: decelerating approach\n(v2: 2.4$\\times$ better, 17% pass —\n"
         "necessary, not sufficient)", "d7_scorecard.json"),
        (0.26, "anchored agent worse than\nfleet mean, 11/12 seeds (v2)",
         "cause: GAIN STARVATION —\nKalman anchoring collapses $P$;\nCI "
         "conservatism protects others\n(m$_\\xi$-trim tested:\nbit-identical, "
         "falsified)",
         "remedy class: covariance floor /\nadaptive beacon $R$ (revision)",
         "hero_v2_ensemble.json"),
        (0.51, "M-FAB ANEES gate does NOT\ntransfer to 450 s (159–229)",
         "cause: bias random-walk growth\nexceeds declared $Q$ over long\n"
         "horizons; gate closed at 130 s (3.96)",
         "remedy: horizon-scoped claims\n(every ANEES carries its horizon)",
         "d7_scorecard.json"),
        (0.76, "broadside guard unexercised\n(ON $\\equiv$ OFF, paired)",
         "cause: $\\hat\\sigma_i$ lags true broadside\n(0.106 vs 0.027 @ "
         "5000 N)", "remedy: lag-aware margin\n(design note, revision)",
         "d10c_guard.json"),
    ]
    for x, head, cause, fix, ev in cards:
        ax.add_patch(FancyBboxPatch((x, 0.66), 0.225, 0.28,
                     boxstyle="round,pad=0.012", fc="#ffebee", ec=FAIL_C,
                     transform=ax.transAxes))
        ax.text(x + 0.112, 0.80, head, fontsize=6.0, ha="center", va="center",
                transform=ax.transAxes, color="#7f1d1d")
        ax.add_patch(FancyBboxPatch((x, 0.30), 0.225, 0.30,
                     boxstyle="round,pad=0.012", fc="#fff8e1", ec="#c9a227",
                     transform=ax.transAxes))
        ax.text(x + 0.112, 0.45, cause, fontsize=5.8, ha="center", va="center",
                transform=ax.transAxes, color="#5d4037")
        ax.add_patch(FancyBboxPatch((x, 0.02), 0.225, 0.22,
                     boxstyle="round,pad=0.012", fc="#e8f5e9", ec=PASS_C,
                     transform=ax.transAxes))
        ax.text(x + 0.112, 0.13, fix, fontsize=5.8, ha="center", va="center",
                transform=ax.transAxes, color="#1b5e20")
        for y0, y1 in ((0.66, 0.60), (0.30, 0.24)):
            ax.annotate("", xy=(x + 0.112, y1), xytext=(x + 0.112, y0),
                        xycoords=ax.transAxes,
                        arrowprops=dict(arrowstyle="-|>", color="#607d8b"))
        ax.text(x + 0.112, 0.965, ev, fontsize=5.4, ha="center",
                transform=ax.transAxes, color="#607d8b", style="italic")
    save(fig, "ral_failure_taxonomy")


if __name__ == "__main__":
    fig_scenario()
    fig_architecture()
    fig_hero_series()
    fig_agent_errors()
    fig_scorecard()
    fig_v2_seeds()
    fig_forest()
    fig_robustness()
    fig_taxonomy()
    print("all RA-L artifacts written to", OUT)
