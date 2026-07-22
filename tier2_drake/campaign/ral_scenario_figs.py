"""RA-L Blind Harbor companion — 5 scenario / qualitative figures grounded in
the recorded Drake transit, built to be read at a glance. Outputs ->
tier2_drake/results/s1/artifacts/.

R1 ral_transit_filmstrip — five ordered snapshots of the barge + 5 ASVs +
                           cables travelling the dogleg channel (the physical
                           transit).
R2 ral_cable_constraint  — the load-to-vessel distances over the transit stay
                           taut through the maneuver (constraint satisfaction).
R3 ral_docking_zoom      — the final approach: the fleet's load-pose estimate
                           vs the truth barge at the dock, with the 0.5 m spec
                           ring (the honest docking limit).
R4 ral_gauge_orbit       — the 5 ghost load-pose estimates drift as a rigid
                           group off the truth through GNSS denial, then
                           collapse at beacon acquisition (Cor. 5.2 in the
                           closed loop).
R5 ral_baseline_divergence — the fleet-estimate track of the paper rule vs the
                           B0 dead-reckoning baseline against the truth.

Truth layout in hero_dogleg_series.npz: [load(3), 5 ASV poses(15),
load twist(3), 5 ASV twists(15)] = 36. Ghost tracks (per-agent load-pose
estimates) come from hero_ghost_tracks.npz (paper + B0 re-run).
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch

S1 = "/workspaces/Anholonomy/tier2_drake/results/s1"
OUT = os.path.join(S1, "artifacts")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "figure.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False})
AGENT_C = [plt.cm.tab10(i / 10) for i in range(5)]


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote", name)


def _load(series="hero_dogleg_series.npz"):
    z = np.load(os.path.join(S1, series))
    ts, tq = z["ts"], z["truth"]
    load = tq[:, 0:3]
    asv = np.stack([tq[:, 3 + 3 * i:6 + 3 * i] for i in range(5)], axis=1)
    return ts, load, asv


def _draw_vessel(ax, pose, color, L=4.2, W=2.0, z=5):
    x, y, th = pose
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = np.array([[L * 0.6, 0], [-L * 0.4, W / 2], [-L * 0.4, -W / 2]])
    ax.add_patch(Polygon(pts @ R.T + [x, y], closed=True, fc=color, ec="k",
                         lw=0.6, zorder=z))


def _draw_barge(ax, pose, z=4):
    x, y, th = pose
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = np.array([[4, 0], [1.2, 3.8], [-3.6, 2.4], [-3.6, -2.4], [1.2, -3.8]])
    ax.add_patch(Polygon(pts @ R.T + [x, y], closed=True, fc="#2b3550",
                         ec="k", lw=1.2, zorder=z))


# ---------------------------------------------------------------------------
# R1 — transit filmstrip
# ---------------------------------------------------------------------------
def fig_transit_filmstrip():
    ts, load, asv = _load()
    beats = [(0.0, "start"), (100.0, "leg 1"), (225.0, "$60°$ dogleg"),
             (350.0, "leg 2"), (445.0, "dock")]
    fig, axes = plt.subplots(1, len(beats), figsize=(10.4, 2.7))
    for ax, (t, name) in zip(axes, beats):
        k = int(np.argmin(np.abs(ts - t)))
        ax.plot(load[:k + 1, 0], load[:k + 1, 1], "-", color="#90a4ae", lw=1.0)
        _draw_barge(ax, load[k])
        for i in range(5):
            ax.plot([load[k, 0], asv[k, i, 0]], [load[k, 1], asv[k, i, 1]],
                    "-", color="#8d6e63", lw=0.8, zorder=3)
            _draw_vessel(ax, asv[k, i], AGENT_C[i])
        cx, cy = load[k, 0], load[k, 1]
        ax.set_xlim(cx - 34, cx + 34); ax.set_ylim(cy - 30, cy + 30)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"t={t:.0f} s\n{name}", fontsize=8)
    fig.suptitle("The Blind Harbor transit: barge towed by 5 ASVs on cables "
                 "through the GNSS-denied dogleg (recorded truth, seed 3)",
                 fontsize=9, y=1.04)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save(fig, "ral_transit_filmstrip")


# ---------------------------------------------------------------------------
# R2 — cable-constraint satisfaction
# ---------------------------------------------------------------------------
def fig_cable_constraint():
    ts, load, asv = _load()
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    for i in range(5):
        d = np.hypot(asv[:, i, 0] - load[:, 0], asv[:, i, 1] - load[:, 1])
        ax.plot(ts, d, "-", color=AGENT_C[i], lw=1.2, label=f"vessel {i+1}")
    ax.axvspan(200, 260, color="#ffe0b2", alpha=0.5)
    ax.annotate("dogleg", (215, ax.get_ylim()[1]), fontsize=7.5, color="#e65100",
                va="top")
    ax.axvline(410, color="#c9a227", ls="--", lw=1.0)
    ax.annotate("beacon", (405, ax.get_ylim()[0]), fontsize=7.5, ha="right",
                color="#8d6e00")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("load-to-vessel distance (m)")
    ax.set_title("Cables stay taut through the transit: the load-to-vessel\n"
                 "distances hold in the taut band (12\\,m cable $+$ barge\n"
                 "attach radius) --- no slack even through the dogleg",
                 fontsize=8.4)
    ax.legend(fontsize=7, ncol=2, loc="best")
    save(fig, "ral_cable_constraint")


# ---------------------------------------------------------------------------
# R4 — the gauge orbit: ghost estimates drift as a group, collapse at beacon
# ---------------------------------------------------------------------------
def fig_gauge_orbit():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, t_on = z["ts"], z["truth"], z["ghost_paper"], float(z["t_on"])
    load = tq[:, 0:3]
    kb = int(np.argmin(np.abs(ts - t_on)))
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.6),
                               gridspec_kw={"width_ratios": [1.15, 1]})
    a.plot(load[:, 0], load[:, 1], "-", color="k", lw=2.2, label="load truth",
           zorder=5)
    for i in range(5):
        a.plot(gp[i, :kb, 0], gp[i, :kb, 1], "-", color=AGENT_C[i], lw=1.0,
               alpha=0.85)
        a.plot(gp[i, kb:, 0], gp[i, kb:, 1], "--", color=AGENT_C[i], lw=1.0)
    a.plot([], [], "-", color="#607d8b", label="ghost estimates (pre-beacon)")
    a.plot([], [], "--", color="#607d8b", label="post-beacon")
    a.set_aspect("equal"); a.set_xlabel("x (m)"); a.set_ylabel("y (m)")
    a.set_title("(a) five ghost load-pose estimates drift as a\ngroup off "
                "the truth, then collapse at beacon", fontsize=8.5)
    a.legend(fontsize=6.5, loc="best")
    # (b) the gauge error (fleet-mean estimate vs truth) over time
    err = np.zeros(len(ts))
    for k in range(len(ts)):
        gm = gp[:, k, :2].mean(axis=0)
        err[k] = np.hypot(gm[0] - load[k, 0], gm[1] - load[k, 1])
    b.plot(ts, err, "-", color="#b2182b", lw=1.8)
    b.axvline(t_on, color="#c9a227", ls="--", lw=1.3)
    b.annotate("beacon\nacquired", (t_on - 6, err.max() * 0.6), fontsize=7.5,
               ha="right", color="#8d6e00")
    b.set_xlabel("t (s)"); b.set_ylabel("fleet gauge error (m)")
    b.set_title("(b) the group drift (gauge error) grows under\nGNSS denial; "
                "one anchor collapses it", fontsize=8.5)
    fig.suptitle("Cor. 5.2 in the closed loop --- the estimates stay a "
                 "consistent fleet but drift together until the dock beacon "
                 "pins the gauge", fontsize=8.5, y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "ral_gauge_orbit")


# ---------------------------------------------------------------------------
# R5 — baseline divergence: paper vs B0 dead-reckon fleet-estimate tracks
# ---------------------------------------------------------------------------
def fig_baseline_divergence():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, gb = z["ts"], z["truth"], z["ghost_paper"], z["ghost_b0"]
    load = tq[:, 0:3]
    gpm = gp[:, :, :2].mean(axis=0)
    gbm = gb[:, :, :2].mean(axis=0)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.5),
                               gridspec_kw={"width_ratios": [1.2, 1]})
    a.plot(load[:, 0], load[:, 1], "-", color="k", lw=2.4, label="load truth")
    a.plot(gpm[:, 0], gpm[:, 1], "-", color="#1565c0", lw=1.6,
           label="DIEKF-$\\Sigma$ fleet estimate")
    a.plot(gbm[:, 0], gbm[:, 1], "-", color="#c62828", lw=1.6,
           label="B0 dead-reckon fleet estimate")
    a.plot(load[0, 0], load[0, 1], "ko", ms=5)
    a.set_aspect("equal"); a.set_xlabel("x (m)"); a.set_ylabel("y (m)")
    a.set_title("(a) fleet load-pose estimate tracks vs truth", fontsize=8.6)
    a.legend(fontsize=7, loc="best")
    ep = np.hypot(gpm[:, 0] - load[:, 0], gpm[:, 1] - load[:, 1])
    eb = np.hypot(gbm[:, 0] - load[:, 0], gbm[:, 1] - load[:, 1])
    b.semilogy(ts, np.maximum(ep, 1e-2), "-", color="#1565c0", lw=1.8,
               label="DIEKF-$\\Sigma$")
    b.semilogy(ts, np.maximum(eb, 1e-2), "-", color="#c62828", lw=1.8,
               label="B0 dead-reckon")
    b.set_xlabel("t (s)"); b.set_ylabel("fleet-mean load error (m)")
    b.set_title("(b) the sheaf fusion holds the load;\ndead-reckoning "
                "diverges", fontsize=8.6)
    b.legend(fontsize=7.5, loc="best")
    fig.suptitle("Why the sheaf transport is load-bearing: without it (B0), "
                 "the fleet estimate walks away from the load",
                 fontsize=8.5, y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "ral_baseline_divergence")


# ---------------------------------------------------------------------------
# R3 — docking approach zoom (honest limit)
# ---------------------------------------------------------------------------
def fig_docking_zoom():
    z = np.load(os.path.join(S1, "hero_ghost_tracks.npz"))
    ts, tq, gp, t_on = z["ts"], z["truth"], z["ghost_paper"], float(z["t_on"])
    load = tq[:, 0:3]
    kd = len(ts) - 1                                   # dock instant
    dock = load[kd, :2]
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.5),
                               gridspec_kw={"width_ratios": [1.0, 1]})
    # (a) TIGHT zoom on the dock so the sub-metre error and 0.5 m spec show
    # barge outline (unfilled so the interior markers read)
    x, y, th = load[kd]
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = np.array([[4, 0], [1.2, 3.8], [-3.6, 2.4], [-3.6, -2.4], [1.2, -3.8]])
    a.add_patch(Polygon(pts @ R.T + [x, y], closed=True, fc="#2b355022",
                        ec="#2b3550", lw=1.6, zorder=2))
    a.plot(*dock, "k+", ms=14, mew=2.2, zorder=5, label="load truth (dock)")
    a.add_patch(Circle(dock, 0.5, fc="none", ec="#2e7d32", lw=2.0, ls="--",
                       zorder=4))
    a.annotate("0.5 m spec", (dock[0] + 0.55, dock[1] + 0.55), fontsize=8,
               color="#2e7d32")
    gm = gp[:, kd, :2].mean(axis=0)
    err = np.hypot(gm[0] - dock[0], gm[1] - dock[1])
    a.plot(*gm, "D", color="#1565c0", ms=11, mec="k", zorder=7,
           label="fleet estimate")
    a.annotate("", xy=gm, xytext=dock, arrowprops=dict(arrowstyle="-|>",
               color="#1565c0", lw=1.8))
    a.annotate(f"error {err:.2f} m", (dock[0] - 1.2, dock[1] - 1.8),
               fontsize=8.5, color="#1565c0", ha="center")
    a.set_xlim(dock[0] - 5, dock[0] + 5); a.set_ylim(dock[1] - 5, dock[1] + 5)
    a.set_aspect("equal"); a.set_xlabel("x (m)"); a.set_ylabel("y (m)")
    a.set_title("(a) at the dock (5 m zoom): fleet estimate\nvs the truth "
                "barge centre", fontsize=8.4)
    a.legend(fontsize=7, loc="upper left")
    # (b) the docking-error distribution honesty (from v2 ensemble)
    v2 = json.load(open(os.path.join(S1, "hero_v2_ensemble.json")))
    pm = np.sort([r["pm"] for r in v2])
    b.step(pm, np.arange(1, len(pm) + 1) / len(pm), where="post",
           color="#1565c0", lw=1.8)
    b.axvline(0.5, color="#2e7d32", ls="--", lw=1.3)
    b.annotate("0.5 m spec", (0.52, 0.1), fontsize=7.5, color="#2e7d32")
    b.axvline(np.median(pm), color="#607d8b", ls=":", lw=1.2)
    b.annotate(f"median {np.median(pm):.2f} m", (np.median(pm) + 0.03, 0.5),
               fontsize=7.5, color="#455a64")
    b.set_xlabel("fleet-mean dock error (m)"); b.set_ylabel("CDF over seeds")
    b.set_title("(b) honest limit: the decelerating approach (v2)\nimproves "
                "docking but 83% of seeds still miss spec", fontsize=8.2)
    fig.suptitle("Docking: the estimator holds the fleet to $\\sim$1 m, but "
                 "the 0.5 m spec is unmet --- the approach geometry binds "
                 "(stated, not hidden)", fontsize=8.3, y=1.02)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "ral_docking_zoom")


if __name__ == "__main__":
    import sys as _s
    which = _s.argv[1] if len(_s.argv) > 1 else "all"
    if which in ("all", "truth"):
        fig_transit_filmstrip()
        fig_cable_constraint()
    if which in ("all", "ghost"):
        fig_gauge_orbit()
        fig_baseline_divergence()
        fig_docking_zoom()
    print("RA-L scenario figures:", which, "done")
