"""Formation-sweep movie (L-CSS S3): the tau^2 order is formation-invariant.
Replays the EXACT 20-formation draw sequence of e3a_extension.py (seed 2026,
same consume order — asserted against the persisted JSON) and, formation by
formation, shows the drawn geometry, its amplitude-vs-tau fit, and the slope
accumulating in a strip that collapses onto 1.9993 +/- 1e-14.

Regenerate with: python formation_sweep_movie.py
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import FancyBboxPatch, Polygon
from tier1_sheaf.sheaf.holonomy import holonomy_amplitude_m2

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
ext = json.load(open(os.path.join(RES, "e3a_extension.json")))
XI = np.array([0.4, 0.0, 0.12])
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
rng = np.random.default_rng(2026)


def draw_shape(margin=0.10):
    while True:
        sig = rng.uniform(-1.2, 1.2)
        sig_i = rng.uniform(-1.2, 1.2)
        if abs(np.cos(sig_i)) > margin and abs(np.cos(sig)) > margin:
            return (float(sig), float(sig_i))


forms, slopes, ampsets = [], [], []
for f in range(20):
    si, sj = draw_shape(), draw_shape()
    amps = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in TAUS])
    forms.append((si, sj)); ampsets.append(amps)
    if amps.min() > 1e-14:
        slopes.append(float(np.polyfit(np.log(TAUS), np.log(amps), 1)[0]))
assert np.allclose(slopes, ext["formation_cluster"]["slopes"], atol=1e-12), \
    "draw-sequence replay diverged from e3a_extension.json"

HOLD = 10                                    # frames per formation
fig = plt.figure(figsize=(11, 6.0), dpi=105)
aF = fig.add_subplot(2, 2, 1)
aA = fig.add_subplot(2, 2, 2)
aS = fig.add_subplot(2, 1, 2)
fig.subplots_adjust(hspace=0.55)


def draw_formation_panel(ax, si, sj):
    ax.add_patch(FancyBboxPatch((-0.4, -0.28), 0.8, 0.56,
                 boxstyle="round,pad=0.05", fc="#37474f", ec="k", zorder=3))
    for (sig, sgi), col in [(si, "#1565c0"), (sj, "#b71c1c")]:
        att = np.array([np.cos(sig), np.sin(sig)]) * 0.5
        tip = np.array([np.cos(sig), np.sin(sig)]) * 1.9
        ax.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63", lw=1.3)
        hd = sig - sgi                       # heading from shape coordinates
        tri = np.array([[0.24, 0], [-0.15, 0.11], [-0.15, -0.11]])
        c, s = np.cos(hd), np.sin(hd)
        ax.add_patch(Polygon(tri @ np.array([[c, -s], [s, c]]).T + tip,
                             closed=True, fc=col, ec="k", zorder=4))
    ax.set_xlim(-2.3, 2.3); ax.set_ylim(-2.3, 2.3)
    ax.set_aspect("equal"); ax.axis("off")


def draw(k):
    f = min(k // HOLD, 19)
    for ax in (aF, aA, aS):
        ax.clear()
    si, sj = forms[f]
    draw_formation_panel(aF, si, sj)
    aF.set_title(f"formation draw {f + 1}/20  (Unif | taut, margin 0.10)\n"
                 f"$s_i$=({si[0]:+.2f},{si[1]:+.2f})  "
                 f"$s_j$=({sj[0]:+.2f},{sj[1]:+.2f})", fontsize=9)
    aA.loglog(TAUS, ampsets[f], "o-", color="#1565c0")
    aA.loglog(TAUS, ampsets[f][0] * (TAUS / TAUS[0]) ** 2, ":", color="#666")
    aA.set_title(f"fit slope: {slopes[f]:.6f}", fontsize=9)
    aA.set_xlabel("$\\tau$"); aA.set_ylabel("$\\Vert\\log\\mathrm{Hol}\\Vert$")
    upto = f + 1
    ref = 1.9992678569271
    dev = (np.array(slopes[:upto]) - ref) * 1e13
    aS.plot(range(1, upto + 1), dev, "o", color="#1565c0")
    aS.axhline((np.mean(slopes) - ref) * 1e13, color="#2e7d32", lw=1.0)
    aS.set_xlim(0.5, 20.5); aS.set_ylim(-4, 4)
    aS.set_xlabel("formation draw")
    aS.set_ylabel("slope $-$ 1.9992678569271\n($\\times 10^{-13}$)")
    aS.set_title(f"the order is a structural constant: "
                 f"{np.mean(slopes[:upto]):.10f} $\\pm$ "
                 f"{np.std(slopes[:upto]):.1e} — geometry moves only the "
                 f"coefficient", fontsize=8.5, pad=8)


ani = animation.FuncAnimation(fig, draw, frames=20 * HOLD, blit=False)
out = os.path.join(RES, "formation_sweep.mp4")
ani.save(out, writer=animation.FFMpegWriter(fps=10, bitrate=1800))
print("wrote", out)
