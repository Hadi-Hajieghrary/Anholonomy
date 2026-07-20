# RA-L Blind Harbor Companion — Submission Package (assembled 2026-07-20)

**Working title:** *The Price of Staleness: Distributed Invariant Estimation for
GNSS-Denied Multi-Vessel Cable Towing*

**Abstract:** as drafted 2026-07-19; findings (i) and (iii) are measured,
adjudicated, and numerics-defended below; finding (ii)'s rule-ranking clause
rests on the Drake arms and the baselines pilot — its definitive head-to-head is
the pending D7 scorecard (§4).

---

## 1. Claim / falsifier ledger (complete adjudication)

| ID | Claim | Pre-registered falsifier | Verdict | Evidence |
|---|---|---|---|---|
| C6 | contraction rate ∝ κλ₂ (Thm 6.3, LTV/frozen) | slope < 0.5 | **PASSED** (1.403, two topologies; μ = −0.062 topology-independent) | e2_contraction.json, F8 |
| C19 | log-linear error dynamics, 2nd-order remainder | remainder exponent CI excludes [1.8, 2.2] | **FALSIFIER TRIPPED** (2.48 [2.32, 2.65] excludes the band). Localization: the deviation is in the favorable direction — the remainder vanishes FASTER than the registered 2nd-order statement; the claim is to be restated with the corrected order, not counted as a pass | e2_contraction.json (v2 scaling-pair estimator) |
| C7a / C8 / C13 | holonomy amplitude O(τ²), coefficient, switch-offs (Thm 7.2, PROV) | 2 ∉ slope CI; coef ∉ [0.9, 1.1]; switch-offs nonzero | **PASSED both plants** — T1: 1.999, switch-offs machine-zero (ξ=0 literally 0.0); Drake D3: 2.000, coef 1.0000, η=0 machine-zero | e3a_amplitude.csv, d3_amplitude.json, F4a-overlay |
| Cor 7.3 (amplitude) | symmetric class suppresses the amplitude | — | **31× on Drake (achieved-ε), machine-zero on Tier-1** | d3_amplitude.json |
| C7b (Tier-1) | closed-loop D_ss order 2 (CONJ) | 2 ∉ p CI | **FALSIFIED at these scales**: fitted p = 1.101 [1.076, 1.125] (a measured slope, CONJ regime — not asserted as a law; the CI also excludes 1). Frozen+noise-off regression arm reproduces the executed null (D_ss ≈ 6e-30, a D value, not a p-value) | e3b_production.json (1584 runs) |
| C7b-Drake | same, Drake | 2 ∉ p CI (measured-D₀ protocol) | **FALSIFIED at these scales**: fitted p = 1.077 [1.054, 1.102] (measured slope; CI also excludes 1); mechanism check passed ~19–21× across τ (falsifier threshold ≥10×) | production_d2_d4_v2 + d2_straight_control + d2_tau005 |
| §6 exponent equivalence | cross-tier | diff CI ⊄ [−0.2, 0.2] | **EQUIVALENT**: +0.023 [−0.012, +0.057] | F4b-overlay |
| §6 coefficient ratio | cross-tier, reference-matched | ratio CI ⊄ [1/1.3, 1.3] | **DISAGREES ×5 (excess ratio 5.04 [3.97, 6.19]) — first ladder rung run**: Q_XI-off probe (matched_t1.json `_qxi_off_probe`) localizes the straight BASELINE (agrees to 12%: 2.29e-3 vs 2.05e-3) and leaves the maneuvering-excess ratio 7.2, attributed to inertia-free shape response; remaining §6 ladder rungs (cable A/B, hydro sensitivity, frozen regressions) pending; validity-domain finding (Drake realized shapes exit reduced model's domain) | matched_drake/matched_t1.json |
| C9b′ | amplitude ε-exponent 1 | 1 ∉ CI | **PASSED** (1.006; base commutator exactly zero) | e3c_symmetry.json, F5(a) |
| C9b | D_ss excess ε-exponent 2 | 2 ∉ CI | **falsifier condition MET on the declared (seed-paired) estimator**: 1.58 [1.44, 1.84] at every τ — 2 excluded (and 1 excluded); the registered single-power model is mis-specified for the evident linear+quadratic mixture (exploratory note: segment slopes rise 1.2→2.1; the R3 artifact class, here on the ε-axis). The unpaired estimator [0.43, 2.89] is UNDER-POWERED per the §1 convention (half-width 1.23 ≫ 0.2) and adjudicates nothing | e3c_c9b_seeds.json (`_paired_estimator`), F5(b) |
| C9c | robust symmetric suppression ≥ 10× at τ=0.4 | S < 10× | **TRIPS on Tier-1** (robust arm: 2.75× [1.94, 3.89], jitter 20% + drops 10%). Drake comparator: 2.1× is the UNIFORM D4 fan/parallel ratio (no Drake robust arm exists yet). The ≥10× protection is an amplitude-object property only | e3c_robust.json; production_d2_d4_v2 (D4, uniform) |
| C9a | full-cycle symmetric amplitude slope 3 | — | **Q3-BLOCKED** (α_k unresolved; never guessed) | author decision pending |
| C18 | conjugated transport load-bearing | A2 ≈ paper rule | **PASSED on Drake** (A2 1.7→8.2× worse with τ); **ordering INVERTS on Tier-1** (regime-dependent; D_ss never ranks rules — definitive ranking awaits D7, which is PENDING §4) | d2_a1_a2_arms.json, F4c |
| C10 | topology dependence (open) | none (exploratory) | connectivity suppresses the floor at moderate τ (5×), benefit collapses at high τ (≤2×); complete graphs most τ-sensitive | e6_topology.json |
| M-FAB / D1 | filter consistency | ANEES ∉ gate | **closed under the author-ruled [0.8, 5.0] gate** (3.96); complement sanity ≤1.3 **FAILED** (3.35) — disclosed wherever M-FAB is cited; filter ~3–4× optimistic (CI structural) | s1_verdict.json |
| E10 / D8 | numerics invariance | exponent CIs disjoint across Δt / h | **PASSED both plants** (Δt 10× range: CIs share [1.185, 1.256]; h: identical to 3 decimals, convergence verified genuine by truth-diff 1.35 mm, recorded in d8_h_sweep.json `_truth_diff_check`) | e10_dt_sweep.json, d8_h_sweep.json |

**Epistemic spine (three measured exponents, three objects, never conflated):**
state-level transport mismatch, measured slope 1.00 → closed-loop D_ss, measured
slopes 1.08–1.10 on both plants (CONJ regime; a fitted mixture slope carried with
the R3 caveat, asserted as no law — the CIs exclude both 1 and 2) →
error-transport holonomy slope 2.00 on both plants (PROV, the theorem's object,
resolved only noise-off).

## 2. Figure inventory

| Figure | File | Status |
|---|---|---|
| Hero movie (dogleg, 5 beats, hedge on-plot, honest scorecard) | tier2_drake/results/s1/hero_dogleg.mp4 (+_web) | done (v1 — lacks the §4 Hero-v2 items: decelerating approach, comms jitter/drops, tension coloring, λ₂ panel) |
| Gauge-pinning demo movie + montage | hero_blind_harbor.mp4, hero_montage.png | done |
| F4a-overlay (PROV panel) | tier2_drake/results/s1/f4a_overlay.png/pdf | done |
| F4b-overlay (CONJ panel + equivalence box) | f4b_overlay.png/pdf | done |
| F4c variance attribution | f4c_variance_attribution.png/pdf | done |
| F4 cross-tier ladder overlay | f4_cross_tier_overlay.png/pdf | done |
| F5 symmetry (two panels, never mixed) | tier1_sheaf/results/f5_symmetry.png/pdf | done |
| F8 contraction | tier1_sheaf/results/f8_contraction.png/pdf | done |
| F3 gauge spectrum (executed earlier) | tier1_sheaf/results/e1_gauge.png | done |
| Baselines table | gallery §4 / baselines.json | done (B1-true/B3 pending D7) |
| Gallery (all of the above, hedged captions) | claude.ai artifact c684d82f… | published |

## 3. Reproducibility manifest (cell → driver → data)

| Cell | Driver | Data |
|---|---|---|
| T1-E3a | tier1_sheaf/experiments/e3a_amplitude.py | results/e3a_amplitude.csv |
| T1-E3b | tier1_sheaf/experiments/e3b_floor.py + tier1_sheaf/campaign/e3b_production.py | results/e3b_production.json |
| T1-E3c | tier1_sheaf/experiments/e3c_symmetry.py (+ tier1_sheaf/campaign/e3c_c9b_v2.py) | e3c_symmetry.json, e3c_c9b_seeds.json, e3c_robust.json |
| T1-E2 | tier1_sheaf/experiments/e2_contraction.py | e2_contraction.json |
| T1-E6 | tier1_sheaf/campaign/e6_topology.py | e6_topology.json |
| T1-E10 | tier1_sheaf/campaign/e10_dt_sweep.py | e10_dt_sweep.json |
| D2 + controls | tier2_drake/campaign/{production_d2_d4,d2_controls,d2_tau005,d2_arms}.py | production_d2_d4_v2.json, d2_straight_control.json, d2_tau005.json, d2_a1_a2_arms.json |
| D3 | tier2_drake/blind_harbor/d3_amplitude.py | d3_amplitude.json |
| D5 / hero | tier2_drake/blind_harbor/hero.py, hero_dogleg.py | hero_*.mp4/npz, hero_ensemble.json |
| D8 | tier2_drake/campaign/d8_h_sweep.py | d8_h_sweep.json |
| §6 matched | tier2_drake/campaign/{matched_drake,matched_t1}.py | matched_drake.json, matched_t1.json |
| Baselines | tier2_drake/campaign/{baselines,b1_true}.py | baselines.json, b1_true.json |

All drivers are versioned in campaign/ directories (rescued from the session
scratchpad per the package audit) and seeded; formation draws are id-keyed; the E3b/E2 harnesses carry
P-class asserts (realized age ≡ τ) that gate off only in the declared robust arms.

## 4. Known scope reductions and open items

- **Author decisions pending:** Q3 (α_k table → C9a and m∈{3,4} E3a extension),
  Q11 ([PUB] factual corrections), Q15 (E4/E5 landing site), QD-gate ratifications.
- **D7 full scorecard** (50 transits, docking metrics, true B1 joint EKF, B3
  relative-pose DInEKF) — design notes recorded from the B1-lite negative result
  (naive centralization loses 2.2× to the record) and the B3 architecture sketch.
- **Hero v2:** decelerating approach (extends beacon window physically),
  jitter/drop comms in the Drake fabric (Tier-1 harness already has them),
  tension-colored cables, online λ₂ panel.
- **E3a extension remainder** (§4.0 items i–v, vii): m>2 walks (Q3-gated),
  ≥12-formation draws for the amplitude cluster bootstrap, sup remainder
  constant, M8/C8b frustration, C15 zero-commutator, explicit τ=0 arm.
- **Metric module unification:** the all-pairs D implementation exists in two
  verified-equal inline copies (s1.py, e3b_floor.py); factor into analysis/metrics.py.
- **L-CSS letter:** E3a package is submission-ready (Q12 satisfied).

## 5. The honest narrative (committed, plan §10 R2)

The amplitude holds (both plants, coefficient and switch-offs). The order-2
conjecture for the closed-loop floor is falsified at these scales on both plants;
the measured slope (≈ 1.05–1.13, cross-tier equivalent) is reported as measured,
with the D₀/mixture caveat (plan R3), and asserted as no law. Transport
compensation is load-bearing on Drake where correctness is measured; the ablation
ordering inverts on Tier-1, and definitive rule ranking awaits the pending D7
scorecard. Agreement alone is purchasable by groupthink and is never a virtue
metric. Every pre-registered negative result is controlled and, where its
localization ladder has completed, localized (the ×5 coefficient disagreement has
one rung run; C10's high-τ structure is exploratory, not pre-registered). No
claim needs retraction — captions were CONJ from the start.
