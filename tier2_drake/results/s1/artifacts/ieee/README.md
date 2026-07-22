# RA-L "Blind Harbor" — IEEE figure **source/build** folder

This folder is the **generator output**, not the reader-facing paper folder. Every
`.png`/`.pdf` here is produced by a single script from committed campaign records;
the canonical `.pdf`s are then copied into
`/workspaces/Anholonomy/papers/ral_blind_harbor/figures/` and `\included` by the
manuscript. For the full reader narrative of each figure (captions, cross-references,
the paper's argument), see that paper folder's figures and the manuscript
`/workspaces/Anholonomy/papers/ral_blind_harbor/main.tex`.

- **Paper:** *The Price of Staleness: Distributed Invariant Estimation for
  GNSS-Denied Multi-Vessel Cable Towing* (RA-L, the Drake companion to the theory).
- **Authoritative ledger (verdicts + epistemic status):**
  `/workspaces/Anholonomy/docs/ral_package.md`.
- **Reconciliation note:** `/workspaces/Anholonomy/docs/reconciliation_2026-07-21.md`.

## 1. Provenance (one generator)

**Every figure in this folder is produced by**
`/workspaces/Anholonomy/tier2_drake/campaign/ral_figs_ieee.py`
(one plot per figure, single axes, IEEE journal style via
`analysis/ieee_style.py`). Its `__main__` loop writes all 26 `ral_*` families
here. Records are read from two roots:

- `S1 = /workspaces/Anholonomy/tier2_drake/results/s1/` (Drake / multibody records)
- `T1 = /workspaces/Anholonomy/tier1_sheaf/results/` (reduced-plant / Tier-1 records)

Re-generate with: `python /workspaces/Anholonomy/tier2_drake/campaign/ral_figs_ieee.py`.
Regenerating overwrites this folder; copies already in the paper's `figures/`
folder are **not** touched by that run (a separate copy step promotes them).

## Data provenance & authenticity

Each of the 26 figure entries below now carries two audit lines: a `*Theory:*`
line (the specific paper statement it bears on — cited by the RA-L manuscript's
own label + number, read from `papers/ral_blind_harbor/main.tex`) and a
`*Provenance:*` line (one authenticity class + the exact committed record it reads
or the fact that it is a diagram). The theory-label map used below (RA-L,
separate IEEEtran counters per environment):
Lemma 1 `lem:m` (Constraint trivialization) · Lemma 2 `lem:edge` (Edge maps
shape-only) · Lemma 3 `lem:bchF` (Group-commutator defect) · Definition 1
`def:sheafF` (Estimation sheaf; sheaf Laplacian) · Theorem 1 `thm:gaugeF` (Exact
residual unobservability = one global gauge) · Theorem 2 `thm:contractF`
(Frozen-linearization contraction) · **Theorem 3 `thm:floorF` (Latency–curvature
floor) [PROVEN]** · Corollary 1 `cor:pinF` (Pinning) · Corollary 2 `cor:inheritF`
(Network inheritance of conditioning singularities) · Corollary 3 `cor:symF`
(Symmetry protection).

**Authenticity classes (counts over all 26 families):**

- **[SIM] — 21.** A driver ran the actual plant (Tier-1 `ReducedPlant` or Tier-2
  Drake `MultibodyPlant`), seeded where stochastic, and wrote a committed
  `.npz`/`.json`/`.csv` record; the figure reads that record (verified: every data
  cell in `ral_figs_ieee.py` is an `np.load`/`json.load`/`csv.reader` of a named
  record — none recompute or invent at plot time). Seeded `default_rng` noise is
  reproducible simulated data, not fabrication. All 21 records were `ls`-confirmed
  present on disk (see the table in §5) and spot-opened to confirm they hold real
  arrays (e.g. `hero_dogleg_series.npz` → `ts,D,kern,comp,truth`, `truth`
  shape `(4501, 36)` float64; `e3a_amplitude.csv` → real slope/amplitude rows with
  machine-zero switch-offs `2.2e-16`).
- **[DET] — 0.** No figure recomputes an analytic operator live at plot time; the
  deterministic quantities (e.g. the noise-off holonomy amplitude) are read from
  committed records and so count as [SIM] records with deterministic content, not
  as [DET] recomputations.
- **[DIAGRAM] — 5.** `ral_scenario`, `ral_staleness`, `ral_arch`, `ral_taxonomy`,
  and `ral_forest`. The first four are conceptual/hand-laid schematics with no
  measured data. `ral_forest` is a **ledger-verdict summary graphic**: its numbers
  are hard-coded in-script but each is an adjudicated verdict transcribed from
  `docs/ral_package.md`, and each traces to a committed record
  (`d3_amplitude.json`, `production_d2_d4_v2.json`, `matched_drake.json` /
  `matched_t1.json`, `d9_scaling.json`) — it carries no *new* measurement and
  invents nothing, so it is classed DIAGRAM (summary), not FLAG.
- **[FLAG] — 0.** No fabricated or untraceable figure was found.

**Finding (asserted true after the audit above):** every *data* figure in this
folder traces to a committed simulated record produced by a seeded run of the
actual plant; no figure recomputes or invents numbers at plot time; the five
diagrams are labelled as such (and the one that shows real numbers, `ral_forest`,
only transcribes ledger verdicts that each trace to a committed record); **nothing
is fabricated, and no [FLAG] was raised.** (Note: `tier2_drake/blind_harbor/b3_relpose.py`
is WIP/DESIGN-INCOMPLETE and feeds **no** paper figure — it is not in this catalogue.)

## 2. Two objects, never conflated (binding)

The paper measures two different `\tau`-scalings and this README labels every
figure with which one it is:

1. **Error-transport holonomy amplitude** — the object of **Thm 7.2 [PROVEN]**.
   Measured slope **1.999 (Tier-1) / 2.000 (Drake)**; symmetric-class switch-offs
   are **machine zero** (`\xi=0` literally `0.0`). Figures `ral_f4a`, and the
   `p=2` arm of `ral_cross_tier`.
2. **Closed-loop steady-state disagreement `D_ss` [CONJECTURAL]** — measured
   slope **1.101 (Tier-1) / 1.077 (Drake)**, a *measured slope in a conjectural
   regime*, carried with the R3 mixture caveat; **its CI excludes both 1 and 2**
   and **asserts no law**. Figures `ral_f4b`, `ral_f4c`, `ral_robust_drops`, and
   the `p≈1.08` arm of `ral_cross_tier`.

A `D_ss` fit is **never** a validation of Thm 7.2, and the `D_ss` slope is
**never** called a first-order law. All poses are world ENU in metres; SE(2) load
pose is `(x, y, yaw)`; `D` is in m² (all-pairs load-pose disagreement).

## 3. Canonical vs. dev-only in this folder

- **24 of the 26 `ral_*` families are CANONICAL**: their `.pdf` is copied into
  `papers/ral_blind_harbor/figures/` and `\included` by `main.tex`.
- **2 families are DEV-ONLY / SUPERSEDED**: `ral_arch` and `ral_taxonomy`. The
  paper renders these two as hand-drawn TikZ vector diagrams
  (`\input{fig_arch.tex}` → Fig. `arch`; `\input{fig_taxonomy.tex}` → Fig.
  `taxonomy`), **not** the matplotlib versions here. Keep them only as quick-look
  previews.

The three `tcns_*` figures the RA-L paper also `\includes` (`tcns_f5_amp`,
`tcns_f5_floor`, `tcns_f8`) are **not** in this folder — they are shared from the
Tier-1 results folder (`tier1_sheaf/results/`) and documented with the flagship.

## 4. Figure catalogue (each entry: `.png`+`.pdf`)

Generator for all rows: `tier2_drake/campaign/ral_figs_ieee.py`
(function named in each row). Records are under `S1` unless prefixed `T1`.

### The scenario and the plant

- **`ral_scenario`** — `fig_scenario`. **CANONICAL** (Fig. `scenario`).
  *Record:* none — schematic drawing (dogleg channel, tow, range-limited dock
  beacon). Fixes the task: absolute information exists only near the dock, at one
  vessel.
  *Theory:* motivates **Corollary 1 (`cor:pinF`, Pinning) [PROVEN]** — the "one
  absolute channel at one vessel near the dock" premise the pinning corollary
  requires; frames the empirical "price of staleness" thesis. Not itself a
  measurement.
  *Provenance:* **[DIAGRAM]** conceptual scenario schematic, no measured data.
- **`ral_staleness`** — `fig_staleness`. **CANONICAL** (Fig. `staleness`).
  *Record:* none — schematic ladder (50 Hz odometry, 20 Hz cable direction,
  `\tau`-stale 0.05–1.6 s neighbor channel, 5 Hz dock beacon). The staleness axis
  is the paper's central variable.
  *Theory:* defines the staleness lag `\tau` that is the free variable of
  **Theorem 3 (`thm:floorF`, Latency–curvature floor) [PROVEN]** (amplitude
  `O(\tau^2)`) and of the conjectural `D_ss` floor; the multi-rate ladder is a
  modeling premise, not a measurement.
  *Provenance:* **[DIAGRAM]** conceptual multi-rate ladder schematic, no measured
  data.
- **`ral_transit`** — `fig_transit`. **CANONICAL** (Fig. `filmstrip`).
  *Record:* `hero_dogleg_series.npz` (`ts`, `truth`; seed 3). Five barge+5-ASV
  snapshots along the ground-truth trail. *Epistemic:* recorded truth trajectory
  (fact, not prediction).
  *Theory:* no theorem — the recorded ground-truth transit establishing the Drake
  plant/scenario for the "price of staleness" empirical setting; a recorded fact,
  not a prediction.
  *Provenance:* **[SIM]** `hero_dogleg_series.npz` (S1; `ts`, `truth`, seed 3),
  confirmed present — Drake multibody recorded truth.
- **`ral_cables`** — `fig_cables`. **CANONICAL** (Fig. `cables`).
  *Record:* `hero_dogleg_series.npz`. Load-to-vessel distances (m) hold in the
  taut band through the dogleg — bilateral distance-constraint cables never slack
  (which is also why D10(a) slack events are out of this plant's validity domain,
  ledger row D10(a)).
  *Theory:* **Lemma 1 (`lem:m`, Constraint trivialization) [PROVEN]** — the taut
  bilateral distance the cables hold is exactly the cable-length constraint that
  `m(s)` trivializes; also fixes the plant validity domain (no slack, ledger
  D10(a)).
  *Provenance:* **[SIM]** `hero_dogleg_series.npz` (S1; load-to-vessel distances),
  confirmed present.

### Gauge pinning (Cor. 5.2 in closed loop) — **[PROVEN]** corollary, closed-loop demonstration

- **`ral_hero_traj`** — `fig_hero_traj`. **CANONICAL** (Fig. `heroseries`).
  *Record:* `hero_dogleg_series.npz`. Recorded 450 s dogleg truth with turn
  (200–260 s) and beacon (≥410 s) windows.
  *Theory:* no theorem — the recorded 450 s truth carrying the turn/beacon windows;
  the empirical stage for the pinning demonstration (**Corollary 1, `cor:pinF`**).
  *Provenance:* **[SIM]** `hero_dogleg_series.npz` (S1; `ts`, `truth`), confirmed
  present.
- **`ral_hero_D`** — `fig_hero_D`. **CANONICAL** (Fig. `heroD`).
  *Record:* `hero_dogleg_series.npz` (`D`, `kern`). Disagreement `D(t)` (m², the
  maneuver excites it and staleness floors it) vs. the gauge-kernel component
  (grows unbounded under GNSS denial, killed **only** by the beacon). The `D`
  spike at acquisition is the pin shock (the anchored agent snapping to truth
  against a fleet still on the drifted gauge). *Epistemic:* Cor. 5.2 pinning is
  **[PROVEN]**; this is its closed-loop illustration.
  *Theory:* **Corollary 1 (`cor:pinF`, Pinning) [PROVEN]** live — the `D(t)` spike
  at beacon acquisition IS the pin; the unbounded gauge-kernel component is the
  `ker L_F` of **Theorem 1 (`thm:gaugeF`, one global gauge)**, killed only by the
  single anchor.
  *Provenance:* **[SIM]** `hero_dogleg_series.npz` (S1; `D`, `kern`), confirmed
  present.
- **`ral_gauge_trails`** — `fig_gauge_trails`. **CANONICAL** (Fig. `gaugeorbit`).
  *Record:* `hero_ghost_tracks.npz` (`ghost_paper`, `t_on`; seed 3). Five agents'
  load-pose estimates drift as one rigid gauge orbit (solid, pre-beacon), then
  collapse to truth once anchored (dashed).
  *Theory:* **Theorem 1 (`thm:gaugeF`, exact residual unobservability = one global
  SE(2) gauge) [PROVEN]** — the single rigid common orbit the estimates drift on IS
  `ker L_F ≅ se(2)`; the collapse to truth at anchoring is **Corollary 1
  (`cor:pinF`)** pinning.
  *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (S1; `ghost_paper`, `t_on`,
  seed 3), confirmed present.
- **`ral_gauge_err`** — `fig_gauge_err`. **CANONICAL** (Fig. `gaugeerr`).
  *Record:* `hero_ghost_tracks.npz`. Fleet gauge error (mean estimate vs. truth,
  m) grows to tens of metres, killed by the single dock anchor.
  *Theory:* **Theorem 1 (`thm:gaugeF`)** + **Corollary 1 (`cor:pinF`)** — the
  unobservable gauge error grows unbounded under GNSS denial and is removed by one
  anchor (the pinning claim, closed-loop).
  *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (S1), confirmed present.
- **`ral_agent_errors`** — `fig_agent_errors`. **CANONICAL** (Fig. `agenterr`).
  *Record:* `hero_series.npz` (`errs`). Per-agent load-pose error
  `\|Log(Ĝ G^{-1})\|` at the **130 s calibration horizon**, where the anchor
  propagates cleanly. *Epistemic guardrail:* this clean propagation is a
  **130 s-horizon** picture; it fails at 450 s (gain starvation, `ral_v2seeds`).
  *Theory:* **Corollary 1 (`cor:pinF`)** empirical — clean single-anchor
  propagation at the 130 s calibration horizon; carries the horizon guardrail
  (fails at 450 s, gain starvation), so it is a demonstration, not the proof.
  *Provenance:* **[SIM]** `hero_series.npz` (S1; `errs`), confirmed present.

### Docking outcomes and the v2 remedy — spec **UNMET** (reported honestly)

- **`ral_score_box`** — `fig_score_box`. **CANONICAL** (Fig. `scorestats`).
  *Record:* `d7_scorecard.json` (50 transits/arm). Fleet-mean dock error per arm
  (log scale). Ordering on D and fleet-mean: B1ᵗ⁻ˡⁱᵐ > paper > B2 ≫ B0
  (0.76/1.57/2.13/66.7 m).
  *Theory:* no theorem — the empirical **D7 baseline scorecard** (ledger row "D7
  scorecard"): paper rule > naive consensus ≫ dead-reckoning on D and fleet-mean;
  B1 is the record's own zero-latency reference, not an oracle.
  *Provenance:* **[SIM]** `d7_scorecard.json` (S1; 50 transits/arm), confirmed
  present.
- **`ral_score_cdf`** — `fig_score_cdf`. **CANONICAL** (Fig. `scorecdf`).
  *Record:* `d7_scorecard.json`. Per-seed CDFs; the 0.5 m spec sits left of every
  arm's support — **0% success at plan-faithful acquisition, all arms including
  the zero-latency B1 limit**: the approach geometry, not the estimator, binds.
  *Theory:* no theorem — the empirical **D7** finding that 0% of every arm (even
  the zero-latency B1 limit) meets the 0.5 m spec: the approach geometry, not the
  estimator, is the binding constraint.
  *Provenance:* **[SIM]** `d7_scorecard.json` (S1), confirmed present.
- **`ral_v2seeds`** — `fig_v2seeds`. **CANONICAL** (Fig. `v2seeds`).
  *Record:* `hero_v2_ensemble.json` (12 seeds). Decelerating approach (v2):
  fleet-mean vs. anchored-agent dock error. Median ≈0.61 m, 17% of seeds under
  spec — **improvement (2.4×) without sufficiency, spec still UNMET**; the
  anchored agent is worse than fleet mean on 11/12 seeds (gain starvation, the
  binding residual per ledger D7).
  *Theory:* no theorem — the empirical **D7 v2 remedy**: a 2.4× fleet-mean
  improvement that still leaves the spec UNMET, with anchored-agent gain starvation
  as the binding residual.
  *Provenance:* **[SIM]** `hero_v2_ensemble.json` (S1; 12 seeds), confirmed
  present.
- **`ral_docking_zoom`** — `fig_docking_zoom`. **CANONICAL** (Fig. `docking`).
  *Record:* `hero_ghost_tracks.npz`. 5 m dock zoom: fleet estimate ≈1 m from the
  truth barge centre, outside the 0.5 m spec ring.
  *Theory:* no theorem — the empirical **D7** spec-unmet picture (fleet estimate
  ≈1 m from the truth centre, outside the 0.5 m ring).
  *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (S1), confirmed present.
- **`ral_docking_cdf`** — `fig_docking_cdf`. **CANONICAL** (Fig. `dockingcdf`).
  *Record:* `hero_v2_ensemble.json`. v2 CDF: median ≈0.61 m, **83% of seeds still
  miss the 0.5 m spec**.
  *Theory:* no theorem — the empirical **D7 v2** CDF: 83% of seeds still miss the
  0.5 m spec (the remedy improves but does not satisfy).
  *Provenance:* **[SIM]** `hero_v2_ensemble.json` (S1), confirmed present.
- **`ral_baseline_tracks`** — `fig_baseline_tracks`. **CANONICAL** (Fig.
  `baseline`). *Record:* `hero_ghost_tracks.npz` (`ghost_paper`, `ghost_b0`).
  DIEKF-Σ tracks truth and is pinned at the beacon; B0 dead-reckoning walks away.
  *Theory:* **Corollary 1 (`cor:pinF`)** illustration plus the empirical baseline
  contrast — the sheaf estimator is pinned at the beacon (pinning) while B0
  dead-reckoning walks away (ledger D7/B0).
  *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (S1; `ghost_paper`, `ghost_b0`),
  confirmed present.
- **`ral_baseline_err`** — `fig_baseline_err`. **CANONICAL** (Fig. `baselineerr`).
  *Record:* `hero_ghost_tracks.npz`. Fleet-mean load error (m): sheaf fusion
  propagates the single anchor (collapses to ≈1 m); dead-reckoning diverges
  (matching the 1.6 vs. 67 m scorecard means).
  *Theory:* no theorem — the empirical **D7/B0** baseline: single-anchor
  propagation collapses fleet error to ≈1 m vs. dead-reckoning divergence (matches
  the 1.6 vs. 67 m scorecard means).
  *Provenance:* **[SIM]** `hero_ghost_tracks.npz` (S1), confirmed present.

### The theorem's object vs. the conjectured floor

- **`ral_f4a`** — `fig_f4a`. **CANONICAL** (Fig. `f4a`). *Records:*
  `T1/e3a_amplitude.csv` + `d3_amplitude.json`. **Holonomy amplitude — Object (1),
  Thm 7.2 [PROVEN].** Tier-1 slope **1.999** (switch-offs machine zero, `\xi=0`
  literally 0.0); Drake slope **2.000**, `m=2` coefficient **1.0000**, `\eta=0`
  switch-off machine zero, parallel class suppresses the coefficient **31×** at
  achieved-`\varepsilon` (exact cancellation remains the Tier-1 machine-zero
  result). Ledger: C7a/C8/C13 **PASSED** both plants.
  *Theory:* **Theorem 3 (`thm:floorF`, Latency–curvature floor) [PROVEN]** — the
  measured slope-2 IS the theorem's `O(\tau^2)` amplitude claim (Object 1); the
  machine-zero symmetric switch-offs are **Corollary 3 (`cor:symF`, Symmetry
  protection)**. Ledger C7a/C8/C13 PASSED both plants.
  *Provenance:* **[SIM]** `T1/e3a_amplitude.csv` + `S1/d3_amplitude.json`, both
  confirmed present — the noise-off deterministic amplitude object stored as
  committed plant records (`\xi=0` switch-off literally `0.0`; symmetric class
  `~2e-16`).
- **`ral_f4b`** — `fig_f4b`. **CANONICAL** (Fig. `f4b`). *Records:*
  `production_d2_d4_v2.json` + `T1/e3b_production.json`. **Closed-loop floor —
  Object (2) `D_ss` [CONJECTURAL].** Excess exponents **1.101 [1.076, 1.125]
  (Tier-1)** and **1.077 [1.054, 1.102] (Drake)** with `D_0` measured in situ by
  straight-tow controls; the conjectured order 2 is **excluded on both plants
  (C7b FALSIFIED at these scales)**; cross-tier equivalence **PASSES** (+0.023
  [−0.012, +0.057]). Measured slope carried with the mixture caveat; CIs exclude 1
  as well — **no first-order law asserted**.
  *Theory:* **NOT** the floor theorem — the closed-loop `D_ss` (Object 2) is
  **[CONJECTURAL]**; the fitted `p≈1.08` **FALSIFIES** the order-2 conjecture
  (ledger **C7b FALSIFIED** both plants), cross-tier exponent **EQUIVALENT**. This
  figure is **never** a validation of Theorem 3 (`thm:floorF`).
  *Provenance:* **[SIM]** `S1/production_d2_d4_v2.json` + `T1/e3b_production.json`,
  both confirmed present.
- **`ral_f4c`** — `fig_f4c`. **CANONICAL** (Fig. `f4c`). *Record:*
  `d2_a1_a2_arms.json`. Transport-rule ablation on `D_ss` [CONJ regime]. A2
  (unconjugated) runs **1.7×→8.2×** above the paper rule with growing `\tau`
  (C18: transport is load-bearing, **PASSED on Drake**); A1 (naive consensus)
  holds `D` flat and low **by groupthink** (anchored ANEES 62, drift 8.4 m at the
  130 s horizon) — agreement alone is never a virtue metric.
  *Theory:* empirical corroboration of **Lemma 1 (`lem:m`)** / **Lemma 2
  (`lem:edge`)** — the conjugation-by-`m` transport is load-bearing: unconjugated
  A2 degrades 1.7×→8.2× (ledger **C18 PASSED on Drake**); A1 groupthink shows
  agreement is not a virtue metric. On the [CONJ] `D_ss` object, so a falsifier
  arm, not a theorem test.
  *Provenance:* **[SIM]** `S1/d2_a1_a2_arms.json`, confirmed present.

### Cross-tier spine, connectivity, robustness, ledger

- **`ral_cross_tier`** — `fig_cross_tier`. **CANONICAL** (Fig. `ladderoverlay`).
  *Records:* `T1/e3a_amplitude.csv` + `production_d2_d4_v2.json`. The epistemic
  spine in one overlay — **three distinct objects, three exponents, never
  conflated**: Tier-1 `\|Log Hol\|` (**p=2.00, [PROVEN]**); Drake transport defect
  (p=1.00, estimate-mismatch channel); Drake closed-loop `D_ss` (**p≈1.08,
  [CONJECTURAL] regime**, `D_0` measured 19–21× below by the straight-tow control).
  *Theory:* three distinct objects, never conflated — the **p=2.00** arm IS
  **Theorem 3 (`thm:floorF`) [PROVEN]**; the **p=1.00** transport-defect arm is the
  estimate-mismatch channel; the **p≈1.08** arm is `D_ss` **[CONJECTURAL]**. Only
  the p=2 arm bears on the theorem.
  *Provenance:* **[SIM]** `T1/e3a_amplitude.csv` + `S1/production_d2_d4_v2.json`,
  both confirmed present.
- **`ral_d9`** — `fig_d9`. **CANONICAL** (Fig. `d9`). *Record:* `d9_scaling.json`.
  Rates vs. algebraic connectivity `\lambda_2`. **D9 falsifier FIRES**: pin rate
  Spearman **ρ=+0.04 ≈ 0** — single-anchor pinning is **anchor-limited, not
  connectivity-limited**; re-agreement around the pin **anti-orders** with
  connectivity (**ρ=−0.51 [−0.65, −0.36]**, consensus stiffness). Reported as the
  ES-01 finding path — a fired falsifier, not a positive result.
  *Theory:* probes **Corollary 1 (`cor:pinF`)** and the `\kappa\lambda_2` rate of
  **Theorem 2 (`thm:contractF`, Frozen-linearization contraction)** — and the
  **falsifier FIRES**: pin rate ρ=+0.04≈0 (anchor-limited, not
  connectivity-limited); re-agreement anti-orders with `\lambda_2` (ρ=−0.51).
  Ledger **D9 FIRES**; the ES-01 finding path, not a positive result.
  *Provenance:* **[SIM]** `S1/d9_scaling.json` (240 records), confirmed present.
- **`ral_robust_drops`** — `fig_robust_drops`. **CANONICAL** (Fig. `robust`).
  *Record:* `d10b_loss.json`. D10(b) `D_ss` [CONJ regime] vs. packet-drop
  probability (drops-only and drops+jitter, 8 seeds each, mean±sd). Graceful:
  **+13% @ p=0.1, +45% @ p=0.3**; anchored ANEES in-gate at p=0.3 (**4.23, at the
  130 s horizon**). Characterization (red-flag rules), no red flags fired.
  *Theory:* no theorem — the empirical **D10(b)** robustness characterization of
  the [CONJ] `D_ss` (+13% @ p=0.1, +45% @ p=0.3; anchored ANEES in-gate 4.23 at the
  130 s horizon); no red flags fired.
  *Provenance:* **[SIM]** `S1/d10b_loss.json` (8 seeds/arm), confirmed present.
- **`ral_robust_guard`** — `fig_robust_guard`. **CANONICAL** (Fig. `guard`).
  *Record:* `d10c_guard.json` (`envelope_probe`). D10(c) null-with-mechanism: the
  broadside guard was **never exercised** — its trigger, the *estimated* cable
  angle `\hat\sigma_i`, lags true broadside across the reachable envelope (at
  5000 N: true 0.027 vs. estimated 0.106). Guard-on ≡ guard-off (bit-identical);
  the rescue movie does not ship.
  *Theory:* **Corollary 2 (`cor:inheritF`, broadside conditioning collapse)** is
  the mechanism the guard targets, but the figure is the **D10(c)
  null-with-mechanism** finding: the *estimated* cable angle `\hat\sigma_i` lags
  true broadside across the reachable envelope, so the guard is never exercised
  (ON≡OFF). A mechanized null, not a theorem test.
  *Provenance:* **[SIM]** `S1/d10c_guard.json` (`envelope_probe`), confirmed
  present.
- **`ral_forest`** — `fig_forest`. **CANONICAL** (Fig. `dforest`). *Record:*
  ledger values hard-coded in-script from `docs/ral_package.md`. The multibody
  falsifier ledger as adjudicated — **green passed, red falsified/fired, orange
  anti-ordered**: D3 amplitude (2.000, PASSED), D3 coefficient (1.0000, PASSED),
  Cor 7.3 protection (31×, PASSED), C7b-Drake `D_ss` p (1.077, **FALSIFIED**), §6
  coef ratio (**5.04, DISAGREES ×5** — a reduced-model validity-domain finding),
  §6 exponent diff (+0.023, EQUIV), D9 pin ρ (+0.04, **FIRES**), D9 re-lock ρ
  (−0.51, **ANTI-ORDERS**). No verdict dressed up.
  *Theory:* no theorem — a summary of the multibody **falsifier ledger** verdicts
  (D3 amplitude/coefficient PASSED, Cor 7.3 protection PASSED, C7b FALSIFIED, §6
  ratio DISAGREES, §6 exponent EQUIV, D9 FIRES/ANTI-ORDERS) as adjudicated in
  `docs/ral_package.md`.
  *Provenance:* **[DIAGRAM]** ledger-verdict summary graphic — the eight values are
  hard-coded in-script but each is an adjudicated verdict transcribed from
  `docs/ral_package.md`, and each traces to a committed record (`d3_amplitude.json`,
  `production_d2_d4_v2.json`, `matched_drake.json`/`matched_t1.json`,
  `d9_scaling.json`). It carries **no new measurement** and invents nothing —
  a summary, **not** a [FLAG].

### Dev-only / superseded (NOT `\included` by the paper)

- **`ral_arch`** — `fig_arch`. **DEV-ONLY.** *Record:* none — hand-laid box
  diagram. **Superseded** by the paper's TikZ `\input{fig_arch.tex}`
  (Fig. `arch`, the plant/estimator boundary with the truth-isolation lint). Keep
  only as a quick-look preview.
  *Theory:* architectural context for **Definition 1 (`def:sheafF`, Estimation
  sheaf; sheaf Laplacian)** — the plant/estimator boundary and fusion pipeline. Not
  a measurement.
  *Provenance:* **[DIAGRAM]** hand-laid box diagram, no measured data (dev-only,
  not `\included`).
- **`ral_taxonomy`** — `fig_taxonomy`. **DEV-ONLY.** *Record:* none — hard-coded
  four-card finding→cause→remedy layout. **Superseded** by the paper's TikZ
  `\input{fig_taxonomy.tex}` (Fig. `taxonomy`). The four adverse findings it
  cards (docking spec unmet 0%<0.5 m; anchored gain starvation 11/12; ANEES
  non-transfer 159–229 @450 s; guard unexercised ON≡OFF) are all reported
  honestly per the ledger.
  *Theory:* no theorem — a finding→cause→remedy card layout of the four adverse
  empirical findings (docking 0%<0.5 m; anchored gain starvation 11/12; ANEES
  159–229 @450 s; guard unexercised), all ledger-honest.
  *Provenance:* **[DIAGRAM]** hard-coded four-card layout, no measured data
  (dev-only, not `\included`); the card numbers are ledger-traceable adverse
  findings, not fabricated.

## 5. Records referenced from this folder

| Record | Root | Feeds |
|---|---|---|
| `hero_dogleg_series.npz` | S1 | transit, cables, hero_traj, hero_D |
| `hero_ghost_tracks.npz` | S1 | gauge_trails, gauge_err, docking_zoom, baseline_tracks, baseline_err |
| `hero_series.npz` | S1 | agent_errors (130 s horizon) |
| `d7_scorecard.json` | S1 | score_box, score_cdf |
| `hero_v2_ensemble.json` | S1 | v2seeds, docking_cdf |
| `d3_amplitude.json` | S1 | f4a (Drake amplitude) |
| `production_d2_d4_v2.json` | S1 | f4b, cross_tier (Drake `D_ss`) |
| `d2_a1_a2_arms.json` | S1 | f4c (A1/A2 ablation) |
| `d9_scaling.json` | S1 | d9 |
| `d10b_loss.json` | S1 | robust_drops |
| `d10c_guard.json` | S1 | robust_guard |
| `e3a_amplitude.csv` | T1 | f4a, cross_tier (Tier-1 amplitude) |
| `e3b_production.json` | T1 | f4b (Tier-1 `D_ss`) |
| — (ledger constants) | — | forest |

Reproducibility manifest (cell → driver → data) is in
`docs/ral_package.md` §3.

## 6. Caveats carried into every caption

- **B1 is the record's own zero-latency all-to-all limit** — a *reference*, never
  an *oracle*; a fundamentally better centralized estimator is not excluded.
- **Every ANEES claim carries its horizon**: in-gate 3.96 at the 130 s S1 horizon;
  **159–229 on 450 s transits** — the M-FAB calibration gate does not transfer.
- **Docking <0.5 m: 0% of all arms** at plan-faithful acquisition (even the
  zero-latency limit misses); v2 improves fleet-mean 2.4× but the spec stays UNMET.
- **Cross-tier coefficient ratio DISAGREES ×5** (5.04 [3.97, 6.19]) — a
  reduced-model validity-domain finding (Drake realized shapes exit the reduced
  model's domain), *not* a modeling error; the exponent is EQUIVALENT (+0.023).
- The papers currently carry **empty bibliographies** (zero `\cite`); nothing here
  is externally cited.
</content>
</invoke>
