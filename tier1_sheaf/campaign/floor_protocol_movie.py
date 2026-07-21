"""Floor-protocol movie (T-CNS M3): the E3b measurement protocol on the
reduced plant. Left: the tow executing the persistent-turn maneuver (load pose
track + the shape fan; shapes must keep moving — D2's premise). Right: the
disagreement D(t) for two staleness values reaching steady state, with the
evaluation window shaded.

EPISTEMIC CAPTION (carried into the paper): D_ss is the stochastic
steady-state object [CONJECTURAL regime] — this movie demonstrates the
measurement PROTOCOL; it does not test Thm 7.2 (whose object is the E3a
amplitude, noise-off).

Compact protocol loop mirroring experiments/e3b_floor.py (same plant, same
estimator calls, same paper fuse rule and DC=0.05 send grid; simplified
sensing cadence for the illustration — quantitative claims in the papers come
from e3b_production.json, never from this movie). Deterministic given SEED.
Regenerate with: python floor_protocol_movie.py
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation

import estimator_core as ec
from tier1_sheaf.core.se2 import Log, inv
from tier1_sheaf.experiments.e3b_floor import (DC, KAPPA_GAIN, draw_formation,
                                               ReducedConfig, ReducedPlant)
from tier2_drake.blind_harbor.sensors import KAPPA_DIR

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
SEED, FORM, TEND, DT, N = 0, 0, 120.0, 0.01, 5


def run_traced(tau):
    s0 = draw_formation(FORM, N)
    cfg = ReducedConfig(N=N, l=1.0, dt=DT, v_ref=0.8, noise_on=True,
                        eta_profile="persistent_turn")
    plant = ReducedPlant(cfg, s0, int(np.random.SeedSequence(
        [SEED, FORM, 3]).generate_state(1)[0] % (2 ** 31)))
    rng = np.random.default_rng(np.random.SeedSequence([SEED, FORM, 7]))
    sts = [ec.FilterState.initial(s0[j].copy(), 1.0) for j in range(N)]
    alpha = KAPPA_GAIN * DC
    lag = int(round(tau / DC))
    assert lag >= 1 and abs(lag * DC - tau) < 1e-9
    nbrs = [[(j - 1) % N, (j + 1) % N] for j in range(N)]
    ring = []
    k50, k20, kdc = int(round(0.02 / DT)), int(round(0.05 / DT)), int(round(DC / DT))
    zeta_meas = [np.zeros(3) for _ in range(N)]
    tt, D_tr, G_tr, s_tr = [], [], [], []
    for k in range(int(round(TEND / DT))):
        t = plant.t
        if k % k50 == 0:
            tw = plant.body_twists()
            for j in range(N):
                z = np.asarray(tw[j], dtype=float).copy()
                z[0] += rng.normal(0.0, 0.01 + 0.02 * abs(z[0]))
                z[1] += rng.normal(0.0, 0.01)
                z[2] += rng.normal(0.0, np.radians(0.2))
                zeta_meas[j] = z
        if k % kdc == 0:
            ring.append([(t, sts[j].G.copy(), sts[j].s.copy()) for j in range(N)])
            idx = len(ring) - 1 - lag
            if idx >= 0:
                for j in range(N):
                    for src in nbrs[j]:
                        stamp, G_nb, s_nb = ring[idx][src]
                        sts[j], _ = ec.fuse_with_rule(
                            "paper", sts[j], G_nb, s_nb, t - stamp,
                            zeta_meas[j], alpha, 1.0, src)
        if k % k50 == 0:
            for j in range(N):
                sts[j] = ec.propagate(sts[j], zeta_meas[j], 0.02,
                                      shape_motion_correction=False)
        if k % k20 == 0:
            for j in range(N):
                z = plant.s[j, 1] + rng.normal(0.0, 1.0 / np.sqrt(KAPPA_DIR))
                sts[j] = ec.update_direction(sts[j], z, KAPPA_DIR)
        plant.step()
        if k % kdc == 0:
            Gs = [sts[j].G for j in range(N)]
            D_tr.append(np.mean([np.sum(Log(inv(Gs[i]) @ Gs[jj]) ** 2)
                                 for i in range(N) for jj in range(i + 1, N)]))
            tt.append(t); G_tr.append(plant.G.copy()); s_tr.append(plant.s.copy())
    return (np.array(tt), np.array(D_tr), np.array(G_tr), np.array(s_tr))


runs = {tau: run_traced(tau) for tau in (0.1, 0.4)}
tt = runs[0.1][0]
STRIDE = 4                              # 2400 epochs -> 600 frames is too many
FRAMES = len(tt[::STRIDE])

fig = plt.figure(figsize=(11, 5.2), dpi=105)
aT = fig.add_subplot(1, 2, 1)
aD = fig.add_subplot(1, 2, 2)


def draw(f):
    k = min(f * STRIDE, len(tt) - 1)
    aT.clear(); aD.clear()
    _, _, G_tr, s_tr = runs[0.4]
    xs = G_tr[:k + 1, 0, 2]; ys = G_tr[:k + 1, 1, 2]
    aT.plot(xs, ys, "-", color="#90a4ae", lw=1.2)
    G = G_tr[k]; s = s_tr[k]
    R, p = G[:2, :2], G[:2, 2]
    aT.plot(*p, "s", color="#37474f", ms=9)
    for j in range(N):
        sig = s[j, 0]
        tip = p + R @ (np.array([np.cos(sig), np.sin(sig)]) * 1.0)
        aT.plot([p[0], tip[0]], [p[1], tip[1]], "-", color="#8d6e63", lw=1.0)
        aT.plot(*tip, "o", color=plt.cm.tab10(j / 10), ms=5)
    aT.set_aspect("equal")
    aT.set_title(f"persistent-turn maneuver, t={tt[k]:.0f} s\n"
                 "(shapes keep moving — the floor's premise)", fontsize=9)
    aT.set_xlabel("x (plant units)"); aT.set_ylabel("y")
    for tau, col in ((0.1, "#1565c0"), (0.4, "#e65100")):
        rt, rD = runs[tau][0], runs[tau][1]
        aD.semilogy(rt[:k + 1], np.maximum(rD[:k + 1], 1e-8), "-", color=col,
                    lw=1.6, label=f"$\\tau$={tau}")
    aD.axvspan(0.7 * TEND, TEND, color="#eceff1", zorder=0)
    aD.annotate("evaluation window\n(last 30%)", (0.72 * TEND, 2e-8),
                fontsize=7.5, color="#546e7a")
    aD.set_xlim(0, TEND); aD.set_ylim(1e-8, 1.0)
    aD.set_xlabel("t (s)"); aD.set_ylabel("disagreement $D(t)$")
    aD.legend(loc="upper left", fontsize=8)
    aD.set_title("staleness raises the steady-state disagreement\n"
                 "$D_{ss}$: measured, [CONJECTURAL] regime — not a Thm 7.2 test",
                 fontsize=9)


ani = animation.FuncAnimation(fig, draw, frames=FRAMES, blit=False)
out = os.path.join(RES, "floor_protocol.mp4")
ani.save(out, writer=animation.FFMpegWriter(fps=25, bitrate=1800))
print("wrote", out)
