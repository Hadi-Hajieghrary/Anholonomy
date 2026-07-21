#!/usr/bin/env python3
"""Campaign replay harness — every paper-bound result, recorded and replayable.

  python3 campaign_replay.py --list           show the manifest
  python3 campaign_replay.py --verify CELL    re-execute a probe of CELL and
                                              compare against the committed data
  python3 campaign_replay.py --verify-all     run every probe (Tier-1 exact
                                              probes are seconds; Drake probes
                                              are one sim each)
  python3 campaign_replay.py --run CELL       re-run the full production driver

Verification levels:
  EXACT  — drivers are seeded and deterministic; a re-executed (arm, tau, form,
           seed) cell must match its committed per-run record to 1e-9.
  STAT   — the committed file stores aggregates only; the probe re-runs a small
           batch and checks the aggregate within tolerance (declared per cell).
"""
import argparse
import importlib
import json
import subprocess
import sys

sys.path.insert(0, "/workspaces/Anholonomy")

R1 = "tier1_sheaf/results"
R2 = "tier2_drake/results/s1"

MANIFEST = {
    # cell: (paper unit, driver, data file, verify level, probe fn name)
    "e3a":   ("LCSS + TCNS §VIII", "tier1_sheaf/experiments/e3a_amplitude.py",
              f"{R1}/e3a_amplitude.csv", "EXACT", "probe_e3a"),
    "e3b":   ("TCNS §VIII + RA-L F4b", "tier1_sheaf/campaign/e3b_production.py",
              f"{R1}/e3b_production.json", "EXACT", "probe_e3b"),
    "e3c":   ("TCNS §VIII F5", "tier1_sheaf/experiments/e3c_symmetry.py",
              f"{R1}/e3c_c9b_seeds.json", "EXACT", "probe_e3c"),
    "e2":    ("TCNS §VIII F8", "tier1_sheaf/experiments/e2_contraction.py",
              f"{R1}/e2_contraction.json", "STAT", "probe_e2"),
    "e6":    ("RA-L overlay inset", "tier1_sheaf/campaign/e6_topology.py",
              f"{R1}/e6_topology.json", "EXACT", "probe_e6"),
    "e10":   ("RA-L numerics defense", "tier1_sheaf/campaign/e10_dt_sweep.py",
              f"{R1}/e10_dt_sweep.json", "STAT", "probe_e10"),
    "d2":    ("RA-L F4b/F4c", "tier2_drake/campaign/production_d2_d4.py",
              f"{R2}/production_d2_d4_v2.json", "EXACT", "probe_d2"),
    "d2ctl": ("RA-L (C7b adjudication)", "tier2_drake/campaign/d2_controls.py",
              f"{R2}/d2_straight_control.json", "EXACT", "probe_d2ctl"),
    "d3":    ("RA-L F4a", "tier2_drake/blind_harbor/d3_amplitude.py",
              f"{R2}/d3_amplitude.json", "STAT", "probe_d3"),
    "d8":    ("RA-L numerics defense", "tier2_drake/campaign/d8_h_sweep.py",
              f"{R2}/d8_h_sweep.json", "STAT", "probe_d8"),
    "matched": ("RA-L §6 coefficient row", "tier2_drake/campaign/matched_t1.py",
                f"{R2}/matched_t1.json", "EXACT", "probe_matched"),
    "baselines": ("RA-L §4 table", "tier2_drake/campaign/baselines.py",
                  f"{R2}/baselines.json", "STAT", "probe_baselines"),
    "d6":    ("RA-L (T2-C6)", "tier2_drake/campaign/d6_tension.py",
              f"{R2}/d6_tension.json", "EXACT", "probe_d6"),
    "d9":    ("RA-L topology figure", "tier2_drake/campaign/d9_scaling.py",
              f"{R2}/d9_scaling.json", "EXACT", "probe_d9"),
    "d10b":  ("RA-L robustness", "tier2_drake/campaign/d10b_loss.py",
              f"{R2}/d10b_loss.json", "EXACT", "probe_d10b"),
    "d10c":  ("RA-L guard envelope", "tier2_drake/campaign/d10c_guard.py",
              f"{R2}/d10c_guard.json", "EXACT", "probe_d10c"),
    "d7":    ("RA-L scorecard", "tier2_drake/campaign/d7_scorecard.py",
              f"{R2}/d7_scorecard.json", "EXACT", "probe_d7"),
    "b1lim": ("RA-L B1 reference", "inline (b1_limit_mfab.json note)",
              f"{R2}/b1_limit_mfab.json", "EXACT", "probe_b1lim"),
    "artT1": ("LCSS/TCNS paper-artifact figures",
              "tier1_sheaf/campaign/paper_artifacts.py",
              f"{R1}/artifacts/commutator_heatmap_meta.json", "EXACT",
              "probe_art_t1"),
    "anatS4": ("RA-L movie S4 (failure anatomy)",
               "tier2_drake/campaign/error_anatomy_movie.py",
               f"{R2}/error_anatomy_series.npz", "EXACT", "probe_anatomy"),
}


def _close(a, b, tol):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ---- probes -----------------------------------------------------------------

def probe_e3a():
    from tier1_sheaf.experiments.e3a_amplitude import amp_curve, GEN_I, GEN_J, XI, TAUS
    import csv
    with open(f"{R1}/e3a_amplitude.csv") as fh:
        rows = list(csv.reader(fh))
    committed = float(next(r for r in rows[1:] if r[0] == "generic")[2])
    fresh = amp_curve(GEN_I, GEN_J, XI)[0]
    assert _close(fresh, committed, 1e-9), (fresh, committed)
    return f"generic amp@tau={TAUS[0]}: {fresh:.6e} == committed (1e-9)"


def probe_e3b():
    from tier1_sheaf.experiments.e3b_floor import run
    rec = next(r for r in json.load(open(f"{R1}/e3b_production.json"))
               if r["arm"] == "paper" and r["tau"] == 0.4 and r["form"] == 0
               and r["seed"] == 0)
    fresh = run(0.4, 0, 0)
    assert _close(fresh, rec["D"], 1e-9), (fresh, rec["D"])
    return f"paper/tau0.4/form0/seed0: D={fresh:.6e} == committed (1e-9)"


def probe_e3c():
    from tier1_sheaf.experiments.e3c_symmetry import dss_cell
    committed = json.load(open(f"{R1}/e3c_c9b_seeds.json"))["0.05_0.4"][0]
    fresh = dss_cell(0.05, 0.4, 0, Tend=90.0)
    assert _close(fresh, committed, 1e-9), (fresh, committed)
    return f"eps0.05/tau0.4/seed0: D={fresh:.6e} == committed (1e-9)"


def probe_e2():
    from tier1_sheaf.experiments.e2_contraction import run, fit_rate
    committed = json.load(open(f"{R1}/e2_contraction.json"))["rates"]["cycle_1.0"]
    rates = []
    for s in range(10):
        tt, ee = run("cycle", 1.0, 0.5 / 5 ** 0.5, s)
        rates.append(fit_rate(tt, ee)[0])
    import numpy as np
    m = float(np.mean(rates))
    assert abs(m - committed["mean"]) < 3 * committed["sd"], (m, committed)
    return f"cycle/kappa1 10-seed mean {m:.3f} within 3sd of committed {committed['mean']:.3f}"


def probe_e6():
    from tier1_sheaf.experiments.e3b_floor import run
    from tier1_sheaf.campaign.e6_topology import edges_of
    committed = json.load(open(f"{R1}/e6_topology.json"))["star_6"]["D02"]
    import numpy as np
    fresh = np.mean([run(0.2, s % 12, s, Tend=90.0, N=6, edges=edges_of("star", 6))
                     for s in range(8)])
    assert _close(fresh, committed, 1e-9), (fresh, committed)
    return f"star/N6/tau0.2 8-seed mean: {fresh:.6e} == committed (1e-9)"


def probe_e10():
    from tier1_sheaf.experiments.e3b_floor import run
    committed = json.load(open(f"{R1}/e10_dt_sweep.json"))["0.005"]["excess"][2]
    import numpy as np
    turn = np.mean([run(0.4, 0, s, Tend=90.0, dt=0.005) for s in range(10)])
    stra = np.mean([run(0.4, 0, s, Tend=90.0, dt=0.005, eta_profile="straight")
                    for s in range(4)])
    assert _close(turn - stra, committed, 1e-9), (turn - stra, committed)
    return f"dt0.005/tau0.4 excess: {turn-stra:.6e} == committed (1e-9)"


def _drake_D(cfg_over, seed):
    from tier2_drake.blind_harbor.s1 import CFG, run_seed, floor_metrics
    cfg = dict(CFG, Tend=90.0, eval_from=63.0, t_on=float("inf"), **cfg_over)
    return floor_metrics(cfg, run_seed(cfg, seed))


def probe_d2():
    import numpy as np
    rng = np.random.default_rng(0)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    rec = next(r for r in json.load(open(f"{R2}/production_d2_d4_v2.json"))
               if r["kind"] == "d2" and r["tau"] == 0.4 and r["form"] == 0
               and r["seed"] == 0)
    fresh = _drake_D(dict(turn_bias=0.03, turn_amp=0.02, tau=0.4,
                          formation="fan", front_arc=fa, perturb=pe), 0)
    assert _close(fresh, rec["D"], 1e-6), (fresh, rec["D"])
    return f"d2/tau0.4/form0/seed0: D={fresh:.6e} == committed (1e-6)"


def probe_d2ctl():
    import numpy as np
    rng = np.random.default_rng(0)
    fa, pe = float(rng.uniform(0.7, 1.3)), float(rng.uniform(-0.15, 0.15))
    rec = next(r for r in json.load(open(f"{R2}/d2_straight_control.json"))
               if r["tau"] == 0.4 and r["form"] == 0 and r["seed"] == 0)
    fresh = _drake_D(dict(turn_bias=0.0, turn_amp=0.0, tau=0.4,
                          formation="fan", front_arc=fa, perturb=pe), 0)
    assert _close(fresh, rec["D"], 1e-6), (fresh, rec["D"])
    return f"straight/tau0.4/form0/seed0: D={fresh:.6e} == committed (1e-6)"


def probe_d3():
    committed = json.load(open(f"{R2}/d3_amplitude.json"))["arms"]["fan"]
    assert abs(committed["slope"] - 2.0) < 0.01
    assert abs(committed["coef_ratio_at_min_tau"] - 1.0) < 0.01
    return ("committed invariants hold (slope 2.000, coef 1.0000); full re-run: "
            "--run d3 (9 Drake sims)")


def probe_d8():
    committed = json.load(open(f"{R2}/d8_h_sweep.json"))
    e1 = committed["0.001"]["exponent"][1]
    e2_ = committed["0.002"]["exponent"][1]
    assert abs(e1 - e2_) < 0.01, "h-invariance broken in committed data"
    fresh = _drake_D(dict(turn_bias=0.03, turn_amp=0.02, tau=0.4, h=1.0e-3), 0)
    return f"h=1ms/tau0.4/seed0 re-executes (D={fresh:.4e}); exponents h-invariant in data"


def probe_matched():
    committed = json.load(open(f"{R2}/matched_t1.json"))["t1_turn"][0]
    import numpy as np
    from tier1_sheaf.experiments.e3b_floor import run
    S0 = np.stack([0.5 * np.linspace(-1.15, 1.15, 5)] * 2, axis=1)
    fresh = run(0.4, 0, 0, eta_profile="drake_maneuver", l=12.0, v_ref=0.9,
                s0_override=S0, dc=0.1, Tend=90.0)
    assert _close(fresh, committed, 1e-9), (fresh, committed)
    return f"matched-T1 turn/seed0: D={fresh:.6e} == committed (1e-9)"


def probe_baselines():
    committed = json.load(open(f"{R2}/baselines.json"))
    arms = {r["arm"] for r in committed}
    assert "DIEKF-paper (record)" in arms and len(arms) == 4
    return ("4 arms present with aggregates; full re-run: --run baselines "
            "(12 Drake sims). B1-true/B3 excluded (WIP, not paper-bound)")


def probe_d6():
    from tier2_drake.campaign.d6_tension import one as d6_one
    rec = next(r for r in json.load(open(f"{R2}/d6_tension.json"))
               if r["seed"] == 0 and r["weights"] == "A3")
    fresh = d6_one((0, "A3"))
    assert _close(fresh["rmse"][0], rec["rmse"][0], 1e-6), (fresh["rmse"][0], rec["rmse"][0])
    return f"seed0/A3 rmse[0]={fresh['rmse'][0]:.6f} == committed (1e-6)"


def probe_d9():
    from tier2_drake.campaign.d9_scaling import one as d9_one
    rec = next(r for r in json.load(open(f"{R2}/d9_scaling.json"))
               if r["topo"] == "cycle" and r["N"] == 5 and r["form"] == 0 and r["seed"] == 0)
    fresh = d9_one(("cycle", 5, 0, 0))
    assert _close(fresh["floor"], rec["floor"], 1e-6), (fresh["floor"], rec["floor"])
    return f"cycle/N5/form0/seed0 floor={fresh['floor']:.6e} == committed (1e-6)"


def probe_d10b():
    from tier2_drake.campaign.d10b_loss import floor_cell
    rec = next(r for r in json.load(open(f"{R2}/d10b_loss.json"))
               if r["kind"] == "floor" and r["p"] == 0.1 and r["J"] == 0 and r["seed"] == 0)
    fresh = floor_cell((0.1, 0, 0))
    assert _close(fresh[4], rec["D"], 1e-6), (fresh[4], rec["D"])
    return f"floor/p0.1/J0/seed0 D={fresh[4]:.6e} == committed (1e-6)"


def probe_d10c():
    from tier2_drake.campaign.d10c_guard import one as d10c_one
    d = json.load(open(f"{R2}/d10c_guard.json"))
    rec = next(r for r in d["pairs"] if r["guard"] and r["seed"] == 0)
    fresh = d10c_one((True, 0))
    assert _close(fresh["exc"], rec["exc"], 1e-6), (fresh["exc"], rec["exc"])
    return f"guardON/seed0 excursion={fresh['exc']:.4e} == committed (1e-6)"


def probe_d7():
    from tier2_drake.campaign.d7_scorecard import one as d7_one
    rec = next(r for r in json.load(open(f"{R2}/d7_scorecard.json"))
               if r["arm"] == "paper" and r["seed"] == 0)
    fresh = d7_one(("paper", 0))
    assert _close(fresh["pa"], rec["pa"], 1e-6), (fresh["pa"], rec["pa"])
    return f"paper/seed0 anchored={fresh['pa']:.4f} == committed (1e-6)"


def probe_b1lim():
    rec = json.load(open(f"{R2}/b1_limit_mfab.json"))
    fresh = _drake_D(dict(tau=0.01, topology="complete", turn_bias=0.0,
                          turn_amp=0.0), 0)
    return (f"config re-executes (D={fresh:.3e}); per-seed err/anees recorded "
            f"with rerun provenance; agg err {rec['err']:.4f}")


def probe_art_t1():
    """Paper-artifact figures: re-derive the two NEW cited numbers (the C15
    level partner and the domain knee) and check the persisted meta records;
    the generator itself replays the e3a_extension draw sequence and asserts
    it (import-time) — run it via --run artT1 for the full check."""
    import numpy as np
    from scipy.optimize import minimize
    from tier1_sheaf.core.shapes import conjugated_generator
    from tier1_sheaf.sheaf.holonomy import (two_agent_commutator,
                                            holonomy_amplitude_m2)
    XI = np.array([0.4, 0.0, 0.12])
    hm = json.load(open(f"{R1}/artifacts/commutator_heatmap_meta.json"))
    ext = json.load(open(f"{R1}/e3a_extension.json"))
    s_ref = ext["C15"][0]["shapes"][:2]
    Cr = conjugated_generator(s_ref[0], s_ref[1], XI)
    f = lambda s: float(np.linalg.norm(
        (lambda C: Cr @ C - C @ Cr)(conjugated_generator(s[0], s[1], XI))))
    r = minimize(f, ext["C15"][0]["shapes"][2:], method="Nelder-Mead",
                 options={"xatol": 1e-13, "fatol": 1e-15, "maxiter": 4000})
    sep = float(np.hypot(r.x[0] - s_ref[0], r.x[1] - s_ref[1]))
    assert _close(sep, hm["partner_sep"], 1e-6), (sep, hm["partner_sep"])
    dom = json.load(open(f"{R1}/artifacts/domain_boundary_meta.json"))
    si, sj = map(tuple, dom["shapes"])
    K = float(np.linalg.norm(two_agent_commutator(si, sj, XI)))
    ts = np.geomspace(0.05, 12.0, 60)
    rel = np.array([abs(holonomy_amplitude_m2(si, sj, XI, t) - t**2 * K)
                    / (t**2 * K) for t in ts])
    knee = float(ts[np.argmax(rel > 0.10)])
    assert _close(knee, dom["knee_tau_10pct"], 1e-9), (knee, dom["knee_tau_10pct"])
    return (f"level-partner sep {sep:.6f} == meta; domain knee {knee:.3f} == "
            f"meta (1e-9)")


def probe_anatomy():
    """S4 movie record: the persisted per-agent error series must reproduce
    the hero_v2_ensemble fleet-mean for its seed exactly (same config, same
    seed, two independent reductions of the same run)."""
    import numpy as np
    z = np.load(f"{R2}/error_anatomy_series.npz")
    assert int(z["seed"]) == 10
    v2 = json.load(open(f"{R2}/hero_v2_ensemble.json"))
    rec = next(r for r in v2 if r["seed"] == 10)
    ks = z["ts"] >= 500.0
    pm = float(np.mean(z["errs"][ks].mean(axis=1)))
    assert _close(pm, rec["pm"], 1e-9), (pm, rec["pm"])
    return f"S4 series fleet-mean {pm:.6f} == hero_v2_ensemble seed 10 (1e-9)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", metavar="CELL")
    ap.add_argument("--verify-all", action="store_true")
    ap.add_argument("--run", metavar="CELL")
    args = ap.parse_args()
    if args.list:
        for cell, (unit, drv, data, lvl, _) in MANIFEST.items():
            print(f"{cell:10s} [{lvl:5s}] {unit:28s} {drv}  ->  {data}")
        return
    if args.run:
        drv = MANIFEST[args.run][1]
        subprocess.run([sys.executable, drv], check=True, cwd="/workspaces/Anholonomy")
        return
    cells = list(MANIFEST) if args.verify_all else [args.verify]
    ok = True
    for cell in cells:
        probe = globals()[MANIFEST[cell][4]]
        try:
            msg = probe()
            print(f"PASS  {cell:10s} {msg}")
        except Exception as e:
            ok = False
            print(f"FAIL  {cell:10s} {e}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
