"""Hero v2: decelerating approach — the docking-spec sufficiency test.
decel ramps thrust to 28% over [395, 415]; tow slows 0.9 -> ~0.25 m/s; the
last ~30 m take ~110 s of anchored time (~5 tau_net)."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier2_drake.blind_harbor.s1 import CFG, run_seed
import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv

V2 = dict(CFG, Tend=520.0, tau=0.31, dogleg=(200.0, 60.0, np.pi/3),
          t_on=410.0, eval_from=500.0, decel=(395.0, 20.0, 0.28),
          mxi_freeze=(390.0, 425.0))

def one(seed):
    out = run_seed(V2, seed)
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = V2["N"]
    ks = np.where(ts >= V2["eval_from"])[0]
    pa = pm = px = ye = 0.0
    for k in ks:
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        e = [Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true)) for i in range(N)]
        pa += np.linalg.norm(e[0][:2]); pm += np.mean([np.linalg.norm(x[:2]) for x in e])
        px += max(np.linalg.norm(x[:2]) for x in e)
        ye += np.degrees(max(abs(x[2]) for x in e))
    n = len(ks)
    return dict(seed=seed, pa=pa/n, pm=pm/n, px=px/n, yaw=ye/n)

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=6) as ex:
        rows = list(ex.map(one, range(12)))
    json.dump(rows, open("/workspaces/Anholonomy/tier2_drake/results/s1/hero_v2_ensemble.json", "w"), indent=1)
    pa = [r["pa"] for r in rows]; pm = [r["pm"] for r in rows]; px = [r["px"] for r in rows]
    print("seed  anch[m]  mean[m]  max[m]  yaw[deg]")
    for r in rows:
        print(f"{r['seed']:3d}  {r['pa']:.3f}   {r['pm']:.3f}   {r['px']:.3f}   {r['yaw']:.2f}")
    print(f"success <0.5 m: anchored {np.mean([x < 0.5 for x in pa]):.0%}  "
          f"fleet-mean {np.mean([x < 0.5 for x in pm]):.0%}  fleet-max {np.mean([x < 0.5 for x in px]):.0%}")
