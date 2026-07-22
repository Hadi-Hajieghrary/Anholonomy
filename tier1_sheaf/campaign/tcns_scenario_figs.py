"""T-CNS section VIII — 5 scenario / qualitative figures grounded in recorded
Tier-1 simulation, each built to be read at a glance (clear agent trails,
labelled events). Outputs -> tier1_sheaf/results/artifacts/.

T1 tcns_gauge_story    — E1: the three agents' load-pose ESTIMATES drift as a
                         rigid group off the truth, then snap to it when one
                         beacon pins the gauge. (agent trails + the two
                         different error curves.)
T2 tcns_contraction_portrait — E2: per-agent gauge-complement error trails
                         spiralling to zero under C5 vs K5 (faster where
                         kappa*lambda2 is larger).
T3 tcns_floor_dynamics — E3b: disagreement D(t) climbing to its steady state
                         D_ss for a sweep of staleness tau (CONJ regime).
T4 tcns_formation_gallery — E3a: 20 random taut formations, each a two-agent
                         tow geometry, all giving the same fitted slope.
T5 tcns_topology_gallery — E6: the four comms topologies with their algebraic
                         connectivity lambda2 and the measured floor.
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
OUT = os.path.join(RES, "artifacts")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "figure.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------
# T1 — the gauge phenomenon: estimates drift as a group, then a beacon pins.
# ---------------------------------------------------------------------------
def fig_gauge_story():
    from tier1_sheaf.experiments.anim_gauge import simulate
    tt, te, Dh, gh, ts, tb = simulate()
    ts = np.asarray(ts)
    N = len(te[0])
    kb = int(np.argmax(ts >= tb))
    truth = np.array([[T[0, 2], T[1, 2]] for T in tt])
    est = np.array([[[te[k][j][0, 2], te[k][j][1, 2]] for j in range(N)]
                    for k in range(len(ts))])
    cols = plt.cm.tab10(np.linspace(0, 0.3, N))
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.6, 3.6),
                               gridspec_kw={"width_ratios": [1.1, 1]})
    # (a) trails
    a.plot(truth[:, 0], truth[:, 1], "-", color="k", lw=2.4, label="load truth",
           zorder=5)
    a.plot(truth[0, 0], truth[0, 1], "ko", ms=6)
    for j in range(N):
        a.plot(est[:kb, j, 0], est[:kb, j, 1], "-", color=cols[j], lw=1.3,
               alpha=0.9)
        a.plot(est[kb:, j, 0], est[kb:, j, 1], "--", color=cols[j], lw=1.3)
        a.plot(est[kb, j, 0], est[kb, j, 1], "*", color=cols[j], ms=11,
               mec="k", zorder=6)
    a.plot([], [], "-", color="#607d8b", label="agent estimates (pre-beacon)")
    a.plot([], [], "--", color="#607d8b", label="post-beacon")
    a.plot([], [], "*", color="#607d8b", mec="k", ms=10, label="beacon instant")
    a.annotate("estimates drift\nas a rigid group\noff the truth",
               (est[kb // 2, 0, 0], est[kb // 2, 0, 1]),
               textcoords="offset points", xytext=(-6, 14), fontsize=7.5,
               color="#455a64", ha="right")
    a.set_aspect("equal"); a.set_xlabel("x"); a.set_ylabel("y")
    a.set_title("(a) the gauge orbit: consensus without truth", fontsize=9)
    a.legend(fontsize=6.3, loc="best")
    # (b) two error curves
    b.semilogy(ts, np.maximum(gh, 1e-4), "-", color="#b2182b", lw=1.8,
               label="gauge error (agents vs truth)")
    b.semilogy(ts, np.maximum(Dh, 1e-4), "-", color="#1565c0", lw=1.8,
               label="disagreement $D$ (agents vs each other)")
    b.axvline(tb, color="#c9a227", ls="--", lw=1.4)
    b.annotate("beacon\n(Cor. 5.2)", (tb - 1.5, 4e-4), fontsize=7.5,
               color="#8d6e00", ha="right", va="bottom")
    b.set_xlabel("t (s)"); b.set_ylabel("error")
    b.set_ylim(1e-4, 30)
    b.set_title("(b) two different objects: the disagreement $D$ runs\n"
                "$\\sim$an order of magnitude below the gauge error;\n"
                "one beacon collapses both", fontsize=8.6)
    b.legend(fontsize=6.8, loc="lower left")
    fig.suptitle("E1 --- with no absolute anchor the estimates agree with each "
                 "other but drift together along the $SE(2)$ gauge; one beacon "
                 "collapses it (Thm. 5.1, Cor. 5.2)", fontsize=8.5, y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "tcns_gauge_story")


# ---------------------------------------------------------------------------
# T2 — contraction: gauge-complement error trails spiral to zero, C5 vs K5.
# ---------------------------------------------------------------------------
def fig_contraction_portrait():
    from tier1_sheaf.campaign.contraction_movie import data, SHAPES
    N = len(SHAPES)
    cols = plt.cm.tab10(np.linspace(0, 0.5, N))
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2),
                             gridspec_kw={"width_ratios": [1, 1, 1.05]})
    for ax, topo, ttl in [(axes[0], "cycle", "(a) $C_5$ cycle ($\\lambda_2$=1.38)"),
                          (axes[1], "complete", "(b) $K_5$ complete ($\\lambda_2$=5)")]:
        tt, comp, pn = data[topo]
        for j in range(N):
            ax.plot(comp[:, j, 0], comp[:, j, 1], "-", color=cols[j], lw=1.2,
                    alpha=0.85)
            ax.plot(comp[0, j, 0], comp[0, j, 1], "o", color=cols[j], ms=5)
        ax.plot(0, 0, "k+", ms=13, mew=2)
        ax.annotate("consensus\n(target)", (0, 0), textcoords="offset points",
                    xytext=(8, 8), fontsize=7, color="#455a64")
        ax.set_aspect("equal"); ax.set_xlim(-0.45, 0.45); ax.set_ylim(-0.45, 0.45)
        ax.set_title(ttl, fontsize=8.5)
        ax.set_xlabel("$e_{\\perp,x}$")
    axes[0].set_ylabel("$e_{\\perp,y}$")
    for topo, c in [("cycle", "#1565c0"), ("complete", "#e65100")]:
        tt, comp, pn = data[topo]
        axes[2].semilogy(tt, np.maximum(pn, 1e-9), "-", color=c, lw=2,
                         label=topo)
    axes[2].set_xlabel("t (s)"); axes[2].set_ylabel("$\\|e_\\perp\\|$")
    axes[2].set_title("(c) decay rate grows with\n$\\kappa\\lambda_2$ "
                      "(C6, slope 1.403)", fontsize=8.5)
    axes[2].legend(fontsize=7.5)
    fig.suptitle("E2 --- step-perturbed estimates: the gauge-complement error "
                 "spirals into consensus, faster on the more connected graph "
                 "(LTV/frozen; Thm. 6.3)", fontsize=8.5, y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "tcns_contraction_portrait")


# ---------------------------------------------------------------------------
# T3 — the floor's dynamics: D(t) climbing to D_ss across a tau sweep.
# ---------------------------------------------------------------------------
def fig_floor_dynamics():
    from tier1_sheaf.campaign import floor_protocol_movie as fpm
    taus = [0.1, 0.2, 0.4, 0.8]
    runs = {t: (fpm.runs[t] if t in fpm.runs else fpm.run_traced(t))
            for t in taus}
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(taus)))
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    Tend = None
    for t, c in zip(taus, cmap):
        rt, rD = runs[t][0], runs[t][1]
        Tend = rt[-1]
        ax.semilogy(rt, np.maximum(rD, 1e-6), "-", color=c, lw=1.6,
                    label=f"$\\tau={t}$")
        # steady-state marker
        dss = np.mean(rD[int(0.7 * len(rD)):])
        ax.plot(rt[-1], dss, "o", color=c, ms=5)
    ax.axvspan(0.7 * Tend, Tend, color="#eceff1", zorder=0)
    ax.annotate("evaluation\nwindow", (0.71 * Tend, 4e-6), fontsize=7,
                color="#546e7a")
    ax.set_xlabel("t (s)"); ax.set_ylabel("disagreement $D(t)$")
    ax.set_ylim(1e-6, 1.0)
    ax.set_title("E3b --- $D(t)$ climbs to its steady state $D_{ss}$, higher\n"
                 "for larger staleness. $D_{ss}$ is measured [CONJ regime] ---\n"
                 "not a test of Thm. 7.2 (whose object is the amplitude)",
                 fontsize=8.2)
    ax.legend(fontsize=7.5, loc="lower right", ncol=2)
    save(fig, "tcns_floor_dynamics")


# ---------------------------------------------------------------------------
# T4 — formation gallery: 20 random taut formations, one fitted slope.
# ---------------------------------------------------------------------------
def fig_formation_gallery():
    from tier1_sheaf.campaign.formation_sweep_movie import forms, slopes
    fig, axes = plt.subplots(4, 5, figsize=(8.6, 6.2))
    for idx, ax in enumerate(axes.ravel()):
        si, sj = forms[idx]
        ax.add_patch(FancyBboxPatch((-0.34, -0.24), 0.68, 0.48,
                     boxstyle="round,pad=0.04", fc="#37474f", ec="k", zorder=3))
        for (sig, sgi), col in [(si, "#1565c0"), (sj, "#b71c1c")]:
            att = np.array([np.cos(sig), np.sin(sig)]) * 0.42
            tip = np.array([np.cos(sig), np.sin(sig)]) * 1.7
            ax.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63",
                    lw=1.1)
            hd = sig - sgi
            tri = np.array([[0.24, 0], [-0.15, 0.12], [-0.15, -0.12]])
            c, s = np.cos(hd), np.sin(hd)
            ax.add_patch(Polygon(tri @ np.array([[c, -s], [s, c]]).T + tip,
                         closed=True, fc=col, ec="k", zorder=4))
        ax.set_xlim(-2.1, 2.1); ax.set_ylim(-2.1, 2.1)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"slope {slopes[idx]:.4f}", fontsize=7)
    fig.suptitle("E3a --- 20 random taut two-agent formations (geometry varies "
                 "widely); every one fits the same order to 4 decimals: "
                 f"{np.mean(slopes):.4f} $\\pm$ {np.std(slopes):.0e}. "
                 "The $\\tau^2$ law is a structural constant.", fontsize=9,
                 y=1.005)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "tcns_formation_gallery")


# ---------------------------------------------------------------------------
# T5 — topology gallery: the four comms graphs, lambda2 and the floor.
# ---------------------------------------------------------------------------
def fig_topology_gallery():
    d = json.load(open(os.path.join(RES, "e6_topology.json")))
    N = 6
    topos = [("cycle", "$C_6$ cycle"), ("path", "$P_6$ path"),
             ("star", "$S_6$ star"), ("complete", "$K_6$ complete")]

    def edges(topo, N):
        if topo == "cycle":
            return [(i, (i + 1) % N) for i in range(N)]
        if topo == "path":
            return [(i, i + 1) for i in range(N - 1)]
        if topo == "star":
            return [(0, i) for i in range(1, N)]
        return [(i, j) for i in range(N) for j in range(i + 1, N)]

    fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9))
    ang = np.linspace(0, 2 * np.pi, N, endpoint=False) + np.pi / 2
    pos = np.stack([np.cos(ang), np.sin(ang)], 1)
    for ax, (topo, ttl) in zip(axes, topos):
        rec = d[f"{topo}_{N}"]
        for i, j in edges(topo, N):
            ax.plot([pos[i, 0], pos[j, 0]], [pos[i, 1], pos[j, 1]], "-",
                    color="#1565c0", lw=1.3, alpha=0.7, zorder=2)
        for k in range(N):
            ax.add_patch(Circle(pos[k], 0.17, fc=plt.cm.tab10(k / 10), ec="k",
                         zorder=4))
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-2.1, 1.6)
        ax.set_title(f"{ttl}\n$\\lambda_2$={rec['lambda2']:.2f}", fontsize=8.5)
        ax.text(0, -1.75, f"floor $D_{{ss}}$: {rec['D02']:.3f} @ $\\tau$=0.2\n"
                f"{rec['D08']:.3f} @ $\\tau$=0.8", ha="center", fontsize=6.8,
                color="#455a64")
    fig.suptitle("E6 (exploratory) --- more connectivity (higher $\\lambda_2$) "
                 "suppresses the floor at moderate staleness; the benefit "
                 "collapses at high staleness", fontsize=8.8, y=1.04)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "tcns_topology_gallery")


if __name__ == "__main__":
    fig_gauge_story()
    fig_contraction_portrait()
    fig_floor_dynamics()
    fig_formation_gallery()
    fig_topology_gallery()
    print("T-CNS scenario figures done")
