"""L-CSS letter figures --- ONE plot per figure, IEEE journal style.

Every figure is a single axes at IEEE single-column width (3.5 in), Times-metric
serif, 8 pt, vector PDF with embedded fonts, grayscale-safe. Data is the same
committed campaign record used elsewhere; importing paper_artifacts replays the
e3a_extension draw sequence and ASSERTS it against the JSON, so slopes/sups/
pair_bank cannot drift.

Outputs -> tier1_sheaf/results/artifacts/ieee/lcss_*.{pdf,png}
"""
import sys, os, json, csv
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from scipy.linalg import expm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle

from analysis.ieee_style import apply_ieee, COLW, cyc, color, save
apply_ieee()

from tier1_sheaf.core.shapes import conjugated_generator
from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                        holonomy_amplitude_m2)
from tier1_sheaf.campaign.level_set_movie import loop_path, frame_pts, GEN, LVL
from tier1_sheaf.campaign import floor_protocol_movie as fpm
# replay-asserted arrays (20 slopes, 220 sups, 60-pair bank, ext JSON)
from tier1_sheaf.campaign.paper_artifacts import slopes, sups, pair_bank, ext

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
OUT = os.path.join(RES, "artifacts", "ieee")
os.makedirs(OUT, exist_ok=True)
XI = np.array([0.4, 0.0, 0.12])
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])


def F(name, w=COLW, h=None):
    return plt.subplots(figsize=(w, h or w * 0.75))


def out(fig, name):
    save(fig, os.path.join(OUT, name))
    print("wrote", name)


# 1 ---- tow geometry (single diagram) --------------------------------------
def fig_geometry():
    tt, D_tr, G_tr, s_tr = fpm.runs[0.4]
    N = s_tr.shape[1]
    k0 = int(0.45 * len(tt))
    sig, sigi = s_tr[k0, :, 0], s_tr[k0, :, 1]
    fig, ax = F("geom", h=COLW * 0.95)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyBboxPatch((-0.9, -0.6), 1.8, 1.2, boxstyle="round,pad=0.1",
                 fc="#37474f", ec="k", zorder=3))
    ax.text(0, 0, "load $G$", color="w", ha="center", va="center", fontsize=7)
    ax.annotate("", xy=(2.4, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=0.9))
    ax.annotate("", xy=(0, 2.0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=0.9))
    ax.text(2.45, -0.15, "$x_L$", fontsize=8); ax.text(0.1, 2.0, "$y_L$", fontsize=8)
    for j in range(N):
        tip = np.array([np.cos(sig[j]), np.sin(sig[j])]) * 4.0
        att = np.array([np.cos(sig[j]), np.sin(sig[j])]) * 0.95
        ax.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63", lw=1.0)
        hd = sig[j] - sigi[j]
        tri = np.array([[0.55, 0], [-0.35, 0.28], [-0.35, -0.28]])
        c, s = np.cos(hd), np.sin(hd)
        ax.add_patch(Polygon(tri @ np.array([[c, -s], [s, c]]).T + tip,
                     closed=True, fc=color(j), ec="k", lw=0.5, zorder=5))
        ax.text(tip[0] * 1.16, tip[1] * 1.16, f"{j+1}", fontsize=7, ha="center",
                va="center", color=color(j))
    j = int(np.argmax(sig)); ang = sig[j]
    ax.annotate("", xy=(1.6 * np.cos(ang), 1.6 * np.sin(ang)), xytext=(1.6, 0),
                arrowprops=dict(arrowstyle="-", color="#c62828", lw=0.8,
                                connectionstyle="arc3,rad=0.3"))
    ax.text(1.5 * np.cos(ang / 2) + 0.2, 1.5 * np.sin(ang / 2), "$\\sigma_j$",
            color="#c62828", fontsize=8)
    ax.set_xlim(-3.2, 6.0); ax.set_ylim(-3.6, 3.2)
    ax.set_title("Cooperative-tow geometry: each agent's shape "
                 "$s_j=(\\sigma_j,\\sigma_{i,j})$")
    out(fig, "lcss_geometry")


# 2 ---- shape-angle trajectories -------------------------------------------
def fig_shape_motion():
    tt, D_tr, G_tr, s_tr = fpm.runs[0.4]
    N = s_tr.shape[1]
    fig, ax = F("shape")
    sty = cyc()
    for j in range(N):
        ax.plot(tt, np.degrees(s_tr[:, j, 0]), **next(sty), markevery=400,
                label=f"agent {j+1}")
    ax.set_xlabel("$t$ (s)"); ax.set_ylabel("cable angle $\\sigma_j(t)$ (deg)")
    ax.set_title("The shape fan never stops moving (persistent turn)")
    ax.legend(ncol=2, fontsize=6)
    out(fig, "lcss_shape_motion")


# 3,4 ---- loop trails, generic and level-set -------------------------------
def _loop_trail(si, sj, tau, npts=60):
    Ci = conjugated_generator(*si, XI); Cj = conjugated_generator(*sj, XI)
    T = np.eye(3); xs, ys = [0.0], [0.0]
    for C, span in [(Ci, tau), (Cj, tau), (Ci, -tau), (Cj, -tau)]:
        for s in np.linspace(span / npts, span, npts):
            Ts = T @ expm(s * C); xs.append(Ts[0, 2]); ys.append(Ts[1, 2])
        T = T @ expm(span * C)
    return np.array(xs), np.array(ys)


def fig_loop(pair, name, title, levelset):
    fig, ax = F(name, h=COLW * 0.9)
    taus = [0.4, 0.8, 1.2, 1.6]
    cmap = plt.cm.viridis(np.linspace(0.15, 0.9, len(taus)))
    for tau, c in zip(taus, cmap):
        xs, ys = _loop_trail(*pair, tau)
        ax.plot(xs, ys, "-", color=c, lw=1.2, label=f"$\\tau={tau}$")
    ax.plot(0, 0, "ko", ms=4, zorder=6)
    ax.annotate("start", (0, 0), textcoords="offset points", xytext=(4, 4),
                fontsize=7)
    if not levelset:
        xs, ys = _loop_trail(*pair, taus[-1])
        ax.annotate("", xy=(xs[-1], ys[-1]), xytext=(0, 0), arrowprops=dict(
            arrowstyle="-|>", color="#c62828", lw=1.6))
        ax.plot(xs[-1], ys[-1], "o", color="#c62828", ms=5, zorder=6)
        ax.annotate("holonomy\ngap", (xs[-1], ys[-1]), textcoords="offset points",
                    xytext=(6, -2), fontsize=7, color="#c62828")
    else:
        ax.annotate("out along $C$, retraces\n$\\to$ closes for every $\\tau$\n"
                    "(gap $<10^{-15}$)", (0.04, 0.7), xycoords="axes fraction",
                    fontsize=7, color="#009E73")
    ax.set_aspect("equal")
    ax.set_xlabel("belief-frame $x$"); ax.set_ylabel("belief-frame $y$")
    ax.set_title(title); ax.legend(fontsize=6)
    out(fig, name)


# 5 ---- measured amplitude law + switch-offs -------------------------------
def fig_amplitude():
    rows = list(csv.reader(open(os.path.join(RES, "e3a_amplitude.csv"))))
    gen = np.array([float(x) for x in next(r for r in rows[1:]
                                           if r[0] == "generic")[2:8]])
    eta0 = np.array([float(x) for x in next(r for r in rows[1:]
                     if r[0].startswith("generic, eta=0"))[2:8]])
    fig, ax = F("amp")
    ax.loglog(TAUS, gen, "o-", color=color(0), ms=4, label="measured (slope 1.999)")
    ax.loglog(TAUS, gen[0] * (TAUS / TAUS[0]) ** 2, ":", color="k",
              label="$\\tau^2$ law")
    ax.loglog(TAUS, np.maximum(eta0, 1e-18), "s--", color=color(2), ms=3,
              label="switch-offs: machine zero")
    ax.set_ylim(1e-18, 3)
    ax.set_xlabel("staleness $\\tau$ (s)")
    ax.set_ylabel("$\\|\\log\\mathrm{Hol}\\|$")
    ax.set_title("Holonomy amplitude verified to coefficient precision")
    ax.legend(loc="lower right", fontsize=6.5)
    out(fig, "lcss_amplitude")


# 6 ---- amplitude carpet ----------------------------------------------------
def fig_carpet():
    s_i = np.array(ext["C15"][0]["shapes"][:2])
    partner = np.array(ext["C15"][0]["shapes"][2:])
    ray = (partner - s_i) / np.linalg.norm(partner - s_i)
    deltas = np.linspace(0.15, 2.4, 110); taus = np.geomspace(0.05, 1.6, 80)
    Z = np.array([[holonomy_amplitude_m2(tuple(s_i), tuple(s_i + d * ray), XI, t)
                   for d in deltas] for t in taus])
    fig, ax = F("carpet")
    pc = ax.pcolormesh(deltas, taus, np.log10(np.maximum(Z, 1e-18)),
                       cmap="magma", shading="auto", rasterized=True)
    ax.set_yscale("log")
    ax.axvline(np.linalg.norm(partner - s_i), color="#39d3c0", lw=1.2, ls="--")
    ax.annotate("level-set\nvalley", (np.linalg.norm(partner - s_i) + 0.06, 0.09),
                color="#39d3c0", fontsize=6.5)
    ax.set_xlabel("shape separation $\\Delta$ (rad)")
    ax.set_ylabel("staleness $\\tau$ (s)")
    ax.set_title("Floor grows as $\\tau^2$, collapses at the level set")
    cb = fig.colorbar(pc, ax=ax, shrink=0.9)
    cb.set_label("$\\log_{10}\\|\\log\\mathrm{Hol}\\|$", fontsize=7)
    out(fig, "lcss_carpet")


# 7 ---- 20-formation slope histogram ---------------------------------------
def fig_slope_hist():
    ref = 1.9992678569271
    fig, ax = F("slope")
    ax.hist((np.array(slopes) - ref) * 1e14, bins=10, color=color(0),
            edgecolor="k", lw=0.4)
    ax.set_xlabel("fitted slope $-$ 1.9992678569271  ($\\times10^{-14}$)")
    ax.set_ylabel("count (of 20 formations)")
    ax.set_title(f"Formation-invariant order: {np.mean(slopes):.6f}, "
                 f"support {max(slopes)-min(slopes):.0e}")
    out(fig, "lcss_slope_hist")


# 8 ---- remainder-constant CDF ---------------------------------------------
def fig_remainder_cdf():
    xs = np.sort(sups); ys = np.arange(1, len(xs) + 1) / len(xs)
    fig, ax = F("rem")
    ax.step(xs, ys, where="post", color=color(0))
    for v, lab in [(ext["remainder_constant"]["median"], "median"),
                   (ext["remainder_constant"]["p95"], "p95"),
                   (ext["remainder_constant"]["sup"], "sup")]:
        ax.axvline(v, color="0.5", lw=0.7, ls=":")
        ax.annotate(f"{lab}\n{v:.4f}", (v, 0.05), fontsize=6, rotation=90,
                    va="bottom", ha="right", color="0.35")
    ax.set_xlabel("$\\sup_\\tau\\|R\\|/\\tau^3$ per draw")
    ax.set_ylabel("empirical CDF (220 draws)")
    ax.set_title("Uniform $O(\\tau^3)$ remainder constant")
    out(fig, "lcss_remainder_cdf")


# 9 ---- coefficient ratio -> 1 ---------------------------------------------
def fig_bound_ratio():
    med, lo, hi = [], [], []
    for t in TAUS[:4]:
        r = [holonomy_amplitude_m2(si, sj, XI, t)
             / (t ** 2 * np.linalg.norm(two_agent_commutator(si, sj, XI)))
             for (si, sj) in pair_bank[:60]]
        med.append(np.median(r)); lo.append(np.percentile(r, 5))
        hi.append(np.percentile(r, 95))
    fig, ax = F("ratio")
    ax.fill_between(TAUS[:4], lo, hi, color=color(0), alpha=0.25,
                    label="5--95\\% band")
    ax.plot(TAUS[:4], med, "o-", color=color(0), ms=4, label="median")
    ax.axhline(1.0, color="k", lw=0.7, ls="--")
    ax.set_xscale("log"); ax.set_xticks(TAUS[:4])
    ax.set_xticklabels([f"{t:g}" for t in TAUS[:4]])
    ax.set_xlabel("staleness $\\tau$ (s)")
    ax.set_ylabel("measured / $\\tau^2\\|[C_i,C_j]\\|$")
    ax.set_title("Coefficient ratio $\\to 1$ as $\\tau\\to0$")
    ax.legend(fontsize=6.5)
    out(fig, "lcss_bound_ratio")


# 10 ---- C15 level-set bars ------------------------------------------------
def fig_levelset_bars():
    seps = [p["sep"] for p in ext["C15"]]
    comm = [max(p["comm"], 1e-19) for p in ext["C15"]]
    dC = []
    for p in ext["C15"]:
        Ci = conjugated_generator(p["shapes"][0], p["shapes"][1], XI)
        Cj = conjugated_generator(p["shapes"][2], p["shapes"][3], XI)
        dC.append(max(np.linalg.norm(Ci - Cj), 1e-19))
    x = np.arange(len(seps))
    fig, ax = F("c15")
    ax.bar(x - 0.19, comm, 0.38, color=color(0), label="$\\|[C_i,C_j]\\|$")
    ax.bar(x + 0.19, dC, 0.38, color=color(2), hatch="//",
           label="$\\|C_i-C_j\\|$")
    ax.set_yscale("log"); ax.set_ylim(1e-19, 1e-12)
    ax.axhline(1e-15, color="0.5", lw=0.7, ls=":")
    ax.annotate("machine precision", (0.0, 1.6e-15), fontsize=6, color="0.35")
    ax.set_xticks(x); ax.set_xticklabels([f"{s:.2f}" for s in seps])
    ax.set_xlabel("pair shape separation (rad, all $\\geq1$)")
    ax.set_ylabel("norm")
    ax.set_title("C15: zero-commutator pairs have $C_i=C_j$")
    ax.legend(fontsize=6.5)
    out(fig, "lcss_levelset_bars")


# 11 ---- commutator heatmap (single) ---------------------------------------
def fig_heatmap():
    s_ref = tuple(ext["C15"][0]["shapes"][:2])
    partner = tuple(ext["C15"][0]["shapes"][2:])
    Cr = conjugated_generator(*s_ref, XI)
    n = 201; sig = np.linspace(-np.pi, np.pi, n)
    Z = np.zeros((n, n))
    for a, x in enumerate(sig):
        for b, y in enumerate(sig):
            C = conjugated_generator(x, y, XI)
            Z[b, a] = np.linalg.norm(Cr @ C - C @ Cr)
    fig, ax = F("heat")
    pc = ax.pcolormesh(sig, sig, np.log10(np.maximum(Z, 1e-17)), cmap="viridis",
                       shading="auto", rasterized=True)
    ax.plot(*s_ref, "*", ms=9, color="w", mec="k", label="$s_{\\mathrm{ref}}$")
    ax.plot(*partner, "o", ms=6, mfc="none", mec="w", mew=1.4,
            label="level partner")
    ax.legend(fontsize=6, labelcolor="w", loc="upper left", framealpha=0.25)
    ax.set_xlabel("$\\sigma$"); ax.set_ylabel("$\\sigma_i$")
    ax.set_title("$\\log_{10}\\|[C(s_{\\mathrm{ref}}),C(s)]\\|$: two discrete zeros")
    cb = fig.colorbar(pc, ax=ax, shrink=0.9)
    out(fig, "lcss_heatmap")


# 12 ---- domain boundary ---------------------------------------------------
def fig_domain():
    si, sj = (0.55, 0.15), (-0.35, -0.7)
    K = np.linalg.norm(two_agent_commutator(si, sj, XI))
    ts = np.geomspace(0.05, 12.0, 60)
    amp = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in ts])
    rel = np.abs(amp - ts ** 2 * K) / (ts ** 2 * K)
    knee = float(ts[np.argmax(rel > 0.10)])
    fig, ax = F("dom")
    ax.loglog(ts, amp, "o-", color=color(0), ms=3, label="measured")
    ax.loglog(ts, ts ** 2 * K, "--", color="k", label="$\\tau^2$ law")
    ax.axvline(knee, color="#c62828", lw=0.9, ls=":")
    ax.annotate(f"10\\% departure\n$\\tau\\approx{knee:.0f}$", (knee * 0.42, amp[0] * 4),
                fontsize=6.5, color="#c62828")
    ax.set_xlabel("staleness $\\tau$ (s)")
    ax.set_ylabel("$\\|\\log\\mathrm{Hol}\\|$")
    ax.set_title("Leading-order domain: 10\\% departure only at $\\tau\\approx10$")
    ax.legend(loc="lower right", fontsize=6.5)
    out(fig, "lcss_domain")


if __name__ == "__main__":
    fig_geometry(); fig_shape_motion()
    fig_loop(GEN, "lcss_loop_generic",
             "Generic pair: the loop fails to close", False)
    fig_loop(LVL, "lcss_loop_levelset",
             "Level-set pair: the loop closes", True)
    fig_amplitude(); fig_carpet(); fig_slope_hist(); fig_remainder_cdf()
    fig_bound_ratio(); fig_levelset_bars(); fig_heatmap(); fig_domain()
    print("L-CSS IEEE single-plot figures done")
