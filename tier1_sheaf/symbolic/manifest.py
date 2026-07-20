"""SymPy verification manifest V1-V6  [ES §11].

This absorbs verify_sheaf.py, with the defect the audit named fixed: the original
had ZERO asserts and always exited 0, so it verified nothing. Here each V-item is
a function returning a structured, testable result; tests/test_manifest.py asserts
them. Symbolic items (V1, V2, V3, V5, V6-sym) are exact; V4 is numeric linear
algebra (eigvalsh) and is labeled as such — the manifest's own "SymPy" wording
overclaims the three spectral checks (audit ES-04/05), so we keep the honest tag.

Ground-truth values (reproduced this session):
  V1: five residuals == 0                  V2: True
  V3: Ad = [[R, Jt],[0,1]], Jt=(t_y,-t_x)  V4a: dim ker 3, ||L x_gauge|| = 6.6e-16
  V4b: lambda_2 2.170 -> 0.084 (broadside) V4c: 1.157524 vs 1.162567 (distinct)
  V5: eps^2 coeff == [X,Y]                 V6: [C_i,C_j]|_{s_i=s_j}=0, generic 0.2409
"""
from __future__ import annotations

import numpy as np
import sympy as sp


# ---- symbolic SE(2) (kept independent of the numeric core, on purpose) ----
def _SE2(th, x, y):
    c, s = sp.cos(th), sp.sin(th)
    return sp.Matrix([[c, -s, x], [s, c, y], [0, 0, 1]])


def _hat(v):
    return sp.Matrix([[0, -v[2], v[0]], [v[2], 0, v[1]], [0, 0, 0]])


def _vee(M):
    return sp.Matrix([M[0, 2], M[1, 2], M[1, 0]])


def _Ad(g):
    cols = []
    for e in [sp.Matrix([1, 0, 0]), sp.Matrix([0, 1, 0]), sp.Matrix([0, 0, 1])]:
        cols.append(_vee(sp.simplify(g * _hat(e) * g.inv())))
    return sp.simplify(sp.Matrix.hstack(*cols))


def _m_of(sig, sigi, ll):
    return _SE2(sig - sigi, ll * sp.cos(sig), ll * sp.sin(sig))


def v1_trivialization_constraints():
    """V1: g_boat = g_L m(s) satisfies the three constraint identities. Returns list of residuals (all sp.Integer(0))."""
    th, x, y, l = sp.symbols('theta x y l', real=True)
    sg, sgi = sp.symbols('sigma sigma_i', real=True)
    gL = _SE2(th, x, y)
    gb = sp.simplify(gL * _m_of(sg, sgi, l))
    px, py = gb[0, 2], gb[1, 2]
    c1 = sp.simplify((px - x) ** 2 + (py - y) ** 2 - l ** 2)
    c2 = sp.simplify(px - x - l * sp.cos(th + sg))
    c3 = sp.simplify(py - y - l * sp.sin(th + sg))
    c4 = sp.simplify(gb[0, 0] - sp.cos(th + sg - sgi))
    c5 = sp.simplify(gb[1, 0] - sp.sin(th + sg - sgi))
    return [c1, c2, c3, c4, c5]


def v2_edge_map_gauge_independence():
    """V2: g_i^{-1} g_j == m_i^{-1} m_j (independent of g_L). Returns bool."""
    th, x, y, l = sp.symbols('theta x y l', real=True)
    sg, sgi, sg2, sgi2 = sp.symbols('sigma sigma_i sigma2 sigma_i2', real=True)
    gL = _SE2(th, x, y)
    m1, m2 = _m_of(sg, sgi, l), _m_of(sg2, sgi2, l)
    diff = sp.simplify((gL * m1).inv() * (gL * m2) - m1.inv() * m2)
    return diff == sp.zeros(3, 3)


def v3_adjoint_formula():
    """V3: Ad_{(R(a),t)} closed form. Returns (sympy matrix, bool matches [[R,Jt],[0,1]] with Jt=(t_y,-t_x))."""
    a, tx, ty = sp.symbols('alpha t_x t_y', real=True)
    Adg = _Ad(_SE2(a, tx, ty))
    expected = sp.Matrix([[sp.cos(a), -sp.sin(a), ty],
                          [sp.sin(a), sp.cos(a), -tx],
                          [0, 0, 1]])
    return Adg, sp.simplify(Adg - expected) == sp.zeros(3, 3)


def v5_bch_leading_commutator():
    """V5: eps^2 coefficient of log(e^X e^Y e^-X e^-Y) == [X, Y] on se(2). Returns bool."""
    eps = sp.symbols('varepsilon')
    Xa = _hat(sp.Matrix(sp.symbols('a1 a2 a3', real=True)))
    Yb = _hat(sp.Matrix(sp.symbols('b1 b2 b3', real=True)))

    def expm_series(M, order=4):
        S = sp.eye(3)
        T = sp.eye(3)
        for k in range(1, order + 1):
            T = T * M / k
            S = S + T
        return S

    G = sp.expand(expm_series(eps * Xa) * expm_series(eps * Yb) *
                  expm_series(-eps * Xa) * expm_series(-eps * Yb))
    Z = G - sp.eye(3)
    logG = sp.expand(Z - Z * Z / 2 + Z * Z * Z / 3)
    lead = sp.expand(logG).applyfunc(lambda e: sp.expand(e).coeff(eps, 2))
    return sp.simplify(lead - (Xa * Yb - Yb * Xa)) == sp.zeros(3, 3)


def v6_conjugated_generator_defect():
    """V6: ad matrix, symmetry protection, generic non-vanishing.

    Returns dict: ad_matrix (sympy), symmetry_protected (bool),
    generic_norm (float, ~0.2409 at the manifest's probe point).
    """
    v_, e_ = sp.symbols('v eta', real=True)
    sg, sgi, sg2, sgi2 = sp.symbols('sigma sigma_i sigma2 sigma_i2', real=True)
    X0 = _hat(sp.Matrix([v_, 0, e_]))
    adchk = [_vee(X0 * _hat(e) - _hat(e) * X0)
             for e in [sp.Matrix([1, 0, 0]), sp.Matrix([0, 1, 0]), sp.Matrix([0, 0, 1])]]
    adM = sp.simplify(sp.Matrix.hstack(*adchk))
    C1 = sp.simplify(_Ad(_m_of(sg, sgi, sp.Integer(1))) * adM * _Ad(_m_of(sg, sgi, sp.Integer(1))).inv())
    C2 = sp.simplify(_Ad(_m_of(sg2, sgi2, sp.Integer(1))) * adM * _Ad(_m_of(sg2, sgi2, sp.Integer(1))).inv())
    comm = sp.simplify(C1 * C2 - C2 * C1)
    same = sp.simplify(comm.subs({sg2: sg, sgi2: sgi}))
    protected = same == sp.zeros(3, 3)
    val = comm.subs({sg: 0.4, sgi: 0.3, sg2: 0.9, sgi2: -0.5, v_: 1.0, e_: 0.2})
    return {"ad_matrix": adM, "symmetry_protected": protected,
            "generic_norm": float(sp.Matrix(val).norm())}
