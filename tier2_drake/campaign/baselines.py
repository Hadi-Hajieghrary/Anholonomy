"""Baseline comparison table (C18: the sheaf/compensation structure is load-bearing)."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, os
import numpy as np
from tier2_drake.blind_harbor.s1 import CFG, run_seed, anees_and_disagreement

ARMS = [
    ("DIEKF-paper (record)", dict(CFG)),
    ("B0 dead-reckon", dict(CFG, fuse_rule="off")),
    ("B2 naive consensus (=A1)", dict(CFG, fuse_rule="A1")),
    ("B1-proxy all-anchored tau_min", dict(CFG, tau=0.01, all_beacons=True)),
]
rows = []
for name, cfg in ARMS:
    per = []
    for seed in range(3):
        out = run_seed(cfg, seed)
        a, c, D, dr = anees_and_disagreement(cfg, out)
        per.append((a, c, D, dr))
    per = np.array(per)
    rows.append(dict(arm=name, anchored=float(per[:,0].mean()),
                     perp=float(per[:,1].mean()), D=float(per[:,2].mean()),
                     drift=float(per[:,3].mean())))
    print(f"{name:32s} anchored={per[:,0].mean():8.3f}  D={per[:,2].mean():.3e}  "
          f"drift={per[:,3].mean():5.2f} m")
out_path = "/workspaces/Anholonomy/tier2_drake/results/s1/baselines.json"
json.dump(rows, open(out_path, "w"), indent=1)
print("written", out_path)
