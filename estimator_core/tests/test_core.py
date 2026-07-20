"""estimator_core skeleton tests — plan §3.1's mandated regressions.

The two load-bearing ones:
  * FROZEN-SHAPE EXACTNESS: paper rule + frozen shapes + noise-free odometry
    ⇒ fusion residual machine zero (pins the executed Tier-1 null).
  * ZERO DRAKE IMPORTS: the package-level invariant.
"""
import sys
import numpy as np
import pytest

import estimator_core as ec
from tier1_sheaf.core.se2 import Exp, Log, inv, Ad
from tier1_sheaf.core.shapes import Ad_m, m_of

L = 12.0     # production cable length — l is required everywhere, no default


def test_no_drake_imports():
    # process-global sys.modules is polluted when tier2 tests share the session;
    # the invariant is that importing estimator_core ITSELF pulls no Drake -> subprocess
    import subprocess
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, estimator_core; "
         "sys.exit(1 if any(m.startswith('pydrake') for m in sys.modules) else 0)"],
        cwd="/workspaces/Anholonomy", capture_output=True)
    assert r.returncode == 0, "importing estimator_core pulled in pydrake"


def test_packet_roundtrip():
    st = ec.FilterState.initial([0.4, 0.3], L)
    st.P[2, 4] = st.P[4, 2] = 3e-3
    v = ec.pack(1.25, 3, st, radial=(np.array([0.1, 0.2, 0.3]), 0.7))
    stamp, sender, G, P, s, b, rho, mxi, valid = ec.unpack(v)
    assert stamp == 1.25 and sender == 3 and valid
    assert np.allclose(G, st.G) and np.allclose(P, st.P) and np.allclose(s, st.s)
    assert np.allclose(b, [0.1, 0.2, 0.3]) and rho == 0.7


def test_propagate_tracks_truth_noise_free():
    # constant twist, exact odometry, correct shape -> G tracks the true load pose
    s = np.array([0.4, 0.3])
    xi_true = np.array([0.4, 0.0, 0.1])
    zeta = np.linalg.inv(Ad_m(s[0], s[1], L)) @ xi_true      # full body twist (incl. sway)
    st = ec.FilterState.initial(s, L)
    G_true = np.eye(3)
    dt = 0.02
    for _ in range(500):                                     # 10 s
        st = ec.propagate(st, zeta, dt, shape_motion_correction=False)
        G_true = G_true @ Exp(dt * xi_true)
    assert np.linalg.norm(Log(inv(st.G) @ G_true)) < 1e-9


def test_frozen_shape_exactness_null():
    """Paper rule + frozen shapes: neighbor twist reconstructed exactly => r ≈ 0.

    Pins the executed Tier-1 null (D_ss ~ 1e-29). Two agents, frozen shapes,
    no noise: after identical propagation, the conjugated fast-forward makes the
    fusion residual vanish to machine precision.
    """
    sA, sB = np.array([0.4, 0.3]), np.array([0.9, -0.5])
    xi = np.array([0.4, 0.0, 0.12])
    zA = np.linalg.inv(Ad_m(*sA, L)) @ xi
    zB = np.linalg.inv(Ad_m(*sB, L)) @ xi
    stA = ec.FilterState.initial(sA, L)
    stB = ec.FilterState.initial(sB, L)
    dt, age = 0.02, 0.4
    hist_B = []
    for k in range(100):
        hist_B.append(stB.copy())
        stA = ec.propagate(stA, zA, dt, shape_motion_correction=False)
        stB = ec.propagate(stB, zB, dt, shape_motion_correction=False)
    stale = hist_B[100 - int(age / dt)]                      # B's state aged by `age`
    _, rec = ec.fuse_paper(stA, stale.G, stale.s, age, zA,
                           alpha=0.1, w=1.0, sender=1)
    assert np.linalg.norm(rec.residual) < 1e-12, \
        f"frozen-shape null violated: |r| = {np.linalg.norm(rec.residual):.2e}"


def test_fusion_record_transport_is_receiver_load_twist():
    # executed-composite rule: transport = age * Ad_{m(s_self)} zeta_self = age * xi_self
    # (the sender's shape telescopes out -- see fuse.py docstring)
    st = ec.FilterState.initial([0.4, 0.3], L)
    s_nb = np.array([0.9, -0.5])
    zeta = np.array([0.3, 0.0, 0.05])
    age = 0.25
    _, rec = ec.fuse_paper(st, np.eye(3), s_nb, age, zeta, 0.1, 1.0, 0)
    assert np.allclose(rec.transport_log, age * (Ad_m(*st.s, L) @ zeta))
    assert rec.realized_age == pytest.approx(age)


def test_update_direction_pulls_sigma_i():
    st = ec.FilterState.initial([0.4, 0.3], L)
    st2 = ec.update_direction(st, sigma_i_meas=0.35, kappa=400.0)
    assert 0.3 < st2.s[1] < 0.35                # moved toward the measurement
    assert st2.P[4, 4] < st.P[4, 4]             # variance shrank
    # broadside guard: near sigma_i = pi/2 the gain collapses
    stb = ec.FilterState.initial([0.4, np.pi / 2 - 0.01], L)
    stb2 = ec.update_direction(stb, sigma_i_meas=np.pi / 2 - 0.06, kappa=400.0)
    assert abs(stb2.s[1] - stb.s[1]) < 0.2 * abs(st2.s[1] - st.s[1]) + 1e-12


def test_a2_signature_pin():
    """A2 (un-conjugated) shows the FIRST-ORDER per-edge defect at frozen shapes
    where `paper` shows machine zero — the label-inversion vaccine (plan §3.1)."""
    from estimator_core.rules import fuse_with_rule
    sA, sB = np.array([0.4, 0.3]), np.array([0.9, -0.5])
    xi = np.array([0.4, 0.0, 0.12])
    zA = np.linalg.inv(Ad_m(*sA, L)) @ xi
    zB = np.linalg.inv(Ad_m(*sB, L)) @ xi
    stA = ec.FilterState.initial(sA, L)
    stB = ec.FilterState.initial(sB, L)
    dt, age = 0.02, 0.1
    hist_B = []
    for _ in range(50):
        hist_B.append(stB.copy())
        stA = ec.propagate(stA, zA, dt, shape_motion_correction=False)
        stB = ec.propagate(stB, zB, dt, shape_motion_correction=False)
    stale = hist_B[50 - int(age / dt)]
    _, rec_p = fuse_with_rule("paper", stA, stale.G, stale.s, age, zA, 0.1, 1.0, 1)
    _, rec_a2 = fuse_with_rule("A2", stA, stale.G, stale.s, age, zA, 0.1, 1.0, 1)
    assert np.linalg.norm(rec_p.residual) < 1e-12                 # paper: exact
    r2 = np.linalg.norm(rec_a2.residual)
    pred = age * np.linalg.norm(zA - xi)                          # first-order defect
    assert r2 > 1e-3, "A2 must show a defect at frozen shapes"
    assert abs(r2 / pred - 1.0) < 0.2, f"A2 defect {r2:.4f} vs first-order {pred:.4f}"


def test_ci_fuse_is_conservative_and_shrinks():
    from estimator_core.ci import ci_fuse_G
    st = ec.FilterState.initial([0.4, 0.3], L)
    P_nb_G = 2.0 * np.eye(3) * 1e-4
    P_new, omega = ci_fuse_G(st.P, P_nb_G, realized_age=0.4)
    assert 0.0 < omega < 1.0
    assert (np.linalg.eigvalsh(P_new[:3, :3]) > 0).all()
    # the CI guarantee: Pf <= P_own/omega in the PSD sense (consistency bound)
    assert (np.linalg.eigvalsh(st.P[:3, :3] / omega - P_new[:3, :3]) > -1e-12).all()
    # a strictly better partner DOES shrink the fused covariance below own:
    P_good = 0.1 * st.P[:3, :3]
    P_shrunk, _ = ci_fuse_G(st.P, P_good, realized_age=0.0)
    assert np.trace(P_shrunk[:3, :3]) < np.trace(st.P[:3, :3])



def test_corrected_model_tracks_reduced_plant():
    """PATH-A ACCEPTANCE: with the shape-motion + lever correction, the estimator
    tracks the Tier-1 REDUCED PLANT (shapes genuinely evolving, persistent turn,
    noise off) to integration error — the model and the plant share the same
    kinematics, so the deterministic mismatch vanishes IN-MODEL."""
    from tier1_sheaf.plant.reduced import ReducedConfig, ReducedPlant
    from tier1_sheaf.core.se2 import Log, inv
    # straight tow: the z-channel of a single dead-reckoner is recursive (no
    # instantaneous eta source without fusion/beacon — documented in propagate);
    # the correction's claim is TRANSLATION mismatch removal, tested here.
    s0 = np.array([[0.4, 0.3], [0.9, -0.5], [-0.7, 0.6]])
    plant = ReducedPlant(ReducedConfig(N=3, l=L, noise_on=False,
                                       eta_profile="straight"), s0, seed=0)
    st = ec.FilterState.initial(s0[0], L)
    while plant.t < 30.0 - 1e-9:
        zeta = plant.body_twists()[0]
        # 50 Hz estimator vs 100 Hz plant: two plant steps per propagate
        plant.step(); plant.step()
        st = ec.propagate(st, zeta, 0.02)
    e = Log(inv(st.G) @ plant.G)
    # fidelity floor: one-step-lag/ZOH residual ≈ 2% of the correction ⇒
    # < 0.007 m/s of persistent shape motion at |σ̇| ~ 0.02, l = 12 (measured)
    assert np.linalg.norm(e[:2]) < 0.007 * 30.0, f"corrected model drifts: {e}"
    # and the UNcorrected model must do measurably worse on the same run
    plant2 = ReducedPlant(ReducedConfig(N=3, l=L, noise_on=False,
                                        eta_profile="straight"), s0, seed=0)
    st2 = ec.FilterState.initial(s0[0], L)
    while plant2.t < 30.0 - 1e-9:
        zeta = plant2.body_twists()[0]
        plant2.step(); plant2.step()
        st2 = ec.propagate(st2, zeta, 0.02, shape_motion_correction=False)
    e2 = Log(inv(st2.G) @ plant2.G)
    assert np.linalg.norm(e2[:2]) > 2 * np.linalg.norm(e[:2]),         f"correction shows no benefit: {np.linalg.norm(e[:2])} vs {np.linalg.norm(e2[:2])}"
