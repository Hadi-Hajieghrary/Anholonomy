# IEEE single-plot figure artifacts (`tier1_sheaf/results/artifacts/ieee/`)

**This is a source/build folder, not a reader-facing paper folder.** Every file here is
an IEEE-restyled, *one-plot-per-figure* render emitted by the `*_figs_ieee.py`
generators under `tier1_sheaf/campaign/`. Canonical figures are then **copied** into a
`papers/*/figures/` tree and `\includegraphics`-ed by the two papers; the rest are
dev-only or superseded. This README carries the **provenance** (generator + data record
+ canonical/superseded status + one-line epistemic verdict) for every file. For the full
reader-facing caption/narrative of a figure, read the corresponding `\caption{}` in the
paper `.tex` (there is no `papers/*/figures/README.md`).

- **L-CSS floor letter** — `papers/lcss_letter/main.tex` (Tier-1 numerics; the
  latency–curvature floor + the C15 level-set protected class).
- **T-CNS Section VIII** — `papers/tcns_section8/section8.tex` (the flagship journal's
  numerical-validation section, **Tier-1 sheaf plant only — NO Drake figures here**).
- **Authoritative ledger** — `docs/ral_package.md` (verdicts + epistemic status).
- **Reconciliation** — `docs/reconciliation_2026-07-21.md`.

All frames are world ENU, metres; the SE(2) load pose is `(x, y, yaw)`; the closed-loop
disagreement `D` is in `m^2`. Predictions are labelled as predictions; only
realized/measured states are stated as facts. The paper bibliographies are currently
**empty** — nothing here is externally cited.

## Data provenance & authenticity

Every one of the **34 figure entries** below has been traced to its generator, its data
mechanism, and the specific statement it bears on (see the *Theory:* / *Provenance:* lines
appended under each family table). The authenticity classes tally as:

- **[SIM] — 21** figures. A generator ran the actual Tier-1 `ReducedPlant` (or the gauge /
  contraction / protocol harness) with a **seeded** `np.random.default_rng` and wrote (or
  replay-asserts against) a **committed record** on disk; the figure reads that record. A
  seeded rng is *reproducible simulated noise* — real simulated data, not fabrication. The
  named records — `results/e3a_amplitude.csv`, `results/e3a_extension.json`,
  `results/e3b_production.json`, `results/e3c_robust.json`, `results/e3c_symmetry.json`,
  `results/e3c_c9b_seeds.json`, `results/e2_contraction.json`, `results/e6_topology.json`,
  `results/e10_dt_sweep.json`, `results/e1_gauge.csv` — are **all confirmed present** in
  `tier1_sheaf/results/` (verified by `ls`; a `.csv`/`.json` head shows populated arrays,
  not empty stubs).
- **[DET] — 9** figures. The figure recomputes an exact analytic quantity from released
  operators (`holonomy_amplitude_m2`, `two_agent_commutator`, `conjugated_generator`, the
  SE(2) `expm` loop walk, or the `sheaf_laplacian` spectrum) at **fixed inputs** (the common
  twist `XI = (0.4, 0, 0.12)` and released C15/level-set shapes) with **no randomness**. Real
  computation, not fabrication.
- **[DIAGRAM] — 4** figures (`lcss_geometry`, `tcns_plant`, `tcns_arch`, `theorem_map`).
  Conceptual/schematic drawings with **no measured data**; each is labelled as a schematic
  and carries no numeric claim. `tcns_arch` and `theorem_map` are additionally superseded by
  inline TikZ in the papers.
- **[FLAG] — 0** figures. **Nothing untraceable or fabricated was found.**

**Finding (as of 2026-07-22):** every *data* figure traces to a committed simulated record
(seeded, reproducible) or to a deterministic operator recomputation at fixed inputs; the four
diagrams are labelled as such and make no measurement claim; nothing is fabricated — **with
one exception since corrected: `tcns_e1_spectrum` shipped fabricated** (its generator's real
`sheaf_laplacian` call failed on a wrong API signature and an inner `try/except` silently
substituted a hand-typed eigenvalue array) and was regenerated from the real operator on
2026-07-22, with the fallback replaced by loud asserts. A sweep of every figure generator
confirmed it was the only silent-fallback site. The two epistemically distinct
objects — the **[PROVEN]** holonomy *amplitude* (`thm:floor` / `thm:floorF`) and the
**[CONJECTURAL]** closed-loop `D_ss` — are kept separate throughout: a `D_ss` figure is never
captioned as validating the floor theorem. One caution worth stating plainly: the
`t1_falsifier_forest` non-slope confidence intervals are **hard-coded constants transcribed
from the committed ledger `docs/ral_package.md`** (its slope row alone is replay-asserted from
`results/e3a_extension.json`). Those constants are traceable to that committed record and are
therefore classed **[DET]**, not fabricated — but they are transcriptions, so they must be
kept in sync with the ledger by hand.

## The two objects these figures separate (binding)

Never conflate them — this is the primary failure mode:

1. **Error-transport holonomy AMPLITUDE** = the object of **Thm 7.2 [PROVEN]**:
   `log Hol = tau^2 * sum_k alpha_k [C_j, C_j'] + O(tau^3)`. Measured slope **1.999**
   (Tier-1), resolved to coefficient precision only with observation noise off; the
   symmetric / level-set switch-offs are **machine-zero** (`xi = 0` is literally `0.0`).
2. **Closed-loop steady-state disagreement `D_ss` [CONJECTURAL]** — a *measured* slope
   **1.08–1.10** in a conjectural regime, carried with the R3 caveat, asserted as **NO
   law**; its CI excludes both 1 and 2. A `D_ss` fit is **never** a validation of Thm 7.2
   and its slope is **never** a first-order law.

Falsifier verdicts are reported as adjudicated, never dressed up: **C7b FALSIFIED**
(Tier-1 `D_ss` slope 1.101); **C9b** falsifier **MET** on the seed-paired estimator
(1.58 [1.44, 1.84], both 2 and 1 excluded — the single-power model is mis-specified for a
linear+quadratic mixture; the unpaired [0.43, 2.89] is under-powered and adjudicates
nothing); **C9c TRIPS** (2.75× < the registered 10× threshold); **C19 TRIPPED** (2.48) but
in the *favorable* direction (remainder vanishes faster than 2nd order) — restated with
corrected order, **not** a pass. A tripped/fired/falsified/MET row is never a positive
result. **C6 contraction PASSED** (slope 1.403, two topologies; `mu = -0.062`
topology-independent).

## Regenerating

From the repo root, with the Tier-1 environment active:

```
python tier1_sheaf/campaign/lcss_figs_ieee.py     # the 12 lcss_* families
python tier1_sheaf/campaign/tcns_figs_ieee.py      # the 20 tcns_* families
python tier1_sheaf/campaign/shared_figs_ieee.py    # theorem_map + t1_falsifier_forest
```

All three import `analysis/ieee_style.py` (`apply_ieee`, `COLW`, `save`, …) for the
single-column IEEE style (3.5 in width, serif 8 pt, vector PDF + raster PNG, grayscale-safe).
`lcss_figs_ieee.py` and `shared_figs_ieee.py` import
`tier1_sheaf.campaign.paper_artifacts`, which **replays the e3a extension draw sequence and
asserts it against the committed JSON** (20 slopes, 220 sups, 60-pair bank, `ext` record),
so slopes/sups/pairs cannot drift.

---

## Figure catalogue (provenance-focused)

Each entry groups the `.pdf` + `.png` of one figure. **CANONICAL** = copied into a
`papers/*/figures/` folder and `\includegraphics`-ed; **SUPERSEDED/dev-only** otherwise.

### Family A — L-CSS letter figures · generator `tier1_sheaf/campaign/lcss_figs_ieee.py`

| files | data record / mechanism | status | epistemic verdict |
|---|---|---|---|
| **`lcss_geometry`** | `floor_protocol_movie.runs[0.4]` shape trace (drawn diagram) | CANONICAL → `papers/lcss_letter/` | schematic — cooperative-tow geometry, each agent shape `s_j=(sigma_j, sigma_{i,j})`. No numeric claim. |
| **`lcss_shape_motion`** | `floor_protocol_movie.runs[0.4]`, cable angle `sigma_j(t)` (deg) vs `t` (s) | CANONICAL → `papers/lcss_letter/` | context — the shape fan never stops (persistent turn; nonzero commutator regime). No verdict. |
| **`lcss_loop_generic`** | `level_set_movie.GEN` pair; SE(2) loop `expm` walk (computed) | CANONICAL → `papers/lcss_letter/` | generic pair: BCH loop fails to close → a holonomy gap exists [PROVEN, Thm 7.2 object]. |
| **`lcss_loop_levelset`** | `level_set_movie.LVL` pair; same walk (computed) | CANONICAL → `papers/lcss_letter/` | C15 level-set pair: loop closes for every `tau` (gap `< 1e-15`), full holonomy vanishes at all orders. |
| **`lcss_amplitude`** | `results/e3a_amplitude.csv` (`generic`, `generic, eta=0` rows) over `tau ∈ [0.05,1.6]` s | CANONICAL → `papers/lcss_letter/` | **AMPLITUDE object [PROVEN]** — slope **1.999**, `tau^2` law; switch-offs at machine zero (`~1e-18`). C7a/C8/C13 PASSED. |
| **`lcss_carpet`** | `ext["C15"][0]` shapes + `holonomy_amplitude_m2` grid over `(Delta, tau)` (computed) | CANONICAL → `papers/lcss_letter/` | amplitude floor grows as `tau^2`, collapses in the level-set valley [PROVEN object]. |
| **`lcss_slope_hist`** | replay-asserted `paper_artifacts.slopes` (20 formations) | CANONICAL → `papers/lcss_letter/` | **formation-invariant** amplitude order: mean **1.9993**, support `~1e-14` (machine). E3a. |
| **`lcss_remainder_cdf`** | replay-asserted `paper_artifacts.sups` (220 draws) + `ext["remainder_constant"]` | CANONICAL → `papers/lcss_letter/` | uniform `O(tau^3)` remainder constant, `sup_tau ‖R‖/tau^3` — the quoted 0.0133 is the **supremum (worst case), NOT the median** (median 0.005, 95th pct 0.011); supports the leading-order law. |
| **`lcss_bound_ratio`** | `paper_artifacts.pair_bank[:60]`; `holonomy_amplitude_m2 / (tau^2 ‖[C_i,C_j]‖)` (computed) | CANONICAL → `papers/lcss_letter/` | coefficient ratio → 1 as `tau → 0` [PROVEN object, C8 coefficient]. |
| **`lcss_levelset_bars`** | `ext["C15"]` pairs; `‖[C_i,C_j]‖` and `‖C_i − C_j‖` (computed) | CANONICAL → **both** `papers/lcss_letter/` **and** `papers/tcns_section8/figures/` | **C15 discovery** — zero-commutator pairs all have `C_i = C_j` to `1e-16`; discrete level set, two zeros per reference torus. |
| **`lcss_heatmap`** | `ext["C15"][0]` ref/partner; `log10 ‖[C(s_ref), C(s)]‖` on a 201² `(sigma, sigma_i)` grid | CANONICAL → `papers/lcss_letter/` (also copied to `papers/tcns_section8/figures/`, not `\included` there) | C15 commutator landscape: **two discrete zeros** — the protected class is a level set, not a symmetry orbit. |
| **`lcss_domain`** | fixed `(s_i, s_j)`; `holonomy_amplitude_m2` vs `tau ∈ [0.05,12]` s, 10% knee (computed) | CANONICAL → `papers/lcss_letter/` | leading-order validity domain: 10% departure from the `tau^2` law only near `tau ≈ 10` s. |

**Theory & provenance — Family A** (labels from `papers/lcss_letter/main.tex`):

- **`lcss_geometry`**
  - *Theory:* setup for **Lemma 3.1 `lem:m` "Constraint trivialization"** — illustrates the
    decentralized load frame and the per-agent shapes `s_j=(sigma_j, sigma_{i,j})` on which
    the trivialization is defined; no numeric claim.
  - *Provenance:* **[DIAGRAM]** conceptual cooperative-tow geometry; the shape frame is a
    single snapshot lifted from the seeded `floor_protocol_movie` run, drawn as a schematic —
    no measured data.
- **`lcss_shape_motion`**
  - *Theory:* context for **Theorem 7.2 `thm:floor` [PROVEN]** — shows the persistent-turn
    (nonzero-commutator) regime in which the floor is active; not itself a test of the theorem.
  - *Provenance:* **[SIM]** shape trajectory `sigma_j(t)` from `floor_protocol_movie.runs[0.4]`
    (seeded `ReducedPlant`, `noise_on=True`, `SeedSequence([SEED,FORM,7])`); committed sibling
    record `results/e3b_production.json` (confirmed present).
- **`lcss_loop_generic`**
  - *Theory:* **Lemma 7.1 `lem:bch` "Group-commutator defect"** / **Theorem 7.2 `thm:floor`
    [PROVEN]** — the BCH loop failing to close IS the nonzero holonomy the floor bounds.
  - *Provenance:* **[DET]** SE(2) `expm` loop walk of `conjugated_generator` at the generic
    (`GEN`) pair, common twist `XI=(0.4,0,0.12)`, no randomness.
- **`lcss_loop_levelset`**
  - *Theory:* **Corollary 7.3 `cor:sym` "Symmetry protection"** (C15 level-set extension) —
    the loop closes for every `tau` (gap `< 1e-15`), so full holonomy vanishes at all orders.
  - *Provenance:* **[DET]** same SE(2) `expm` walk at the level-set (`LVL`) pair, `XI` fixed.
- **`lcss_amplitude`**
  - *Theory:* **Theorem 7.2 `thm:floor` [PROVEN]** — the measured slope **1.999** IS the
    theorem's order-2 (`tau^2`) amplitude claim; the `eta=0` / `xi=0` switch-off arms realize
    the null directions of **Lemma 7.1 `lem:bch`**.
  - *Provenance:* **[SIM]** committed record `results/e3a_amplitude.csv` (confirmed present);
    the switch-off rows are the deterministic operator at machine zero (`~1e-18`).
- **`lcss_carpet`**
  - *Theory:* **Theorem 7.2 `thm:floor` [PROVEN]** + **Corollary 7.3 `cor:sym`** — amplitude
    grows as `tau^2` and collapses in the level-set valley.
  - *Provenance:* **[DET]** `holonomy_amplitude_m2` on a `(Delta, tau)` grid, shapes from
    `ext["C15"][0]`, `XI` fixed.
- **`lcss_slope_hist`**
  - *Theory:* **Theorem 7.2 `thm:floor` [PROVEN]** — formation-invariance of the order-2
    exponent (mean **1.9993**, support `~1e-14`).
  - *Provenance:* **[SIM]** replay-asserted `paper_artifacts.slopes`, asserted (`atol 1e-12`)
    against `results/e3a_extension.json` `formation_cluster.slopes` (confirmed present; seeded
    20-formation draw, `rng=2026`).
- **`lcss_remainder_cdf`**
  - *Theory:* **Theorem 7.2 `thm:floor` [PROVEN]** — bounds the `O(tau^3)` remainder
    (sup constant **0.0133**, the worst case, not the median), supporting the leading-order law.
  - *Provenance:* **[SIM]** replay-asserted `paper_artifacts.sups` + `ext["remainder_constant"]`
    from committed `results/e3a_extension.json` (confirmed present).
- **`lcss_bound_ratio`**
  - *Theory:* **Lemma 7.1 `lem:bch`** / **Theorem 7.2 `thm:floor`** coefficient (falsifier C8)
    — the coefficient ratio → 1 as `tau → 0`.
  - *Provenance:* **[DET]** `holonomy_amplitude_m2 / (tau^2 * ‖two_agent_commutator‖)` over
    `paper_artifacts.pair_bank[:60]`, `XI` fixed.
- **`lcss_levelset_bars`**
  - *Theory:* **Corollary 7.3 `cor:sym`** (the C15 discovery) — zero-commutator pairs all have
    `C_i = C_j` to `1e-16`; a discrete level set, not a symmetry orbit.
  - *Provenance:* **[DET]** `conjugated_generator` → `‖[C_i,C_j]‖` and `‖C_i − C_j‖` on the
    `ext["C15"]` pairs (from committed `results/e3a_extension.json`), `XI` fixed.
- **`lcss_heatmap`**
  - *Theory:* **Corollary 7.3 `cor:sym`** — the commutator landscape has **two discrete zeros**,
    so the protected class is a level set rather than a symmetry orbit.
  - *Provenance:* **[DET]** `log10‖[C(s_ref),C(s)]‖` from `conjugated_generator` on a 201²
    `(sigma, sigma_i)` grid, reference from `ext["C15"][0]`, `XI` fixed.
- **`lcss_domain`**
  - *Theory:* **Theorem 7.2 `thm:floor` [PROVEN]** — the leading-order validity domain (10%
    departure from the `tau^2` law only near `tau ≈ 10` s).
  - *Provenance:* **[DET]** `holonomy_amplitude_m2` vs `tau` at fixed `(s_i, s_j)`, `XI` fixed.

### Family B — T-CNS Section VIII figures · generator `tier1_sheaf/campaign/tcns_figs_ieee.py`

| files | data record / mechanism | status | epistemic verdict |
|---|---|---|---|
| **`tcns_plant`** | drawn diagram (`N=5`, `C_5` comms) | CANONICAL → `papers/tcns_section8/figures/` | schematic — reduced Tier-1 plant. No numeric claim. |
| **`tcns_gauge_trails`** | `tier1_sheaf/experiments/anim_gauge.simulate()` (E1) | CANONICAL → `papers/tcns_section8/figures/` | gauge story: estimates drift as a group off truth, snap at the beacon (load pose observable only modulo one SE(2) gauge). |
| **`tcns_gauge_errors`** | `anim_gauge.simulate()` gauge error vs `D` (E1) | CANONICAL → `papers/tcns_section8/figures/` | `D` (agents-vs-each-other, `m^2`) runs an order of magnitude below the gauge error (vs truth). |
| **`tcns_e1_spectrum`** | `sheaf.laplacian.sheaf_laplacian` eigenvalues, unanchored + one-anchor (E1) | CANONICAL → `papers/tcns_section8/figures/` **and** `papers/ral_blind_harbor/figures/` | `dim ker L_F = 3` — the exact `se(2)` gauge (Thm 5.1) — collapsing to `lambda_min = 0.175` under one anchor (Cor 5.2). **Regenerated 2026-07-22; previously fabricated.** |
| **`tcns_amplitude`** | `results/e3a_amplitude.csv` (shared with L-CSS) | CANONICAL → `papers/tcns_section8/figures/` | **AMPLITUDE object [PROVEN]** — slope 1.999, coeff 1.0000, switch-offs machine-zero. |
| **`tcns_formations`** | `campaign/formation_sweep_movie.forms, slopes` (E3a) | CANONICAL → `papers/tcns_section8/figures/` | 20 formations overlaid; formation-invariant amplitude slope [PROVEN object]. |
| **`tcns_f4b`** | `results/e3b_production.json` (1584 runs), arms paper/straight/frozen | CANONICAL → `papers/tcns_section8/figures/` | **`D_ss` floor [CONJ]** — excess slope **1.101 [1.076,1.125]**; order 2 **FALSIFIED** at these scales (C7b). NOT Thm 7.2. |
| **`tcns_dss_cdf`** | `results/e3b_production.json`, per-run `D` at `tau=0.4` by arm | CANONICAL → `papers/tcns_section8/figures/` | per-run `D_ss` spread [CONJ regime]. Descriptive. |
| **`tcns_dss_box`** | `results/e3b_production.json`, paper-rule `D` across seeds/formations | CANONICAL → `papers/tcns_section8/figures/` | paper-rule `D_ss` spread vs `tau` [CONJ regime]. Descriptive. |
| **`tcns_ladder`** | `results/e3b_production.json`, median `D` per arm × `tau` | CANONICAL → `papers/tcns_section8/figures/` | switch-off ladder [CONJ] — **A1 sits below paper (ordering inversion)**; `D_ss` does not rank rules (honest disclosure). |
| **`tcns_floor_dyn`** | `floor_protocol_movie.runs` / `run_traced` (E3b) | CANONICAL → `papers/tcns_section8/figures/` | floor dynamics: `D(t) → D_ss` [CONJ regime], higher for larger `tau`. |
| **`tcns_robust`** | `results/e3c_robust.json` (jitter 20% + drops 10%) | CANONICAL → `papers/tcns_section8/figures/` | **C9c TRIPS** — robust suppression **2.75× [1.94,3.89] < registered 10×**. Not a pass. |
| **`tcns_f5_amp`** | `results/e3c_symmetry.json` (`C9bp_amplitude`) | CANONICAL → `papers/tcns_section8/figures/` | **F5 amplitude arm [PROVEN object]** — first-order in `epsilon` (slope 1.006), base commutator exactly zero. C9b′ PASSED. |
| **`tcns_f5_floor`** | `results/e3c_symmetry.json` + `results/e3c_c9b_seeds.json` (`_paired_estimator`) | CANONICAL → `papers/tcns_section8/figures/` | **F5 floor arm [CONJ]** — paired excess slope **1.58 [1.44,1.84]**; **falsifier MET** (2 and 1 excluded; mixture mis-spec). Not a pass. |
| **`tcns_contraction_xy`** | `campaign/contraction_movie.data` (E2), gauge-complement error | CANONICAL → `papers/tcns_section8/figures/` | contraction portrait — error spirals to consensus, both topologies. |
| **`tcns_contraction_decay`** | `campaign/contraction_movie.data` (E2), `‖e_perp‖(t)` | CANONICAL → `papers/tcns_section8/figures/` | **C6 PASSED** — decay grows with `kappa lambda_2` (slope 1.403). |
| **`tcns_dt`** | `results/e10_dt_sweep.json` fitted `D_ss` exponent vs `Delta t` | CANONICAL → `papers/tcns_section8/figures/` | **E10 PASSED** — numerics invariance over 10× `Delta t` (shared exponent band). |
| **`tcns_topology`** | `results/e6_topology.json` `D_ss` vs `lambda_2` | CANONICAL → `papers/tcns_section8/figures/` | **C10 (exploratory)** — connectivity suppresses the floor at moderate `tau` (~5×), benefit collapses at high `tau` (≤2×). |
| **`tcns_f8`** | `results/e2_contraction.json` rate vs `kappa lambda_2` | CANONICAL → `papers/tcns_section8/figures/` | **C6 PASSED** — contraction rate ∝ `kappa lambda_2` (slope 1.403); `mu=-0.062` topology-independent. |
| **`tcns_arch`** | drawn architecture diagram (double-width) | **SUPERSEDED / dev-only** — the paper draws the architecture with inline TikZ via `\input{fig_arch.tex}`; the raster `tcns_arch.pdf` in `papers/tcns_section8/figures/` is **not `\included`** | schematic — pipeline/plant. No numeric claim; not the published version. |

**Theory & provenance — Family B** (labels from `papers/tcns_section8/section8.tex`; the
`*F` statements are the flagship-suffixed forms defined in
`papers/ral_blind_harbor/main.tex` and referenced by Section VIII):

- **`tcns_plant`**
  - *Theory:* setup for **`thm:gaugeF` "Exact residual unobservability = one global gauge"** —
    the `N=5` reduced plant the gauge / floor statements act on; no numeric claim.
  - *Provenance:* **[DIAGRAM]** schematic `N=5`, `C_5` comms; conceptual, no measured data.
- **`tcns_gauge_trails`**
  - *Theory:* **`thm:gaugeF`** (pose observable only modulo one SE(2) gauge) + **`cor:pinF`
    "Pinning"** — estimates drift as a group off truth and snap at the beacon.
  - *Provenance:* **[SIM]** `tier1_sheaf/experiments/anim_gauge.simulate(seed=3)` (seeded
    `ReducedPlant` with per-agent bias + `rng.standard_normal` noise, E1); committed sibling
    record `results/e1_gauge.csv` (confirmed present).
- **`tcns_gauge_errors`**
  - *Theory:* **`thm:gaugeF`** — the inter-agent disagreement `D` runs an order of magnitude
    below the gauge error (vs truth), because the gauge direction is unobservable.
  - *Provenance:* **[SIM]** `anim_gauge.simulate(seed=3)` gauge error vs `D` (E1);
    `results/e1_gauge.csv` (confirmed present).
- **`tcns_e1_spectrum`**
  - *Theory:* **`thm:gaugeF`** — `dim ker L_F = 3`, the exact `se(2)` gauge (repo convention
    Thm 5.1 in the theory source).
  - *Provenance:* **[DET]** eigenvalues of `sheaf.laplacian.sheaf_laplacian` on the E1 sheaf
    (triangle config of `experiments/e1_gauge.py`), plus an anchored arm (`+1.0*I` on agent
    0's load block); deterministic, no record read, no noise.
    **⚠ Corrected 2026-07-22 — previously FABRICATED.** The generator's real
    `sheaf_laplacian` call failed on a wrong API signature and an inner `try/except`
    silently substituted a hand-typed array `[0, 0, 0, 2.1, 2.4, 3.0, 3.3, 4.1, 5.5]`. The
    fallback was removed and replaced with asserts (`dim ker == 3` unanchored, `== 0`
    anchored) that fail loudly; the PDF is now the genuine spectrum. Repo-wide sweep: this
    was the **only** silent-fallback site.
- **`tcns_amplitude`**
  - *Theory:* **`thm:floorF` "Latency–curvature floor" [PROVEN]** — slope 1.999, coeff 1.0000,
    switch-offs machine-zero: the `O(tau^2)` amplitude claim.
  - *Provenance:* **[SIM]** committed record `results/e3a_amplitude.csv` (confirmed present);
    switch-off arms are the deterministic operator at machine zero.
- **`tcns_formations`**
  - *Theory:* **`thm:floorF` [PROVEN]** — formation-invariant amplitude slope across 20
    formations.
  - *Provenance:* **[SIM]** `campaign/formation_sweep_movie.forms, slopes` (E3a), replay-asserted
    (`atol 1e-12`) against committed `results/e3a_extension.json` (confirmed present).
- **`tcns_f4b`**
  - *Theory:* **NOT a theorem** — the **[CONJECTURAL]** closed-loop `D_ss` floor; excess slope
    **1.101 [1.076,1.125]**, order-2 **FALSIFIED** (falsifier **C7b**). Explicitly a different
    object from `thm:floorF`.
  - *Provenance:* **[SIM]** committed record `results/e3b_production.json` (1584 runs, confirmed
    present), arms paper/straight/frozen.
- **`tcns_dss_cdf`**
  - *Theory:* **empirical `D_ss` [CONJ]** spread — descriptive, no theorem.
  - *Provenance:* **[SIM]** `results/e3b_production.json`, per-run `D` at `tau=0.4` by arm
    (confirmed present).
- **`tcns_dss_box`**
  - *Theory:* **empirical `D_ss` [CONJ]** spread vs `tau` — descriptive, no theorem.
  - *Provenance:* **[SIM]** `results/e3b_production.json`, paper-rule `D` across seeds/formations.
- **`tcns_ladder`**
  - *Theory:* **empirical switch-off ordering [CONJ]** — `D_ss` does **not** rank rules (A1
    below paper, an ordering inversion, disclosed honestly); no theorem.
  - *Provenance:* **[SIM]** `results/e3b_production.json`, median `D` per arm × `tau`.
- **`tcns_floor_dyn`**
  - *Theory:* **empirical `D_ss` dynamics [CONJ]** — `D(t) → D_ss`, higher for larger `tau`;
    not `thm:floorF`.
  - *Provenance:* **[SIM]** `floor_protocol_movie.runs`/`run_traced` (E3b, seeded); committed
    sibling `results/e3b_production.json` (confirmed present).
- **`tcns_robust`**
  - *Theory:* **falsifier C9c (robustness)** — suppression **2.75× [1.94,3.89] < registered
    10×**, TRIPS (not a pass); empirical, not a theorem.
  - *Provenance:* **[SIM]** committed record `results/e3c_robust.json` (jitter 20% + drops 10%,
    confirmed present).
- **`tcns_f5_amp`**
  - *Theory:* **`cor:symF` "Symmetry protection" [PROVEN object]** — amplitude first-order in
    `epsilon` (slope 1.006), base commutator exactly zero (falsifier **C9b′ PASSED**).
  - *Provenance:* **[SIM]** committed record `results/e3c_symmetry.json` (`C9bp_amplitude`,
    confirmed present).
- **`tcns_f5_floor`**
  - *Theory:* **NOT a theorem** — the **[CONJECTURAL]** `D_ss` symmetry arm; paired excess slope
    **1.58 [1.44,1.84]**, falsifier **C9b MET** (2 and 1 excluded; linear+quadratic mixture
    mis-specified — not a pass).
  - *Provenance:* **[SIM]** committed records `results/e3c_symmetry.json` +
    `results/e3c_c9b_seeds.json` (`_paired_estimator`, both confirmed present).
- **`tcns_contraction_xy`**
  - *Theory:* **`thm:contractF` "Frozen-linearization contraction"** — the gauge-complement
    error spirals to consensus, both topologies.
  - *Provenance:* **[SIM]** `campaign/contraction_movie.data` (E2, seeded
    `SeedSequence([SEED,17])`); committed sibling `results/e2_contraction.json` (confirmed
    present).
- **`tcns_contraction_decay`**
  - *Theory:* **`thm:contractF`** — the decay grows with `kappa lambda_2` (falsifier **C6
    PASSED**, slope 1.403).
  - *Provenance:* **[SIM]** `campaign/contraction_movie.data` (E2), `‖e_perp‖(t)`; committed
    sibling `results/e2_contraction.json` (confirmed present).
- **`tcns_dt`**
  - *Theory:* **empirical E10 numerics invariance** — shared exponent band over 10× `Delta t`
    (**PASSED**); shows the measured object is not a discretization artifact; no theorem.
  - *Provenance:* **[SIM]** committed record `results/e10_dt_sweep.json` (confirmed present).
- **`tcns_topology`**
  - *Theory:* **empirical C10 (exploratory)** — connectivity suppresses the floor at moderate
    `tau` (~5×), benefit collapses at high `tau` (≤2×); no theorem.
  - *Provenance:* **[SIM]** committed record `results/e6_topology.json` (`D_ss` vs `lambda_2`,
    confirmed present).
- **`tcns_f8`**
  - *Theory:* **`thm:contractF`** — contraction rate ∝ `kappa lambda_2` (falsifier **C6
    PASSED**, slope 1.403; `mu=-0.062` topology-independent).
  - *Provenance:* **[SIM]** committed record `results/e2_contraction.json` (rate vs
    `kappa lambda_2`, confirmed present).
- **`tcns_arch`**
  - *Theory:* architecture schematic (pipeline/plant); no theorem, no numeric claim; superseded
    by the paper's inline TikZ.
  - *Provenance:* **[DIAGRAM]** drawn architecture, no measured data.

### Family C — shared figures · generator `tier1_sheaf/campaign/shared_figs_ieee.py`

| files | data record / mechanism | status | epistemic verdict |
|---|---|---|---|
| **`t1_falsifier_forest`** | replay-asserted `paper_artifacts.slopes` + hard-coded ledger CIs (`docs/ral_package.md`) | CANONICAL → **both** `papers/lcss_letter/` **and** `papers/tcns_section8/figures/` | the Tier-1 falsifier ledger as adjudicated: C7a/C9b′/C6/E10 PASSED (green); C19 TRIPPED-faster, C7b FALSIFIED, C9b MET, C9c TRIPS (red/orange). Verdicts shown honestly. |
| **`theorem_map`** | drawn dependency graph + `paper_artifacts.slopes` | **SUPERSEDED / dev-only** — both papers draw the statement map with inline TikZ via `\input{fig_thmmap.tex}`; the raster `theorem_map.pdf` copied into both `papers/*/figures/` folders is **not `\included`** | statement-dependency map; green = [proven], dashed red = [conjectural] `D_ss` (a different object from the Thm 7.2 amplitude). Not the published version. |

**Theory & provenance — Family C:**

- **`t1_falsifier_forest`**
  - *Theory:* **no single theorem** — this is the Tier-1 falsifier *ledger* as adjudicated
    (C7a / C9b′ / C6 / E10 **PASSED**; C19 **TRIPPED-faster**, C7b **FALSIFIED**, C9b **MET**,
    C9c **TRIPS**). It is the summary that keeps the **[PROVEN]** amplitude (`thm:floor` /
    `thm:floorF`) and the **[CONJECTURAL]** `D_ss` verdicts side by side and honest.
  - *Provenance:* **[DET]** the C7a slope row is replay-asserted `paper_artifacts.slopes`
    (committed `results/e3a_extension.json`); the remaining confidence intervals are
    **hard-coded constants transcribed verbatim from the committed ledger `docs/ral_package.md`**
    — traceable to that record, **not fabricated**, but transcriptions that must be kept in
    sync with the ledger by hand.
- **`theorem_map`**
  - *Theory:* the statement-dependency map itself — green = [proven], dashed red =
    [conjectural] `D_ss` (a *different* object from the `thm:floor`/`thm:floorF` amplitude); an
    illustration, not a measurement.
  - *Provenance:* **[DIAGRAM]** drawn dependency graph (annotated with replay-asserted slopes),
    superseded by inline TikZ; no measured data is plotted.

---

## Cross-links

- Reader-facing captions/narrative: the `\caption{}` blocks in
  `papers/lcss_letter/main.tex` and `papers/tcns_section8/section8.tex`.
- Verdict provenance and full adjudication: `docs/ral_package.md` §1 ledger.
- Publication split: **L-CSS = latency–curvature floor letter (Tier-1)**, **T-CNS =
  flagship Section VIII (Tier-1 only, no Drake)**, RA-L = the Drake "Blind Harbor"
  companion (its figures live under `tier2_drake/`, not here).
