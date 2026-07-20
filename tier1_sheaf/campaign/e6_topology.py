"""T1-E6 — multi-topology (plan §4.4; C10 CONJ/open, EXPLORATORY — no falsifier).
Topologies x N in {4,6,8} (never N=3), tau sweep per topology; D_ss coefficient
vs lambda_2(L). rgg deferred (needs a positions model); captioned exploratory."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier1_sheaf.experiments.e3b_floor import run

def edges_of(topo, N):
    if topo == "cycle":
        return [(j, (j + 1) % N) for j in range(N)]
    if topo == "path":
        return [(j, j + 1) for j in range(N - 1)]
    if topo == "star":
        return [(0, j) for j in range(1, N)]
    return [(i, j) for i in range(N) for j in range(i + 1, N)]   # complete

def lam2(topo, N):
    E = edges_of(topo, N)
    L = np.zeros((N, N))
    for i, j in E:
        L[i, i] += 1; L[j, j] += 1; L[i, j] -= 1; L[j, i] -= 1
    return float(np.sort(np.linalg.eigvalsh(L))[1])

TOPOS = ["cycle", "path", "star", "complete"]
NS = [4, 6, 8]
TAUS = [0.2, 0.8]

def cell(args):
    topo, N, tau, seed = args
    D = run(tau, seed % 12, seed, Tend=90.0, N=N, edges=edges_of(topo, N))
    return (topo, N, tau, seed, D)

GRID = [(t, n, tau, s) for t in TOPOS for n in NS for tau in TAUS for s in range(8)]

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(cell, GRID, chunksize=4))
    pool = {}
    for topo, N, tau, s, D in res:
        pool.setdefault((topo, N, tau), []).append(D)
    out = {}
    print("topo      N  lam2   D(0.2)      D(0.8)     ratio")
    for topo in TOPOS:
        for N in NS:
            l2 = lam2(topo, N)
            d2 = np.mean(pool[(topo, N, 0.2)]); d8 = np.mean(pool[(topo, N, 0.8)])
            out[f"{topo}_{N}"] = dict(lambda2=l2, D02=float(d2), D08=float(d8))
            print(f"{topo:9s} {N}  {l2:.3f}  {d2:.4e}  {d8:.4e}  {d8/d2:.2f}")
    # coefficient vs lambda2 (log-log association, exploratory)
    xs = [np.log(v["lambda2"]) for v in out.values()]
    ys = [np.log(v["D08"]) for v in out.values()]
    sl = np.polyfit(xs, ys, 1)[0]
    out["_slope_logD08_vs_loglam2"] = float(sl)
    print(f"exploratory association: d log D(0.8) / d log lambda2 = {sl:.2f}")
    json.dump(out, open("/workspaces/Anholonomy/tier1_sheaf/results/e6_topology.json", "w"),
              indent=1)
    print("written e6_topology.json")
