# `tier2_drake/results/s1/` — Blind Harbor campaign records (RA-L companion)

**This is a source / build folder, not the reader-facing paper folder.** It holds the
committed, seeded **data records** (`.json`/`.npz`) and the **movies** for the RA-L
companion *"The Price of Staleness: Distributed Invariant Estimation for GNSS-Denied
Multi-Vessel Cable Towing"* (`papers/ral_blind_harbor/main.tex`), plus a set of
developer / preview figure renders.

The paper's reader-facing figures are **not** the images in this folder. They live in
`papers/ral_blind_harbor/figures/` (basenames `ral_*.pdf`, `tcns_*.pdf`) and are rendered
by `analysis/figures/ral_artifacts.py`, which reads **only** the committed records here
and re-simulates nothing. So for most files in this folder the "canonical" role is as a
**data record that feeds a paper figure through `ral_artifacts.py`**, not as an included
image. The `f4*_overlay.*` / `d9_topology.*` images here are earlier standalone renders,
**superseded** by the `ral_*.pdf` renders in the paper folder.

For the full reader narrative of any figure, cross-link to
**`papers/ral_blind_harbor/figures/README.md`** (the paper-facing catalogue). For per-claim
verdicts see the authoritative ledger **`docs/ral_package.md`**; reconciliation status is in
**`docs/reconciliation_2026-07-21.md`**.

## Publication split (do not conflate)
- **RA-L** = this Drake "Blind Harbor" companion (the only unit that carries Drake figures).
- **T-CNS** flagship §VIII and **L-CSS** floor letter are **Tier-1 numerics only** — no Drake
  figures. The `tcns_f5_amp/floor` and `tcns_f8` images the paper \includes are rendered from
  Tier-1 records that live under `tier1_sheaf/results/`, not here.

## Two objects, never conflated (binding)
1. **Error-transport holonomy amplitude** — object of Thm 7.2 **[PROVEN]**, leading-order,
   deterministic. Measured slope **1.999 (Tier-1) / 2.000 (Drake)**; coefficient 1.0000;
   switch-offs (`ξ=0`, `η=0`) at **machine zero**. Resolved only noise-off.
2. **Closed-loop steady-state disagreement `D_ss`** (units **m²**) — **[CONJECTURAL]**.
   Measured slope **1.101 [1.076,1.125] (Tier-1) / 1.077 [1.054,1.102] (Drake)** — a *measured*
   slope in a conjectural regime, carried with the R3 mixture caveat, **asserted as no law**;
   its CI **excludes both 1 and 2**. The order-2 conjecture is **falsified at these scales**.

**Never caption a `D_ss` fit as validating Thm 7.2. Never call the `D_ss` slope a first-order
law.** A tripped / fired / falsified / MET falsifier row is never reported as a positive result.

Frames/units: world **ENU, metres**; load pose **SE(2) = (x, y, yaw)**; `D` (disagreement) in
**m²**; staleness `τ` in **s**. Predictions are labelled as predictions; only realized/measured
states are stated as facts. The paper bibliographies are currently **empty (zero `\cite`)** — no
file here is externally cited.

---

## Data provenance & authenticity

Every catalogued entry below carries two added labels: a **`*Theory:*`** line naming the specific
RA-L statement (label + number) or the honest empirical thesis / falsifier it bears on, and a
**`*Provenance:*`** line assigning exactly one authenticity class and naming the exact on-disk
record. The theorem numbers cited are the RA-L paper's own (`papers/ral_blind_harbor/main.tex`,
independent per-environment counters): **Lemma 1** `lem:m` (constraint trivialization), **Lemma 2**
`lem:edge`, **Lemma 3** `lem:bchF` (group-commutator defect); **Definition 1** `def:sheafF`
(estimation sheaf / sheaf Laplacian); **Theorem 1** `thm:gaugeF` (exact residual unobservability =
one global gauge), **Theorem 2** `thm:contractF` (frozen-linearization contraction), **Theorem 3**
`thm:floorF` [PROVEN] (latency–curvature floor, amplitude order `τ²`); **Corollary 1** `cor:pinF`
(pinning), **Corollary 2** `cor:inheritF` (network inheritance of conditioning singularities),
**Corollary 3** `cor:symF` (symmetry protection). (The `Thm 7.2` / `Cor. 5.2` numbers used in the
prose above and below are the **theory-source** numbering, preserved verbatim; they correspond to
`thm:floorF` and `cor:pinF` respectively.)

**Authenticity classes** — one per entry:
- **[SIM]** a seeded generator ran the actual plant (Tier-2 Drake `MultibodyPlant`, or the Tier-1
  `ReducedPlant` for the cross-tier reference rungs) under a fixed seed and wrote a committed
  `.json`/`.npz` record; the figure/movie reads that record. Seeded `np.random.default_rng(seed)`
  is **reproducible simulation noise = real simulated data, not fabrication**.
- **[DET]** deterministic recomputation of an exact analytic quantity from released operators at
  fixed inputs, no randomness.
- **[DIAGRAM]** a conceptual/schematic illustration with no measured data.
- **[FLAG]** fabricated or untraceable — a measurement-looking plot with invented numbers.

**Counts for this folder (38 entries): [SIM] 38 · [DET] 0 · [DIAGRAM] 0 · [FLAG] 0.**

**Finding — nothing is fabricated.** Every data figure in this folder traces to a committed,
seeded simulation record (a Drake `MultibodyPlant` transit/sweep, or a Tier-1 `ReducedPlant`
reference record committed here for the cross-tier rungs) or to a standalone/movie render that
reads only those committed records and re-simulates nothing (`ral_artifacts.py` is a pure
record→figure renderer; `campaign_replay.py` re-probes the records to `1e-6`). There are **no**
deterministic-operator entries, **no** conceptual diagrams, and **no [FLAG]** — no hardcoded or
untraceable measurement-looking values were found in this folder. The analytic `[DET]` amplitude
recomputations and the schematic `[DIAGRAM]` figures live in the **paper** figure folders
(`papers/…/figures/`), not here. Epistemic guardrails hold throughout: the **[PROVEN]** amplitude
(object 1, `thm:floorF`/Thm 7.2) and the **[CONJECTURAL]** closed-loop `D_ss` (object 2) are never
conflated; falsifier rows (C7b **FALSIFIED**, D9 **FIRES**, docking **UNMET**, C9c **TRIPS**) are
reported as such, never as positive results; B1 is a **reference, not an oracle**; every ANEES
claim carries its horizon. The one dev-only exception to "feeds the paper" is the `pilot6*`
family, which is a superseded seeded pilot (still [SIM], but read by nothing).

---

## File catalogue (every file, provenance-focused)

### Primary closed-loop / hero records (canonical data → paper figures)

**`hero_dogleg_series.npz`** — generator `tier2_drake/blind_harbor/hero_dogleg.py`; read by
`ral_artifacts.py`. The committed 450 s dogleg transit truth (seed 3), barge + vessel
trajectories, `D(t)`, gauge-kernel component. **CANONICAL data**: renders `ral_hero_traj.pdf`
(Fig. heroseries) and `ral_hero_D.pdf` (Fig. heroD) in the paper folder. *Verdict:* the `D(t)`
acquisition spike is the **pin shock** of Cor. 5.2 [PROVEN] in closed loop; the gauge-kernel
component grows unbounded under GNSS denial and is killed only by the beacon.

*Theory:* **Corollary 1 (`cor:pinF`) [PROVEN]** — the `D(t)` acquisition spike **is** the pin shock live; the unbounded gauge-kernel growth realizes **Theorem 1 (`thm:gaugeF`) [PROVEN]** (pose observable only modulo one SE(2) gauge, so the kernel drifts freely until the beacon pins it).  
*Provenance:* **[SIM]** — `hero_dogleg_series.npz` (Drake `MultibodyPlant`, seed 3; arrays `ts,D,kern,comp,truth`, `ts` shape (4501,) float64) confirmed present on disk.

**`hero_series.npz`** — generator `hero_dogleg.py`; read by `ral_artifacts.py`. Per-agent
load-pose error at the **130 s calibration horizon** (recorded run). **CANONICAL data**: renders
`ral_agent_errors.pdf` (Fig. agenterr). *Verdict:* at this horizon the single beacon (agent 0)
propagates cleanly through fusion; the 130 s ANEES gate does **not** transfer to 450 s transits.

*Theory:* empirical validation of **Corollary 1 (`cor:pinF`)** under fusion — the single pin propagates through the sheaf; the ANEES gate is the empirical **M-FAB / D1 calibration falsifier** (carried with its **130 s horizon**), not a theorem claim.  
*Provenance:* **[SIM]** — `hero_series.npz` (Drake `MultibodyPlant`, recorded hero run) confirmed present on disk.

**`hero_ghost_tracks.npz`** — generator `tier2_drake/campaign/hero_ghost_tracks.py`; read by
`tier2_drake/campaign/ral_scenario_figs.py` / `ral_figs_ieee.py`. The five agents' private
load-pose estimates (ghost caissons, seed 3). **CANONICAL data**: renders `ral_gauge_trails.pdf`
(Fig. gaugeorbit). *Verdict:* Cor. 5.2 [PROVEN] shown spatially — the fleet stays a tight
consistent group but drifts off truth, then collapses toward it at beacon acquisition.

*Theory:* **Theorem 1 (`thm:gaugeF`) [PROVEN]** shown spatially — the tight consistent fleet that drifts off truth **is** the SE(2) gauge orbit; its collapse at acquisition is **Corollary 1 (`cor:pinF`) [PROVEN]**.  
*Provenance:* **[SIM]** — `hero_ghost_tracks.npz` (Drake `MultibodyPlant`, seed 3; arrays `ts,truth,ghost_paper,ghost_b0,t_on,seed`) confirmed present on disk.

**`hero_v2_ensemble.json`** — generator `tier2_drake/campaign/hero_v2_ensemble.py`; read by
`ral_artifacts.py`. 12-seed decelerating-approach (v2) ensemble. **CANONICAL data**: renders
`ral_v2seeds.pdf` (Fig. v2seeds). *Verdict:* v2 improves fleet-mean **2.4×** (median 0.61 m; 17%
of seeds < 0.5 m) — **spec still UNMET**; the anchored agent is worse than the fleet mean on
**11/12** seeds (anchored gain starvation). Also carries the long-transit ANEES **159–229**
disclosure (M-FAB gate does not transfer to 450 s).

*Theory:* empirical **"price of staleness" / docking-remedy** thesis and the anchored-gain-starvation caveat on **Corollary 1 (`cor:pinF`)** — **not** a theorem pass: docking **spec UNMET**, and the ANEES **159–229** disclosure carries its **450 s horizon**.  
*Provenance:* **[SIM]** — `hero_v2_ensemble.json` (12-seed Drake `MultibodyPlant` ensemble) confirmed present on disk.

**`hero_ensemble.json`** — generator `tier2_drake/blind_harbor/hero_dogleg.py` (hero v1). The v1
transit ensemble. **SUPERSEDED for the docking-remedy figure by `hero_v2_ensemble.json`** (the
v2 record is what the paper \includes); retained as the v1 baseline ensemble.

*Theory:* same empirical docking-remedy thesis as `hero_v2_ensemble.json` (v1 baseline arm); superseded, not itself \included.  
*Provenance:* **[SIM]** — `hero_ensemble.json` (v1 Drake `MultibodyPlant` transit ensemble) confirmed present on disk.

### Docking scorecard (D7)

**`d7_scorecard.json`** — generator `tier2_drake/campaign/d7_scorecard.py`; read by
`ral_artifacts.py`. 50 dogleg transits × 4 arms (B1-limit, DIEKF-Σ, B2 consensus, B0
dead-reckon). **CANONICAL data**: fills Table `scorecard` and renders `ral_score_box.pdf` /
`ral_score_cdf.pdf`. *Verdict:* ordering on **`D` and fleet-mean** B1lim > paper > B2 ≫ B0
(fleet-mean 0.76 / 1.57 / 2.13 / 66.7 m); **docking < 0.5 m: 0% of ALL arms** at plan-faithful
acquisition (even the zero-latency B1-limit misses spec) — approach geometry, not the estimator,
binds.

*Theory:* empirical validation of **Corollary 1 (`cor:pinF`)** under staleness and the **D7 docking-scorecard falsifier** (docking-spec **UNMET, 0% all arms**) — an approach-geometry finding, not a theorem.  
*Provenance:* **[SIM]** — `d7_scorecard.json` (50 transits × 4 arms, Drake `MultibodyPlant`; JSON list of 200 records) confirmed present on disk.

**`d7_a2_arm.json`** — generator `tier2_drake/campaign/d7_a2_arm.py`. The A2 (unconjugated
transport) arm's own 50 transits. **CANONICAL data**: supplies the **A2 row** of Table
`scorecard` (fleet-mean 1.75 m). *Verdict:* ablating the conjugated transport degrades the
scorecard; the A2-inclusive rule head-to-head in the transit setting is otherwise noted as
un-run in the ledger.

*Theory:* ablation supporting **Lemma 1 (`lem:m`)** (conjugation by `m` makes the decentralized load frame well-posed) — unconjugated A2 transport degrades the D7 scorecard; empirical ablation, not a theorem test.  
*Provenance:* **[SIM]** — `d7_a2_arm.json` (A2 arm, 50 Drake transits) confirmed present on disk.

### Amplitude & floor overlays (D2 / D3 records + preview renders)

**`d3_amplitude.json`** — generator `tier2_drake/blind_harbor/d3_amplitude.py`; read by
`ral_artifacts.py`. Drake error-transport holonomy amplitude sweep. **CANONICAL data**: renders
`ral_f4a.pdf` (Fig. f4a). *Verdict:* **PASSED** — slope **2.000**, `m=2` coefficient 1.0000,
`η=0` switch-off machine-zero; symmetric class suppresses the **amplitude** **31×**
(achieved-ε; exact cancellation is the Tier-1 machine-zero result). Object (1), [PROVEN].

*Theory:* **Theorem 3 (`thm:floorF`) [PROVEN]** — the measured **slope-2 IS the theorem's amplitude claim** (object 1); the defect is **Lemma 3 (`lem:bchF`)** `Log Hol = τ²[C_i,C_j]+O(τ³)`, and the 31× symmetric suppression is **Corollary 3 (`cor:symF`)**.  
*Provenance:* **[SIM]** — `d3_amplitude.json` (Drake `MultibodyPlant` amplitude sweep; dict `{taus, arms}`) confirmed present on disk.

**`production_d2_d4_v2.json`** — generator `tier2_drake/campaign/production_d2_d4.py`. Drake
closed-loop `D_ss` vs `τ` (measured-`D₀` protocol), the production floor record. **CANONICAL
data**: the Drake `D_ss` exponent behind Fig. f4b / cross-tier. *Verdict:* order-2 conjecture
**FALSIFIED at these scales** — slope **1.077 [1.054,1.102]** (excludes 2 and 1). Object (2),
[CONJECTURAL]; measured slope, no law asserted.

*Theory:* **object (2), closed-loop `D_ss` [CONJECTURAL]** — explicitly **NOT** a test of `thm:floorF`; this is falsifier **C7b-Drake**, verdict **FALSIFIED** (2 ∉ CI). Never caption as validating the floor theorem.  
*Provenance:* **[SIM]** — `production_d2_d4_v2.json` (Drake `MultibodyPlant`, measured-`D₀` protocol; JSON list of 270 records) confirmed present on disk.

**`production_d2_d4.json`** — generator `production_d2_d4.py` (pre-`v2`). Earlier D2/D4 floor
production run. **SUPERSEDED by `production_d2_d4_v2.json`** (the v2 measured-`D₀` protocol is the
one the paper reports).

*Theory:* same **object (2) [CONJECTURAL]** floor / **C7b** falsifier as the v2 record; superseded pre-`v2` run.  
*Provenance:* **[SIM]** — `production_d2_d4.json` (earlier Drake `MultibodyPlant` floor run) confirmed present on disk.

**`d2_straight_control.json`** — generator `tier2_drake/campaign/d2_controls.py`. Straight-tow
control that measures `D₀` **in situ** (the noise-floor control). **CANONICAL data**: supplies
the measured-`D₀` baseline and the motion-excitation ratio (**19–21×** at every `τ`) for Fig. f4b
/ f4c. *Verdict:* mechanism check **passes** (excitation ≫ 10× threshold) — closed-loop floor is
excited only by shape motion.

*Theory:* **object (2)** mechanism control — the **D2 excitation check** (shape-motion excites the floor ≫ 10×); empirical noise-floor control for the [CONJECTURAL] sweep, not a theorem.  
*Provenance:* **[SIM]** — `d2_straight_control.json` (straight-tow Drake `MultibodyPlant` control) confirmed present on disk.

**`d2_tau005.json`** — generator `tier2_drake/campaign/d2_tau005.py`. The `τ=0.05 s` short-lag
floor arm. **CANONICAL data**: low-`τ` point for the Drake floor fit (Fig. f4b). *Verdict:* part
of the [CONJECTURAL] floor sweep; same falsification verdict as above.

*Theory:* **object (2) [CONJECTURAL]** floor-sweep point (short-lag `τ=0.05 s`); same **C7b** falsification, not a `thm:floorF` test.  
*Provenance:* **[SIM]** — `d2_tau005.json` (`τ=0.05 s` Drake `MultibodyPlant` arm) confirmed present on disk.

**`d2_a1_a2_arms.json`** — generator `production_d2_d4.py` / `d2` arm drivers; read by
`ral_artifacts.py`. All Drake fusion-rule arms (paper rule, A1 naive consensus, A2 unconjugated)
on matched formation draws. **CANONICAL data**: renders `ral_f4c.pdf` (Fig. f4c). *Verdict:*
conjugated transport is **load-bearing** — A2 runs **1.7×→8.2×** above the paper rule with growing
`τ`; A1 consensus holds disagreement flat **by groupthink** (anchored ANEES 62, drift 8.4 m at the
130 s horizon) — **agreement alone is never a virtue metric**.

*Theory:* **Lemma 1 (`lem:m`)** conjugated transport is load-bearing — unconjugated A2 departs 1.7×→8.2×; A1 groupthink shows agreement is not a virtue metric; empirical arm comparison in the object-(2) regime.  
*Provenance:* **[SIM]** — `d2_a1_a2_arms.json` (paper/A1/A2 Drake `MultibodyPlant` arms on matched draws) confirmed present on disk.

**`f4a_overlay.pdf` / `.png`** — generator `analysis/figures/f4a_overlay.py`. Standalone amplitude
overlay (Tier-1 vs Drake). **SUPERSEDED / dev-preview** — the paper \includes `ral_f4a.pdf`
(rendered by `ral_artifacts.py` from `d3_amplitude.json`). Same verdict as `d3_amplitude.json`.

*Theory:* **Theorem 3 (`thm:floorF`) [PROVEN]** amplitude object (1) — the measured slope-2 amplitude claim; superseded standalone render.  
*Provenance:* **[SIM]** — a render (no new simulation) of committed records `d3_amplitude.json` (+ Tier-1 `tier1_sheaf/results/e3a_amplitude.csv`); both confirmed present on disk.

**`f4b_overlay.pdf` / `.png`** — generator `analysis/figures/f4b_overlay.py`. Standalone
cross-tier floor overlay + equivalence box. **SUPERSEDED / dev-preview** — the paper \includes
`ral_f4b.pdf`. *Verdict:* cross-tier exponent **EQUIVALENT** (+0.023 [−0.012,+0.057] ⊂ [−0.2,0.2]);
order-2 excluded on both plants ([CONJECTURAL] floor).

*Theory:* **object (2), `D_ss` [CONJECTURAL]** — NOT `thm:floorF`; cross-tier equivalence of the *measured* exponent (order-2 excluded on both plants); superseded render.  
*Provenance:* **[SIM]** — a render of committed records `production_d2_d4_v2.json` (+ Tier-1 `tier1_sheaf/results/f4b_tier1.*`); confirmed present on disk.

**`f4c_variance_attribution.pdf` / `.png`** — generator `analysis/figures/f4c_attribution.py`.
Standalone variance-attribution render. **SUPERSEDED / dev-preview** — the paper \includes
`ral_f4c.pdf` (from `d2_a1_a2_arms.json`). Same verdict as `d2_a1_a2_arms.json`.

*Theory:* **Lemma 1 (`lem:m`)** conjugated-transport attribution in the object-(2) regime; superseded standalone render.  
*Provenance:* **[SIM]** — a render of committed record `d2_a1_a2_arms.json`; confirmed present on disk.

**`f4_cross_tier_overlay.pdf` / `.png`** — generator `analysis/figures/f4_overlay.py`. Three-exponent
epistemic-spine overlay. **SUPERSEDED / dev-preview** — the paper \includes `ral_cross_tier.pdf`
(Fig. ladderoverlay). *Verdict:* the three-object spine — `p=2.00` theorem object [PROVEN],
`p=1.00` transport-mismatch channel, `p≈1.08` measured closed-loop floor [CONJECTURAL] — **never
conflated**.

*Theory:* the three-object epistemic spine — **Theorem 3 (`thm:floorF`) [PROVEN]** `p=2` amplitude (object 1) vs the `p=1` transport-mismatch channel vs the **[CONJECTURAL]** `p≈1.08` measured floor (object 2); the figure exists to keep them **never conflated**.  
*Provenance:* **[SIM]** — a render of committed records `d3_amplitude.json` + `production_d2_d4_v2.json` + `matched_*.json`; all confirmed present on disk.

### Cross-tier coefficient matching (§VI)

**`matched_drake.json`** — generator `tier2_drake/campaign/matched_drake.py`. Reference-matched
Drake coefficient record. **CANONICAL data**: the cross-tier coefficient-ratio row (forest fig
`ral_forest.pdf`). *Verdict:* coefficient ratio **DISAGREES ×5** (5.04 [3.97,6.19]) — a
reduced-model **validity-domain** finding (Drake realized shapes exit the reduced model's domain),
not an error.

*Theory:* **§VI cross-tier coefficient matching** — a reduced-model **validity-domain** finding for the amplitude coefficient behind `lem:bchF`/`thm:floorF`; empirical (a ×5 domain disagreement), **not** a theorem pass.  
*Provenance:* **[SIM]** — `matched_drake.json` (reference-matched Drake `MultibodyPlant`; dict `{turn, straight, shapes}`) confirmed present on disk.

**`matched_t1.json`** — generator `tier2_drake/campaign/matched_t1.py`. Reference-matched Tier-1
coefficient record; carries the `_qxi_off_probe`. **CANONICAL data**: the localization rung of the
×5 disagreement. *Verdict:* with reduced-plant process noise off, straight **baselines agree to
12%** — the excess is attributed to the inertia-free shape response.

*Theory:* **§VI cross-tier matching** (Tier-1 localization rung of the ×5 disagreement); empirical validity-domain evidence, not a theorem test.  
*Provenance:* **[SIM]** — `matched_t1.json` (Tier-1 `ReducedPlant` reference record, `_qxi_off_probe`) confirmed present on disk.

### Baselines / centralized reference (B1)

**`b1_limit_mfab.json`** — generator `tier2_drake/campaign/baselines.py` (B1-limit). The record's
own **zero-latency all-to-all limit** at the M-FAB 130 s horizon. **CANONICAL data**: the B1
reference (scorecard B1-limit row; text). *Verdict:* a **REFERENCE, not an oracle** — 6% gap at
the 130 s horizon (0.172 vs 0.183 m); a fundamentally better centralized estimator is **not
excluded**.

*Theory:* the record's own **zero-latency all-to-all B1 reference** (not an oracle, not a theorem) — the anchor of the empirical price-of-staleness comparison, carried with its **130 s horizon**.  
*Provenance:* **[SIM]** — `b1_limit_mfab.json` (B1-limit Drake `MultibodyPlant` run) confirmed present on disk.

**`b1_true.json`** — generator `tier2_drake/campaign/b1_true.py`. B1 true-state reference run.
**CANONICAL data**: supporting B1 record for the centralization-worth discussion. *Verdict:* same
"reference, not oracle" framing.

*Theory:* same **B1 reference-not-oracle** framing; empirical baseline for the centralization-worth discussion, not a theorem.  
*Provenance:* **[SIM]** — `b1_true.json` (B1 true-state Drake `MultibodyPlant` run) confirmed present on disk.

**`baselines.json`** — generator `tier2_drake/campaign/baselines.py`. The baselines table record
(B0/B1/B2 family). **CANONICAL data**: baselines table / discussion. *Verdict:* dead-reckoning
(B0) diverges to tens of metres; consensus (B2) buys agreement by groupthink; the sheaf transport
is load-bearing.

*Theory:* empirical baselines supporting the **"sheaf transport is load-bearing"** thesis (context of **Definition 1 (`def:sheafF`)** and **Lemma 1 (`lem:m`)**); not itself a theorem test.  
*Provenance:* **[SIM]** — `baselines.json` (B0/B1/B2 Drake `MultibodyPlant` family) confirmed present on disk.

### Numerics defense & robustness

**`d8_h_sweep.json`** — generator `tier2_drake/campaign/d8_h_sweep.py`. Integrator-step sweep
`h ∈ {0.5,1,2} ms`; carries `_truth_diff_check`. **CANONICAL data**: the numerics-defense
paragraph (Sec. results; no dedicated figure). *Verdict:* **PASSED** — floor exponent identical to
three decimals across `h`; convergence verified genuine by truth-diff **1.35 mm** over 30 s.

*Theory:* **D8 numerics-defense falsifier** — the object-(2) floor exponent is `h`-invariant to three decimals; supports integrity of the [CONJECTURAL] floor sweep, not a theorem.  
*Provenance:* **[SIM]** — `d8_h_sweep.json` (`h ∈ {0.5,1,2} ms` Drake `MultibodyPlant` sweep, `_truth_diff_check`) confirmed present on disk.

**`d9_scaling.json`** — generator `tier2_drake/campaign/d9_scaling.py`; read by `ral_artifacts.py`.
Topology × `N` scaling (`λ₂`), pin-rate, re-agreement. **CANONICAL data**: renders `ral_d9.pdf`
(Fig. d9). *Verdict:* **D9 falsifier FIRES** — pin rate `ρ=+0.04 ≈ 0` (**anchor-limited, not
connectivity-limited**); `D` re-agreement **anti-orders** `−0.51 [−0.65,−0.36]` (stiff consensus
resists the pin). Reported honestly as the ES-01 finding, never as a pass.

*Theory:* bears on **Corollary 2 (`cor:inheritF`)** (network inheritance) and the `κλ₂` rate of **Theorem 2 (`thm:contractF`)**, but the result is the **D9 falsifier — verdict FIRES** (pin anchor-limited, `ρ=+0.04≈0`), reported as the ES-01 finding, **never a pass**.  
*Provenance:* **[SIM]** — `d9_scaling.json` (topology × `N` Drake `MultibodyPlant` scaling, ~977 KB) confirmed present on disk.

**`d9_topology.pdf` / `.png`** — a standalone topology preview render from the D9 campaign.
**SUPERSEDED / dev-preview** — the paper \includes `ral_d9.pdf` (from `d9_scaling.json`). Same
verdict as `d9_scaling.json`.

*Theory:* same **D9 falsifier (FIRES)** / `cor:inheritF` context as `d9_scaling.json`; superseded standalone render.  
*Provenance:* **[SIM]** — a render of committed record `d9_scaling.json`; confirmed present on disk.

**`d10b_loss.json`** — generator `tier2_drake/campaign/d10b_loss.py`; read by `ral_artifacts.py`.
Packet-drop / jitter robustness (8 seeds/arm, outside protocol class 𝒫). **CANONICAL data**:
renders `ral_robust_drops.pdf` (Fig. robust). *Verdict:* **graceful, no red flags** — floor +13% @
`p=0.1`, +45% @ `p=0.3`; anchored ANEES in-gate at `p=0.3` (**4.23, at the 130 s horizon**).

*Theory:* **D10b robustness falsifier** (drop/jitter **outside protocol class 𝒫**) — empirical graceful degradation of the object-(2) floor; carries its **130 s ANEES horizon**; not a theorem.  
*Provenance:* **[SIM]** — `d10b_loss.json` (8 seeds/arm packet-drop Drake `MultibodyPlant` runs) confirmed present on disk.

**`d10c_guard.json`** — generator `tier2_drake/campaign/d10c_guard.py`; read by `ral_artifacts.py`.
Broadside-guard gust campaign (pairs + envelope probes). **CANONICAL data**: renders
`ral_robust_guard.pdf` (Fig. guard). *Verdict:* **null with a mechanism** — the guard trigger
(estimated `σ̂_i`) lags true broadside across the reachable envelope (true 0.027 vs est 0.106 at
5000 N), so ON ≡ OFF bit-identical; the rescue movie does **not** ship.

*Theory:* **D10c robustness falsifier** — an empirical **null with a mechanism** (guard estimator lags true broadside, ON ≡ OFF); honest negative, not a theorem test.  
*Provenance:* **[SIM]** — `d10c_guard.json` (broadside-guard gust Drake `MultibodyPlant` pairs + envelope probes) confirmed present on disk.

**`d6_tension.json`** — generator `tier2_drake/campaign/d6_tension.py`; read by `ral_artifacts.py`.
Fusion-weight (tension channel) dose-response. **CANONICAL data**: ledger row / forest fig
(no dedicated `\include` — campaign matrix files this under "ledger"). *Verdict:* Part 1 **PASSES**
(series weights: Δ shape-RMSE −8.4e-3 [−10.9e-3,−5.8e-3]); Part 2 dose-response **dropped per
pre-registration** (CI includes 0).

*Theory:* **C6 / D6 falsifier** (tension/information channel carries estimation benefit; context of the fusion-weighting in **Theorem 2 (`thm:contractF`)**) — Part 1 PASSES, Part 2 dropped per pre-registration; empirical.  
*Provenance:* **[SIM]** — `d6_tension.json` (fusion-weight dose-response Drake `MultibodyPlant` sweep) confirmed present on disk.

**`s1_verdict.json`** — generator `tier2_drake/blind_harbor/s1.py`. The M-FAB / D1 filter-consistency
verdict at the S1 horizon. **CANONICAL data**: the "Calibration, disclosed" paragraph. *Verdict:*
consistency gate closes only under the author-ruled `[0.8, 5.0]` gate **at the 130 s horizon**
(ANEES **3.96**); original `[0.8,1.3]` not met; complement sanity failed at 3.35; filter ~3–4×
optimistic (CI structural). Every ANEES claim carries its horizon.

*Theory:* **D1 / M-FAB filter-consistency falsifier** — empirical calibration disclosure (ANEES **3.96** at the **130 s horizon**, filter 3–4× optimistic); a disclosed limitation, not a theorem claim.  
*Provenance:* **[SIM]** — `s1_verdict.json` (Drake `MultibodyPlant` consistency verdict; keys `seeds, anees_anchored_mean, gate, in_gate, …`) confirmed present on disk.

### Movies (supplementary S1–S4; none evidentiary)

**`hero_dogleg_web.mp4`** — generator `tier2_drake/blind_harbor/hero_dogleg.py`. **CANONICAL**:
the shipped supplementary **S1** (450 s transit, five-beat storyboard, honest scorecard closing
card, ~9× time compression). Cross-link the paper's Supplementary Movies §.

*Theory:* illustrates **Corollary 1 (`cor:pinF`)** pin shock and **Theorem 1 (`thm:gaugeF`)** gauge drift in closed loop; supplementary, **non-evidentiary**.  
*Provenance:* **[SIM]** — rendered from the same seed-3 Drake `MultibodyPlant` transit as `hero_dogleg_series.npz`; movie confirmed present on disk.

**`hero_dogleg.mp4`** — generator `hero_dogleg.py`. Full-resolution S1 source. **Dev/preview** —
`hero_dogleg_web.mp4` is the web-encoded version that ships.

*Theory:* same S1 content (`cor:pinF` / `thm:gaugeF` illustration); non-evidentiary dev/preview source.  
*Provenance:* **[SIM]** — full-resolution render of the same seed-3 Drake transit; confirmed present on disk.

**`hero_blind_harbor.mp4`** — generator `tier2_drake/blind_harbor/hero.py`. **CANONICAL**: the
shipped supplementary **S2** (gauge-pinning demo with ghost-caisson overlays; the `D(t)` spike is
Cor. 5.2 live, ~4.8× real time).

*Theory:* **Corollary 1 (`cor:pinF`) [PROVEN]** live — the `D(t)` spike is the pin shock; supplementary, non-evidentiary.  
*Provenance:* **[SIM]** — rendered from a seeded Drake `MultibodyPlant` gauge-pinning run (`hero.py`); confirmed present on disk.

**`hero_blind_harbor.gif`** — generator `hero.py`. GIF preview of S2. **Dev/preview** —
`hero_blind_harbor.mp4` is the shipped movie.

*Theory:* same S2 content (`cor:pinF` live); non-evidentiary dev/preview.  
*Provenance:* **[SIM]** — GIF render of the same seeded Drake gauge-pinning run; confirmed present on disk.

**`hero_montage.png`** — generator `hero.py`. Static montage of the S2 gauge-pinning frames.
**Dev/preview / gallery still** — not `\included` by the paper (no `\includegraphics{hero_montage}`).

*Theory:* static montage of the S2 (`cor:pinF`) frames; non-evidentiary gallery still.  
*Provenance:* **[SIM]** — montage of frames from the same seeded Drake gauge-pinning run (real simulated frames, not a schematic); confirmed present on disk.

**`error_anatomy.mp4`** — generator `tier2_drake/campaign/error_anatomy_movie.py`. **CANONICAL**:
the shipped supplementary **S4**, the deliberate **failure-case** movie (hero v2 median seed;
post-beacon the anchored agent starves its beacon gain and stays high, ~25× real time).

*Theory:* empirical **failure-case** — the anchored-gain-starvation caveat on **Corollary 1 (`cor:pinF`)**; supplementary, non-evidentiary (an honest negative, not a theorem).  
*Provenance:* **[SIM]** — rendered from the committed run `error_anatomy_series.npz` (hero-v2 median seed); confirmed present on disk.

**`error_anatomy_series.npz`** — generator `error_anatomy_movie.py`. The persisted run underlying
S4 (so the failure-case movie is itself replayable). **CANONICAL data** for S4.

*Theory:* same failure-case / `cor:pinF` starvation caveat as S4; the replayable record behind the movie.  
*Provenance:* **[SIM]** — `error_anatomy_series.npz` (Drake `MultibodyPlant`; arrays `ts,truth,errs,seed`, `ts` shape (5201,) float64) confirmed present on disk.

> S3 (`tow_N5.mp4`, generated by `render.py`) is referenced by the paper but is **not present in
> this folder** — do not look for it here.

### Developer pilots (not used by the paper)

**`pilot6.json`, `pilot6_gen.json`, `pilot6_parallel.json`** — early 6-arm pilots (Jul 18; see
`docs/comprehensive_execution_plan.md`). **Dev-only / SUPERSEDED** by the D2 production records
above. Not read by `ral_artifacts.py` and not `\included`.

*Theory:* **none** — developer pilots feed no paper figure and support no theorem; superseded by the D2 production records.  
*Provenance:* **[SIM]** — seeded early 6-arm pilot runs; `pilot6.json`, `pilot6_gen.json`, `pilot6_parallel.json` confirmed present on disk (dev-only, read by nothing).

### `artifacts/` subdirectory — developer gallery build

`artifacts/` (and `artifacts/ieee/`) is a **preview gallery build** produced by
`tier2_drake/campaign/ral_scenario_figs.py`, `ral_figs_ieee.py`, and
`analysis/figures/build_drake_gallery.py` — an alternate/earlier render of the same figure set
(`ral_scenario`, `ral_transit_filmstrip`, `ral_gauge_orbit`, `ral_scorecard_stats`, `ral_v2_seeds`,
`ral_forest`, the `ieee/` IEEE-styled variants, etc.). **These are SUPERSEDED / dev-preview**: the
paper \includes the `ral_*.pdf` set in `papers/ral_blind_harbor/figures/` rendered by
`analysis/figures/ral_artifacts.py`. The one **canonical data** file inside is
**`artifacts/scorecard_wins.json`** — the seed-wise win-count record read by `ral_artifacts.py`
for the scorecard figures (paper rule beats B2 41/50, beats B0 50/50; B1-limit beats paper rule
47/50).

*Theory:* superseded gallery renders of the same figure set; the canonical `scorecard_wins.json` supports the empirical **D7 scorecard** win-counts (empirical, not a theorem).  
*Provenance:* **[SIM]** — superseded renders of committed records, plus the canonical seeded record `artifacts/scorecard_wins.json` (win-counts over the 50 Drake transits); confirmed present on disk.

---

## Reproducibility
Every record is written by a seeded, versioned driver under `tier2_drake/campaign/` or
`tier2_drake/blind_harbor/`; `campaign_replay.py` re-executes per-run probes that must match the
committed records exactly (Drake to `1e-6`). The paper-figure generator
`analysis/figures/ral_artifacts.py` reads **only** these records and re-simulates nothing, so the
figures cannot drift from the campaign. See Table `registry` in the paper and §3 of
`docs/ral_package.md`.
