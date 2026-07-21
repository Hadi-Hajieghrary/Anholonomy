"""D7 addendum: the A2 (un-conjugated transport) arm on the 50-transit dogleg —
closes the 'A2-inclusive rule head-to-head in the transit setting' gap."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json
from concurrent.futures import ProcessPoolExecutor
from tier2_drake.campaign.d7_scorecard import one, ARMS

ARMS["A2"] = {"fuse_rule": "A2"}

if __name__ == "__main__":
    grid = [("A2", s) for s in range(50)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, grid, chunksize=2))
    ok = [r for r in rows if "err" not in r]
    json.dump(rows, open("/workspaces/Anholonomy/tier2_drake/results/s1/d7_a2_arm.json", "w"), indent=1)
    import numpy as np
    v = ok
    print(f"{len(ok)}/50 ok")
    print(f"A2: anchored {np.mean([r['pa'] for r in v]):.3f}  mean {np.mean([r['pm'] for r in v]):.3f}  "
          f"max {np.mean([r['px'] for r in v]):.3f}  D {np.mean([r['D'] for r in v]):.3e}  "
          f"ANEES {np.mean([r['anees'] for r in v]):.1f}  drift {np.mean([r['drift'] for r in v]):.1f}")
