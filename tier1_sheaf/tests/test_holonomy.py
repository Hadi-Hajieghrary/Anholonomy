"""E3a regression: the deterministic holonomy amplitude is the theorem's object.

Locks in the decisive facts (Thm 7.2 / Cor 7.3, plan §3 C7a/C8/C9a/C13):
  * generic m=2 amplitude has slope 2 in tau
  * amplitude vanishes identically under symmetry, eta=0, xi=0 (the switch-offs
    the pilot's D_ss FAILED — this is what makes it the theorem's object)
  * at m=2 the coefficient equals ||[C_i,C_j]|| (unit alpha, Q3)
"""
import numpy as np
import pytest

from tier1_sheaf.sheaf.holonomy import holonomy_amplitude_m2, two_agent_commutator

GEN_I, GEN_J = (0.4, 0.3), (0.9, -0.5)
XI = np.array([0.4, 0.0, 0.12])
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8])


def test_generic_amplitude_slope_two():
    amp = np.array([holonomy_amplitude_m2(GEN_I, GEN_J, XI, t) for t in TAUS])
    slope = np.polyfit(np.log(TAUS), np.log(amp), 1)[0]
    assert slope == pytest.approx(2.0, abs=0.05)


def test_symmetry_protection_amplitude_vanishes():
    # Cor 7.3: identical shapes -> [C_i,C_j]=0 -> Hol = I
    for t in TAUS:
        assert holonomy_amplitude_m2((0.5, 0.2), (0.5, 0.2), XI, t) < 1e-12


def test_eta_zero_switchoff_vanishes():
    # [C_i,C_j] proportional to eta: eta=0 kills the amplitude (pilot D_ss did NOT)
    xi_noeta = np.array([0.4, 0.0, 0.0])
    for t in TAUS:
        assert holonomy_amplitude_m2(GEN_I, GEN_J, xi_noeta, t) < 1e-12


def test_xi_zero_switchoff_vanishes():
    xi0 = np.zeros(3)
    for t in TAUS:
        assert holonomy_amplitude_m2(GEN_I, GEN_J, xi0, t) < 1e-12


def test_m2_coefficient_is_commutator_norm():
    # C8 (Q3): ||log Hol||/tau^2 -> ||[C_i,C_j]|| as tau->0, unit coefficient
    tau = 0.02
    amp = holonomy_amplitude_m2(GEN_I, GEN_J, XI, tau)
    comm = np.linalg.norm(two_agent_commutator(GEN_I, GEN_J, XI))
    assert amp / tau**2 == pytest.approx(comm, rel=1e-3)
