"""E1 — the gauge theorem and pinning collapse (Thm 5.1, Cor 5.2).

Thm 5.1 [thm:gauge]: ker L_F (load blocks) = { Ad_{m(s_j)}^{-1} c : c in se(2) } ~= se(2),
so the decentralized problem is observable exactly modulo one global SE(2) gauge (dim 3).
Cor 5.2 [cor:pin]: a single absolute-pose anchor gives one vertex a full-rank potential,
ker -> 0, and lambda_min becomes the relevant rate.

This uses the sheaf Laplacian directly (no estimator needed): assemble L_F for a triangle,
exhibit dim ker = 3 and that the kernel IS the gauge-section space, then add an anchor block
to one vertex and watch the kernel collapse.

Metric note (fixes sim_design.tex:70 / plan §7.2): the gauge is 3-dimensional in R^{3N},
NOT a per-agent rank-3 object — a per-agent stack of 3-vectors has at most 3 singular values,
so "sigma_4/sigma_3" is not computable that way. The kernel dimension of L_F on R^{3N} is the
right, computable quantity.
"""
from __future__ import annotations

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier1_sheaf.sheaf.laplacian import sheaf_laplacian, kernel_dim, lambda2
from tier1_sheaf.sheaf.gauge import kernel_basis

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results")
os.makedirs(OUT, exist_ok=True)

SHAPES = [(0.4, 0.3), (0.9, -0.5), (-0.7, 0.6)]
EDGES = [(0, 1), (1, 2), (2, 0)]
L0 = 1.0
KTOL = 1e-9


def pin(L, agent, strength):
    """Add a full-rank anchor potential to one vertex block (Cor 5.2)."""
    Lp = L.copy()
    b = 3 * agent
    Lp[b:b + 3, b:b + 3] += strength * np.eye(3)
    return Lp


def main():
    L, _, _ = sheaf_laplacian(SHAPES, EDGES, weights=[1.0, 1.0, 1.0], l=L0)
    ev = np.sort(np.linalg.eigvalsh(L))

    # Thm 5.1: kernel is exactly the gauge sections
    B = kernel_basis(SHAPES, l=L0)
    gauge_residual = np.linalg.norm(L @ B)
    kdim = kernel_dim(L, KTOL)

    print("=== E1: gauge theorem (Thm 5.1) + pinning (Cor 5.2) ===")
    print(f"  unpinned eigenvalues: {np.round(ev, 6)}")
    print(f"  dim ker L_F          = {kdim}   (claim 3 = se(2) gauge)")
    print(f"  ||L_F @ gauge_basis|| = {gauge_residual:.2e}   (claim 0: kernel IS the gauge)")
    assert kdim == 3, "gauge theorem failed: kernel is not 3-dimensional"
    assert gauge_residual < 1e-12, "kernel is not the gauge-section space"

    # Cor 5.2: pin one agent, sweep anchor strength, watch ker collapse
    strengths = np.array([0.0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0])
    rows = []
    print("\n  pinning agent 0 (Cor 5.2):")
    print(f"  {'strength':>10} {'dim ker':>8} {'lambda_min':>12}")
    lam2_unpinned = lambda2(L, KTOL)
    for s in strengths:
        Lp = pin(L, 0, s) if s > 0 else L
        evp = np.sort(np.linalg.eigvalsh(Lp))
        kd = int((np.abs(evp) < KTOL).sum())
        lmin = float(evp[evp > KTOL][0]) if kd < 9 else 0.0
        # after pinning, the smallest nonzero eigenvalue is lambda_min (Cor 5.2)
        lmin_full = float(evp[0]) if kd == 0 else lmin
        rows.append((s, kd, lmin_full))
        print(f"  {s:>10.4g} {kd:>8} {lmin_full:>12.6f}")

    with open(os.path.join(OUT, "e1_gauge.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anchor_strength", "dim_ker", "lambda_min"])
        w.writerows(rows)

    # figure F3: kernel dimension and lambda_min vs anchor strength
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2))
    ss = np.array([r[0] for r in rows])
    kd = np.array([r[1] for r in rows])
    lm = np.array([r[2] for r in rows])
    xs = np.where(ss == 0, strengths[strengths > 0].min() / 10, ss)
    ax1.semilogx(xs, kd, "o-", color="#b2182b", lw=2, ms=6)
    ax1.axhline(3, ls=":", color="gray", label="unpinned gauge dim = 3")
    ax1.axhline(0, ls=":", color="green")
    ax1.set_xlabel("anchor strength"); ax1.set_ylabel(r"$\dim\ker L_\mathcal{F}$")
    ax1.set_title("Cor 5.2: one anchor collapses the gauge", fontsize=9.5)
    ax1.set_yticks([0, 1, 2, 3]); ax1.legend(fontsize=8); ax1.grid(alpha=0.25)
    ax2.loglog(xs, np.clip(lm, 1e-6, None), "s-", color="#2166ac", lw=2, ms=6)
    ax2.axhline(lam2_unpinned, ls=":", color="gray", label=r"unpinned $\lambda_2$")
    ax2.set_xlabel("anchor strength"); ax2.set_ylabel(r"$\lambda_{\min}(L_\mathcal{F}^{\rm pinned})$")
    ax2.set_title(r"$\lambda_{\min}$ becomes the rate", fontsize=9.5)
    ax2.legend(fontsize=8); ax2.grid(alpha=0.25, which="both")
    fig.suptitle("F3 — E1: gauge structure (Thm 5.1) and pinning collapse (Cor 5.2)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "e1_gauge.png"), dpi=150, bbox_inches="tight")
    print(f"\nwrote {OUT}/e1_gauge.csv and e1_gauge.png")


if __name__ == "__main__":
    main()
