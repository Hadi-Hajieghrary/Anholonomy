"""L-CSS letter — 5 scenario / qualitative figures grounded in real Tier-1
simulation, conveying WHAT the latency-curvature floor looks like and what the
letter accomplishes. All data is recomputed deterministically from the same
operators the campaign uses (imported trace functions; no re-render side
effects after the __main__ guards). Outputs -> tier1_sheaf/results/artifacts/.

L1 lcss_loop_filmstrip   — the transported frame around the stale round-trip
                           loop at growing tau, generic vs the C15 level-set
                           pair: the defect grows quadratically on the left,
                           stays machine-zero on the right (the mechanism +
                           the discovery, made visual).
L2 lcss_transit_scene    — the reduced cooperative-tow plant executing the
                           persistent turn: load track + shape fan at three
                           instants (the physical setting the floor lives in;
                           shapes must keep moving).
L3 lcss_amplitude_carpet — ||log Hol|| over (staleness tau, shape separation):
                           the tau^2 growth and the protection valley at the
                           level set, in one field.
L4 lcss_commutator_landscape — log10||[C(s_ref),C(s)]|| as a surface over the
                           shape torus with the two discrete zeros marked.
L5 lcss_graphical_abstract — problem -> mechanism -> result in one panel.
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch
from scipy.linalg import expm

from tier1_sheaf.core.shapes import conjugated_generator
from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                        holonomy_amplitude_m2)
from tier1_sheaf.campaign.level_set_movie import loop_path, frame_pts, GEN, LVL
from tier1_sheaf.campaign import floor_protocol_movie as fpm

RES = "/workspaces/Anholonomy/tier1_sheaf/results"
OUT = os.path.join(RES, "artifacts")
os.makedirs(OUT, exist_ok=True)
XI = np.array([0.4, 0.0, 0.12])
ext = json.load(open(os.path.join(RES, "e3a_extension.json")))
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "figure.dpi": 150})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------
# L1 — the transported-belief TRAIL around the stale fusion loop. Two panels
# (generic vs level-set); in each, the continuous path of the belief's frame
# origin as it is carried along the four legs e^{tau Ci} e^{tau Cj}
# e^{-tau Ci} e^{-tau Cj}, drawn for several tau. The path should return to
# the start but does not: the visible gap IS the holonomy (the disagreement a
# stale round trip injects). On the level set the trail closes for every tau.
# ---------------------------------------------------------------------------
def _loop_trail(si, sj, tau, npts=60):
    """Origin (x,y) and heading of the running product along the loop."""
    Ci = conjugated_generator(*si, XI)
    Cj = conjugated_generator(*sj, XI)
    legs = [(Ci, +tau), (Cj, +tau), (Ci, -tau), (Cj, -tau)]
    T = np.eye(3)
    xs, ys = [T[0, 2]], [T[1, 2]]
    ths = [np.arctan2(T[1, 0], T[0, 0])]
    for C, span in legs:
        for s in np.linspace(span / npts, span, npts):
            Ts = T @ expm(s * C)
            xs.append(Ts[0, 2]); ys.append(Ts[1, 2])
            ths.append(np.arctan2(Ts[1, 0], Ts[0, 0]))
        T = T @ expm(span * C)
    return np.array(xs), np.array(ys), np.array(ths)


def fig_loop_filmstrip():
    taus = [0.4, 0.8, 1.2, 1.6]
    cmap = plt.cm.viridis(np.linspace(0.15, 0.9, len(taus)))
    fig, (aG, aL) = plt.subplots(1, 2, figsize=(8.2, 3.9))
    for ax, pair, ttl, closes in [
            (aG, GEN, "generic pair  ($[C_i,C_j]\\neq 0$)", False),
            (aL, LVL, "level-set pair  ($C_i=C_j$, C15)", True)]:
        for tau, c in zip(taus, cmap):
            xs, ys, ths = _loop_trail(*pair, tau)
            ax.plot(xs, ys, "-", color=c, lw=1.8, label=f"$\\tau={tau}$")
            gap = np.hypot(xs[-1] - xs[0], ys[-1] - ys[0])
            if not closes and tau == taus[-1]:
                # the closing defect for the largest tau
                ax.annotate("", xy=(xs[-1], ys[-1]), xytext=(xs[0], ys[0]),
                            arrowprops=dict(arrowstyle="-|>", color="#c62828",
                                            lw=2.4))
                ax.plot(xs[-1], ys[-1], "o", color="#c62828", ms=7, zorder=6)
                ax.annotate(f"holonomy gap\n$\\|\\log\\mathrm{{Hol}}\\|"
                            f"={holonomy_amplitude_m2(*pair, XI, tau):.2f}$",
                            (xs[-1], ys[-1]), textcoords="offset points",
                            xytext=(8, -4), fontsize=7.5, color="#c62828")
        ax.plot(0, 0, "ko", ms=7, zorder=6)
        ax.annotate("start", (0, 0), textcoords="offset points",
                    xytext=(6, 6), fontsize=8)
        if closes:
            # mark the turnaround: legs 1-2 go out along C, legs 3-4 retrace
            xs, ys, _ = _loop_trail(*pair, taus[-1])
            mid = len(xs) // 2
            ax.plot(xs[mid], ys[mid], "s", color="#2e7d32", ms=7, zorder=6)
            ax.annotate("turnaround", (xs[mid], ys[mid]),
                        textcoords="offset points", xytext=(-4, -14),
                        fontsize=7.5, color="#2e7d32", ha="right")
            ax.annotate("out along $C$, then\nretraces exactly $\\to$\ncloses "
                        "for every $\\tau$\n(gap $<10^{-15}$)",
                        (0.04, 0.60), xycoords="axes fraction",
                        fontsize=8, color="#2e7d32")
        ax.set_aspect("equal")
        ax.set_title(ttl, fontsize=9.5)
        ax.set_xlabel("belief-frame $x$"); ax.legend(fontsize=7, loc="best")
    aG.set_ylabel("belief-frame $y$")
    fig.suptitle("The transported belief's trail around the stale fusion loop "
                 "$e^{\\tau C_i}e^{\\tau C_j}e^{-\\tau C_i}e^{-\\tau C_j}$: it "
                 "should return to the start but does not --- the gap is the "
                 "holonomy", fontsize=9, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "lcss_loop_filmstrip")


# ---------------------------------------------------------------------------
# L2 — the cooperative-tow scenario, made legible. (a) the tow GEOMETRY in the
# load frame with the shape angles labeled (why each agent sees the load
# differently -> [C_i,C_j] != 0); (b) the REAL shape-angle trajectories from
# the reduced-plant run (why the floor is active: the shapes never stop
# moving). Grounded in floor_protocol_movie.runs (recorded sim).
# ---------------------------------------------------------------------------
def fig_transit_scene():
    tt, D_tr, G_tr, s_tr = fpm.runs[0.4]
    N = s_tr.shape[1]
    cols = plt.cm.tab10(np.linspace(0, 0.85, N))
    k0 = int(0.45 * len(tt))                       # a representative instant
    sig = s_tr[k0, :, 0]                            # cable dir in load frame
    sigi = s_tr[k0, :, 1]                           # cable dir in vessel frame
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.6, 3.7),
                               gridspec_kw={"width_ratios": [1.05, 1]})

    # ---- (a) geometry snapshot in the LOAD frame ----------------------------
    a.set_aspect("equal"); a.axis("off")
    a.set_title("(a) cooperative-tow geometry (load frame)", fontsize=9)
    a.add_patch(FancyBboxPatch((-0.9, -0.6), 1.8, 1.2, boxstyle="round,pad=0.1",
                fc="#37474f", ec="k", zorder=3))
    a.text(0, 0, "load $G$", color="w", ha="center", va="center", fontsize=9)
    a.annotate("", xy=(2.4, 0), xytext=(0, 0), arrowprops=dict(
        arrowstyle="-|>", color="k", lw=1.3))
    a.annotate("", xy=(0, 2.0), xytext=(0, 0), arrowprops=dict(
        arrowstyle="-|>", color="k", lw=1.3))
    a.text(2.45, -0.1, "$x_L$", fontsize=9); a.text(0.08, 2.0, "$y_L$", fontsize=9)
    L = 4.0
    for j in range(N):
        att = np.array([np.cos(sig[j]), np.sin(sig[j])]) * 0.95
        tip = np.array([np.cos(sig[j]), np.sin(sig[j])]) * L
        a.plot([att[0], tip[0]], [att[1], tip[1]], "-", color="#8d6e63",
               lw=1.6, zorder=2)
        hd = sig[j] - sigi[j]                        # vessel heading in load frame
        tri = np.array([[0.55, 0], [-0.35, 0.28], [-0.35, -0.28]])
        c, s = np.cos(hd), np.sin(hd)
        a.add_patch(Polygon(tri @ np.array([[c, -s], [s, c]]).T + tip,
                    closed=True, fc=cols[j], ec="k", zorder=5))
        a.text(tip[0] * 1.16, tip[1] * 1.16, f"{j+1}", fontsize=8,
               ha="center", va="center", color=cols[j], fontweight="bold")
    # annotate the shape angles on agent 0's cable
    j = int(np.argmax(sig)); ang = sig[j]
    a.annotate("", xy=(1.6 * np.cos(ang), 1.6 * np.sin(ang)), xytext=(1.6, 0),
               arrowprops=dict(arrowstyle="-", color="#c62828", lw=1.0,
                               connectionstyle="arc3,rad=0.3"))
    a.text(1.5 * np.cos(ang / 2) + 0.2, 1.5 * np.sin(ang / 2), "$\\sigma_j$",
           color="#c62828", fontsize=10)
    tipj = np.array([np.cos(ang), np.sin(ang)]) * L
    hd = ang - sigi[j]
    a.plot([tipj[0], tipj[0] + 1.1 * np.cos(hd)],
           [tipj[1], tipj[1] + 1.1 * np.sin(hd)], ":", color=cols[j], lw=1.2)
    a.text(tipj[0] + 0.5, tipj[1] + 0.9,
           "$\\sigma_{i,j}$: cable dir\nin vessel frame", fontsize=7.5,
           color="#455a64")
    a.text(1.0, -4.2, "each agent views the load through its own shape "
           "$s_j=(\\sigma_j,\\sigma_{i,j})$\n$\\Rightarrow$ generators $C_j$ "
           "differ $\\Rightarrow$ $[C_i,C_j]\\neq0$ (the floor)", ha="center",
           fontsize=7.8, color="#37474f")
    a.set_xlim(-3.2, 6.2); a.set_ylim(-4.8, 3.2)

    # ---- (b) the shapes keep moving -----------------------------------------
    for j in range(N):
        b.plot(tt, np.degrees(s_tr[:, j, 0]), "-", color=cols[j], lw=1.4,
               label=f"agent {j+1}")
    b.axvline(tt[k0], color="#90a4ae", ls=":", lw=1.2)
    b.annotate("$\\leftarrow$ panel (a) instant", (tt[k0] + 2, -47),
               fontsize=7, color="#607d8b", ha="left")
    b.set_xlabel("t (s)"); b.set_ylabel("cable angle $\\sigma_j(t)$ (deg)")
    b.set_ylim(-55, 62)
    b.set_title("(b) the shape fan never stops moving\n(persistent turn "
                "$\\Rightarrow$ the floor is active)", fontsize=9)
    b.legend(fontsize=7, ncol=3, loc="upper center")
    fig.tight_layout()
    save(fig, "lcss_transit_scene")


# ---------------------------------------------------------------------------
# L3 — amplitude carpet over (tau, shape separation)
# ---------------------------------------------------------------------------
def fig_amplitude_carpet():
    # a one-parameter family: fix s_i, sweep s_j along a ray so the shape
    # separation Delta = ||s_j - s_i|| varies; the level-set partner sits at
    # a specific Delta where the amplitude collapses.
    s_i = np.array(ext["C15"][0]["shapes"][:2])
    partner = np.array(ext["C15"][0]["shapes"][2:])
    ray = partner - s_i
    ray = ray / np.linalg.norm(ray)
    deltas = np.linspace(0.15, 2.4, 120)
    taus = np.geomspace(0.05, 1.6, 90)
    Z = np.zeros((len(taus), len(deltas)))
    for b, d in enumerate(deltas):
        s_j = s_i + d * ray
        for a, t in enumerate(taus):
            Z[a, b] = holonomy_amplitude_m2(tuple(s_i), tuple(s_j), XI, t)
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    pc = ax.pcolormesh(deltas, taus, np.log10(np.maximum(Z, 1e-18)),
                       cmap="magma", shading="auto", rasterized=True)
    ax.set_yscale("log")
    d_lvl = np.linalg.norm(partner - s_i)
    ax.axvline(d_lvl, color="#39d3c0", lw=1.6, ls="--")
    ax.annotate("level-set\npartner\n(protection\nvalley)", (d_lvl + 0.05, 0.09),
                color="#39d3c0", fontsize=7)
    ax.set_xlabel("shape separation $\\Delta = \\|s_j - s_i\\|$ (rad)")
    ax.set_ylabel("staleness $\\tau$ (s)")
    ax.set_title("$\\log_{10}\\|\\log\\mathrm{Hol}\\|$: the floor grows as "
                 "$\\tau^2$\nand collapses at the level set", fontsize=8.5)
    fig.colorbar(pc, ax=ax, shrink=0.85, label="$\\log_{10}\\|\\log\\mathrm{Hol}\\|$")
    save(fig, "lcss_amplitude_carpet")


# ---------------------------------------------------------------------------
# L4 — commutator landscape over the shape torus (3D surface)
# ---------------------------------------------------------------------------
def fig_commutator_landscape():
    s_ref = np.array(ext["C15"][0]["shapes"][:2])
    partner = np.array(ext["C15"][0]["shapes"][2:])
    Cr = conjugated_generator(s_ref[0], s_ref[1], XI)
    n = 121
    sig = np.linspace(-np.pi, np.pi, n)
    sgi = np.linspace(-np.pi, np.pi, n)
    S, SI = np.meshgrid(sig, sgi)
    Z = np.zeros_like(S)
    for a in range(n):
        for b in range(n):
            C = conjugated_generator(S[a, b], SI[a, b], XI)
            Z[a, b] = np.log10(max(np.linalg.norm(Cr @ C - C @ Cr), 1e-12))
    fig = plt.figure(figsize=(5.6, 4.0))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(S, SI, Z, cmap="viridis", rstride=2, cstride=2,
                    linewidth=0, antialiased=True, alpha=0.85)
    zfloor = -12.5
    for pt, mk, lab in [(s_ref, "*", "$s_{\\mathrm{ref}}$"),
                        (partner, "o", "level partner")]:
        C = conjugated_generator(pt[0], pt[1], XI)
        zval = np.log10(max(np.linalg.norm(Cr @ C - C @ Cr), 1e-13))
        # a bright stem from the floor up to the surface marks each exact zero
        ax.plot([pt[0], pt[0]], [pt[1], pt[1]], [zfloor, 0.5], color="#e53935",
                lw=2.2, zorder=10)
        ax.scatter([pt[0]], [pt[1]], [0.6], color="#e53935", s=55, marker=mk,
                   zorder=11)
        ax.text(pt[0], pt[1], 1.6, lab, color="#b71c1c", fontsize=8)
    ax.set_zlim(zfloor, 1.5)
    ax.set_xlabel("$\\sigma$", labelpad=-3)
    ax.set_ylabel("$\\sigma_i$", labelpad=-3)
    ax.set_zlabel("$\\log_{10}\\|[C_{\\mathrm{ref}},C]\\|$", labelpad=-6)
    ax.set_title("The commutator surface is nowhere flat but at TWO points:\n"
                 "the protected class is discrete over the shape torus",
                 fontsize=8.5)
    ax.view_init(elev=28, azim=-62)
    ax.tick_params(labelsize=6, pad=-2)
    save(fig, "lcss_commutator_landscape")


# ---------------------------------------------------------------------------
# L5 — graphical abstract (problem -> mechanism -> result)
# ---------------------------------------------------------------------------
def fig_graphical_abstract():
    fig = plt.figure(figsize=(9.4, 2.9))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.15], wspace=0.28)
    # (1) problem: stale fusion around a cycle
    a = fig.add_subplot(gs[0]); a.axis("off"); a.set_aspect("equal")
    a.set_title("problem: delayed decentralized fusion", fontsize=8.5)
    ang = np.linspace(0, 2 * np.pi, 4, endpoint=False) + 0.4
    pts = np.stack([np.cos(ang), np.sin(ang)], 1)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        a.annotate("", xy=pts[j], xytext=pts[i], arrowprops=dict(
            arrowstyle="-|>", color="#1565c0", lw=1.4,
            connectionstyle="arc3,rad=0.18"))
    for k, pp in enumerate(pts):
        a.add_patch(Circle(pp, 0.16, fc=plt.cm.tab10(k / 10), ec="k", zorder=4))
    a.text(0, 0, "load\n$G$", ha="center", va="center", fontsize=7)
    a.text(0, -1.55, "each edge fused with\nstaleness $\\tau$", ha="center",
           fontsize=7, color="#455a64")
    a.set_xlim(-1.5, 1.5); a.set_ylim(-1.9, 1.5)
    # (2) mechanism: the loop defect
    b = fig.add_subplot(gs[1]); b.axis("off"); b.set_aspect("equal")
    b.set_title("mechanism: constraint-curvature holonomy", fontsize=8.5, pad=12)
    path = loop_path(GEN[0], GEN[1], 1.2)
    cols = ["#999", "#1a6b8a", "#5a5f2d", "#8a5a1a", "#b3452c"]
    for i, (P, c) in enumerate(zip(path, cols)):
        F = frame_pts(P, 0.5)
        lw = 2.6 if i in (0, 4) else 1.1
        b.plot([F[0, 0], F[1, 0]], [F[0, 1], F[1, 1]], "-", color=c, lw=lw)
        b.plot([F[0, 0], F[2, 0]], [F[0, 1], F[2, 1]], "--", color=c, lw=lw)
    b.annotate("", xy=path[-1][:2, 2], xytext=path[0][:2, 2],
               arrowprops=dict(arrowstyle="-|>", color="#b3452c", lw=2.2))
    b.text(0.1, -1.5, "$\\log\\mathrm{Hol}=\\tau^2[C_i,C_j]+O(\\tau^3)$",
           ha="center", fontsize=8.5, color="#b3452c")
    b.set_xlim(-1.3, 2.0); b.set_ylim(-1.8, 1.6)
    # (3) result: measured law + switch-offs
    c = fig.add_subplot(gs[2])
    import csv
    rows = list(csv.reader(open(os.path.join(RES, "e3a_amplitude.csv"))))
    taus = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
    gen = next(r for r in rows[1:] if r[0] == "generic")
    amp = np.array([float(x) for x in gen[2:8]])           # 6 tau columns
    soff = next(r for r in rows[1:] if r[0].startswith("generic, eta=0"))
    eta0 = np.array([float(x) for x in soff[2:8]])
    c.loglog(taus, amp, "o-", color="#1565c0", lw=2, ms=5,
             label="measured (slope 1.999)")
    c.loglog(taus, amp[0] * (taus / taus[0]) ** 2, ":", color="#455a64",
             label="$\\tau^2$ law")
    c.loglog(taus, np.maximum(eta0, 1e-18), "s--", color="#2e7d32", ms=3,
             lw=1.0, label="switch-offs ($\\eta{=}0$, $\\xi{=}0$,\n"
             "$s_i{=}s_j$, level set): machine zero")
    c.set_ylim(1e-18, 3)
    c.set_xlabel("$\\tau$ (s)"); c.set_ylabel("$\\|\\log\\mathrm{Hol}\\|$")
    c.set_title("result: verified to coefficient precision", fontsize=8.5)
    c.legend(fontsize=6.0, loc="lower right", framealpha=0.9)
    save(fig, "lcss_graphical_abstract")


if __name__ == "__main__":
    fig_loop_filmstrip()
    fig_transit_scene()
    fig_amplitude_carpet()
    fig_commutator_landscape()
    fig_graphical_abstract()
    print("L-CSS scenario figures done")
