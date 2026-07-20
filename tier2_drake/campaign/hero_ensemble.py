"""Dogleg hero ensemble: median-D_ss seed selection (plan §7.1 rule, v1 = 12 seeds).
v1 disclosed deltas: fixed tau=0.31 s (no jitter/drops yet); beacon acquired at ~58 m (t_on=385 s, ~3 network diffusion constants) — v1
extended-range delta; the 30 m rule with a decelerating approach profile is v2."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier2_drake.blind_harbor.s1 import CFG, run_seed
import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv

HERO_CFG = dict(CFG, Tend=450.0, tau=0.31, dogleg=(200.0, 60.0, np.pi/3),
                t_on=385.0, eval_from=430.0)

def one(seed):
    out = run_seed(HERO_CFG, seed)
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = HERO_CFG["N"]
    ks = np.where((ts >= 100.0) & (ts <= 400.0))[0]
    D = np.mean([np.mean([np.sum(Log(inv(ests[i][k][ec.SL_G].reshape(3,3)) @
                                      ests[j][k][ec.SL_G].reshape(3,3))**2)
                          for i in range(N) for j in range(i+1, N)]) for k in ks[::10]])
    # docking scorecard at the end
    kf = np.where(ts >= HERO_CFG["eval_from"])[0]
    G_true_f = SE2(tq[kf[-1], 2], tq[kf[-1], 0:2])
    errs = [np.linalg.norm(Log(ests[i][kf[-1]][ec.SL_G].reshape(3,3) @ inv(G_true_f))[:2])
            for i in range(N)]
    yaw_errs = [abs(Log(ests[i][kf[-1]][ec.SL_G].reshape(3,3) @ inv(G_true_f))[2])
                for i in range(N)]
    return dict(seed=seed, D=float(D), dock_pos_max=float(max(errs)),
                dock_yaw_max_deg=float(np.degrees(max(yaw_errs))))

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(one, range(12)))
    for r in res:
        print(f"seed {r['seed']:2d}: D={r['D']:.4e}  dock_pos={r['dock_pos_max']:.3f} m  "
              f"dock_yaw={r['dock_yaw_max_deg']:.2f} deg")
    Ds = sorted(res, key=lambda r: r["D"])
    hero = Ds[len(Ds)//2]
    print(f"MEDIAN-D hero seed: {hero['seed']}  (D={hero['D']:.4e})")
    json.dump(dict(rule="ensemble median D_ss over [100,400] s, 12-seed v1 subset",
                   hero_seed=hero["seed"], ensemble=res),
              open("/workspaces/Anholonomy/tier2_drake/results/s1/hero_ensemble.json", "w"),
              indent=1)
