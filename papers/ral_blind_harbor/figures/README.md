# RA-L "Blind Harbor" companion — figure & artifact guide

This folder holds the figures for the RA-L Drake companion paper
**"The Price of Staleness: Distributed Invariant Estimation for GNSS-Denied
Multi-Vessel Cable Towing"** (`../main.tex`). The paper studies DIEKF-Σ, a
distributed invariant EKF that treats taut tow-cables as a measurement channel
and fuses τ-stale inter-vessel packets through shape-conjugated transports,
evaluated in closed loop on two independent plants (a reduced kinematic plant
integrating the theory's shape ODEs, and a physics-complete Drake multibody
plant with SAP contact, distance-constraint cables, and hydrodynamic drag).
The figures span the physical scenario and cable constraints, the gauge-pinning
result (Cor. 5.2) as a live D(t) spike, the closed-loop steady-state floor
(the falsified order-2 conjecture), the two-plant holonomy-amplitude check
(the proven Thm 7.2 object), the cross-tier equivalence/coefficient split, the
50-transit docking scorecard, the D9 anchor-limited pin, robustness, and the
recorded hero dogleg transit. Every figure is generated **from committed
campaign records only** — nothing is re-simulated at plot time.

The folder mixes the paper's own `ral_*` / `tcns_*` figures with **superseded
alternates and pre-composition source panels** kept for re-editing. Used-vs-
unused status is marked on every entry below.

## Data provenance & authenticity

Every figure entry below now carries two added lines: a **Theory:** line (the
specific labelled statement of `../main.tex` it bears on, cited by the paper's
own label and counter number) and a **Provenance:** line (its authenticity
class plus the exact committed record it reads, or the reason it holds no
measured data). The paper's theorem counters are independent (no
`numberwithin`), so: Lemma 1 `lem:m`, Lemma 2 `lem:edge`, Lemma 3 `lem:bchF`;
Definition 1 `def:sheafF`; Theorem 1 `thm:gaugeF`, Theorem 2 `thm:contractF`,
Theorem 3 `thm:floorF`; Corollary 1 `cor:pinF`, Corollary 2 `cor:inheritF`,
Corollary 3 `cor:symF`.

**Counts per class (30 figure entries):**

- **[SIM] — 24 entries.** Simulated data: a generator ran the actual plant
  (Tier-1 `ReducedPlant` integrating the theory's shape ODEs, or the Tier-2
  Drake `MultibodyPlant` with SAP contact, distance-constraint cables, and
  hydrodynamic drag) under a **seeded** RNG and wrote a committed record; the
  figure reads that record. Every named record was `ls`-confirmed present on
  disk (`tier2_drake/results/s1/*.{json,npz}`, `tier1_sheaf/results/*.{json,csv}`)
  and opened to confirm it holds real arrays, not a stub — e.g.
  `d7_scorecard.json` = 200 seed×arm dicts (50 transits/arm),
  `hero_dogleg_series.npz` = float arrays `ts/D/kern/comp/truth` of length 4501,
  `hero_ghost_tracks.npz` = `ts/truth/ghost_paper/ghost_b0/t_on/seed`,
  `hero_series.npz` = `ts/errs/D/truth`, `e3b_production.json` = 1584 runs. A
  seeded `np.random.default_rng(seed)` is **reproducible simulation noise = real
  simulated data, not fabrication**. `ral_forest.pdf` is a SIM ledger-
  transcription (see its entry): its CIs are transcribed from the
  `docs/ral_package.md` adjudication, and **each value traces to a named,
  present, committed record**.
- **[DET] — 1 entry.** `tcns_e1_spectrum` (Fig. 6) recomputes an analytic
  operator at plot time: it assembles the sheaf Laplacian L_F from
  `tier1_sheaf/sheaf/laplacian.sheaf_laplacian` at fixed shapes and takes its
  eigenvalues, plus an anchored variant — exact linear algebra, no record read
  and no RNG. Every *other* data-bearing figure reads a committed record; the
  deterministic operators (`holonomy_amplitude_m2`, `two_agent_commutator`, …)
  run inside the generators that *produced* those records, not at plot time.
- **[DIAGRAM] — 5 entries.** Conceptual/schematic panels with **no measured
  data**: `ral_scenario`, `ral_staleness`, `ral_architecture` (superseded by the
  TikZ `fig:arch`), `ral_failure_taxonomy` (superseded by the TikZ
  `fig:taxonomy`), and `hero_montage.png` (a non-evidentiary movie still). Each
  is labelled as a diagram and must never read as a measurement.
- **[FLAG] — 0 entries now, but one fabrication was found and fixed.**
  `tcns_e1_spectrum` shipped **fabricated** until 2026-07-22: its generator's
  real `sheaf_laplacian` call failed on a wrong API signature, and an inner
  `try/except` silently substituted a hand-typed eigenvalue array
  `[0, 0, 0, 2.1, 2.4, 3.0, 3.3, 4.1, 5.5]`. The fallback was removed and
  replaced with loud asserts, and the figure regenerated from the real operator
  (see its entry). A sweep of every figure generator confirmed this was the
  **only** silent-fallback site: the two remaining `except` blocks in
  `tcns_figs_ieee.py` / `ral_figs_ieee.py` are `__main__` loop guards that print
  `FAIL` and substitute nothing. (The WIP `analysis/.../b3_relpose.py` is
  explicitly excluded — "synthetic … DESIGN INCOMPLETE" — and feeds **no** paper
  figure, so it is not among the 30.)

**Finding:** every data figure traces to a committed **simulated** record
(Tier-1 `ReducedPlant` or Tier-2 Drake `MultibodyPlant`, seeded RNG) or, in the
single [DET] case, to an exact recomputation from a released operator; the
diagrams are labelled as such; the one ledger-summary figure (`ral_forest`)
transcribes CIs that each trace to a named committed record. **Nothing here is
fabricated as of 2026-07-22 — one figure (`tcns_e1_spectrum`) was found
fabricated and was corrected at the generator, not patched over.** The two
epistemic objects stay separate
throughout: the τ²/ε **amplitude** is [PROVEN] (Theorem 3 `thm:floorF`,
Corollary 3 `cor:symF`), while the closed-loop **D_ss** slope is [CONJECTURAL]
and *measured* — never captioned as validating the theorem.

## How these were generated

Three committed generators, all reading only the committed record files, all
sharing one style module:

- **`tier2_drake/campaign/ral_figs_ieee.py`** — the primary paper-figure
  generator. One single-axes plot per figure, written to
  `tier2_drake/results/s1/artifacts/ieee/`, then copied into this folder. It
  reads the Drake records in `tier2_drake/results/s1/` (`d7_scorecard.json`,
  `hero_ghost_tracks.npz`, `hero_dogleg_series.npz`, `hero_series.npz`,
  `hero_v2_ensemble.json`, `d3_amplitude.json`, `production_d2_d4_v2.json`,
  `d2_a1_a2_arms.json`, `d9_scaling.json`, `d10b_loss.json`, `d10c_guard.json`)
  and the Tier-1 record `tier1_sheaf/results/e3b_production.json` (for the F4b
  overlay).
- **`tier1_sheaf/campaign/tcns_figs_ieee.py`** — the `tcns_f5_amp`,
  `tcns_f5_floor`, and `tcns_f8` panels, from Tier-1 records
  `e3c_symmetry.json`, `e3c_c9b_seeds.json` (`_paired_estimator`), and
  `e2_contraction.json`. (`tier1_sheaf/campaign/f5_symmetry_fig.py` builds the
  combined two-panel `f5_symmetry` alternate.)
- **`analysis/figures/ral_artifacts.py`** and the `analysis/figures/f4*_*.py`
  overlay scripts — build the pre-composition `f4a_overlay` / `f4b_overlay` /
  `f4c_variance_attribution` / `f4_cross_tier_overlay` panels and the earlier
  `ral_scenario` / `ral_architecture` / `ral_scorecard_stats` / `ral_robustness`
  / `ral_failure_taxonomy` variants (from the same `results/s1/*.json,*.npz`).

**Shared style** — `analysis/ieee_style.py` (`apply_ieee`): STIXGeneral serif
at 8 pt with STIX math, single-column 3.5 in / double-column 7.16 in figure
widths, Type-42 embedded fonts, vector PDF saved at 400 dpi, and a
grayscale-safe Okabe-Ito palette where every series carries a distinct
(colour, linestyle, marker) triple so nothing depends on colour alone. All
PDFs here are **vector** with committed generators, so they are re-buildable
and editable; the one raster file (`hero_montage.png`) is a movie still.

## Figure catalogue

Grouped by figure; near-duplicate variants and pre-composition sources fold
into the entry for the figure they feed.

### `ral_scenario.pdf`
- **`ral_scenario.pdf`** — vector PDF. USED as **Fig. 1** (`fig:scenario`) —
  "The Blind Harbor Transit: a GNSS-denied dogleg channel, with one
  range-limited docking beacon at a single vessel."
- *Depicts:* the dogleg channel (two legs, one 60° turn) in the world ENU
  plane (metres), the pentagon caisson under tow, and the single docking beacon
  with its range ring at one vessel.
- *Why / how:* a schematic panel from `ral_figs_ieee.py:fig_scenario`,
  fixing the task geometry — absolute information exists *only* near the dock
  and only at one vessel.
- *Significance:* establishes the premise (GNSS-denied 400 m transit, one
  5 Hz beacon) that makes the gauge and its single-anchor pinning the paper's
  subject. Framing figure, no verdict.
- *Theory:* Framing for **Theorem 1 (`thm:gaugeF`, "Exact residual
  unobservability = one global gauge") [PROVEN]** and **Corollary 1 (`cor:pinF`,
  "Pinning") [PROVEN]** — it fixes the geometry (one beacon at one vessel) in
  which the global SE(2) gauge exists and a single anchor can pin it. No theorem
  is tested here; it establishes the premise.
- *Provenance:* **[DIAGRAM]** — conceptual scenario schematic
  (`ral_figs_ieee.py:fig_scenario`), no measured data.

### `ral_staleness.pdf`
- **`ral_staleness.pdf`** — vector PDF. USED as **Fig. 2** (`fig:staleness`) —
  "The information-staleness ladder: local sensing is fast, shared estimates
  are τ-stale, absolute fixes exist only at the dock."
- *Depicts:* a timing ladder of the estimator's channels — 50 Hz odometry,
  20 Hz cable direction, 5 Hz beacon, down to the τ-stale neighbor channel.
- *Why / how:* schematic from `fig_staleness`; names the central variable τ.
- *Significance:* motivates "the price of staleness": proven τ² at the
  error-transport level, measured ≈τ^1.08 for the stochastic closed-loop floor
  ([CONJECTURAL] regime). Framing figure.
- *Theory:* Names the variable τ of **Lemma 3 (`lem:bchF`, "Group-commutator
  defect")** and **Theorem 3 (`thm:floorF`, "Latency–curvature floor")
  [PROVEN]**; motivates the empirical "price of staleness" thesis (proven τ² at
  the error-transport level vs. the *measured* [CONJECTURAL] closed-loop floor).
  Framing, not a test.
- *Provenance:* **[DIAGRAM]** — conceptual timing-ladder schematic
  (`fig_staleness`), no measured data.

### `ral_transit.pdf` (+ unused `ral_transit_filmstrip.pdf`)
- **`ral_transit.pdf`** — vector PDF. USED as **Fig. 3** (`fig:filmstrip`) —
  "The recorded transit: the pentagon barge towed by five ASVs on cables
  (coloured triangles) through the GNSS-denied dogleg, drawn at five instants
  along its ground-truth trail. From the committed multibody run (seed 3)."
- **`ral_transit_filmstrip.pdf`** — vector PDF. NOT used in the submitted
  paper — superseded filmstrip alternate of `ral_transit`, kept as a layout
  variant.
- *Depicts:* world-ENU (metres) ground-truth trail of the N=5 tow at five
  snapshots; caisson polygon plus five vessel triangles and their cables.
- *Why / how:* `fig_transit` reads the committed Drake `hero_dogleg_series.npz`
  (seed 3); five equal-time beats along the recorded truth path.
- *Significance:* shows the physical scenario really executed in the multibody
  plant. Descriptive, no verdict.
- *Theory:* No theorem — descriptive evidence that the physical scenario really
  executed in the Drake multibody plant; empirical grounding for the "price of
  staleness" study.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `tier2_drake/results/s1/hero_dogleg_series.npz` (seed 3; confirmed present,
  float arrays `ts/D/kern/comp/truth`).

### `ral_cables.pdf` (+ unused `ral_cable_constraint.pdf`)
- **`ral_cables.pdf`** — vector PDF. USED as **Fig. 4** (`fig:cables`) —
  "Constraint satisfaction through the transit: the load-to-vessel distances
  hold in the taut band (12 m cable plus the barge attachment radius) — the
  distance-constraint cables never go slack, even through the dogleg."
- **`ral_cable_constraint.pdf`** — vector PDF. NOT used — superseded alternate
  of `ral_cables`, kept as a variant.
- *Depicts:* load-to-vessel distances (metres) vs. transit time (s), one trace
  per cable, against the taut band (12 m cable + 4 m attachment radius).
- *Why / how:* `fig_cables` from `hero_dogleg_series.npz`; the bilateral
  distance-constraint cables are structurally taut.
- *Significance:* documents the plant's validity domain — bilateral cables
  *cannot* slack, which is exactly why slack events (D10a) are scoped out of v1
  as a measured boundary, not a result.
- *Theory:* No theorem — documents the plant's validity domain (bilateral
  distance-constraint cables stay taut), scoping the D10a slack boundary out of
  v1; supports **Definition 1 (`def:sheafF`, "Estimation sheaf; sheaf
  Laplacian")** as the operating regime in which taut cables are the measurement
  channel.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_dogleg_series.npz` (confirmed present).

### `ral_architecture.pdf`
- **`ral_architecture.pdf`** — vector PDF. NOT used in the submitted paper —
  the paper's architecture figure (`fig:arch`) is the TikZ `\input{fig_arch.tex}`
  in `main.tex`, not this rendered PDF; kept as the matplotlib-rendered
  alternate of the DIEKF-Σ pipeline / plant–estimator boundary diagram.
- *Depicts:* the per-agent DIEKF-Σ block diagram (invariant propagation,
  direction update with broadside guard, executed-composite delayed fusion,
  beacon channel) with the linted plant/estimator boundary.
- *Why / how:* `ral_artifacts.py:fig_architecture`, schematic.
- *Significance:* illustrates the machine-checked truth-isolation boundary.
  Conceptual, no verdict; superseded by the TikZ version in the manuscript.
- *Theory:* Illustrates the DIEKF-Σ pipeline realizing **Lemma 2 (`lem:edge`,
  "Edge maps are shape-only and locally computable")** and **Definition 1
  (`def:sheafF`)**; no theorem tested.
- *Provenance:* **[DIAGRAM]** — conceptual block diagram
  (`ral_artifacts.py:fig_architecture`), no measured data; superseded by the
  TikZ `fig:arch`.

### `tcns_e1_spectrum.pdf`
- **`tcns_e1_spectrum.pdf`** — vector PDF. USED as **Fig. 6** (`fig:gaugespec`) —
  "The gauge, computed directly rather than inferred: the sheaf Laplacian L_F
  (Def. 1) has exactly three eigenvalues at machine zero — ker L_F ≅ se(2), the
  one global SE(2) gauge of Thm 1 — and a single full-rank anchor lifts all
  three off zero, its λ_min = 0.18 becoming the relevant rate (Cor. 1)."
- *Depicts:* the nine eigenvalues of the sheaf Laplacian L_F (dimensionless;
  shape-only, no physical unit) as grouped log-scale bars over mode index 0–8 —
  the unanchored spectrum beside the one-anchor spectrum. Modes 0–2 sit in the
  shaded machine-zero band (≤ 1.1×10⁻¹⁵) unanchored and lift to ≈0.18–0.27 with
  one anchor; modes 3–8 (1.16, 1.38, 3.00, 4.07, 6.56, 7.83) are essentially
  unchanged.
- *Why / how:* `tier1_sheaf/campaign/tcns_figs_ieee.py:fig_e1_spectrum`
  assembles `sheaf_laplacian(SHAPES, EDGES, weights=[1,1,1], l=1.0)` on the
  three-agent triangle of `experiments/e1_gauge.py`
  (SHAPES = [(0.4, 0.3), (0.9, −0.5), (−0.7, 0.6)], EDGES the 3-cycle), takes
  `eigvalsh`, then adds a full-rank vertex potential (+1.0·I on agent 0's 3×3
  load block) for the anchored arm. Exact linear algebra — no simulation, no
  RNG, no record read.
- *Significance:* the most direct evidence in the paper for the gauge theorem —
  dim ker L_F = 3 is *exhibited*, not inferred from closed-loop drift, and the
  single-anchor collapse is shown on the same axes. Shared with T-CNS §VIII
  (there `fig:f3`). Structural and shape-only, hence **plant-independent: this
  is not a Drake result** and the caption says so; the closed-loop realization
  is Figs. 9–10.
- *Theory:* **Theorem 1 (`thm:gaugeF`, "Exact residual unobservability = one
  global gauge") [PROVEN]** — the three machine-zero modes *are* ker L_F ≅
  se(2); and **Corollary 1 (`cor:pinF`, "Pinning") [PROVEN]** — one full-rank
  anchor sends ker → 0 with λ_min becoming the rate. Also exercises
  **Definition 1 (`def:sheafF`)**, whose L_F it assembles.
- *Provenance:* **[DET]** — exact recomputation from the released operator
  `tier1_sheaf/sheaf/laplacian.sheaf_laplacian` at fixed shapes.
  **⚠ Corrected 2026-07-22:** the previously shipped PDF was **fabricated** —
  the generator's real `sheaf_laplacian` call failed on a wrong API signature
  and an inner `try/except` silently substituted a hand-typed array
  `[0, 0, 0, 2.1, 2.4, 3.0, 3.3, 4.1, 5.5]`. That fallback has been removed and
  replaced with asserts (`dim ker == 3` unanchored, `== 0` anchored) that fail
  loudly, so a future regression surfaces as a build failure instead of fake
  eigenvalues. The current PDF is the genuine spectrum.

### `ral_hero_traj.pdf` (+ unused `ral_hero_series.pdf`)
- **`ral_hero_traj.pdf`** — vector PDF. USED as **Fig. 7** (`fig:heroseries`) —
  "The recorded 450 s dogleg transit truth (from the committed
  `hero_dogleg_series.npz`): barge trajectory with the turn and beacon windows
  marked."
- **`ral_hero_series.pdf`** — vector PDF. NOT used — superseded alternate of
  the hero-transit series (`ral_artifacts.py:fig_hero_series`), kept as a
  variant.
- *Depicts:* world-ENU (metres) ground-truth barge trajectory over the 450 s
  transit, with the 60° turn and beacon-acquisition windows annotated.
- *Why / how:* `fig_hero_traj` from `hero_dogleg_series.npz`.
- *Significance:* grounds the pinning narrative in the recorded transit.
  Descriptive.
- *Theory:* No theorem — descriptive; grounds the **Corollary 1 (`cor:pinF`)**
  pinning narrative in the recorded 450 s transit.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_dogleg_series.npz` (confirmed present).

### `ral_hero_D.pdf`
- **`ral_hero_D.pdf`** — vector PDF. USED as **Fig. 8** (`fig:heroD`) —
  "Disagreement D(t) vs. the gauge-kernel component along the same transit: the
  maneuver excites the former; only the beacon kills the latter; the acquisition
  spike in D is the pin shock."
- *Depicts:* two time series over the transit (s) — the inter-agent
  disagreement D(t) (m²) and the kernel-projected gauge-error component; the
  D(t) **spike** at beacon acquisition.
- *Why / how:* `fig_hero_D` from `hero_dogleg_series.npz`. The kernel component
  grows unbounded under GNSS denial (rigid gauge orbit) and is killed only by
  the beacon; D spikes because the anchored agent snaps to truth against a
  fleet still carrying the drifted gauge (τ_net ≈ 21 s on C₅).
- *Significance:* **Cor. 5.2 [PROVEN] in closed loop** — a single anchor pins
  the whole fleet through fusion, and beacon activation momentarily *breaks*
  agreement before the pin propagates. The spike is the pin shock, not an
  artifact; D is a disagreement metric, never a correctness ranking.
- *Theory:* **Corollary 1 (`cor:pinF`, "Pinning") [PROVEN] live in closed loop**
  — a single anchor pins the whole fleet through fusion, the acquisition spike
  being the pin shock; the kernel-projected component is exactly **Theorem 1
  (`thm:gaugeF`)**'s one common SE(2) gauge that only the beacon kills.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_dogleg_series.npz` (confirmed present, `ts/D/kern/comp` arrays).

### `ral_gauge_trails.pdf` (+ unused `ral_gauge_orbit.pdf`)
- **`ral_gauge_trails.pdf`** — vector PDF. USED as **Fig. 9** (`fig:gaugeorbit`)
  — "Cor. 5.2 in the closed loop, spatially: the five agents' load-pose
  estimates (colours) stay a tight, consistent fleet but drift as a group off
  the truth (black) through GNSS denial, then collapse toward it once the dock
  beacon is acquired (solid → dashed). From the committed `hero_ghost_tracks.npz`
  (seed 3)."
- **`ral_gauge_orbit.pdf`** — vector PDF. NOT used — superseded alternate of
  the gauge-orbit view, kept as a variant.
- *Depicts:* world-ENU (metres) — five per-agent load-pose estimate tracks
  (coloured) tight to each other but offset from truth (black); solid pre-beacon,
  dashed post-beacon collapse.
- *Why / how:* `fig_gauge_trails` from `hero_ghost_tracks.npz` (seed 3).
- *Significance:* the spatial face of **Cor. 5.2 [PROVEN]**: consistent fleet,
  coherent gauge drift, single-anchor pin. Harmonic sections = one common
  SE(2) load-frame perturbation.
- *Theory:* **Theorem 1 (`thm:gaugeF`) [PROVEN]** spatially — the coherent
  fleet drift IS the single common SE(2) harmonic section (ker L_F ≅ se(2)) —
  together with **Corollary 1 (`cor:pinF`) [PROVEN]** single-anchor collapse.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_ghost_tracks.npz` (seed 3; confirmed present,
  `ts/truth/ghost_paper/ghost_b0` arrays).

### `ral_gauge_err.pdf`
- **`ral_gauge_err.pdf`** — vector PDF. USED as **Fig. 10** (`fig:gaugeerr`) —
  "The fleet gauge error (mean estimate vs. truth) grows to tens of metres under
  GNSS denial and is killed by the single dock anchor."
- *Depicts:* fleet-mean gauge error (metres) vs. time (s), rising into tens of
  metres, then collapsing at the anchor.
- *Why / how:* `fig_gauge_err` from `hero_ghost_tracks.npz`.
- *Significance:* magnitude of the gauge drift the single anchor removes —
  **Cor. 5.2 [PROVEN]**. States the realized gauge error as a measured fact.
- *Theory:* **Corollary 1 (`cor:pinF`, "Pinning") [PROVEN]** — the magnitude of
  gauge drift (tens of metres) that the single dock anchor removes; stated as a
  measured fact.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_ghost_tracks.npz` (confirmed present).

### `ral_agent_errors.pdf`
- **`ral_agent_errors.pdf`** — vector PDF. USED as **Fig. 11** (`fig:agenterr`)
  — "Per-agent load-pose error at the 130 s calibration horizon (recorded
  `hero_series.npz`): the beacon at agent 0 (gold, from 30 s) propagates through
  fusion to the whole fleet — at this horizon. The 450 s failure of this picture
  is the gain-starvation finding of Fig. `v2seeds`."
- *Depicts:* per-agent load-pose error (metres) vs. time (s) to the **130 s**
  horizon; agent 0's beacon (from 30 s) pulling the fleet down through fusion.
- *Why / how:* `fig_agent_errors` from `hero_series.npz`.
- *Significance:* the anchor propagates cleanly **at the S1 (130 s) horizon**;
  the contrast row for the long-horizon starvation. Carries its horizon — the
  M-FAB gate closes at 130 s (ANEES 3.96) and does **not** transfer to 450 s
  transits (ANEES 159–229).
- *Theory:* Empirical support for **Corollary 1 (`cor:pinF`)** at the 130 s S1
  horizon — the anchor propagates through fusion — carrying its horizon; not a
  long-transit claim (450 s ANEES 159–229). Empirical, not a theorem test.
- *Provenance:* **[SIM]** — reads the committed Drake record `hero_series.npz`
  (confirmed present, `ts/errs/D/truth` arrays, 130 s horizon).

### `ral_score_box.pdf` + `ral_score_cdf.pdf` (+ unused `ral_scorecard_stats.pdf`)
- **`ral_score_box.pdf`** — vector PDF. USED as **Fig. 12** (`fig:scorestats`)
  — "The 50-transit scorecard: fleet-mean dock error per arm (log scale — B0's
  failure is two orders, not a tail)."
- **`ral_score_cdf.pdf`** — vector PDF. USED as **Fig. 13** (`fig:scorecdf`) —
  "Per-seed CDFs of the fleet-mean dock error: the ordering
  B1ˡⁱᵐ > paper > B2 ≫ B0 holds seed-wise; the 0.5 m spec is left of every
  support (0% success at plan-faithful acquisition)."
- **`ral_scorecard_stats.pdf`** — vector PDF. NOT used — superseded combined
  (box + CDF) alternate from `ral_artifacts.py:fig_scorecard_stats`; the paper
  uses the two split panels above.
- *Depicts:* box: fleet-mean dock error (m, log scale) per arm; CDF: per-seed
  cumulative distributions with the 0.5 m spec line. Arms: B1-limit, DIEKF-Σ,
  B2 consensus, B0 dead-reckon (and A2 in the table).
- *Why / how:* `fig_score_box` / `fig_score_cdf` from `d7_scorecard.json`
  (50 dogleg transits/arm). Fleet-mean 0.76 / 1.57 / 2.13 / 66.7 m; D
  0.72 / 2.85 / 3.37 / 9624. Seed-paired, the paper rule beats B2 41/50 and B0
  50/50; the zero-latency limit beats the paper rule 47/50.
- *Significance:* finding (ii) rule ranking — **the ordering on D and fleet-mean
  holds** (paper > B2 ≫ B0; B1-limit reference above all). **Docking <0.5 m:
  0% of ALL arms** at plan-faithful acquisition, including the zero-latency
  limit — the approach geometry, not the estimator, binds. B1 is the record's
  own zero-latency all-to-all limit, a **reference, not an oracle**.
- *Theory:* No theorem — the empirical "price of staleness" rule-ranking thesis
  (finding ii) and the **D7 falsifier scorecard**; empirical validation of
  **Corollary 1 (`cor:pinF`)** under staleness, with the docking spec measured
  (0% < 0.5 m across all arms).
- *Provenance:* **[SIM]** — reads the committed Drake record `d7_scorecard.json`
  (confirmed present; 200 seed×arm records, 50 dogleg transits/arm).

### `ral_v2seeds.pdf` (+ unused `ral_v2_seeds.pdf`)
- **`ral_v2seeds.pdf`** — vector PDF. USED as **Fig. 14** (`fig:v2seeds`) —
  "Hero v2 (decelerating approach), all 12 seeds sorted: fleet-mean vs.
  anchored-agent dock error. Median 0.61 m, 17% under spec — improvement without
  sufficiency; the anchored agent is worse than the fleet mean on 11/12 seeds
  (gain starvation); best/median/worst marked, worst shown."
- **`ral_v2_seeds.pdf`** — vector PDF. NOT used — underscore-named twin of the
  same figure (`ral_artifacts.py:fig_v2_seeds`); the paper includes the
  no-underscore `ral_v2seeds.pdf` from `ral_figs_ieee.py`.
- *Depicts:* all 12 hero-v2 seeds sorted — fleet-mean vs. anchored-agent dock
  error (metres); best/median/worst marked, worst (fleet-mean 2.1 m) shown.
- *Why / how:* `fig_v2seeds` from `hero_v2_ensemble.json`. The decelerating
  approach improves fleet-mean 2.4× (median 0.61 m; 17% of seeds < 0.5 m); the
  anchored agent starves (sustained Kalman anchoring collapses its covariance;
  CI keeps unanchored gains healthy); trim-contamination tested and falsified
  (frozen-trim bit-identical).
- *Significance:* the tested remedy — **necessary but the spec remains UNMET**;
  exposes anchored-agent gain starvation honestly. Not a positive docking
  result.
- *Theory:* No theorem — the empirical docking-remedy thesis (the D7 scorecard
  remedy path); exposes anchored-agent gain starvation; spec UNMET.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_v2_ensemble.json` (12 seeds; confirmed present).

### `ral_docking_zoom.pdf`
- **`ral_docking_zoom.pdf`** — vector PDF. USED as **Fig. 15** (`fig:docking`) —
  "The docking outcome at the dock (5 m zoom): the fleet's load-pose estimate
  sits about a metre from the truth barge centre, outside the 0.5 m spec ring."
- *Depicts:* world-ENU (metres), 5 m zoom on the dock — fleet load-pose estimate
  vs. truth barge centre and the 0.5 m spec ring.
- *Why / how:* `fig_docking_zoom` from `hero_ghost_tracks.npz`.
- *Significance:* visual of the ~1 m miss — **spec UNMET**, the binding
  constraint is the approach geometry.
- *Theory:* No theorem — the empirical docking outcome (~1 m miss); the D7
  spec-UNMET finding, approach geometry binds.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_ghost_tracks.npz` (confirmed present).

### `ral_docking_cdf.pdf`
- **`ral_docking_cdf.pdf`** — vector PDF. USED as **Fig. 16** (`fig:dockingcdf`)
  — "Across seeds, the decelerating approach (v2) improves the fleet-mean dock
  error (median 0.61 m) but 83% of seeds still miss the 0.5 m spec — the approach
  geometry, not the estimator, binds."
- *Depicts:* CDF of fleet-mean dock error (metres) across the v2 seeds vs. the
  0.5 m spec.
- *Why / how:* `fig_docking_cdf` from `hero_v2_ensemble.json`.
- *Significance:* v2 improves but **83% of seeds still miss spec — UNMET**.
- *Theory:* No theorem — the empirical docking-spec thesis (D7 remedy path); v2
  improves the fleet-mean but 83% of seeds still miss the 0.5 m spec.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_v2_ensemble.json` (confirmed present).

### `ral_baseline_tracks.pdf`
- **`ral_baseline_tracks.pdf`** — vector PDF. USED as **Fig. 17**
  (`fig:baseline`) — "Why the sheaf transport is load-bearing: fleet load-pose
  estimate tracks. The DIEKF-Σ (blue) follows the truth and is pinned at the
  beacon; B0 dead-reckoning (red) walks away."
- *Depicts:* world-ENU (metres) — DIEKF-Σ estimate track (blue, pinned at
  beacon) vs. B0 dead-reckoning (red, diverging) against truth.
- *Why / how:* `fig_baseline_tracks` from `hero_ghost_tracks.npz`.
- *Significance:* finding (ii) — the sheaf transport is load-bearing; naive
  dead-reckoning cannot use the single anchor. Descriptive support.
- *Theory:* Empirical finding (ii) — the shape-conjugated sheaf transport is
  load-bearing; naive dead-reckoning cannot use the single anchor (contrast for
  **Corollary 1 (`cor:pinF`)**). Descriptive support, not a theorem test.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_ghost_tracks.npz` (confirmed present).

### `ral_baseline_err.pdf` (+ unused `ral_baseline_divergence.pdf`)
- **`ral_baseline_err.pdf`** — vector PDF. USED as **Fig. 18**
  (`fig:baselineerr`) — "Fleet-mean load error: the sheaf fusion propagates the
  single anchor to the whole fleet at the dock, collapsing to ~1 m;
  dead-reckoning cannot, and diverges (matching the 1.6 vs. 67 m scorecard
  means)."
- **`ral_baseline_divergence.pdf`** — vector PDF. NOT used — superseded
  alternate of `ral_baseline_err`, kept as a variant.
- *Depicts:* fleet-mean load error (metres) vs. time (s) — DIEKF-Σ collapsing
  to ~1 m at dock vs. B0 diverging.
- *Why / how:* `fig_baseline_err` from `hero_ghost_tracks.npz`; matches the
  1.57 vs. 66.7 m scorecard fleet-means.
- *Significance:* finding (ii) — fusion propagates the single anchor to the
  whole fleet; naive dead-reckoning (B0) cannot use the anchor and diverges to
  the 66.7 m scorecard fleet-mean. Support for the load-bearing transport claim.
- *Theory:* Empirical finding (ii) — fusion propagates the single anchor to the
  fleet (**Corollary 1 (`cor:pinF`)** in effect) while B0 cannot; matches the
  1.57 vs. 66.7 m scorecard fleet-means. Empirical, not a theorem test.
- *Provenance:* **[SIM]** — reads the committed Drake record
  `hero_ghost_tracks.npz` (confirmed present).

### `ral_f4a.pdf` (+ source `f4a_overlay.pdf`)
- **`ral_f4a.pdf`** — vector PDF. USED as **Fig. 19** (`fig:f4a`) —
  "Error-transport holonomy amplitude on both plants. Thm 7.2 (leading-order,
  deterministic): Tier-1 slope 1.999 with switch-offs at machine zero; Drake
  slope 2.000 with the m=2 coefficient check at 1.0000, the η=0 switch-off at
  machine zero, and the parallel class suppressing the coefficient 31×
  (achieved-ε; exact cancellation remains the Tier-1 machine-zero result)."
- **`f4a_overlay.pdf`** — vector PDF. NOT used directly — the pre-composition
  overlay panel (`analysis/figures/f4a_overlay.py`) that `ral_f4a` renders in
  IEEE style; kept as the editable source.
- *Depicts:* log-log ‖Log Hol(γ)‖ (holonomy amplitude) vs. staleness τ, both
  plants; fitted slopes and switch-off arms.
- *Why / how:* `fig_f4a` from `d3_amplitude.json` (Drake) + the Tier-1
  `e3a_amplitude.csv` fit. Amplitude ∝ τ²; symmetric-class switch-offs are
  machine-zero (ξ=0 literally 0.0 on Tier-1).
- *Significance:* **Thm 7.2 [PROVEN], PASSED both plants** — slope 1.999 (T1) /
  2.000 (Drake), coefficient 1.0000, switch-offs machine-zero, parallel class
  31× on Drake (achieved-ε; exact on Tier-1). This is the **error-transport
  holonomy amplitude object** — do not conflate with the D_ss floor.
- *Theory:* **Theorem 3 (`thm:floorF`, "Latency–curvature floor") [PROVEN,
  leading order]** — the measured slope ≈2 IS the theorem's amplitude claim
  (log Hol(γ) = τ²Σₖαₖ[C_{j_k},C_{j_{k+1}}] + O(τ³)) — with **Corollary 3
  (`cor:symF`, "Symmetry protection")** switch-offs (symmetric class / ξ=0
  machine-zero on Tier-1). The error-transport holonomy amplitude object, NOT
  the D_ss floor.
- *Provenance:* **[SIM]** — reads the committed records `d3_amplitude.json`
  (Drake) and `tier1_sheaf/results/e3a_amplitude.csv` (Tier-1 fit); both
  confirmed present.

### `ral_f4b.pdf` (+ source `f4b_overlay.pdf`)
- **`ral_f4b.pdf`** — vector PDF. USED as **Fig. 20** (`fig:f4b`) —
  "Tier-1/Tier-2 agreement on the conjectured steady-state floor. … With D₀
  measured in situ by straight-tow controls, the fitted excess exponents are
  1.101 [1.076, 1.125] (Tier-1) and 1.077 [1.054, 1.102] (Drake); the
  pre-registered equivalence test passes (+0.023 [−0.012, +0.057] ⊂ [−0.2, 0.2])
  and the conjectured order 2 is excluded on both plants…"
- **`f4b_overlay.pdf`** — vector PDF. NOT used directly — pre-composition
  overlay (`analysis/figures/f4b_overlay.py`); editable source for `ral_f4b`.
- *Depicts:* log-log closed-loop steady-state disagreement D_ss (m²) vs.
  staleness τ, both plants, with D₀ measured in situ; fitted excess-exponent
  lines and the cross-tier equivalence box.
- *Why / how:* `fig_f4b` from `production_d2_d4_v2.json` (Drake) +
  `e3b_production.json` (Tier-1, 1584 runs). D₀ measured by straight-tow
  controls, not fitted.
- *Significance:* **C7b FALSIFIED at these scales on two plants** — the
  conjectured order-2 steady-state floor is excluded; measured slopes
  1.101 (T1) / 1.077 (Drake), cross-tier **EQUIVALENT** (+0.023). This is the
  **D_ss floor [CONJECTURAL]** object — a *measured* slope in a conjectural
  regime, carried with the mixture caveat; the CIs exclude order 1 too, and
  **no first-order law is asserted**. Never read this as validating Thm 7.2.
- *Theory:* The **[CONJECTURAL] stochastic extension** of **Theorem 3
  (`thm:floorF`)** — the closed-loop steady-state floor D_ss — which the paper
  **FALSIFIES (falsifier C7b)**: measured excess exponents 1.101 (T1) /
  1.077 (Drake) exclude the conjectured order 2 (and 1). A DIFFERENT object from
  `ral_f4a`; never read as validating the proven amplitude theorem.
- *Provenance:* **[SIM]** — reads the committed records `production_d2_d4_v2.json`
  (Drake) and `tier1_sheaf/results/e3b_production.json` (Tier-1, 1584 runs; both
  confirmed present); D₀ measured in situ by straight-tow controls, not fitted.

### `ral_f4c.pdf` (+ source `f4c_variance_attribution.pdf`)
- **`ral_f4c.pdf`** — vector PDF. USED as **Fig. 21** (`fig:f4c`) — "All Drake
  arms on matched formation draws. Ablating the conjugated transport (A2) runs
  1.7×→8.2× above the paper rule with growing τ; naive consensus (A1) holds
  disagreement flat and low — by groupthink (anchored ANEES 62, drift 8.4 m;
  baselines cell, 130 s horizon): agreement alone is never a virtue metric. The
  straight-tow control shows the motion excitation (19–21× at every τ)."
- **`f4c_variance_attribution.pdf`** — vector PDF. NOT used directly —
  pre-composition overlay (`analysis/figures/f4c_attribution.py`); editable
  source for `ral_f4c`.
- *Depicts:* disagreement D (m²) vs. staleness τ for all Drake arms (paper rule,
  A2 unconjugated, A1 consensus, straight-tow control) on matched formation
  draws.
- *Why / how:* `fig_f4c` from `d2_a1_a2_arms.json`. A2 degrades 1.7→8.2× with τ;
  A1 stays flat by groupthink (ANEES 62, drift 8.4 m at the 130 s horizon);
  straight-tow control excites 19–21× (mechanism check, threshold ≥10×).
- *Significance:* finding (ii) variance attribution — **conjugated transport is
  load-bearing on Drake** (up to 8.2×); flat agreement is purchasable by
  groupthink and is exposed by every correctness metric. **Agreement (D) is
  never a correctness ranking.**
- *Theory:* No theorem — empirical variance attribution (finding ii): the
  Ad_m-conjugated transport of **Definition 1 (`def:sheafF`)** is load-bearing
  (A2 ablation degrades 1.7→8.2×), while flat agreement (A1) is purchasable by
  groupthink. Agreement D is never a correctness ranking.
- *Provenance:* **[SIM]** — reads the committed Drake record `d2_a1_a2_arms.json`
  (confirmed present).

### `ral_cross_tier.pdf` (+ unused `f4_cross_tier_overlay.pdf`)
- **`ral_cross_tier.pdf`** — vector PDF. USED as **Fig. 29**
  (`fig:ladderoverlay`, the paper's closing synthesis figure in the Discussion) — "The epistemic spine in one overlay: three distinct
  objects, three measured exponents — Tier-1 ‖Log Hol‖ (p = 2.00, the theorem's
  object, [PROVEN]); the Drake round-trip transport defect (p = 1.00,
  estimate-mismatch dominated); and the Drake closed-loop D_ss (p = 1.08
  [1.05, 1.10], [CONJECTURAL] regime, D₀ measured by the straight-tow control
  19–21× below). Never conflated."
- **`f4_cross_tier_overlay.pdf`** — vector PDF. NOT used — pre-composition
  cross-tier ladder overlay (`analysis/figures/f4_overlay.py`); editable source
  variant of `ral_cross_tier`.
- *Depicts:* log-log, three superposed exponents vs. τ — holonomy amplitude
  (p=2.00), transport-mismatch channel (p=1.00), closed-loop D_ss (p≈1.08).
- *Why / how:* `fig_cross_tier` from `production_d2_d4_v2.json` and the Tier-1
  records; the three objects plotted separately with their own fits.
- *Significance:* the paper's **epistemic spine — three distinct objects, never
  conflated**: state-level mismatch (1.00), D_ss floor (1.08, [CONJECTURAL],
  measured not a law), error-transport holonomy (2.00, [PROVEN], resolved only
  noise-off). The guardrail figure against conflating the two floors.
- *Theory:* The epistemic spine — three distinct objects: **Theorem 3
  (`thm:floorF`)** amplitude [PROVEN] p=2.00, the state-mismatch transport
  channel p=1.00, and the [CONJECTURAL] D_ss floor p≈1.08. The guardrail against
  conflating the proven amplitude with the measured floor; never conflated.
- *Provenance:* **[SIM]** — reads the committed records `production_d2_d4_v2.json`
  (Drake) and the Tier-1 records (confirmed present).

### `tcns_f5_amp.pdf` (+ unused `f5_symmetry.pdf`)
- **`tcns_f5_amp.pdf`** — vector PDF. USED as **Fig. 22** (`fig:f5`) —
  "Symmetry, the amplitude object: the departure from the symmetric class is
  first-order in ε (measured 1.006, base commutator exactly zero) — PASSED."
- **`f5_symmetry.pdf`** — vector PDF. NOT used — the combined two-panel
  (amplitude + floor) symmetry figure (`tier1_sheaf/campaign/f5_symmetry_fig.py`);
  the paper splits it into the two `tcns_f5_*` panels.
- *Depicts:* log-log departure-from-symmetric amplitude vs. ε; slope ≈1, base
  commutator exactly zero.
- *Why / how:* `tcns_figs_ieee.py:fig_f5_amp` from `e3c_symmetry.json`.
- *Significance:* **C9b′ PASSED** — amplitude ε-exponent 1.006, base commutator
  exactly zero. Symmetry protection lives on the **amplitude object** (Cor. 7.3),
  not the floor. Never mixed with the D_ss floor.
- *Theory:* **Corollary 3 (`cor:symF`, "Symmetry protection") [PROVEN]** on the
  amplitude object — departure from the symmetric class is first-order in ε
  (falsifier C9b′ **PASSED**, 1.006; base commutator exactly zero). Lives on the
  amplitude object only, never the floor.
- *Provenance:* **[SIM]** — reads the committed Tier-1 record
  `tier1_sheaf/results/e3c_symmetry.json` (confirmed present).

### `tcns_f5_floor.pdf`
- **`tcns_f5_floor.pdf`** — vector PDF. USED as **Fig. 23** (`fig:f5floor`) —
  "Symmetry, the closed-loop floor [CONJECTURAL]: the seed-paired estimator
  gives slope 1.58 [1.44, 1.84] at every τ, excluding both 2 and 1 — a
  linear-plus-quadratic mixture the registered single-power model mis-specifies.
  Never mixed with the amplitude object."
- *Depicts:* log-log closed-loop D_ss excess vs. ε on the symmetric axis;
  seed-paired estimator slope 1.58.
- *Why / how:* `fig_f5_floor` from `e3c_symmetry.json` +
  `e3c_c9b_seeds.json` (`_paired_estimator`).
- *Significance:* **C9b — the falsifier condition is MET on the declared
  seed-paired estimator** (1.58 [1.44, 1.84]; both 2 and 1 excluded): the
  registered single-power model is mis-specified for a linear+quadratic mixture.
  The unpaired estimator [0.43, 2.89] is **UNDER-POWERED** and adjudicates
  nothing. Reported as a MET falsifier, not dressed as a pass; this is the
  D_ss floor object, never the amplitude object.
- *Theory:* The **[CONJECTURAL]** closed-loop D_ss floor on the symmetry (ε)
  axis — NOT **Corollary 3 (`cor:symF`)**'s amplitude claim; the **falsifier C9b
  condition is MET** on the declared seed-paired estimator (1.58 [1.44, 1.84],
  both 1 and 2 excluded): the registered single-power model is mis-specified for
  a linear+quadratic mixture.
- *Provenance:* **[SIM]** — reads the committed Tier-1 records
  `e3c_symmetry.json` and `e3c_c9b_seeds.json` (`_paired_estimator`; both
  confirmed present).

### `tcns_f8.pdf` (+ unused `f8_contraction.pdf`)
- **`tcns_f8.pdf`** — vector PDF. USED as **Fig. 25** (`fig:f8`) —
  "Contraction in its own domain (frozen, unanchored): rate versus κλ₂ across
  two topologies, slope 1.40 (falsifier < 0.5); μ calibrated at κ=0, so the
  identity line is anchored, not predicted. The log-linearity remainder vanishes
  faster than the registered second order (2.48 [2.32, 2.65]; falsifier band
  excluded on the favorable side, reported as tripped with the corrected order)."
- **`f8_contraction.pdf`** — vector PDF. NOT used — alternate rendering of the
  contraction figure, kept as a variant.
- *Depicts:* contraction rate vs. κλ₂ across two topologies; slope 1.40; the
  identity line anchored via μ calibrated at κ=0.
- *Why / how:* `tcns_figs_ieee.py:fig_contraction` from `e2_contraction.json`.
- *Significance:* **C6 contraction PASSED** — slope 1.403 across two topologies;
  μ=−0.062 topology-independent (the consensus term does the contraction).
  Note **C19: the remainder falsifier TRIPPED (2.48)** but on the *favorable*
  side (remainder vanishes faster than 2nd order) — restated with corrected
  order, **not counted as a pass**.
- *Theory:* **Theorem 2 (`thm:contractF`, "Frozen-linearization contraction")
  [PROVEN, LTV level]** — rate ∝ κλ₂ (falsifier C6 **PASSED**, slope 1.403,
  μ=−0.062 topology-independent, the consensus term does the contraction); the
  **C19 remainder falsifier TRIPPED (2.48)** but on the favorable side —
  restated with corrected order, not a pass.
- *Provenance:* **[SIM]** — reads the committed Tier-1 record
  `e2_contraction.json` (confirmed present).

### `ral_d9.pdf` (+ unused `d9_topology.pdf`)
- **`ral_d9.pdf`** — vector PDF. USED as **Fig. 24** (`fig:d9`) — "Connectivity
  buys agreement, not anchoring. The pre-anchor floor improves with λ₂ (a);
  single-anchor pinning is anchor-rate-limited (b, Spearman +0.04); re-agreement
  around the pin *anti*-orders with connectivity (c, −0.51 [−0.65, −0.36]). …
  this is the pre-registered ES-01 finding path, reported as such."
- **`d9_topology.pdf`** — vector PDF. NOT used — superseded topology-panel
  alternate of `ral_d9`, kept as a variant.
- *Depicts:* three panels — (a) pre-anchor floor vs. λ₂ (improves); (b) pin rate
  vs. λ₂ (Spearman +0.04 ≈ 0); (c) re-agreement vs. λ₂ (−0.51, anti-ordering).
- *Why / how:* `fig_d9` from `d9_scaling.json` (topology × N sweep).
- *Significance:* **D9 falsifier FIRES** — pin rate ρ=+0.04 ≈ 0 means the pin is
  **anchor-limited, not connectivity-limited**; D re-agreement **anti-orders**
  (−0.51: stiff consensus resists the pin). Connectivity buys agreement, not
  anchoring — reported as the ES-01 finding path, never as a positive result.
- *Theory:* Empirical test of the connectivity dependence of **Corollary 1
  (`cor:pinF`)** — the **D9 falsifier FIRES**: pin rate ρ=+0.04 ≈ 0
  (anchor-limited, not connectivity-limited), re-agreement anti-orders −0.51.
  Connectivity buys agreement, not anchoring; the ES-01 finding path, not a
  positive result.
- *Provenance:* **[SIM]** — reads the committed Drake record `d9_scaling.json`
  (topology × N sweep; confirmed present).

### `ral_robust_drops.pdf` (+ unused `ral_robustness.pdf`)
- **`ral_robust_drops.pdf`** — vector PDF. USED as **Fig. 26** (`fig:robust`) —
  "D10(b) robustness (outside class P): floor vs. packet-drop probability,
  drops-only and drops+jitter arms (8 seeds each; mean ± sd) — graceful, no red
  flags; anchored ANEES in-gate at p=0.3 at the 130 s horizon."
- **`ral_robustness.pdf`** — vector PDF. NOT used — superseded combined
  (drops + guard) robustness alternate from `ral_artifacts.py:fig_robustness`;
  the paper uses the two split panels (`ral_robust_drops` + `ral_robust_guard`).
- *Depicts:* floor (m²) vs. packet-drop probability p; drops-only and
  drops+jitter arms, 8 seeds each, mean ± sd.
- *Why / how:* `fig_robust_drops` from `d10b_loss.json`. Floor +13% at p=0.1,
  +45% at p=0.3 (jitter arm milder); anchored ANEES 4.23 in-gate at p=0.3 (130 s
  horizon).
- *Significance:* **D10(b) characterization — graceful degradation, no red flags
  fired.** Outside protocol class P, reported as characterization (red-flag
  rules, not falsifiers). ANEES carries its 130 s horizon.
- *Theory:* No theorem — empirical **D10(b)** robustness characterization
  outside protocol class P (red-flag rules, not a falsifier); graceful
  degradation, no red flags fired. ANEES carries its 130 s horizon.
- *Provenance:* **[SIM]** — reads the committed Drake record `d10b_loss.json`
  (8 seeds/arm; confirmed present).

### `ral_robust_guard.pdf`
- **`ral_robust_guard.pdf`** — vector PDF. USED as **Fig. 27** (`fig:guard`) —
  "D10(c): why the broadside guard never fired — σ̂_i lags true broadside across
  the reachable gust envelope, so ON ≡ OFF. Reported as a null with its
  mechanism."
- *Depicts:* the reachable gust envelope — true vs. estimated cable-angle cosine
  probes (e.g. true 0.027 vs. estimated 0.106 at the 5000 N probe); the guard
  region never entered.
- *Why / how:* `fig_robust_guard` from `d10c_guard.json` (`envelope_probe`).
  The guard triggers on the *estimated* angle σ̂_i, which lags true broadside;
  guard-on/off runs are bit-identical.
- *Significance:* **D10(c) — a null reported with its mechanism.** The
  set-piece rescue movie does *not* ship; the honest deliverable is a lag-aware
  margin design note. Not a positive result.
- *Theory:* No theorem — empirical **D10(c)** null: the broadside guard (the
  **Corollary 2 (`cor:inheritF`, "Network inheritance of conditioning
  singularities")** regime) is never entered because σ̂_i lags true broadside,
  so ON ≡ OFF. Reported as a null with its mechanism.
- *Provenance:* **[SIM]** — reads the committed Drake record `d10c_guard.json`
  (`envelope_probe`; confirmed present).

### `ral_forest.pdf`
- **`ral_forest.pdf`** — vector PDF. USED as **Fig. 28** (`fig:dforest`) — "The
  multibody falsifier ledger, verdicts as adjudicated: green passed, red
  falsified / fired, orange anti-ordered. Grey marks registered references and
  equivalence bands; evidence record named per row. [CONJECTURAL] rows report
  measured slopes as measured — no law asserted."
- *Depicts:* a two-scale forest plot — left panel exponent/ratio rows
  (amplitude, D_ss exponent, cross-tier ratio), right panel differences and
  correlations (D6 ΔRMSE, D9 pin-rate ρ, D9 re-lock ρ), each with CI, verdict
  colour, and named evidence file.
- *Why / how:* `fig_forest`, values transcribed from `docs/ral_package.md`
  adjudication (d3_amplitude.json, d2_a1_a2_arms.json, d6_tension.json,
  d9_scaling.json, …).
- *Significance:* the adjudicated ledger in one figure — theorem object green
  to coefficient precision [PROVEN]; the [CONJECTURAL] closed-loop exponent red
  (**C7b FALSIFIED**); cross-tier coefficient ratio red at ×5
  (5.04 [3.97, 6.19], **DISAGREES** — validity-domain finding); both D9 findings
  (pin-rate uncorrelated +0.04, re-lock anti-ordered −0.51, **FIRES**). No
  verdict is dressed up.
- *Theory:* The adjudicated falsifier ledger in one figure — **Theorem 3
  (`thm:floorF`)** amplitude green to coefficient precision [PROVEN]; the
  [CONJECTURAL] D_ss exponent red (**C7b FALSIFIED**); the cross-tier
  coefficient ratio red ×5 (**DISAGREES**); both D9 findings (**FIRES**). No
  verdict dressed up.
- *Provenance:* **[SIM]** (ledger transcription) — values transcribed from the
  `docs/ral_package.md` adjudication, each traceable to a named committed record
  (`d3_amplitude.json`, `d2_a1_a2_arms.json`, `d6_tension.json`,
  `d9_scaling.json`; all confirmed present). Not a fresh plot-time record read,
  but every CI traces to real simulated data — not fabricated.

### `ral_failure_taxonomy.pdf`
- **`ral_failure_taxonomy.pdf`** — vector PDF. NOT used in the submitted paper —
  the paper's taxonomy figure (`fig:taxonomy`) is the TikZ
  `\input{fig_taxonomy.tex}` in `main.tex`, not this rendered PDF; kept as the
  matplotlib-rendered alternate (`ral_artifacts.py:fig_failure_taxonomy`).
- *Depicts:* the four adverse findings (docking spec unmet, anchored gain
  starvation, ANEES non-transfer, guard unexercised) with measured cause and
  recorded remedy class.
- *Why / how:* schematic transcribed from the ledger; no record read at plot
  time beyond the named evidence files.
- *Significance:* organizes the honest limits — each finding with cause and
  remedy class. Conceptual; superseded by the TikZ version in the manuscript.
- *Theory:* No theorem — organizes the four honest empirical limits (docking
  spec unmet, anchored gain starvation, ANEES non-transfer, guard unexercised)
  with measured cause and recorded remedy class.
- *Provenance:* **[DIAGRAM]** — schematic transcribed from the ledger
  (`ral_artifacts.py:fig_failure_taxonomy`), no record read at plot time beyond
  the named evidence files; superseded by the TikZ `fig:taxonomy`.

### `hero_montage.png`
- **`hero_montage.png`** — raster PNG (the only non-vector file here). NOT used
  in the submitted paper — a still montage of the gauge-pinning demonstration
  movie (S2, `hero_blind_harbor.mp4`), kept as a visual aid / poster still.
- *Depicts:* montaged frames of the ghost-caisson gauge-pinning demo — each
  agent's private load estimate drawn as a translucent caisson, coherently
  drifting then pinned at the beacon.
- *Why / how:* rendered from the S2 movie pipeline; the movies are **not
  evidentiary** — every quantitative claim traces to the committed campaign
  records.
- *Significance:* illustrative of **Cor. 5.2 [PROVEN]** live. Non-evidentiary
  visualization only.
- *Theory:* Illustrative of **Corollary 1 (`cor:pinF`, "Pinning") [PROVEN]**
  live (coherent gauge drift, then the single-anchor pin); non-evidentiary.
- *Provenance:* **[DIAGRAM]** — non-evidentiary movie still from the S2
  `hero_blind_harbor.mp4` pipeline; every quantitative claim traces to the
  committed campaign records, not this frame.

## Epistemic notes

- **Two different objects, never conflated.** (1) The **error-transport
  holonomy amplitude** = the object of **Thm 7.2 [PROVEN]**, measured slope
  1.999 (Tier-1) / 2.000 (Drake), resolved only noise-off; symmetric-class
  switch-offs are **machine-zero** (ξ=0 literally 0.0). Lives in `ral_f4a`,
  `tcns_f5_amp`, and the p=2.00 trace of `ral_cross_tier`. (2) The **closed-loop
  steady-state disagreement D_ss [CONJECTURAL]**, measured slope ≈1.08–1.10 on
  both plants — a *measured* slope in a conjectural regime, carried with the R3
  mixture caveat, asserted as **no law**; its CI excludes both 1 and 2. Lives in
  `ral_f4b`, `tcns_f5_floor`, and the p≈1.08 trace of `ral_cross_tier`. **Never
  caption a D_ss fit as validating Thm 7.2; never call the D_ss slope a
  first-order law.**
- **Falsifier verdicts are reported honestly, never dressed up.** C7b
  **FALSIFIED** at these scales (`ral_f4b`, `ral_forest`). C9b falsifier
  condition **MET** on the seed-paired estimator; the unpaired estimator is
  under-powered (`tcns_f5_floor`). C9c **TRIPS** on Tier-1 (2.75× < the 10×
  threshold). C19 falsifier **TRIPPED** (2.48) but in the favorable direction —
  restated with corrected order, **not** a pass (`tcns_f8`). D9 falsifier
  **FIRES** — pin rate ρ=+0.04 ≈ 0 (anchor-limited); re-agreement anti-orders
  −0.51 (`ral_d9`, `ral_forest`). A tripped/fired/falsified/MET row is never
  presented as a positive result.
- **C6 contraction PASSED** (slope 1.403, two topologies; μ=−0.062
  topology-independent — the consensus term does the contraction), `tcns_f8`.
- **Cross-tier:** exponent **EQUIVALENT** (+0.023 [−0.012, +0.057]); coefficient
  ratio **DISAGREES ×5** (5.04 [3.97, 6.19]) — a reduced-model validity-domain
  finding (Drake's realized maneuvering shapes exit the reduced model's stable
  domain), `ral_cross_tier`, `ral_forest`.
- **B1 is the record's own zero-latency all-to-all limit — a reference, never
  an "oracle."** A fundamentally better centralized estimator is not excluded
  (`ral_score_box`, `ral_score_cdf`).
- **Every ANEES claim carries its horizon.** In-gate 3.96 at the **130 s** S1
  horizon; **159–229** on 450 s transits (the M-FAB calibration gate does *not*
  transfer to long transits). See `ral_agent_errors`, `ral_robust_drops`.
- **Docking <0.5 m: 0% of ALL arms** at plan-faithful acquisition (even the
  zero-latency limit misses spec); v2 improves fleet-mean 2.4× (median ~0.61 m;
  17% of seeds under 0.5 m) but the **spec remains UNMET** (`ral_score_*`,
  `ral_docking_*`, `ral_v2seeds`).
- **Frames and units:** world ENU in metres; SE(2) load pose = (x, y, yaw);
  disagreement D in m². Predictions are labelled as predictions; only realized/
  measured states are stated as facts.
- The paper currently carries an **empty bibliography** (zero `\cite`); these
  figures are not externally cited.

## Cross-links

- **Paper source:** `../main.tex` (RA-L "Blind Harbor" companion). This folder
  is `\graphicspath{{figures/}}`. TikZ figures `fig:arch` and `fig:taxonomy`
  live in `../fig_arch.tex` / `../fig_taxonomy.tex`, not here.
- **Authoritative ledger (verdicts + epistemic status):**
  `../../../docs/ral_package.md`.
- **Reconciliation note:** `../../../docs/reconciliation_2026-07-21.md`.
- **Generators:** `tier2_drake/campaign/ral_figs_ieee.py` (paper figures),
  `tier1_sheaf/campaign/tcns_figs_ieee.py` (`tcns_f5_*`, `tcns_f8`),
  `analysis/figures/ral_artifacts.py` + `analysis/figures/f4*_*.py` (source
  overlays and alternates). Shared style: `analysis/ieee_style.py`.
- **Data records:** Drake `tier2_drake/results/s1/*.{json,npz}`; Tier-1
  `tier1_sheaf/results/*.{json,csv}`. See the reproducibility manifest
  (`docs/ral_package.md` §3) and the paper's Table `tab:registry`.
