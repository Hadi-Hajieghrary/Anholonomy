"""The constraint-induced estimation sheaf F_Sigma and its Laplacian  [ES §4].

Restriction map on edge e = (i, j), load block:  rho_{j<|e} = Ad_{m(s_j)} pi_L.
Coboundary:  (delta x)_e = rho_i x_i - rho_j x_j.
Weighted sheaf Laplacian:  L_F = delta^T W delta   (block-assembled).

This absorbs verify_sheaf.py::sheaf_L, with two corrections the audit flagged:
  * WEIGHT CONVENTION (Q6a). Def 4.1 specifies *series information*
    w_e = 1/(1/iota_i + 1/iota_j). verify_sheaf.py computed the *harmonic mean*
    2/(1/iota_i + 1/iota_j) and mislabeled it "series information" — a factor of 2,
    and lambda_2 is linear in w. We default to `series` (the spec) and expose
    `harmonic` to reproduce the published [ES] numbers. The choice is an open
    author decision; do not hard-code paper numbers without stating which.
  * lambda_2 SELECTOR (verify_sheaf.py:94). Taking eigenvalue index [3] as the
    spectral gap is only correct when dim ker == 3 (unpinned). Under pinning the
    kernel shrinks and the index is wrong (audit: "10.5x under pinning"). We
    select by a kernel-dimension tolerance instead.
"""
from __future__ import annotations

import numpy as np

from ..core.se2 import Ad
from ..core.shapes import m_of, DEFAULT_L

__all__ = [
    "channel_information", "edge_weight", "coboundary", "sheaf_laplacian",
    "lambda2", "kernel_dim", "WEIGHT_CONVENTIONS",
]

WEIGHT_CONVENTIONS = ("series", "harmonic", "uniform")
_KER_TOL = 1e-9


def channel_information(sigma: float, sigma_i: float) -> float:
    """Direction-channel Fisher gain iota_j  (up to the undefined constant, Q6b).

    Proportional to cos^2(sigma_i) * sec^4(sigma)  ([OBS]/[IK], verify_sheaf chan_info).
    The proportionality constant is not fixed in any source document (Q6b); this
    returns the shape-dependent factor only. A small floor guards the sec^4 pole.
    """
    return (np.cos(sigma_i) ** 2) / (np.cos(sigma) ** 4 + 1e-12)


def edge_weight(iota_i: float, iota_j: float, convention: str = "series") -> float:
    """Combine two endpoint informations into a scalar edge weight.

    series   = 1 / (1/iota_i + 1/iota_j)        (Def 4.1 — the spec default)
    harmonic = 2 / (1/iota_i + 1/iota_j)        (what verify_sheaf.py used)
    uniform  = 1                                (ablation A3, w_e == 1)
    """
    if convention == "uniform":
        return 1.0
    inv_sum = 1.0 / iota_i + 1.0 / iota_j
    if convention == "series":
        return 1.0 / inv_sum
    if convention == "harmonic":
        return 2.0 / inv_sum
    raise ValueError(f"unknown weight convention {convention!r}; use one of {WEIGHT_CONVENTIONS}")


def _restrictions(shapes, l):
    """Per-vertex restriction cores A_j = Ad_{m(s_j)} for the load block."""
    return [Ad(m_of(sig, sigi, l)) for (sig, sigi) in shapes]


def coboundary(edges, restrictions) -> np.ndarray:
    """Block coboundary delta: R^{3N} -> R^{3|E|}.

    (delta x)_e = A_i x_i - A_j x_j  for e=(i,j).
    """
    N = len(restrictions)
    E = len(edges)
    D = np.zeros((3 * E, 3 * N))
    for k, (i, j) in enumerate(edges):
        D[3 * k:3 * k + 3, 3 * i:3 * i + 3] = restrictions[i]
        D[3 * k:3 * k + 3, 3 * j:3 * j + 3] = -restrictions[j]
    return D


def sheaf_laplacian(shapes, edges, *, weights=None, convention="series",
                    l: float = DEFAULT_L):
    """Assemble L_F = delta^T W delta for a list of per-agent shapes.

    shapes : list of (sigma, sigma_i) pairs, one per agent (vertex).
    edges  : list of (i, j) index pairs (directed representative per undirected edge).
    weights: optional explicit per-edge scalar weights; if None they are computed
             from the channel information under `convention`.
    Returns (L, restrictions, weights).
    """
    restr = _restrictions(shapes, l)
    if weights is None:
        iota = [channel_information(sig, sigi) for (sig, sigi) in shapes]
        weights = [edge_weight(iota[i], iota[j], convention) for (i, j) in edges]
    D = coboundary(edges, restr)
    W = np.zeros((3 * len(edges), 3 * len(edges)))
    for k, w in enumerate(weights):
        W[3 * k:3 * k + 3, 3 * k:3 * k + 3] = w * np.eye(3)
    L = D.T @ W @ D
    # symmetrize against round-off before it reaches an eigensolver
    L = 0.5 * (L + L.T)
    return L, restr, list(weights)


def kernel_dim(L, tol: float = _KER_TOL) -> int:
    """Number of eigenvalues within tol of zero (numerical kernel dimension)."""
    ev = np.linalg.eigvalsh(np.asarray(L, dtype=float))
    return int((np.abs(ev) < tol).sum())


def lambda2(L, tol: float = _KER_TOL) -> float:
    """Spectral gap: smallest eigenvalue above the numerical kernel.

    Selects by kernel-dimension tolerance (not a hard index), so it stays correct
    under pinning where dim ker changes (fixes verify_sheaf.py:94).
    """
    ev = np.sort(np.linalg.eigvalsh(np.asarray(L, dtype=float)))
    above = ev[ev > tol]
    if above.size == 0:
        raise ValueError("no eigenvalue above the kernel tolerance; L may be zero")
    return float(above[0])
