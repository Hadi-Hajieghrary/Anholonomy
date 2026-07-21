# Refs + Papers ↔ Campaign Reconciliation (2026-07-21)

A pass over the theory source, the planning/audit corpus, and the three papers,
reconciling every falsifiable claim against the **executed** campaign
(frozen ledger: [`docs/ral_package.md`](ral_package.md)). Method: a 6-cluster
finder workflow (theory source, paper fidelity, `sim_design`, publication plan,
supporting refs, companion theory) with adversarial grounding of each proposed
edit against the committed records. Discipline is **additive** — annotate
adjudicated conjectures, mark untested/superseded material, fix outright errors;
no proven theory was rewritten.

> `refs/` is gitignored and unversioned. A full fresh backup was taken before
> any edit (`scratchpad/refs_backup_2026-07-21/`, 42 files). The annotations
> below live in the author's working corpus; this file is the tracked record.

## Papers — fidelity verdict: CLEAN (no edits needed this pass)

The three papers were already audited twice for numbers/labels (`5f78235`,
`7ff0982`). On the *fidelity-to-source* axis they check out:
- theorem statements carry the source's epistemic tags verbatim
  (`\provtag`/`\conjtag`); the floor theorem's "leading order, deterministic;
  … stochastic steady-state floor: [Conjectural]" hedge is present in all three;
- **no** planner/Maupertuis claim leaks in (the papers are correctly scoped to
  gauge / floor / contraction — the untested branch is absent);
- **no** place captions or describes a `D_ss` fit as validating the amplitude
  theorem; the amplitude (PROV) and `D_ss` (CONJ, falsified-at-scale) are kept
  distinct everywhere;
- the C15 level-set result is presented as an **observation** (proof open), not
  as proved, in both the letter and §VIII.

## `refs/estimation_sheaf.tex` (theory source) — annotated, still compiles (8 pp)

A `\camp` (Campaign-outcome) environment was added; the proven mathematics is
untouched. Adjudications recorded next to the relevant statements:

| Claim | Source tag | Campaign outcome recorded | Grounding |
|---|---|---|---|
| Thm floor — amplitude | `[Proved here]` | CONFIRMED both plants (slope 1.999/2.000, coeff 1.0000, switch-offs machine-zero) | C7a/C8/C13 |
| Thm floor — `D_ss` stochastic floor | `[Conjectural]` | **FALSIFIED at these scales** (1.101 [1.076,1.125] T1; 1.077 [1.054,1.102] Drake; excludes 2 and 1) | C7b, C7b-Drake |
| Cor sym (symmetry protection) | `[Proved here]` | **Extended** (observed): protected class = level set of s↦C(s;ξ), discrete, exact all-orders (C15). Closed-loop robust suppression **TRIPS** at 2.75× (< ≥10×); large protection is amplitude-only | C15, C9c |
| Cor inherit — monotone rate | `[Conjectural]` | **REFUTED**: pin rate λ₂-independent (ρ=+0.04); D re-lock anti-orders (ρ=−0.51). Floor: connectivity 5×→2× | D9, C10 |
| Thm contract | `[Proved here]` (LTV) | κλ₂ term CONFIRMED (slope 1.403). Premise refined: μ = −0.062 at κ=0 (consensus does the contraction). C19 remainder faster than order 2 | C6, C19 |
| Thm gauge / Cor pin | `[Proved here]` | CONFIRMED (dim ker = 3, section ~1.3e-15; anchor collapses kernel). Numerics-invariance passed | E1, E10/D8 |
| §8 Maupertuis, Def cap2, refraction, roadmap (vi) E4/E5 | `[Proved here]`/`[Conjectural]` | **UNTESTED** — planner deferred (Q10); no numerical evidence | ledger scope |
| §11 verification manifest | — | pointer added to the full Tier-1+Drake campaign as extended verification | — |

## `refs/sim_design.tex` (pre-registration) — E1–E8 outcome box added (compiles, 5 pp)

`E1` MET · `E2` MET + μ<0 refinement · **`E3` SPLIT** (amplitude passes; `D_ss`
slope-2 **falsified**; symmetric ≥10× **trips** to 2.75×; ε² overturned) ·
**`E4`/`E5` NOT RUN** (planner deferred) · `E6` MET (exploratory) · **`E7`
PARTIAL** (ANEES<3 only at the 130 s horizon; slack scoped out) · `E8` run,
docking spec unmet by all arms.

## `refs/ieee_transactions_publication_plan.md` — marked (open in the author's IDE)

Top **campaign-status banner** + inline marks:
- **F4** — CONFLATION HAZARD: no slope-2 guides on a `D_ss` panel (measured ≈1.08).
- **F5 / R12** — OVERTURNED: "headline 10–50×, 400× ideal" → robust suppression
  trips at 2.75×; 400× unsupported; ε² curve wrong.
- **R3 / C5-edit-3** — the CONJ steady-state O(τ²) is *falsified-at-scale*, not
  merely open.
- **C6 / §VII** — UNTESTED (planner deferred).
- **C4** — resolved via Path B (E2/C6 slope 1.403; the μ=−0.062 nuance).

## Supporting refs — status banners

- `tier1_simulation_plan_v2.md` — EXECUTED banner (author decisions resolved,
  falsifiers adjudicated; the "μ>0" premise contradicted).
- `blind_harbor_drake_simulation_plan.md` — EXECUTED banner (C2 falsified on
  Drake; **C4 ~400× overturned**; coefficient ratio disagrees ×5; ANEES horizon).
- `tier1_simulation_implementation_plan.md` (v1.0) — SUPERSEDED banner
  (slope-2 `D_ss` target conflates amplitude with the falsified closed-loop floor).
- `constraint_geometry_tutorial.tex` — MIRROR banner (byte-identical to
  `_v3_1.tex`, md5 `b419ba26…`; `_v3_1` is the source of record).

## Companion theory (`propagation`/`observer`/`infokinetic`) — no change

These are `[Established]` imports (S1–S5). The campaign exercises them only
indirectly (broadside sec-conditioning via the λ₂ collapse and broadside margin;
observability via E1) and contradicts none; left intact.
