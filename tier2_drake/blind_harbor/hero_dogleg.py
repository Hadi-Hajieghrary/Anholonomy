"""Blind Harbor dogleg hero movie (plan §7 storyboard, v1).

Beats: INIT-1 | Leg 1 | THE TURN | Leg 2 | BEACON + DOCK.
Left: harbor chart (corridor from the transited track, truth caisson, five ghost
caissons in Okabe-Ito, cables, beacon ring). Right: (P1) disagreement E_F(t) with
the conjectured-floor band and the MANDATED hedge on the plot; (P3-lite) gauge
split — kernel-projected (common-mode) vs complement error. Bottom: beat ribbon.
Always-visible sim clock + compression badge.

v1 disclosed deltas: fixed tau = 0.31 s (no jitter/drops); beacon time-triggered
(stands in for the last-30 m rule); tension coloring and online lambda_2 panel
deferred to v2. Hero seed = ensemble median D_ss (hero_ensemble.json).
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation

import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv
from tier2_drake.harbor import pentagon_vertices, front_attachments
from tier2_drake.blind_harbor.s1 import CFG, build_s1
from tier2_drake.blind_harbor.lint import truth_isolation_lint
from pydrake.systems.analysis import Simulator

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "s1")
OKABE = ["#E69F00", "#56B4E9", "#009E73", "#CC79A7", "#D55E00"]

HERO_CFG = dict(CFG, Tend=450.0, tau=0.31, dogleg=(200.0, 60.0, np.pi / 3),
                t_on=410.0, eval_from=430.0)
BEATS = [(0, "INIT-1"), (10, "Leg 1"), (200, "THE TURN"), (260, "Leg 2"),
         (410, "BEACON"), (440, "DOCK")]


def _run(seed):
    diagram, plant, leaves, logs, starts, scen = build_s1(HERO_CFG, seed)
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
    ests = [logs[f"est_{i}"].FindLog(root).data().T for i in range(HERO_CFG["N"])]
    return ts, tq, ests, scen


def _series(ts, tq, ests, N):
    K = len(ts)
    D = np.zeros(K); kern = np.zeros(K); comp = np.zeros(K)
    for k in range(K):
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        e = np.array([Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true))
                      for i in range(N)])
        D[k] = np.mean([np.sum((e[i] - e[j]) ** 2)
                        for i in range(N) for j in range(i + 1, N)])
        kern[k] = np.linalg.norm(e.mean(axis=0))
        comp[k] = np.mean(np.linalg.norm(e - e.mean(axis=0), axis=1))
    return D, kern, comp


def _poly(x, y, th, verts):
    c, s = np.cos(th), np.sin(th)
    return (verts @ np.array([[c, -s], [s, c]]).T) + np.array([x, y])


def _asv(x, y, th, L=3.4, W=1.6):
    return _poly(x, y, th, np.array([[L*.6, 0], [-L*.4, W/2], [-L*.4, -W/2]]))


def _corridor(tq, half=13.0):
    """Offset walls of the transited track (smoothed load path)."""
    p = tq[::40, :2]
    d = np.gradient(p, axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], axis=1)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    return p + half * n, p - half * n


def main():
    ens = json.load(open(os.path.join(OUT, "hero_ensemble.json")))
    seed = ens["hero_seed"]
    print(f"hero seed {seed} (rule: {ens['rule']})")
    ts, tq, ests, scen = _run(seed)
    N = HERO_CFG["N"]
    verts = pentagon_vertices(scen.load_radius, scen.load_phase)
    attach_pts = [a[:2] for a in front_attachments(scen)[0]]
    D, kern, comp = _series(ts, tq, ests, N)
    np.savez(os.path.join(OUT, "hero_dogleg_series.npz"),
             ts=ts, D=D, kern=kern, comp=comp, truth=tq)
    wallA, wallB = _corridor(tq)
    # conjectured-floor band from THIS run's own leg-1 steady level to the turn peak
    leg1 = np.median(D[(ts > 100) & (ts < 190)])
    band = (leg1, leg1 * 25.0)

    stride = 3
    idx = np.arange(0, len(ts), stride)
    fig = plt.figure(figsize=(16, 9), dpi=100)
    gs = fig.add_gridspec(3, 5, height_ratios=[3.2, 1.6, 0.28], hspace=0.3,
                          wspace=0.55)
    axC = fig.add_subplot(gs[0:2, 0:3])
    axP1 = fig.add_subplot(gs[0, 3:5])
    axP3 = fig.add_subplot(gs[1, 3:5])
    axR = fig.add_subplot(gs[2, :])

    def draw(j):
        k = idx[j]; t = ts[k]
        for ax in (axC, axP1, axP3, axR):
            ax.clear()
        # ---- chart ----
        axC.plot(wallA[:, 0], wallA[:, 1], "-", color="#8d8577", lw=2.5)
        axC.plot(wallB[:, 0], wallB[:, 1], "-", color="#8d8577", lw=2.5)
        axC.plot(tq[:k, 0], tq[:k, 1], "-", color="#aab", lw=1.0, alpha=0.7)
        for i in range(N):
            G = ests[i][k][ec.SL_G].reshape(3, 3)
            gx, gy, gth = G[0, 2], G[1, 2], np.arctan2(G[1, 0], G[0, 0])
            P = _poly(gx, gy, gth, verts)
            axC.fill(P[:, 0], P[:, 1], color=OKABE[i], alpha=0.20)
            axC.plot(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], "--",
                     color=OKABE[i], lw=1.1)
        P = _poly(tq[k, 0], tq[k, 1], tq[k, 2], verts)
        axC.fill(P[:, 0], P[:, 1], color="#2b3550", alpha=0.9)
        c, s = np.cos(tq[k, 2]), np.sin(tq[k, 2])
        R = np.array([[c, -s], [s, c]])
        for i in range(N):
            ax_, ay_, ath = tq[k, 3+3*i], tq[k, 4+3*i], tq[k, 5+3*i]
            att = R @ attach_pts[i] + tq[k, :2]
            axC.plot([att[0], ax_], [att[1], ay_], "-", color="#777", lw=0.8)
            T = _asv(ax_, ay_, ath)
            axC.fill(T[:, 0], T[:, 1], color=OKABE[i], ec="#222", lw=0.6)
        if t >= HERO_CFG["t_on"]:
            bx, by = tq[k, 3], tq[k, 4]
            ph = (t * 0.8) % 1.0
            axC.add_patch(plt.Circle((bx, by), 2.5 + 7 * ph, fill=False,
                                     color="#c9a227", lw=1.8, alpha=0.9*(1-ph)))
            axC.plot([bx], [by], "*", color="#c9a227", ms=15, mec="#7a6210")
        cx, cy = tq[k, 0], tq[k, 1]
        axC.set_xlim(cx-45, cx+45); axC.set_ylim(cy-32, cy+32)
        axC.set_aspect("equal"); axC.set_xticks([]); axC.set_yticks([])
        beat = [b for b in BEATS if t >= b[0]][-1][1]
        cap = {"INIT-1": "calibration straight — the GNSS-denied clock starts at t=10 s",
               "Leg 1": "no GNSS, no relative-pose sensing: each vessel sees only its own\n"
                        "odometry and its own cable. Ghosts drift as ONE rigid gauge orbit (Thm 5.1)",
               "THE TURN": "shape motion × latency: disagreement blooms out of the noise\n"
                           "intercept — at frozen shapes the fusion is exact (executed null)",
               "Leg 2": "relaxation — the ghost cluster stays offset (the gauge is still free)",
               "BEACON": "docking beacon acquired — one anchor kills the gauge (Cor 5.2)",
               "DOCK": "docked GNSS-denied"}[beat]
        axC.set_title(f"Blind Harbor dogleg transit — {beat}", fontsize=13)
        axC.text(0.01, 0.02, cap, transform=axC.transAxes, fontsize=8.5,
                 bbox=dict(fc="white", alpha=0.85, ec="none"))
        axC.text(0.99, 0.97, f"t = {t:5.1f} s   ×9", transform=axC.transAxes,
                 ha="right", va="top", fontsize=11, family="monospace",
                 bbox=dict(fc="#2b3550", alpha=0.85, ec="none"), color="w")
        # ---- P1 ----
        axP1.axhspan(band[0], band[1], color="#b3452c", alpha=0.10)
        axP1.text(0.02, 0.96,
                  "conjectured stochastic steady-state floor\n(Thm 7.2 is leading-order and deterministic;\nthe steady-state floor is conjectured)",
                  transform=axP1.transAxes, fontsize=6.8, va="top", color="#8a3a26")
        axP1.semilogy(ts[:k+1], np.maximum(D[:k+1], 1e-8), color="#222", lw=1.4)
        axP1.axvline(HERO_CFG["t_on"], color="#c9a227", ls="--", lw=1)
        for tb, _ in BEATS[2:4]:
            axP1.axvline(tb, color="#999", ls=":", lw=0.8)
        axP1.set_xlim(0, HERO_CFG["Tend"]); axP1.set_ylim(1e-6, 10)
        axP1.set_ylabel(r"$E_F(t)$ disagreement", fontsize=9)
        axP1.grid(True, which="both", alpha=0.2)
        # ---- P3 ----
        axP3.semilogy(ts[:k+1], np.maximum(kern[:k+1], 1e-5), color="#1a6b8a",
                      lw=1.4, label="kernel-projected (gauge) error")
        axP3.semilogy(ts[:k+1], np.maximum(comp[:k+1], 1e-5), color="#5a5f2d",
                      lw=1.4, label="complement error (bounded)")
        axP3.axvline(HERO_CFG["t_on"], color="#c9a227", ls="--", lw=1)
        axP3.set_xlim(0, HERO_CFG["Tend"]); axP3.set_ylim(1e-4, 50)
        axP3.set_xlabel("t [s]", fontsize=9)
        axP3.legend(fontsize=7, loc="upper left")
        axP3.grid(True, which="both", alpha=0.2)
        # ---- ribbon ----
        axR.set_xlim(0, HERO_CFG["Tend"]); axR.set_ylim(0, 1)
        cols = ["#ccc", "#9fb0d8", "#b3452c", "#9fb0d8", "#c9a227", "#3f6b3a"]
        for (tb, name), col in zip(BEATS, cols):
            te = ([b[0] for b in BEATS] + [HERO_CFG["Tend"]])[BEATS.index((tb, name)) + 1]
            axR.axvspan(tb, te, color=col, alpha=0.5 if tb <= t else 0.15)
            axR.text((tb + te) / 2, 0.5, name, ha="center", va="center", fontsize=8)
        axR.axvline(t, color="k", lw=1.5)
        axR.set_yticks([]); axR.set_xticks([])
        # docking scorecard on the final beat
        if t >= 440:
            kf = k
            G_true = SE2(tq[kf, 2], tq[kf, 0:2])
            errs = [Log(ests[i][kf][ec.SL_G].reshape(3, 3) @ inv(G_true))
                    for i in range(N)]
            pa = np.linalg.norm(errs[0][:2])                 # anchored agent
            pm = float(np.mean([np.linalg.norm(e[:2]) for e in errs]))
            px = max(np.linalg.norm(e[:2]) for e in errs)
            ye = np.degrees(max(abs(e[2]) for e in errs))
            tick = lambda v, thr: '✓' if v < thr else '✗'
            axC.text(0.99, 0.02,
                     f"DOCKING SCORECARD (est. error, <0.5 m / <5°)\n"
                     f"anchored agent {pa:.2f} m {tick(pa, 0.5)}\n"
                     f"fleet mean     {pm:.2f} m {tick(pm, 0.5)}\n"
                     f"fleet max      {px:.2f} m {tick(px, 0.5)}  (diffusion-limited)\n"
                     f"heading (max)  {ye:.1f}°  {tick(ye, 5.0)}   cables taut ✓",
                     transform=axC.transAxes, fontsize=8.5, ha="right",
                     family="monospace",
                     bbox=dict(fc="#f6f4ee", ec="#3f6b3a", lw=1.5))
        return []

    ani = animation.FuncAnimation(fig, draw, frames=len(idx), blit=False)
    mp4 = os.path.join(OUT, "hero_dogleg.mp4")
    ani.save(mp4, writer=animation.FFMpegWriter(fps=30, bitrate=3500))
    print("wrote", mp4, f"({len(idx)} frames)")
    plt.close(fig)


if __name__ == "__main__":
    main()
