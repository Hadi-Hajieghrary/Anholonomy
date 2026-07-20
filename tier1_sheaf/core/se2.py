"""SE(2) / se(2) Lie-group machinery — NumPy reference backend.

Conventions (fixed, verified against the project's SymPy manifest [ES §11], V3):
  * Group element g = (R(alpha), t) is the 3x3 homogeneous matrix
        [[cos a, -sin a, t_x],
         [sin a,  cos a, t_y],
         [    0,      0,    1]].
  * Algebra element xi = (v_x, v_y, omega) in R^3 maps to
        hat(xi) = [[0, -omega, v_x],
                   [omega, 0,   v_y],
                   [0,     0,     0]].
  * Adjoint:  Ad_{(R(a),t)} = [[R(a), J t], [0, 1]] with  J t = (t_y, -t_x).
    (V3 of the manifest: derived by conjugation; this sign is load-bearing and
     matches pilot_e3.py and verify_sheaf.py.)
  * ad_xi for xi=(v_x,v_y,omega):  [[0,-omega,v_y],[omega,0,-v_x],[0,0,0]].
    (V6 special case ad_{(v,0,eta)} = [[0,-eta,0],[eta,0,-v],[0,0,0]].)

The Exp/Log closed forms are lifted verbatim from pilot_e3.py, which is
mutually consistent with the symbolic manifest and is the one piece of the
existing code the audit found correct.
"""
from __future__ import annotations

import numpy as np

__all__ = [
    "hat", "vee", "SE2", "Exp", "Log", "Ad", "ad", "inv", "compose",
    "SMALL_ANGLE",
]

# Below this |omega| the series-limit (rotation -> identity) branch is used.
SMALL_ANGLE = 1e-9


def hat(xi) -> np.ndarray:
    """se(2) vector (v_x, v_y, omega) -> 3x3 matrix in the Lie algebra."""
    v = np.asarray(xi, dtype=float)
    return np.array([[0.0, -v[2], v[0]],
                     [v[2], 0.0, v[1]],
                     [0.0, 0.0, 0.0]])


def vee(M) -> np.ndarray:
    """Inverse of hat: 3x3 algebra matrix -> (v_x, v_y, omega)."""
    M = np.asarray(M, dtype=float)
    return np.array([M[0, 2], M[1, 2], M[1, 0]])


def SE2(alpha: float, t) -> np.ndarray:
    """Group element from angle alpha and translation t=(t_x, t_y)."""
    c, s = np.cos(alpha), np.sin(alpha)
    M = np.eye(3)
    M[:2, :2] = [[c, -s], [s, c]]
    M[:2, 2] = t
    return M


def Exp(xi) -> np.ndarray:
    """Group exponential se(2) -> SE(2). Closed form (pilot_e3.py, verified)."""
    xi = np.asarray(xi, dtype=float)
    v = xi[:2]
    w = xi[2]
    if abs(w) < SMALL_ANGLE:
        Rm = np.eye(2)
        Vv = v
    else:
        c, s = np.cos(w), np.sin(w)
        Rm = np.array([[c, -s], [s, c]])
        V = np.array([[s, c - 1.0], [1.0 - c, s]]) / w
        Vv = V @ v
    M = np.eye(3)
    M[:2, :2] = Rm
    M[:2, 2] = Vv
    return M


def Log(M) -> np.ndarray:
    """Group logarithm SE(2) -> se(2). Closed form (pilot_e3.py, verified)."""
    M = np.asarray(M, dtype=float)
    w = np.arctan2(M[1, 0], M[0, 0])
    v = M[:2, 2]
    if abs(w) < SMALL_ANGLE:
        p = v
    else:
        c, s = np.cos(w), np.sin(w)
        V = np.array([[s, c - 1.0], [1.0 - c, s]]) / w
        p = np.linalg.solve(V, v)
    return np.array([p[0], p[1], w])


def Ad(M) -> np.ndarray:
    """Adjoint representation of a group element on se(2) (3x3).

    Ad_{(R,t)} = [[R, J t], [0, 1]],  J t = (t_y, -t_x).  (V3)
    """
    M = np.asarray(M, dtype=float)
    Rm = M[:2, :2]
    t = M[:2, 2]
    A = np.eye(3)
    A[:2, :2] = Rm
    A[0, 2] = t[1]      # +t_y
    A[1, 2] = -t[0]     # -t_x
    return A


def ad(xi) -> np.ndarray:
    """Adjoint action of the algebra: ad_xi (3x3), xi=(v_x,v_y,omega).

    ad_xi = [[0, -omega, v_y], [omega, 0, -v_x], [0, 0, 0]].
    Verified: ad_xi @ zeta == vee([hat(xi), hat(zeta)]).
    """
    v = np.asarray(xi, dtype=float)
    return np.array([[0.0, -v[2], v[1]],
                     [v[2], 0.0, -v[0]],
                     [0.0, 0.0, 0.0]])


def inv(M) -> np.ndarray:
    """Inverse of an SE(2) element (via structure, not general solve)."""
    M = np.asarray(M, dtype=float)
    Rm = M[:2, :2]
    t = M[:2, 2]
    Mi = np.eye(3)
    Mi[:2, :2] = Rm.T
    Mi[:2, 2] = -Rm.T @ t
    return Mi


def compose(*mats) -> np.ndarray:
    """Left-to-right group product of SE(2) elements."""
    out = np.eye(3)
    for M in mats:
        out = out @ np.asarray(M, dtype=float)
    return out
