"""Animation of the gauge phenomenon (E1) — Thm 5.1 + Cor 5.2, made visual.

HONEST SCOPE: this animates the abstract 3-agent load-pose estimation, NOT the
Blind Harbor Transit (boats/barge/channel), which is Tier-2/RA-L and not built.
There is no harbor scene to show yet — only the estimation geometry.

What you see: the true load pose G(t) (black) moves along a gentle curve. Three
agents dead-reckon their own load-pose estimate from noisy odometry and fuse over
the sheaf. With NO absolute anchor, the three estimates stay clustered with each
other (consensus) but drift as a group OFF the truth — along the 3-dim SE(2) gauge
(Thm 5.1: observable exactly modulo one global gauge). At t_beacon a docking beacon
pins agent 0 to an absolute pose; the gauge collapses and all three snap to truth
(Cor 5.2). Right panel: disagreement D(t) (agents vs each other) stays low
throughout, while the gauge error (agents vs truth) is large pre-beacon and
collapses after — the two are different quantities, which is the whole point.
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from tier1_sheaf.core.se2 import Exp, Log, inv
from tier1_sheaf.core.shapes import m_of, Ad_m

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)


def simulate(seed=3, Tend=90.0, dt=0.05, Dc=0.1, tau=0.3, kappa=2.0, t_beacon_frac=0.6):
    rng = np.random.default_rng(seed)
    shapes = [(0.4, 0.3), (0.9, -0.5), (-0.7, 0.6)]
    edges = [(0, 1), (1, 2), (2, 0)]
    N = 3
    m = [m_of(*s) for s in shapes]
    Adm = [Ad_m(*s) for s in shapes]
    Admi = [np.linalg.inv(A) for A in Adm]
    bias = [np.array([rng.normal(0, 0.006), 0, rng.normal(0, 0.008)]) for _ in range(N)]
    sig = np.array([0.012, 0, 0.006])

    G = np.eye(3)
    Gh = [np.eye(3) for _ in range(N)]
    steps = int(Tend / dt)
    per = int(Dc / dt)
    lag = int(round(tau / Dc))
    t_beacon = t_beacon_frac * Tend
    buf = [[] for _ in range(N)]
    zeta_last = [np.zeros(3) for _ in range(N)]
    alpha = kappa * Dc

    traj_true, traj_est, D_hist, gauge_hist, ts = [], [], [], [], []
    for k in range(steps):
        t = k * dt
        xi = np.array([0.4, 0.0, 0.10 * np.sin(0.10 * t) + 0.04])
        G = G @ Exp(dt * xi)
        for j in range(N):
            zeta = Admi[j] @ xi
            zh = zeta + bias[j] + sig * rng.standard_normal(3)
            zeta_last[j] = zh
            Gh[j] = Gh[j] @ Exp(dt * (Adm[j] @ zh))
        if k % per == 0:
            for j in range(N):
                buf[j].append(Gh[j] @ m[j])
            idx = len(buf[0]) - 1 - lag
            if idx >= 0:
                for (a, b) in edges + [(b, a) for (a, b) in edges]:
                    Hst = buf[b][idx]
                    Tt = Hst @ Exp(tau * (Admi[b] @ (Adm[a] @ zeta_last[a])))
                    r = Log(inv(Gh[a]) @ (Tt @ inv(m[b])))
                    Gh[a] = Gh[a] @ Exp(alpha * r)
            if t >= t_beacon:                       # Cor 5.2: anchor agent 0 to truth
                Gh[0] = Gh[0] @ Exp(0.25 * Log(inv(Gh[0]) @ G))
        # record ~every 0.5 s for the animation
        if k % int(0.5 / dt) == 0:
            traj_true.append(G.copy())
            traj_est.append([g.copy() for g in Gh])
            D = np.mean([np.sum(Log(inv(Gh[i]) @ Gh[j]) ** 2) for (i, j) in edges])
            gerr = np.mean([np.sum(Log(Gh[j] @ inv(G)) ** 2) for j in range(N)])
            D_hist.append(D)
            gauge_hist.append(gerr)
            ts.append(t)
    return traj_true, traj_est, np.array(D_hist), np.array(gauge_hist), np.array(ts), t_beacon


def frame_pose(ax, Gm, color, label=None, sz=1.4, lw=2.0, alpha=1.0):
    x, y = Gm[0, 2], Gm[1, 2]
    th = np.arctan2(Gm[1, 0], Gm[0, 0])
    ax.plot([x], [y], "o", color=color, ms=6, alpha=alpha)
    ax.plot([x, x + sz * np.cos(th)], [y, y + sz * np.sin(th)], "-",
            color=color, lw=lw, alpha=alpha, label=label)


def main():
    tt, te, Dh, gh, ts, t_beacon = simulate()
    COL = ["#b2182b", "#1b7837", "#2166ac"]
    xs = [G[0, 2] for G in tt]
    ys = [G[1, 2] for G in tt]
    xmin, xmax = min(xs) - 3, max(xs) + 3
    ymin, ymax = min(ys) - 3, max(ys) + 3

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1.5, 1]})

    def draw(i):
        axL.clear(); axR.clear()
        axL.plot(xs[:i + 1], ys[:i + 1], "-", color="k", lw=1, alpha=0.4)
        frame_pose(axL, tt[i], "k", "true load pose", sz=1.8, lw=2.6)
        for j in range(3):
            frame_pose(axL, te[i][j], COL[j], f"agent {j} estimate")
        beacon_on = ts[i] >= t_beacon
        axL.set_xlim(xmin, xmax); axL.set_ylim(ymin, ymax); axL.set_aspect("equal")
        axL.set_title(f"t = {ts[i]:5.1f} s   " +
                      ("BEACON ON — gauge pinned (Cor 5.2)" if beacon_on else
                       "no anchor — estimates drift along the SE(2) gauge (Thm 5.1)"),
                      fontsize=9.5, color=("#1b7837" if beacon_on else "#b2182b"))
        axL.set_xlabel("x (m)"); axL.set_ylabel("y (m)")
        axL.legend(fontsize=7, loc="upper left"); axL.grid(alpha=0.2)

        axR.semilogy(ts[:i + 1], np.clip(gh[:i + 1], 1e-6, None), "-", color="#762a83",
                     lw=2, label="gauge error (agents vs truth)")
        axR.semilogy(ts[:i + 1], np.clip(Dh[:i + 1], 1e-6, None), "-", color="#f1a340",
                     lw=2, label="disagreement D (agents vs each other)")
        axR.axvline(t_beacon, ls=":", color="gray", lw=1)
        axR.text(t_beacon, axR.get_ylim()[1], " beacon", fontsize=7, va="top", color="gray")
        axR.set_xlim(ts[0], ts[-1]); axR.set_ylim(1e-6, 1e2)
        axR.set_xlabel("t (s)"); axR.set_title("two different quantities", fontsize=9.5)
        axR.legend(fontsize=7, loc="lower left"); axR.grid(alpha=0.2, which="both")
        fig.tight_layout()

    n = len(tt)
    anim = FuncAnimation(fig, draw, frames=n, interval=120)
    gif = os.path.join(OUT, "gauge_drift.gif")
    anim.save(gif, writer=PillowWriter(fps=8))
    print(f"wrote {gif}")
    try:
        mp4 = os.path.join(OUT, "gauge_drift.mp4")
        anim.save(mp4, writer=FFMpegWriter(fps=8, bitrate=1200))
        print(f"wrote {mp4}")
    except Exception as e:
        print(f"(mp4 skipped: {e})")
    print(f"pre-beacon gauge error ~{gh[:int(0.6*n)].mean():.2f}, "
          f"post-beacon ~{gh[int(0.75*n):].mean():.4f}; "
          f"D stays ~{Dh.mean():.3f} throughout")


if __name__ == "__main__":
    main()
