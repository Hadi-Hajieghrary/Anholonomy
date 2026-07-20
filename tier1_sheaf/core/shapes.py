"""Constraint trivialization m(s) and the conjugated error-transport generator.

From [ES §3] (Lemma 3.1, 3.2) and [ES §7]:
  * Trivialization:   m(sigma, sigma_i) = ( R(sigma - sigma_i),  l*(cos sigma, sin sigma) ).
    World pose factors as g_boat = g_L * m(s)   (Lemma 3.1),
    and edge maps g_i^{-1} g_j = m_i^{-1} m_j are g_L-independent (Lemma 3.2).
  * Conjugated generator (the object Thm 7.2's holonomy is built from):
        C_j(s_j; xi) = Ad_{m(s_j)} @ ad_xi @ Ad_{m(s_j)}^{-1},
    where xi is the common load twist. This is the frozen transport generator of
    agent j's load block ([ES §7], estimation_sheaf.tex:175-180).

NOTE (channel-shape naming). A per-agent shape is the pair
    s_j = (sigma^{(j)}, sigma^{(j)}_j)
i.e. (cable direction in the load frame, cable direction in the boat frame).
We denote them (sigma, sigma_i) to match the source LaTeX, where `sigma_i` is the
boat-frame angle (the subscript is the source's, not an agent index).
"""
from __future__ import annotations

import numpy as np

from .se2 import SE2, Ad, ad

__all__ = ["m_of", "Ad_m", "conjugated_generator", "commutator"]

# Default cable length. The audit (Q6/§4.3) established that spectral quantities
# are l-dependent; experiments run at l = 12 m (sim_design.tex:24), while the
# original SymPy manifest used l = 1. Callers must pass l explicitly for anything
# that feeds a paper number; this default exists only for unit-level algebra.
DEFAULT_L = 1.0


def m_of(sigma: float, sigma_i: float, l: float = DEFAULT_L) -> np.ndarray:
    """Constraint trivialization m(sigma, sigma_i) in SE(2)  (Lemma 3.1)."""
    return SE2(sigma - sigma_i, [l * np.cos(sigma), l * np.sin(sigma)])


def Ad_m(sigma: float, sigma_i: float, l: float = DEFAULT_L) -> np.ndarray:
    """Adjoint of the trivialization, Ad_{m(s)}  (the sheaf restriction core)."""
    return Ad(m_of(sigma, sigma_i, l))


def conjugated_generator(sigma: float, sigma_i: float, xi, l: float = DEFAULT_L) -> np.ndarray:
    """C_j(s_j; xi) = Ad_{m} ad_xi Ad_{m}^{-1}   ([ES §7]).

    xi is the common load twist (v_x, v_y, omega).
    """
    A = Ad_m(sigma, sigma_i, l)
    return A @ ad(xi) @ np.linalg.inv(A)


def commutator(A, B) -> np.ndarray:
    """Matrix commutator [A, B] = AB - BA."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    return A @ B - B @ A
