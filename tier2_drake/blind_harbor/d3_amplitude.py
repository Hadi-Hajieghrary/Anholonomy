"""D3 — measured error-transport holonomy amplitude in closed loop (the PROV Drake cell).

Q14 resolved to option (i): the theorem's object, measured on Drake closed-loop
states. At each eval-window sample, the conjugated generators
    C_j = Ad_{m(s_hat_j)} ad_xi_hat Ad_{m(s_hat_j)}^{-1}      (l = Drake cable length)
are built from the ESTIMATOR's own logged shape pairs s_hat and load-twist
estimate xi_hat; the m=2 round-trip error-transport holonomy per comms edge is
    Hol(tau) = exp(tau C_i) exp(tau C_j) exp(-tau C_i) exp(-tau C_j).

EPISTEMIC BOUNDARY: ||log Hol|| = O(tau^2) is Thm 7.2's PROVED, deterministic
object. The tau-dependence is analytic once the C's are fixed — the MEASURED
content of this cell is (a) the coefficient ||[C_i, C_j]|| realized by Drake's
closed-loop geometry, (b) the switch-offs (parallel formation -> commutators
vanish; eta = 0 -> vanish), and (c) the O(tau^3) departure at the top of the
grid. Never present the tau^2 slope itself as an independent discovery.

Arms: fan (generic) | parallel (theorem-symmetric, Cor 7.3 switch-off) | eta=0.
"""
import sys, os, json
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
from scipy.linalg import expm, logm

import estimator_core as ec
from estimator_core.state import SL_XIPREV
from tier1_sheaf.core.shapes import conjugated_generator, commutator
from tier2_drake.blind_harbor.s1 import CFG, run_seed

TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
OUT = "/workspaces/Anholonomy/tier2_drake/results/s1/d3_amplitude.json"
MACHINE_ZERO = 1e-14


def edge_curves(cfg, out, *, zero_eta=False):
    """Per-edge amplitude curves ||log Hol(tau)|| and commutator norms, sampled
    over the eval window from the logged estimator states."""
    N = cfg["N"]
    ts, ests = out["ts"], out["ests"]
    l = cfg["l"]
    ks = np.where(ts >= cfg["eval_from"])[0][::5]           # 2 Hz samples suffice
    curves, knorms = [], []
    for k in ks:
        ss = [ests[i][k][ec.SL_S] for i in range(N)]
        xis = [ests[i][k][SL_XIPREV] for i in range(N)]
        for i in range(N):
            j = (i + 1) % N                                  # cycle edges
            xi = 0.5 * (xis[i] + xis[j])
            if zero_eta:
                xi = np.array([xi[0], xi[1], 0.0])
            Ci = conjugated_generator(ss[i][0], ss[i][1], xi, l)
            Cj = conjugated_generator(ss[j][0], ss[j][1], xi, l)
            knorms.append(float(np.linalg.norm(commutator(Ci, Cj))))
            amps = []
            for tau in TAUS:
                H = (expm(tau * Ci) @ expm(tau * Cj)
                     @ expm(-tau * Ci) @ expm(-tau * Cj))
                amps.append(float(np.linalg.norm(logm(H))))
            curves.append(amps)
    return np.array(curves), np.array(knorms)


def fit_slope(amp, taus=None):
    taus = TAUS if taus is None else taus
    good = amp > MACHINE_ZERO
    if good.sum() < 2:
        return float("nan")
    return float(np.polyfit(np.log(taus[good]), np.log(amp[good]), 1)[0])


def main(seeds=3):
    res = {}
    for arm, cfg_over, zeta in (
            ("fan", {}, False),
            ("parallel", {"formation": "parallel"}, False),
            ("fan_eta0", {}, True)):
        cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"),
                   turn_bias=0.03, turn_amp=0.02, **cfg_over)
        all_c, all_k = [], []
        for seed in range(seeds):
            out = run_seed(cfg, seed)
            c, kn = edge_curves(cfg, out, zero_eta=zeta)
            all_c.append(c); all_k.append(kn)
        C = np.concatenate(all_c); K = np.concatenate(all_k)
        mean = C.mean(axis=0)
        res[arm] = dict(
            amp_mean=mean.tolist(),
            amp_p10=np.percentile(C, 10, axis=0).tolist(),
            amp_p90=np.percentile(C, 90, axis=0).tolist(),
            slope=fit_slope(mean),
            slope_low4=fit_slope(mean[:4], TAUS[:4]),       # small-tau regime
            K_mean=float(K.mean()), K_p10=float(np.percentile(K, 10)),
            K_p90=float(np.percentile(K, 90)), n_samples=int(len(K)))
        # leading-order check: amp/tau^2 -> ||K|| as tau -> 0
        res[arm]["coef_ratio_at_min_tau"] = float(
            (mean[0] / TAUS[0] ** 2) / max(K.mean(), 1e-30))
        print(f"{arm:9s} slope={res[arm]['slope']:.3f} (low-tau {res[arm]['slope_low4']:.3f})  "
              f"||K||={K.mean():.4e} [{res[arm]['K_p10']:.1e},{res[arm]['K_p90']:.1e}]  "
              f"coef/||K||@0.05={res[arm]['coef_ratio_at_min_tau']:.4f}  n={len(K)}")
    json.dump(dict(taus=TAUS.tolist(), arms=res), open(OUT, "w"), indent=1)
    print("written", OUT)


if __name__ == "__main__":
    main()
