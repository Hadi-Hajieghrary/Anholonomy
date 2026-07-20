"""The gauge kernel H^0(F_Sigma) = se(2) and gauge-safe alignment  [ES §5].

Thm 5.1:  ker L_F (load blocks) = { (Ad_{m(s_j)}^{-1} c)_j : c in se(2) } ~= se(2).
The harmonic sections are one common load-frame perturbation c seen from each
body frame. Accuracy metrics must be reported modulo this 3-dim gauge, on a
window disjoint from the alignment window (guards alignment leakage, plan R-iv).
"""
from __future__ import annotations

import numpy as np

from ..core.se2 import Log, Ad, inv
from ..core.shapes import m_of, DEFAULT_L

__all__ = ["kernel_basis", "gauge_align_firstorder", "log_errors"]


def kernel_basis(shapes, l: float = DEFAULT_L) -> np.ndarray:
    """The 3N x 3 basis of the gauge kernel: column c gives (Ad_{m(s_j)}^{-1} c)_j.

    Thm 5.1's harmonic sections. L_F @ kernel_basis == 0 to machine precision.
    """
    N = len(shapes)
    B = np.zeros((3 * N, 3))
    for j, (sig, sigi) in enumerate(shapes):
        Aj_inv = np.linalg.inv(Ad(m_of(sig, sigi, l)))
        B[3 * j:3 * j + 3, :] = Aj_inv
    return B


def log_errors(Ghat_list, Gtruth) -> np.ndarray:
    """Stacked per-agent log-errors Log(Ghat_j @ Gtruth^{-1}), shape (N, 3)."""
    Gi = inv(Gtruth)
    return np.array([Log(Gh @ Gi) for Gh in Ghat_list])


def gauge_align_firstorder(Ghat_list, Gtruth) -> np.ndarray:
    """First-order gauge alignment: the common shift h minimizing the residual.

    Returns the aligned log-errors e_j - mean_j(e_j). The mean is the least-squares
    first-order estimate of the common gauge c; the residual lives on the gauge
    complement V (Thm 5.1). Exact SE(2) alignment (an argmin over h) is a later
    refinement; to first order in the errors the two coincide.
    """
    e = log_errors(Ghat_list, Gtruth)
    return e - e.mean(axis=0)
