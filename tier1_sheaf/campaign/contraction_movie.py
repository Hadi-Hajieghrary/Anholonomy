"""Contraction movie (T-CNS M2): the Thm 6.3 mechanism made visible.
Both topologies (C_5 cycle, K_5 complete) run the E2 protocol — frozen shapes,
noise off, step-perturbed estimates — side by side. Left: each agent's SE(2)
error vector (translation components) shrinking toward the shared gauge
component; right: the gauge-complement norm decaying log-linearly at the
measured rates, with mu + kappa*lambda2 the tested prediction (C6 PASSED,
slope 1.403; LTV/frozen hedge carried).

Same estimator calls and constants as experiments/e2_contraction.py; per-agent
errors recorded for animation. Deterministic given SEED.
Regenerate with: python contraction_movie.py
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation

import estimator_core as ec
from tier1_sheaf.core.se2 import Exp, Log, inv
from tier1_sheaf.core.shapes import Ad_m
from tier1_sheaf.experiments.e2_contraction import (SHAPES, XI, DC, edges_of,
                                                    lambda2)
from tier2_drake.blind_harbor.sensors import KAPPA_DIR

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
SEED, KAPPA, DELTA, TEND, DT = 7, 1.0, 0.5, 6.0, 0.02


def run_traced(topology):
    """The E2 loop (deterministic propagate, direction @20Hz, fuse @DC),
    recording per-agent gauge-complement errors at every send epoch."""
    rng = np.random.default_rng(np.random.SeedSequence([SEED, 17]))
    N = len(SHAPES)
    sts = [ec.FilterState.initial(SHAPES[j].copy(), 1.0) for j in range(N)]
    zetas = [np.linalg.solve(Ad_m(*SHAPES[j], 1.0), XI) for j in range(N)]
    G = np.eye(3)
    for j in range(N):
        d = rng.standard_normal(3); d *= DELTA / np.linalg.norm(d)
        sts[j] = sts[j].replace(G=sts[j].G @ Exp(d))
    alpha = KAPPA * DC
    E = edges_of(topology)
    directed = E + [(b, a) for (a, b) in E]
    per = int(round(DC / DT))
    tt, comp, perp_n = [], [], []
    for k in range(int(round(TEND / DT))):
        t = k * DT
        for j in range(N):
            sts[j] = ec.propagate(sts[j], zetas[j], DT,
                                  shape_motion_correction=False)
        G = G @ Exp(DT * XI)
        if k % 2 == 1:
            for j in range(N):
                sts[j] = ec.update_direction(sts[j], SHAPES[j][1], KAPPA_DIR)
        if k % per == 0 and alpha > 0:
            snaps = [(sts[j].G.copy(), sts[j].s.copy()) for j in range(N)]
            for (a, b) in directed:
                G_nb, s_nb = snaps[b]
                sts[a], _ = ec.fuse_with_rule("paper", sts[a], G_nb, s_nb,
                                              DC, zetas[a], alpha, 1.0, b)
        if k % per == 0:
            errs = np.array([Log(sts[j].G @ inv(G)) for j in range(N)])
            e_perp = errs - errs.mean(axis=0)
            tt.append(t); comp.append(e_perp.copy())
            perp_n.append(float(np.linalg.norm(e_perp)))
    return np.array(tt), np.array(comp), np.array(perp_n)


data = {topo: run_traced(topo) for topo in ("cycle", "complete")}
COLS = plt.cm.tab10(np.linspace(0, 0.5, len(SHAPES)))

fig = plt.figure(figsize=(11, 5.4), dpi=105)
aC = fig.add_subplot(1, 3, 1)
aK = fig.add_subplot(1, 3, 2)
aR = fig.add_subplot(1, 3, 3)
K_FR = len(data["cycle"][0])


def draw(k):
    for ax in (aC, aK, aR):
        ax.clear()
    for ax, topo, ttl in ((aC, "cycle", "$C_5$ cycle ($\\lambda_2$=1.38)"),
                          (aK, "complete", "$K_5$ complete ($\\lambda_2$=5)")):
        tt, comp, _ = data[topo]
        for j in range(len(SHAPES)):
            ax.plot(comp[:k + 1, j, 0], comp[:k + 1, j, 1], "-",
                    color=COLS[j], lw=0.9, alpha=0.6)
            ax.plot(comp[k, j, 0], comp[k, j, 1], "o", color=COLS[j], ms=6)
        ax.plot(0, 0, "k+", ms=10)
        ax.set_xlim(-0.45, 0.45); ax.set_ylim(-0.45, 0.45)
        ax.set_aspect("equal")
        ax.set_title(f"{ttl}\ngauge-complement error, t={tt[k]:.2f} s",
                     fontsize=9)
        ax.set_xlabel("$e_{\\perp,x}$"); ax.set_ylabel("$e_{\\perp,y}$")
    for topo, col in (("cycle", "#1565c0"), ("complete", "#e65100")):
        tt, _, pn = data[topo]
        aR.semilogy(tt[:k + 1], np.maximum(pn[:k + 1], 1e-9), "-", color=col,
                    lw=2, label=f"{topo}")
    aR.set_xlim(0, TEND); aR.set_ylim(1e-9, 2.0)
    aR.set_xlabel("t (s)"); aR.set_ylabel("$\\Vert e_\\perp\\Vert$")
    aR.legend(fontsize=8)
    aR.set_title("rate grows with $\\kappa\\lambda_2$ (C6 PASSED,\n"
                 "slope 1.403; LTV/frozen hedge)", fontsize=9)


ani = animation.FuncAnimation(fig, draw, frames=K_FR, blit=False)
out = os.path.join(RES, "contraction.mp4")
ani.save(out, writer=animation.FFMpegWriter(fps=15, bitrate=1800))
print("wrote", out)
