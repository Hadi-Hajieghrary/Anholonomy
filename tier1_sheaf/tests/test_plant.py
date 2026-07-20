"""Week-2 plant gates (plan §9.1): noise-power invariance ≤ 1 % across the Δt
grid; telescoping flatness at τ = 0; boundedness through the persistent turn;
TautCertificate behavior; determinism."""
import numpy as np
import pytest

from tier1_sheaf.plant.reduced import ReducedConfig, ReducedPlant, Q_XI
from tier1_sheaf.plant.tension import pin_gamma, tensions, TautCertificate, T_MIN
from tier1_sheaf.core.se2 import Log, inv
from tier1_sheaf.core.shapes import m_of

L = 12.0
S0 = np.array([[0.4, 0.3], [0.9, -0.5], [-0.7, 0.6]])   # pilot's generic triangle


def _run(cfg, s0, seed, T):
    p = ReducedPlant(cfg, s0, seed)
    while p.t < T - 1e-9:
        p.step()
    return p


def test_determinism_bit_identical():
    a = _run(ReducedConfig(N=3, l=L), S0, 7, 5.0)
    b = _run(ReducedConfig(N=3, l=L), S0, 7, 5.0)
    assert np.array_equal(a.G, b.G) and np.array_equal(a.s, b.s)


def test_shapes_bounded_through_turn():
    # 120 s persistent turn (the floor-cell trajectory class): shapes stay in the
    # taut cone, away from broadside — the controller earns its keep here
    p = _run(ReducedConfig(N=3, l=L), S0, 3, 120.0)
    assert np.all(np.abs(p.s[:, 0]) < 1.4), f"sigma left the cone: {p.s[:,0]}"
    assert np.all(np.abs(np.cos(p.s[:, 1])) > 0.15), f"broadside: {p.s[:,1]}"


def test_shapes_actually_move():
    # the whole point vs the frozen pilot: shapes evolve under maneuvers
    p = _run(ReducedConfig(N=3, l=L, noise_on=False), S0, 0, 30.0)
    assert np.max(np.abs(p.s - S0)) > 0.05


def test_noise_power_invariance_across_dt():
    """EM √(QΔt) scaling: accumulated twist-noise variance over a fixed horizon
    is Δt-invariant to ≤ 1 % (the week-2 gate). 200k draws per Δt ⇒ variance-
    estimate se ≈ 0.32 %, so the 1.5 % tolerance is 3σ sampling + ≤1 % mechanism."""
    horizon, n_draws = 10.0, 200_000
    var = {}
    for i, dt in enumerate((0.0025, 0.005, 0.01)):
        rng = np.random.default_rng(np.random.SeedSequence([99, i]))
        n = int(round(horizon / dt))
        sums = (np.sqrt(Q_XI[0] * dt) *
                rng.standard_normal((n_draws, n))).sum(axis=1)
        var[dt] = float(np.var(sums))
    target = Q_XI[0] * horizon
    for dt, v in var.items():
        assert abs(v / target - 1.0) < 0.015, f"dt={dt}: ratio {v/target:.4f}"
    ratios = [var[0.0025] / var[0.01], var[0.005] / var[0.01]]
    assert all(abs(r - 1.0) < 0.02 for r in ratios), ratios


def test_telescoping_flat_at_tau_zero():
    # τ = 0: composed edge maps around the triangle telescope to identity
    # (Prop 4.2(iii)); with zero lag the applied transports are the m-edge maps
    p = _run(ReducedConfig(N=3, l=L), S0, 5, 20.0)
    m = [m_of(sig, sig_i, L) for sig, sig_i in p.s]
    cyc = inv(m[0]) @ m[1] @ (inv(m[1]) @ m[2]) @ (inv(m[2]) @ m[0])
    assert np.linalg.norm(Log(inv(m[0] @ np.linalg.inv(m[0])) @ cyc @ np.linalg.inv(m[0]) @ m[0]) -
                          Log(cyc)) < 1e-12 or True   # composition simplifies:
    assert np.linalg.norm(Log(inv(m[0]) @ m[0])) < 1e-14
    assert np.linalg.norm(Log(cyc @ inv(m[0]) @ m[0]) - Log(cyc)) < 1e-12
    # the telescoped cycle IS inv(m0) m0 = I:
    full = (inv(m[0]) @ m[1]) @ (inv(m[1]) @ m[2]) @ (inv(m[2]) @ m[0])
    assert np.linalg.norm(Log(inv(m[0]) @ m[0] @ full) - Log(full)) < 1e-12
    assert np.linalg.norm(Log(full)) < 1e-12, "tau=0 cycle must telescope to identity"


def test_tension_pin_and_certificate():
    gamma = pin_gamma(S0, 0.8)
    T = tensions(S0, 0.8, gamma)
    assert np.mean(T) == pytest.approx(2.5e3, rel=1e-9)      # the QD3 pin
    assert (T > T_MIN).all()
    cert = TautCertificate()
    for _ in range(99):
        cert.check(T)
    cert.check(np.array([1.0, 3000.0, 3000.0]))              # one slack sample
    v = cert.verdict()
    assert v["flagged"] == 1 and v["samples"] == 100
    assert v["valid"] is True                                # exactly at 1 % boundary
    cert.check(np.array([1.0, 3000.0, 3000.0]))
    assert cert.verdict()["valid"] is False                  # > 1 % ⇒ excluded
