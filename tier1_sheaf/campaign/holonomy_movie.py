"""Holonomy-loop supplementary movie (L-CSS / T-CNS): the round-trip defect
made visible. Left: a reference frame carried around the two-transport loop
e^{tau Ci} e^{tau Cj} e^{-tau Ci} e^{-tau Cj} — the residual frame mismatch IS
the holonomy. Right: ||Log Hol|| tracing the tau^2 law as tau grows."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.linalg import expm
from tier1_sheaf.core.shapes import conjugated_generator
from tier1_sheaf.sheaf.holonomy import holonomy_amplitude_m2

GEN_I, GEN_J = (0.4, 0.3), (0.9, -0.5)
XI = np.array([0.4, 0.0, 0.12])
Ci = conjugated_generator(*GEN_I, XI)
Cj = conjugated_generator(*GEN_J, XI)
TAU_MAX = 1.6
N_FR = 160

def frame_pts(T, scale=1.0):
    """Unit frame (origin, x-axis, y-axis) mapped by the se(2)-matrix rep T."""
    pts = np.array([[0, 0], [scale, 0], [0, scale]])
    R = T[:2, :2]; t = T[:2, 2] if T.shape[1] > 2 else np.zeros(2)
    return pts @ R.T + t

fig, (aL, aR) = plt.subplots(1, 2, figsize=(11, 5), dpi=110)

def draw(k):
    aL.clear(); aR.clear()
    tau = 0.02 + (TAU_MAX - 0.02) * k / (N_FR - 1)
    legs = [expm(tau * Ci), expm(tau * Cj), expm(-tau * Ci), expm(-tau * Cj)]
    T = np.eye(3)
    path = [T.copy()]
    for L in legs:
        T = T @ L
        path.append(T.copy())
    cols = ["#999", "#1a6b8a", "#5a5f2d", "#8a5a1a", "#b3452c"]
    labs = ["start", r"$e^{\tau C_i}$", r"$e^{\tau C_j}$", r"$e^{-\tau C_i}$", r"$e^{-\tau C_j}$ (end)"]
    for i, (P, c) in enumerate(zip(path, cols)):
        F = frame_pts(P, 0.5)
        aL.plot([F[0,0], F[1,0]], [F[0,1], F[1,1]], "-", color=c, lw=2.5 if i in (0,4) else 1.2)
        aL.plot([F[0,0], F[2,0]], [F[0,1], F[2,1]], "--", color=c, lw=2.5 if i in (0,4) else 1.2)
        aL.plot([F[0,0]], [F[0,1]], "o", color=c, ms=6, label=labs[i])
    d = np.linalg.norm(path[-1][:2, 2] - path[0][:2, 2])
    aL.set_xlim(-1.4, 1.9); aL.set_ylim(-1.4, 1.6); aL.set_aspect("equal")
    aL.legend(fontsize=7, loc="upper left")
    aL.set_title(f"the loop fails to close: frame gap = holonomy\n"
                 rf"$\tau$ = {tau:.2f} s;  end-frame offset {d:.3f}", fontsize=10)
    taus = np.linspace(0.02, TAU_MAX, 80)
    amps = [holonomy_amplitude_m2(GEN_I, GEN_J, XI, t) for t in taus]
    aR.loglog(taus, amps, "-", color="#1a6b8a", lw=1.6)
    aR.loglog([tau], [holonomy_amplitude_m2(GEN_I, GEN_J, XI, tau)], "o",
              color="#b3452c", ms=9)
    aR.loglog(taus, [t**2 * 0.241 for t in taus], ":", color="#999", lw=1)
    aR.annotate(r"$\tau^2\,\|[C_i,C_j]\|$", (0.5, 0.03), color="#999", fontsize=10)
    aR.set_xlabel(r"$\tau$ [s]"); aR.set_ylabel(r"$\|\mathrm{Log\,Hol}\|$")
    aR.set_title("the amplitude traces the quadratic law\n(Thm: leading-order, deterministic)", fontsize=10)
    aR.grid(True, which="both", alpha=0.25)
    return []

ani = animation.FuncAnimation(fig, draw, frames=N_FR, blit=False)
out = "/workspaces/Anholonomy/tier1_sheaf/results/holonomy_loop.mp4"
ani.save(out, writer=animation.FFMpegWriter(fps=20, bitrate=1800))
print("wrote", out)
