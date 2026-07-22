# T-CNS §VIII figures & artifacts — figure & artifact guide

## 1. Orientation

This folder holds the figure PDFs for **`papers/tcns_section8/section8.tex`** — the
"Numerical verification" section (§VIII) of the T-CNS flagship journal paper. Per the
publication split this section is **Tier-1 sheaf numerics ONLY**: every cell runs on the
*reduced plant* inside protocol class *P* (uniform lags, zero jitter/loss, realized age
asserted equal to τ). There are **no Drake / multibody figures here** — the "Blind Harbor"
multibody campaign is the separate RA-L companion, and the L-CSS latency-curvature-floor
letter is a third unit. The figures establish, on the Tier-1 plant: the plant/pipeline and
its information boundary; formations and comms topologies; the SE(2) gauge story; the
**proven** amplitude O(τ²) law versus the **conjectural** closed-loop disagreement `D_ss`;
contraction; the symmetry pair; the switch-off ladder; Δt/step invariance; floor dynamics;
and topology dependence. Every figure was produced by a committed, seeded Python generator
that reads a committed campaign record and renders a vector PDF in the shared IEEE style.

## Data provenance & authenticity

Every figure entry below now carries a **`*Theory:*`** line (the specific statement it bears
on, cited by the paper's own `\label`) and a **`*Provenance:*`** line (its authenticity class
plus the exact source). Counting all **39 figure entries** in this folder (**21 used** by
`section8.tex` + **18 kept-but-unused** variants):

- **[SIM] simulated data — 27.** A seeded generator ran the actual Tier-1 `ReducedPlant`
  (or replayed a seeded formation / gauge / contraction ensemble) and the figure reads the
  committed record it produced. Records confirmed present on disk under
  `tier1_sheaf/results/`: `e3b_production.json` (1584 runs), `e3c_symmetry.json`,
  `e3c_c9b_seeds.json`, `e3c_robust.json`, `e2_contraction.json`, `e6_topology.json`,
  `e10_dt_sweep.json`, `e3a_extension.json`, `e1_gauge.csv`, plus the supplementary movies
  `gauge_drift.mp4` / `contraction.mp4` / `floor_protocol.mp4`. A seeded
  `np.random.default_rng(seed)` is **reproducible simulation noise = real simulated data**,
  not fabrication.
- **[DET] deterministic recomputation — 7.** Exact analytic quantities from released
  operators at fixed inputs, **no rng**: `sheaf_laplacian` eigenvalues (E1 spectrum),
  `holonomy_amplitude_m2` over the τ grid (record `e3a_amplitude.csv`, confirmed present),
  `conjugated_generator` / `two_agent_commutator` (the C15 level set, the C9b′ amplitude, the
  L-CSS heatmap), and the falsifier forest's **verbatim transcription** of the frozen ledger
  (`docs/ral_package.md`), each of whose rows itself sources a committed record.
- **[DIAGRAM] conceptual / schematic — 5.** `tcns_plant`, `tcns_arch`, `tcns_architecture`,
  `tcns_topology_gallery`, `theorem_map` — hand-drawn setup / architecture / dependency
  illustrations with **no measured data** (the topology gallery's λ₂ labels are deterministic
  Laplacian eigenvalues). Each is labelled as a diagram and never reads as a measurement.
- **[FLAG] fabricated / untraceable — 0 now, but ONE was found and fixed.**
  **`tcns_e1_spectrum` (Fig. 2) shipped fabricated until 2026-07-22** — its generator's real
  `sheaf_laplacian` call failed on a wrong API signature and an inner `try/except` silently
  substituted a hand-typed eigenvalue array. The fallback was removed, replaced with loud
  asserts, and the figure regenerated from the real operator (see its entry). A repo-wide
  sweep confirmed it was the **only** silent-fallback site; the remaining `except` blocks in
  `tcns_figs_ieee.py` / `ral_figs_ieee.py` are `__main__` loop guards that substitute nothing.

**Finding:** every *data* figure in this folder traces to a **committed, seeded simulated
record** (confirmed present on disk) or to a **deterministic operator recomputation**; the
schematics are labelled as such; **nothing is fabricated as of 2026-07-22 — one figure
(`tcns_e1_spectrum`) was found fabricated and was corrected at the generator, not patched
over.** The two-objects guardrail holds
throughout — amplitude figures (`thm:floorF` **[PROVEN]**) and `D_ss` figures
(**[CONJECTURAL]**) are kept distinct, and no `D_ss` fit is captioned as validating the floor
theorem. `b3_relpose.py` (Tier-2, explicitly WIP / "DESIGN INCOMPLETE") feeds **no** figure
here and is correctly absent.

## 2. How these were generated

**Generators** (all under `tier1_sheaf/campaign/`):
- `tcns_figs_ieee.py` — the primary generator for the *used* `tcns_*` figures. Writes to
  `tier1_sheaf/results/artifacts/ieee/` as `<name>.pdf` (+ a 400-dpi `.png` twin); those PDFs
  were copied into this folder.
- `lcss_figs_ieee.py` — produces `lcss_levelset_bars.pdf` (and the unused `lcss_heatmap.pdf`).
- `shared_figs_ieee.py` — produces `t1_falsifier_forest.pdf` (and the unused `theorem_map.pdf`).
- `tcns_scenario_figs.py`, `paper_artifacts.py`, `e3a_extension_panels.py`,
  `f5_symmetry_fig.py` — produce the **superseded / alternate** variants (see catalogue).
  `paper_artifacts.py` is also the reproducibility driver named in the paper's registry table:
  it re-derives the extension datasets seed-exactly at import and refuses to plot on mismatch.

**Data records read** (all under `tier1_sheaf/results/`, base path `RES` hard-coded in the
generators): `e3a_amplitude.csv` (amplitude), `e3a_extension.json` (C15 level set),
`e3b_production.json` (1584-run `D_ss` production), `e3c_symmetry.json` +
`e3c_c9b_seeds.json` (symmetry, paired estimator), `e3c_robust.json` (robust arm),
`e2_contraction.json` (contraction), `e6_topology.json` (topology sweep),
`e10_dt_sweep.json` (Δt sweep). A few figures compute live from library code rather than a
record: the E1 spectrum recomputes `sheaf_laplacian` on three shapes; the contraction
portrait/decay pull traces from `contraction_movie`; the floor-dynamics traces from
`floor_protocol_movie`; the plant/gauge schematics are drawn.

**Shared style** (`analysis/ieee_style.py`, imported as `apply_ieee, COLW, DBLW, cyc`):
STIXGeneral serif text at 8 pt with STIX math, single-column width **COLW = 3.5 in** /
double-column **DBLW = 7.16 in**, vector PDF with Type-42 embedded fonts, raster twins at
**400 dpi**, and the colour-blind-safe **Okabe-Ito** palette paired one-to-one with
distinct linestyles + markers so every figure survives grayscale. The PDFs are **vector**
with **committed generators**, so they are re-buildable and editable from the records.

## 3. Figure catalogue

> "USED" = appears via `\includegraphics` in `section8.tex`. Ordinals below index the **PDF
> figures of this folder** in order of appearance; the `\label` given per entry is the
> authoritative cross-reference. Note the section's **Figure 2 is the inline TikZ architecture**
> (`fig:archF`, `\input{fig_arch.tex}` — a `\begin{figure*}` that shares the figure counter,
> **not** a PDF in this folder), so in the compiled section the paper's own figure numbers run
> one higher than these PDF ordinals from the gauge spectrum onward. Nothing in §VIII is a
> Drake figure.

### Used figures

#### **`tcns_plant.pdf`** — vector PDF
- USED in T-CNS §VIII as **Fig. 1** (`fig:plantF`) — the reduced plant and its comms
  structure: shapes `s_j = (σ_j, σ_{i,j})` on taut unit cables; comms graph (dashed) is a
  controlled variable (default `C_5` cycle shown; `K_5` and the E6 sweep vary λ₂).
- *Depicts:* a schematic of N agents on unit cables to a common load, cable attachment rays,
  and the dashed communication graph. Axes are a drawn 2-D layout (no physical units); the
  frame is the load-centred body plane.
- *Why / how:* hand-drawn by `tcns_figs_ieee.fig_plant` — a definitional schematic, not a
  data plot, fixing the experimental object and naming λ₂ as the controlled variable.
- *Significance:* orients the whole section; establishes that comms connectivity (λ₂) is
  swept, which the contraction (C6) and topology (E6) results depend on. Definitional, no verdict.
- *Theory:* no theorem — a **definitional** schematic fixing the experimental object (the
  estimation setting of `def:sheafF`) and naming λ₂ as the swept control that `thm:contractF`
  (contraction) and the E6 sweep depend on.
- *Provenance:* **[DIAGRAM]** — conceptual diagram, no measured data (`fig_plant` hand-draws
  the N=5 tow + `C_5` graph with fixed geometry).

#### **`tcns_e1_spectrum.pdf`** — vector PDF
- USED as **Fig. 2** (`fig:f3`) — gauge spectrum: `dim ker L_F = 3` without an anchor,
  collapsing to zero with one anchor whose λ_min becomes the rate.
- *Depicts:* grouped log-scale bars of the sheaf-Laplacian eigenvalues λ(L_F) (dimensionless,
  shape-only) over mode index 0–8 — the unanchored spectrum beside the one-anchor spectrum.
  Modes 0–2 sit in the shaded machine-zero band (≤ 1.1×10⁻¹⁵) unanchored, annotated
  "dim ker L_F = 3 (the SE(2) gauge)", and lift to ≈0.18–0.27 with one anchor; modes 3–8
  (1.16, 1.38, 3.00, 4.07, 6.56, 7.83) are essentially unchanged.
- *Why / how:* `fig_e1_spectrum` assembles `sheaf_laplacian(SHAPES, EDGES, weights=[1,1,1],
  l=1.0)` on the three-agent triangle of `experiments/e1_gauge.py`
  (SHAPES = [(0.4, 0.3), (0.9, −0.5), (−0.7, 0.6)], EDGES the 3-cycle) and takes `eigvalsh`,
  then adds a full-rank vertex potential (+1.0·I on agent 0's 3×3 load block) for the
  anchored arm — so the pinning collapse is *shown on the same axes*, not asserted. The
  harmonic-section identity annihilates to **1.3×10⁻¹⁵** (reported in text); the computed
  gauge modes are ≤ 1.1×10⁻¹⁵ and the anchored λ_min is 0.175.
- *Significance:* the gauge theorem (Thm 5.1) and pinning corollary (Cor 5.2) as linear
  algebra. Structural falsifier "kernel dim ≠ 3" — **PASSED** (pass/fail, not an estimate).
  **Now shared with the RA-L companion**, which `\includes` the same PDF as its Fig. 6
  (`fig:gaugespec`) to back the gauge/pinning statements directly rather than inferring them
  from closed-loop drift; it is structural and shape-only, hence plant-independent, and is
  captioned there as *not* a Drake result.
- *Theory:* `thm:gaugeF` (Exact residual unobservability = one global gauge) **+** `cor:pinF`
  (Pinning) — the three exact zeros **ARE** `dim ker L_F = 3` (the SE(2) gauge), and one
  anchor collapsing the kernel **IS** the pinning claim, both shown as pure linear algebra.
- *Provenance:* **[DET]** — exact recomputation from the released operator
  `tier1_sheaf/sheaf/laplacian.sheaf_laplacian` on three **fixed** triangle shapes (edges
  `(0,1),(1,2),(2,0)`); no record read, no rng; harmonic-section identity annihilates to
  1.3×10⁻¹⁵.
  **⚠ Corrected 2026-07-22 — this figure was previously FABRICATED.** The generator's real
  `sheaf_laplacian` call failed on a wrong API signature (`shapes` passed as a 2-D array with
  an `edges=` kwarg, and the function's 3-tuple return treated as a matrix), and an inner
  `try/except` silently substituted a **hand-typed** eigenvalue array
  `[0, 0, 0, 2.1, 2.4, 3.0, 3.3, 4.1, 5.5]` — so the shipped Fig. 2 was a placeholder, not a
  computation. The fallback has been removed and replaced with asserts (`dim ker == 3`
  unanchored, `== 0` anchored) that fail loudly, and the PDF regenerated from the real
  operator. A repo-wide sweep of the figure generators found this was the **only** silent-
  fallback site (the remaining `except` blocks are `__main__` loop guards that print `FAIL`
  and substitute nothing).

#### **`tcns_gauge_trails.pdf`** — vector PDF
- USED as **Fig. 3** (`fig:gaugestory`) — the gauge phenomenon as trajectories: with no
  anchor the agents' load-pose estimates track each other but drift as a rigid group off the
  truth; at the beacon they snap back.
- *Depicts:* estimate trajectories (coloured, one per agent) vs. the truth (black) in the
  world ENU plane (metres); beacon events as stars; the post-snap segment dashed.
- *Why / how:* `fig_gauge_trails` renders the E1 phenomenon — mutually consistent estimates
  drifting **as a group** along the SE(2) gauge, collapsed by one absolute anchor.
- *Significance:* visual companion to the gauge/pinning result; it is the same phenomenon as
  supplementary movie M1. Illustrates the two-objects distinction (disagreement vs. truth error).
- *Theory:* `thm:gaugeF` / `cor:pinF` — the group drift **along** the SE(2) gauge and the
  beacon snap-back are the observable content of the gauge theorem and pinning corollary.
- *Provenance:* **[SIM]** — seeded `anim_gauge.simulate(seed=3)` reproducible run; the same
  phenomenon as supplementary movie `gauge_drift.mp4` (confirmed present in `tier1_sheaf/results/`).

#### **`tcns_gauge_errors.pdf`** — vector PDF
- USED as **Fig. 4** (`fig:gaugeerr`) — the two error objects are distinct: disagreement D
  (agents vs. each other) runs ~an order of magnitude below the gauge error (agents vs.
  truth); one anchor collapses both.
- *Depicts:* two error time-series — disagreement `D` and gauge (vs-truth) error — in the
  load-pose metric (`‖Log(G_i⁻¹G_j)‖²`, m²/rad² mix), before and after the anchor.
- *Why / how:* `fig_gauge_errors` contrasts the disagreement functional with the truth-referenced
  error to make concrete that **D is not a truth error**.
- *Significance:* the folder's central guardrail in one plot — `D` (a disagreement) is a
  different object from the gauge error, both collapsed by pinning (Thm 5.1, Cor 5.2).
- *Theory:* `thm:gaugeF` / `cor:pinF` and the folder's two-objects guardrail — disagreement
  `D` is **not** a truth error; both collapse under one anchor (pinning). An empirical
  illustration, not a quantitative falsifier.
- *Provenance:* **[SIM]** — the same seeded `anim_gauge.simulate(seed=3)` run
  (`gauge_drift.mp4` confirmed present).

#### **`tcns_amplitude.pdf`** — vector PDF
- USED as **Fig. 5** (`fig:f4a`) — F4a: the leading-order, deterministic holonomy amplitude
  of Thm 7.2 — slope 1.999, coefficient 1.0000, switch-offs at machine zero.
- *Depicts:* log-log of `‖Log Hol‖` (dimensionless) vs. staleness τ (s) over the grid
  {0.05…1.6}; measured points (slope 1.999), a τ² guide, and the switch-off arm pinned at the
  plot's machine-zero floor (the ξ=0 arm is exactly 0.0, unplottable on a log axis).
- *Why / how:* `fig_amplitude` reads `e3a_amplitude.csv`; the m=2 round-trip amplitude fits
  slope **1.999**, coefficient ratio `‖Log Hol‖/τ²‖[C_i,C_j]‖ = 1.0000` at the smallest τ;
  switch-offs (`s_i≡s_j` < 1e-15, `η=0` < 1e-16, `ξ=0` exactly 0.0).
- *Significance:* **Object 1** — the error-transport holonomy amplitude, the object of
  **Thm 7.2 [PROVEN]**. Falsifiers C7a/C8/C13 **PASSED** (2 ∉ slope CI; coef ∈ [0.9,1.1];
  switch-offs nonzero all fail to fire). This is *not* `D_ss` and must never be conflated with it.
- *Theory:* `thm:floorF` (Latency–curvature floor) **[PROVEN]** — the measured slope **1.999
  IS the theorem's O(τ²) amplitude claim**; coefficient 1.0000 and the machine-zero switch-offs
  are `lem:bchF` (group-commutator defect) + `cor:symF` (symmetry protection). Falsifiers
  C7a/C8/C13 PASSED.
- *Provenance:* **[DET]** — reads committed `e3a_amplitude.csv` (confirmed present); the
  generic arm is `holonomy_amplitude_m2` over the τ grid {0.05…1.6}, **deterministic, no rng**
  (symmetric arm is literally ~1e-16).

#### **`tcns_formations.pdf`** — vector PDF
- USED as **Fig. 6** (`fig:f4aext`) — E3a formation invariance: 20 random taut formations
  overlaid; the geometry varies widely yet every one fits slope 1.9993.
- *Depicts:* an overlay (equal-aspect, axes off) of 20 two-agent taut formations — load box,
  cable rays, tip markers — with the title stating the common slope.
- *Why / how:* `fig_formations` pulls `forms`/`slopes` from `formation_sweep_movie`; the
  amplitude slope is **formation-invariant at 1.9993 ± 0.0000** across 20 draws.
- *Significance:* strengthens Object 1 — the τ² order is a *structural constant*, independent
  of formation geometry. Extends C7a; part of the switch-off / invariance ladder. **[PROVEN]** object.
- *Theory:* `thm:floorF` **[PROVEN]** — the τ² order is **formation-invariant** (slope
  1.9993 ± 0.0000 over 20 draws), i.e. a structural constant of the amplitude object; extends
  falsifier C7a.
- *Provenance:* **[SIM]** — a seeded formation ensemble (`np.random.default_rng(2026)`)
  reproducing committed `e3a_extension.json["formation_cluster"]` (confirmed present); each
  slope is a deterministic `holonomy_amplitude_m2` fit on the seeded geometry.

#### **`lcss_levelset_bars.pdf`** — vector PDF
- USED as **Fig. 7** (`fig:c15tc`) — E3a level-set protection (C15): the five zero-commutator
  pairs at ≥ 1 rad separation all satisfy `C_i = C_j` to 10⁻¹⁶ — the protected class is a
  level set, not just coincident shapes.
- *Depicts:* a grouped log-scale bar chart, one x-group per pair (labelled by shape
  separation in rad, all ≥ 1), bars `‖[C_i,C_j]‖` vs. `‖C_i − C_j‖`, with a machine-precision
  line at 1e-15.
- *Why / how:* `lcss_figs_ieee.fig_levelset_bars` reads `e3a_extension.json["C15"]` and
  recomputes `conjugated_generator`; the search for zero-commutator pairs at ≥ 1 rad
  separation found **only** pairs with `C_i = C_j` to 10⁻¹⁶.
- *Significance:* the **NEW** protected-class result. The protected class is a discrete
  **level set** of `s ↦ C(s;ξ)` (two zeros per reference torus); on it the full holonomy
  vanishes **at all orders**. Presented as an **observation** (proof open), extending Cor 5.x
  symmetry protection. An amplitude-object (Object 1) finding, not a `D_ss` claim.
- *Theory:* `cor:symF` (Symmetry protection) — the C15 extension: the protected class is a
  discrete **level set** of `s ↦ C(s;ξ)` (zero-commutator pairs all have `C_i = C_j` to 1e-16),
  on which the full holonomy vanishes **at all orders**. Stated as an observation (proof open).
- *Provenance:* **[DET]** — reads committed `e3a_extension.json["C15"]` (confirmed present)
  and recomputes `conjugated_generator`; `‖[C_i,C_j]‖` is deterministic, no rng.

#### **`tcns_f4b.pdf`** — vector PDF
- USED as **Fig. 8** (`fig:f4b`) — numerical evidence for the *conjectured* stochastic
  steady-state floor; fitted excess exponent **1.101 [1.076, 1.125]**: conjectured order 2 is
  excluded (and so is 1); the frozen+noise-off regression reproduces the executed null.
- *Depicts:* log-log of the `D_ss` excess over the frozen-shape control vs. τ (s), with the
  fitted slope and CI; controls shown below the paper arm.
- *Why / how:* `fig_f4b` reads `e3b_production.json` (1584 runs; 12 formations × 10 seeds per
  τ + controls). Straight-tow control ≈ 5× below, frozen-shape ≈ 15× below the paper arm at
  every τ; the executed null (shapes frozen, noise off) gives `D_ss ~ 10⁻³⁰`.
- *Significance:* **Object 2** — the closed-loop steady-state disagreement `D_ss`
  **[CONJECTURAL]**. Falsifier **C7b FALSIFIED at these scales** (slope 1.101; CI excludes
  both 1 and 2). This is a **measured slope in a conjectural regime**, carried with the R3
  caveat, asserted as **NO law**. NEVER caption this as validating Thm 7.2; NEVER call the
  slope a first-order law.
- *Theory:* **NOT a theorem** — the closed-loop `D_ss` **[CONJECTURAL]**, a **different
  object** from `thm:floorF`; falsifier **C7b FALSIFIED at these scales** (slope 1.101
  [1.076,1.125], CI excludes both 1 and 2). Never a validation of `thm:floorF`.
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (1584 seeded `ReducedPlant`
  runs; confirmed present); the executed frozen+noise-off null gives `D_ss ≈ 6×10⁻³⁰`.

#### **`tcns_dss_cdf.pdf`** — vector PDF
- USED as **Fig. 9** (`fig:dssdist`) — per-run `D_ss` CDFs by arm at τ = 0.4 (1584-run
  production record). `D_ss` is the stochastic steady-state object [CONJ] — measured, not a
  test of Thm 7.2.
- *Depicts:* empirical CDFs (y = cumulative fraction, x = `D_ss`, m²) for the paper-rule and
  frozen-shape arms at the reference staleness τ = 0.4.
- *Why / how:* `fig_dss_cdf` reads `e3b_production.json`. The arm CDFs **do not overlap at any
  quantile** — the separation is distributional, not just in medians.
- *Significance:* exposes the distribution the C7b exponent summarizes. [CONJ] regime; a
  measured object, not a theorem test. Distinct from Object 1.
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** distribution at τ = 0.4; a measured
  object exposing what falsifier C7b summarizes, explicitly **not** a test of `thm:floorF`.
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (confirmed present).

#### **`tcns_dss_box.pdf`** — vector PDF
- USED as **Fig. 10** (`fig:dssbox`) — paper-rule `D_ss` spread across seeds and formations
  per τ ([CONJ] regime).
- *Depicts:* per-τ box plots of `D_ss` (m²) over seeds × formations across the τ grid.
- *Why / how:* `fig_dss_box` reads `e3b_production.json`. The spread is ≈ 1.6× interquartile,
  ≈ 3.7× between 5th and 95th percentiles — ~one τ octave — which is *why* the campaign
  pre-registered **seed-paired** estimators and declared unpaired CIs under-powered.
- *Significance:* motivates the paired-estimator methodology used in the symmetry figures.
  [CONJ] regime, measured object.
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** seed × formation spread; it **motivates**
  the seed-paired estimator methodology (unpaired CIs declared under-powered). Not a theorem test.
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (confirmed present).

#### **`tcns_floor_dyn.pdf`** — vector PDF
- USED as **Fig. 11** (`fig:floordyn`) — the floor's dynamics: `D(t)` climbs from a
  perturbation to `D_ss` over a τ sweep, higher for larger τ, inside the shaded window. This
  is the measurement protocol for the [CONJ] steady-state object; it is **not** a test of Thm 7.2.
- *Depicts:* semilog `D(t)` (m²) vs. t (s) for τ ∈ {0.1, 0.2, 0.4, 0.8}; steady-state dots;
  the last-30% evaluation window shaded.
- *Why / how:* `fig_floor_dyn` pulls traces from `floor_protocol_movie`; larger τ → higher
  steady state, matching the metric protocol (all-pairs mean, last-30% window).
- *Significance:* documents the `D_ss` **measurement protocol** (supplementary movie M3
  animates it). [CONJ] object; explicitly not a Thm 7.2 test.
- *Theory:* **NOT a theorem** — documents the `D_ss` **[CONJ]** MEASUREMENT PROTOCOL (climb to
  steady state, last-30% window); explicitly **not** a test of `thm:floorF`.
- *Provenance:* **[SIM]** — seeded `ReducedPlant` traces via `floor_protocol_movie`; the
  protocol record `e3b_production.json` and supplementary movie `floor_protocol.mp4` are both
  confirmed present.

#### **`tcns_robust.pdf`** — vector PDF
- USED as **Fig. 12** (`fig:robustF`) — the C9c trip at run level: generic vs. symmetric-class
  `D_ss` under 20% jitter + 10% drops (outside class *P*). Ratio **2.75× [1.94, 3.89]** —
  protection persists but falls an order short of the registered 10×.
- *Depicts:* two box plots (generic, symmetric) of `D_ss` at τ = 0.4 under the robust arm, m².
- *Why / how:* `fig_robust` reads `e3c_robust.json`. The registered statistic is the ratio of
  arm **means**, 2.75× (box **medians** ratio 3.2×), under heterogeneous realized ages —
  explicitly **outside protocol class *P***, so it characterizes robustness, not the theorem.
- *Significance:* falsifier **C9c TRIPS on Tier-1** (2.75× < the 10× threshold). Large
  symmetric protection is a property of the **amplitude object only**. A tripped row is a
  finding, **not** presented as a pass.
- *Theory:* **NOT a theorem** (outside protocol class *P*) — falsifier **C9c TRIPS on Tier-1**
  (2.75× [1.94,3.89] < the registered 10×); characterizes robustness of the amplitude-object
  protection, reported as a tripped row, **not** as a pass.
- *Provenance:* **[SIM]** — reads committed `e3c_robust.json` (confirmed present; seeded runs
  with 20% jitter + 10% drops).

#### **`tcns_f5_amp.pdf`** — vector PDF
- USED as **Fig. 13** (`fig:f5tc`) — symmetry, the amplitude object (C9b′): the departure
  from the symmetric class is first-order in ε (slope 1.006), base commutator exactly zero — PASSED.
- *Depicts:* log-log of `‖[C_i,C_j]‖` vs. ε (departure from symmetric class), measured points
  (slope 1.006) with a ∝ε guide.
- *Why / how:* `fig_f5_amp` reads `e3c_symmetry.json["C9bp_amplitude"]`; the base commutator
  is exactly zero, and departure is linear in ε.
- *Significance:* **Object 1** on the ε-axis. Falsifier **C9b′ PASSED** (1 ∉ CI; 1.006).
  The amplitude object's symmetry protection is first-order and clean.
- *Theory:* `cor:symF` (Symmetry protection), the **amplitude** object — departure from the
  symmetric class is first-order in ε (slope 1.006), base commutator exactly zero; falsifier
  **C9b′ PASSED** (1 ∉ CI).
- *Provenance:* **[DET]** — reads committed `e3c_symmetry.json["C9bp_amplitude"]` (confirmed
  present); `‖[C_i,C_j]‖` via `two_agent_commutator`, deterministic (no rng).

#### **`tcns_f5_floor.pdf`** — vector PDF
- USED as **Fig. 14** (`fig:f5floor`) — symmetry, the closed-loop floor (C9b, [CONJ]): the
  seed-paired ε-exponent is 1.58 at every τ, excluding both 2 and 1 — falsifier MET, a
  linear-plus-quadratic mixture the registered single-power model mis-specifies. Never mixed
  with the amplitude object.
- *Depicts:* log-log of the `D_ss` ε-excess `D_ss(ε)−D_ss(0)` (m²) vs. ε for τ ∈ {0.2,0.4,0.8},
  each labelled with its paired slope + CI, and a ∝ε² guide.
- *Why / how:* `fig_f5_floor` reads `e3c_symmetry.json["C9b_dss"]` and the `_paired_estimator`
  in `e3c_c9b_seeds.json`. Segment slopes rise **1.2 → 2.1** up the ladder — a linear+quadratic
  mixture. The **unpaired** estimator [0.43, 2.89] is under-powered and adjudicates nothing.
- *Significance:* **Object 2** on the ε-axis. Falsifier condition **C9b MET on the declared
  (seed-paired) estimator**: 1.58 [1.44, 1.84], both 2 and 1 excluded; the registered
  single-power model is **mis-specified**. [CONJ] regime; reported as MET, not as a pass, and
  never mixed with the Fig. 13 amplitude object.
- *Theory:* **NOT a theorem** — the closed-loop `D_ss` **[CONJ]** ε-response; falsifier
  condition **C9b MET** on the declared seed-paired estimator (1.58 [1.44,1.84], both 1 and 2
  excluded; the registered single-power model is mis-specified). Reported as MET, never mixed
  with the Fig. 13 amplitude object.
- *Provenance:* **[SIM]** — reads committed `e3c_symmetry.json["C9b_dss"]` +
  `e3c_c9b_seeds.json["_paired_estimator"]` (both confirmed present; seeded paired runs).

#### **`tcns_f8.pdf`** — vector PDF
- USED as **Fig. 15** (`fig:f8tc`) — F8: rate versus κλ₂ across two topologies, slope 1.40
  (falsifier < 0.5); μ calibrated at κ = 0, so the identity line is anchored, not predicted;
  the nonlinear extension is open.
- *Depicts:* the contraction rate vs. κλ₂ (log-log or linear-fit), points for `C_5` and `K_5`,
  fit slope 1.40; the μ = 0-anchored identity line.
- *Why / how:* `fig_f8` reads `e2_contraction.json`; rate scales with κλ₂ at slope **1.403**
  across a 4× gain range and two topologies, with **μ = −0.062 topology-independent** (the
  consensus term does the contraction; μ calibrated at κ=0, not predicted).
- *Significance:* Thm 6.3 (contraction). Falsifier **C6 PASSED** (slope 1.403 < 0.5 trip
  threshold; μ = −0.062 topology-independent). In-domain result.
- *Theory:* `thm:contractF` (Frozen-linearization contraction) — rate scales with κλ₂ at slope
  1.403 across two topologies, μ = −0.062 topology-independent (μ calibrated at κ=0, not
  predicted); falsifier **C6 PASSED** (slope < 0.5). LTV/frozen domain.
- *Provenance:* **[SIM]** — reads committed `e2_contraction.json` (confirmed present; seeded
  contraction runs).

#### **`tcns_contraction_xy.pdf`** — vector PDF
- USED as **Fig. 16** (`fig:contportrait`) — contraction as trajectories: after a step
  perturbation, each agent's gauge-complement error spirals into consensus (origin), faster
  under `K_5` than `C_5` (LTV/frozen regime).
- *Depicts:* phase portrait of the gauge-complement error (e_⊥,x vs. e_⊥,y), one spiral per
  agent per topology, converging to the origin; `C_5` vs. `K_5` colour-coded.
- *Why / how:* `fig_contraction_xy` pulls traces from `contraction_movie`; the more connected
  `K_5` contracts faster, consistent with the κλ₂ law.
- *Significance:* visual mechanism for C6 (supplementary movie M2). **PASSED**; carries the
  LTV/frozen-regime hedge (nonlinear extension open).
- *Theory:* `thm:contractF` — the spiral-into-consensus mechanism, `K_5` faster than `C_5`,
  consistent with the κλ₂ law (C6 PASSED); carries the LTV/frozen hedge (nonlinear extension open).
- *Provenance:* **[SIM]** — seeded `ReducedPlant` traces via `contraction_movie`
  (`SeedSequence([SEED,17])`); the rate-law record `e2_contraction.json` and movie
  `contraction.mp4` are both confirmed present.

#### **`tcns_contraction_decay.pdf`** — vector PDF
- USED as **Fig. 17** (`fig:contdecay`) — the gauge-complement decay: its rate scales with
  κλ₂ (C6, slope 1.403), faster on the more connected graph.
- *Depicts:* semilog `‖e_⊥‖` vs. t (s) for `cycle` and `complete`; faster decay on the
  complete graph.
- *Why / how:* `fig_contraction_decay` pulls the same `contraction_movie` traces; the decay
  rate ordering is set by κλ₂.
- *Significance:* the fitted quantity behind C6 (slope 1.403). **PASSED**, in-domain.
- *Theory:* `thm:contractF` — the fitted gauge-complement decay rate behind C6 (slope 1.403),
  ordered by κλ₂; PASSED, in-domain.
- *Provenance:* **[SIM]** — the same `contraction_movie` traces; record `e2_contraction.json`
  confirmed present.

#### **`tcns_dt.pdf`** — vector PDF
- USED as **Fig. 18** (`fig:dtF`) — E10: the fitted exponent across a 10× range of integrator
  steps; all CIs share the green band [1.185, 1.256].
- *Depicts:* the fitted excess exponent (with CI bars) vs. integrator step Δt ∈ {0.001,
  0.0025, 0.005, 0.01} s; a shared green band highlighting the common overlap.
- *Why / how:* `fig_dt` reads `e10_dt_sweep.json`; all CIs share **[1.185, 1.256]**, coefficient
  converging mildly under refinement.
- *Significance:* numerics-invariance — **no exponent in the section is a discretization
  artifact**. Falsifier "CI disjointness" does not fire. Supports the [CONJ] `D_ss` exponent
  being a real (if conjectural-regime) measurement, not a numerical ghost.
- *Theory:* **NOT a theorem** — the numerics-invariance guard (E10): all Δt CIs share
  [1.185,1.256], so no exponent is a discretization artifact; supports the `D_ss` **[CONJ]**
  exponent being a real measurement. Falsifier "CI disjointness" does not fire (PASSED).
- *Provenance:* **[SIM]** — reads committed `e10_dt_sweep.json` (confirmed present; seeded
  `D_ss` runs across Δt ∈ {0.001…0.01} s).

#### **`tcns_topology.pdf`** — vector PDF
- USED as **Fig. 19** (`fig:topoF`) — E6 (exploratory, C10): floor vs. topology×N ordered by
  λ₂, at moderate (τ=0.2) and high (τ=0.8) staleness. Connectivity suppresses the floor 5× at
  moderate τ; the benefit collapses at high τ.
- *Depicts:* `D_ss` (m²) vs. topology×fleet-size ordered by λ₂ (cycle/path/star/complete,
  N ∈ {4,6,8}), two series (τ=0.2 and τ=0.8).
- *Why / how:* `fig_topology` reads `e6_topology.json`; connectivity buys up to 5× floor
  suppression at moderate τ, collapsing to ≤ 2× at high τ (complete graphs most τ-sensitive).
- *Significance:* pre-registered **exploratory** (C10, **no falsifier**). A design observation,
  not an adjudicated pass. The anchoring-side counterpart (pin-rate vs. λ₂) is answered
  **negatively** in the RA-L companion (D9 fires), not here.
- *Theory:* **NOT a theorem** — pre-registered **EXPLORATORY** (C10, **no falsifier**):
  connectivity suppresses the `D_ss` **[CONJ]** floor 5× at moderate τ, ≤2× at high τ. A design
  observation, not an adjudicated pass.
- *Provenance:* **[SIM]** — reads committed `e6_topology.json` (confirmed present; seeded
  topology × N sweep).

#### **`tcns_ladder.pdf`** — vector PDF
- USED as **Fig. 20** (`fig:ladderF`) — E3b transport-rule and control arms, median `D_ss` by
  staleness [CONJ object]. The Tier-1 A1-below-paper inversion is shown, not smoothed.
- *Depicts:* grouped log-scale bars of median `D_ss` (m²) per arm (paper, A1 no-comp, A2
  unconj, straight, frozen) across τ ∈ {0.1, 0.2, 0.4, 0.8}.
- *Why / how:* `fig_ladder` reads `e3b_production.json`. On *this* plant the A1 ablation sits
  **below** the paper rule — the ordering **inverts** relative to the multibody plant. The
  resolution is the metric: `D_ss` is a **disagreement** functional, agreement is purchasable
  by groupthink, so it **never ranks rules**. Rule ranking lives on the companion's
  truth-referenced metrics.
- *Significance:* honest disclosure of the inversion; reinforces that `D_ss` (Object 2) is a
  disagreement, not a correctness metric. The noise-off frozen null (`D_ss ~ 10⁻³⁰`) is 27
  orders below the axis (reported in the switch-off table).
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** transport-rule / control arms; the honest
  A1-below-paper **INVERSION** showing `D_ss` is a disagreement functional that **never ranks
  rules** (rule ranking belongs to the companion's truth-referenced metrics). Empirical disclosure.
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (confirmed present); the
  noise-off frozen null is `D_ss ~ 10⁻³⁰`.

#### **`t1_falsifier_forest.pdf`** — vector PDF
- USED as **Fig. 21** (`fig:forestF`) — the complete Tier-1 falsifier ledger, verdicts as
  adjudicated: green passed, red falsified/met ([CONJ] rows), orange tripped favorably. Grey
  marks the registered references.
- *Depicts:* a forest plot — one row per quantitative falsifier with point estimate + CI,
  registered reference (grey), and colour-coded verdict text.
- *Why / how:* `shared_figs_ieee.fig_forest` renders the adjudicated rows verbatim from the
  frozen ledger (`docs/ral_package.md`): proved chain (C7a slope, C9b′, C6, E10) green; the
  [CONJ] regime (C7b, C9b, C9c) red where fired; C19 orange (tripped favorably).
- *Significance:* the section's statistical-integrity statement in one axis. Makes the
  epistemic split visible: **the theorem's objects survive every registered attack; the
  conjectured stochastic extension does not and is reported as measured.** The structural E1
  falsifier (kernel dim ≠ 3) is pass/fail and reported in §E1, not on this axis.
- *Theory:* the section's **falsifier ledger** in one axis — the proved-chain objects
  (`thm:floorF` amplitude C7a, `cor:symF` C9b′, `thm:contractF` C6, E10) survive every
  registered attack (green); the `D_ss` **[CONJ]** extension (C7b/C9b/C9c) does not and is
  reported as measured (red); C19 tripped-favorable (orange). Not itself a theorem.
- *Provenance:* **[DET]** — a deterministic transcription of the adjudicated point estimates
  + CIs **verbatim** from the frozen ledger `docs/ral_package.md`; every row itself sources a
  committed record (`e3a_amplitude.csv`, `e2_contraction.json`, `e3b`/`e3c`/`e10`). No re-fit,
  no rng, no invented value.

### Unused figures (present in the folder, NOT `\included` by `section8.tex`)

#### **`e1_gauge.png`** — raster PNG
- NOT used in the submitted paper — raw experiment-output plot of the E1 gauge cell
  (`experiments/e1_gauge.py`), **superseded by `tcns_e1_spectrum.pdf`** (the IEEE-styled
  spectrum). Kept as the un-styled experiment artifact.
- **Note (2026-07-22):** `e1_gauge.py` was the *genuine* implementation throughout — it
  computes the real `sheaf_laplacian`, asserts `dim ker == 3` and the gauge-basis
  annihilation, and sweeps the anchor strength. During the window in which
  `tcns_e1_spectrum.pdf` was fabricated (see its entry), **this raster was the only honest
  rendering of the E1 cell.** The corrected `fig_e1_spectrum` now reuses this script's exact
  triangle config (`SHAPES`, `EDGES`, `l=1.0`).
- *Theory:* the same gauge / pinning phenomenon (`thm:gaugeF` / `cor:pinF`) as the used
  `tcns_e1_spectrum.pdf`, un-styled.
- *Provenance:* **[SIM]** — raw output of `experiments/e1_gauge.py`; record `e1_gauge.csv`
  confirmed present in `tier1_sheaf/results/`. Superseded.

#### **`e3a_amplitude.png`** — raster PNG
- NOT used — raw experiment plot of the E3a amplitude cell (`experiments/e3a_amplitude.py`),
  **superseded by `tcns_amplitude.pdf`**. Kept as the un-styled experiment artifact.
- *Theory:* `thm:floorF` **[PROVEN]** amplitude — the un-styled raw of the used `tcns_amplitude.pdf`.
- *Provenance:* **[DET]** — reads `e3a_amplitude.csv` (confirmed present), deterministic
  `holonomy_amplitude_m2` over the τ grid. Superseded.

#### **`e3a_extension_panels.pdf`** — vector PDF
- NOT used — multi-panel E3a-extension figure from `e3a_extension_panels.py` (formation
  invariance + remainder-constant + C15 in one sheet). **Superseded** in §VIII by the split
  single-panel figures `tcns_formations.pdf` (Fig. 6) and `lcss_levelset_bars.pdf` (Fig. 7).
  Kept as the combined overview.
- *Theory:* `thm:floorF` **[PROVEN]** (formation invariance) **+** `cor:symF` / C15 (level set)
  — the combined sheet later split into used Figs 6 & 7.
- *Provenance:* **[SIM]** — reads committed `e3a_extension.json` (confirmed present; seeded
  formation ensemble + deterministic commutators). Superseded.

#### **`f4b_tier1.pdf`** — vector PDF
- NOT used — an alternate/earlier rendering of the conjectural floor panel; **superseded by
  `tcns_f4b.pdf`** (Fig. 8). No committed generator maps to this basename; kept as a legacy variant.
- *Theory:* **NOT a theorem** — an earlier rendering of the `D_ss` **[CONJ]** floor (C7b), the
  same object as the used `tcns_f4b.pdf`; never a `thm:floorF` validation.
- *Provenance:* **[SIM]** — the data source is the committed `e3b_production.json` (confirmed
  present); legacy variant (no committed generator maps to this basename, but the values trace
  to the committed production record). Superseded.

#### **`f5_symmetry.pdf`** — vector PDF
- NOT used — a combined symmetry figure from `f5_symmetry_fig.py`; **superseded** in §VIII by
  the split pair `tcns_f5_amp.pdf` (Fig. 13, amplitude/PASSED) and `tcns_f5_floor.pdf`
  (Fig. 14, floor/MET), which the paper keeps deliberately separate. Kept as the combined variant.
- *Theory:* `cor:symF` amplitude (C9b′ PASSED) **+** the `D_ss` **[CONJ]** ε-response (C9b MET)
  — the combined figure later split into used Figs 13 & 14.
- *Provenance:* **[SIM]** — reads committed `e3c_symmetry.json` (+ `e3c_c9b_seeds.json`), both
  confirmed present. Superseded.

#### **`f8_contraction.pdf`** — vector PDF
- NOT used — an alternate rendering of the contraction rate-law figure; **superseded by
  `tcns_f8.pdf`** (Fig. 15). No committed generator maps to this exact basename; kept as a legacy variant.
- *Theory:* `thm:contractF` (C6) — an alternate contraction rate-law rendering of the used
  `tcns_f8.pdf`.
- *Provenance:* **[SIM]** — the data source is the committed `e2_contraction.json` (confirmed
  present); legacy variant. Superseded.

#### **`lcss_heatmap.pdf`** — vector PDF
- NOT used in §VIII — the commutator heatmap from `lcss_figs_ieee.fig_heatmap` (an L-CSS-side
  artifact). §VIII carries the C15 level-set result via `lcss_levelset_bars.pdf` instead. Kept
  for the L-CSS letter / cross-reference.
- *Theory:* `cor:symF` / `cor:sym` symmetry protection — the commutator structure `‖[C_i,C_j]‖`
  across a shape grid (an L-CSS-side artifact).
- *Provenance:* **[DET]** — recomputes `conjugated_generator` / the two-agent commutator over a
  shape grid, deterministic, no rng. Not used in §VIII.

#### **`tcns_arch.pdf`** — vector PDF
- NOT used — a rendered architecture/pipeline diagram from `tcns_figs_ieee.fig_arch`; the
  paper uses the inline TikZ `fig_arch.tex` for `fig:archF` instead. **Superseded** by the
  TikZ source. Kept as the PDF variant.
- *Theory:* no theorem — the architecture / pipeline schematic (the `fig:archF` role),
  superseded by the inline TikZ `fig_arch.tex`.
- *Provenance:* **[DIAGRAM]** — conceptual diagram, no measured data.

#### **`tcns_architecture.pdf`** — vector PDF
- NOT used — an alternate architecture diagram from `paper_artifacts.fig_architecture`; same
  role as `tcns_arch.pdf`, superseded by the inline TikZ `fig_arch.tex`. Kept as a variant.
- *Theory:* no theorem — an alternate architecture schematic (same `fig:archF` role),
  superseded by the inline TikZ.
- *Provenance:* **[DIAGRAM]** — conceptual diagram, no measured data.

#### **`tcns_contraction_portrait.pdf`** — vector PDF
- NOT used — earlier phase-portrait variant from `tcns_scenario_figs.fig_contraction_portrait`;
  **superseded by `tcns_contraction_xy.pdf`** (Fig. 16). Kept as the scenario-figure variant.
- *Theory:* `thm:contractF` (C6) — an earlier phase-portrait variant of the used
  `tcns_contraction_xy.pdf`.
- *Provenance:* **[SIM]** — seeded `contraction_movie` traces / record `e2_contraction.json`
  (confirmed present). Superseded.

#### **`tcns_dss_dist.pdf`** — vector PDF
- NOT used — combined CDF+box of per-run `D_ss` from `paper_artifacts` (fig 8 there);
  **superseded** in §VIII by the split `tcns_dss_cdf.pdf` (Fig. 9) + `tcns_dss_box.pdf`
  (Fig. 10). Kept as the combined variant. [CONJ] object.
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** distribution (combined CDF + box) later
  split into used Figs 9 & 10.
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (confirmed present). Superseded.

#### **`tcns_dt_invariance.pdf`** — vector PDF
- NOT used — alternate E10 invariance figure from `paper_artifacts` (fig 11 there);
  **superseded by `tcns_dt.pdf`** (Fig. 18). Kept as a variant.
- *Theory:* **NOT a theorem** — the E10 numerics-invariance guard, an alternate of the used
  `tcns_dt.pdf`.
- *Provenance:* **[SIM]** — reads committed `e10_dt_sweep.json` (confirmed present). Superseded.

#### **`tcns_floor_dynamics.pdf`** — vector PDF
- NOT used — scenario-style floor-dynamics figure from `tcns_scenario_figs.fig_floor_dynamics`;
  **superseded by `tcns_floor_dyn.pdf`** (Fig. 11). Kept as a variant. [CONJ] object.
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** measurement-protocol dynamics, a scenario
  variant of the used `tcns_floor_dyn.pdf`.
- *Provenance:* **[SIM]** — seeded `floor_protocol_movie` traces / record `e3b_production.json`
  (confirmed present). Superseded.

#### **`tcns_formation_gallery.pdf`** — vector PDF
- NOT used — a gallery of the 20 formations laid out individually
  (`tcns_scenario_figs.fig_formation_gallery`); **superseded** in §VIII by the overlaid
  `tcns_formations.pdf` (Fig. 6). Kept as the gallery variant.
- *Theory:* `thm:floorF` **[PROVEN]** formation invariance — a gallery variant of the used
  `tcns_formations.pdf`.
- *Provenance:* **[SIM]** — the seeded formation ensemble of committed
  `e3a_extension.json["formation_cluster"]` (confirmed present). Superseded.

#### **`tcns_gauge_story.pdf`** — vector PDF
- NOT used — the scenario-style gauge-drift narrative from
  `tcns_scenario_figs.fig_gauge_story`; **superseded by `tcns_gauge_trails.pdf`** (Fig. 3).
  Kept as a variant.
- *Theory:* `thm:gaugeF` / `cor:pinF` gauge drift — a scenario variant of the used
  `tcns_gauge_trails.pdf`.
- *Provenance:* **[SIM]** — seeded `anim_gauge` run / supplementary movie `gauge_drift.mp4`
  (confirmed present). Superseded.

#### **`tcns_ladder_bars.pdf`** — vector PDF
- NOT used — alternate switch-off / transport-rule ablation bars from
  `paper_artifacts` (fig 9 there); **superseded by `tcns_ladder.pdf`** (Fig. 20). Kept as a
  variant. [CONJ] object; same A1-below-paper inversion.
- *Theory:* **NOT a theorem** — the `D_ss` **[CONJ]** transport-rule ablation, an alternate of
  the used `tcns_ladder.pdf` (same A1-below-paper inversion).
- *Provenance:* **[SIM]** — reads committed `e3b_production.json` (confirmed present). Superseded.

#### **`tcns_topology_gallery.pdf`** — vector PDF
- NOT used — a gallery of the four comms topologies with their λ₂
  (`tcns_scenario_figs.fig_topology_gallery`); a companion/alternate to the quantitative
  `tcns_topology.pdf` (Fig. 19). Kept as the illustrative gallery.
- *Theory:* no theorem — an illustrative gallery of the four comms topologies with their λ₂
  (companion to the quantitative used `tcns_topology.pdf`).
- *Provenance:* **[DIAGRAM]** — topology schematics; the λ₂ annotations are deterministic
  algebraic-connectivity (Laplacian) eigenvalues, no measured / seeded data.

#### **`theorem_map.pdf`** — vector PDF
- NOT used in §VIII — the statement-dependency map from `shared_figs_ieee.fig_theorem_map`.
  §VIII renders only the falsifier forest (`t1_falsifier_forest.pdf`). Kept for the broader
  paper / overview.
- *Theory:* no theorem — the statement-dependency map itself (a conceptual overview of the
  lemma → theorem → corollary structure).
- *Provenance:* **[DIAGRAM]** — conceptual diagram, no measured data.

## 4. Epistemic notes (folder-specific guardrails)

- **Two different objects, never conflated.** (1) The **holonomy amplitude** `‖Log Hol‖` —
  the object of **Thm 7.2 [PROVEN]**, measured slope **1.999** (Tier-1), coefficient 1.0000,
  resolved only noise-off; symmetric-class switch-offs are **machine-zero** (ξ=0 literally
  0.0). Figures: `tcns_amplitude`, `tcns_formations`, `lcss_levelset_bars`, `tcns_f5_amp`.
  (2) The **closed-loop steady-state disagreement `D_ss` [CONJECTURAL]**, measured slope
  **~1.08–1.10** (1.101 [1.076,1.125] Tier-1), a MEASURED slope in a conjectural regime,
  carried with the R3 caveat, asserted as **NO law**; its CI excludes both 1 and 2. Figures:
  `tcns_f4b`, `tcns_dss_cdf/box`, `tcns_floor_dyn`, `tcns_f5_floor`, `tcns_ladder`,
  `tcns_robust`. **Never caption a `D_ss` fit as validating Thm 7.2; never call the `D_ss`
  slope a first-order law.**
- **Honest falsifier verdicts** (from `docs/ral_package.md`): C7a/C8/C13 **PASSED**; C6
  **PASSED** (1.403); C9b′ **PASSED** (1.006). C7b **FALSIFIED at these scales** (1.101).
  C9b falsifier condition **MET** on the declared seed-paired estimator (1.58 [1.44,1.84]; the
  registered single-power model is mis-specified for a linear+quadratic mixture; the unpaired
  [0.43,2.89] is **under-powered** and adjudicates nothing). C9c **TRIPS** (2.75× < 10×). C19
  **TRIPPED** in the **favorable** direction (2.48; remainder vanishes faster than 2nd order —
  restated with corrected order, **not** counted as a pass). A tripped / fired / falsified /
  MET row is **never** presented as a positive result.
- **`D_ss` is a disagreement, not a truth error** (see `tcns_gauge_errors` and the
  `tcns_ladder` inversion): agreement is purchasable by groupthink, so `D_ss` **never ranks
  transport rules** — rule ranking belongs to the truth-referenced metrics on the companion
  (RA-L) plant only. There are **no Drake / ANEES / docking figures in this Tier-1 section**;
  any such claim belongs to the companion and carries its own horizon there.
- **Units & frames.** World ENU, metres; SE(2) load pose = (x, y, yaw); the disagreement
  metric `D = ‖Log(G_i⁻¹G_j)‖²` is in m² (with the yaw component). τ is in seconds on the grid
  {0.05…1.6}. Predictions are labelled predictions; only realized/measured states are stated
  as facts.
- **C15 level set** is presented as an **observation** (proof open): the protected class is a
  discrete level set of `s ↦ C(s;ξ)` (two zeros per reference torus); zero-commutator pairs all
  have `C_i = C_j` to 1e-16 and the full holonomy vanishes at all orders.
- The paper currently carries an **empty bibliography** (zero `\cite`). These figures are not
  externally cited; make no such claim.

## 5. Cross-links

- **Paper source:** `../section8.tex` (this folder is `papers/tcns_section8/figures/`), with
  the inline architecture TikZ at `../fig_arch.tex` and preview wrapper `../standalone.tex`.
- **Authoritative ledger (verdicts + epistemic status):** `../../../docs/ral_package.md`.
- **Reconciliation note:** `../../../docs/reconciliation_2026-07-21.md`.
- **Generators:** `../../../tier1_sheaf/campaign/tcns_figs_ieee.py` (primary),
  `lcss_figs_ieee.py`, `shared_figs_ieee.py`, `tcns_scenario_figs.py`, `paper_artifacts.py`
  (reproducibility driver), `e3a_extension_panels.py`, `f5_symmetry_fig.py`.
- **Shared style:** `../../../analysis/ieee_style.py`.
- **Data records:** `../../../tier1_sheaf/results/` (`e3a_amplitude.csv`, `e3a_extension.json`,
  `e3b_production.json`, `e3c_symmetry.json`, `e3c_c9b_seeds.json`, `e3c_robust.json`,
  `e2_contraction.json`, `e6_topology.json`, `e10_dt_sweep.json`) and the rendered PDFs under
  `tier1_sheaf/results/artifacts/ieee/`.
- **Companions:** the RA-L "Blind Harbor" multibody paper (Drake numerics, cross-tier
  equivalence, D9/ANEES/docking) and the L-CSS latency-curvature-floor letter — both **out of
  scope** for this Tier-1 section.
