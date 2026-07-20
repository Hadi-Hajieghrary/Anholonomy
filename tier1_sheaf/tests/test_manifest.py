"""V1-V6 as REAL regression tests (verify_sheaf.py had zero asserts).

Numeric anchors reproduced this session from verify_sheaf.py; if the mathematics
or a convention drifts, one of these fails loudly instead of exiting 0.
"""
import numpy as np
import sympy as sp
import pytest

from tier1_sheaf.symbolic import manifest as M
from tier1_sheaf.core.shapes import m_of, conjugated_generator, commutator
from tier1_sheaf.sheaf.laplacian import sheaf_laplacian, lambda2, kernel_dim
from tier1_sheaf.sheaf.gauge import kernel_basis


# ---------------- symbolic manifest ----------------
def test_v1_trivialization_constraints_vanish():
    residuals = M.v1_trivialization_constraints()
    assert all(r == 0 for r in residuals), residuals


def test_v2_edge_maps_gauge_independent():
    assert M.v2_edge_map_gauge_independence() is True


def test_v3_adjoint_formula():
    _, matches = M.v3_adjoint_formula()
    assert matches is True


def test_v5_bch_leading_commutator():
    assert M.v5_bch_leading_commutator() is True


def test_v6_symmetry_protection_and_generic():
    r = M.v6_conjugated_generator_defect()
    assert r["symmetry_protected"] is True
    # generic ||[C_i,C_j]|| = 0.24090... at the manifest probe point
    assert r["generic_norm"] == pytest.approx(0.24090492419921994, rel=1e-9)
    # ad_{(v,0,eta)} = [[0,-eta,0],[eta,0,-v],[0,0,0]]
    v_, e_ = sp.symbols('v eta', real=True)
    expected = sp.Matrix([[0, -e_, 0], [e_, 0, -v_], [0, 0, 0]])
    assert sp.simplify(r["ad_matrix"] - expected) == sp.zeros(3, 3)


# ---------------- V4: numeric sheaf-Laplacian spectrum ----------------
# V4 uses the harmonic convention to reproduce [ES]'s published numbers exactly
# (verify_sheaf.py:92). The library default is `series` (Def 4.1); see Q6a.
L0 = 1.0
_BASE = [(0.4, 0.3), (0.9, -0.5), (-0.7, 0.6)]
_TRI_EDGES = [(0, 1), (1, 2), (2, 0)]


def test_v4a_psd_and_kernel_dim_three():
    L, _, _ = sheaf_laplacian(_BASE, _TRI_EDGES, weights=[1.0, 1.0, 1.0], l=L0)
    ev = np.linalg.eigvalsh(L)
    assert (ev > -1e-10).all(), "L_F not PSD"
    assert kernel_dim(L) == 3


def test_v4a_gauge_section_annihilated():
    # ker L_F = { Ad_{m(s_j)}^{-1} c } (Thm 5.1): L_F @ kernel_basis == 0
    L, _, _ = sheaf_laplacian(_BASE, _TRI_EDGES, weights=[1.0, 1.0, 1.0], l=L0)
    B = kernel_basis(_BASE, l=L0)
    assert np.linalg.norm(L @ B) < 1e-12


def test_v4b_lambda2_broadside_collapse():
    # lambda_2: 2.170 -> 0.084 as sigma_i2 -> pi/2 (Cor 5.3), harmonic weights
    endpoints = {}
    for t in (0.0, 1.5):
        shapes = [(0.4, 0.3), (0.9, t), (-0.7, 0.6)]
        L, _, _ = sheaf_laplacian(shapes, _TRI_EDGES, convention="harmonic", l=L0)
        endpoints[t] = lambda2(L)
    assert endpoints[0.0] == pytest.approx(2.170123, abs=1e-4)
    assert endpoints[1.5] == pytest.approx(0.084224, abs=1e-4)
    assert endpoints[1.5] < 0.2 * endpoints[0.0]   # genuine collapse


def test_v4b_lambda2_monotone_toward_broadside():
    vals = []
    for t in (0.0, 0.5, 1.0, 1.3, 1.5):
        shapes = [(0.4, 0.3), (0.9, t), (-0.7, 0.6)]
        L, _, _ = sheaf_laplacian(shapes, _TRI_EDGES, convention="harmonic", l=L0)
        vals.append(lambda2(L))
    assert all(x > y for x, y in zip(vals, vals[1:])), vals


def test_v4c_lambda2_distinct_across_shapes_fixed_weights():
    # geometric (Ad) twist alone moves lambda_2 at fixed weights W = I
    LA, _, _ = sheaf_laplacian(_BASE, _TRI_EDGES, weights=[1, 1, 1], l=L0)
    LB, _, _ = sheaf_laplacian([(1.4, 0.3), (0.9, -0.5), (-0.7, 0.6)],
                               _TRI_EDGES, weights=[1, 1, 1], l=L0)
    a, b = lambda2(LA), lambda2(LB)
    assert a == pytest.approx(1.157524, abs=1e-4)
    assert b == pytest.approx(1.162567, abs=1e-4)
    assert not np.isclose(a, b)


# ---------------- holonomy / symmetry (cross-check core vs symbolic) ----------------
def test_symmetry_protection_numeric_matches_symbolic():
    xi = np.array([1.0, 0.0, 0.2])
    same = commutator(conjugated_generator(0.4, 0.3, xi),
                      conjugated_generator(0.4, 0.3, xi))
    assert np.linalg.norm(same) < 1e-12
    generic = commutator(conjugated_generator(0.4, 0.3, xi),
                         conjugated_generator(0.9, -0.5, xi))
    assert np.linalg.norm(generic) == pytest.approx(0.24090492419921994, rel=1e-9)
