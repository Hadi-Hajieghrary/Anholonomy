"""D7 — the BHT scorecard (plan §5.4): 50 dogleg transits per arm.
Arms (all in-loop, parity-safe): DIEKF-paper (record) | B0 dead-reckon |
B2 naive consensus | B1-limit (record architecture at tau=0.01, complete graph
— the measured centralization oracle; re-architected centralized filters and
the B3 relative-pose baseline are design-incomplete and excluded, WIP-logged).
Metrics at dock (t in [430, 450]): est-error anchored agent / fleet mean /
fleet max, heading max, D, anchored ANEES, pre-anchor drift."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
import estimator_core as ec
from tier1_sheaf.core.se2 import SE2, Log, inv
from tier2_drake.blind_harbor.s1 import CFG, run_seed

DOGLEG = dict(CFG, Tend=450.0, tau=0.31, dogleg=(200.0, 60.0, np.pi/3),
              t_on=410.0, eval_from=430.0)
ARMS = {"paper": {}, "B0": {"fuse_rule": "off"}, "B2": {"fuse_rule": "A1"},
        "B1lim": {"tau": 0.01, "topology": "complete"}}

def one(args):
    arm, seed = args
    cfg = dict(DOGLEG, **ARMS[arm])
    try:
        out = run_seed(cfg, seed)
    except Exception as e:
        return dict(arm=arm, seed=seed, err=str(e)[:80])
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = cfg["N"]
    ks = np.where(ts >= cfg["eval_from"])[0]
    pa = pm = px = ye = D = an = 0.0
    for k in ks:
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        e = [Log(ests[i][k][ec.SL_G].reshape(3, 3) @ inv(G_true)) for i in range(N)]
        pa += np.linalg.norm(e[0][:2]); pm += np.mean([np.linalg.norm(x[:2]) for x in e])
        px += max(np.linalg.norm(x[:2]) for x in e)
        ye += np.degrees(max(abs(x[2]) for x in e))
        D += np.mean([np.sum((e[i] - e[j]) ** 2) for i in range(N) for j in range(i+1, N)])
        P0 = ec.unvech(ests[0][k][ec.SL_P])[:3, :3]
        an += float(e[0] @ np.linalg.solve(P0, e[0])) / 3.0
    n = len(ks)
    dr = []
    for k in np.where((ts >= 0.6 * cfg["t_on"]) & (ts < cfg["t_on"]))[0][::10]:
        G_true = SE2(tq[k, 2], tq[k, 0:2])
        dr.append(np.mean([np.linalg.norm(Log(ests[i][k][ec.SL_G].reshape(3, 3)
                                              @ inv(G_true))[:2]) for i in range(N)]))
    return dict(arm=arm, seed=seed, pa=pa/n, pm=pm/n, px=px/n, yaw=ye/n,
                D=D/n, anees=an/n, drift=float(np.mean(dr)))

if __name__ == "__main__":
    grid = [(a, s) for a in ARMS for s in range(50)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, grid, chunksize=2))
    ok = [r for r in rows if "err" not in r]
    json.dump(rows, open("/workspaces/Anholonomy/tier2_drake/results/s1/d7_scorecard.json", "w"), indent=1)
    print(f"{len(ok)}/{len(grid)} ok")
    print("arm    anchored[m] mean[m]  max[m]   yaw[deg]  D          ANEES   drift[m]  dock<0.5(anch)")
    for a in ARMS:
        v = [r for r in ok if r["arm"] == a]
        if not v: continue
        succ = np.mean([r["pa"] < 0.5 for r in v])
        print(f"{a:6s} {np.mean([r['pa'] for r in v]):8.3f} {np.mean([r['pm'] for r in v]):8.3f} "
              f"{np.mean([r['px'] for r in v]):8.3f} {np.mean([r['yaw'] for r in v]):7.2f}  "
              f"{np.mean([r['D'] for r in v]):.3e}  {np.mean([r['anees'] for r in v]):6.2f}  "
              f"{np.mean([r['drift'] for r in v]):7.2f}   {succ:.0%}")
    print("written d7_scorecard.json")
