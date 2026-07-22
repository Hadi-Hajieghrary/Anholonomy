# `tier2_drake/results/s1/artifacts/` — figure build/export folder (RA-L "Blind Harbor")

**Corresponding paper:** the RA-L companion *The Price of Staleness: Distributed
Invariant Estimation for GNSS-Denied Multi-Vessel Cable Towing*
(`papers/ral_blind_harbor/main.tex`), the Tier-2 Drake experimental companion to
the sheaf-theory papers.

**Authoritative ledger (verdicts + epistemic status):**
`docs/ral_package.md`.
**Reconciliation note:** `docs/reconciliation_2026-07-21.md`.

---

## 1. What this folder is

This is a **source / build / export folder**, not the reader-facing paper figures
folder. It holds figure renders produced from the committed S1 records under
`tier2_drake/results/s1/` (`*.json`, `*.npz`) — nothing is re-simulated by the
figure code here.

It contains **two distinct generations** of figures:

- **Top-level `ral_*.{png,pdf}` (descriptive names)** — an earlier gallery/dev
  generation, produced by `analysis/figures/ral_artifacts.py` and
  `tier2_drake/campaign/ral_scenario_figs.py`. **None of these top-level files are
  the canonical copies.** Every top-level file differs (by md5) from its namesake
  in `papers/ral_blind_harbor/figures/`, and several use names the paper never
  `\include`s at all. Treat all top-level `ral_*` files as **SUPERSEDED / dev-only**.
- **`ieee/` subdirectory** — the **CANONICAL** RA-L export set, produced by
  `tier2_drake/campaign/ral_figs_ieee.py`. These files are **byte-identical**
  (md5-verified) to `papers/ral_blind_harbor/figures/` and are the ones the paper
  actually `\include`s. See §3.

**For the full reader-facing narrative of each figure, see
`papers/ral_blind_harbor/figures/README.md`** (the canonical folder). This README
is provenance-focused: generator → data record → canonical/superseded → one-line
epistemic verdict.

## 2. Epistemic guardrails (binding — carried from the ledger)

- **Two different objects, never conflated.** (1) The **error-transport holonomy
  amplitude** = the object of Thm 7.2 **[PROVEN]**; measured slope 1.999 (Tier-1) /
  2.000 (Drake); coefficient 1.0000; switch-offs machine-zero (ξ=0/η=0 literally
  0.0). (2) The **closed-loop steady-state disagreement `D_ss`** **[CONJECTURAL]**;
  measured slope 1.101 [1.076,1.125] (Tier-1) / 1.077 [1.054,1.102] (Drake) — a
  measured slope in a conjectural regime, carried with the R3 mixture caveat, its
  CI excluding both 1 and 2; **no law is asserted**. Never caption a `D_ss` fit as
  validating Thm 7.2.
- **Falsifier rows are reported honestly**, never dressed up: C7b **FALSIFIED** at
  these scales; C9c robust-suppression **TRIPS** (2.75× < 10×); C19 **TRIPPED** but
  in the favorable direction; **D9 falsifier FIRES** (pin-rate Spearman ρ=+0.04 ≈ 0:
  anchor-limited, not connectivity-limited; D re-agreement anti-orders −0.51).
- **Cross-tier:** exponent **EQUIVALENT** (+0.023 [−0.012,+0.057]); coefficient
  ratio **DISAGREES ×5** (5.04 [3.97,6.19]) — a reduced-model validity-domain
  finding (Drake's realized maneuvering shapes exit the reduced model's domain).
- **Docking <0.5 m: 0% of all arms** at plan-faithful acquisition — even the
  zero-latency B1 reference misses spec; v2 decelerating approach improves
  fleet-mean 2.4× (median ≈0.61 m; 17% of seeds under spec) but the **spec remains
  UNMET**. B1 is "the record's own zero-latency all-to-all limit" — a **reference,
  never an oracle**.
- **Every ANEES carries its horizon:** in-gate 3.96 at the 130 s S1 horizon (widened
  author-ruled [0.8,5.0] gate); 159–229 on 450 s transits — the M-FAB calibration
  gate does **not** transfer to long transits.
- Units/frame: world ENU, metres; SE(2) load pose = (x, y, yaw); disagreement
  `D` in m². Predictions are labelled as predictions; only realized/measured states
  are stated as facts. The paper bibliography is currently empty — these figures are
  not externally cited.

---

## Data provenance & authenticity

A per-figure audit (the two labelled lines added to every entry below) traces each
catalogued figure to its generator, the committed record it reads (or the
deterministic operator it recomputes, or its status as a labelled diagram), and the
specific theorem or falsifier it bears on. Theorem/label numbers below are the RA-L
paper's own (`papers/ral_blind_harbor/main.tex`, sequential `\newtheorem`
counters): Lemma 1 = `lem:m`, Lemma 2 = `lem:edge`, Lemma 3 = `lem:bchF`;
Theorem 1 = `thm:gaugeF`, Theorem 2 = `thm:contractF`, Theorem 3 = `thm:floorF`;
Corollary 1 = `cor:pinF`, Corollary 2 = `cor:inheritF`, Corollary 3 = `cor:symF`;
Definition 1 = `def:sheafF`. (These are the same objects the guardrails above cite
by their theory-source numbers "Thm 7.2" / "Cor. 5.2".)

**Counts across the 22 annotated entries:**

- **[SIM] — 18.** A generator ran the actual plant (Tier-1 `ReducedPlant` / Tier-2
  Drake `MultibodyPlant`) under a **seeded** rng and wrote a committed record; the
  figure reads that record. Records **confirmed present on disk**: under
  `tier2_drake/results/s1/` — `hero_dogleg_series.npz`, `hero_ghost_tracks.npz`,
  `hero_series.npz`, `d7_scorecard.json`, `d3_amplitude.json`, `d2_a1_a2_arms.json`,
  `d2_straight_control.json`, `d6_tension.json`, `d9_scaling.json`, `d10b_loss.json`,
  `d10c_guard.json`, `hero_v2_ensemble.json`, `matched_t1.json`, `matched_drake.json`,
  `production_d2_d4_v2.json`, `d2_tau005.json`; under `tier1_sheaf/results/` —
  `e3b_production.json`, `e3a_amplitude.csv`. Each opened holds **real arrays, not
  empty stubs** (e.g. the `.npz` files carry 4501-/1301-sample truth/disagreement/
  error arrays: `hero_ghost_tracks.npz` `ghost_paper` is 5×4501×3; `d7_scorecard.json`
  holds 200 per-arm/per-seed records with `D`/`anees`/`drift` fields). A seeded
  `default_rng(seed)` is **reproducible simulation noise = real simulated data, not
  fabrication.**
- **[DET] — 1.** `ieee/ral_f4a` — the error-transport holonomy amplitude is a
  **deterministic** operator sweep (no rng; switch-offs literally `0.0`, coefficient
  exactly `1.0000`), recomputed at fixed twists and cross-checked against the
  committed `d3_amplitude.json` / `e3a_amplitude.csv`.
- **[DIAGRAM] — 3.** `ral_scenario`, `ral_architecture`, `ral_failure_taxonomy` —
  honest conceptual/schematic figures with **no measured data of their own**; each is
  labelled as such and none reads as a measurement.
- **[FLAG] — 0.** None found.

**Finding:** every **data** figure in this folder traces to a committed **simulated
record ([SIM])** or a **deterministic operator recomputation ([DET])**; the three
**diagrams are labelled as diagrams**; **nothing is fabricated or hardcoded.** The
known WIP `b3_relpose.py` (self-labelled "synthetic … DESIGN INCOMPLETE") feeds **no
figure here** and is correctly excluded. Epistemic separation is preserved end to
end: the **PROVEN** amplitude (Theorem 3 `thm:floorF`, `ral_f4a`) and the
**CONJECTURAL** closed-loop `D_ss` (`ral_f4b`) are annotated as **different
objects**, and no `D_ss` fit is captioned as validating the floor theorem.

---

## 3. Figure catalogue (provenance-focused)

Every entry: **generator** → **data record(s) read** → **canonical vs superseded**
→ **one-line epistemic verdict**. `.png` + `.pdf` of one figure grouped into one
entry. All top-level files are SUPERSEDED; the canonical `\included` copies are the
`ieee/`-named exports now living in `papers/ral_blind_harbor/figures/`.

### Scenario / descriptive-context figures

- **`ral_scenario.{png,pdf}`** — gen `analysis/figures/ral_artifacts.py`
  (`fig_scenario`); schematic layout, no numeric record. **SUPERSEDED** by
  `ieee/ral_scenario.pdf` (= paper Fig. `scenario`, `\included`; different md5).
  *Depicts:* the GNSS-denied dogleg channel, the tow, the single range-limited dock
  beacon. Descriptive — no epistemic claim.
  - *Theory:* No theorem — a descriptive scene establishing the GNSS-denied dogleg /
    single-beacon Blind Harbor task; it frames the empirical "price of staleness"
    thesis that the paper's measured figures test.
  - *Provenance:* **[DIAGRAM]** conceptual scene / schematic layout, no measured data.
- **`ral_architecture.{png,pdf}`** — gen `ral_artifacts.py` (`fig_architecture`);
  block diagram. **DEV-ONLY, not `\included`:** the paper's architecture figure is
  the TikZ `\input{fig_arch.tex}`, not a raster. (An `ieee/ral_arch.pdf` also exists
  but is likewise not `\included`.) Descriptive.
  - *Theory:* Illustrates Definition 1 (`def:sheafF`, estimation sheaf + sheaf
    Laplacian) and Lemma 2 (`lem:edge`, edge maps shape-only / locally computable) —
    the DIEKF-Σ data flow; no measurement.
  - *Provenance:* **[DIAGRAM]** block diagram, no measured data (dev-only; the paper's
    architecture figure is the TikZ `fig_arch.tex`).
- **`ral_transit_filmstrip.{png,pdf}`** — gen
  `tier2_drake/campaign/ral_scenario_figs.py`; reads
  `../hero_dogleg_series.npz` (seed 3, 5 ASVs, 36-wide truth layout).
  **SUPERSEDED** by `ieee/ral_transit.pdf` (= paper Fig. `filmstrip`). *Depicts:* the
  pentagon barge towed on cables at five instants along the recorded ground-truth
  trail. Descriptive — recorded run, not a claim.
  - *Theory:* No theorem — a descriptive recorded run establishing the Drake
    `MultibodyPlant` that every downstream claim executes on.
  - *Provenance:* **[SIM]** `tier2_drake/results/s1/hero_dogleg_series.npz` (seed 3;
    `ts`/`D`/`kern`/`comp`/`truth` arrays, 4501 samples) — confirmed present.
- **`ral_hero_series.{png,pdf}`** — gen `ral_artifacts.py` (`fig_hero_series`);
  reads `../hero_dogleg_series.npz`. **SUPERSEDED** by `ieee/ral_hero_traj.pdf`
  (= paper Fig. `heroseries`). *Depicts:* the recorded 450 s dogleg truth
  trajectory with turn/beacon windows. Descriptive.
  - *Theory:* No theorem — the descriptive 450 s recorded truth trajectory; context
    for the horizon-scoped error claims.
  - *Provenance:* **[SIM]** `hero_dogleg_series.npz` (seed 3) — confirmed present.

### Constraint satisfaction

- **`ral_cable_constraint.{png,pdf}`** — gen `ral_scenario_figs.py`; reads
  `../hero_dogleg_series.npz`. **SUPERSEDED** by `ieee/ral_cables.pdf`
  (= paper Fig. `cables`). *Depicts:* load-to-vessel distances holding in the taut
  band (12 m cable + barge attach radius) through the dogleg. Verdict: the
  **bilateral distance-constraint cables never go slack** — D10a slack events are
  scoped out for v1 precisely because these cables cannot slack (validity-domain
  line; unilateral-cable plant is a revision item).
  - *Theory:* Lemma 1 (`lem:m`, constraint trivialization) — the taut bilateral
    distance constraints are exactly the holonomic constraints conjugated by m; the
    figure shows they stay in the taut band (never slack), i.e. the validity-domain
    premise under which `lem:m` applies (D10a scoped out for v1).
  - *Provenance:* **[SIM]** `hero_dogleg_series.npz` (load-to-vessel distances from
    the recorded truth layout) — confirmed present.

### Gauge pinning (Cor. 5.2, PROVEN)

- **`ral_gauge_orbit.{png,pdf}`** — gen `ral_scenario_figs.py`; reads
  `../hero_ghost_tracks.npz` (per-agent load-pose ghost estimates, seed 3).
  **SUPERSEDED** by `ieee/ral_gauge_trails.pdf` (= paper Fig. `gaugeorbit`).
  *Depicts:* the five per-agent load-pose estimates drift as one rigid **gauge
  orbit** off truth through GNSS denial, then collapse toward truth once the dock
  beacon is acquired. Verdict: **Cor. 5.2 (pinning) [PROVEN]** acting in closed
  loop — a single anchor pins the whole fleet through fusion; kernel error grows
  unbounded, complement stays two orders smaller.
  - *Theory:* Theorem 1 (`thm:gaugeF`, exact residual unobservability = one global
    gauge) with Corollary 1 (`cor:pinF`, pinning) **[PROVEN]** — the rigid drift IS
    the SE(2) gauge orbit of `thm:gaugeF`; the beacon-time collapse IS `cor:pinF`
    acting live in closed loop.
  - *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (5 per-agent load-pose ghost
    estimates, seed 3; `ghost_paper` is 5×4501×3) — confirmed present.

- **`ral_agent_errors.{png,pdf}`** — gen `ral_artifacts.py` (`fig_agent_errors`);
  reads `../hero_series.npz`. Basename coincides with the paper's `\include`
  `ral_agent_errors.pdf`, but the canonical copy is the **ieee** render (different
  md5) — this top-level file is **SUPERSEDED** by `ieee/ral_agent_errors.pdf`
  (= paper Fig. `agenterr`). *Depicts:* per-agent load-pose error at the **130 s
  calibration horizon**, where the beacon at agent 0 (from 30 s) propagates cleanly
  through fusion to the whole fleet. Verdict: this clean-propagation picture holds
  **only at the 130 s horizon** — its 450 s failure is the gain-starvation finding
  (see `ral_v2_seeds`). Every ANEES/error claim carries its horizon.
  - *Theory:* Empirical instance of Corollary 1 (`cor:pinF`) — one anchor propagates
    through fusion to the whole fleet, but only at the 130 s calibration horizon; not
    a horizon-free theorem claim.
  - *Provenance:* **[SIM]** `hero_series.npz` (per-agent `errs` 1301×5, seeded) —
    confirmed present.

### Baselines — transport is load-bearing (C18)

- **`ral_baseline_divergence.{png,pdf}`** — gen `ral_scenario_figs.py`; reads
  `../hero_ghost_tracks.npz` (paper rule + B0 re-run tracks). **SUPERSEDED** by
  `ieee/ral_baseline_tracks.pdf` + `ieee/ral_baseline_err.pdf` (= paper Figs.
  `baseline`, `baselineerr`). *Depicts:* DIEKF-Σ follows truth and is pinned at the
  beacon; B0 dead-reckoning walks away (fleet-mean 66.7 m vs 1.57 m at dock).
  Verdict: **C18 conjugated transport load-bearing — PASSED on Drake** (A2 ablation
  1.7→8.2× worse with τ). Ordering *inverts* on Tier-1 (regime-dependent); `D_ss`
  never ranks rules. B1 is the record's zero-latency limit, a reference not an
  oracle.
  - *Theory:* No theorem — an empirical baseline ablation; falsifier **C18**
    (conjugated transport load-bearing) **PASSED on Drake** (A2 1.7→8.2× worse with
    τ). Contrasts B0 dead-reckoning against the `cor:pinF`-pinned paper rule; B1 is a
    reference, not an oracle.
  - *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (paper-rule + B0 re-run tracks) —
    confirmed present.

### Docking outcomes

- **`ral_docking_zoom.{png,pdf}`** — gen `ral_scenario_figs.py`; reads
  `../hero_ghost_tracks.npz`. Basename coincides with the paper's `\include`
  `ral_docking_zoom.pdf`, but the canonical copy is the **ieee** render (different
  md5) — this top-level file is **SUPERSEDED** by `ieee/ral_docking_zoom.pdf`
  (= paper Fig. `docking`). *Depicts:* 5 m zoom at the dock; the fleet load-pose
  estimate sits ~1 m from the truth barge centre, **outside the 0.5 m spec ring**.
  Verdict: docking spec **UNMET — 0% of all arms** under 0.5 m at plan-faithful
  acquisition; approach geometry, not the estimator, binds.
  - *Theory:* No theorem — an empirical docking-spec outcome supporting the adverse
    "price of staleness" finding (0% of arms <0.5 m; ledger row **D7**); approach
    geometry binds, not the estimator.
  - *Provenance:* **[SIM]** `hero_ghost_tracks.npz` — confirmed present.
- **`ral_scorecard_stats.{png,pdf}`** — gen `ral_artifacts.py` (`fig_scorecard`);
  reads `../d7_scorecard.json`; **also writes `scorecard_wins.json`** (see §4).
  **SUPERSEDED** by `ieee/ral_score_box.pdf` + `ieee/ral_score_cdf.pdf` (= paper
  Figs. `scorestats`, `scorecdf`). *Depicts:* the D7 50-transit BHT scorecard —
  per-arm boxes and per-seed CDFs of fleet-mean dock error. Verdict: ordering
  **B1-limit > paper > B2 ≫ B0** on `D` and fleet-mean (fleet mean
  0.76/1.57/2.13/66.7 m; `D` 0.72/2.85/3.37/9624 m²), holds seed-wise; **0.5 m spec
  left of every arm's support (0% success)**.
  - *Theory:* No theorem — the **D7** 50-transit falsifier scorecard (empirical arm
    ordering + docking-spec 0%); supports the "price of staleness" thesis, not a
    theorem.
  - *Provenance:* **[SIM]** `d7_scorecard.json` (200 records, `arm`/`seed`/`D`/`anees`/
    `drift`) — confirmed present.
- **`ral_v2_seeds.{png,pdf}`** — gen `ral_artifacts.py` (`fig_v2_seeds`); reads
  `../hero_v2_ensemble.json` (12 seeds). **SUPERSEDED** by `ieee/ral_v2seeds.pdf`
  (note: canonical basename drops the underscore; = paper Fig. `v2seeds`).
  *Depicts:* the decelerating-approach (v2) remedy per seed — fleet-mean vs
  anchored-agent dock error. Verdict: v2 improves fleet-mean **2.4×** (median
  ≈0.61 m; **17%** of seeds under 0.5 m) but the **spec remains UNMET**; the
  anchored agent is *worse* than the fleet mean on **11/12** seeds
  (anchored-agent gain starvation — sustained Kalman anchoring collapses P; the
  frozen-trim hypothesis was tested and falsified).
  - *Theory:* No theorem — an empirical characterization of the v2 decelerating-
    approach remedy and the anchored-agent gain-starvation failure mode (**D7** remedy
    row); the spec remains **UNMET**.
  - *Provenance:* **[SIM]** `hero_v2_ensemble.json` (12 seeds) — confirmed present.

### Adjudicated ledger

- **`ral_forest.{png,pdf}`** — gen `ral_artifacts.py` (`fig_forest`); reads
  `../d3_amplitude.json`, `../d2_a1_a2_arms.json`, `../d6_tension.json`,
  `../d9_scaling.json`. Basename coincides with the paper's `\include` `ral_forest`,
  but the canonical copy is the **ieee** render (different md5) — this top-level file
  is **SUPERSEDED** by `ieee/ral_forest.pdf` (= paper Fig. `dforest`). *Depicts:* the
  multibody falsifier ledger, verdicts as adjudicated (green passed / red
  falsified-or-fired / orange anti-ordered). Carries: D3 amplitude slope **2.000
  [PROVEN]**, coefficient 1.0000, Cor 7.3 protection **31×**; C18 A2 degradation
  1.7→8.2×; D6 tension ΔRMSE; **D9 pin-rate ρ=+0.04 (falsifier FIRES,
  anchor-limited)**; D9 re-lock ρ=−0.51 (anti-orders). No row dressed up.
  - *Theory:* A ledger spanning several results — carries the D3 slope-2 amplitude of
    Theorem 3 (`thm:floorF`) **[PROVEN]** and the 31× protection of Corollary 3
    (`cor:symF`), alongside empirical falsifiers **C18** / **D6** / **D9** (D9 pin
    ρ=+0.04 **FIRES**). Not a single-theorem test.
  - *Provenance:* **[SIM]** `d3_amplitude.json` (`taus`/`arms`), `d2_a1_a2_arms.json`
    (240), `d6_tension.json` (50), `d9_scaling.json` (240) — all confirmed present.

### Robustness (D10, outside protocol class 𝒫)

- **`ral_robustness.{png,pdf}`** — gen `ral_artifacts.py` (`fig_robustness`); reads
  `../d10b_loss.json` + `../d10c_guard.json`. **SUPERSEDED** by
  `ieee/ral_robust_drops.pdf` + `ieee/ral_robust_guard.pdf` (= paper Figs. `robust`,
  `guard`). *Depicts:* (drops) floor degrades **gracefully** — +13% at p=0.1, +45%
  at p=0.3, anchored ANEES in-gate at p=0.3 (**4.23, at the 130 s horizon**), no red
  flags; (guard) the broadside guard was **never exercised** in the reachable gust
  envelope (its trigger σ̂ᵢ lags true broadside; ON ≡ OFF, bit-identical) —
  reported as a **null with its mechanism**. Pre-registered as characterization,
  not a falsifier.
  - *Theory:* No theorem — a **D10** robustness characterization outside protocol
    class 𝒫 (graceful floor degradation; guard-null reported with its mechanism);
    falsifier rows **D10b** / **D10c**.
  - *Provenance:* **[SIM]** `d10b_loss.json` (66), `d10c_guard.json` (`pairs` +
    `envelope_probe`) — confirmed present.

### Not used by the paper

- **`ral_failure_taxonomy.{png,pdf}`** — gen `ral_artifacts.py` (`fig_taxonomy`);
  ledger schematic citing `../d7_scorecard.json`, `../hero_v2_ensemble.json`,
  `../d10c_guard.json`. **DEV-ONLY, not `\included`:** the paper's taxonomy figure
  is the TikZ `\input{fig_taxonomy.tex}`, not this raster. Organizes the four
  adverse findings (docking spec, gain starvation, ANEES horizon, guard null) with
  measured cause and recorded remedy.
  - *Theory:* No theorem — a schematic organizing the four adverse empirical findings
    (docking spec, gain starvation, ANEES horizon, guard null) with their measured
    cause / recorded remedy.
  - *Provenance:* **[DIAGRAM]** ledger schematic, no measured data of its own (it
    cites `d7_scorecard.json` / `hero_v2_ensemble.json` / `d10c_guard.json` as
    sources; dev-only, paper uses TikZ `fig_taxonomy.tex`).

---

## 4. Data file

- **`scorecard_wins.json`** — a **data record written by** `ral_artifacts.py`
  (`fig_scorecard`), not a figure. Holds the seed-wise win counts backing the
  paper's Sec. "docking outcomes" text: `{ "wins_vs_B2": 41, "wins_vs_B0": 50,
  "B1lim_beats_paper": 47 }` — i.e. paired by seed, the paper rule beats B2 on
  fleet-mean in 41/50 transits and B0 in 50/50, while the zero-latency B1 limit
  beats the paper rule in 47/50. Derived from `../d7_scorecard.json`.
  - *Theory:* No theorem — derived seed-win counts backing the docking-outcomes prose
    (ledger row **D7**).
  - *Provenance:* **[SIM]** derived (deterministic seed-pairing) from `d7_scorecard.json`
    — confirmed present; a computed roll-up of a committed record, not a fabricated
    table.

---

## 5. `ieee/` subdirectory — the CANONICAL export set

Generated by `tier2_drake/campaign/ral_figs_ieee.py`. **md5-verified byte-identical
to `papers/ral_blind_harbor/figures/`** — these are the files the paper actually
`\include`s. Each is a `.png` + `.pdf` pair.

`\included` by `main.tex` (canonical, one per paper figure): `ral_scenario`,
`ral_staleness`, `ral_transit`, `ral_cables`, `ral_hero_traj`, `ral_hero_D`,
`ral_gauge_trails`, `ral_gauge_err`, `ral_agent_errors`, `ral_score_box`,
`ral_score_cdf`, `ral_v2seeds`, `ral_docking_zoom`, `ral_docking_cdf`,
`ral_baseline_tracks`, `ral_baseline_err`, `ral_f4a`, `ral_f4b`, `ral_f4c`,
`ral_cross_tier`, `ral_d9`, `ral_robust_drops`, `ral_robust_guard`, `ral_forest`.
(The `tcns_f5_amp`, `tcns_f5_floor`, `tcns_f8` panels the paper also `\include`s
come from `tier1_sheaf/results/`, not this folder.)

Present in `ieee/` but **not `\included`** (paper uses TikZ instead): `ral_arch`
(→ `fig_arch.tex`), `ral_taxonomy` (→ `fig_taxonomy.tex`).

Epistemic verdicts of the analysis-panel exports (per `docs/ral_package.md`):

- **`ieee/ral_f4a.{png,pdf}`** — error-transport **holonomy amplitude [PROVEN]**:
  Tier-1 slope **1.999** (switch-offs machine-zero), Drake slope **2.000**, coef
  1.0000, η=0 machine-zero, parallel class 31× coefficient suppression. Thm 7.2.
  - *Theory:* Theorem 3 (`thm:floorF`, latency–curvature floor) **[PROVEN]** with
    Lemma 3 (`lem:bchF`, group-commutator defect) and Corollary 3 (`cor:symF`,
    symmetry protection) — the measured slope 1.999/2.000 and coefficient 1.0000 ARE
    the theorem's O(τ²) amplitude claim; η=0 machine-zero and 31× parallel-class
    suppression ARE `cor:symF`. (Falsifiers C7a/C8/C13 PASSED.)
  - *Provenance:* **[DET]** deterministic holonomy-amplitude sweep (no rng; switch-offs
    literally 0.0, coefficient exactly 1.0000) — cross-checked against `d3_amplitude.json`
    (Drake) and `tier1_sheaf/results/e3a_amplitude.csv` (Tier-1), both confirmed present.
- **`ieee/ral_f4b.{png,pdf}`** — closed-loop **`D_ss` floor [CONJECTURAL]**: fitted
  excess exponents **1.101 [1.076,1.125]** (Tier-1) / **1.077 [1.054,1.102]**
  (Drake); cross-tier equivalence **PASSES** (+0.023); **order 2 FALSIFIED at these
  scales** (CIs also exclude 1); a measured slope, no law asserted.
  - *Theory:* Closed-loop steady-state disagreement `D_ss` **[CONJECTURAL]** — a
    DIFFERENT object from Theorem 3 (`thm:floorF`); order-2 **FALSIFIED** at these
    scales (falsifier **C7b**), measured excess exponent ≈1.1. Explicitly **NOT** a
    test of the floor theorem; no law asserted.
  - *Provenance:* **[SIM]** seeded closed-loop ensembles — Tier-1
    `tier1_sheaf/results/e3b_production.json` (1584 runs) + Drake
    `production_d2_d4_v2.json` / `d2_tau005.json` — confirmed present.
- **`ieee/ral_f4c.{png,pdf}`** — variance attribution: A2 ablation 1.7→8.2× above the
  paper rule; naive consensus (A1) holds disagreement flat **by groupthink**
  (anchored ANEES 62, drift 8.4 m at the 130 s horizon) — agreement is never a
  virtue metric; straight-tow control shows 19–21× motion excitation.
  - *Theory:* No theorem — empirical variance attribution (falsifier **C18** A2
    ablation 1.7→8.2×; naive-consensus A1 holds `D` flat by groupthink — agreement is
    never a virtue metric). Supports the "transport is load-bearing" thesis.
  - *Provenance:* **[SIM]** `d2_a1_a2_arms.json` (240) + `d2_straight_control.json` —
    confirmed present.
- **`ieee/ral_cross_tier.{png,pdf}`** — cross-tier ladder: exponent EQUIVALENT;
  **coefficient ratio DISAGREES ×5** (5.04 [3.97,6.19]); baseline agrees to 12% with
  reduced-plant noise off — a reduced-model **validity-domain** finding.
- **`ieee/ral_d9.{png,pdf}`** — connectivity buys agreement, not anchoring: floor
  improves with λ₂; **single-anchor pin is anchor-rate-limited (Spearman +0.04 —
  falsifier FIRES)**; re-agreement anti-orders with connectivity (−0.51).
- **`ieee/ral_gauge_err.{png,pdf}`**, **`ieee/ral_agent_errors.{png,pdf}`** — gauge
  error grows to tens of metres under GNSS denial, killed by the single anchor;
  per-agent anatomy at the **130 s calibration horizon** (carry the horizon).
- Remaining `ieee/` scenario/docking/hero/baseline/robust/scorecard exports are the
  canonical counterparts of the superseded top-level figures catalogued in §3 —
  same verdicts, reader narrative in `papers/ral_blind_harbor/figures/README.md`.
</content>
</invoke>
