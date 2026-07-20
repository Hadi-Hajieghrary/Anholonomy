"""Matched-config coefficient ratio, Tier-1 side — REFERENCE-matched (plan §6 v1).
Drake's REALIZED maneuvering shapes exit the reduced model's stable domain
[measured: sigma_i windup at sin(sigma_i-sigma)=0.88 > eta*l/v]; the ratio is
therefore evaluated at matched REFERENCES: operating fan = half the Drake default
front-arc (the declared E3b compression), l=12, v=0.9, drake_maneuver eta,
DC=0.1 (Drake's send epoch), tau=0.4, Tend=90 (same eval fraction)."""
import sys; sys.path.insert(0, "/workspaces/Anholonomy")
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from tier1_sheaf.experiments.e3b_floor import run

S0 = np.stack([0.5 * np.linspace(-1.15, 1.15, 5)] * 2, axis=1)  # (sigma, sigma_i=sigma)

def one(args):
    seed, turn = args
    D = run(0.4, 0, seed, eta_profile="drake_maneuver" if turn else "straight",
            l=12.0, v_ref=0.9, s0_override=S0, dc=0.1, Tend=90.0)
    return dict(seed=seed, turn=turn, D=D)

if __name__ == "__main__":
    grid = [(s, True) for s in range(25)] + [(s, False) for s in range(25)]
    with ProcessPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(one, grid))
    turn = [r["D"] for r in res if r["turn"]]
    stra = [r["D"] for r in res if not r["turn"]]
    print(f"T1 turn D:     {np.mean(turn):.4e}")
    print(f"T1 straight D: {np.mean(stra):.4e}")
    print(f"T1 excess:     {np.mean(turn)-np.mean(stra):.4e}")
    dk = json.load(open("/workspaces/Anholonomy/tier2_drake/results/s1/matched_drake.json"))
    ex2 = np.mean(dk["turn"]) - np.mean(dk["straight"])
    rng = np.random.default_rng(21); ratios = []
    for _ in range(4000):
        e1 = np.mean(rng.choice(turn, 25)) - np.mean(rng.choice(stra, 25))
        e2 = np.mean(rng.choice(dk["turn"], 25)) - np.mean(rng.choice(dk["straight"], 25))
        if e1 > 0 and e2 > 0:
            ratios.append(e1 / e2)
    lo, med, hi = np.percentile(ratios, [2.5, 50, 97.5])
    inside = lo >= 1/1.3 and hi <= 1.3
    print(f"coefficient ratio T1/Drake: {med:.2f} [{lo:.2f}, {hi:.2f}]  "
          f"band [1/1.3, 1.3]: {'AGREE' if inside else 'ESCAPES (finding -> localization ladder)'}")
    json.dump(dict(t1_turn=turn, t1_straight=stra, ratio=[lo, med, hi]),
              open("/workspaces/Anholonomy/tier2_drake/results/s1/matched_t1.json", "w"), indent=1)
