"""Render the N-vessel Drake transit: top-down animation + tension plots."""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from tier2_drake.harbor import ScenarioConfig, pentagon_vertices
from tier2_drake.run import run_transit

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)

WATER = "#dbe7ef"
WATER_D = "#0f2231"
BARGE = "#2b3a4a"
VESSEL = "#b23b2a"


def _box(cx, cy, yaw, lx, ly):
    c, s = np.cos(yaw), np.sin(yaw)
    corners = np.array([[lx/2, ly/2], [lx/2, -ly/2], [-lx/2, -ly/2], [-lx/2, ly/2]])
    R = np.array([[c, -s], [s, c]])
    return (corners @ R.T) + np.array([cx, cy])


def _load_polygon(cx, cy, yaw, cfg):
    """World-frame outline of the load: pentagon or box."""
    c, s = np.cos(yaw), np.sin(yaw)
    R = np.array([[c, -s], [s, c]])
    if cfg.load_shape == "pentagon":
        pts = pentagon_vertices(cfg.load_radius, cfg.load_phase)
    else:
        lx, ly = cfg.load_len, cfg.load_wid
        pts = np.array([[lx/2, ly/2], [lx/2, -ly/2], [-lx/2, -ly/2], [-lx/2, ly/2]])
    return (pts @ R.T) + np.array([cx, cy])


def _attach_world(load_pose, attach):
    x, y, th = load_pose
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, -s], [s, c]])
    return (attach @ R.T) + np.array([x, y])


def animate(data, path_mp4, path_gif=None, fps=12, stride=2):
    cfg = data["cfg"]
    t = data["t"][::stride]
    load = data["load"][::stride]
    asv = data["asv"][::stride]
    ten = data["tension"][::stride]
    tmax = float(np.percentile(data["tension"], 98)) or 1.0

    fig, (ax, axT) = plt.subplots(1, 2, figsize=(12, 5),
                                  gridspec_kw={"width_ratios": [1.7, 1]})
    load_size = cfg.load_radius if cfg.load_shape == "pentagon" else max(cfg.load_len, cfg.load_wid) / 2
    win = load_size + cfg.cable_len + 4.0

    def draw(i):
        ax.clear(); axT.clear()
        cx, cy = load[i, 0], load[i, 1]
        ax.set_facecolor(WATER)
        ax.add_patch(Polygon(_load_polygon(cx, cy, load[i, 2], cfg),
                             closed=True, fc=BARGE, ec="#10171f", lw=1.2, zorder=3))
        aw = _attach_world(load[i], data["attach"])
        cmap = plt.cm.YlOrRd
        for k in range(cfg.N):
            ax_, ay_, ay2 = asv[i, k]
            frac = np.clip(ten[i, k] / (tmax + 1e-9), 0, 1)
            ax.plot([aw[k, 0], ax_], [aw[k, 1], ay_], "-",
                    color=cmap(0.35 + 0.6 * frac), lw=1.5 + 3 * frac, zorder=2)
            ax.add_patch(Polygon(_box(ax_, ay_, ay2, cfg.asv_len, cfg.asv_wid),
                                 closed=True, fc=VESSEL, ec="#3a1109", lw=1.0, zorder=4))
        ax.set_xlim(cx - win, cx + win * 1.4); ax.set_ylim(cy - win * 0.75, cy + win * 0.75)
        ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        load_name = "caisson" if cfg.load_shape == "pentagon" else "barge"
        ax.set_title(f"N = {cfg.N} vessels · cooperative tow · t = {t[i]:5.1f} s   "
                     f"({load_name} at x = {cx:6.1f} m)", fontsize=10)
        ax.grid(alpha=0.15, color="#4a6a80")

        for k in range(cfg.N):
            axT.plot(t[:i+1], data["tension"][::stride][:i+1, k] / 1000,
                     lw=1.6, color=plt.cm.YlOrRd(0.4 + 0.5 * k / max(1, cfg.N-1)),
                     label=f"cable {k}")
        axT.set_xlim(t[0], t[-1]); axT.set_ylim(0, tmax / 1000 * 1.25)
        axT.set_xlabel("t (s)"); axT.set_ylabel("cable tension (kN)")
        axT.set_title("analytic tension recovery", fontsize=10)
        axT.grid(alpha=0.25); axT.legend(fontsize=7, ncol=2, loc="lower right")
        fig.tight_layout()

    anim = FuncAnimation(fig, draw, frames=len(t), interval=1000 / fps)
    anim.save(path_mp4, writer=FFMpegWriter(fps=fps, bitrate=1600))
    print(f"wrote {path_mp4}")
    if path_gif:
        anim.save(path_gif, writer=PillowWriter(fps=fps))
        print(f"wrote {path_gif}")
    plt.close(fig)


def comparison_figure(sym_datas, asym_data, path):
    """Left: barge heading over time. Right: steady cable tensions per formation.

    Symmetric thrust ⇒ zero yaw and equal tensions; unequal thrust (a weaker starboard
    thruster) ⇒ the barge yaws and the cables carry uneven tension.
    """
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.6))
    cols = {4: "#2166ac", 5: "#b2182b"}
    for d in sym_datas:
        N = d["cfg"].N
        axA.plot(d["t"], np.degrees(d["load"][:, 2]), "-", lw=2.2, color=cols.get(N, "k"),
                 label=f"N={N} symmetric")
    if asym_data is not None:
        axA.plot(asym_data["t"], np.degrees(asym_data["load"][:, 2]), "--", lw=2.4,
                 color="#8a5a00", label="N=4 unequal thrust")
    axA.axhline(0, ls=":", color="gray", lw=0.8)
    axA.set_xlabel("t (s)"); axA.set_ylabel("load heading (deg)")
    axA.set_title("Load heading — symmetric thrust holds course;\nunequal thrust induces yaw",
                  fontsize=10)
    axA.legend(fontsize=8, loc="upper left"); axA.grid(alpha=0.25)

    for d in sym_datas:
        N = d["cfg"].N
        Tss = d["tension"][int(0.8*len(d["tension"])):].mean(0) / 1000
        axB.plot(range(N), Tss, "o-", color=cols.get(N, "k"), lw=2, ms=7, label=f"N={N} symmetric")
    if asym_data is not None:
        Tss = asym_data["tension"][int(0.8*len(asym_data["tension"])):].mean(0) / 1000
        spread = (Tss.max() - Tss.min()) / Tss.mean() * 100
        axB.plot(range(asym_data["cfg"].N), Tss, "s--", color="#8a5a00", lw=2, ms=8,
                 label=f"N=4 unequal ({spread:.0f}% spread)")
    axB.set_xlabel("cable index"); axB.set_ylabel("steady tension (kN)")
    axB.set_title("Steady cable tensions —\nsymmetric ⇒ equal, unequal thrust ⇒ imbalanced", fontsize=10)
    axB.set_ylim(0, None); axB.legend(fontsize=8); axB.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"wrote {path}")
    plt.close(fig)


def main():
    sym = []
    for N in (4, 5):
        d = run_transit(ScenarioConfig(N=N), Tend=40.0, log_dt=0.15)
        sym.append(d)
        animate(d, os.path.join(OUT, f"tow_N{N}.mp4"),
                os.path.join(OUT, f"tow_N{N}.gif"), fps=10, stride=1)
    asym = run_transit(ScenarioConfig(N=4, thrust_scale=(1.3,1.1,0.9,0.7)), Tend=40.0, log_dt=0.15)
    animate(asym, os.path.join(OUT, "tow_N4_asym.mp4"), None, fps=10, stride=1)
    comparison_figure(sym, asym, os.path.join(OUT, "tow_comparison.png"))


if __name__ == "__main__":
    main()
