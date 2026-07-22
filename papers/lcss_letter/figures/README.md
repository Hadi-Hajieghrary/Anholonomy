# L-CSS floor letter — figure & artifact guide

This folder holds every figure PDF for the L-CSS letter **"A Latency–Curvature
Floor for Distributed Estimation under Constraint-Induced Sheaf Fusion"**
(`../main.tex`). The letter is the **latency–curvature FLOOR** unit of the
publication split (Tier-1 numerics only; no Drake/`tier2` figures live here).
Its figures must show one thing three ways: the error-transport **holonomy
amplitude** exists, scales at **order 2** in the staleness `τ` [PROVEN, Thm 7.2],
and switches off **exactly** on the symmetric / C15 level-set class. The family
splits into 13 figures the submitted paper `\includegraphics`-es and 13
superseded / alternate variants kept for provenance. All were produced by
committed Python generators that replay the campaign draw sequence
**seed-exact and assert it against the committed record** before plotting, so no
figure can silently drift from the data.

---

## Data provenance & authenticity

Every figure entry below carries a `*Provenance:*` line assigning exactly one
authenticity class. The purpose of this section is to prove that **nothing in
this folder is fabricated**. Class counts over the 26 figure entries:

- **[SIM] — 11.** Seeded-simulation records: a generator ran the actual Tier-1
  `ReducedPlant` (or drew shapes) under a *seeded* rng and wrote a committed
  record; the figure reads that record. A seeded `np.random.default_rng(...)` /
  `SeedSequence` is reproducible simulation noise = real simulated data, not
  fabrication. Records used: `tier1_sheaf/results/e3a_extension.json` (driver
  `e3a_extension.py`, seed 2026 — 20 formation slopes, 220 remainder draws,
  60-pair coefficient bank, C15 records) and the seeded `ReducedPlant` run
  `floor_protocol_movie.run_traced(0.4)` (committed video
  `tier1_sheaf/results/floor_protocol.mp4`). All confirmed present on disk.
- **[DET] — 13.** Deterministic recomputation: the figure computes an exact,
  rng-free analytic quantity from released operators —
  `sheaf/holonomy.{holonomy_amplitude_m2, two_agent_commutator}` and
  `core/shapes.conjugated_generator` — at the fixed common load twist
  `ξ=(0.4,0,0.12) ∈ 𝔰𝔢(2)`, or reads the rng-free analytic record
  `tier1_sheaf/results/e3a_amplitude.csv`. Real computation, not fabrication.
- **[DIAGRAM] — 2.** Conceptual schematics with NO measured data
  (`lcss_schematic.pdf`, `theorem_map.pdf`) — labelled as such; honest
  illustrations, never presented as measurements.
- **[FLAG] — 0.** No fabricated or untraceable figure was found.

**Finding (asserted, and true):** every *data* figure in this folder traces to
either a committed seeded-simulation record (`e3a_extension.json`, the seeded
`floor_protocol_movie` run) or a deterministic operator recomputation at the
fixed load twist `ξ=(0.4,0,0.12)`; the two diagrams are labelled as diagrams;
and the one transcription case — `t1_falsifier_forest.pdf`, whose per-row
estimates/CIs are copied from the adjudicated ledger `docs/ral_package.md` — is
**fully traceable** to committed seeded records (`e3b_production.json`,
`e3c_c9b_seeds.json`, `e3c_robust.json`, `e2_contraction.json`,
`e10_dt_sweep.json`, with the C7a row live from `e3a_extension.json`), all
confirmed present. **Nothing is fabricated; no [FLAG] figure exists.** The
falsifier forest is classed [SIM] on the strength of that traceability, with the
transcription noted explicitly in its entry.

---

## How these were generated

**Generators (all committed, re-runnable):**

- `tier1_sheaf/campaign/lcss_figs_ieee.py` — the 12 single-axes IEEE figures the
  paper uses for everything except the falsifier forest (geometry, shape motion,
  the two loop trails, amplitude, carpet, slope histogram, remainder CDF, bound
  ratio, level-set bars, heatmap, domain).
- `tier1_sheaf/campaign/shared_figs_ieee.py` — `t1_falsifier_forest` (used) and
  a `theorem_map` variant (unused; the paper draws its map from TikZ instead).
- `tier1_sheaf/campaign/paper_artifacts.py` — the earlier wide multi-content
  variants (`lcss_schematic`, `lcss_commutator_heatmap`, `lcss_remainder_stats`,
  `lcss_bound_tightness`, `lcss_domain_boundary`, a `theorem_map`, a
  `t1_falsifier_forest`). Also the module that **replays** the 20-formation and
  220-draw sequences and `assert`s them against `e3a_extension.json` at import
  time (imported by `lcss_figs_ieee.py`); exposes `slopes`, `sups`, `pair_bank`,
  `ext`.
- `tier1_sheaf/campaign/lcss_scenario_figs.py` — the 5 wide qualitative scenario
  figures (`lcss_loop_filmstrip`, `lcss_transit_scene`, `lcss_amplitude_carpet`,
  `lcss_commutator_landscape`, `lcss_graphical_abstract`); none is in the paper.
- `tier1_sheaf/campaign/e3a_extension_panels.py` — the combined extension
  multi-panel (`e3a_extension_panels`); unused.
- `tier1_sheaf/experiments/e3a_amplitude.py` — the raw amplitude experiment,
  writes `e3a_amplitude.csv` and a diagnostic `e3a_amplitude.png` (unused).

**Data records they read** (all under `tier1_sheaf/results/`, committed):

- `e3a_amplitude.csv` — measured `‖log Hol‖` over `τ ∈ {0.05,0.1,0.2,0.4,0.8,1.6}` s
  for the generic pair and the switch-off arms (`η=0`, etc.). Feeds `lcss_amplitude`.
- `e3a_extension.json` — the pre-registered extension arms: 20 per-formation
  slopes, 220 per-draw remainder constants, the 60-pair coefficient bank, and the
  C15 zero-commutator pair records (`shapes`, `sep`, `comm`). Feeds the slope
  histogram, remainder CDF, bound ratio, level-set bars, carpet, heatmap.
- `floor_protocol_movie.runs[0.4]` — a recorded reduced-plant cooperative-tow
  run (seed 0), providing the real cable-angle traces `σ_j(t)`. Feeds
  `lcss_geometry` and `lcss_shape_motion`.

Everything else (carpet field, heatmap surface, bound ratio, domain boundary) is
recomputed deterministically from the released operators
`tier1_sheaf/core/shapes.conjugated_generator` and
`tier1_sheaf/sheaf/holonomy.{two_agent_commutator, holonomy_amplitude_m2}` at the
fixed common load twist `ξ = (0.4, 0, 0.12) ∈ 𝔰𝔢(2)`.

**Shared style:** `analysis/ieee_style.py` — STIXGeneral serif 8 pt, STIX math,
IEEE single-column 3.5 in (double 7.16 in), vector PDF with Type-42 embedded
fonts at 400 dpi, colour never the sole cue (Okabe-Ito colour+linestyle+marker
triples, grayscale-safe). Every `.pdf` here is **vector with a committed
generator** — re-buildable and editable, not a flattened raster. (The wide
scenario/artifact variants predate the IEEE-style pass and use a lighter local
rcParams override.)

---

## Figure catalogue

### `lcss_geometry.pdf`
- **`lcss_geometry.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 1**
  (`fig:scene`) — cooperative-tow geometry in the load frame: five vessels on
  cables, each viewing the load through its own shape `s_j=(σ_j,σ_{i,j})`, so the
  conjugated generators `C_j` differ and `[C_i,C_j]≠0` — the source of the floor.
- *Depicts:* a single load-frame diagram (world axes `x_L,y_L`, dimensionless
  load-frame units; cable length `l=1` in Tier-1). The load `G∈SE(2)` is a box at
  the origin; five brown cables fan out to coloured vessel markers oriented by
  `σ_j−σ_{i,j}`; the load-frame cable angle `σ_j` is arced in red.
- *Why / how:* one representative instant (`k≈0.45·len`) of the recorded seed-0
  reduced-plant run (`floor_protocol_movie.runs[0.4]`); the fan is asymmetric
  because each agent's shape genuinely differs.
- *Significance:* fixes the geometry whose distinct shapes make `[C_i,C_j]≠0`,
  the standing hypothesis of Thm 7.2 [PROVEN]. Conceptual, not a measurement.
- *Theory:* Lemma 3.1 (`lem:m`, "Constraint trivialization") [PROVEN] — this is
  the `m(s)` geometry the trivialization needs, and it fixes the distinct-shape
  hypothesis `[C_i,C_j]≠0` that Theorem 7.2 (`thm:floor`) stands on; it grounds
  the hypotheses, it is not itself the amplitude measurement.
- *Provenance:* [SIM] — one instant of the seeded `ReducedPlant` run
  `floor_protocol_movie.run_traced(0.4)` (seeded `SeedSequence`/`default_rng`;
  positions are real simulated plant state, not drawn by hand); committed video
  `tier1_sheaf/results/floor_protocol.mp4` confirmed present.

### `lcss_shape_motion.pdf`
- **`lcss_shape_motion.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 2**
  (`fig:shape`) — the real cable-angle trajectories `σ_j(t)` from the
  reduced-plant run: the shape fan never stops moving under the persistent turn,
  so the lagged transports carry a nonzero twist and the floor is active.
- *Depicts:* x = `t` (s), y = cable angle `σ_j(t)` (deg); five series, one per
  agent, from the recorded run.
- *Why / how:* the persistent turn (`ξ≠0, η≠0`) keeps all five `σ_j(t)` sweeping;
  a straight tow would freeze them and kill the floor.
- *Significance:* demonstrates the theorem's standing hypothesis `ξ≠0, η≠0` holds
  on a real recorded plant. Conceptual grounding for [PROVEN] Thm 7.2.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] standing hypothesis `ξ≠0, η≠0` —
  the moving shape fan is direct evidence the persistent-turn premise of the
  floor theorem holds on a real plant; grounding, not the amplitude fit.
- *Provenance:* [SIM] — the same seeded `ReducedPlant` run
  `floor_protocol_movie.run_traced(0.4)` (`runs[0.4]` cable-angle traces `σ_j(t)`,
  seed 0); committed video `tier1_sheaf/results/floor_protocol.mp4` confirmed
  present.

### `lcss_loop_generic.pdf`
- **`lcss_loop_generic.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 4**
  (`fig:filmstrip`) — generic pair: the transported belief's trail is a closed
  walk that does not close; the red arrow is the holonomy gap for the largest τ,
  loops nested over `τ∈{0.4,0.8,1.2,1.6}`.
- *Depicts:* x,y = belief-frame position (dimensionless SE(2) translation); four
  nested trails of the frame origin carried along
  `e^{τC_i}e^{τC_j}e^{−τC_i}e^{−τC_j}`, plus a red holonomy-gap arrow from start
  to the open endpoint.
- *Why / how:* generic shape pair `GEN`; the leading `τ²[C_i,C_j]` term is nonzero
  so the loop opens, and the gap grows quadratically with `τ`.
- *Significance:* makes the mechanism visible — the failure-to-close **is** the
  disagreement a stale round trip injects. Supports [PROVEN] Thm 7.2.
- *Theory:* Lemma 7.1 (`lem:bch`, "Group-commutator defect") + Theorem 7.2
  (`thm:floor`) [PROVEN] — the visible failure-to-close IS the leading
  `τ²[C_i,C_j]` defect the lemma/theorem assert; the growing gap is the `τ²`
  amplitude, drawn.
- *Provenance:* [DET] — deterministic loop
  `e^{τC_i}e^{τC_j}e^{−τC_i}e^{−τC_j}` from `conjugated_generator` on the fixed
  generic pair `GEN` at `ξ=(0.4,0,0.12)`; no rng, no record.

### `lcss_loop_levelset.pdf`
- **`lcss_loop_levelset.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 5**
  (`fig:looplvl`) — level-set pair (`C_i=C_j`): the walk goes out along the common
  generator and retraces exactly, returning to the start (gap `<10⁻¹⁵`) at every
  τ — exact protection at all orders.
- *Depicts:* same belief-frame axes as Fig. 4; four `τ` trails that collapse onto
  a retraced out-and-back segment closing at the start.
- *Why / how:* the C15 level-set pair `LVL` has `C_i=C_j`, so the four legs cancel
  identically for **every** `τ`, not just to `O(τ³)`.
- *Significance:* the visual switch-off — the NEW C15 protected class, where the
  full holonomy vanishes at all orders. C15 discovery [PROVEN switch-off,
  protected-class extension is an OBSERVATION; proof left to companion].
- *Theory:* Corollary 7.3 (`cor:sym`, "Symmetry protection") [PROVEN] switch-off
  + its C15 level-set extension [OBSERVED] — the exact retrace at every `τ` is the
  `[C_i,C_j]=0` null; the extension from coincident to conjugation-equivalent
  shapes is a numerical observation, proof deferred to the companion.
- *Provenance:* [DET] — same deterministic loop operators
  (`conjugated_generator`, matrix exp) on the fixed level-set pair `LVL`
  (`C_i=C_j`) at `ξ=(0.4,0,0.12)`; no rng, no record.

### `lcss_amplitude.pdf`
- **`lcss_amplitude.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 13**
  (`fig:e3a`) — measured `‖log Hol‖` vs τ (analytic shapes): generic pair fitted
  slope 1.999 over `τ∈[0.05,1.6]` s, coefficient ratio 1.0000 at the smallest τ;
  switch-off arms (`s_i=s_j`; `η=0`; `ξ=0`) at machine zero (`ξ=0` literally 0.0).
- *Depicts:* log–log; x = staleness `τ` (s), y = `‖log Hol‖` (dimensionless); the
  measured curve, the dotted `τ²` reference, and the machine-zero switch-off
  series pinned at the `1e-18` floor.
- *Why / how:* reads `e3a_amplitude.csv` (the `generic` and `generic, eta=0` rows)
  produced by `e3a_amplitude.py`; the effect is analytic in `τ` once generators
  are fixed, so the measured content is the coefficient and the switch-offs.
- *Significance:* the headline verification of the amplitude law and its exact
  nulls. [PROVEN, Thm 7.2] — order 1.999, coefficient 1.0000, switch-offs
  machine-zero (`ξ=0` = 0.0). This is the holonomy amplitude, NOT the closed-loop
  `D_ss`.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] — the measured slope 1.999 and
  coefficient ratio 1.0000 ARE the theorem's order-2 amplitude claim; the
  switch-off arms are the exact nulls of Corollary 7.3 (`s_i=s_j`) and of the
  `ξ=0` / `η=0` hypotheses. This is the amplitude object, explicitly NOT the
  [CONJECTURAL] closed-loop `D_ss`.
- *Provenance:* [DET] — reads `tier1_sheaf/results/e3a_amplitude.csv`
  (confirmed present): rng-free analytic `‖log Hol‖` over the 6 fixed `τ` from
  `holonomy_amplitude_m2`, with `ξ=0` row literally `0.0` and `η=0` row `<10⁻¹⁶`.

### `lcss_carpet.pdf`
- **`lcss_carpet.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 6**
  (`fig:carpet`) — the floor as a field: `log₁₀‖log Hol‖` over staleness τ
  (vertical, log) and shape separation `Δ` (horizontal), growing as `τ²` and
  collapsing in a narrow valley at the level-set separation (dashed).
- *Depicts:* a `magma` pcolormesh; x = shape separation `Δ` (rad, along a ray
  through the level-set partner), y = `τ` (s, log), colour = `log₁₀‖log Hol‖`;
  cyan dashed line marks the level-set valley.
- *Why / how:* fixes `s_i` at the first C15 pair's shape and sweeps `s_j` along the
  ray to the partner; amplitude recomputed by `holonomy_amplitude_m2` on an 80×110
  grid. Deepens as `τ²` vertically; the valley sits at the partner separation.
- *Significance:* growth law and protected class in one view. [PROVEN] growth
  order + [OBSERVED] discrete level set.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] `τ²` growth (vertical axis) +
  Corollary 7.3 / C15 level-set valley [OBSERVED] (horizontal collapse at the
  level-set separation) — the theorem's growth order and the observed protected
  class in one field.
- *Provenance:* [DET] — `holonomy_amplitude_m2` recomputed on an 80×110 `(τ,Δ)`
  grid at `ξ=(0.4,0,0.12)`, `s_i` anchored to the first C15 shape of
  `e3a_extension.json`; no rng.

### `lcss_slope_hist.pdf`
- **`lcss_slope_hist.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 8**
  (`fig:slopehist`) — formation invariance (arm i): the 20 per-formation fitted
  slopes, in deviation units, span only `5.7×10⁻¹⁴` around 1.9993 — the `τ²` order
  is a structural constant.
- *Depicts:* histogram; x = fitted slope − 1.9992678569271 (×`10⁻¹⁴`), y = count
  of 20 formations.
- *Why / how:* `slopes` from the replay-asserted `e3a_extension.json` (20 shape
  pairs drawn uniformly from the taut-admissible box, broadside margin 0.10); the
  order is a structural constant, so formations move only the coefficient.
- *Significance:* the `τ²` order is formation-invariant to `10⁻¹⁴`. [PROVEN, arm i]
  — slope `1.9993 ± 0.0000`.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] order-2 claim, arm i — the order
  survives as a structural constant across formations (`1.9993 ± 0.0000` to
  `10⁻¹⁴`), so geometry moves only the coefficient, never the exponent.
- *Provenance:* [SIM] — `tier1_sheaf/results/e3a_extension.json`
  `formation_cluster.slopes` (20 shape pairs drawn under seeded rng, driver
  `e3a_extension.py` seed 2026; sd `1.2×10⁻¹⁴`); confirmed present.

### `lcss_remainder_cdf.pdf`
- **`lcss_remainder_cdf.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 9**
  (`fig:remstats`) — uniform remainder (arm ii): empirical CDF of the per-draw
  remainder constant `sup_τ‖R‖/τ³` over 220 shape draws; the quoted 0.0133 is the
  supremum, not a typical value.
- *Depicts:* step CDF; x = `sup_τ‖R‖/τ³` per draw, y = empirical CDF over 220
  draws; dotted verticals at median (0.005), p95 (0.011), sup (0.0133).
- *Why / how:* `sups` array and `ext["remainder_constant"]` from the asserted
  extension record; quantifies the `O(τ³)` constant the theorem leaves implicit.
- *Significance:* the leading-order truncation is uniformly tight on the
  admissible shape region. [PROVEN, arm ii] — worst-case constant ≤ 0.0133.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] `O(τ³)` remainder, arm ii — it
  measures the constant the theorem leaves implicit, showing the leading-order
  truncation is uniformly tight (worst case `≤ 0.0133`) over the admissible region.
- *Provenance:* [SIM] — `tier1_sheaf/results/e3a_extension.json`
  `remainder_constant` and the 220-draw `sups` array (seeded shape draws, driver
  `e3a_extension.py` seed 2026); confirmed present.

### `lcss_bound_ratio.pdf`
- **`lcss_bound_ratio.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 10**
  (`fig:bound`) — bound tightness: the measured/predicted ratio
  `‖log Hol‖/τ²‖[C_i,C_j]‖` rises to 1 as τ→0, the 5–95% band across 60 draws
  narrower than `2×10⁻⁴`.
- *Depicts:* x = `τ` (s, log, first four grid points), y = measured/`τ²‖[C_i,C_j]‖`;
  median line to 1.0 with a shaded 5–95% band; dashed `y=1` guide.
- *Why / how:* over the 60-pair `pair_bank`, the ratio at each small `τ` is the
  measured amplitude divided by the leading-order prediction; the band collapses
  because the `O(τ³)` remainder shrinks.
- *Significance:* tests the theorem's **constant**, not the fit — the constant is
  the data to the width of the remainder. [PROVEN, Thm 7.2 coefficient = 1.0000].
- *Theory:* Theorem 7.2 (`thm:floor`) + Lemma 7.1 (`lem:bch`) [PROVEN] — it tests
  the leading-order *coefficient* `τ²‖[C_i,C_j]‖` (ratio → 1.0000 as `τ→0`), i.e.
  the theorem's constant rather than its exponent.
- *Provenance:* [SIM] — the 60-pair coefficient bank `pair_bank` from
  `tier1_sheaf/results/e3a_extension.json` (seeded draws, driver
  `e3a_extension.py` seed 2026); confirmed present.

### `lcss_levelset_bars.pdf`
- **`lcss_levelset_bars.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 12**
  (`fig:ext`) — level-set protection (arm iv): the five zero-commutator pairs found
  at `≥1` rad separation all satisfy `C_i=C_j` to `10⁻¹⁶` (both bars below machine
  precision) — the protected class is a level set, not just coincident shapes.
- *Depicts:* grouped log bars; x = pair shape separation (rad, all ≥1), y = norm;
  paired bars `‖[C_i,C_j]‖` and `‖C_i−C_j‖`, both under the `1e-15` machine-precision
  line.
- *Why / how:* the five C15 records from `ext["C15"]`; a numerical search for
  zero-commutator pairs ≥1 rad apart found five, and at every one the generators
  themselves coincide (`~10⁻¹⁶`), so the FULL holonomy vanishes at all orders.
- *Significance:* the NEW protected-class result — protection is a discrete level
  set `{s : C(s;ξ)=const}`, exact at all orders. [OBSERVED numerically; commutant
  argument suggested, proof deferred to companion].
- *Theory:* Corollary 7.3 (`cor:sym`) extension / C15 level-set [OBSERVED] — the
  protected class of the symmetry corollary extends from coincident shapes to a
  discrete level set `{s : C(s;ξ)=const}`; stated as a numerical observation,
  proof deferred.
- *Provenance:* [SIM] — the five C15 records `ext["C15"]` from the seeded
  zero-commutator search in `tier1_sheaf/results/e3a_extension.json`
  (`C15_pairs_found`, driver `e3a_extension.py` seed 2026); confirmed present.

### `lcss_heatmap.pdf`
- **`lcss_heatmap.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 7**
  (`fig:heatmap`) — the protected class globally: `log₁₀‖[C(s_ref),C(s)]‖` over the
  shape torus, exactly two zeros — the reference and one isolated level partner
  1.057 rad away with `C=C_ref`.
- *Depicts:* `viridis` pcolormesh over the shape torus `[−π,π]²`; x = `σ`, y = `σ_i`;
  white star at `s_ref`, open circle at the level partner.
- *Why / how:* fixes the reference at the first C15 pair's first shape and maps the
  commutator norm on a 201×201 grid; a basin-polished exhaustive scan finds exactly
  two zeros, nowhere else does the commutator vanish without the generators
  coinciding — the level set is **discrete** at this `ξ`.
- *Significance:* sharpens the protected class to all-or-nothing in shape space.
  [OBSERVED] — discrete level set, exact protection only at the two zeros.
- *Theory:* Corollary 7.3 (`cor:sym`) / C15 [OBSERVED] — the global picture of the
  protected class: exactly two torus zeros (reference + one isolated partner
  1.057 rad away with `C=C_ref`), so the level set is discrete and protection is
  all-or-nothing in shape space.
- *Provenance:* [DET] — `two_agent_commutator` recomputed on a 201×201 shape-torus
  grid at `ξ=(0.4,0,0.12)`, reference anchored to the first C15 shape of
  `e3a_extension.json`; no rng.

### `lcss_domain.pdf`
- **`lcss_domain.pdf`** — vector PDF; USED IN the L-CSS letter as **Fig. 11**
  (`fig:domain`) — outside the leading-order domain: the measured amplitude departs
  from the `τ²` law by 10% only at `τ≈10` — an order of magnitude beyond the
  operating grid (`τ≤1.6`), where the relative departure stays below `3.4×10⁻³`.
- *Depicts:* log–log; x = `τ` (s) extended to 12, y = `‖log Hol‖`; measured curve,
  dashed `τ²` law, red dotted knee at the 10%-departure `τ`.
- *Why / how:* one fixed shape pair, `holonomy_amplitude_m2` over
  `τ∈geomspace(0.05,12)`; the relative departure crosses 10% only near `τ≈10`.
- *Significance:* the measured boundary of the small-`τ` statement — the domain is
  far larger than the operating regime needs. [PROVEN small-`τ` statement; the
  `τ≈10` 10%-departure boundary is MEASURED, not proven].
- *Theory:* Theorem 7.2 (`thm:floor`) is a small-`τ` statement [PROVEN]; this
  figure MEASURES (not proves) the boundary of that domain — the `τ²` law holds to
  `<3.4×10⁻³` inside the operating grid and departs by 10% only near `τ≈10`.
- *Provenance:* [DET] — `holonomy_amplitude_m2` recomputed over
  `τ∈geomspace(0.05,12)` for one fixed shape pair at `ξ=(0.4,0,0.12)`; no rng.

### `t1_falsifier_forest.pdf`
- **`t1_falsifier_forest.pdf`** — vector PDF (double-column); USED IN the L-CSS
  letter as **Fig. 14** (`fig:forest`) — the complete Tier-1 falsifier ledger,
  verdicts as registered: green passed, red falsified/met, orange tripped-favorably.
- *Depicts:* a forest plot; x = estimate (95% CI where declared, log axis), one row
  per pre-registered falsifier with registered reference/threshold in grey and a
  verdict label per row.
- *Why / how:* hard-coded from the adjudicated ledger (`docs/ral_package.md`). Rows,
  with the ledger verdicts stated **honestly, none dressed up**:
  - C7a amplitude slope — **PASSED** (mean ≈1.9993, ref line 2.0)
  - C9b′ amplitude ε-exponent — **PASSED** (1.006)
  - C6 contraction slope — **PASSED** (1.403, threshold 0.5; μ=−0.062 topology-independent)
  - E10 Δt-invariance — **PASSED** (CI [1.185, 1.256])
  - C19 remainder order — **TRIPPED favorably** (2.48 [2.32,2.65], band [1.8,2.2];
    remainder vanishes FASTER than 2nd order — orange, NOT a pass)
  - C7b `D_ss` p [CONJ] — **FALSIFIED at these scales** (1.101 [1.076,1.125] vs
    conjectured order 2; CI also excludes 1 — a measured slope, no law asserted)
  - C9b ε-exponent [CONJ] — **falsifier condition MET** on the seed-paired
    estimator (1.58 [1.44,1.84]; both 2 and 1 excluded — single-power model
    mis-specified for a linear+quadratic mixture)
  - C9c robust suppression — **TRIPS** (2.75× [1.94,3.89] < the ≥10× threshold —
    protection is an amplitude-object property, degraded outside the uniform-delay
    protocol class)
- *Significance:* the letter's statistical-integrity statement — the top block is
  the [PROVEN] amplitude chain (all green); the bottom block is the [CONJECTURAL]
  closed-loop `D_ss` regime whose order-2 conjecture is falsified at these scales.
  A tripped/met/falsified row is never presented as a positive result.
- *Theory:* empirical statistical-integrity ledger, NOT a single theorem —
  the top block is the [PROVEN] amplitude chain (falsifiers C7a/C9b′/C6/E10, all
  green against Theorem 7.2 / Corollary 7.3 / the contraction result); the bottom
  block is the [CONJECTURAL] closed-loop `D_ss` regime (C7b FALSIFIED, C9b MET,
  C9c TRIPS 2.75×<10×), a DIFFERENT object that is never a validation of
  `thm:floor`. Verdicts per `docs/ral_package.md`.
- *Provenance:* [SIM] (transcribed, fully traceable — NOT a flag) — per-row
  estimates/CIs copied from the adjudicated ledger `docs/ral_package.md`, each
  sourced to a committed seeded record (`e3b_production.json`,
  `e3c_c9b_seeds.json`, `e3c_robust.json`, `e2_contraction.json`,
  `e10_dt_sweep.json`), with the C7a row live from `e3a_extension.json` `slopes`;
  all records confirmed present. Hardcoded values, but every one traces to a
  committed simulation record — nothing invented.

---

### `e3a_amplitude.png`
- **`e3a_amplitude.png`** — raster PNG (150 dpi); NOT used in the submitted paper —
  the raw diagnostic plot of the `e3a_amplitude.py` experiment, superseded by the
  IEEE-styled `lcss_amplitude.pdf`. Kept as the experiment's own output next to
  `e3a_amplitude.csv`.
- *Depicts:* the same amplitude-vs-τ content as Fig. 13 in the experiment's local
  (non-IEEE) style.
- *Significance:* provenance for `lcss_amplitude.pdf`; same [PROVEN] object, not
  submission-quality.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] — the same amplitude object as
  Fig. 13 (order + coefficient + switch-offs), in diagnostic style.
- *Provenance:* [DET] — the same rng-free analytic record
  `tier1_sheaf/results/e3a_amplitude.csv` (confirmed present) written by
  `e3a_amplitude.py`.

### `e3a_extension_panels.pdf`
- **`e3a_extension_panels.pdf`** — vector PDF; NOT used in the submitted paper —
  the combined extension multi-panel (from `e3a_extension_panels.py`), superseded
  by the individual IEEE figures (`lcss_slope_hist`, `lcss_remainder_cdf`,
  `lcss_levelset_bars`, `lcss_carpet`). Kept as a one-glance summary of the four
  extension arms.
- *Significance:* same extension-arm data (formation invariance, remainder, C15)
  as the split figures; [PROVEN arms i–ii] + [OBSERVED arm iv].
- *Theory:* Theorem 7.2 (`thm:floor`) arms i–ii [PROVEN] (formation-invariant
  order, uniform remainder) + Corollary 7.3 / C15 level set [OBSERVED] — the same
  statements as the split IEEE figures, combined.
- *Provenance:* [SIM] — `tier1_sheaf/results/e3a_extension.json` (the same seeded
  seed-2026 extension record — slopes, remainder, C15); confirmed present.

### `lcss_amplitude_carpet.pdf`
- **`lcss_amplitude_carpet.pdf`** — vector PDF; NOT used in the submitted paper —
  wide scenario variant (`lcss_scenario_figs.py` L3) of the used `lcss_carpet.pdf`.
  Kept as the fuller-annotation version of the amplitude field.
- *Significance:* same `τ²` growth + level-set valley as Fig. 6; [PROVEN] growth +
  [OBSERVED] level set.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] `τ²` growth + Corollary 7.3 / C15
  level-set valley [OBSERVED] — same statements as the used carpet (Fig. 6).
- *Provenance:* [DET] — `holonomy_amplitude_m2` recomputed on a `(τ,Δ)` grid at
  `ξ=(0.4,0,0.12)` (scenario-style annotation of the same deterministic field);
  no rng.

### `lcss_bound_tightness.pdf`
- **`lcss_bound_tightness.pdf`** — vector PDF; NOT used in the submitted paper —
  earlier `paper_artifacts.py` variant of the used `lcss_bound_ratio.pdf`.
- *Significance:* same measured/predicted ratio → 1 result; [PROVEN] coefficient
  1.0000.
- *Theory:* Theorem 7.2 (`thm:floor`) + Lemma 7.1 (`lem:bch`) [PROVEN] — the same
  leading-order coefficient test (ratio → 1.0000) as the used `lcss_bound_ratio`.
- *Provenance:* [SIM] — the 60-pair `pair_bank` of
  `tier1_sheaf/results/e3a_extension.json` (seeded, seed 2026); confirmed present.

### `lcss_commutator_heatmap.pdf`
- **`lcss_commutator_heatmap.pdf`** — vector PDF; NOT used in the submitted paper —
  earlier `paper_artifacts.py` variant of the used `lcss_heatmap.pdf` (the torus
  commutator map). Writes `commutator_heatmap_meta.json` alongside.
- *Significance:* same discrete-level-set structure as Fig. 7; [OBSERVED].
- *Theory:* Corollary 7.3 (`cor:sym`) / C15 [OBSERVED] — same discrete level-set
  structure on the shape torus as the used heatmap (Fig. 7).
- *Provenance:* [DET] — `two_agent_commutator` recomputed over the shape torus at
  `ξ=(0.4,0,0.12)` (writes `commutator_heatmap_meta.json`); no rng.

### `lcss_commutator_landscape.pdf`
- **`lcss_commutator_landscape.pdf`** — vector PDF (largest file, ~200 kB); NOT
  used in the submitted paper — a 3D surface variant (`lcss_scenario_figs.py` L4)
  of the heatmap: `log₁₀‖[C_ref,C]‖` as a surface over the shape torus with red
  stems at the two exact zeros.
- *Significance:* alternate depiction of the same discrete protected class as
  Fig. 7; [OBSERVED] — the surface is nowhere flat but at two points.
- *Theory:* Corollary 7.3 (`cor:sym`) / C15 [OBSERVED] — same discrete protected
  class as Fig. 7, as a 3D surface with the two exact zeros marked.
- *Provenance:* [DET] — `two_agent_commutator` recomputed as a surface over the
  shape torus at `ξ=(0.4,0,0.12)`; no rng.

### `lcss_domain_boundary.pdf`
- **`lcss_domain_boundary.pdf`** — vector PDF; NOT used in the submitted paper —
  earlier `paper_artifacts.py` variant of the used `lcss_domain.pdf`. Writes
  `domain_boundary_meta.json` alongside.
- *Significance:* same leading-order-domain boundary (10% departure at `τ≈10`);
  [PROVEN] small-`τ` statement.
- *Theory:* Theorem 7.2 (`thm:floor`) small-`τ` statement [PROVEN]; the `τ≈10`
  10%-departure boundary is MEASURED (as in the used `lcss_domain`).
- *Provenance:* [DET] — `holonomy_amplitude_m2` recomputed over a large-`τ` range
  at `ξ=(0.4,0,0.12)` (writes `domain_boundary_meta.json`); no rng.

### `lcss_graphical_abstract.pdf`
- **`lcss_graphical_abstract.pdf`** — vector PDF; NOT used in the submitted paper —
  a three-panel graphical abstract (`lcss_scenario_figs.py` L5): problem
  (delayed decentralized fusion around a cycle) → mechanism
  (`log Hol = τ²[C_i,C_j]+O(τ³)`) → result (measured law + machine-zero
  switch-offs). Kept as a presentation/overview asset.
- *Significance:* narrative summary of the whole letter; the amplitude object is
  [PROVEN], switch-offs machine-zero.
- *Theory:* Theorem 7.2 (`thm:floor`) [PROVEN] amplitude law + switch-offs,
  narrated end to end; the left problem panel illustrates the `lem:m` /
  cyclic-fusion setup.
- *Provenance:* [DET] (with a schematic problem panel) — the result panel is a
  deterministic `holonomy_amplitude_m2` recomputation at `ξ=(0.4,0,0.12)`; the
  left problem panel is a labelled schematic with no measured data.

### `lcss_loop_filmstrip.pdf`
- **`lcss_loop_filmstrip.pdf`** — vector PDF; NOT used in the submitted paper —
  the two-panel filmstrip (`lcss_scenario_figs.py` L1) combining the generic and
  level-set loop trails the paper instead splits into `lcss_loop_generic.pdf`
  (Fig. 4) and `lcss_loop_levelset.pdf` (Fig. 5). Annotates the printed holonomy
  gap and the level-set turnaround.
- *Significance:* same mechanism + C15 discovery, side by side; [PROVEN] loop
  defect + [OBSERVED] all-orders protection.
- *Theory:* Lemma 7.1 (`lem:bch`) loop defect [PROVEN] + Corollary 7.3 (`cor:sym`)
  / C15 all-orders protection [OBSERVED] — the same two statements as Figs. 4–5,
  side by side.
- *Provenance:* [DET] — the same deterministic loop operators
  (`conjugated_generator`, matrix exp) on the fixed generic and level-set pairs at
  `ξ=(0.4,0,0.12)`; no rng.

### `lcss_remainder_stats.pdf`
- **`lcss_remainder_stats.pdf`** — vector PDF; NOT used in the submitted paper —
  earlier `paper_artifacts.py` variant that combined the 220-draw remainder CDF and
  the 20-formation slope histogram; the paper splits these into
  `lcss_remainder_cdf.pdf` (Fig. 9) and `lcss_slope_hist.pdf` (Fig. 8).
- *Significance:* same arm-i/arm-ii data; [PROVEN].
- *Theory:* Theorem 7.2 (`thm:floor`) arms i–ii [PROVEN] — the same
  formation-invariant order and uniform-remainder statements as Figs. 8–9.
- *Provenance:* [SIM] — `tier1_sheaf/results/e3a_extension.json` (seeded, seed
  2026 — `formation_cluster.slopes` + `sups`/`remainder_constant`); confirmed
  present.

### `lcss_schematic.pdf`
- **`lcss_schematic.pdf`** — vector PDF; NOT used in the submitted paper — a
  problem-definition + notation + loop-concept schematic (`paper_artifacts.py`
  `fig_schematic`); the paper conveys the geometry with `lcss_geometry.pdf`
  (Fig. 1) and the mechanism with the loop figures instead.
- *Significance:* conceptual setup only; not a measurement.
- *Theory:* illustrates the Lemma 3.1 (`lem:m`) trivialization setup and the
  cyclic-fusion loop concept behind Theorem 7.2 (`thm:floor`); it is setup, not a
  test of any statement.
- *Provenance:* [DIAGRAM] — conceptual/notation schematic, no measured data.

### `lcss_transit_scene.pdf`
- **`lcss_transit_scene.pdf`** — vector PDF; NOT used in the submitted paper — the
  two-panel scene (`lcss_scenario_figs.py` L2) combining (a) the tow geometry and
  (b) the shape-angle traces the paper instead splits into `lcss_geometry.pdf`
  (Fig. 1) and `lcss_shape_motion.pdf` (Fig. 2).
- *Significance:* same recorded reduced-plant grounding; conceptual.
- *Theory:* Theorem 7.2 (`thm:floor`) standing hypothesis (`lem:m` geometry +
  `ξ≠0, η≠0`) [PROVEN] — the same grounding as Figs. 1–2, combined.
- *Provenance:* [SIM] — the seeded `ReducedPlant` run
  `floor_protocol_movie.runs[0.4]` (seed 0, real cable-angle traces); committed
  video `tier1_sheaf/results/floor_protocol.mp4` confirmed present.

### `theorem_map.pdf`
- **`theorem_map.pdf`** — vector PDF; NOT used in the submitted paper — a rendered
  statement-dependency map (`shared_figs_ieee.py` / `paper_artifacts.py`). The
  paper draws its Fig. `fig:thmmap` from the TikZ source `\input{fig_thmmap.tex}`
  instead, so this PDF is an alternate rendering kept for reference.
- *Depicts:* the proof roadmap — trivialization + edge maps → sheaf → BCH + floor
  theorem → symmetry corollary; the one dashed red node is the [CONJECTURAL]
  stochastic steady-state floor, drawn OUTSIDE the proved chain.
- *Significance:* provenance for the paper's TikZ map; marks the exact
  [PROVEN]/[CONJECTURAL] boundary the letter respects.
- *Theory:* illustrates the whole chain — Lemma 3.1 (`lem:m`) → Lemma 7.1
  (`lem:bch`) → Theorem 7.2 (`thm:floor`) → Corollary 7.3 (`cor:sym`) — and marks
  the [CONJECTURAL] `D_ss` node explicitly OUTSIDE the proved chain; it depicts
  the statements, it does not measure them.
- *Provenance:* [DIAGRAM] — rendered dependency map, no measured data.

---

## Epistemic notes

- **Two different objects, never conflated.** (1) The **error-transport holonomy
  amplitude** = the object of Thm 7.2 [PROVEN] — measured slope 1.999 (Tier-1) /
  2.000 (Drake), coefficient 1.0000; every switch-off is **machine-zero**
  (`ξ=0` literally 0.0, `η=0` `<10⁻¹⁶`, `s_i=s_j` `<10⁻¹⁵`). This is what
  `lcss_amplitude`, `lcss_carpet`, `lcss_bound_ratio`, `lcss_slope_hist`,
  `lcss_remainder_cdf`, `lcss_domain`, and the loop figures show. (2) The
  **closed-loop steady-state disagreement `D_ss`** [CONJECTURAL] — measured slope
  1.08–1.10 on both plants, a MEASURED slope in a conjectural regime whose CI
  excludes both 1 and 2, asserted as NO law. It appears here ONLY as the falsified
  bottom block of `t1_falsifier_forest`. Never read a `D_ss` row as validating
  Thm 7.2, and never call the `D_ss` slope a first-order law.
- **Honest falsifier verdicts** in the forest: C19 TRIPPED favorably (drawn
  orange, not a pass); C7b `D_ss` FALSIFIED at these scales; C9b falsifier MET;
  C9c TRIPS (2.75× < the 10× threshold). A tripped / met / falsified row is never
  dressed as a positive result.
- **C15 is an OBSERVATION.** The discrete level-set protected class
  (`lcss_levelset_bars`, `lcss_heatmap`, `lcss_loop_levelset`) is a numerical
  observation — five zero-commutator pairs with `‖C_i−C_j‖~10⁻¹⁶`, full holonomy
  vanishing at all orders, exactly two torus zeros with the partner 1.057 rad away.
  A commutant argument is suggested; the proof is left to the companion. Do not
  cite it as proved.
- **Units / frame.** Belief-frame axes are dimensionless SE(2) translations; `τ`
  is in seconds; shape separation `Δ` in radians; the shape torus is `[−π,π]²`;
  the common load twist is `ξ=(0.4,0,0.12)`. Cable length `l=1` (unit) in Tier-1.
- **No Drake figures live here.** The independent-plant check (Drake, slope 2.000,
  31× achieved-ε suppression) is reported in the paper text but its figures belong
  to the RA-L companion, not this folder. No ANEES / docking / transit claims
  appear in this Tier-1 floor folder.

## Cross-links

- **Paper:** `../main.tex` (`papers/lcss_letter/main.tex`) — the L-CSS floor letter.
- **Authoritative ledger (verdicts + epistemic status):**
  `../../../docs/ral_package.md`.
- **Reconciliation note:** `../../../docs/reconciliation_2026-07-21.md`.
- **Generators:** `tier1_sheaf/campaign/lcss_figs_ieee.py`,
  `tier1_sheaf/campaign/shared_figs_ieee.py`,
  `tier1_sheaf/campaign/paper_artifacts.py`,
  `tier1_sheaf/campaign/lcss_scenario_figs.py`,
  `tier1_sheaf/campaign/e3a_extension_panels.py`,
  `tier1_sheaf/experiments/e3a_amplitude.py`.
- **Data records:** `tier1_sheaf/results/e3a_amplitude.csv`,
  `tier1_sheaf/results/e3a_extension.json` (replayed and asserted by
  `paper_artifacts.py` before any figure is drawn).
- **Shared style:** `analysis/ieee_style.py`.
