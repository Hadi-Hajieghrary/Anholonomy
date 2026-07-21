"""RA-L movie S4 — failure-case anatomy (honest): anchored-agent gain
starvation on the 520 s hero-v2 transit.

One seed (10 — the fleet-mean median representative of hero_v2_ensemble.json),
EXACT V2 config of tier2_drake/campaign/hero_v2_ensemble.py. Left: top-view
scene (barge, ASVs, dock, beacon ring). Right: per-agent load-pose error —
after beacon-on the UNANCHORED agents converge through fusion while the
anchored agent (gold) stays fleet-worst: long-horizon Kalman anchoring has
collapsed P until the beacon gain starves, while CI conservatism keeps the
others' gains healthy. The m_xi-trim hypothesis was tested and falsified
(freeze bit-identical); remedy class: covariance floor / adaptive beacon R
(revision item).

The run's series is persisted to error_anatomy_series.npz (recorded +
replayable). Regenerate with: python error_anatomy_movie.py
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Circle, Polygon

import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv
from tier2_drake.blind_harbor.s1 import CFG, run_seed

S1DIR = "/workspaces/Anholonomy/tier2_drake/results/s1"
SEED = 10
V2 = dict(CFG, Tend=520.0, tau=0.31, dogleg=(200.0, 60.0, np.pi / 3),
          t_on=410.0, eval_from=500.0, decel=(395.0, 20.0, 0.28),
          mxi_freeze=(390.0, 425.0))

NPZ = os.path.join(S1DIR, "error_anatomy_series.npz")
if os.path.exists(NPZ):
    z = np.load(NPZ)
    ts, tq, errs = z["ts"], z["truth"], z["errs"]
else:
    out = run_seed(V2, SEED)
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = V2["N"]
    errs = np.zeros((len(ts), N))
    for k in range(len(ts)):
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        for i in range(N):
            e = Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true))
            errs[k, i] = np.linalg.norm(e[:2])
    np.savez(NPZ, ts=ts, truth=tq, errs=errs, seed=SEED)
    print("recorded", NPZ)

N = V2["N"]
STRIDE = max(1, len(ts) // 520)              # ~520 frames
FRAMES = len(ts[::STRIDE])
dock = tq[-1, 0:2] + 8.0 * np.array([np.cos(tq[-1, 2]), np.sin(tq[-1, 2])])

fig = plt.figure(figsize=(11, 5.2), dpi=105)
aS = fig.add_subplot(1, 2, 1)
aE = fig.add_subplot(1, 2, 2)
AGENT_C = [plt.cm.tab10(i / 10) for i in range(N)]


def draw(f):
    k = min(f * STRIDE, len(ts) - 1)
    t = ts[k]
    aS.clear(); aE.clear()
    aS.plot(tq[:k + 1, 0], tq[:k + 1, 1], "-", color="#90a4ae", lw=1.0)
    th = tq[k, 2]
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    barge = np.array([[-4, -2.6], [4, -2.6], [4, 2.6], [-4, 2.6]]) @ R.T + tq[k, 0:2]
    aS.add_patch(Polygon(barge, closed=True, fc="#37474f", ec="k", zorder=4))
    for i in range(N):
        p = tq[k, 3 + 3 * i:5 + 3 * i]
        aS.plot([tq[k, 0], p[0]], [tq[k, 1], p[1]], "-", color="#8d6e63",
                lw=0.8, zorder=3)
        aS.add_patch(Circle(p, 1.3, fc=AGENT_C[i], ec="k", lw=0.6, zorder=5))
    aS.add_patch(Circle(dock, 2.5, fc="#c9a227", ec="k", zorder=4))
    aS.add_patch(Circle(dock, 30, fc="none", ec="#c9a227", ls=":", lw=1.0))
    phase = ("transit" if t < 200 else "60° dogleg" if t < 260 else
             "leg 2" if t < 395 else "decelerating approach (v2)" if t < 410
             else "beacon acquired — anchored agent 0 starving")
    aS.set_title(f"hero v2, seed {SEED} (fleet-mean median) — t={t:.0f} s\n"
                 f"{phase}", fontsize=9.5)
    aS.set_aspect("equal")
    aS.set_xlabel("x (m)"); aS.set_ylabel("y (m)")
    for i in range(N):
        kw = (dict(color="#c9a227", lw=2.2,
                   label="anchored agent 0 (beacon; gain-starved)")
              if i == 0 else dict(color=AGENT_C[i], lw=0.9, alpha=0.8))
        aE.semilogy(ts[:k + 1], np.maximum(errs[:k + 1, i], 5e-2), "-", **kw)
    aE.axvline(395, color="#607d8b", ls="--", lw=0.9)
    aE.annotate("decel", (392, 120), fontsize=7, color="#607d8b", ha="right")
    aE.axvline(410, color="#c9a227", ls="--", lw=0.9)
    aE.annotate("beacon", (414, 120), fontsize=7, color="#8d6e00")
    aE.axvspan(500, 520, color="#eceff1", zorder=0)
    aE.set_xlim(0, 520); aE.set_ylim(5e-2, 300)
    aE.set_xlabel("t (s)")
    aE.set_ylabel("load-pose position error (m)")
    aE.legend(fontsize=7, loc="lower left")
    aE.set_title("pre-beacon: agents drift TOGETHER (the gauge, not "
                 "disagreement);\npost-beacon: the anchored agent's collapsed "
                 "$P$ starves its gain — worst on this seed", fontsize=8.5)


ani = animation.FuncAnimation(fig, draw, frames=FRAMES, blit=False)
out = os.path.join(S1DIR, "error_anatomy.mp4")
ani.save(out, writer=animation.FFMpegWriter(fps=25, bitrate=1800))
print("wrote", out)
