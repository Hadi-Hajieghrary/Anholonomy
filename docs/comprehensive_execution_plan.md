# Comprehensive Execution Plan — Tier-1 Completion + DIEKF-Σ in the Drake Loop
## One estimator, two plants, three papers: the unified campaign for T-CNS §VIII (Tier-1) and the RA-L/ICRA Blind Harbor companion

**Version 1.0 — 2026-07-17.**
Supersedes nothing; *executes* `refs/tier1_simulation_plan_v2.md` (binding for Tier-1 protocol) and
`refs/blind_harbor_drake_simulation_plan.md` (binding for Drake platform design), with the deltas
recorded here. Labels: **[HAVE]** built and green, **[SPEC]** fixed by a source document (cited),
**[DESIGN]** a choice made here and disclosed, **[GAP]** open work or an open author decision.

**The ask this plan answers** (author, verbatim intent): complete Tier-1 *and* put the DIEKF-Σ
estimator in the Drake loop; "the simulation and the results should demonstrate the very extreme
capability of the proposed theorem in most realistic scenarios with best presentable results and
artifacts for a prestigious publication." **Interpretation, binding:** ambition is spent on scenario
realism, statistical rigor, and presentation quality — never on claim inflation. The epistemic
contract (§1) is the program's #1 integrity rule and is machine-enforced (§3.6, §7.4).

---

## 0. Executive summary and honest inventory

### 0.1 The one-paragraph plan

Extract the DIEKF-Σ into a plant-agnostic pure-NumPy package (`estimator_core/`, zero Drake
imports) consumed by **both** the Tier-1 reduced Lie-group plant and a thin Drake `LeafSystem`
adapter — *same code, two plants*. Complete the four remaining Tier-1 cells (T1-E2 contraction,
T1-E3b dynamic floor **with moving shapes**, T1-E3c symmetry, T1-E6 topology) under plan-v2's
binding statistics protocol. Build the Drake closed loop on the existing green pentagon-caisson
platform (sensors, comms fabric with latency/jitter/drop, estimator LeafSystems, truth-isolation
lint) and run the closed-loop campaign D1–D10, whose scientific heart is the **executed null
result**: at frozen shapes the paper's fusion rule reconstructs the neighbor twist exactly
(D_ss ≈ 1e-29), so the conjectured stochastic floor exists **only** under shape motion × curvature
× latency — precisely the regime the Drake plant reaches natively during maneuvers. The capstone is
the cross-tier overlay (amplitude PROV panel + D_ss CONJ panel, one shared analysis module, two
independent plants) — the pre-registered kill of reviewer attack R9 ("your floor is a
discretization artifact"). The showcase is the Blind Harbor Transit hero movie: five vessels, one
2 500 kg caisson, no GPS, acoustic latency, docking at < 0.5 m — every dramatic beat a labeled
theorem, every caption carrying its hedge verbatim.

### 0.2 What already exists — executed numbers (do not rebuild; do not re-run to "confirm")

**[HAVE] `tier1_sheaf/` (25 tests green).**

| Asset | Executed result |
|---|---|
| `core/se2.py` | Exp/Log/Ad/ad, V3 convention `Jt = (t_y, −t_x)`; mutually consistent with the SymPy manifest |
| `core/shapes.py` | `m(s)`, `Ad_m`, conjugated generator `C_j(s_j; ξ)` |
| `sheaf/laplacian.py` | `L_F`, `λ₂` with kernel-tolerance selector (fixes the `eigvalsh[3]` pinning bug); weight convention configurable `series/harmonic/uniform` — the Q6a 2× ambiguity is an explicit switch |
| `sheaf/gauge.py`, `sheaf/holonomy.py` | kernel basis + first-order alignment; leading amplitude + full expm/logm error-transport holonomy at m = 2 |
| `symbolic/manifest.py` | V1–V6 as **real pytest asserts** (the original `verify_sheaf.py` had zero asserts) |
| **T1-E3a EXECUTED** | generic amplitude slope **1.999**; symmetric / η=0 / ξ=0 all **machine zero** (every free switch-off holds); C8 coefficient ratio **1.0000** at m = 2. F4a produced. |
| **T1-E1 (spectral half) EXECUTED** | dim ker L_F = **3**; kernel = gauge sections to **1.3e-15**; pinning collapses kernel to 0 and `λ_min` becomes the rate. F3 produced. |
| **CRITICAL NULL (executed)** | At **frozen shapes** the paper's fusion rule (`sim_design.tex:54` conjugated fast-forward) reconstructs the neighbor's twist **exactly**: D_ss ≈ **1e-29** (machine zero). The closed-loop floor arises **only** from stale shape estimates `ŝ` inside `Ad_{m(ŝ)}` under shape motion, noise, and lag heterogeneity. |
| Pilot forensics | `pilot_e3.py` arm labels **inverted**: its "generic" (slope 2.01) = ablation **A2**; its "lag-compensated" = the paper's rule; symmetric slope 1.59 = pure noise floor. CSV kept as a determinism fixture only, relabeled. |

**[HAVE] `tier2_drake/` (8 tests green, Drake 1.51.1 pinned).**

| Asset | Executed result |
|---|---|
| `harbor.py` | Config-driven discrete MultibodyPlant (SAP, h = 1 ms); pentagon caisson (circumradius 4 m, 2 500 kg, bow vertex forward, SolidCylinder inertia proxy, front-edge attachments via ray-polygon intersection; `load_shape="box"` restores a barge); N ASVs as PlanarJoint boxes; N cables as `AddDistanceConstraint` (taut to ~1e-8 m); `TowController` (drag + ramped thrust, per-vessel `thrust_scale` for genuine persistent asymmetry) |
| `run.py` | Analytic `TensionObserver` `λ = −(J M⁻¹ Jᵀ)⁻¹ [J̇v + J M⁻¹ (τ − Cv)]` from documented plant queries only |
| `render.py` | Top-down animations + comparison figure |
| **Executed transits** | N=4: 141 m @ **2.56 kN**/cable; N=5: 162 m @ **2.35 kN**; unequal thrust (1.3, 1.1, 0.9, 0.7) → **94 % tension spread**, **+21°** load yaw |

**[HAVE] Two published galleries** (Tier-1 results; Drake pentagon towing).

**[GAP] Everything else:** Tier-1 shape ODEs + reduced plant with noise, the DIEKF-Σ itself
(update, covariance, CI, weights — *nothing exists in either tier*), comms fabric, sensors,
shared analysis module, all of D1–D10, the overlay, the hero movie.

### 0.3 Why the Drake loop is the decisive experiment, not a demo

The executed frozen-shape null converts the program's logic. Thm 7.2 (PROV) is a statement about
leading-order **deterministic transport holonomy** — testable by pure transport computation
(T1-E3a, executed) and by logged applied transports in closed loop (D3, new). The **stochastic
steady-state floor D_ss is CONJ** and, per the null, is excited only when shapes genuinely move
during latency — i.e., in maneuvers. The Drake closed loop, where shapes evolve because five real
hulls drag a caisson through a turn, is therefore the conjecture's home turf, and the straight-line
/ frozen-shape arms are the in-plant switch-offs that bracket it from below. Every floor cell in
both tiers **must** use maneuvering trajectories; every straight/frozen arm is a control, not a
failure.

---

## 1. The claims contract (binding; inherited from plan-v2 §2, compressed)

| Object | τ-order | ε-order | Status | May be claimed as… |
|---|---|---|---|---|
| Holonomy amplitude `‖Log Hol‖` (M5) | **O(τ²)** | ε¹ | **PROV** — Thm 7.2 [thm:floor], *leading order, deterministic* | "slope 2 confirms the leading-order holonomy amplitude of Thm 7.2 within its stated hypotheses" |
| Symmetric amplitude | **O(τ³)** | — | **PROV** — Cor 7.3 [cor:sym] | "one order of protection" — never "floor eliminated" |
| Dynamic steady state `D_ss` / `E_F` (M4) | O(τ²) *claimed* | ε² | **CONJ** — balance heuristic, [ES §10(ii)] | **Only**: *"numerical evidence for the conjectured stochastic steady-state floor ([ES §10(ii)])."* **NEVER "validates Thm 7.2."** |
| Frustration `η_c ≍ (1/m)‖Log Hol‖²` (M8) | O(τ⁴) | ε² | EST (imported BSS) / constant CONJ | scaling only; `≍`, never `=` |
| Amplitude coefficient vs `C_hol` | — | — | PROV **at m = 2 only** (Lem 7.1; `α_k` absent from [ES] for m > 2) | ratio `Ĉ/C_hol` at m = 2; scaling + sim-derived `α_k` for m > 2, flagged |
| Contraction rate `μ + κλ₂ − c_A` | — | — | **PROV LTV/frozen only**; nonlinear CONJ; **AUDIT ES-01**: μ and κλ₂ act on **different subspaces** — the additive rate needs that qualification, stated verbatim wherever Thm 6.3 is cited | frozen cells; an **inequality** (rate ≥ bound); slope-in-κλ₂ is the tested prediction (μ is calibrated at κ = 0 and disclosed as fitted) |
| Fused-flow group-affinity | — | — | PROV 1st order; exact CONJ (Lem 6.2) | bound the departure (C19); never assert exactness |
| Gauge kernel = se(2); pinning | — | — | **PROV** (Thm 5.1, Cor 5.2) | validation language permitted |
| Broadside `λ₂ → 0` | — | — | PROV inheritance; **monotone CONJ** (Cor 5.3) | exhibit the curve; "consistent with the conjectured monotone dependence", never "proves" |
| Force channel; Fisher rate ∝ v² | — | — | PROV **under A10** (a modelling choice, named in caption) | yes, with A10 named; never "first use of tension" |
| Robust symmetric suppression | — | — | **DESIGN** (C9c) | **"≥ 10×, one-sided; magnitude reported, not bounded above."** The ~400× figure is an ideal-case artifact of chosen σ — reference-line label only, never a headline |
| Near-symmetric scalings | — | ε¹ (amplitude), ε² (D_ss) | NEW (plan-derived from §6.5) | "measured scalings consistent with the leading-order structure"; the two exponents must hold **jointly**, never mixed in one panel |
| Maupertuis / information wells (E4/E5) | — | — | **DEFERRED out of this cycle** (Q10 amended; landing site = Q15) | §VII carries pointers; Thm 8.1 presented proved-but-unillustrated; **no D-cell here executes them** — [PUB] F7 is cut from the flagship set and `fig6_landscape.png` is banned from reuse until re-run (Q15) |

**The caption rule.** Every figure/movie caption naming a theorem states the theorem's hedge
**verbatim**. Every CONJ-probing artifact says "conjectured" in the caption. §VIII prose mirrors
the table. **Mechanical enforcement (§3.6):** all hedge strings live in one `analysis/captions.py`
CaptionRegistry; figure and movie builders may obtain theorem references only through it; a CI test
checks every emitted caption/annotation and **fails the build** if (a) any token matching the stem
regex `validat\w*` (validate/validates/validated/validation/validating…) occurs in the **same
sentence** as "Thm 7.2"/"Theorem 7.2" on any D_ss/E_F-tagged artifact — a stem match over a
sentence window, not a fixed-word radius; (b) any theorem mention lacks its registered hedge
(for Thm 7.2 that hedge is **"leading-order, deterministic" in full** — [ES] line 196); or (c) any
sentence naming a theorem is not **byte-identical** to a CaptionRegistry literal (registry-identity
check — paraphrase loopholes closed by construction). A **lint self-test** runs the lint over every
caption literal mandated in this plan (checked in as fixtures), so the enforcement instrument and
the mandated text can never contradict each other. *(Memory note honored: Thm 7.2 is
leading-order/deterministic; D_ss is CONJ; a D_ss fit is never captioned as validating the
theorem.)*

**Falsifier/acceptance convention [SPEC, plan-v2 §3], uniform across both tiers:** predicted
exponent **∉ CI ⇒ falsified**; **∈ CI and CI half-width < 0.2 ⇒ accepted**; anything else
**UNDER-POWERED — reported with the CI and the systematic budget, never silently passed.**

---

## 2. Publication routing table

Three-unit split is **FIXED**: (i) **L-CSS letter** = floor-theorem priority stamp; (ii) **IEEE
T-CNS flagship** = framework paper, §VIII numerics **Tier-1 ONLY** (the pre-registered R9
defense); (iii) **RA-L/ICRA companion** = DIEKF-Σ implementation + Blind Harbor campaign on Drake.
Routing is enforced in tooling: every figure/movie manifest carries a target tag
`{LCSS | TCNS-SVIII | TCNS-supp | RAL}`; `analysis/figures.py` **refuses** to emit a
TCNS-SVIII-tagged artifact from Tier-2 primary data.

| Artifact (experiment → figure/movie) | LCSS | TCNS §VIII | TCNS supp | RA-L primary |
|---|---|---|---|---|
| T1-E3a amplitude log-log + C8 ratio (**executed**) | **headline** | F4a | | |
| T1-E9 switch-off table (C13) + T1-E10 Δt-sweep (C14) | inset | **main text** (pre-committed defenses stay out of supplementary; **Tier-1 rows only** — §7.3's rendition rule strips the Drake row mechanically) | | |
| T1-E3b `D_ss` (moving shapes, CONJ) | | F4b | | |
| T1-E3c symmetry (uniform + robust arms) | | F5 | | |
| T1-E1 gauge/pinning + C17 ANEES + C18 B2 | | F3, F8 | C18 detail | |
| T1-E2 contraction (subspace-resolved) + C19 | | F8 | C19 | |
| T1-E6 topology sweep (C10, exploratory) | | F4b overlay | detail | |
| C8b frustration scalings; C15 zero-commutator detail; sup R/τ³ remainder constant | | | yes | |
| D1 consistency/ANEES; D5 gauge snap; D6 tension dose-response; D7 baselines + BHT scorecard; D9 scaling; D10 robustness | | | | **all** |
| D2 closed-loop floor (CONJ) + "no motion, no floor" mechanism figure | | | | yes |
| D3 measured holonomy amplitude in closed loop (PROV) | | | forward pointer | yes |
| D4 symmetry suppression split-screen | | | | yes |
| **XT cross-tier overlay** (F4a-overlay PROV + F4b-overlay CONJ) + Drake h-sweep (D8) | | | **yes + forward pointer** | **centerpiece** |
| Hero movie (BHT), set-piece movies, Meshcat HTML, gallery 3 | | | 30 s cut + pointer | **video suite** |

**Rules.** (1) The flagship §VIII contains no Drake-primary evidence, ever. (2) The Drake closed
loop feeds the flagship only as supplementary + forward pointer. (3) The L-CSS letter's headline
(C7a) is already supported by executed E3a numbers (slope 1.999, switch-offs, coefficient 1.0000)
— the one-week check plan-v2's Q12 demanded is **done**; Q12 is resolved (§11).

---

## 3. Architecture: one estimator, two plants, one analysis

### 3.1 The mandated structure

```
Anholonomy/
  estimator_core/            # NEW — pure NumPy, ZERO Drake imports, the ONE DIEKF-Σ
    state.py                 #   FilterState: G (3,3), s (2,), P (5,5), per-neighbor stamps
    propagate.py             #   (P) 50 Hz: ζ̂ from odometry → ξ̂ = Ad_{m(ŝ)} ζ̂ → G Exp(Δt ξ̂); P log-linear Jacobian per [ES] Def 6.1(a) (group-affine block exact, EST — Lem 6.2 is about FUSION and is cited only on fuse.py)
    update.py                #   (U) 20 Hz: vM direction (κ = c T²/r₀, A10) + magnitude; IEKF gain, Fisher weight; broadside guard: clip gain when cos σ̂ < 0.1 (Cor 5.3)
    fuse.py                  #   (F): G̃ = Ĝ_{j'}(t−τ) Exp(τ Ad_{m(ŝ_{j'})⁻¹ m(ŝ_j)} ζ̂_j); r = Log(Ĝ_j⁻¹ G̃); G ← G Exp(α w_e r), α = κΔ_c (κ = 2; Δ_c INJECTED by the harness — 0.05 s Tier-1 theory cells, 0.1 s Drake — never a literal; load-time assert α = κ·send_epoch); 1st-order log-linearity preserved per Lem 6.2 (exact group-affinity of the fused flow: CONJ); CI ω = argmin tr; RETURNS a FusionRecord logging the APPLIED TRANSPORT (this is what makes D3/M5 measurable in closed loop)
    weights.py               #   ι_j, w_e = SERIES information (1/ι_i + 1/ι_j)⁻¹ — Def 4.1, pinned (§11 Q6a)
    rules.py                 #   fuse_rule registry: paper | A1 (no lag comp) | A2 (un-conjugated) | A3 (w_e≡1) | b2 (identity edge maps) | oosm_augmented (outside-class demarcation arm, plan-v2 §8.0b)
    gauge.py                 #   kernel-basis transport (wraps tier1_sheaf.sheaf.gauge). h* SE(2) argmin alignment is [GAP] NEW CODE — tier1_sheaf ships only gauge_align_firstorder (its docstring defers the argmin): 3-parameter Gauss–Newton over SE(2) on the alignment window (~0.5 day + tests); acceptance pre-registered: first-order and exact agree within 1 % at D1/D5 error magnitudes, and exact is MANDATORY whenever kernel-projected drift > 0.1 rad (where first-order breaks)
    packets.py               #   fixed-width packet: [stamp, sender, vec(G) 9, vech(P) 15, ŝ 2, valid] = 29 floats
    tests/                   #   group-affinity 1st-order check; FROZEN-SHAPE EXACTNESS regression (paper rule + frozen shapes ⇒ D_ss < 1e-25 — pins the executed null); A2 SIGNATURE PIN (A2 reproduces the pilot's slope-2.01 diagnostic — the label-inversion vaccine); CI ω sanity
  analysis/                  # NEW — shared by BOTH tiers; consumes parquet only
    metrics.py               #   M4 in COBOUNDARY form ≡ Tier-2 E_F: D(t) = Σ_e w_e‖ρ_{i◁e}x̂_i − ρ_{j◁e}x̂_j‖², ρ_j = Ad_{m(ŝ_j)}π_L  (plan-v2 §8.0e — the §VI object); M5 from FusionRecords; M1–M3, M6, M8 (lagged coboundary + gauge min)
    windows.py               #   ONE window rule: turn-containing segment |η_ref| ≥ η_min (0.05 rad/s), post-transient, last 30 %; alignment window DISJOINT from evaluation (first 20 % / last 30 %)
    fits.py                  #   pre-registered D_ss model D₀ + C·τ^p (§8.2); WLS on log-means; cluster bootstrap over FORMATIONS (2000); Holm–Bonferroni per family; three-outcome verdicts
    captions.py              #   CaptionRegistry — the only source of theorem text; hedges as literals; forbidden-collocation lint
    style.py                 #   Okabe-Ito agent palette (N ≤ 8), viridis tension fixed 0–3 kN, one rcParams block, vector PDF; both papers visually one system
    figures.py               #   tier tags + routing enforcement; every figure regenerable from parquet + manifest
  tier1_sheaf/               # [HAVE] + additions
    plant/                   #   NEW: reduced integrator — Crouch–Grossman Lie–Euler for g_L, RK4 for shape ODEs (sim_design.tex:25–33), Δt = 0.01 s (E10 sweeps it); Euler–Maruyama √(QΔt) noise (plan-v2 §6.8); quasistatic tension + BINDING TautCertificate
    harness/                 #   NEW: drives estimator_core against the reduced plant (50/20 Hz cadence, Δ_c = 0.05 s theory cells — QD5 delta from plan-v2 §8.0c's 0.025 s, see §3.3); per-edge lag buffers, jitter/loss for robust arms; protocol-class 𝒫 assertion
    experiments/             #   e2.py, e3b.py, e3c.py, e6.py, e10.py (+ existing e1, e3a extended)
    configs/                 #   one YAML per cell
  tier2_drake/               # [HAVE] + additions (extend, don't rewrite what is green)
    blind_harbor/
      config.py              #   frozen dataclasses → YAML → SHA-256 into manifest; taut-feasibility QP at load; --dry-run prints Graphviz + exits
      world/                 #   harbor.py (existing builder, extended: dogleg corridor geometry, current/gust field, waypoint spline)
      agents/sensors.py      #   §5.2 suite; one vectorized SensorSuite LeafSystem per agent
      agents/diekf_leaf.py   #   DIEKFSigmaLeaf — THIN adapter, < 100 lines, ports in/out only, ZERO algorithm code (imports estimator_core); one discrete state group: vec(G) 9 + ŝ 2 + vech(P) 15 + deg(i) stamps
      agents/controller.py   #   PD in log-coordinates on the agent's OWN estimate + feedforward; use_truth switch for paired ablations only. REFACTOR: harbor.py's TowController splits into HydroDrag (physics, plant-side, legitimately reads plant state — lint-exempt BY CLASS) + this estimate-driven Controller
      agents/baselines.py    #   B0 dead-reckon | B1 centralized oracle | B2 naive consensus (identity edge maps) | B3 synthetic relative-pose DInEKF (1 Hz, 0.1 m/1°) — same LeafSystem interface, config-selected. RECORDED DELTA from sim_design §Baselines: B4 (shared-scalar [IK, Thm C]) and B5 (shortest-path planner) are DROPPED this cycle — B5 ablates the Maupertuis planner (out of scope with E4/E5, Q15) and B4 requires broadcast, violating the decentralization premise under test; both revisit with E4/E5's landing unit (Q15)
      comms/                 #   VectorRingDelay (own small ring-buffer LeafSystem — do NOT bet on DiscreteTimeDelay API; ring spans max delay + max jitter: 160 + 10 slots at τ = 1.6 s); DropGate AFTER the delay (erasure at reception); PacketSerializer; per-packet integer jitter draws at send. Slot-collision policy PRE-REGISTERED: keep-newest-stamp on collision, overwrites counted as drops in the manifest, zero collisions ASSERTED in 𝒫 cells (jitter = 0 there, so the assert is free)
      runtime/monitors.py    #   TensionObserver (factored from run.py), TautCertificate (BINDING), EnergyAudit, truth-isolation lint (walks the built Diagram: no estimator/controller input connects to any plant output)
      viz/anim2d.py          #   guaranteed matplotlib+ffmpeg movie path, parquet-driven; meshcat_html.py StaticHtml supplementary
      scenarios/             #   one YAML per cell (S1-hero … per §5.4)
      experiments/runner.py  #   multiprocessing.Pool, one build+run per worker, plain-data configs across the boundary; runs/<scenario>/<confighash>/<seed>/
```

### 3.2 Why sharing the estimator strengthens, not weakens, the overlay [DESIGN, decided]

The panel conflict is resolved as follows. The attack under defense (R9) is *"the floor is a
plant/discretization artifact"* — so **plant independence is the load-bearing independence**:
integrators (Crouch–Grossman + RK4 vs SAP discrete solver), constraint handling (exact reduced
coordinates vs distance constraints), tension recovery (quasistatic balance vs TensionObserver),
and shape evolution (shape ODEs vs full multibody) are fully independent and **never shared**.
Sharing the estimator, the metric functional, the window rules, and the fit code **removes the
implementation-difference confound**: cross-tier agreement becomes a statement about *the
algorithm on two plants*, and any disagreement localizes to the plant — exactly the object R9
disputes. This line appears verbatim in both papers. Plan-v2 §10.4's "do not share estimator
implementations" is **amended** by this plan (recorded as a delta): its purpose (independence
where it matters) is preserved by the plant-independence line, and the within-tier artifact
defenses (T1-E10, Drake h-sweep, cable A/B differencing, TensionObserver ≤ 1 % cross-check)
require no independence argument at all.

### 3.3 Rates, scheduling, determinism [SPEC + DESIGN]

| Process | Tier-1 | Tier-2 (Drake) | Source |
|---|---|---|---|
| Plant step | Δt = 0.01 s (E10 sweeps {0.001, 0.0025, 0.005, 0.01} — 0.02 dropped, QD5: it divides neither the 50 ms update period nor Δ_c; 0.001 added as the refinement point) | h = 1 ms (D8 sweeps {0.25, 0.5, 1, 2} ms) | sim_design.tex:33; Drake plan §6; QD5 |
| Estimator propagate | **50 Hz** (Δt_filt = 0.02 s) | **50 Hz**, offset 0 | DIEKF spec; audit XCON-05: filter dt ≠ plant dt, **asserted in code as an integer step ratio** |
| Measurement update | 20 Hz | 20 Hz, offset 10 ms (integer multiple of h; avoids alignment with fusion) | sim_design.tex:40–41 |
| Fusion send epoch | **Δ_c = 0.05 s** (theory cells; τ grid {0.05 … 1.6} stays exact with lag ∈ {1 … 32} ≥ 1. **QD5 delta from plan-v2 §8.0c's 0.025 s**, which violates plan-v2's own load invariant: 0.025/0.01 = 2.5) | Δ_c = 0.1 s sends; delay quantum T_c = 10 ms | sim_design.tex:46 (Drake); QD5 (Tier-1) |
| **Fusion consume** | on the Δ_c grid (synchronous) | **dedicated 100 Hz (T_c-grid) poll event on DIEKFSigmaLeaf** — consumption coincides with every possible arrival instant, so odd-k delays (e.g. τ = 0.05 s) are never aliased onto the 20 ms propagate grid (+20 % age error at the smallest τ otherwise) | [DESIGN] — closes the realized-age gap |
| Fusion gain | α = κΔ_c, κ = 2 (⇒ 0.1 at Δ_c = 0.05) | α = κΔ_c = 0.2 (κ = 2, Δ_c = 0.1) | sim_design.tex:57 — α is **derived**, never a literal; load-time assert α = κ·send_epoch |
| τ realization | per-edge lag buffers; assert τ_e exact multiple of Δ_c, lag ≥ 1 | τ_e = k·T_c, k ∈ ℕ; stamps ride in-packet; the logged **realized age is the fit regressor** (§5.2) and realized ≡ nominal τ is asserted per fuse event inside protocol class 𝒫 | plan-v2 §8.0c; Drake plan §5.3 |
| Controller | (reference-driven shape controller, sim_design.tex:61) | 50 Hz | |
| Loggers / movie frames | signal-native / 30 fps | signal-native / 30 fps | |

**Determinism contract (both tiers, CI-blocking):** one master seed →
`numpy.random.SeedSequence.spawn()` keyed by `(run_seed, system_name)`; RNGs live inside systems
and advance only in periodic events; no wall-clock, no threads in-run; two runs at same
`(config, seed)` produce **bit-identical parquet**. All periods are asserted integer multiples of
the plant step at config load.

**Truth isolation is a test, not a convention:** the lint walks the built Diagram and fails if any
estimator/controller input port connects to a plant output port. Two principled exemptions, both
mechanical, neither editorial: (i) systems classified plant-side **by class** (HydroDrag — physics,
not control; the TowController refactor of §3.1); (ii) a config-declared exemption set keyed to arm
id (`b1` centralized oracle, `use_truth` paired ablations) — and the lint **asserts the exemption
set is empty in every GNSS-denied/theory cell**, so the hero claim stays enforced. This is what
makes "GNSS-denied" an enforced property.

### 3.4 Sensor suite (Tier-2 default; GNSS-denied by construction) [SPEC: sim_design.tex:36–43]

| Channel | Rate | Model | Parameters |
|---|---|---|---|
| Odometry, surge (+sway) | 50 Hz | `ṽ = v(1+β) + n` | n ~ N(0, (0.01+0.02v)²), bias β ~ N(0, 0.01²) fixed/run |
| Gyro | 50 Hz | `ω̃ = ω + b + n` | n ~ N(0, (0.2°/s)²), ḃ RW 0.01°/s/√s |
| Tension magnitude | 20 Hz | `T̃ = T + n` | n ~ N(0, (0.5+0.02T)²) N; truth from TensionObserver |
| Tension direction | 20 Hz | `σ̃ ~ vM(σ, κ)` | κ = c T²/r₀ (A10); **c calibrated at Drake-scale tensions ~2.5 kN — §11 QD3** |
| Docking beacon | 5 Hz, **last 30 m only** | full pose | N(0, diag(0.05², 0.05², (0.5°)²)) |
| Cable angle (optional) | 20 Hz | body-frame departure angle | σ_α; **off by default**; INIT-1 contingency only, documented in both papers if promoted |
| Synthetic relative pose (**B3 baseline only**) | 1 Hz | relative SE(2) | σ = (0.1 m, 1°) |

**Correction to Drake plan §4.1 [DESIGN, binding]:** the default suite contains **no relative
range–bearing sensor**. `sim_design.tex:19` defines BHT by "each vessel senses only (i) its own
odometry … and (ii) its own cable channel", and the novelty argument (":21") rests on relative-pose
sensing being *absent*. Range–bearing exists only as B3's granted synthetic sensor.

### 3.5 Config schema [DESIGN]

One YAML per cell; frozen dataclasses; SHA-256 of canonical serialization + seed + drake/git
versions + TautCertificate verdict + exclusion counts in every run manifest.

```yaml
# scenarios/D2_floor_primary.yaml (one grid point; sweeps.py expands)
formation: {type: pentagon_front_arc, n: 5, draw: {mode: random, support: taut_admissible_K, margin_rad: 0.10, on_reject: resample},
            epsilon: 0.0, epsilon_dir: {agent: 2, vec: [0.8321, 0.5547]}}   # ‖Dc·d‖ > 0 asserted at load
graph:     {type: cycle, tau_s: 0.4, jitter_frac: 0.0, drop_prob: 0.0}     # theory cell: uniform τ asserted (protocol class P)
trajectory:{type: persistent_turn, eta_ref: {bias: 0.15, amp: 0.10, freq_rads: 0.05}, v_ref: 0.8}  # |η| ∈ [0.05, 0.25], never vanishing (plan-v2 §9.1)
rates:     {plant_h: 1.0e-3, propagate_hz: 50, update_hz: 20, send_epoch_s: 0.1, consume_hz: 100, delay_quantum_s: 0.01}
geometry:  {cable_len_m: 12.0}       # l — REQUIRED, no default (sim_design.tex:24; harbor.py cable_len)
estimator: {type: diekf_sigma, fuse_rule: paper, covariance: ci, weights: series}
noise:     {profile: nominal}        # named profile (plan-v2 §5.1a); 'off' for deterministic arms
arm:       {id: primary}             # primary|dogleg|straight|frozen_replay|A1|A2|noise_off — arm id travels in the config hash, never in a free-text label
seed:      1234
```

**Cable length is load-bearing and has no default.** The audit (plan-v2 Q6/§4.3) established that
every spectral/weight/holonomy quantity is l-dependent; `tier1_sheaf`'s `DEFAULT_L = 1.0` exists
for unit-level algebra only (its own docstring says so), while production runs at l = 12 m
(sim_design.tex:24; `harbor.py` `cable_len = 12.0`). Therefore l is a **required kwarg** through
`estimator_core` and `analysis` (FilterState and metrics constructors take it), and CI asserts no
production path reaches a `tier1_sheaf` call via the default (sentinel raises).

### 3.6 Integrity instruments (both tiers, binding)

1. **TautCertificate:** `min_k T_k(t) < 5 N` flags the run; any theorem cell with > 1 % flagged
   time in its measurement window is **excluded** and listed in the manifest with counts. Slack is
   studied only in D10, outside the premise. Taut-feasibility QP at config load.
2. **EnergyAudit** (power balance vs kinetic-energy rate, residual bounded by solver tolerance)
   + momentum sanity on coast segments.
3. **Noise-power invariance:** accumulated twist-perturbation variance over a fixed horizon agrees
   within 1 % across the entire Δt/h grid — the test that makes C14/D8 mean something (√Δt
   convention, plan-v2 §6.8).
4. **Caption lint** (§1: `validat\w*` stem match, sentence window, registry-identity check,
   self-test over every plan-mandated caption literal) and **routing enforcement** (§2) in CI.
5. **Label-inversion vaccine:** unit tests pin each fuse_rule's executed signature (paper + frozen
   shapes → machine zero; A2 → the pilot's slope-2 diagnostic signature).
6. **Adapter parity:** the Drake-embedded filter equals `estimator_core` driven open-loop by the
   identical logged streams to 1e-12 (hard fail at 1e-9). Reruns on every Drake version bump.
7. **Bit-reproducibility** test; **truth-isolation lint**; **windows/alignment disjointness**
   asserted in `analysis/windows.py`.
8. **Weight convention:** SERIES pinned everywhere; the published harmonic-convention λ₂ pair
   (2.17 → 0.08) is **regenerated** (series gives 1.0851 → 0.0421, V2V-5) before any λ₂-bearing
   artifact ships; axis labels state "λ₂ (series-information weights, Def 4.1)".

---

## 4. Tier-1 completion (flagship §VIII evidence; all cells inside protocol class 𝒫)

Cells T1-E3a (extension), T1-E9, T1-E10 partials are **[HAVE]-adjacent**; T1-E2, E3b, E3c, E6 are
**[GAP]**. Full specs below; plan-v2 §8 remains the authority for anything not restated.

### 4.0 T1-E3a extension + T1-E9 + T1-E10 (close out the PROV block) — C7a, C8, C8b, C13, C14, C15

**[HAVE]:** generic slope 1.999; free switch-offs machine zero; C8 ratio 1.0000 at m = 2.
**Remaining [GAP]:** (i) m ∈ {3, 4} walks with sim-derived α_k (scaling claims only, flagged);
(ii) ≥ 12 random formations from the declared draw (`Unif(𝒦)|taut`, margin 0.10) with cluster
bootstrap; (iii) the remainder constant: over ≥ 200 shape draws in 𝒦 report
`sup_𝒦 R(τ,s)/τ³` where `R = ‖Log Π_c − τ² Σ_k α_k [C_{j_k}, C_{j_{k+1}}]‖` ([PUB] ledger 3);
(iv) **M8/C8b**: `sheaf/frustration.py` (lagged coboundary + gauge min), fit `log M8` on
`log M5²` (predict 2) and on `log m` (predict CI ⊂ [−1.3, −0.7]); (v) **C15 zero-commutator**
formations: `‖c_i − c_j‖ < 1e-12` with shapes ≥ 1 rad apart — amplitude slope ≥ 3 predicted;
falsifier: slope CI **includes** [1.8, 2.2] (failed to separate from generic); (vi) T1-E10
production: Δt ∈ {0.001, 0.0025, 0.005, 0.01} × τ grid (QD5: 0.02 dropped — commensurate with
neither the 50 ms update period nor Δ_c = 0.05 s; 0.001 added as the refinement point),
deterministic M5 arm headline, noisy D_ss beside it; falsifier: exponent or coefficient CIs
disjoint across Δt. Lie–Trotter and Strang implemented as named baselines (the [NPA] "you
rediscovered Strang splitting" defense: floor survives h → 0 at fixed τ); (vii) an explicit
**τ = 0 evaluation arm** (machine zero by construction) so the ladder's τ→0 row (§7.3) is
executed fact rather than inferred from the fitted slope-2 decay.

### 4.1 T1-E2 — Contraction, subspace-resolved · C6, C19 · PROV (LTV/frozen only) · F8

| | |
|---|---|
| **Design** | Reduced plant, **frozen shapes** (Q2 Path B default), gauge complement, **A3 idealized weights primary** with CI variant side-by-side (Rem 6.4; sim_design R-iii). Step-perturb all Ĝ_j by Exp(δ), ‖δ‖₂ = 0.5; fit exponential decay of ‖e_⊥‖₂ over a **4× κ range** × two topologies (cycle, complete). **ES-01 handled by design:** project e_⊥(t) onto (i) the measurement-contraction subspace (μ's domain) and (ii) the consensus subspace (κλ₂'s domain) using the tier1_sheaf kernel/gauge basis; report **three fitted rates** (two per-subspace + whole-vector) and test the additive prediction only as the qualified whole-vector envelope. μ calibrated at κ = 0 and **disclosed as fitted** — the tested prediction is the **unit slope in κλ₂**. **C19 arm:** sweep ‖δ‖ over ≥ 3 decades {5e-3 … 5e-1}; fit the log-linearity residual exponent (predict 2). |
| **Factors / seeds** | κ 4× × 2 topologies × {A3, CI} × ‖δ‖ (3 decades); 50 seeds |
| **Falsifiers** | slope(rate vs κλ₂) < 0.5 (either topology) ⇒ C6 falsified. C19 residual-exponent CI excludes [1.8, 2.2] ⇒ the "IEKF machinery survives fusion" claim is weakened in §V, reported. |
| **Caption** | "Rate prediction holds for the frozen linearization (Thm 6.3, an inequality; μ calibrated at κ = 0, so the identity line is anchored, not predicted); μ and κλ₂ act on different subspaces (per-subspace rates shown); the nonlinear extension is open." |
| **Finding path** | If the whole-vector rate deviates while per-subspace rates match their own predictions, **that is the ES-01 finding** and is written up as such — not treated as a numerics bug. |

### 4.2 T1-E3b — Dynamic D_ss floor with MOVING shapes · C7b · **CONJ** · F4b

The executed frozen-shape null makes shape motion **mandatory**: a static-shape cell measures
exactly nothing (D_ss ≈ 1e-29).

| | |
|---|---|
| **Design** | Reduced plant **integrating the shape ODEs** along the persistent-turn reference (η_ref ∈ [0.05, 0.25] rad/s, never vanishing — plan-v2 §9.1's re-centred profile); full DIEKF-Σ (P/U/F) from `estimator_core`; noise/bias on (`nominal`); uniform τ, jitter = loss = 0, inside 𝒫. τ ∈ {0.05, 0.1, 0.2, 0.4, 0.8, 1.6} s (6 pts, 1.505 decades). Formation kinds: generic, symmetric, near-symmetric, **zero_commutator** (C15's stochastic arm, exploratory). **≥ 12 formation draws × ≥ 10 seeds = ≥ 120 noise draws per τ point**; cluster bootstrap over formations (2000). Metric **M4 in coboundary form** (identical code to Tier-2 E_F), last 30 %, turn-window rule. **Arms on matched seeds:** paper rule (primary), A1, A2 (diagnostic), A3, `oosm_augmented` (the outside-class arm that **removes** the floor — reported as the class demarcation with its buffer-memory price vs τ), frozen-shape replay (regression to the executed null). |
| **Fit model [DESIGN, pre-registered — delta from plan-v2's plain log-log]** | `D_ss = D₀ + C·τ^p`. Rationale: the executed null shows the τ-independent noise component and the τ² staleness component have different physical origins; a naive log-log fit of the mixture reports an in-between slope and manufactures a spurious falsification. D₀ estimated from the τ→0 end and the frozen/straight controls; p fitted on the floor-dominated regime; **D₀ and p reported separately with CIs**; the plain power-law fit reported beside it. If regimes cannot be separated on this grid, extend the grid upward before declaring anything. |
| **Falsifier** | 2 ∉ p's CI (generic arm) ⇒ C7b falsified (a CONJ falsification — reported, not fatal; §10 R2). Zero-commutator D_ss arm: exploratory, no falsifier. |
| **Caption (mandatory, verbatim)** | *"Numerical evidence for the conjectured stochastic steady-state floor ([ES §10(ii)]); Theorem 7.2 is leading-order and deterministic and is tested in panel (a)."* |

### 4.3 T1-E3c — Symmetry suppression: two metrics, two exponents, uniform/robust split · C9a, C9b, C9b′, C9c · F5

| | |
|---|---|
| **Design** | ε ∈ {0, 0.0125, 0.025, 0.05, 0.1, 0.2} along the **declared** `formation.epsilon_dir` (unit vector in one named agent's (σ, σ_i)); **‖Dc·d‖ > 0 asserted at the base shape** (a degenerate direction silently flips 1→2 and 2→4); τ grid (6); noise `off` (ideal) and `nominal`. **Amplitude (M5) vs ε: exponent 1 (C9b′). D_ss ratio S(ε,τ) = D_ss(ε)/D_ss(0): exponent 2 (C9b). Never mixed in one panel.** **E3c-uniform** (uniform τ, inside 𝒫) = the theorem test (C9a: symmetric amplitude slope 3). **E3c-robust** = heterogeneous acoustic lags τ_e = d_e/1500 + τ_p, τ_p ∈ [0.1, 0.5] s, 20 % jitter, tension noise, ε ≠ 0 — captioned *"outside Thm 7.2's uniform-delay hypothesis; a robustness characterization, not a theorem test."* (reworded so no `validat\w*` token can collocate with the theorem on a D_ss-tagged artifact — the §1 lint applies to this caption too) |
| **Headline** | robust suppression **≥ 10× at τ = 0.4 s, one-sided; magnitude reported, not bounded above**. 400× appears only as "ideal-case artifact of chosen σ" reference label. |
| **Falsifiers (separable rows)** | C9a: 3 ∉ symmetric amplitude slope CI. C9b′: 1 ∉ amplitude ε-exponent CI. C9b: 2 ∉ D_ss ε-exponent CI. C9c: robust S < 10× at τ = 0.4 s. Each row falsifies itself only. |

### 4.4 T1-E6 — Multi-topology · C10 · CONJ/open · F4b overlay

Topologies {cycle, star, complete, path, rgg} × N ∈ {4, 6, 8} (**never N = 3**: C₃ = K₃), **with a
τ sweep per topology** (a floor coefficient requires one); amplitude and D_ss coefficients vs
λ₂(L_F) with SERIES weights; M4 as weighted **sum** (the per-edge mean confounds |E| with
spectrum). Tree topologies are **m = 2-dominated positive cells** with predicted amplitude
τ²|η|·‖c_j − c_i‖ to C8's [0.9, 1.1] tolerance — a sharper pre-registration than "expect zero".
Exploratory: no falsifier (C10 is open, [ES §10(vi)]); captioned as such.

---

## 5. DIEKF-Σ in Drake: integration milestones and the closed-loop campaign D1–D10

### 5.1 Integration milestones (risk-ordered; each gate falsifiable)

| M | Week | Content | Acceptance gate (hard) |
|---|---|---|---|
| **WS-0 walking skeleton** | 1 | One ASV + pentagon + 1 cable on the existing plant; **minimal `estimator_core` P/U/F skeleton** (pure functions, paper rule only — no CI ω search, no rules registry, no weights) sufficient for the parity gate, full package lands wk 3–4 (§9.2); `DIEKFSigmaLeaf` adapter; `VectorRingDelay` + DropGate in loopback; parquet exporter + manifest | (a) bit-identical parquet on replay; (b) **adapter parity ≤ 1e-12** vs open-loop core on identical logged streams; (c) wall-clock per simulated second **measured and recorded** — this number sizes the campaign. If > 12× real-time at N = 5: profile + consolidate sensor systems before any cell runs. |
| **INIT-1 shape bootstrap** | 2 | ŝ₀ from the tension channel: 10 s straight-tow calibration segment (declared, before the GNSS-denial clock); load-side angle from formation prior refined by 20 Hz updates; ±π branch disambiguated by sign of dT/d(thrust) | median ŝ error < 2° at corridor entry, max < 5° (50 seeds, N ∈ {4, 5}). **Pre-declared contingency:** promote the cable-angle sensor into the default suite and document the change in both papers — never silently tune. A biased ŝ₀ injects a spurious D_ss offset; floor cells cannot run until this gate passes. A D_ss-vs-ŝ-error scatter is logged in every D2 cell as a standing confounder check. |
| **M-FAB** | 3–4 | N-agent build loop (config-only structure, no literal N), full comms fabric, sensors, controller, baselines; S1 end-to-end nominal transit; truth-isolation lint green; first hero-movie draft via anim2d | S1 runs closed-loop, TautCertificate clean; determinism + lint tests green; D1 pilot ANEES within [0.8, 1.3] on ≥ 6 seeds |
| **PILOT-6** | 5 | Entire D-grid at 6 seeds/cell | sd(log E_F) per cell → power check (§8); TautCertificate/guard trigger rates (> 20 % invalidation ⇒ trajectory redesign, not exclusion-by-attrition); measured minutes/run → final MC sizing; **QD4 decided** (τ = 1.6 s retention) |
| Production D-cells | 5–9 | §5.4 | per-cell falsifiers §5.4 |

### 5.2 Comms fabric [DESIGN, from Drake plan §5 + panel consensus]

Per directed edge (i→j): `PacketSerializer → VectorRingDelay(T_c = 10 ms, k_ij) → DropGate(p_ij)
→ pkt_in`. Packets are fixed-width 29-float vectors (§3.1); drops **after** the delay (erasure at
reception) via validity flag; jitter = per-packet integer delay-step draw at send from a seeded
stream. Stamps ride in-packet: the estimator consumes on the dedicated 100 Hz T_c-grid poll (§3.3)
and uses **measured** age, and **the FusionRecord's logged realized age — not nominal τ — is the
fit regressor in every cell, both tiers** [DESIGN, pre-registered]; in protocol class 𝒫
(synchronous-periodic, theory cells) realized age ≡ τ_ij is **asserted per fuse event** — the
premise is a config-visible, machine-checked object; robust cells (D10, E3c-robust analog) step
outside it **by config, visibly**. Acoustic model for
showcase/robust cells: τ_e = d_e/1500 m s⁻¹ + τ_p, τ_p ∈ [0.1, 0.5] s, jitter 20 %, loss p ∈
[0, 0.2] (sim_design.tex:19).

### 5.3 Trajectory classes [DESIGN]

- `persistent_turn` — |η_ref| ∈ [0.05, 0.25] rad/s, never vanishing; **the primary floor-cell
  trajectory in both tiers** (plan-v2 §9.1's window rule made binding; a single 60° turn at the
  dogleg yields only a ~10–20 s window — too short for a clean last-30 % D_ss).
- `dogleg` — 400 m, two straight legs, one 60° turn, width 18–30 m (sim_design.tex:19); the
  showcase transit and the demonstration arm of D2; measurement window = the turn-containing
  segment by the one window rule.
- `straight_tow` — η ≈ 0; the in-plant floor switch-off and in-situ D₀ measurement.
- 120 s window-focused trajectories for floor cells; ~600 s for the full BHT transit.

### 5.4 The closed-loop experiments (all RA-L primary; claim binding + hedge + falsifier each)

**D1 — Consistency and filter correctness (Drake plan C1; S1).**
Design: nominal transits, 50 seeds; per-agent NEES/ANEES **on the gauge complement** (target
[0.8, 1.3]) with h* alignment on a window disjoint from evaluation; NIS per measurement family vs
χ² envelopes; analytic Jacobians cross-checked by **central finite differences** through the
factored pure functions along a logged trajectory — mechanism pre-registered because
`estimator_core` is pure NumPy and Drake's AutoDiffXd does not pass through `np.linalg.inv`/scipy
`expm` (relative step 1e-6; elementwise tolerance 1e-6·(1 + |J|)); B0/B1 overlays (B0 drifts,
B1 bounds).
Claim: Def 6.1 as implemented; consistency rests on Thm 6.3's LTV/frozen hypothesis — ES-01
subspace qualification quoted. Falsifier: ANEES ∉ [0.8, 1.3] pre-beacon (reported as R4
consistency failure); Jacobian mismatch above elementwise tol ⇒ blocking bug.

**D2 — Closed-loop D_ss floor on maneuvering trajectories (the conjecture's home turf; Drake plan C2; T2-E2).**
Design: τ ∈ {0.05, 0.1, 0.2, 0.4, 0.8, 1.6} s via k·T_c (k ∈ {5, 10, 20, 40, 80, 160}; τ = 1.6
retention pilot-gated, QD4); **arms on matched seeds**: (a) `persistent_turn` **primary fit**;
(b) `dogleg` demonstration; (c) `straight_tow` — predicted collapse ≥ 2 orders; (d) frozen-shape
**replay** (shapes clamped in the estimator's transport; **offline re-processing of arm (a)'s
logged runs, zero sim cost**) — predicted machine zero, **re-demonstrating the executed Tier-1
null inside the full multibody plant** (the regression that pins it — the null itself was executed
in Tier-1, not here); (e) A1; (f) A2 (diagnostic; signature pinned); (g) noise-off deterministic. ≥ 12
formation variants (fan-angle/thrust-scale draws) × ≥ 4 seeds ⇒ ≥ 48 draws per (τ, primary) point,
≥ 25 seeds at the controls' 3-point τ grid {0.1, 0.4, 1.6}; cluster bootstrap over formations.
Metric E_F computed by the **same** `analysis/metrics.py` as Tier-1 M4; fit `D₀ + C·τ^p` (§4.2).
Claim binding: **CONJ only** — caption verbatim: *"numerical evidence for the conjectured
stochastic steady-state floor under realistic shape motion. Thm 7.2 (leading-order, deterministic)
is not tested here; its amplitude is measured in D3."* (worded so no `validat\w*` token collocates
with the theorem — the §1 lint passes its own mandated captions). Arm (c) vs (a): the mechanism claim "the floor is excited by
motion × curvature" — DESIGN-level, grounded in the executed null.
Falsifiers: (a) 2 ∉ p's CI ⇒ C7b-Drake falsified (reported; outcome ladder §10 R2); (c) straight
floor NOT ≥ 10× below dogleg/persistent-turn at τ = 0.4 s ⇒ the motion×curvature mechanism story
is retracted; (d) nonzero floor above solver tolerance ⇒ implementation indictment, campaign
halts; (f) A2 indistinguishable from paper rule ⇒ conjugated transport not load-bearing
(C18-class failure, reported).

**D3 — Measured holonomy amplitude in closed loop (Q14 resolved to option (i); the PROV Drake cell).**
Design: every fuse event logs its **applied transport** (FusionRecord); analysis computes
M5 = ‖Log Π_c (applied transports)‖ per comm cycle per epoch on the same runs as D2 (zero extra
simulation cost). Deterministic sub-arm: noise/bias off, single transit per (τ, formation).
Compare fitted Ĉ against C_hol from `tier1_sheaf/sheaf/holonomy.py` evaluated on the **logged
Drake shape trajectories** (not idealized shapes) — the theorem's formula against the full plant's
actual configurations. The source-quotable C_hol comparison stays at **m = 2** (per-edge closed
walks on C₅); the 5-cycle amplitude is reported as scaling with sim-derived α_k, flagged.
Claim binding: **Thm 7.2 PROV, leading-order deterministic** — the only Drake cell allowed to name
the theorem without the conjecture hedge, because it measures the theorem's own object (transport
cycle non-commutativity), not D_ss. **Two CaptionRegistry entries, keyed by arm** — the "validate"
verb binds to the deterministic sub-arm ONLY, because Thm 7.2's hypotheses are deterministic and
D2's primary runs are noisy: noise-off sub-arm — *"noise-off closed-loop transports validate the
leading-order holonomy amplitude of Thm 7.2 (deterministic, O(τ²)) within its stated
hypotheses."*; M5 on D2's `nominal` (noisy) runs — *"consistent with the leading-order amplitude
of Thm 7.2 under closed-loop noise."*
Falsifier: noise-off slope CI excludes [1.8, 2.2], or Ĉ/C_hol CI excludes 1 beyond the stated
sup R/τ³ remainder bound on 𝒦 ⇒ a finding, localized via D8 sweeps before touching the theorem.

**D4 — Symmetry suppression, closed loop (Drake plan C4; T2-E3).**
Design: {symmetric pentagon front-arc class (equal fan angles + equal cable lengths, Q7),
near-symmetric ε ∈ {0.0125, 0.025, 0.05, 0.1, 0.2} along the declared direction, generic} ×
τ ∈ {0.1, 0.2, 0.4, 0.8}; **seeds [DESIGN]: 25 matched pairs per τ for the headline ratio
(paired, 200 runs); 12 formation draws × 1 seed per (ε, τ) point on the ε grid (240 runs — §8.2's
draw count met, noise replication deliberately thin) ⇒ ≈ 440 runs total (§9.3)**;
persistent-turn window. **Power pre-declaration:** the ≥ 10× one-sided suppression is the powered
claim; the E_F ε-exponent row is a **reduced-power cell — expected UNDER-POWERED at this budget
and reported as such (§1 convention)**: the powered ε-exponent claims live in Tier-1 E3c, and the
amplitude ε-exponent comes free via D3's M5 on the same runs. **Achieved ε measured
from logged shapes and reported** — SAP numerics, drag, and controller transients never give exact
symmetry, so the exact-cancellation claim stays in Tier-1 (machine zero, executed) and Drake
claims only the ratio.
Claim binding: Cor 7.3-motivated; caption carries the achieved-ε caveat; headline = robust
**≥ 10× one-sided at τ = 0.4 s**.
Falsifiers: suppression < 10× one-sided; near-symmetric exponents (1 amplitude via D3's M5, 2 on
E_F) outside CIs — separable rows.

**D5 — Gauge rank-3 drift and beacon collapse (Drake plan C5; S5).**
Design: long GNSS-denied transit, docking beacon (5 Hz, full pose, σ = (0.05 m, 0.05 m, 0.5°))
enabled only in the final 30 m; empirical covariance of {Log(Ĝ_j G⁻¹)}_j across agents; numerical
rank via σ₄/σ₃ < 0.1 on the stacked-ℝ^{3N} error; kernel- vs complement-projected error and
covariance trace (kernel basis transported by restriction maps, `sheaf/gauge.py`); at beacon-on,
full-rank collapse within 10 s (collapse threshold: λ_min reaching 10⁻³·λ₂(unpinned) — a ratio, so
it survives Q6b either way); ANEES on complement; alignment window disjoint (first 20 % / last
30 %). 50 seeds.
Claim binding: **Thm 5.1 + Cor 5.2 PROV — validation language permitted.** The Tier-1 spectral
facts are already executed (dim ker 3, sections to 1.3e-15, pinning collapse); this shows the
structure survives the full plant, noise, and closed-loop control.
Falsifier: σ₄/σ₃ > 0.1 without beacon; no collapse within 10 s; complement error unbounded.
Because the theorem is PROV, failure indicts the implementation first — pre-registered debug
order: restriction-map functoriality test → truth-isolation lint → INIT-1 ŝ bias.

**D6 — The information channel IS the force (Drake plan C6; S6; two-part paired design).**
Part 1 (ablation): tension channel ON vs `consensus_only`, matched seeds, ≥ 25 pairs; Δ tr Σ_shape
and Δ shape-RMSE with bootstrap CIs. Part 2 (**dose-response — the stronger evidence**): the
executed unequal-thrust config (thrust_scale 1.3/1.1/0.9/0.7 → 94 % tension spread) makes
per-agent tension a covariate; regress per-agent shape RMSE and tr Σ_shape against time-averaged
T_j² (the A10 Fisher proxy) across agents and seeds. Log broadside-guard activations and show
guarded intervals coincide with online λ₂ dips (M6).
Claim binding: Def 4.1 weights + Cor 5.3 — *"consistent with the conjectured monotone
dependence"*, never "proves"; A10's κ ∝ T² is a **model assumption, stated as such**.
Falsifier: Part 1 ΔCI includes 0 ⇒ **T2-C6** falls (the Drake plan's "tension channel carries
estimation information" claim — **namespaced**: Drake-plan claim IDs are cited as T2-Cn throughout
this plan, because Tier-1 ledger C6 is the *contraction* claim (T1-E2) and the bare token collided).
Part 2 slope non-negative (CI) ⇒ the Fisher-weight model is wrong for this plant; reported,
dose-response claim dropped.

**D7 — Baselines head-to-head + BHT scorecard (sim_design E8, retired to Tier-2).**
Design: 50 full transits per method ∈ {DIEKF-Σ, B0, B1, B2, B3}: docking success (< 0.5 m, < 5°),
energy, min clearance, min tension, ANEES. B2 (identity edge maps, no conjugated fast-forward)
is the sheaf ablation — feeds C18's "the sheaf is load-bearing" with a closed-loop consequence.
Claim binding: none beyond "the pipeline solves BHT where the ablations degrade"; headline table
of the RA-L paper. Falsifier: DIEKF-Σ does not outperform B2 on docking/disagreement at matched
comms ⇒ the induced sheaf is not load-bearing in closed loop — a major reported finding.

**D8 — Artifact defense battery (Drake plan C9/E8).**
(i) h ∈ {0.25, 0.5, 1, 2} ms on D2's central column τ ∈ {0.1, 0.4, 1.6}, 25 seeds, √h-consistent
noise asserted (1 % invariance gate); (ii) cable variant A (distance constraint) vs variant B
(rod + reaction forces) differencing + TensionObserver ≤ 1 % RMS cross-check; (iii) hydro
`neglect` vs `lagged` anisotropy sensitivity pair.
Claim binding: C14-class DESIGN: "the floor is invariant under discretization refinement and cable
model." Falsifier: exponent/coefficient CIs disjoint across h or cable models ⇒ localized finding,
reported before any theory-facing claim ships.

**D9 — Scaling montage (Drake plan S7; sim_design E6 Tier-2 half).**
N ∈ {3, 4, 5, 6, 8} × {cycle, complete}; formations auto-generated from config (zero code change —
the scalability contract); E_F floor and re-lock rate vs λ₂(L_F) with ring ∝ 1/N² and expander
Θ(1) curves; N = 3 is demonstration-only (C₃ = K₃ — no cross-topology inference at N = 3);
wall-clock per run reported. **Seeds [DESIGN]: 12 formation draws × 2 seeds per (N, topology)
cell (≈ 240 runs, §9.3). Power pre-declaration:** the **Spearman ordering by λ₂ is the powered
claim**; the ring −2 exponent (3 support points, N ∈ {4, 6, 8}) is a reduced-power row — reported
with its CI and expected UNDER-POWERED under the §1 convention unless pilot variance is low.
Claim binding: Thm 5.1 spectral structure PROV; rate-vs-λ₂ via Thm 6.3 LTV form with ES-01
qualification; D_ss-vs-λ₂ trend CONJ-captioned. Falsifier: rate fails to order by λ₂ at fixed N
(Spearman CI includes 0), or ring exponent CI excludes −2 over N ∈ {4, 6, 8}.

**D10 — Robustness outside the premise (sim_design E7; SLACK-1; broadside set piece).**
(a) Slack events: aggressive-turn variants (|η| at the 0.3 rad/s limit, gusts) engineered to
produce slack; hysteresis [5, 15] N; TautCertificate-excluded regime studied deliberately: re-lock
time, ANEES excursion/recovery. (b) Packet loss p ∈ {0, 0.1, 0.3} + jitter sweeps.
(c) Broadside guard-save: scripted gust drives one cable toward cos σ → 0; paired seeds guard-ON
vs guard-OFF; divergence rate and re-lock time; pilot parameter search documents the envelope —
if the guard genuinely fails inside it, that is a reported finding, and the set-piece movie ships
only if the paired statistics support the scene.
Claim binding: **explicitly outside the taut-trivialization premise / protocol class 𝒫** —
captions state the hypothesis is violated by construction; graceful degradation only; Cor 5.3
broadside degeneracy "monotonicity conjectured". Falsifier: none (characterization); reportable
red flags: ANEES > 3 persisting > 30 s after re-tension; guard-OFF failing to degrade.

---

## 6. The cross-tier overlay (capstone)

**Matched configuration:** pentagon front-arc formation mapped into Tier-1 shape coordinates
(attachment geometry → (σ, σ_j) pairs — the mapping function is part of `analysis/`), graph C₅,
identical τ grid {0.05 … 1.6} s, noise matched **in distribution** (never "seeds mapped" —
different draw counts per step make bit-matching impossible; stated in the paper), ≥ 25 seeds per
tier per point. **Estimand [DESIGN, explicit]:** exponents and coefficients are **inherited from
the production fits** (T1-E3a/E3b and D3/D2, each with their ≥ 12-formation clusters per §8.2);
the matched runs supply **only the cross-tier coefficient ratio at the matched config** — no new
slope is fitted on them, so §8.2's formation-draw requirement does not bind here.

**Two panels:**
- **F4a-overlay (PROV):** T1-E3a amplitude ↔ D3 measured M5, with Ĉ/C_hol from both tiers. May
  name Thm 7.2 with its leading-order/deterministic hedge.
- **F4b-overlay (CONJ):** T1-E3b D_ss ↔ D2 E_F — both computed by the single shared metrics
  module in coboundary form (the metric reconciliation plan-v2 §10.4 demanded). Mandatory caption
  (a CaptionRegistry literal; the §1 lint self-test runs over it): *"Tier-1/Tier-2 agreement on
  the conjectured steady-state floor ([ES §10(ii)]). Panel (a) separately tests the leading-order,
  deterministic holonomy amplitude of Thm 7.2 in both tiers."* — no `validat\w*` token ever
  collocates with the theorem on this CONJ panel, and the full registered hedge is present.

**Agreement criteria [DESIGN, pre-registered as an equivalence test — never satisfiable by mere CI
width]:** agreement ⇔ the cross-tier exponent-difference CI ⊂ [−0.2, +0.2] **and** the coefficient
ratio's CI ⊂ [1/1.3, 1.3] (δ = 0.3, declared here; half-widths reported). A CI that merely
*contains* the null but escapes its equivalence band is **UNDER-POWERED** per the §1 three-outcome
convention — reported with the CI and the systematic budget, never read as agreement.
Disagreement = the exponent-difference CI excluding 0 or the ratio CI excluding 1 —
**a finding, not an embarrassment**: localization ladder (Drake h-sweep → cable A/B differencing →
hydro sensitivity → Tier-1 Δt-sweep → frozen-shape regressions in both tiers) runs **before** any
theory edit; if disagreement survives localization, the reduced model's validity domain is
narrower than claimed and §VIII says so.

**Independence line (verbatim in both papers):** *plants, integrators, constraint solvers, tension
recovery, and shape evolution are independent; the estimator, metric functional, window rules, and
fit code are deliberately shared, so that agreement is a statement about the algorithm on two
plants and any disagreement localizes to the plant.*

Alongside the overlay: the Drake h-sweep inset and cable-model differencing (D8) — the two-tier R9
defense in one figure. Routing: RA-L centerpiece; TCNS supplementary + forward pointer only.

---

## 7. The showcase: Blind Harbor Transit

### 7.1 Hero scenario [SPEC: sim_design.tex:19 — channel/geometry/comms] + [DESIGN: N = 5, pentagon caisson]

N = 5 ASVs tow the 2 500 kg pentagon caisson (circumradius 4 m, bow vertex forward, front-arc
attachments, ~2.35 kN/cable at the executed N = 5 config) — a **disclosed delta** from
sim_design.tex:19's N ∈ {3, 4, 6, 8} barge, chosen for the executed platform's pentagon-caisson
config and recorded here in the same style as §3.4's sensor correction — through the 400 m dogleg
(two straight legs, one 60° turn, width 18–30 m). **GNSS denied for the entire transit** (lint-enforced);
acoustic comms on C₅: τ_e = d_e/1500 + 0.3 s, 20 % jitter, p = 0.1 drop [DESIGN within
sim_design's p ∈ [0, 0.2]]; docking beacon (5 Hz) visible only in the final 30 m; docking success
= position < 0.5 m, heading < 5°, clearances > 2 m, cables taut. Every agent runs the identical
`estimator_core` that produced the Tier-1 curves. INIT-1's 10 s calibration straight precedes the
denial clock. **Hero seed = ensemble median D_ss over the 50-seed S1-hero ensemble — a documented
selection rule printed in the supplementary, never cherry-picked.**

### 7.2 Hero movie storyboard (~90–120 s at 6–8× compression; anim2d guaranteed path)

Rendered exclusively from parquet logs (matplotlib FuncAnimation + ffmpeg, h264, 1920×1080,
30 fps); Meshcat StaticHtml is the interactive twin; always-visible sim-clock + "×8" speed badge.

**Layout.** Left ~62 %: top-down harbor chart — quay walls, corridor; caisson truth pose solid;
**five ghost caisson outlines** (one per agent's Ĝ_j, Okabe-Ito palette, 40 % alpha); vessels as
oriented hulls; **cables colored by instantaneous tension** (viridis, fixed 0–3 kN scale, colorbar
with the 5 N TautCertificate margin marked); comm edges flash at packet-consumption instants with
measured age labels ("τ = 0.31 s"); drops flash red-x. Right ~38 %, three synchronized panels:
(P1) E_F(t), log scale, with a shaded band labeled **on the plot**: *"conjectured stochastic
steady-state floor (Thm 7.2 is leading-order and deterministic; the steady-state floor is
conjectured)"* — the hedge survives screenshots; (P2) online λ₂(L_F(ŝ)) with the broadside-guard
threshold and activation flags; (P3) gauge split: kernel-projected error (growing) vs
complement error (bounded, 3σ envelope) + a σ₁…σ₄ spectrum strip. Bottom ribbon: beat timeline
Leg 1 | TURN | Leg 2 | BEACON | DOCK.

**Five beats.**
1. *Formation* — tensions ramp taut; E_F at the noise intercept; title card states the sensing
   contract: "No GNSS. No relative-pose sensing. Each vessel sees only its own odometry and its
   own cable."
2. *Leg 1* — the ghost cluster drifts off truth **as a rigid body** while complement error stays
   flat; annotation: "All drift lies in a 3-dim gauge orbit (Thm 5.1) — the fleet knows its shape,
   not its place."
3. *THE TURN (the scientific climax)* — as shapes evolve through the 60° bend, E_F blooms out of
   the noise intercept into the shaded band and relaxes after; annotation: "Shape motion ×
   curvature × latency: the conjectured floor appears only when the formation maneuvers — at
   frozen shapes the fusion is exact." A gust event drives P2 toward the guard line; guard flag
   fires; the near-broadside cable dims (information weight → 0); λ₂ recovers.
4. *Leg 2* — E_F relaxes toward the intercept; ghosts still offset as a cluster.
5. *BEACON + DOCK* — beacon ring at 30 m; σ₁…σ₃ collapse within 10 s, σ₄ never excited; the ghost
   cluster snaps onto truth ("one anchor kills the gauge — Cor 5.2"); docking scorecard card with
   pass/fail ticks (ATE, heading, clearance, min tension, ANEES, energy).

**Fallback honesty:** if no honest comms setting puts the turn bloom ≥ 3× above the straight-leg
band (piloted against the D2 grid), the bloom beat is **cut** and the floor appears only in the
dedicated D2 figure — the movie never manufactures the effect.

### 7.3 Supporting artifacts

| Artifact | Content | Why it lands |
|---|---|---|
| **Split-screen movie** (D4) | symmetric vs generic formation, same seed, same dogleg, **one shared log-E_F axis**; achieved-ε printed on screen | the ≥ 10× separation read directly off one chart; a design principle demonstrated, not asserted |
| **"No motion, no floor" figure** (D2 a/c/d) | maneuvering floor vs straight-tow vs frozen-replay machine zero, one set of axes | converts the executed null into the sharpest honest statement of the conjecture's mechanism |
| **"Same code, two plants" short** (~30 s) | Tier-1 reduced integrator and Drake side-by-side on the matched config, two E_F(t) traces overlaid live | the overlay capstone as a moving image |
| **Gauge-snap long-form** (D5) | rank-3 waterfall through beacon-on | validates PROV theorems with validation language legitimately available |
| **Failure-honesty clip** | a TautCertificate violation run (slack at the turn) being invalidated on camera | the validity instrument, shown working |
| **Gallery 3 "Blind Harbor"** | static HTML: embedded mp4 + Meshcat StaticHtml + per-artifact caption-with-hedge + config hash + one-line regeneration command | reproducibility as an experience; extends the two published galleries |
| **Switch-off ladder table** — ONE tier-tagged source table; `figures.py` emits two renditions **mechanically** (per-row tier tags filter, the tool never refuses the whole table): the TCNS §VIII rendition carries **Tier-1 rows only**, and the straight-line-in-Drake row appears **only in the RA-L rendition** (at most a TCNS-supp forward pointer) — §2 rule (1) satisfied by construction, not editorially | ~7 rows: τ→0 (explicit τ = 0 arm, §4.0(vii)), ξ=0, η=0, s_i≡s_j (**edge-wise, the executed m = 2 E3a arm**), full-cycle symmetric class (**a distinct cell — E3c C9a at N = 5**), zero-commutator, straight-line-in-Drake — each showing machine zero or the predicted order shift | reviewers trust an effect that dies on command; **three rows (s_i≡s_j, η=0, ξ=0) are executed machine-zero fact; τ→0 is the executed fitted slope-2 decay until its explicit arm runs** |
| **Tension dose-response figure** (D6) | per-agent RMSE / tr Σ vs T²-information across the 94 % spread | the information channel IS the force, as a checkable regression; pins Q6 constants at ~2.5 kN |

**Style standards:** one `analysis/style.py` for both tiers; agent palette Okabe-Ito; tension
always viridis 0–3 kN; vector PDF for paper figures, 600 dpi PNG only for raster-heavy heatmaps;
every movie regenerable by one CLI command from `(config hash, seed)`; time compression always
badged; Tier-1's existing `gauge_drift.mp4` restyled through the same module.

---

## 8. Statistics protocol (binding; plan-v2 §9.2 + §3 convention)

1. **50 seeds/cell production; pilot 6.** The pilot sizes variance before any 50-seed spend.
2. **The FORMATION is the inferential unit** for cross-formation claims: ≥ 12 formation draws per
   grid point for any slope claim; **cluster bootstrap over formations** (2000 resamples), both
   variance components reported (within- vs across-formation). Formation draw law declared:
   Unif(𝒦) with margin 0.10, `on_reject: resample` (validity-conditioned estimand); rejection
   rate reported per cell.
3. **τ grids span ≥ 1.5 decades** (the 6-point doubling grid = 1.505).
4. **Three-outcome convention** (§1): falsified / accepted / **UNDER-POWERED, reported as such**.
5. **Holm–Bonferroni within each E-family.**
6. **Pre-registered fit models:** amplitude cells — WLS on log-means; stochastic cells —
   `D₀ + C·τ^p` with D₀ measured in situ by the straight/frozen controls (§4.2).
7. **Window rule** stated once, applied uniformly by `analysis/windows.py`; sensitivity appendix
   shows fits under ±50 % threshold variation; the rule is in the run manifest.
8. **Systematic budget** (fit sub-range, grid endpoints, Δt/h, formation draw) reported beside
   every seed CI — a tight CI never masquerades as a risky prediction passed.
9. **Paired designs wherever a toggle exists** (matched seeds): D4, D6, D10c, use_truth ablations.
10. **Exclusion accounting:** TautCertificate exclusions, divergent-run flags (ANEES > 10), and
    guard activations reported as counts per cell — never silently dropped.
11. **Power sanity:** the discredited "n ≥ 12" heuristic is deleted (plan-v2 §9.2); pilot-measured
    sd(log D_ss) drives sizing; if sd > 0.15 on contested arms, lengthen the turn window or add
    formations before adding seeds.

---

## 9. Milestones, effort, compute budget

### 9.1 Combined program — the **two-engineer** critical path (one engineer per track after wk 2)

| Wk | Track | Content | Falsifiable gate |
|---|---|---|---|
| 1 | Both | **WS-0** (§5.1) + `estimator_core` extraction + `analysis/` skeleton (metrics, captions, style) | WS-0 gates (a)–(c); caption lint live in CI |
| 2 | Both | **INIT-1**; Tier-1 `plant/` shape ODEs + √Δt noise + TautCertificate; **λ₂ regeneration** (series weights) | INIT-1 gate; telescoping-flat at τ = 0; noise-power invariance ≤ 1 % across Δt grid; 2.17→0.08 regenerated as series numbers |
| 3–4 | Drake | **M-FAB**: N-agent fabric, sensors, controller, baselines, S1 end-to-end, hero draft, D1 pilot | M-FAB gate (§5.1) |
| 3–4 | Tier-1 | T1-E3a extension (m ∈ {3,4}, ≥ 12 formations, sup R/τ³, M8/C8b, C15) + T1-E10 production | T1-M2-class gate: 2 ∈ amplitude CI half-width < 0.2; free switch-offs kill it; Ĉ/C_hol ∈ [0.9, 1.1] at m = 2; exponent invariant across Δt |
| 5 | Both | **PILOT-6** (Drake grid) + Tier-1 E3b/E3c pilot; power checks; QD4 | PILOT-6 gate (§5.1); descope decisions recorded |
| 5–7 | Both | Production: **D2, D3, D4**; **T1-E3b, T1-E3c**; T1-E2 | per-cell falsifiers (§4, §5.4) |
| 7–8 | Both | **D5, D6, D7**; T1-E1 closed-loop half (C17 ANEES, C18 B2); T1-E6 | per-cell falsifiers |
| 8–9 | Both | **D8** h-sweep + cable differencing + hydro pair; **XT overlay** (§6); D9 | D8/overlay criteria (§6) |
| 9–10 | Both | **D10** robustness/slack/broadside; hero movie final + set pieces + gallery 3; failure clip | movie ships only if paired statistics support each scene |
| 10–11 | Both | Figure/movie set freeze; **routing-table audit of every artifact against its target paper** + **claim-ID namespace audit (Tier-1 Cn vs T2-Cn — the D6 collision class)**; repro freeze (Docker, manifests, `make figures` from parquet only); manifest **V1–V6** re-run against frozen theorem statements ([PUB] ledger 6 **as corrected by Q11** — its "V1–V9" does not exist, §0.2); **Q11's [PUB] corrections applied in the flagship drafting pass** | one-command regeneration; routing audit signed off; caption lint green over the full artifact set |

Rows sharing a week are the two parallel tracks (one engineer each). **A single engineer
serializes them to ~16–20 weeks** — §9.2's 15–20.5 engineer-week sum; the 11-week figure is valid
only at two engineers. WS-0's week-1 scope is the P/U/F skeleton (§5.1), not the full
`estimator_core` (§9.2 prices that at 3–4 weeks, landing wk 3–4).

### 9.2 Effort re-costing (honest; supersedes nothing — plan-v2 §12 still governs Tier-1-only scope)

| Workstream | Wks (low–high) | Basis |
|---|---|---|
| `estimator_core/` (P/U/F, CI, weights, rules, tests) | 3–4 | plan-v2 §12 "agents/": nothing exists; CI ω search is the per-step cost driver (1-D Brent if the 19-point grid binds) |
| Tier-1 `plant/` + `harness/` + comms | 2–2.5 | shape ODEs new (pilot had frozen shapes) |
| `analysis/` shared module | 1.5–2 | on the critical path for every CI/figure |
| Drake WS-0 + INIT-1 + M-FAB (sensors, fabric, adapter, baselines, monitors) | 3–4 | platform exists; agents/comms new |
| Production cells both tiers (runs + analysis passes) | 2–3 | compute is 2–3 overnights (§9.3); human cost is triage |
| Viz (anim2d, movies, gallery) + overlay | 1.5–2 | layout grammar reused across all movies |
| Integration/debug slack | 2–3 | |
| **Total** | **15–20.5** | two engineers compress to ~9–12 by parallelizing the Drake and Tier-1 tracks after week 2 |

### 9.3 Compute budget [DESIGN — planning numbers, measured at WS-0 and PILOT-6]

Tier-1: theory cells ~120 s ≈ 12 k steps; spec DIEKF-Σ ≈ 680 µs/step (plan-v2 §12 benchmark;
56 % is the CI ω search) ⇒ full Tier-1 campaign ≈ 9 CPU-h NumPy; T1-E3a/E10 deterministic arms
nearly free. Drake: ~2 300 sim runs, costed in **two run classes plus the h-sweep** (the earlier
uniform 4-min pricing understated the transit mix): **(i) full ~600 s BHT transits** — D7 250 +
D1 50 + D5 50 + hero 50 = 400 runs × ~20 min (600 s at ~2× real-time) ≈ 133 CPU-h; **(ii) ~120 s
window-focused runs at h = 1 ms, ~4 min each** — D2 ≈ 620 (its own §5.4 spec: 288 primary +
~300 controls + ~36 noise-off; arm (d) and all of D3 are offline re-processing of logged runs,
zero sim cost) + D4 ≈ 440 + D6 ≈ 100 + D9 ≈ 240 + D10 ≈ 150 + D8's nominal-h arms ≈ 125
⇒ ≈ 1 675 runs ≈ 112 CPU-h; **(iii) D8 h-swept runs scale ∝ 1/h** — 75 runs each at
h ∈ {0.25, 0.5, 2} ms (the 1 ms column reuses D2's central column) ≈ 33 CPU-h. Total
≈ **280 CPU-h ⇒ two overnights on a 32-core box (plan 2–3 with PILOT-6 and re-runs — still
comfortably feasible, and now the number that drives PILOT-6's MC sizing and the descope order)**
via `multiprocessing.Pool` (one build+run per worker; Drake objects never cross
process boundaries; `SeedSequence(master).spawn` per run). **Hard descope order, pre-declared:**
drop the fine-τ arm first, then D8 columns, then D9 breadth — **never seeds below the power
requirement** (an under-powered cell is reported as UNDER-POWERED, not quietly passed).

---

## 10. Risk register

| # | Risk | Impact | Mitigation / pre-registered outcome |
|---|---|---|---|
| R1 | Estimator/LeafSystem seam silently diverges (context mishandling, event order, ZOH aliasing across 1 kHz/50/20/10 Hz) | poisons every downstream cell | WS-0 adapter-parity ≤ 1e-12, CI-blocking from week 1; pull-semantics-only; explicit offsets; parity rerun on Drake bumps |
| R2 | **Closed-loop D_ss shows no clean slope 2** — the single most likely "bad news", since D_ss is CONJ and dynamic noise may dominate τ² at feasible speeds | the RA-L floor panel weakens | **Pre-registered outcome ladder:** (i) D3's PROV amplitude is computed in the same runs and succeeds independently; (ii) the decomposition arms (frozen replay → machine zero, straight, A1/A2, noise-off) yield a **variance-attribution figure** — publishable in itself; (iii) caption: "not resolved under closed-loop noise at these scales"; (iv) the amplitude-holds/D_ss-flat branch **is the honest RA-L narrative, committed to now** so nobody is tempted to inflate later. No claim needs retraction — captions were CONJ from the start. |
| R3 | D₀ (τ-independent noise floor) and C·τ² mix, a naive log-log fit reports an in-between slope ⇒ spurious falsification | false negative on C7b | pre-registered `D₀ + C·τ^p` model; D₀ measured in situ (straight arm, τ→0 end); extend the grid upward before declaring if regimes cannot separate |
| R4 | SAP compliance/regularization aliases into the O(τ²) measurement | corrupts the Drake floor coefficient | D8 battery: h-sweep, stiffness/compliance sweep or A↔B differencing, TensionObserver ≤ 1 % gate; instability localized before any theory-facing claim |
| R5 | Shared estimator weakens the "independent implementations" reading of the overlay | reviewer discounts the capstone | §3.2's reframe in print: plant independence is the load-bearing independence for R9; within-tier defenses (E10, h-sweep, A/B differencing) need no independence argument |
| R6 | ŝ₀ bootstrap biased/branch-ambiguous → spurious D_ss offset masquerading as (or masking) the floor | contaminates every CONJ cell | INIT-1 gate (< 2° median) before floor cells; declared cable-angle-sensor contingency; standing D_ss-vs-ŝ-error scatter in every D2 cell |
| R7 | Drake symmetric arm never exactly symmetric | Cor 7.3 claim overreach | achieved-ε measured/reported; exact cancellation stays Tier-1 (executed machine zero); Drake claims ≥ 10× one-sided only |
| R8 | ES-01: whole-vector E2 rate "fails" for a reason the theorem statement must qualify | substantive finding mishandled as a bug | subspace-resolved three-rate design (§4.1); Q2 Path B statement; per-subspace-match/whole-vector-deviation is written up as the finding |
| R9 | Turn-window choice is a researcher degree of freedom | manufactured/destroyed slope | one pre-registered rule in shared code, applied uniformly both tiers; ±50 % sensitivity appendix; rule in the manifest |
| R10 | Claim leakage in captions/movies ("validates Thm 7.2" on a D_ss panel; 400× headlined) | the program's integrity position collapses | CaptionRegistry + CI lint (§1: `validat\w*` stem match over a sentence window; required hedges; registry-identity check; self-test over every plan-mandated caption); hedge printed **on** the E_F plot band; headline fixed one-sided ≥ 10×; final routing audit |
| R11 | Label inversion recurs (the pilot's arms were inverted) | a headline conclusion flips sign | fuse_rule signatures pinned by unit test to executed ground truth; arm id travels in the config hash, never a free-text label |
| R12 | Broadside/slack excursions corrupt cell statistics | biased means | binding TautCertificate + 1 %-window exclusion + published counts; divergence flags (ANEES > 10) reported per cell; > 20 % invalidation ⇒ trajectory redesign, not attrition |
| R13 | Runtime blow-up (1 kHz SAP + ~30 Python LeafSystems × ~2 300 runs) | campaign infeasible | runtime is a **measured gate** (WS-0, PILOT-6); vectorized per-agent sensor suite + single hydro system; window-focused 120 s trajectories; pre-declared descope order (§9.3) |
| R14 | Drake API drift (constraints, reaction ports, Meshcat names) | build breakage or silent semantics change | version pinned 1.51.1; §14 checklist of the Drake plan reruns on any bump; VectorRingDelay and anim2d are dependency-free fallbacks |
| R15 | Underpowered slope/ratio claims after Holm–Bonferroni | claims neither pass nor fail | three-outcome convention binding; pilot-driven sizing; ≥ 12 formations; ≥ 1.5-decade grids; lengthen windows/add formations before seeds |
| R16 | Q9/Q2 author decisions stall the campaign | schedule slip | both carried as gates with shipping defaults (§11): Q9 default = executed switch-offs + one-sentence F = 0 concession; Q2 default = Path B; neither blocks any cell above |

---

## 11. Decision gates for the author (each with a concrete recommendation)

| # | Decision | Status | Recommendation |
|---|---|---|---|
| Q1 | Transport level / fusion rule | **RESOLVED (executed):** (c) Thm 7.2 lives at error-transport level + (a) deployed estimator uses the paper's rule | none — consequences executed (E3a/E1 done; frozen-shape null established) |
| Q2 | Path A/B on Thm 6.3 | open | **Path B**: frozen statement + E2 empirical closure declared **inside §VIII** ([PUB] fallback); Path A (nonlinear upgrade) named as the open problem; E2's subspace-resolved design (§4.1) serves both |
| Q3 | α_k for m > 2 | open | (c)+(b): restrict the source-quoted C_hol comparison to m = 2 (Lem 7.1); publish sim-derived α_k for m ∈ {3, 4} flagged as a contribution; confirm α₁ − α₂ = 1 at m = 2 (one line) |
| Q5 | Integrator order vs [PUB] R9's "RKMK4" | open | amend R9 to "order-1 Lie–Euler + T1-E10 h-invariance + named Lie–Trotter/Strang baselines" — the sweep, not the order, is the defense; upgrade to CG2 only if E10 shows drift |
| Q6a | Weight convention | decided here | **SERIES pinned** (Def 4.1); regenerate the published 2.17→0.08 (harmonic) as series numbers before any λ₂ artifact ships (V2V-5: 1.0851→0.0421); `laplacian.py`'s switch runs the one-line sensitivity check |
| Q6b–d | ι constant; γ (drag); c, r_T, r₀, W | open | **the Drake plant resolves γ physically** — real drag model, executed tensions 2.35–2.56 kN; pin ι's constant so nominal λ₂ is O(1) at the executed config; **QD3:** re-pin the vM calibration at Drake scale — c such that sd = 1° at T = 2.5 kN (sim_design's "1° at 100 N" presupposed ~100 N tensions; at 2.5 kN it implies an implausible 0.04° sensor). Keep the A10 T² scaling; state the calibration point in both papers |
| Q7 | "Symmetric formation" + ε at N ≥ 4 | open — **this plan proposes the definition** | (i) Tier-1 symmetric at any N: identical shape pairs on the walk (Cor 7.3's hypothesis, realizable in reduced coordinates); (ii) Drake symmetric class: equal fan angles + equal cable lengths on the pentagon front arc (mirror symmetry about the bow axis), **achieved-ε measured and reported**; (iii) ε-perturbation: declared unit vector in one named agent's (σ, σ_i) with ‖Dc·d‖ > 0 asserted at load. Author to ratify |
| Q8 | Remaining falsifier numbers | proposed | Ĉ/C_hol ∈ [0.9, 1.1]; collapse = λ_min reaching 10⁻³·λ₂(unpinned); 𝒦 margin 0.10; η_min = 0.05; ‖c_i − c_j‖ < 1e-12; P₁ = information of sim_design.tex:42's beacon; beacon t_on = final-30 m entry (hero) / t = 0.7·T (T1-E1) **[GAP — confirm t_on]** |
| Q9 | F = 0 integrable variant | open | default that ships: exhibit the free switch-offs — **three executed machine-zero arms (s_i≡s_j, η=0, ξ=0) plus the fitted τ→0 slope-2 decay of the generic curve** (the explicit τ = 0 arm of §4.0(vii) upgrades that row to executed) — and state the concession in one sentence ("two of Rem 7.4's three switch-offs are exhibited numerically; the integrable-variant construction is left open"); derive it if desired — nothing blocks on it |
| Q10 | E4/E5 | **AMENDED: deferred OUT OF THIS CYCLE** — the RA-L campaign defined here (D1–D10) contains no Maupertuis cell, so "deferred to RA-L" had no executor; recorded honestly | flagship §VII: pointers only, Thm 8.1 proved-but-unillustrated; **[PUB] F7 cut from the flagship figure set** (no producer this cycle); `fig6_landscape.png` **banned from reuse** until re-run — a re-run this plan does NOT schedule (Q15 owns it) |
| **Q11** | [PUB] factual corrections (plan-v2 Q11: **V1–V9 → V1–V6** in four places; the **R12 inversion** + its unsupported [10, 50] band; §VIII(a)/F4's Ĉ-vs-C_hol restricted to **m = 2**; §VIII(b)'s heterogeneous-lag headline scoped out of the theorem test) | open — previously missing from this table while its downstream consequences were already implemented in the cells | **accept plan-v2's corrections wholesale**; owner: the flagship drafting pass, executed with the wk 10–11 audit (§9.1); until applied, [PUB] is never cited for V7–V9 (they do not exist — §0.2) |
| Q12 | L-CSS timing | **RESOLVED:** E3a executed (slope 1.999, switch-offs, coefficient 1.0000) supports the letter's headline | submit the letter; cite the executed artifacts |
| Q13 | plan-v2 "(inferred)" numbers | open, minor | extend `verify_plan_v2.py` during Wk 1–2 spike work; downgrade the rest to (inferred) in manuscript-facing text |
| Q14 | Drake M5 cell | **RESOLVED to (i):** D3 exists | none — the PROV overlay (F4a-overlay) is thereby created |
| **QD1** | D2 primary trajectory | new [DESIGN] | **persistent-turn primary** for the fit (clean window; matches Tier-1 E3b) + dogleg as the demonstration arm; ratify |
| **QD2** | Default Drake sensor suite | new [DESIGN] | **no relative range–bearing** (correction to Drake plan §4.1; preserves BHT's novelty premise); B3 keeps the synthetic sensor; ratify |
| **QD4** | τ = 1.6 s in closed loop | new | keep in grid; PILOT-6 decides retention (divergent seeds flagged, fit on the floor-dominated regime); if dropped, the grid still spans 1.204 decades and the Tier-1 grid carries the 1.5-decade claim |
| **QD5** | Tier-1 scheduling repair: plan-v2 §8.0c's Δ_c = 0.025 s violates plan-v2's own load invariant against dt = 0.01 s (0.025/0.01 = 2.5), and E10's dt = 0.02 breaks both the 20 Hz update (0.05/0.02 = 2.5) and Δ_c | new — **a blocking contradiction inherited verbatim from plan-v2, resolved here with a shipping default** | **Δ_c = 0.05 s** (the τ grid {0.05 … 1.6} stays exact with lag ∈ {1 … 32} ≥ 1; integer against dt ∈ {0.001, 0.0025, 0.005, 0.01} and the 50/20 Hz cadence) + **E10 grid swaps 0.02 → 0.001** (refinement replaces coarsening). Recorded as a delta in §3.3/§4.0. Author ratifies — these are pre-registered protocol numbers |
| **Q15** | Landing site for E4/E5 + the Maupertuis planner (and with them sim_design's B4/B5 ablations — §3.1's recorded drop) | new — Q10's deferral needs a defined executor; this plan's RA-L campaign has none | **author decision:** (a) a scoped RA-L revision/extension cell after this campaign ships, or (b) a fourth publication unit. Until decided, the recorded status everywhere is "deferred out of this cycle, landing site open (Q15)" — never "deferred to RA-L"; the `fig6_landscape.png` re-run is week 1 of whichever unit wins |

*Numbering notes: plan-v2's Q4 has no row because its recommendation is already served — "C18
makes this a figure rather than a paragraph" (plan-v2 Q4, verbatim) and C18's B2 arm is carried in
T1-E1/D7. QD3 (vM calibration re-pin at Drake-scale tensions) lives inside the Q6b–d row. The
numbering gaps are intentional on their face.*

---

## Appendix A — Experiment → claim → theorem → falsifier → figure → paper (both tiers)

| Experiment | Claim(s) | Theorem [label] · status | Key falsifier (numeric) | Figure/artifact | Paper |
|---|---|---|---|---|---|
| T1-E3a (**executed** + extension) | C7a, C8, C8b, C9b′, C15, C18 | Thm 7.2 [thm:floor] + Lem 7.1 [lem:bch] · **PROV** (leading-order, deterministic) | 2 ∉ slope CI; Ĉ/C_hol ∉ [0.9, 1.1] at m = 2; C15 CI includes [1.8, 2.2]; O(τ³) residual fails | F4a + insets, F6 | LCSS headline; TCNS §VIII |
| T1-E9 (**executed**, free controls) | C13 | Rem 7.4 + plan-derived · PROV | amplitude survives any of τ→0, ξ=0, η=0, s_i≡s_j ⇒ bug | switch-off table (main text) | TCNS §VIII |
| T1-E10 | C14 | — (R9 defense) · DESIGN | exponent/coefficient CIs disjoint across Δt | F4a inset | TCNS §VIII |
| T1-E2 | C6, C19 | Thm 6.3 [thm:contract] · PROV LTV/frozen; ES-01 qualified; Lem 6.2 [lem:loglin] · PROV 1st order | slope(rate vs κλ₂) < 0.5; C19 residual ∉ [1.8, 2.2] | F8 | TCNS §VIII (+supp C19) |
| T1-E3b | C7b | none — [ES §10(ii)] · **CONJ** | 2 ∉ p CI (fit D₀ + Cτ^p) | F4b | TCNS §VIII |
| T1-E3c | C9a, C9b, C9b′, C9c | Cor 7.3 [cor:sym] · PROV (C9a); C9b/b′ NEW; C9c DESIGN | 3 ∉ symmetric slope CI; 1 ∉ amp-ε CI; 2 ∉ D_ss-ε CI; robust S < 10× @ τ = 0.4 | F5 | TCNS §VIII |
| T1-E1 (spectral **executed**; closed-loop remaining) | C3, C4, C5, C17, C18 | Thm 5.1 [thm:gauge], Cor 5.2 [cor:pin], Cor 5.3 [cor:inherit] · PROV; C17 admission | dim ker ≠ 3; σ₄/σ₃ > 0.1; no collapse in 10 s; ANEES ∉ [0.8, 1.3]; B2 kernel-section residual < 1e-9 | F3, F8 | TCNS §VIII |
| T1-E6 | C10 | none · CONJ/open | (exploratory) | F4b overlay | TCNS §VIII |
| D1 | filter consistency | Def 6.1; Thm 6.3 hypothesis, ES-01 quoted | ANEES ∉ [0.8, 1.3]; FD-Jacobian mismatch (§5.4 D1's pre-registered check) | consistency panel | RA-L |
| D2 | closed-loop floor (CONJ); motion×curvature mechanism (DESIGN) | [ES §10(ii)] · **CONJ**; caption hedge mandatory | 2 ∉ p CI (reported); straight not ≥ 10× below maneuvering; frozen replay ≠ machine zero ⇒ halt | floor log-log; "no motion, no floor" figure | RA-L |
| D3 | closed-loop holonomy amplitude | Thm 7.2 · **PROV** (only Drake cell naming the theorem unhedged-by-conjecture) | noise-off slope ∉ [1.8, 2.2]; Ĉ/C_hol ∉ 1 ± remainder bound | M5 log-log; F4a-overlay half | RA-L (+TCNS supp pointer) |
| D4 | closed-loop symmetry suppression | Cor 7.3-motivated; achieved-ε caveat | S < 10× one-sided @ τ = 0.4; ε-exponents outside CIs | suppression heatmap; split-screen movie | RA-L |
| D5 | gauge drift + beacon snap | Thm 5.1 + Cor 5.2 · **PROV** (validation language allowed) | σ₄/σ₃ > 0.1 pre-beacon; no 10 s collapse; complement unbounded | rank waterfall; gauge-snap movie | RA-L |
| D6 | tension channel information | Def 4.1 + Cor 5.3 (monotone CONJ); A10 named | ablation ΔCI ∋ 0; dose-response slope ≥ 0 | dose-response figure | RA-L |
| D7 | end-to-end BHT vs B0/B1/B2/B3 | none (system claim); C18 closed-loop consequence | DIEKF-Σ ≤ B2 at matched comms | headline scorecard table | RA-L |
| D8 | anti-artifact battery | C14-class · DESIGN | CIs disjoint across h or cable model | h-sweep inset; A/B differencing | RA-L (+TCNS supp inset) |
| D9 | scaling | Thm 5.1 PROV; Thm 6.3 LTV; trend CONJ | Spearman CI ∋ 0; ring exponent CI excludes −2 (N ≥ 4) | scaling montage | RA-L |
| D10 | robustness outside premise | outside Lem 3.1 domain / outside 𝒫 — stated | (characterization; red flags reported) | slack/re-lock, guard-save movie | RA-L |
| XT overlay | implementation-independence of exponent/coefficient | F4a-overlay: Thm 7.2 PROV hedge; F4b-overlay: CONJ hedge mandatory | equivalence test §6: difference CI ⊄ [−0.2, 0.2] or ratio CI ⊄ [1/1.3, 1.3] ⇒ finding/UNDER-POWERED, localization ladder | twin-panel overlay | RA-L centerpiece; TCNS supp |
| Hero movie + gallery | integration showcase | on-screen hedges per CaptionRegistry | scorecard thresholds; median-seed rule | BHT film suite, gallery 3 | RA-L video; TCNS supp 30 s cut |

---

*End of plan. The bar this document holds itself to: a senior PhD student executes it without
asking questions; a hostile reviewer finds the epistemic discipline airtight; and every claim the
papers make traces to a cell, a falsifier, and a hedge that was pre-registered here.*
