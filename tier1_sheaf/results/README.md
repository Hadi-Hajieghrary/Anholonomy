# `tier1_sheaf/results/` — Tier-1 sheaf campaign records, figures, and movies (source / build folder)

This is the **source/build** folder for the Tier-1 (reduced-plant) numerics behind two
papers:

- **L-CSS floor letter** — `papers/lcss_letter/main.tex` — the *latency–curvature floor*
  letter. Its claim: the error-transport **holonomy amplitude** obeys
  `‖Log Hol‖ = τ² ‖[Cᵢ,Cⱼ]‖ + O(τ³)`, an **O(τ²) law [PROVEN, Thm 7.2]** (measured
  slope 1.999), switched off exactly on the symmetric / **C15 level-set** class.
- **T-CNS flagship §VIII** — `papers/tcns_section8/section8.tex` — the flagship's
  numerical-validation section, **Tier-1 sheaf numerics ONLY** (no Drake figures here;
  the multibody campaign is the RA-L "Blind Harbor" companion).

Authoritative epistemic ledger: [`docs/ral_package.md`](../../docs/ral_package.md).
Reconciliation of papers ↔ campaign: [`docs/reconciliation_2026-07-21.md`](../../docs/reconciliation_2026-07-21.md).

Because this is a build folder, the catalogue below is **provenance-focused**: for each
family it names the generator script, the data record it reads, whether it is
**CANONICAL** (copied into a `papers/*/figures/` folder and `\included`) or
**SUPERSEDED/dev-only**, and the one-line epistemic verdict. For the full
reader-facing narrative, cross-link to the paper `figures/` folders
(`papers/lcss_letter/figures/`, `papers/tcns_section8/figures/`).

---

## 0. Data provenance & authenticity

Every figure and movie catalogued below carries two added lines — a **`*Theory:*`**
line (the specific paper statement it bears on, cited by label + number, or the honest
empirical thesis / falsifier when no theorem applies) and a **`*Provenance:*`** line
(its authenticity class + the exact record it reads, the operator + fixed inputs it
recomputes, or a diagram label). The four authenticity classes and their counts across
the **50 figure/movie entries** augmented below (Sections 3, 4, 5a, 5c):

| Class | Count | Meaning |
|---|---|---|
| **[SIM]** | **29** | ran the actual reduced plant / gauge-fusion / step-perturbation with a **seeded** `np.random.default_rng` and wrote (or replays seed-exactly) a committed `*.json` / `*.csv` record; the figure reads that record. Seeded reproducible simulation noise = real simulated data. |
| **[DET]** | **17** | exact analytic recomputation from released operators (`holonomy_amplitude_m2`, `two_agent_commutator`, `conjugated_generator`, `sheaf_laplacian`) at **fixed** inputs (common twist `ξ=(0.4,0,0.12)`, analytic shapes) with **no randomness**. Real computation. |
| **[DIAGRAM]** | **4** | conceptual/schematic — tow geometry, plant object, architecture, statement-dependency map. Labelled as such; **no measured curve** is plotted as data. |
| **[FLAG]** | **0 now** | fabricated / untraceable. **One was found and fixed:** `artifacts/ieee/tcns_e1_spectrum` shipped fabricated (hardcoded eigenvalue fallback) until it was regenerated from the real `sheaf_laplacian` on **2026-07-22** — see its entries below. Repo-wide sweep: the only silent-fallback site. |

**Finding (asserted true after tracing every entry, as of 2026-07-22):** *every data figure
traces to a committed, seeded simulated record or a deterministic operator recomputation from
released code; the four diagrams are labelled as diagrams and plot no measured data; nothing
is fabricated — with one figure (`tcns_e1_spectrum`) having been found fabricated and
corrected at the generator rather than patched over.* The 11 ground-truth records of Section 2 are the **[SIM]/[DET]
sources themselves** — each was `ls`-confirmed present on disk (e.g. `e3a_extension.json`
opened and confirmed to hold real arrays: `formation_cluster.slopes`, 220-draw
`remainder_constant`, C15 pair bank — not an empty stub). The Section 5b gallery figures
are **superseded duplicates** that inherit the authenticity class of their `ieee/`
counterpart (no independent data). The superseded early diagnostic `e3_diagnostic.csv`
(Section 2) is a **real** early-harness run, not fabricated — but its ≈2.0 `D_ss` slope
is a reconciled artifact and is flagged in-text as **not** citable against Thm 7.2.

**Epistemic guardrail carried through every line below:** the holonomy **amplitude**
(slope 1.999, switch-offs machine-zero) is the **[PROVEN]** object of **Thm 7.2
(`thm:floor`) / `thm:floorF`**; the closed-loop **`D_ss`** (slope 1.101, m²) is a
**[CONJECTURAL]** object — *different object, never conflated*; no `D_ss` figure is ever
captioned as validating the floor theorem. Falsifier verdicts are reported as
adjudicated (C7b FALSIFIED, C9b MET 1.58, C9c TRIPS 2.75× < 10×, C19 tripped-favorable),
never as positive results.

---

## 1. How this folder relates to the papers

The `\included` figures do **not** live here directly — they live in
`papers/lcss_letter/figures/` and `papers/tcns_section8/figures/`. Their **byte
sources** are in `artifacts/ieee/` (the IEEE-final redesign). The relationship:

| Layer | Location | Role |
|---|---|---|
| Data records | top-level `*.json`, `*.csv` | ground truth; every figure re-derives from these |
| IEEE-final figures | `artifacts/ieee/*.{pdf,png}` | **CANONICAL** — copied into `papers/*/figures/` and `\included` |
| Research-artifact-package figures | `artifacts/*.{pdf,png}` (not `ieee/`) | earlier artifact-gallery design; mostly **SUPERSEDED** by the `ieee/` redesign |
| Legacy shared figures | top-level `f4b_tier1.*`, `f5_symmetry.*`, `f8_contraction.*`, `e1_gauge.png`, `e3a_amplitude.png`, `e3_diagnostic.*`, `e3a_extension_panels.*` | **SUPERSEDED** by the `tcns_*`/`lcss_*` redesign; kept for provenance |
| Supplementary movies | top-level `*.mp4`, `*.gif` | **CANONICAL** — referenced as movies S1–S3 (letter) / M1–M3 (§VIII) |

**Generators** (all under `tier1_sheaf/campaign/` unless noted):
- `lcss_figs_ieee.py`, `tcns_figs_ieee.py`, `shared_figs_ieee.py` → the canonical `artifacts/ieee/` figures.
- `paper_artifacts.py`, `lcss_scenario_figs.py`, `tcns_scenario_figs.py` → the top-level `artifacts/` package figures.
- Movie scripts: `holonomy_movie.py`, `level_set_movie.py`, `formation_sweep_movie.py`, `floor_protocol_movie.py`, `contraction_movie.py`; `experiments/anim_gauge.py` (gauge drift).
- Cell drivers: `experiments/e1_gauge.py`, `experiments/e3a_amplitude.py`, `experiments/e3c_symmetry.py`, `experiments/e2_contraction.py`, `campaign/e3a_extension.py`, `campaign/e3b_production.py`, `campaign/e3c_c9b_v2.py`, `campaign/e6_topology.py`, `campaign/e10_dt_sweep.py`.

The two figure objects are **never conflated** in either paper and must not be here:
1. **Holonomy amplitude** = the object of **Thm 7.2 [PROVEN]**, slope **1.999** (Tier-1),
   switch-offs machine-zero (ξ=0 literally `0.0`).
2. **Closed-loop steady-state disagreement `D_ss`** = a **[CONJECTURAL]** object, `m²`,
   measured slope **1.101 [1.076, 1.125]** on this plant — a *measured slope in a
   conjectural regime, carried with the R3 caveat, asserted as NO law* (CI excludes
   both 1 and 2). **Never** caption a `D_ss` fit as validating Thm 7.2.

---

## 2. Data records (ground truth — every figure re-derives from these)

Units/frame throughout: world ENU, metres; SE(2) load pose = (x, y, yaw); `τ` in s;
`η` in rad/s; `D`/`D_ss` in **m²**.

- **`e1_gauge.csv`** — driver `experiments/e1_gauge.py` (cell E1). Columns
  `anchor_strength, dim_ker, lambda_min`. Records `dim ker L_F = 3` with no anchor,
  collapsing to 0 with one anchor. Verdict: gauge/pinning **PASSED** (kernel dim = 3;
  section annihilated to 1.3e-15). **Note (2026-07-22):** this CSV is the E1 experiment's
  own anchor-strength sweep; the paper figure `tcns_e1_spectrum` does **not** read it —
  `fig_e1_spectrum` independently re-assembles `sheaf_laplacian` on this script's same
  triangle config and takes `eigvalsh` ([DET], not a record read). The two agree by
  construction (both assert `dim ker = 3`).

- **`e3a_amplitude.csv`** — driver `experiments/e3a_amplitude.py` (cell E3a). Per-arm
  fitted slope + amplitude at τ∈{0.05,0.1,0.2,0.4,0.8,1.6}. Generic slope **1.9992…**;
  symmetric/η=0/ξ=0 arms at machine zero (`nan` slope = flat at ~1e-16). **CANONICAL
  data** behind the amplitude figures. Verdict: **PASSED** (C7a/C8/C13), Thm 7.2 object.

- **`e3a_extension.json`** — driver `campaign/e3a_extension.py` (seed 2026). Keys:
  `formation_cluster` (20-draw slope **1.9993 ± 0.0000**), `remainder_constant`
  (sup‖R‖/τ³ **≤ 0.0133** over 220 draws), `tau0` (explicit τ=0 arm = exactly 0),
  `C15_pairs_found` / `C15` (five zero-commutator pairs, `Cᵢ=Cⱼ` to 1e-16). **CANONICAL
  data** behind the extension arms and the C15 level-set discovery. Verdict:
  amplitude order is a structural constant; **C15 protected class = a discrete level
  set of s↦C(s;ξ)**, full holonomy vanishes at ALL orders (stated as an observation,
  proof open).

- **`e3b_production.json`** — driver `campaign/e3b_production.py` (cell E3b, **1584
  runs** = 12 formations × 10 seeds per τ + controls). The closed-loop `D_ss`
  production record. Fitted excess exponent **1.101 [1.076, 1.125]**. **CANONICAL data**
  behind `tcns_f4b` / `tcns_dss_*` / `tcns_floor_dyn` / `tcns_ladder`. Verdict:
  **C7b FALSIFIED at these scales** — the conjectured order 2 is excluded (and so is 1);
  reported as a measured slope, **no law**. Frozen+noise-off arm reproduces the null
  `D_ss ~ 1e-30`.

- **`e3c_symmetry.json`** — driver `experiments/e3c_symmetry.py` (cell E3c). Amplitude
  ε-response `C9bp_amplitude` (slope **1.006**, base commutator exactly 0). **CANONICAL
  data** behind `tcns_f5_amp` / `f5_symmetry`. Verdict: **C9b′ PASSED** (amplitude
  object, first-order departure from the symmetric class).

- **`e3c_c9b_seeds.json`** — driver `campaign/e3c_c9b_v2.py` (cell E3c, seed-paired
  estimator). The closed-loop-floor ε-exponent. **CANONICAL data** behind `tcns_f5_floor`.
  Verdict: **C9b falsifier condition MET** on the declared seed-paired estimator —
  **1.58 [1.44, 1.84]** (both 2 and 1 excluded); the registered single-power model is
  mis-specified for a linear+quadratic mixture. The unpaired estimator [0.43, 2.89] is
  UNDER-POWERED and adjudicates nothing. `[CONJECTURAL]` regime.

- **`e3c_robust.json`** — driver `campaign/e3c_c9b_v2.py` (robust arm). Robust
  symmetric-suppression factor under 20% jitter + 10% drops. **CANONICAL data** behind
  `tcns_robust`. Verdict: **C9c TRIPS on Tier-1** — 2.75× [1.94, 3.89] `<` the
  registered 10× threshold; large protection is an **amplitude-object property only**,
  and this arm is explicitly **outside protocol class 𝒫** (heterogeneous realized ages).

- **`e2_contraction.json`** — driver `experiments/e2_contraction.py` (cell E2).
  Contraction-rate vs κλ₂ over two topologies + the log-linearity remainder.
  **CANONICAL data** behind `tcns_f8` / `tcns_contraction_*`. Verdict: **C6 PASSED**
  (slope **1.403**; μ = **−0.062** topology-independent — the consensus term does the
  contraction). **C19 falsifier TRIPPED (2.48 [2.32, 2.65])** but in the **FAVORABLE**
  direction (remainder vanishes faster than 2nd order) — restated with corrected order,
  **NOT counted as a pass**.

- **`e6_topology.json`** — driver `campaign/e6_topology.py` (cell E6, exploratory).
  Floor vs topology×N (cycle/path/star/complete, N∈{4,6,8}) ordered by λ₂. **CANONICAL
  data** behind `tcns_topology`. Verdict: **C10 (exploratory, no falsifier)** —
  connectivity suppresses the floor up to **5×** at moderate τ; benefit collapses to
  **≤2×** at high τ; complete graphs most τ-sensitive.

- **`e10_dt_sweep.json`** — driver `campaign/e10_dt_sweep.py` (cell E10). Excess
  exponent across Δt∈{0.001,0.0025,0.005,0.01}s (10× range). **CANONICAL data** behind
  `tcns_dt`. Verdict: **PASSED** — all CIs share **[1.185, 1.256]**; no exponent above
  is a discretization artifact.

- **`e3_diagnostic.csv` / `e3_diagnostic.png`** — driver `experiments/run_e3_diagnostic.py`
  (early E3b diagnostic). Reports a `D_ss` slope ≈ **2.006** (A2/generic, noise ON/OFF).
  **SUPERSEDED / dev-only.** ⚠ This early diagnostic's ~2.0 slope was reconciled to the
  corrected 1584-run production value **1.101** in `e3b_production.json`; the ≈2 value
  here is a superseded harness artifact and **must not** be cited as validating Thm 7.2
  or any order-2 `D_ss` law.

---

## 3. Top-level figures (legacy shared Tier-1 — SUPERSEDED)

These were the earlier shared Tier-1 figures (they are the ones the `docs/ral_package.md`
figure inventory still lists). The current L-CSS/T-CNS papers `\include` the redesigned
`tcns_*`/`lcss_*` variants instead, so these are **SUPERSEDED, kept for provenance**.

- **`f4b_tier1.pdf` / `.png`** — closed-loop `D_ss` panel, cell E3b. Generator not present
  in the current `campaign/` tree (pre-redesign build). **SUPERSEDED by** `artifacts/ieee/tcns_f4b.pdf`.
  Verdict: `D_ss` slope 1.101, **[CONJECTURAL] / falsified-at-scale** — never a slope-2 law.
  - *Theory:* **no theorem** — empirical "price of staleness" `D_ss` thesis; **falsifier C7b FALSIFIED-at-scale** (order 2 excluded, so is 1). The CONJECTURAL closed-loop object, **explicitly NOT a test of Thm 7.2 (`thm:floor`) / `thm:floorF`** whose object is the amplitude.
  - *Provenance:* **[SIM]** — reads `e3b_production.json` (1584 seeded runs; confirmed present); frozen+noise-off arm reproduces the null `D_ss ~ 1e-30`.

- **`f5_symmetry.pdf` / `.png`** — symmetry pair figure (both metrics on one sheet),
  generator `campaign/f5_symmetry_fig.py`, reads `e3c_symmetry.json` + `e3c_c9b_seeds.json`.
  **SUPERSEDED by** the split `artifacts/ieee/tcns_f5_amp.pdf` (amplitude, C9b′ PASSED)
  **and** `tcns_f5_floor.pdf` (floor, C9b falsifier MET 1.58). The split exists precisely
  so the PROVEN amplitude object and the CONJECTURAL floor object are never mixed.

- **`f8_contraction.pdf` / `.png`** — contraction rate vs κλ₂. Generator not in current
  `campaign/` tree. Reads `e2_contraction.json`. **SUPERSEDED by** `artifacts/ieee/tcns_f8.pdf`.
  Verdict: **C6 PASSED** (slope 1.403; μ=−0.062).

- **`e1_gauge.png`** — gauge-spectrum bar figure, generator `experiments/e1_gauge.py` /
  `experiments/build_gallery.py`, reads `e1_gauge.csv`. **SUPERSEDED by**
  `artifacts/ieee/tcns_e1_spectrum.pdf`. Verdict: gauge/pinning **PASSED**.
  **Note (2026-07-22):** this raster was computed from the real Laplacian throughout, while
  the superseding IEEE PDF was **fabricated** (hardcoded eigenvalue fallback) until it was
  regenerated on 2026-07-22 — during that window this was the only honest rendering of E1.

- **`e3a_amplitude.png`** — amplitude-law plot, generator `experiments/build_gallery.py` /
  `lcss_figs_ieee.py`, reads `e3a_amplitude.csv`. A copy sits in both paper `figures/`
  folders but the papers `\include` `lcss_amplitude.pdf` / `tcns_amplitude.pdf` instead —
  so this raster is **dev/legacy**. Verdict: amplitude **PASSED** (slope 1.999).

- **`e3a_extension_panels.pdf` / `.png`** — multi-panel extension summary, generator
  `campaign/e3a_extension_panels.py`, reads `e3a_extension.json`. Present in both paper
  `figures/` folders but **not `\included`** (the extension arms ship as the individual
  `lcss_slope_hist` / `lcss_remainder_cdf` / `lcss_bound_ratio` / `lcss_domain` /
  `lcss_levelset_bars` figures). **SUPERSEDED / dev-only.** Verdict: extension arms all
  PASSED; C15 level-set observed.

---

## 4. Supplementary movies (CANONICAL)

All seeded/deterministic; each carries a distinct piece of the argument. Referenced by
filename in the papers.

- **`holonomy_loop.mp4`** — generator `campaign/holonomy_movie.py`. Letter movie **S1**:
  the four-leg loop `e^{τCᵢ}e^{τCⱼ}e^{−τCᵢ}e^{−τCⱼ}` fails to close; the closing gap is
  the holonomy, growing along the **τ² [PROVEN]** law. 20 fps.

- **`level_set.mp4`** — generator `campaign/level_set_movie.py`, reads `e3a_extension.json`.
  Letter movie **S2**: generic pair (loop opens ∝τ²) vs the discovered **C15 level-set**
  pair 1.06 rad apart (loop closes to 1e-16 at every τ). One changed variable: the
  commutator. Verdict: exact all-orders protection on the level set (observed).

- **`formation_sweep.mp4`** — generator `campaign/formation_sweep_movie.py`, reads
  `e3a_extension.json` (replayed seed-exact, asserted against the record). Letter movie
  **S3**: the 20-formation draw sequence collapsing onto slope **1.9993** — order is
  structural, geometry moves only the coefficient. 10 fps.

- **`gauge_drift.mp4`** and **`gauge_drift.gif`** — generator `experiments/anim_gauge.py`.
  §VIII movie **M1**: three agents fuse without an anchor, stay mutually consistent, drift
  **as a group** along the SE(2) gauge; a beacon collapses the gauge and all snap to truth.
  The two on-screen curves (disagreement vs truth error) are the two objects the paper
  refuses to conflate. `.gif` = derived alt format of the `.mp4`. 8 fps.

- **`contraction.mp4`** — generator `campaign/contraction_movie.py`, reads
  `e2_contraction.json`. §VIII movie **M2**: identical step perturbations decaying under
  C₅ vs K₅, rates ordered by κλ₂ (C6's tested prediction; LTV/frozen hedge on-screen).
  15 fps. Verdict: **C6 PASSED**.

- **`floor_protocol.mp4`** — generator `campaign/floor_protocol_movie.py`, reads
  `e3b_production.json`. §VIII movie **M3**: the reduced plant executes the persistent turn
  while `D(t)` for two stalenesses rises to steady state inside the evaluation window.
  On-screen caption carries the registry hedge verbatim — `D_ss` is measured in the
  **[CONJECTURAL]** regime; the movie demonstrates the **protocol**, it is **not** a test
  of Thm 7.2. 25 fps.

---

## 5. `artifacts/` subfolder

### 5a. `artifacts/ieee/` — CANONICAL IEEE-final figures (sources of the `\included` figures)

Generated by `lcss_figs_ieee.py`, `tcns_figs_ieee.py`, `shared_figs_ieee.py`. Each
basename ships as a `.pdf` + `.png` pair; the `.pdf` is copied into `papers/*/figures/`
and `\included`. Full reader captions live in the paper `figures/README.md`. Verdicts
are those of §2's data records.

**L-CSS letter figures** (from `lcss_figs_ieee.py`, reading `e3a_amplitude.csv` /
`e3a_extension.json`):
- `lcss_geometry`, `lcss_shape_motion` — tow geometry & shape-angle motion (conceptual).
- `lcss_amplitude` — the amplitude law, slope 1.999, switch-offs at machine zero **[PROVEN]**.
- `lcss_loop_generic`, `lcss_loop_levelset` — the loop-trail mechanism (generic vs level-set).
- `lcss_carpet` — amplitude field over τ × shape-separation (growth law + protected valley).
- `lcss_slope_hist` — formation invariance (20 slopes span 5.7e-14 around 1.9993).
- `lcss_remainder_cdf` — remainder-constant CDF (sup ≤ 0.0133 over 220 draws).
- `lcss_bound_ratio` — measured/predicted → 1 as τ→0 (leading-order tightness).
- `lcss_domain` — domain boundary (10% departure only at τ≈10).
- `lcss_heatmap` — global commutator map over the shape torus; **discrete** level set (2 zeros).
- `lcss_levelset_bars` — the five C15 pairs all satisfy Cᵢ=Cⱼ to 1e-16 (**also `\included` by §VIII**).

**T-CNS §VIII figures** (from `tcns_figs_ieee.py`, reading the E-cell records):
- `tcns_plant` — reduced plant + comms graph (E-cell config).
- `tcns_e1_spectrum` — gauge spectrum, dim ker = 3 (E1) **PASSED**.
- `tcns_gauge_trails`, `tcns_gauge_errors` — gauge drift & the two distinct error objects.
- `tcns_amplitude` — amplitude law (F4a) **[PROVEN]**.
- `tcns_formations` — E3a formation invariance (slope 1.9993).
- `tcns_f4b` — the `D_ss` floor, excess exponent 1.101 **[CONJECTURAL], falsified-at-scale**.
- `tcns_dss_cdf`, `tcns_dss_box` — per-run `D_ss` distributions **[CONJECTURAL]** (never a Thm-7.2 test).
- `tcns_floor_dyn` — `D_ss` measurement protocol (dynamics into steady state) **[CONJECTURAL]**.
- `tcns_f5_amp` — symmetry, amplitude object (C9b′, slope 1.006) **PASSED**.
- `tcns_f5_floor` — symmetry, closed-loop floor (C9b, seed-paired ε-exponent 1.58) **falsifier MET**.
- `tcns_robust` — C9c robust suppression **TRIPS** at 2.75× (< 10×), outside class 𝒫.
- `tcns_f8` — contraction vs κλ₂ (C6, slope 1.403) **PASSED**; μ=−0.062 anchored.
- `tcns_contraction_xy`, `tcns_contraction_decay` — contraction trajectories & decay.
- `tcns_dt` — E10 numerics invariance (CIs share [1.185, 1.256]) **PASSED**.
- `tcns_topology` — E6 connectivity vs floor (5×→2×) **exploratory (C10)**.
- `tcns_ladder` — E3b transport-rule ablation, median `D_ss` **[CONJECTURAL]**; shows the
  Tier-1 A1-below-paper **inversion** honestly (`D_ss` is a disagreement metric, never
  ranks rules).

**Shared** (from `shared_figs_ieee.py`):
- `t1_falsifier_forest` — the complete adjudicated Tier-1 falsifier ledger (green passed,
  red falsified/met, orange C19 tripped-favorably). `\included` by **both** papers.
- `theorem_map`, `tcns_arch` — raster theorem-map / architecture. **NOT `\included`** — the
  papers draw these as TikZ via `\input{fig_thmmap.tex}` / `\input{fig_arch.tex}`; these
  rasters are alternates.

### 5b. `artifacts/*.{pdf,png}` (top level) — research-artifact-package gallery (mostly SUPERSEDED)

Generated by `paper_artifacts.py`, `lcss_scenario_figs.py`, `tcns_scenario_figs.py` for an
earlier structured artifact gallery. Most are **SUPERSEDED** by the differently-named
`ieee/` redesign (naming differs: e.g. `lcss_commutator_heatmap`→`lcss_heatmap`,
`lcss_amplitude_carpet`→`lcss_carpet`, `lcss_remainder_stats`→`lcss_remainder_cdf`,
`lcss_domain_boundary`→`lcss_domain`, `lcss_bound_tightness`→`lcss_bound_ratio`,
`tcns_architecture`→`tcns_arch`, `tcns_dss_dist`→`tcns_dss_cdf`,
`tcns_floor_dynamics`→`tcns_floor_dyn`, `tcns_dt_invariance`→`tcns_dt`,
`tcns_ladder_bars`→`tcns_ladder`, `tcns_contraction_portrait`→`tcns_contraction_xy`).
`t1_falsifier_forest` and `theorem_map` here duplicate the shared figures. `.pdf`+`.png`
pairs each. Epistemic verdicts identical to the corresponding `ieee/` figure / §2 record.

L-CSS gallery: `lcss_amplitude_carpet`, `lcss_bound_tightness`, `lcss_commutator_heatmap`,
`lcss_commutator_landscape`, `lcss_domain_boundary`, `lcss_graphical_abstract`,
`lcss_loop_filmstrip`, `lcss_remainder_stats`, `lcss_schematic`, `lcss_transit_scene`.
T-CNS gallery: `tcns_architecture`, `tcns_contraction_portrait`, `tcns_dss_dist`,
`tcns_dt_invariance`, `tcns_floor_dynamics`, `tcns_formation_gallery`, `tcns_gauge_story`,
`tcns_ladder_bars`, `tcns_plant`, `tcns_robust`, `tcns_topology`, `tcns_topology_gallery`.
Shared: `t1_falsifier_forest`, `theorem_map`.

### 5c. `artifacts/*.json` — figure-side meta records (written by `paper_artifacts.py`)

- **`ladder_medians.json`** — per-τ median `D_ss` per E3b arm (m²), read back to draw the
  ladder bars. **[CONJECTURAL]** regime — a disagreement metric, never ranks rules.
- **`bound_tightness_meta.json`** — the measured/predicted-ratio summary behind
  `lcss_bound_tightness`. Amplitude object **[PROVEN]**.
- **`commutator_heatmap_meta.json`** — torus-scan summary behind the commutator heatmap
  (discrete C15 level set: 2 zeros; partner 1.057 rad away). Observation, proof open.
- **`domain_boundary_meta.json`** — large-τ domain-boundary summary (10% departure at
  τ≈10) behind `lcss_domain_boundary`. Amplitude object **[PROVEN]**.

---

## 6. Reproducibility

Every number traces to a seeded, versioned driver; `campaign_replay.py` re-executes
per-run probes that must match committed records (Tier-1 exact-class to 1e-9). The
figure generator `campaign/paper_artifacts.py` re-derives the 20-formation and 220-draw
extension datasets seed-exactly at import and **refuses to plot on mismatch**, so figures
cannot silently drift from the records. Cell → driver → record → probe map:
`docs/ral_package.md` §3 and `papers/tcns_section8/section8.tex` Table (registry).

**Epistemic guardrails (binding):** the holonomy **amplitude** (slope 1.999, switch-offs
machine-zero) is the **[PROVEN]** object of Thm 7.2; the closed-loop **`D_ss`** (slope
1.101, m²) is a **[CONJECTURAL]** object, falsified-at-scale, reported as measured with no
law asserted. Tripped/fired/met falsifier rows (C7b, C9b, C9c, C19) are reported honestly
and are **never** presented as positive results. The papers carry **empty bibliographies**
(zero `\cite`) — do not claim any of these artifacts is externally cited.
