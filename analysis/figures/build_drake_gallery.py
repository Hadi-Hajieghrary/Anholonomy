"""Build the Drake Blind Harbor gallery HTML (self-contained, data-URI assets)."""
import base64, os

R = "/workspaces/Anholonomy/tier2_drake/results"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drake_gallery.html")


def b64(path, mime):
    with open(path, "rb") as fh:
        return f"data:{mime};base64,{base64.b64encode(fh.read()).decode()}"


hero_mp4 = b64(f"{R}/s1/hero_blind_harbor.mp4", "video/mp4")
dogleg_mp4 = b64(f"{R}/s1/hero_dogleg_web.mp4", "video/mp4")
montage = b64(f"{R}/s1/hero_montage.png", "image/png")
f4 = b64(f"{R}/s1/f4_cross_tier_overlay.png", "image/png")
f4c = b64(f"{R}/s1/f4c_variance_attribution.png", "image/png")
f4b = b64(f"{R}/s1/f4b_overlay.png", "image/png")
f4a = b64(f"{R}/s1/f4a_overlay.png", "image/png")
tow5 = b64(f"{R}/tow_N5.mp4", "video/mp4")
comp = b64(f"{R}/tow_comparison.png", "image/png")

HTML = f"""<title>Blind Harbor — Drake N-agent gallery</title>
<style>
:root {{
  --paper:#f6f4ee; --ink:#1d2433; --ink-2:#4a5266; --line:#d8d3c4;
  --card:#fffdf7; --navy:#2b3550; --gold:#b3861d; --gold-soft:#f3e8c8;
  --good:#3f6b3a; --bad:#a03d2c; --mono:'SFMono-Regular',ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --paper:#161a24; --ink:#e8e6df; --ink-2:#a8adbd; --line:#333a4d;
          --card:#1e2431; --navy:#9fb0d8; --gold:#d4b04a; --gold-soft:#3a3220;
          --good:#8fbc8a; --bad:#d98a7a; }}
}}
:root[data-theme="dark"] {{ --paper:#161a24; --ink:#e8e6df; --ink-2:#a8adbd; --line:#333a4d;
          --card:#1e2431; --navy:#9fb0d8; --gold:#d4b04a; --gold-soft:#3a3220;
          --good:#8fbc8a; --bad:#d98a7a; }}
:root[data-theme="light"] {{ --paper:#f6f4ee; --ink:#1d2433; --ink-2:#4a5266; --line:#d8d3c4;
          --card:#fffdf7; --navy:#2b3550; --gold:#b3861d; --gold-soft:#f3e8c8;
          --good:#3f6b3a; --bad:#a03d2c; }}
body {{ background:var(--paper); color:var(--ink);
  font:16px/1.6 Georgia,'Times New Roman',serif; margin:0; }}
main {{ max-width:60rem; margin:0 auto; padding:2.5rem 1.25rem 4rem; }}
h1 {{ font-size:1.9rem; line-height:1.2; margin:0 0 .3rem; text-wrap:balance; }}
h2 {{ font-size:1.25rem; margin:2.8rem 0 .6rem; border-bottom:1px solid var(--line);
     padding-bottom:.35rem; }}
.sub {{ color:var(--ink-2); margin:0 0 1rem; }}
.chips {{ display:flex; flex-wrap:wrap; gap:.5rem; margin:1rem 0 0; }}
.chip {{ font-family:var(--mono); font-size:.72rem; letter-spacing:.04em;
  padding:.25rem .6rem; border:1px solid var(--line); border-radius:99px;
  background:var(--card); color:var(--ink-2); }}
.chip b {{ color:var(--good); font-weight:600; }}
video, img {{ max-width:100%; border:1px solid var(--line); border-radius:6px;
  background:#fff; display:block; }}
figure {{ margin:1rem 0; }}
figcaption {{ font-size:.85rem; color:var(--ink-2); margin-top:.5rem; }}
.note {{ background:var(--gold-soft); border-left:3px solid var(--gold);
  padding:.7rem 1rem; font-size:.9rem; margin:1.2rem 0; border-radius:0 6px 6px 0; }}
.tablewrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; font-size:.85rem; width:100%; margin:.8rem 0;
  font-variant-numeric:tabular-nums; }}
th, td {{ border:1px solid var(--line); padding:.4rem .7rem; text-align:right; }}
th:first-child, td:first-child {{ text-align:left; }}
th {{ background:var(--card); font-family:var(--mono); font-size:.72rem;
  letter-spacing:.03em; }}
.win td {{ background:var(--gold-soft); }}
.mono {{ font-family:var(--mono); font-size:.85em; }}
.k {{ color:var(--ink-2); }}
footer {{ margin-top:3rem; font-size:.78rem; color:var(--ink-2);
  border-top:1px solid var(--line); padding-top:1rem; }}
</style>
<main>
<h1>Blind Harbor — GNSS-denied multi-vessel towing on Drake</h1>
<p class="sub">Five autonomous vessels tow a pentagon caisson through a coordinated
turn with no global positioning. Each runs the DIEKF-&Sigma; estimator on gyro +
cable-direction sensing, fusing delayed packets; a single docking beacon on one
vessel pins the whole fleet's estimate (Cor&nbsp;5.2).</p>
<div class="chips">
  <span class="chip">Drake 1.51 &middot; SAP contact &middot; distance-constraint cables</span>
  <span class="chip">production <b>702 runs</b> (D2 six-&tau; grid + controls + A1/A2 arms; D4 reduced slice)</span>
  <span class="chip">M-FAB gate <b>closed</b> (ANEES 3.96, author-ruled gate [0.8,&thinsp;5.0])</span>
  <span class="chip">truth-isolation lint <b>green</b></span>
</div>

<h2>1 &middot; Hero transit — the Blind Harbor dogleg (plan &sect;7 storyboard, v1)</h2>
<figure>
<video controls loop src="{dogleg_mp4}"></video>
<figcaption>The full 400&nbsp;m GNSS-denied transit at &times;9 compression, hero seed
selected by the documented median-D<sub>ss</sub> rule (12-seed v1 subset, never
cherry-picked). Five beats: INIT-1 calibration &middot; Leg&nbsp;1 (the five ghost
caissons drift as <em>one rigid gauge orbit</em> &mdash; the fleet knows its shape,
not its place, Thm&nbsp;5.1; kernel error grows unbounded while complement error stays
100&times; smaller) &middot; THE TURN (disagreement blooms out of the noise intercept
into the shaded band; the on-plot label carries the mandated hedge verbatim) &middot;
Leg&nbsp;2 relaxation &middot; BEACON + DOCK (one anchor kills the gauge, Cor&nbsp;5.2;
the D-spike at acquisition is the pin propagating). The scorecard reports anchored /
fleet-mean / fleet-max estimate errors each ticked against the 0.5&nbsp;m criterion
&mdash; positions read 0.77 / 1.44 / 2.03&nbsp;m (&#10007;) at 34&nbsp;s
post-acquisition: network-diffusion-limited (&tau;<sub>net</sub>&nbsp;&asymp;&nbsp;21&nbsp;s
vs a ~40&nbsp;s window at tow speed), with heading 0.4&deg; (&#10003;) and cables taut
(&#10003;). v1 disclosed deltas: fixed &tau;&nbsp;=&nbsp;0.31&nbsp;s (no jitter/drops),
time-triggered beacon at ~36&nbsp;m, no deceleration profile &mdash; the v2 decelerating
approach physically extends the convergence window.</figcaption>
</figure>
<figure>
<video controls loop src="{hero_mp4}"></video>
<figcaption>N=5, &tau;=0.4&nbsp;s staleness, coordinated turn &mdash; a single
illustrative run (seed 0); the pin-and-converge behavior is quantified across seeds in
the gate campaign (&sect;4). Dashed pentagons are each vessel's <em>own</em> estimate of
the load pose &mdash; their spread <em>is</em> the disagreement D(t); their common offset
is the free gauge. At t=30&nbsp;s the docking beacon (gold star) activates on one vessel:
D(t) briefly <em>spikes</em> &mdash; that agent snaps to truth while the others still
carry the drifted gauge &mdash; then fusion propagates the pin and the fleet
converges.</figcaption>
</figure>
<figure>
<img src="{montage}" alt="three-phase montage">
<figcaption>The three phases. Left: gauge free &mdash; the five ghosts drift
<em>coherently</em> (they overlap each other while offset from truth, the sheaf's gauge
freedom made visible). Middle: beacon pins one agent; the fleet is mid-convergence.
Right: converged through the turn.</figcaption>
</figure>

<h2>2 &middot; Cross-tier overlay — three distinct objects, three measured exponents</h2>
<figure>
<img src="{f4}" alt="cross-tier overlay">
<figcaption>Measured scaling laws on one axis, with the straight-tow control. Drake
round-trip transport defect (O(&tau;), dominated by inter-agent estimate mismatch, not
the theorem's geometric term): exponent 1.003&nbsp;[1.003,&thinsp;1.004]. Drake
steady-state disagreement D<sub>ss</sub>, turn arm: maneuver-excess exponent
1.077&nbsp;[1.054,&thinsp;1.102] over the full six-point grid, with D&#8320; measured in situ by the control arm
(open markers). Tier-1 error-transport holonomy amplitude: slope 1.999 with switch-off
arms at machine zero &mdash; the slope-2 line is <em>Tier-1 data</em>; the Drake measurement of the same object is the capstone panel (a) (D3).</figcaption>
</figure>
<div class="note"><b>Epistemic ladder.</b> These are three distinct objects.
(i)&nbsp;The &tau;&sup2; error-transport holonomy is the quantity of Thm&nbsp;7.2
(leading-order, deterministic; PROV) &mdash; its leading-order analysis is also what
elevates the O(&tau;) transport defect to O(&tau;&sup2;) in the error dynamics.
(ii)&nbsp;The D<sub>ss</sub> floor is a measured closed-loop quantity in the
<em>conjectured</em> stochastic regime, and the pre-registered adjudication is now
complete: with D&#8320; <em>measured in situ</em> by the straight-tow control arm
(6.8e-4, ~20&times; below signal at every &tau;), the maneuver-excess exponent over the full pre-registered grid (&tau; &isin; {{0.05&hellip;1.6}}, 1.51 decades) is
p&nbsp;=&nbsp;1.08&nbsp;[1.05,&thinsp;1.10] &mdash; the conjectured order 2 is excluded,
and <b>C7b-Drake is falsified at these scales</b> (a CONJ falsification, reported per
the committed outcome ladder, plan &sect;10 R2). The earlier joint-fit exponent 1.73
was a model-degeneracy artifact: the free-D&#8320; mixture fit assigns
D&#8320;&nbsp;=&nbsp;9.6e-3, which the control experiment directly refutes (13&times;
smaller measured). Closed-loop disagreement on the full plant is dominated by the
first-order estimate-mismatch channel &mdash; the &tau;&sup2; holonomy object is
resolved only in the noise-off setting (Tier-1, machine-zero switch-offs).
(iii)&nbsp;The O(&tau;) defect is the first-order estimate-mismatch term &mdash; a
measured closed-loop quantity, not a theorem object.</div>

<h2>2b &middot; The capstone: one estimator, two plants, two panels</h2>
<figure>
<img src="{f4a}" alt="F4a cross-tier overlay (PROV)">
<figcaption><b>Panel (a) — the theorem's object (PROV).</b> The error-transport
holonomy amplitude of Thm&nbsp;7.2 (leading-order, deterministic), measured on both
plants. Tier-1 E3a: slope 1.999 with all switch-offs at machine zero. Drake D3:
generators built from the estimator's own closed-loop shape/twist states &mdash;
slope 2.000, the m=2 coefficient check amp/&tau;&sup2;&#8214;[C<sub>i</sub>,C<sub>j</sub>]&#8214;
= 1.0000, the &eta;=0 switch-off exactly zero, and the parallel (theorem-symmetric)
class suppressing the coefficient 31&times; (achieved-&epsilon;; exact cancellation
remains Tier-1's machine-zero result). The &tau;-law is the theorem's prediction;
the measured content is the coefficient and the switch-offs. Note the object
separation: Cor&nbsp;7.3's protection is large (31&times;) on the holonomy amplitude
&mdash; its own object &mdash; while closed-loop D<sub>ss</sub> showed only ~2&times;,
because D<sub>ss</sub> is mismatch-dominated, not holonomy-dominated.</figcaption>
</figure>
<figure>
<img src="{f4b}" alt="F4b cross-tier overlay">
<figcaption>Tier-1/Tier-2 agreement on the conjectured steady-state floor
([ES &sect;10(ii)]). Panel (a) separately tests the leading-order, deterministic
holonomy amplitude of Thm&nbsp;7.2 in both tiers. The Tier-1 cell (E3b: reduced
plant, moving shapes, persistent turn, 1584 runs, identical estimator config)
measures excess exponent 1.101&nbsp;[1.076,&thinsp;1.125]; Drake measures
1.077&nbsp;[1.054,&thinsp;1.102]; the pre-registered equivalence test passes
(difference +0.023&nbsp;[&minus;0.012,&thinsp;+0.057] &sub; [&minus;0.2,&thinsp;0.2]).
The conjectured order 2 is excluded on <em>both</em> plants &mdash; C7b is falsified
coherently at these scales, and the agreement of two independent plants on the
honest answer is the strongest cross-tier statement the campaign makes. The
coefficient row, evaluated reference-matched (Drake's realized maneuvering shapes
exit the reduced model's stable domain &mdash; a validity-domain finding reported
per &sect;6), gives ratio 5.04&nbsp;[3.97,&thinsp;6.19] &mdash; outside the
pre-registered [1/1.3,&thinsp;1.3] band, reported as a plant-side disagreement
pending the localization ladder (candidates: inertia-free shape response;
Tier-1-only plant process-noise injection, visible as a 62&times; straight-tow
baseline gap). The Tier-1
frozen+noise-off regression reproduces the executed null (6e-30). A1's groupthink
signature reproduces on Tier-1; the A2 ablation ordering inverts across tiers
(regime-dependent) &mdash; a further reason D<sub>ss</sub> alone never ranks fusion
rules.</figcaption>
</figure>

<h2>3 &middot; Production campaign (D2 / D4)</h2>
<div class="tablewrap"><table>
<tr><th>&tau; [s]</th><th>D<sub>ss</sub> (mean, n=48)</th><th>round-trip defect (O(&tau;))</th></tr>
<tr><td>0.1</td><td>1.09e-2</td><td>1.86e-2</td></tr>
<tr><td>0.2</td><td>1.76e-2</td><td>3.55e-2</td></tr>
<tr><td>0.4</td><td>3.58e-2</td><td>6.94e-2</td></tr>
<tr><td>0.8</td><td>9.20e-2</td><td>1.37e-1</td></tr>
<tr><td>1.6</td><td>2.86e-1</td><td>2.73e-1</td></tr>
</table></div>
<p><b>Adjudicated fit (protocol-compliant).</b> The straight-tow control arm (120
matched runs) measures the no-maneuver disagreement directly: 5.2e-4 &rarr; 1.5e-2
across the &tau; grid, 19&ndash;21&times; below the turn arm everywhere. With that
control subtracted per &tau;, the maneuver-excess exponent over the full six-point grid is
p&nbsp;=&nbsp;1.077&nbsp;[1.054,&thinsp;1.102] (run-level bootstrap; the 5-point production subset gives 1.178&nbsp;[1.145,&thinsp;1.210]; per-formation range on that subset [1.177,&thinsp;1.178]). Segment slopes steepen up the grid (0.69&nbsp;&rarr;&nbsp;1.63) &mdash; a single power law is imperfect and a superlinear component emerges at high &tau; &mdash; but no segment approaches 2. The free-D&#8320; mixture fit's
p&nbsp;=&nbsp;1.73 is reported beside it as required but is refuted as an artifact:
its fitted D&#8320;&nbsp;=&nbsp;9.6e-3 contradicts the measured control
(6.8e-4). Falsifier status for C7b-Drake and the mechanism check are in &sect;2 and
below. Pre-registered scope notes: the &tau;=0.05 grid point, the frozen-replay
control, and the A1/A2 diagnostic arms remain pending.</p>
<p><b>Mechanism check &mdash; passed.</b> Arm (c)'s pre-registered falsifier required
the straight-tow floor &ge;10&times; below the maneuvering arm at &tau;=0.4; measured
20.2&times; (and 19&ndash;21&times; at every &tau;). The motion&times;curvature
excitation story stands: no maneuver, no floor &mdash; even though the excess that
motion excites scales first-order at these noise scales, not as the conjectured
&tau;&sup2;.</p>
<figure>
<img src="{f4c}" alt="variance attribution">
<figcaption>The variance-attribution figure (pre-registered outcome ladder, plan
&sect;10 R2): all Drake arms on matched formation draws. A2 (transport conjugation
ablated) runs 1.7&times;&rarr;8.2&times; above the paper rule with growing &tau; and
scales steeper (p=1.75) &mdash; the conjugated transport is load-bearing, increasingly
so with staleness (C18). A1 (naive consensus) holds D flat at 5.8e-3 &mdash;
<em>below</em> the paper rule &mdash; but that agreement is groupthink: its anchored
ANEES is 62 and its drift 8.4&nbsp;m (&sect;4 table). The straight-tow control shows
the motion excitation. Disagreement alone is not a virtue metric; the paper rule is
the only arm that agrees <em>and</em> is right.</figcaption>
</figure>
<p><b>Exponent stability across formation draws (empirical).</b> Across the 12
independently drawn formations of this draw-law (pentagon fan variants, N=5, cycle
graph), the maneuver-excess exponent is stable &mdash; per-formation slopes span
[1.177,&thinsp;1.178] &mdash; while the amplitude prefactor varies 21%. This is
consistent with the exponent being set by the delay process rather than the drawn
geometry, within this scenario family; formations shift D<sub>ss</sub> nearly
multiplicatively, so resampling them moves the prefactor but barely the exponent. The
run-level CI [1.145,&thinsp;1.210] carries the honest seed-noise uncertainty.</p>
<p><b>Symmetric-class floor ratio — pre-registered falsifier tripped.</b> Parallel-cable
formations (the symmetric class whose <em>leading-order holonomy</em> Cor&nbsp;7.3
(proven) concerns) measure D<sub>ss</sub>&nbsp;=&nbsp;1.72e-2 at &tau;=0.4 vs 3.58e-2
for generic fans: a 2.1&times; ratio. The pre-registered Drake headline was
&ge;10&times; one-sided; that falsifier <b>trips</b> and is reported as such per plan
&sect;5.4. Exact cancellation remains a Tier-1 result (machine-zero switch-offs,
executed); whether Cor&nbsp;7.3's mechanism explains any floor suppression is part of
the conjectured D<sub>ss</sub> regime, not a consequence of the corollary.</p>
<p><b>&epsilon;-ladder — under-powered, as pre-declared.</b> Grading asymmetry off the
parallel class raises the floor monotonically (1.72e-2&nbsp;&rarr;&nbsp;2.25e-2 over
&epsilon;=0&rarr;0.4 at &tau;=0.4). The excess-exponent fit gives q&nbsp;=&nbsp;1.5 with
seed-bootstrap CI [0.0,&thinsp;4.8] &mdash; consistent with both the conjectured
&epsilon;&sup2; and a linear law; this slice cannot adjudicate C9b. Confounds, stated:
one formation per &epsilon; point, &tau;=0.4 only, and &epsilon;=0.4 exceeds the
declared grid maximum of 0.2 (exploratory extension). The powered &epsilon;-exponent
test lives in Tier-1 E3c.</p>

<h2>4 &middot; Baselines — why the fusion rule matters</h2>
<div class="tablewrap"><table>
<tr><th>arm</th><th>anchored ANEES</th><th>complement ANEES</th><th>disagreement D</th><th>pre-anchor drift [m]</th></tr>
<tr class="win"><td>DIEKF-&Sigma; (paper rule)</td><td>3.57</td><td>3.04</td><td>0.097</td><td>1.68</td></tr>
<tr><td>B0 dead-reckoning (no fusion)</td><td>4.49</td><td>75.9</td><td>33.2</td><td>1.91</td></tr>
<tr><td>B2 naive consensus</td><td>61.8</td><td>21.1</td><td>0.83</td><td>8.35</td></tr>
<tr><td>B1-proxy all-anchored, &tau;<sub>min</sub></td><td>17.5</td><td>16.2</td><td>0.33</td><td>1.15</td></tr>
</table></div>
<p>Among the arms run so far (B0, B2, and a B1 proxy; the true centralized-EKF B1 and
the relative-pose B3 are pending), only the paper's transport-aware rule delivers
agreement, gate-passing covariance, and low drift at once: 8.6&times; lower disagreement
than naive consensus (342&times; lower than no fusion, a comparison that is trivially
large by construction), covariance inside the author-ruled gate, and the lowest drift of
the fusing arms. Naive consensus <em>agrees</em> &mdash; but on a badly mis-calibrated
estimate, with 4.4&times; the drift of running no fusion at all. <b>B1-proxy is not the
plan's centralized-EKF oracle</b> (not yet run); it approximates B1's information
advantage by giving every agent a beacon at minimum delay, and its ANEES reflects that
shortcut, not centralized fusion. A second attempt &mdash; a centralized zero-latency
WLS replay over all raw sensor streams &mdash; achieved D&equiv;0 and 40% lower
pre-anchor drift (1.0 vs 1.68&nbsp;m) but 2.2&times; <em>worse</em> steady-state
accuracy than the record (0.41 vs 0.183&nbsp;m): naive centralization does not beat
the record; its covariance-coupled measurement architecture carries real accuracy.
Kept as a negative result; the true joint-EKF B1 pends the D7 campaign.</p>
<div class="note"><b>Calibration status, disclosed.</b> These ANEES values are not
&chi;&sup2;-calibrated: the shipped filter is ~3&ndash;4&times; optimistic. The original
plan gate was [0.8,&thinsp;1.3]; the shipping gate [0.8,&thinsp;5.0] is an author-ruled
widening justified by the covariance-architecture elimination table (decorrelated CI
over mutually-correlated estimates is structurally optimistic). The declared one-sided
complement sanity bound (&le;&thinsp;1.3) <b>failed</b> in the gate campaign
(complement ANEES 3.35) and is reported here as such. Chip value 3.96 = the 6-seed gate
campaign; table value 3.57 = the separate baselines run set.</div>

<h2>5 &middot; Scenario</h2>
<figure>
<video controls loop src="{tow5}"></video>
<figcaption>The physical scenario: five ASVs, taut distance-constraint cables,
pentagon caisson (circumradius 4&nbsp;m), hydrodynamic drag, thrust sized for a
0.9&nbsp;m/s tow.</figcaption>
</figure>
<figure>
<img src="{comp}" alt="formation comparison">
<figcaption>Symmetric vs perturbed attachment geometry (N=4 and N=5 configurations).</figcaption>
</figure>

<footer>Blind Harbor S1 campaign &middot; DIEKF-&Sigma; = distributed invariant EKF with
covariance-intersection fusion (Joseph-form updates, decorrelated CI, declared Q)
&middot; gates: truth-isolation lint, WS-0 replay parity, anchored ANEES &isin; [0.8, 5.0]
(author-ruled) &middot; data: production_d2_d4_v2.json, baselines.json, s1_verdict.json
&middot; 2026-07-18</footer>
</main>
"""

with open(OUT, "w") as fh:
    fh.write(HTML)
print(f"wrote {OUT}  ({os.path.getsize(OUT)/1e6:.1f} MB)")
