"""RA-L Blind Harbor figures --- ONE plot per figure, IEEE journal style.
Single axes each, from committed records. Outputs -> results/s1/artifacts/ieee/.
"""
import sys, os, json, csv
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
from analysis.ieee_style import apply_ieee, COLW, DBLW, cyc, color, save
apply_ieee()

S1 = "/workspaces/Anholonomy/tier2_drake/results/s1"
OUT = os.path.join(S1, "artifacts", "ieee")
os.makedirs(OUT, exist_ok=True)
T1 = "/workspaces/Anholonomy/tier1_sheaf/results"
AC = [color(i) for i in range(5)]


def F(h=None):
    return plt.subplots(figsize=(COLW, h or COLW * 0.75))


def out(fig, n):
    save(fig, os.path.join(OUT, n)); print("wrote", n)


def _load(series="hero_dogleg_series.npz"):
    z = np.load(os.path.join(S1, series))
    tq = z["truth"]
    load = tq[:, 0:3]
    asv = np.stack([tq[:, 3 + 3 * i:6 + 3 * i] for i in range(5)], axis=1)
    return z["ts"], load, asv, z


def _barge(ax, pose, fc="#2b3550", z=4, alpha=1.0):
    x, y, th = pose; c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = np.array([[4, 0], [1.2, 3.8], [-3.6, 2.4], [-3.6, -2.4], [1.2, -3.8]])
    ax.add_patch(Polygon(pts @ R.T + [x, y], closed=True, fc=fc, ec="k",
                         lw=0.8, zorder=z, alpha=alpha))


def _vessel(ax, pose, cc, z=5):
    x, y, th = pose; c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = np.array([[3.4, 0], [-2.2, 1.6], [-2.2, -1.6]])
    ax.add_patch(Polygon(pts @ R.T + [x, y], closed=True, fc=cc, ec="k",
                         lw=0.4, zorder=z))


# ---- scenario (map) + staleness ladder ------------------------------------
def fig_scenario():
    fig, ax = F(COLW * 0.8); ax.set_aspect("equal"); ax.axis("off")
    t1 = np.linspace(0, 60, 40); p1 = np.stack([t1, np.zeros_like(t1)], 1)
    th = np.linspace(0, np.pi / 3, 30); Rr = 18.0
    c0 = p1[-1] + [0, Rr]; arc = c0 + Rr * np.stack([np.sin(th), -np.cos(th)], 1)
    d2 = np.array([np.cos(np.pi / 3), np.sin(np.pi / 3)])
    p2 = arc[-1] + np.linspace(0, 38, 30)[:, None] * d2[None, :]
    path = np.vstack([p1, arc, p2])
    tang = np.gradient(path, axis=0); tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    for sgn in (1, -1):
        b = path + sgn * 14 * nrm; o = path + sgn * 22 * nrm
        ax.fill(np.r_[b[:, 0], o[::-1, 0]], np.r_[b[:, 1], o[::-1, 1]],
                color="#d7ccc8", lw=0)
    ax.plot(path[:, 0], path[:, 1], "--", color="#607d8b", lw=0.9)
    _barge(ax, [p1[22, 0], p1[22, 1], 0])
    for a in np.linspace(-0.55, 0.55, 5):
        tip = p1[22] + [np.cos(a) * 12, np.sin(a) * 12]
        ax.plot([p1[22, 0], tip[0]], [p1[22, 1], tip[1]], "-", color="#8d6e63", lw=0.7)
        ax.add_patch(Circle(tip, 1.2, fc=color(0), ec="k", lw=0.4))
    dock = p2[-1] + d2 * 4
    ax.add_patch(Circle(dock, 2.2, fc="#E69F00", ec="k"))
    ax.add_patch(Circle(dock, 24, fc="none", ec="#E69F00", ls=":", lw=1.0))
    ax.annotate("beacon\n(dock only)", dock + [-46, 4], fontsize=6, color="#8d6e00")
    ax.annotate("60$°$ dogleg", (arc[12, 0] + 4, arc[12, 1] - 9), fontsize=6,
                color="#607d8b")
    ax.set_xlim(-8, 120); ax.set_ylim(-30, 66)
    ax.set_title("The Blind Harbor Transit (GNSS-denied dogleg)")
    out(fig, "ral_scenario")


def fig_staleness():
    fig, ax = F(COLW * 0.55); ax.axis("off")
    rows = [("own odometry", "50 Hz", 0.82, color(0)),
            ("own cable direction", "20 Hz", 0.62, color(0)),
            ("neighbor estimates", "$\\tau$-stale 0.05--1.6 s", 0.42, color(1)),
            ("beacon (one agent)", "5 Hz, dock only", 0.22, "#E69F00")]
    for lab, rate, y, c in rows:
        ax.annotate(lab, (0.02, y), xycoords="axes fraction", fontsize=7.5)
        ax.annotate(rate, (0.6, y), xycoords="axes fraction", fontsize=7.5, color=c)
        ax.plot([0.02, 0.97], [y - 0.05, y - 0.05], "-", color="0.9", lw=0.6,
                transform=ax.transAxes)
    ax.set_title("Information staleness ladder")
    out(fig, "ral_staleness")


# ---- transit trajectory with barge snapshots (single axes) ----------------
def fig_transit():
    ts, load, asv, z = _load()
    fig, ax = F(COLW * 0.72)
    ax.plot(load[:, 0], load[:, 1], "-", color="#90a4ae", lw=1.0, zorder=1)
    for t in [0, 110, 225, 340, 445]:
        k = int(np.argmin(np.abs(ts - t)))
        _barge(ax, load[k], alpha=0.9)
        for i in range(5):
            ax.plot([load[k, 0], asv[k, i, 0]], [load[k, 1], asv[k, i, 1]], "-",
                    color="#8d6e63", lw=0.5, zorder=3)
            _vessel(ax, asv[k, i], AC[i])
        ax.annotate(f"{t:.0f}s", (load[k, 0], load[k, 1] + 12), fontsize=6,
                    ha="center", color="#455a64")
    ax.set_aspect("equal"); ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
    ax.set_title("Recorded transit: barge + 5 ASVs through the dogleg")
    out(fig, "ral_transit")


# ---- cable constraint ------------------------------------------------------
def fig_cables():
    ts, load, asv, z = _load()
    fig, ax = F(); sty = cyc()
    for i in range(5):
        d = np.hypot(asv[:, i, 0] - load[:, 0], asv[:, i, 1] - load[:, 1])
        ax.plot(ts, d, color=AC[i], lw=1.0, label=f"vessel {i+1}")
    ax.axvspan(200, 260, color="#ffe0b2", alpha=0.5)
    ax.axvline(410, color="#E69F00", ls=":", lw=0.8)
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("load-to-vessel distance (m)")
    ax.set_title("Cables stay taut through the transit (no slack)")
    ax.legend(fontsize=6, ncol=2)
    out(fig, "ral_cables")


# ---- hero series: truth traj + D/kern -------------------------------------
def fig_hero_traj():
    ts, load, asv, z = _load()
    fig, ax = F(COLW * 0.72)
    ax.plot(load[:, 0], load[:, 1], "-", color="k", lw=1.4, label="load truth")
    kt = (ts >= 200) & (ts <= 260)
    ax.plot(load[kt, 0], load[kt, 1], "-", color=color(1), lw=2.2, label="dogleg")
    kb = ts >= 410
    ax.plot(load[kb, 0], load[kb, 1], "-", color="#E69F00", lw=2.2, label="beacon window")
    ax.set_aspect("equal"); ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
    ax.set_title("Recorded 450\\,s transit (truth)")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "ral_hero_traj")


def fig_hero_D():
    ts, load, asv, z = _load()
    fig, ax = F()
    ax.semilogy(ts, np.maximum(z["D"], 1e-7), "-", color=color(0), label="disagreement $D$")
    ax.semilogy(ts, np.maximum(z["kern"], 1e-7), "--", color=color(3),
                label="gauge-kernel component")
    ax.axvspan(200, 260, color="#ffe0b2", alpha=0.5)
    ax.axvline(410, color="#E69F00", ls=":", lw=0.9)
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("value"); ax.set_ylim(1e-7, 60)
    ax.set_title("Maneuver excites $D$; beacon kills the gauge, not $D$")
    ax.legend(fontsize=6.5, loc="lower left")
    out(fig, "ral_hero_D")


# ---- gauge orbit: ghost trails + gauge error ------------------------------
def fig_gauge_trails():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, t_on = z["ts"], z["truth"], z["ghost_paper"], float(z["t_on"])
    load = tq[:, 0:3]; kb = int(np.argmin(np.abs(ts - t_on)))
    fig, ax = F(COLW * 0.78)
    ax.plot(load[:, 0], load[:, 1], "-", color="k", lw=1.4, label="load truth")
    for i in range(5):
        ax.plot(gp[i, :kb, 0], gp[i, :kb, 1], "-", color=AC[i], lw=0.8)
        ax.plot(gp[i, kb:, 0], gp[i, kb:, 1], "--", color=AC[i], lw=0.8)
    ax.plot([], [], "-", color="0.5", label="estimates (pre-beacon)")
    ax.plot([], [], "--", color="0.5", label="post-beacon")
    ax.set_aspect("equal"); ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
    ax.set_title("Ghost estimates drift as a group, collapse at beacon")
    ax.legend(fontsize=6, loc="best")
    out(fig, "ral_gauge_trails")


def fig_gauge_err():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, t_on = z["ts"], z["truth"], z["ghost_paper"], float(z["t_on"])
    load = tq[:, 0:3]
    err = np.hypot(gp[:, :, 0].mean(0) - load[:, 0], gp[:, :, 1].mean(0) - load[:, 1])
    fig, ax = F()
    ax.plot(ts, err, "-", color=color(1))
    ax.axvline(t_on, color="#E69F00", ls=":", lw=1.0)
    ax.annotate("beacon", (t_on - 6, err.max() * 0.6), fontsize=6.5, ha="right",
                color="#8d6e00")
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("fleet gauge error (m)")
    ax.set_title("Group drift grows under GNSS denial; one anchor kills it")
    out(fig, "ral_gauge_err")


# ---- agent errors ---------------------------------------------------------
def fig_agent_errors():
    z = np.load(os.path.join(S1, "hero_series.npz"))
    ts, errs = z["ts"], z["errs"]
    fig, ax = F()
    for i in range(errs.shape[1]):
        if i == 0:
            continue
        ax.semilogy(ts, np.maximum(errs[:, i], 1e-4), "-", color=AC[i], lw=0.8)
    ax.semilogy(ts, np.maximum(errs[:, 0], 1e-4), "-", color="#E69F00", lw=1.6,
                label="anchored agent 0")
    ax.axvline(30, color="#E69F00", ls=":", lw=0.9)
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("$\\|\\mathrm{Log}(\\hat G G^{-1})\\|$")
    ax.set_title("Per-agent error at the 130\\,s horizon: anchor propagates")
    ax.legend(fontsize=6.5)
    out(fig, "ral_agent_errors")


# ---- scorecard: box + CDF -------------------------------------------------
def _d7():
    return json.load(open(os.path.join(S1, "d7_scorecard.json")))


def fig_score_box():
    d = _d7(); arms = ["B1lim", "paper", "B2", "B0"]
    pm = {a: [r["pm"] for r in d if r["arm"] == a] for a in arms}
    fig, ax = F()
    bp = ax.boxplot([pm[a] for a in arms], tick_labels=["B1$^{lim}$", "paper", "B2", "B0"],
                    widths=0.5, patch_artist=True, showfliers=True)
    for p in bp["boxes"]:
        p.set_facecolor("#b3cde3")
    ax.set_yscale("log"); ax.set_ylabel("fleet-mean dock error (m)")
    ax.set_title("50 seeded transits per arm")
    out(fig, "ral_score_box")


def fig_score_cdf():
    d = _d7(); arms = [("B1lim", "B1$^{lim}$"), ("paper", "paper"),
                       ("B2", "B2"), ("B0", "B0")]
    fig, ax = F(); sty = cyc()
    for a, lab in arms:
        pm = np.sort([r["pm"] for r in d if r["arm"] == a]); s = next(sty)
        ax.step(pm, np.arange(1, len(pm) + 1) / len(pm), where="post",
                color=s["color"], ls=s["linestyle"], label=lab)
    ax.axvline(0.5, color="k", ls=":", lw=0.8)
    ax.annotate("0.5 m spec\n(0\\% all arms)", (0.53, 0.06), fontsize=6)
    ax.set_xscale("log"); ax.set_xlabel("fleet-mean dock error (m)")
    ax.set_ylabel("CDF over seeds")
    ax.set_title("Ordering holds seed-wise")
    ax.legend(fontsize=6, loc="upper left")
    out(fig, "ral_score_cdf")


def fig_v2seeds():
    v2 = json.load(open(os.path.join(S1, "hero_v2_ensemble.json")))
    order = np.argsort([r["pm"] for r in v2])
    pms = np.array([v2[i]["pm"] for i in order]); pas = np.array([v2[i]["pa"] for i in order])
    x = np.arange(len(v2))
    fig, ax = F()
    ax.bar(x - 0.2, pms, 0.4, color=color(0), label="fleet mean")
    ax.bar(x + 0.2, pas, 0.4, color="#E69F00", hatch="//", label="anchored agent")
    ax.axhline(0.5, color="k", ls=":", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels([v2[i]["seed"] for i in order], fontsize=6)
    ax.set_xlabel("seed (sorted by fleet mean)"); ax.set_ylabel("dock error (m)")
    ax.set_title(f"Hero v2: median {np.median(pms):.2f}\\,m, 17\\% under spec;\n"
                 "anchored agent gain-starved")
    ax.legend(fontsize=6.5)
    out(fig, "ral_v2seeds")


# ---- docking: zoom + CDF --------------------------------------------------
def fig_docking_zoom():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    tq, gp = z["truth"], z["ghost_paper"]; kd = len(z["ts"]) - 1
    dock = tq[kd, 0:2]; th = tq[kd, 2]
    fig, ax = F(COLW * 0.8)
    c, s = np.cos(th), np.sin(th); R = np.array([[c, -s], [s, c]])
    pts = np.array([[4, 0], [1.2, 3.8], [-3.6, 2.4], [-3.6, -2.4], [1.2, -3.8]])
    ax.add_patch(Polygon(pts @ R.T + dock, closed=True, fc="#2b355022",
                         ec="#2b3550", lw=1.2))
    ax.plot(*dock, "k+", ms=12, mew=1.8, label="truth barge centre")
    ax.add_patch(Circle(dock, 0.5, fc="none", ec=color(2), lw=1.6, ls="--"))
    ax.annotate("0.5 m spec", (dock[0] + 0.55, dock[1] + 0.55), fontsize=7, color=color(2))
    gm = gp[:, kd, :2].mean(0); err = np.hypot(gm[0] - dock[0], gm[1] - dock[1])
    ax.plot(*gm, "D", color=color(0), ms=9, mec="k", label="fleet estimate")
    ax.annotate("", xy=gm, xytext=dock, arrowprops=dict(arrowstyle="-|>", color=color(0), lw=1.4))
    ax.annotate(f"error {err:.2f} m", (dock[0] - 1.2, dock[1] - 1.8), fontsize=7.5, color=color(0))
    ax.set_xlim(dock[0] - 5, dock[0] + 5); ax.set_ylim(dock[1] - 5, dock[1] + 5)
    ax.set_aspect("equal"); ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
    ax.set_title("At the dock (5\\,m zoom): estimate vs truth")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "ral_docking_zoom")


def fig_docking_cdf():
    v2 = json.load(open(os.path.join(S1, "hero_v2_ensemble.json")))
    pm = np.sort([r["pm"] for r in v2])
    fig, ax = F()
    ax.step(pm, np.arange(1, len(pm) + 1) / len(pm), where="post", color=color(0))
    ax.axvline(0.5, color=color(2), ls="--", lw=1.0)
    ax.annotate("0.5 m spec", (0.52, 0.1), fontsize=7, color=color(2))
    ax.axvline(np.median(pm), color="0.5", ls=":", lw=0.9)
    ax.set_xlabel("fleet-mean dock error (m)"); ax.set_ylabel("CDF over seeds")
    ax.set_title(f"v2 improves docking but 83\\% miss spec (median {np.median(pm):.2f}\\,m)")
    out(fig, "ral_docking_cdf")


# ---- baseline divergence: tracks + error ----------------------------------
def fig_baseline_tracks():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    tq, gp, gb = z["truth"], z["ghost_paper"], z["ghost_b0"]; load = tq[:, 0:3]
    gpm = gp[:, :, :2].mean(0); gbm = gb[:, :, :2].mean(0)
    fig, ax = F(COLW * 0.78)
    ax.plot(load[:, 0], load[:, 1], "-", color="k", lw=1.6, label="load truth")
    ax.plot(gpm[:, 0], gpm[:, 1], "-", color=color(0), lw=1.2, label="DIEKF-$\\Sigma$")
    ax.plot(gbm[:, 0], gbm[:, 1], "--", color=color(1), lw=1.2, label="B0 dead-reckon")
    ax.set_aspect("equal"); ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
    ax.set_title("Fleet load-pose estimate tracks vs truth")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "ral_baseline_tracks")


def fig_baseline_err():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, gb = z["ts"], z["truth"], z["ghost_paper"], z["ghost_b0"]; load = tq[:, 0:3]
    ep = np.hypot(gp[:, :, 0].mean(0) - load[:, 0], gp[:, :, 1].mean(0) - load[:, 1])
    eb = np.hypot(gb[:, :, 0].mean(0) - load[:, 0], gb[:, :, 1].mean(0) - load[:, 1])
    fig, ax = F()
    ax.semilogy(ts, np.maximum(ep, 1e-2), "-", color=color(0), label="DIEKF-$\\Sigma$")
    ax.semilogy(ts, np.maximum(eb, 1e-2), "--", color=color(1), label="B0 dead-reckon")
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("fleet-mean load error (m)")
    ax.set_title("Sheaf fusion propagates the anchor; dead-reckoning diverges")
    ax.legend(fontsize=6.5, loc="lower left")
    out(fig, "ral_baseline_err")


# ---- robustness: drops + guard --------------------------------------------
def fig_robust_drops():
    d = json.load(open(os.path.join(S1, "d10b_loss.json")))
    fig, ax = F()
    for J, c, ls, lab in [(0, color(0), "-", "drops only"), (8, color(3), "--", "drops+jitter")]:
        ps, mean, sd = [], [], []
        for p in (0.0, 0.1, 0.3):
            v = [r["D"] for r in d if r["kind"] == "floor" and r["p"] == p and r["J"] == J]
            ps.append(p); mean.append(np.mean(v)); sd.append(np.std(v))
        ax.errorbar(ps, mean, yerr=sd, fmt="o", color=c, ls=ls, capsize=2, label=lab)
    ax.set_xlabel("packet-drop probability $p$"); ax.set_ylabel("floor $D_{ss}$")
    ax.set_title("D10(b): graceful (+13\\% @0.1, +45\\% @0.3);\nANEES in-gate (4.23, 130\\,s)")
    ax.legend(fontsize=6.5)
    out(fig, "ral_robust_drops")


def fig_robust_guard():
    g = json.load(open(os.path.join(S1, "d10c_guard.json")))["envelope_probe"]
    forces = sorted(g.keys(), key=float); x = np.arange(len(forces))
    fig, ax = F()
    ax.bar(x - 0.18, [g[f]["min_cos_sigma_i_true"] for f in forces], 0.36,
           color="#37474f", label="true min $\\cos\\sigma_i$")
    ax.bar(x + 0.18, [g[f]["min_cos_sigma_i_hat"] for f in forces], 0.36,
           color=color(1), hatch="//", label="estimated $\\hat\\sigma_i$")
    ax.set_xticks(x); ax.set_xticklabels([f"{float(f):.0f} N" for f in forces])
    ax.set_ylabel("closest broadside approach")
    ax.set_title("D10(c): $\\hat\\sigma_i$ lags true broadside --- guard\n"
                 "unexercised (ON $\\equiv$ OFF)")
    ax.legend(fontsize=6.5)
    out(fig, "ral_robust_guard")


# ---- cross-tier overlays --------------------------------------------------
def fig_f4a():
    rows = list(csv.reader(open(os.path.join(T1, "e3a_amplitude.csv"))))
    TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
    t1 = np.array([float(x) for x in next(r for r in rows[1:] if r[0] == "generic")[2:8]])
    d3 = json.load(open(os.path.join(S1, "d3_amplitude.json")))
    dt = np.array(d3["taus"]); dfan = np.array(d3["arms"]["fan"]["amp_mean"])
    fig, ax = F()
    ax.loglog(TAUS, t1, "o-", color=color(0), label="Tier-1 (slope 1.999)")
    ax.loglog(dt, dfan, "s--", color=color(1), label="Drake D3 (slope 2.000)")
    ax.loglog(TAUS, t1[0] * (TAUS / TAUS[0]) ** 2, ":", color="k", label="$\\tau^2$")
    ax.set_xlabel("$\\tau$ (s)"); ax.set_ylabel("holonomy amplitude")
    ax.set_title("F4a [PROV]: amplitude, both plants, slope 2, coeff 1.0000")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "ral_f4a")


def fig_f4b():
    runs = json.load(open(os.path.join(S1, "production_d2_d4_v2.json")))
    taus = sorted({r["tau"] for r in runs if r["kind"] == "d2"})
    med = [np.median([r["D"] for r in runs if r["kind"] == "d2" and abs(r["tau"] - t) < 1e-9])
           for t in taus]
    e3b = json.load(open(os.path.join(T1, "e3b_production.json")))
    t1t = [0.1, 0.2, 0.4, 0.8]
    t1m = [np.median([r["D"] for r in e3b if r["arm"] == "paper" and abs(r["tau"] - t) < 1e-9])
           for t in t1t]
    fig, ax = F()
    ax.loglog(t1t, t1m, "o-", color=color(0), label="Tier-1 (p=1.101)")
    ax.loglog(taus, med, "s--", color=color(1), label="Drake (p=1.077)")
    ax.loglog(taus, np.array(taus) ** 2 * (med[0] / taus[0] ** 2), ":", color="k",
              label="$\\tau^2$ (falsified)")
    ax.set_xlabel("$\\tau$ (s)"); ax.set_ylabel("$D_{ss}$")
    ax.set_title("F4b [CONJ]: floor slope $\\approx$1.1 both plants;\norder 2 excluded")
    ax.legend(fontsize=6.3, loc="upper left")
    out(fig, "ral_f4b")


def fig_f4c():
    runs = json.load(open(os.path.join(S1, "d2_a1_a2_arms.json")))
    taus = sorted({r["tau"] for r in runs})
    fig, ax = F()
    for arm, c, m, lab in [("A1", color(2), "^", "A1 (consensus)"),
                           ("A2", color(1), "s", "A2 (unconjugated)")]:
        med = [np.median([r["D"] for r in runs if r["kind"] == arm and abs(r["tau"] - t) < 1e-9])
               for t in taus]
        ax.loglog(taus, med, marker=m, color=c, label=lab)
    ax.set_xlabel("$\\tau$ (s)"); ax.set_ylabel("$D_{ss}$")
    ax.set_title("F4c: transport-rule ablation (A2 degrades $1.7$--$8.2\\times$)")
    ax.legend(fontsize=6.5, loc="upper left")
    out(fig, "ral_f4c")


def fig_cross_tier():
    rows = list(csv.reader(open(os.path.join(T1, "e3a_amplitude.csv"))))
    TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
    t1amp = np.array([float(x) for x in next(r for r in rows[1:] if r[0] == "generic")[2:8]])
    runs = json.load(open(os.path.join(S1, "production_d2_d4_v2.json")))
    taus = sorted({r["tau"] for r in runs if r["kind"] == "d2"})
    dss = [np.median([r["D"] for r in runs if r["kind"] == "d2" and abs(r["tau"] - t) < 1e-9])
           for t in taus]
    fig, ax = F(COLW * 0.85)
    ax.loglog(TAUS, t1amp, "o-", color=color(0), label="Tier-1 $\\|\\log\\mathrm{Hol}\\|$ (p=2, PROV)")
    ax.loglog(taus, dss, "s--", color=color(1), label="Drake $D_{ss}$ (p=1.08, CONJ)")
    ax.loglog(TAUS, t1amp[0] * (TAUS / TAUS[0]), ":", color=color(2),
              label="transport defect (p=1)")
    ax.set_xlabel("staleness $\\tau$ (s)"); ax.set_ylabel("amplitude")
    ax.set_title("The epistemic spine: three objects, three exponents")
    ax.legend(fontsize=6, loc="upper left")
    out(fig, "ral_cross_tier")


def fig_d9():
    d = json.load(open(os.path.join(S1, "d9_scaling.json")))
    lam = {"cycle": {3: 1.0, 4: 2.0, 6: 1.0}, "complete": {3: 3.0, 4: 4.0, 6: 6.0}}
    xs, pin, rel = [], [], []
    for r in d:
        L = lam.get(r["topo"], {}).get(r["N"])
        if L is None:
            continue
        xs.append(L); pin.append(r["pin"]); rel.append(r["relock"])
    fig, ax = F()
    ax.scatter(xs, pin, s=10, color=color(0), marker="o", label="pin rate ($\\rho{=}{+}0.04$)")
    ax.scatter(xs, rel, s=10, color=color(1), marker="s", label="re-lock ($\\rho{=}{-}0.51$)")
    ax.set_xlabel("algebraic connectivity $\\lambda_2$")
    ax.set_ylabel("rate (s$^{-1}$)")
    ax.set_title("D9: connectivity buys agreement, not anchoring")
    ax.legend(fontsize=6.5)
    out(fig, "ral_d9")


# ---- forest (single axes, from ledger) ------------------------------------
def fig_forest():
    PASS, FAIL, TRIP = "#009E73", "#c62828", "#D55E00"
    rows = [("D3 amplitude slope", None, 2.000, None, ("line", 2.0), "PASSED", PASS),
            ("D3 coefficient", None, 1.0000, None, ("band", (0.9, 1.1)), "PASSED", PASS),
            ("Cor 7.3 protection $\\times$", None, 31.0, None, ("none", None), "PASSED", PASS),
            ("C7b-Drake $D_{ss}$ $p$", 1.054, 1.077, 1.102, ("line", 2.0), "FALSIFIED", FAIL),
            ("\\S6 coef ratio", 3.97, 5.04, 6.19, ("band", (0.77, 1.3)), "DISAGREES", FAIL),
            ("\\S6 exponent diff", -0.012, 0.023, 0.057, ("band", (-0.2, 0.2)), "EQUIV", PASS),
            ("D9 pin $\\rho$", None, 0.04, None, ("line", 0.0), "FIRES", FAIL),
            ("D9 re-lock $\\rho$", -0.65, -0.51, -0.36, ("line", 0.0), "ANTI-ORDERS", TRIP)]
    fig, ax = plt.subplots(figsize=(DBLW, DBLW * 0.4))
    for k, (lab, lo, mid, hi, ref, v, c) in enumerate(rows):
        y = len(rows) - 1 - k; kind, rv = ref
        if kind == "line":
            ax.plot([rv, rv], [y - 0.3, y + 0.3], color="0.6", lw=0.7, ls="--")
        elif kind == "band":
            ax.fill_betweenx([y - 0.3, y + 0.3], rv[0], rv[1], color="0.85")
        if lo is not None:
            ax.plot([lo, hi], [y, y], color=c, lw=1.5)
            for e in (lo, hi):
                ax.plot([e, e], [y - 0.1, y + 0.1], color=c, lw=1.1)
        ax.plot(mid, y, "o", ms=4, color=c)
        ax.annotate(v, (6.5, y), fontsize=6, color=c, va="center")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=6)
    ax.axvline(0, color="0.8", lw=0.5)
    ax.set_xlim(-0.9, 9)
    ax.set_xlabel("estimate (mixed scales; exponents/ratios and correlations)")
    ax.set_title("Drake falsifier ledger, verdicts as adjudicated")
    out(fig, "ral_forest")


# ---- failure taxonomy (single diagram) ------------------------------------
def fig_taxonomy():
    fig, ax = plt.subplots(figsize=(DBLW, DBLW * 0.32)); ax.axis("off")
    cards = [(0.01, "docking spec unmet\n(0\\% $<$0.5 m)", "approach geometry", "decel approach"),
             (0.26, "anchored gain\nstarvation (11/12)", "covariance collapse", "cov. floor / adaptive $R$"),
             (0.51, "ANEES non-transfer\n(159--229 @450 s)", "bias RW $>$ $Q$", "horizon-scoped claims"),
             (0.76, "guard unexercised\n(ON $\\equiv$ OFF)", "$\\hat\\sigma_i$ lags", "lag-aware margin")]
    for x, head, cause, fix in cards:
        ax.add_patch(FancyBboxPatch((x, 0.62), 0.22, 0.3, boxstyle="round,pad=0.01",
                     fc="#fdecea", ec="#c62828", transform=ax.transAxes))
        ax.text(x + 0.11, 0.77, head, fontsize=6, ha="center", va="center",
                transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((x, 0.34), 0.22, 0.22, boxstyle="round,pad=0.01",
                     fc="#fff8e1", ec="#E69F00", transform=ax.transAxes))
        ax.text(x + 0.11, 0.45, "cause:\n" + cause, fontsize=5.5, ha="center",
                va="center", transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((x, 0.04), 0.22, 0.24, boxstyle="round,pad=0.01",
                     fc="#e6f4ea", ec="#009E73", transform=ax.transAxes))
        ax.text(x + 0.11, 0.16, "remedy:\n" + fix, fontsize=5.5, ha="center",
                va="center", transform=ax.transAxes)
    ax.set_title("Failure/limit taxonomy: finding $\\to$ cause $\\to$ remedy")
    out(fig, "ral_taxonomy")


# ---- architecture (reuse tcns-style, wider) -------------------------------
def fig_arch():
    fig, ax = plt.subplots(figsize=(DBLW, DBLW * 0.4)); ax.axis("off")
    ax.fill_betweenx([0, 1], 0, 0.30, color="#efebe9", alpha=0.6)
    ax.text(0.15, 0.96, "PLANT (Drake)", ha="center", fontsize=6.5,
            color="#4e342e", transform=ax.transAxes)
    ax.text(0.66, 0.96, "ESTIMATOR (sensors only, linted)", ha="center",
            fontsize=6.5, color="#1b5e20", transform=ax.transAxes)
    boxes = [(0.01, 0.55, "barge + $N$ ASVs,\ncables, tension", "#d7ccc8"),
             (0.01, 0.15, "HydroDrag +\nThruster", "#d7ccc8"),
             (0.17, 0.37, "sensors:\nodom/dir/beacon", "#ffe0b2"),
             (0.34, 0.55, "InEKF propagate\n(slaved twist)", "#fff3e0"),
             (0.34, 0.15, "direction +\nbroadside guard", "#fff3e0"),
             (0.53, 0.37, "executed-composite\nfusion (frozen exact)", "#e8f5e9"),
             (0.72, 0.55, "comms\n(drops/jitter)", "#ede7f6"),
             (0.72, 0.15, "beacon (agent 0)", "#fce4ec"),
             (0.88, 0.37, "$\\hat G_i$, CI cov", "#eceff1")]
    for x, y, lab, fc in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 0.14, 0.22, boxstyle="round,pad=0.008",
                     fc=fc, ec="#455a64", transform=ax.transAxes))
        ax.text(x + 0.07, y + 0.11, lab, fontsize=5.3, ha="center", va="center",
                transform=ax.transAxes)
    ax.text(0.01, 0.02, "commands are truth-free; state reaches the estimator only "
            "through the sensor models (linted by class)", fontsize=5.5,
            color="#455a64", transform=ax.transAxes)
    out(fig, "ral_arch")


if __name__ == "__main__":
    for f in [fig_scenario, fig_staleness, fig_transit, fig_cables, fig_hero_traj,
              fig_hero_D, fig_gauge_trails, fig_gauge_err, fig_agent_errors,
              fig_score_box, fig_score_cdf, fig_v2seeds, fig_docking_zoom,
              fig_docking_cdf, fig_baseline_tracks, fig_baseline_err,
              fig_robust_drops, fig_robust_guard, fig_f4a, fig_f4b, fig_f4c,
              fig_cross_tier, fig_d9, fig_forest, fig_taxonomy, fig_arch]:
        try:
            f()
        except Exception as e:
            print("FAIL", f.__name__, repr(e)[:180])
    print("RA-L IEEE figures done")
