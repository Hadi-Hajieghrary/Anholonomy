"""E3a extension (plan §4.0 items ii, iii, v, vii) — the L-CSS/T-CNS closeout.

(ii)  >=12 formation draws Unif(K)|taut (margin 0.10): amplitude slope per
      formation, cluster spread.
(iii) remainder constant: sup over >=200 shape draws of
      R(tau, s)/tau^3, R = ||Log Hol - tau^2 [C_i, C_j]|| at m=2 (alpha=1).
(v)   C15 zero-commutator formations: pairs with ||[C_i,C_j]|| < 1e-12 but
      shapes >= 1 rad apart; amplitude slope predicted >= 3;
      falsifier: slope CI includes [1.8, 2.2] (failed to separate).
(vii) explicit tau = 0 arm (machine zero by construction, executed as fact).
"""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
import numpy as np
from scipy.linalg import logm
from scipy.optimize import minimize

from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                        error_transport_holonomy_m2,
                                        holonomy_amplitude_m2)

XI = np.array([0.4, 0.0, 0.12])
TAUS = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6])
OUT = "/workspaces/Anholonomy/tier1_sheaf/results/e3a_extension.json"
rng = np.random.default_rng(2026)

def draw_shape(margin=0.10):
    """Unif over the taut-admissible shape box with broadside margin."""
    while True:
        sig = rng.uniform(-1.2, 1.2)
        sig_i = rng.uniform(-1.2, 1.2)
        if abs(np.cos(sig_i)) > margin and abs(np.cos(sig)) > margin:
            return (float(sig), float(sig_i))

res = {}

# (ii) formation-draw cluster: slope per random pair
slopes = []
for f in range(20):
    si, sj = draw_shape(), draw_shape()
    amps = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in TAUS])
    if amps.min() > 1e-14:
        slopes.append(float(np.polyfit(np.log(TAUS), np.log(amps), 1)[0]))
res["formation_cluster"] = dict(n=len(slopes), slopes=slopes,
                                mean=float(np.mean(slopes)),
                                sd=float(np.std(slopes)),
                                lo=float(np.min(slopes)), hi=float(np.max(slopes)))
print(f"(ii) {len(slopes)} formation draws: slope {np.mean(slopes):.4f} "
      f"+/- {np.std(slopes):.4f}  range [{min(slopes):.4f}, {max(slopes):.4f}]")

# (iii) remainder constant over >=200 draws
sups = []
for d in range(220):
    si, sj = draw_shape(), draw_shape()
    K = two_agent_commutator(si, sj, XI)
    per_tau = []
    for t in TAUS[:4]:                       # small-tau regime for the O(tau^3) constant
        H = error_transport_holonomy_m2(si, sj, XI, t)
        R = np.linalg.norm(logm(H) - t ** 2 * K)
        per_tau.append(R / t ** 3)
    sups.append(max(per_tau))
res["remainder_constant"] = dict(n=len(sups), sup=float(np.max(sups)),
                                 p95=float(np.percentile(sups, 95)),
                                 median=float(np.median(sups)))
print(f"(iii) sup_K R/tau^3 over {len(sups)} draws: {np.max(sups):.4f} "
      f"(p95 {np.percentile(sups, 95):.4f}, median {np.median(sups):.4f})")

# (vii) explicit tau = 0 arm
H0 = error_transport_holonomy_m2(draw_shape(), draw_shape(), XI, 0.0)
res["tau0"] = float(np.linalg.norm(logm(H0)))
print(f"(vii) tau=0 arm: ||Log Hol|| = {res['tau0']:.3e} (machine zero)")

# (v) C15 zero-commutator formations: minimize ||[C_i,C_j]|| with separation
def obj(x):
    return np.linalg.norm(two_agent_commutator((x[0], x[1]), (x[2], x[3]), XI))

found = []
for trial in range(200):
    x0 = np.array([draw_shape() + draw_shape()]).ravel()
    r = minimize(obj, x0, method="Nelder-Mead",
                 options=dict(xatol=1e-14, fatol=1e-16, maxiter=4000))
    sep = np.linalg.norm(r.x[:2] - r.x[2:])
    if r.fun < 1e-12 and sep >= 1.0:
        found.append(dict(shapes=r.x.tolist(), comm=float(r.fun), sep=float(sep)))
    if len(found) >= 5:
        break
res["C15_pairs_found"] = len(found)
if found:
    c15 = []
    for p in found:
        si, sj = tuple(p["shapes"][:2]), tuple(p["shapes"][2:])
        amps = np.array([holonomy_amplitude_m2(si, sj, XI, t) for t in TAUS])
        good = amps > 1e-14
        sl = (float(np.polyfit(np.log(TAUS[good]), np.log(amps[good]), 1)[0])
              if good.sum() >= 3 else None)
        c15.append(dict(**p, slope=sl, amps=amps.tolist()))
    res["C15"] = c15
    sls = [c["slope"] for c in c15 if c["slope"] is not None]
    print(f"(v) C15: {len(found)} zero-commutator pairs (sep >= 1 rad); "
          f"amplitude slopes {['%.2f' % s for s in sls]} "
          f"(prediction >= 3; falsifier: CI includes [1.8, 2.2])")
else:
    print("(v) C15: no zero-commutator pairs found at sep >= 1 rad")

json.dump(res, open(OUT, "w"), indent=1)
print("written", OUT)
