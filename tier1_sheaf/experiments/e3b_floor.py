"""T1-E3b — dynamic D_ss floor with MOVING shapes (plan §4.2; C7b, CONJ, F4b).

The decisive Tier-1 cell: the executed frozen-shape null (e3_diagnostic) proved a
static-shape run measures nothing (D_ss ~ 1e-29), so shape motion is mandatory.
This harness runs the SAME estimator_core DIEKF-Sigma as the Drake leaf — identical
tick order (consume -> propagate 50 Hz -> update 20 Hz), identical fusion API
(fuse_with_rule + ci_fuse_G), identical sensor spec (plan §3.4) — on the reduced
plant integrating the shape ODEs along the persistent-turn reference.

Estimator config = the Drake record EXACTLY, including
shape_motion_correction=False: the Path-A correction is validated on straight tow
only (test_corrected_model_tracks_reduced_plant) — its eta-channel is recursive
(no instantaneous eta source without beacon) and under the persistent turn that
recursion is unstable [measured: 1e32 blowup]. Running the identical estimator
config on both plants removes every config delta from the cross-tier overlay.

Formation draw law = the Drake production law mapped into shape coordinates
(sigma_j = attachment-ray angle over +/-front_arc with perturb; sigma_i,j = 0,
vessels start cable-aligned) — the same draws serve the capstone matched config.
Metric = Drake floor_metrics verbatim: all-pairs mean ||Log(G_i^-1 G_j)||^2 on the
last 30%.

Arms: paper (primary) | A1 | A2 | off, x frozen_shapes (regression to the executed
null) x eta profile (persistent_turn primary, straight = D0 control).

SCOPE (dated 2026-07-19): the spec's A3-weights and oosm_augmented arms and the
symmetric/near-symmetric/zero_commutator formation kinds are NOT in this block —
they feed C9/C15, not the C7b falsifier, and follow in the E3c/E6 drivers. The
metric is an inline copy verified equal to Drake floor_metrics (all-pairs form);
factoring into a shared analysis/metrics.py is queued with the capstone.
"""
from __future__ import annotations

import numpy as np

import estimator_core as ec
from tier1_sheaf.core.se2 import Log, inv
from tier1_sheaf.plant.reduced import ReducedConfig, ReducedPlant
from tier2_drake.blind_harbor.sensors import KAPPA_DIR

DC = 0.05                     # send epoch = QD5 shipping default: tau grid
                              # {0.05..1.6} exact with lag in {1..32} >= 1
KAPPA_GAIN = 2.0              # alpha = kappa * Dc, the record gain


def draw_formation(form_id: int, N: int = 5):
    """Drake production draw law in shape coordinates."""
    rng = np.random.default_rng(form_id)
    front_arc = float(rng.uniform(0.7, 1.3))
    perturb = float(rng.uniform(-0.15, 0.15))
    # E3b draw law [DESIGN, declared]: HALF the Drake attachment-ray arc.
    # Drake's rays are where cables ATTACH; the operating fan compresses forward
    # at steady tow. Full-arc shapes put the outermost vessel within noise-walk
    # distance of the broadside singularity cos(sigma_i)=0 and the truth plant
    # blows up [measured]. The capstone matched config maps measured operating
    # shapes, not rays, so this delta does not break the cross-tier mapping.
    angles = 0.5 * np.linspace(-front_arc, front_arc, N) + perturb
    # sigma_i(0) = sigma(0): vessel heading = load heading, the towing
    # equilibrium of the shape ODEs (sigma_i = 0, vessel-along-cable, is ~1 rad
    # from equilibrium for wide fans and winds the truth plant past broadside
    # [measured blowup]). The draw law's ANGLES carry the Drake matching.
    return np.stack([angles, angles.copy()], axis=1)        # (sigma, sigma_i)


class _FrozenShapePlant(ReducedPlant):
    """Frozen-shape regression arm: G moves, shapes do not (the executed null).
    step() re-pins s afterward — the base step adds Q_S shape noise even with
    zero drift, which would silently unfreeze the arm."""

    def _sdot(self, s, v, eta, eta_j):
        return np.zeros_like(s)

    def step(self):
        s_pin = self.s.copy()
        out = super().step()
        self.s = s_pin
        return out


def run(tau: float, form_id: int, seed: int, *, fuse_rule="paper",
        eta_profile="persistent_turn", frozen=False, noise_on=True,
        Tend=120.0, l=1.0, N=5, v_ref=0.8, s0_override=None, dc=None,
        plant_noise=None, jitter_frac=0.0, drop_p=0.0, dt=0.01,
        edges=None):
    # edges: undirected edge list for the comms graph (E6 multi-topology);
    # default None = the C_N cycle. Packets flow both ways on each edge.
    # jitter_frac/drop_p > 0 => the ROBUST arm, explicitly OUTSIDE protocol
    # class P (heterogeneous realized ages; the per-fuse exactness assert is
    # gated off). Captioned per plan 4.3: "outside Thm 7.2's uniform-delay
    # hypothesis; a robustness characterization, not a theorem test." 
    # l=1, v=0.8: the Tier-1 unit-cable convention the pre-registered eta band
    # [0.05, 0.25] was written for — feasibility requires eta <= v/l; Drake's
    # l=12 m geometry would cap eta at 0.075 and the formation winds past
    # broadside [measured blowup]. Angles carry the formation mapping; l only
    # scales the lever, and the capstone mapping rescales explicitly.
    s0 = (np.asarray(s0_override, dtype=float) if s0_override is not None
          else draw_formation(form_id, N))
    DCr = DC if dc is None else float(dc)
    cfg = ReducedConfig(N=N, l=l, dt=dt, v_ref=v_ref,
                        noise_on=(noise_on if plant_noise is None else plant_noise),
                        eta_profile=eta_profile)
    Plant = _FrozenShapePlant if frozen else ReducedPlant
    # plant stream keyed on (seed, form): with seed alone, same-seed runs across
    # formations share one process-noise path and replicates are correlated
    # [audit finding — silently narrows the exponent CI]
    plant = Plant(cfg, s0, int(np.random.SeedSequence([seed, form_id, 3])
                               .generate_state(1)[0] % (2**31)))

    rng = np.random.default_rng(np.random.SeedSequence([seed, form_id, 7]))
    beta = np.array([rng.normal(0.0, 0.01) if noise_on else 0.0 for _ in range(N)])
    gyro_bias = np.zeros(N)

    sts = [ec.FilterState.initial(s0[j].copy(), l) for j in range(N)]
    alpha = KAPPA_GAIN * DCr
    lag = int(round(tau / DCr))
    in_P = (jitter_frac == 0.0 and drop_p == 0.0)
    assert lag >= 1 and abs(lag * DCr - tau) < 1e-9, \
        f"tau={tau} not representable on the DC={DCr} send grid"  # P-class exactness
    if edges is None:
        edges = [(j, (j + 1) % N) for j in range(N)]        # C_N cycle default
    nbrs = [[] for _ in range(N)]
    for a, b in edges:
        nbrs[a].append(b); nbrs[b].append(a)
    ring: list[list] = [[] for _ in range(N)]               # per-agent tx history
    stamps = np.full((N, max(len(x) for x in nbrs)), -1.0)  # newest consumed stamp
    # one-period-stale measurement buffers: the Drake leaf's port Eval reads the
    # PRE-update context, so its propagate consumes the previous 50 Hz odometry
    # sample and its direction update the previous 20 Hz sample [audit] — mirror
    # that freshness here so the cross-tier overlay carries no latency delta
    zeta_meas = [np.zeros(3) for _ in range(N)]             # consumed (stale) sample
    zeta_new = [np.zeros(3) for _ in range(N)]              # freshly sensed sample
    dir_meas = [float(s0[j, 1]) for j in range(N)]
    dir_new = [float(s0[j, 1]) for j in range(N)]

    steps = int(round(Tend / cfg.dt))
    k_eval = int(np.ceil(0.7 * steps))          # integer threshold [audit: float t drift]
    # cadence patterns derived from dt (E10 sweeps dt; all periods must divide)
    k50 = int(round(0.02 / dt)); k20 = int(round(0.05 / dt))
    k20_off = int(round(0.01 / dt))             # +10 ms direction offset [SPEC]
    kdc = int(round(DCr / cfg.dt))
    for name, per, k in (("50Hz", 0.02, k50), ("20Hz", 0.05, k20), ("DC", DCr, kdc)):
        assert abs(k * dt - per) < 1e-12, f"dt={dt} incommensurate with {name}" 
    D_hist = []
    for k in range(steps):
        t = plant.t
        # -- sensors (SPEC §3.4, mirrors tier2 sensors.py) --------------------
        if k % k50 == 0:                                    # 50 Hz odometry
            tw = plant.body_twists()
            for j in range(N):
                z = np.asarray(tw[j], dtype=float).copy()
                if noise_on:
                    gyro_bias[j] += rng.normal(0.0, np.radians(0.01)) * np.sqrt(0.02)
                    z[0] = z[0] * (1.0 + beta[j]) + rng.normal(0.0, 0.01 + 0.02 * abs(z[0]))
                    z[1] = z[1] + rng.normal(0.0, 0.01)
                    z[2] = z[2] + gyro_bias[j] + rng.normal(0.0, np.radians(0.2))
                zeta_meas[j] = zeta_new[j]
                zeta_new[j] = z

        # -- estimator tick, leaf order: consume -> propagate -> update -------
        if k % kdc == 0:                                    # send epoch: snapshot tx
            for j in range(N):
                ring[j].append((t, sts[j].G.copy(), sts[j].s.copy(),
                                sts[j].P[:3, :3].copy()))
            idx = len(ring[0]) - 1 - lag
            if idx >= 0 and fuse_rule != "off":
                for j in range(N):
                    for slot, src in enumerate(nbrs[j]):
                        if drop_p > 0.0 and rng.random() < drop_p:
                            continue                              # erasure at reception
                        idx_j = idx
                        if jitter_frac > 0.0:
                            extra = rng.integers(0, max(int(np.ceil(jitter_frac * lag)), 1) + 1)
                            idx_j = max(idx - int(extra), 0)
                        stamp, G_nb, s_nb, P_nb = ring[src][idx_j]
                        if stamp <= stamps[j, slot]:
                            continue
                        age = t - stamp
                        if in_P:
                            assert abs(age - tau) < 1e-9, \
                                f"realized age {age} != tau {tau}"   # P-class per-fuse assert
                        sts[j], _rec = ec.fuse_with_rule(
                            fuse_rule, sts[j], G_nb, s_nb, age, zeta_meas[j],
                            alpha, 1.0, src)
                        P_new, _ = ec.ci_fuse_G(sts[j].P, P_nb, age)
                        sts[j] = sts[j].replace(P=P_new)
                        stamps[j, slot] = stamp
        if k % k50 == 0:                                    # 50 Hz propagate
            for j in range(N):
                sts[j] = ec.propagate(sts[j], zeta_meas[j], 0.02,
                                      shape_motion_correction=False)
        if k % k20 == k20_off:                              # 20 Hz direction
            for j in range(N):
                sts[j] = ec.update_direction(sts[j], dir_meas[j], KAPPA_DIR)
                dir_meas[j] = dir_new[j]
                dir_new[j] = plant.s[j, 1] + (rng.normal(0.0, 1.0 / np.sqrt(KAPPA_DIR))
                                              if noise_on else 0.0)

        plant.step()
        if k >= k_eval:                                     # M4, last 30%, all pairs
            Gs = [sts[j].G for j in range(N)]
            D_hist.append(np.mean([np.sum(Log(inv(Gs[i]) @ Gs[jj]) ** 2)
                                   for i in range(N) for jj in range(i + 1, N)]))
    return float(np.mean(D_hist))


if __name__ == "__main__":
    import sys
    tau = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4
    for arm in ("paper", "A2", "off"):
        D = run(tau, form_id=0, seed=0, fuse_rule=arm)
        print(f"tau={tau} arm={arm:6s} D_ss={D:.4e}")
    Dfroz = run(tau, 0, 0, fuse_rule="paper", frozen=True, noise_on=False)
    print(f"frozen+noise-off regression: D_ss={Dfroz:.3e} (executed null ~1e-29)")
