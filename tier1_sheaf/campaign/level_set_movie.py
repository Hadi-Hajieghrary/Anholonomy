"""Level-set movie (L-CSS S2): side-by-side loop transport — a generic shape
pair (nonzero commutator: the loop fails to close, gap tracing the tau^2 law)
vs the C15 level-set pair from e3a_extension.json (equal conjugated generators
at 1.06 rad shape separation: the loop closes to machine precision at EVERY
tau). The protected class is the level set of s -> C(s; xi) — observed.

Deterministic (no RNG). Versioned; regenerate with: python level_set_movie.py
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.linalg import expm
from tier1_sheaf.core.shapes import conjugated_generator
from tier1_sheaf.sheaf.holonomy import holonomy_amplitude_m2

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
ext = json.load(open(os.path.join(RES, "e3a_extension.json")))
XI = np.array([0.4, 0.0, 0.12])

GEN = ((0.4, 0.3), (0.9, -0.5))                       # generic pair (S1 movie)
LVL = (tuple(ext["C15"][0]["shapes"][:2]),            # the C15 discovered pair
       tuple(ext["C15"][0]["shapes"][2:]))
TAU_MAX, N_FR = 1.6, 160


def frame_pts(T, scale=1.0):
    pts = np.array([[0, 0], [scale, 0], [0, scale]])
    return pts @ T[:2, :2].T + T[:2, 2]


def loop_path(si, sj, tau):
    Ci = conjugated_generator(*si, XI)
    Cj = conjugated_generator(*sj, XI)
    T = np.eye(3)
    path = [T.copy()]
    for L in (expm(tau * Ci), expm(tau * Cj), expm(-tau * Ci), expm(-tau * Cj)):
        T = T @ L
        path.append(T.copy())
    return path


taus = np.linspace(0.02, TAU_MAX, N_FR)
amp_gen = np.array([holonomy_amplitude_m2(*GEN, XI, t) for t in taus])
amp_lvl = np.array([holonomy_amplitude_m2(*LVL, XI, t) for t in taus])

fig = plt.figure(figsize=(11, 6.4), dpi=105)
aG = fig.add_subplot(2, 2, 1)
aL = fig.add_subplot(2, 2, 2)
aB = fig.add_subplot(2, 1, 2)


def draw(k):
    for ax in (aG, aL, aB):
        ax.clear()
    tau = taus[k]
    for ax, pair, ttl, amp in (
            (aG, GEN, "generic pair: $[C_i,C_j]\\neq 0$", amp_gen[k]),
            (aL, LVL, "level-set pair (C15): $C_i=C_j$ at 1.06 rad apart",
             amp_lvl[k])):
        path = loop_path(*pair, tau)
        cols = ["#999", "#1a6b8a", "#5a5f2d", "#8a5a1a", "#b3452c"]
        for i, (P, c) in enumerate(zip(path, cols)):
            F = frame_pts(P, 0.5)
            lw = 2.5 if i in (0, 4) else 1.1
            ax.plot([F[0, 0], F[1, 0]], [F[0, 1], F[1, 1]], "-", color=c, lw=lw)
            ax.plot([F[0, 0], F[2, 0]], [F[0, 1], F[2, 1]], "--", color=c, lw=lw)
            ax.plot([F[0, 0]], [F[0, 1]], "o", color=c, ms=5)
        ax.set_xlim(-1.6, 2.1); ax.set_ylim(-1.6, 1.8); ax.set_aspect("equal")
        ax.set_title(f"{ttl}\n$\\tau$={tau:.2f}   "
                     f"$\\Vert\\log\\mathrm{{Hol}}\\Vert$ = {amp:.2e}",
                     fontsize=9)
    aB.loglog(taus[:k + 1], np.maximum(amp_gen[:k + 1], 1e-17), "-",
              color="#b3452c", lw=2, label="generic pair")
    aB.loglog(taus[:k + 1], np.maximum(amp_lvl[:k + 1], 1e-17), "-",
              color="#2e7d32", lw=2, label="level-set pair (machine zero, all $\\tau$)")
    aB.loglog(taus, amp_gen[0] * (taus / taus[0]) ** 2, ":", color="#666",
              label="$\\tau^2$ guide")
    aB.set_xlim(taus[0], TAU_MAX); aB.set_ylim(1e-17, 1.0)
    aB.set_xlabel("staleness $\\tau$ (s)")
    aB.set_ylabel("$\\Vert\\log\\mathrm{Hol}\\Vert$")
    aB.legend(loc="center left", fontsize=8)
    aB.set_title("exact protection at all orders — not merely $O(\\tau^3)$",
                 fontsize=9)


ani = animation.FuncAnimation(fig, draw, frames=N_FR, blit=False)
out = os.path.join(RES, "level_set.mp4")
ani.save(out, writer=animation.FFMpegWriter(fps=20, bitrate=1800))
print("wrote", out)
