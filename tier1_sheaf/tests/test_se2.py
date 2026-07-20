"""SE(2)/se(2) core axioms — the numeric backend must satisfy the group laws."""
import numpy as np
import pytest

from tier1_sheaf.core.se2 import hat, vee, SE2, Exp, Log, Ad, ad, inv, compose

RNG = np.random.default_rng(0)


def _rand_xi(scale=1.0):
    return RNG.uniform(-scale, scale, 3)


def test_hat_vee_roundtrip():
    for _ in range(50):
        xi = _rand_xi()
        assert np.allclose(vee(hat(xi)), xi)


def test_exp_log_roundtrip():
    # away from the omega = pi wrap, Log(Exp(xi)) == xi
    for _ in range(200):
        xi = _rand_xi(scale=2.5)
        assert np.allclose(Log(Exp(xi)), xi, atol=1e-10)


def test_log_exp_roundtrip_on_group():
    for _ in range(200):
        alpha = RNG.uniform(-3.0, 3.0)
        t = RNG.uniform(-5, 5, 2)
        g = SE2(alpha, t)
        assert np.allclose(Exp(Log(g)), g, atol=1e-10)


def test_inv_is_group_inverse():
    for _ in range(100):
        g = Exp(_rand_xi(2.0))
        assert np.allclose(g @ inv(g), np.eye(3), atol=1e-12)
        assert np.allclose(inv(g) @ g, np.eye(3), atol=1e-12)


def test_ad_is_homomorphism():
    # Ad(g h) == Ad(g) Ad(h)
    for _ in range(100):
        g, h = Exp(_rand_xi(2.0)), Exp(_rand_xi(2.0))
        assert np.allclose(Ad(g @ h), Ad(g) @ Ad(h), atol=1e-10)


def test_ad_conjugation_identity():
    # Ad(g) @ vee(X) == vee(g hat(X) g^{-1}): the defining property of Ad
    for _ in range(100):
        g = Exp(_rand_xi(2.0))
        xi = _rand_xi()
        lhs = Ad(g) @ xi
        rhs = vee(g @ hat(xi) @ inv(g))
        assert np.allclose(lhs, rhs, atol=1e-10)


def test_ad_bracket_matches_matrix_commutator():
    # ad(xi) @ zeta == vee([hat(xi), hat(zeta)])
    for _ in range(100):
        xi, zeta = _rand_xi(), _rand_xi()
        lhs = ad(xi) @ zeta
        rhs = vee(hat(xi) @ hat(zeta) - hat(zeta) @ hat(xi))
        assert np.allclose(lhs, rhs, atol=1e-12)


def test_ad_sign_convention_Jt():
    # V3: Ad_{(R(a),t)} = [[R, Jt],[0,1]] with Jt = (t_y, -t_x)
    alpha, tx, ty = 0.7, 1.3, -0.4
    A = Ad(SE2(alpha, [tx, ty]))
    assert np.isclose(A[0, 2], ty)    # +t_y
    assert np.isclose(A[1, 2], -tx)   # -t_x


def test_small_angle_branch_continuity():
    # Exp/Log must be continuous through omega -> 0
    xi = np.array([0.3, -0.2, 1e-11])
    assert np.allclose(Log(Exp(xi)), xi, atol=1e-9)
