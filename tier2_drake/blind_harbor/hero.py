"""Blind Harbor hero movie — the flagship demonstration artifact.

One N=5 pentagon tow, GNSS-denied, with the coordinated-turn maneuver:
  phase 1 (t < t_on):  dead-reckoning + cable fusion only — the gauge is free,
                       the fleet's shared estimate drifts coherently (Thm 5.1);
  phase 2 (t >= t_on): agent 0 acquires the docking beacon — Cor 5.2's single
                       anchor pins the gauge and the whole fleet converges
                       through fusion.

Renders:
  results/s1/hero_blind_harbor.mp4   (+ .gif preview)
  results/s1/hero_montage.png        three-phase still for the paper

Overlay semantics: each agent's ghost pentagon is drawn at its OWN estimate
Ghat_i of the load pose — spread of the ghosts IS the disagreement D(t); their
common offset from truth is the gauge error the beacon kills.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation

from tier2_drake.harbor import pentagon_vertices
from tier2_drake.blind_harbor.s1 import CFG, build_s1
from tier2_drake.blind_harbor.lint import truth_isolation_lint
from estimator_core import state as ec
from tier1_sheaf.core.se2 import Log
from pydrake.systems.analysis import Simulator

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "s1")

HERO_CFG = dict(CFG, tau=0.4, t_on=30.0, turn_bias=0.03, turn_amp=0.02)
SEED = 0

AGENT_C = ["#b3452c", "#1a6b8a", "#5a5f2d", "#8a5a1a", "#6b4a8a"]


def _run():
    diagram, plant, leaves, logs, starts, scen = build_s1(HERO_CFG, SEED)
    truth_isolation_lint(diagram, plant)
    ctx = diagram.CreateDefaultContext()
    pc = plant.GetMyMutableContextFromRoot(ctx)
    lj = plant.GetJointByName("load_joint")
    lj.set_translation(pc, [0.0, 0.0]); lj.set_rotation(pc, 0.0)
    for i in range(HERO_CFG["N"]):
        aj = plant.GetJointByName(f"asv_{i}_joint")
        x, y, yaw = starts[i]
        aj.set_translation(pc, [x, y]); aj.set_rotation(pc, yaw)
    sim = Simulator(diagram, ctx)
    sim.Initialize(); sim.AdvanceTo(HERO_CFG["Tend"])
    root = sim.get_context()
    ts = logs["truth"].FindLog(root).sample_times()
    tq = logs["truth"].FindLog(root).data().T
    ests = [logs[f"est_{i}"].FindLog(root).data().T
            for i in range(HERO_CFG["N"])]
    return ts, tq, ests, scen


def _ghost_pose(est_row):
    G = est_row[ec.SL_G].reshape(3, 3)
    return G[0, 2], G[1, 2], np.arctan2(G[1, 0], G[0, 0])


def _poly(x, y, th, verts):
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    return (verts @ R.T) + np.array([x, y])


def _asv_tri(x, y, th, L=3.4, W=1.6):
    pts = np.array([[L * 0.6, 0], [-L * 0.4, W / 2], [-L * 0.4, -W / 2]])
    return _poly(x, y, th, pts)


def _series(ts, tq, ests, N):
    """Per-agent pose error ||Log(Ghat G^-1)|| and pairwise disagreement D(t)."""
    from numpy.linalg import inv
    K = len(ts)
    errs = np.zeros((K, N))
    D = np.zeros(K)
    for k in range(K):
        c, s = np.cos(tq[k, 2]), np.sin(tq[k, 2])
        G_true = np.array([[c, -s, tq[k, 0]], [s, c, tq[k, 1]], [0, 0, 1]])
        e = []
        for i in range(N):
            Gh = ests[i][k][ec.SL_G].reshape(3, 3)
            e.append(Log(Gh @ inv(G_true)))
        e = np.array(e)
        errs[k] = np.linalg.norm(e, axis=1)
        D[k] = np.mean([np.sum((e[i] - e[j]) ** 2)
                        for i in range(N) for j in range(i + 1, N)])
    return errs, D


def _draw_scene(ax, k, ts, tq, ests, scen, verts, trail_upto=None):
    N = HERO_CFG["N"]
    t = ts[k]
    # load trail
    upto = trail_upto if trail_upto is not None else k
    ax.plot(tq[:upto, 0], tq[:upto, 1], "-", color="#99a", lw=1.0, alpha=0.6)
    # ghost pentagons (each agent's own estimate of the load pose)
    for i in range(N):
        gx, gy, gth = _ghost_pose(ests[i][k])
        P = _poly(gx, gy, gth, verts)
        ax.fill(P[:, 0], P[:, 1], color=AGENT_C[i], alpha=0.10)
        ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]],
                "--", color=AGENT_C[i], lw=1.1, alpha=0.85)
    # truth pentagon
    P = _poly(tq[k, 0], tq[k, 1], tq[k, 2], verts)
    ax.fill(P[:, 0], P[:, 1], color="#2b3550", alpha=0.85)
    ax.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]],
            "-", color="#151b30", lw=1.6)
    # ASVs + cables
    for i in range(N):
        ax_, ay_, ath = tq[k, 3 + 3 * i], tq[k, 4 + 3 * i], tq[k, 5 + 3 * i]
        c, s = np.cos(tq[k, 2]), np.sin(tq[k, 2])
        R = np.array([[c, -s], [s, c]])
        att = R @ scen._attach_pts[i] + tq[k, :2] if hasattr(scen, "_attach_pts") \
            else np.array([ax_, ay_])
        ax.plot([att[0], ax_], [att[1], ay_], "-", color="#777", lw=0.8)
        T = _asv_tri(ax_, ay_, ath)
        ax.fill(T[:, 0], T[:, 1], color=AGENT_C[i], alpha=0.95,
                ec="#222", lw=0.6)
    # beacon halo on agent 0 once acquired
    if t >= HERO_CFG["t_on"]:
        bx, by = tq[k, 3], tq[k, 4]
        ph = (t * 0.8) % 1.0
        ax.add_patch(plt.Circle((bx, by), 2.5 + 6.0 * ph, fill=False,
                                color="#c9a227", lw=1.6, alpha=0.9 * (1 - ph)))
        ax.plot([bx], [by], "*", color="#c9a227", ms=14, mec="#7a6210")


def main():
    os.makedirs(OUT, exist_ok=True)
    ts, tq, ests, scen = _run()
    N = HERO_CFG["N"]
    verts = pentagon_vertices(scen.load_radius, scen.load_phase)
    # cache attach points for cable drawing
    from tier2_drake.harbor import front_attachments
    scen._attach_pts = [a[:2] for a in front_attachments(scen)[0]]
    errs, D = _series(ts, tq, ests, N)
    np.savez(os.path.join(OUT, "hero_series.npz"),
             ts=ts, errs=errs, D=D, truth=tq)

    stride = 2                                   # ~10 Hz log -> 5 Hz of sim time
    idx = np.arange(0, len(ts), stride)

    fig = plt.figure(figsize=(9.2, 8.0), dpi=110)
    gs = fig.add_gridspec(2, 1, height_ratios=[2.6, 1.0], hspace=0.16)
    axS = fig.add_subplot(gs[0]); axM = fig.add_subplot(gs[1])

    def draw(j):
        k = idx[j]
        axS.clear(); axM.clear()
        t = ts[k]
        _draw_scene(axS, k, ts, tq, ests, scen, verts)
        cx, cy = tq[k, 0], tq[k, 1]
        axS.set_xlim(cx - 38, cx + 38); axS.set_ylim(cy - 26, cy + 26)
        axS.set_aspect("equal")
        axS.set_title("Blind Harbor — GNSS-denied 5-vessel pentagon tow "
                      "(coordinated turn)", fontsize=11)
        phase = ("dead-reckoning + cable fusion — gauge FREE, fleet drifts coherently"
                 if t < HERO_CFG["t_on"] else
                 "docking beacon on agent 0 — gauge PINNED, fleet converges (Cor 5.2)")
        axS.text(0.02, 0.02, f"t = {t:5.1f} s   {phase}",
                 transform=axS.transAxes, fontsize=9,
                 bbox=dict(fc="white", alpha=0.8, ec="none"))
        axS.set_xticks([]); axS.set_yticks([])
        # metrics strip
        for i in range(N):
            axM.semilogy(ts[:k + 1], np.maximum(errs[:k + 1, i], 1e-4),
                         color=AGENT_C[i], lw=1.0, alpha=0.9,
                         label=r"per-agent $\|\hat G_i \ominus G\|$" if i == 0 else None)
        axM.semilogy(ts[:k + 1], np.maximum(D[:k + 1], 1e-6), color="#222",
                     lw=1.6, label=r"disagreement $D(t)$")
        axM.axvline(HERO_CFG["t_on"], color="#c9a227", lw=1.2, ls="--")
        axM.text(HERO_CFG["t_on"] + 1, 6.0, "beacon on", color="#7a6210",
                 fontsize=8)
        axM.set_xlim(0, HERO_CFG["Tend"]); axM.set_ylim(1e-4, 20.0)
        axM.set_xlabel("t [s]", fontsize=9)
        axM.set_ylabel(r"$\|\mathrm{Log}(\hat G_i \ominus G)\|$", fontsize=9)
        axM.legend(fontsize=8, loc="upper right")
        axM.grid(True, which="both", alpha=0.25)
        return []

    ani = animation.FuncAnimation(fig, draw, frames=len(idx), blit=False)
    mp4 = os.path.join(OUT, "hero_blind_harbor.mp4")
    ani.save(mp4, writer=animation.FFMpegWriter(fps=24, bitrate=2400))
    print("wrote", mp4, f"({len(idx)} frames)")

    # gif preview (coarser)
    idx_g = np.arange(0, len(ts), stride * 4)
    ani2 = animation.FuncAnimation(
        fig, lambda j: draw(int(j * 4)), frames=len(idx_g), blit=False)
    gif = os.path.join(OUT, "hero_blind_harbor.gif")
    ani2.save(gif, writer=animation.PillowWriter(fps=10))
    print("wrote", gif)
    plt.close(fig)

    # three-phase montage still (paper figure)
    figM, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), dpi=150)
    picks = [np.searchsorted(ts, tt) for tt in (15.0, 45.0, 120.0)]
    labels = ["t = 15 s — gauge free: ghosts drift together",
              "t = 45 s — beacon pins agent 0; fleet converging",
              "t = 120 s — converged through the turn"]
    for ax, k, lab in zip(axes, picks, labels):
        _draw_scene(ax, k, ts, tq, ests, scen, verts)
        cx, cy = tq[k, 0], tq[k, 1]
        ax.set_xlim(cx - 34, cx + 34); ax.set_ylim(cy - 24, cy + 24)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(lab, fontsize=9.5)
    figM.suptitle("Blind Harbor: single-beacon gauge pinning of a "
                  "5-agent estimation sheaf", fontsize=12)
    figM.tight_layout()
    figM.savefig(os.path.join(OUT, "hero_montage.png"))
    print("wrote hero_montage.png")


if __name__ == "__main__":
    main()
