"""Build a self-contained HTML results gallery with all media embedded as data URIs."""
import base64
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
OUT = "/tmp/claude-1000/-workspaces-Anholonomy/3a36d322-c72b-4eff-acdc-cc60e2f82f83/scratchpad/tier1_results_gallery.html"


def data_uri(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


F4A = data_uri(os.path.join(RES, "e3a_amplitude.png"), "image/png")
F3 = data_uri(os.path.join(RES, "e1_gauge.png"), "image/png")
DIAG = data_uri(os.path.join(RES, "e3_diagnostic.png"), "image/png")
MOV = data_uri(os.path.join(RES, "gauge_drift.mp4"), "video/mp4")

HTML = f"""<style>
:root {{
  --paper:#f6f7f9; --panel:#ffffff; --ink:#151a21; --ink-soft:#3c4653; --ink-faint:#6b7683;
  --line:#e2e6ec; --line-soft:#eef1f5;
  --signal:#b2182b; --prov:#1b7837; --conj:#a8741a; --diag:#2166ac;
  --prov-bg:#e9f3ec; --conj-bg:#f6efe0; --diag-bg:#e7eef7; --signal-bg:#f6e7e9;
  --shadow:0 1px 2px rgba(20,26,33,.04), 0 8px 28px rgba(20,26,33,.06);
  --serif:Charter,'Bitstream Charter','Iowan Old Style',Georgia,'Times New Roman',serif;
  --sans:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --paper:#0f1319; --panel:#161c24; --ink:#e8ecf1; --ink-soft:#b3bcc7; --ink-faint:#7c8794;
    --line:#252d38; --line-soft:#1c232c;
    --signal:#e8607a; --prov:#5fb87f; --conj:#d6a94a; --diag:#6fa3d8;
    --prov-bg:#16241b; --conj-bg:#271f10; --diag-bg:#132234; --signal-bg:#2a151a;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 10px 30px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="light"] {{
  --paper:#f6f7f9; --panel:#ffffff; --ink:#151a21; --ink-soft:#3c4653; --ink-faint:#6b7683;
  --line:#e2e6ec; --line-soft:#eef1f5;
  --signal:#b2182b; --prov:#1b7837; --conj:#a8741a; --diag:#2166ac;
  --prov-bg:#e9f3ec; --conj-bg:#f6efe0; --diag-bg:#e7eef7; --signal-bg:#f6e7e9;
}}
:root[data-theme="dark"] {{
  --paper:#0f1319; --panel:#161c24; --ink:#e8ecf1; --ink-soft:#b3bcc7; --ink-faint:#7c8794;
  --line:#252d38; --line-soft:#1c232c;
  --signal:#e8607a; --prov:#5fb87f; --conj:#d6a94a; --diag:#6fa3d8;
  --prov-bg:#16241b; --conj-bg:#271f10; --diag-bg:#132234; --signal-bg:#2a151a;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans);
  line-height:1.6; -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:900px; margin:0 auto; padding:clamp(1.4rem,4vw,3.5rem) clamp(1rem,4vw,2rem) 5rem; }}

.eyebrow {{ font-family:var(--mono); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--signal); margin:0 0 .9rem; }}
h1 {{ font-family:var(--serif); font-weight:600; font-size:clamp(1.9rem,5vw,2.9rem); line-height:1.08;
  letter-spacing:-.01em; margin:0 0 1rem; text-wrap:balance; }}
.lede {{ font-size:1.08rem; color:var(--ink-soft); max-width:64ch; margin:0 0 1.4rem; }}
.scope {{ font-size:.92rem; color:var(--ink-soft); background:var(--panel); border:1px solid var(--line);
  border-left:3px solid var(--conj); border-radius:8px; padding:.85rem 1.05rem; max-width:66ch;
  margin:0 0 2.6rem; }}
.scope b {{ color:var(--ink); }}

.summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:10px; overflow:hidden; margin:0 0 3rem; }}
.stat {{ background:var(--panel); padding:1rem 1.1rem; }}
.stat .k {{ font-family:var(--mono); font-size:1.5rem; font-weight:600; font-variant-numeric:tabular-nums;
  line-height:1; }}
.stat .l {{ font-size:.78rem; color:var(--ink-faint); margin-top:.4rem; }}
.stat.prov .k {{ color:var(--prov); }} .stat.signal .k {{ color:var(--signal); }}
.stat.diag .k {{ color:var(--diag); }}

section.card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px;
  box-shadow:var(--shadow); overflow:hidden; margin:0 0 1.8rem; }}
.card-head {{ padding:1.25rem 1.4rem .9rem; }}
.tagrow {{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:0 0 .7rem; }}
.chip {{ font-family:var(--mono); font-size:.7rem; font-weight:600; letter-spacing:.06em;
  text-transform:uppercase; padding:.28rem .6rem; border-radius:5px; }}
.chip.prov {{ color:var(--prov); background:var(--prov-bg); }}
.chip.conj {{ color:var(--conj); background:var(--conj-bg); }}
.chip.diag {{ color:var(--diag); background:var(--diag-bg); }}
.thm {{ font-family:var(--mono); font-size:.78rem; color:var(--ink-faint); }}
.card-head h2 {{ font-family:var(--serif); font-weight:600; font-size:1.42rem; letter-spacing:-.01em;
  margin:.1rem 0 .35rem; text-wrap:balance; }}
.card-head p {{ margin:0; color:var(--ink-soft); font-size:.96rem; max-width:62ch; }}
.figwrap {{ background:#fff; border-top:1px solid var(--line-soft); border-bottom:1px solid var(--line-soft); }}
.figwrap img, .figwrap video {{ display:block; width:100%; height:auto; }}
.readout {{ display:flex; flex-wrap:wrap; gap:0 2.2rem; padding:1rem 1.4rem; font-family:var(--mono);
  font-size:.85rem; font-variant-numeric:tabular-nums; border-bottom:1px solid var(--line-soft); }}
.readout div {{ padding:.15rem 0; }}
.readout .lab {{ color:var(--ink-faint); }}
.readout .val {{ color:var(--ink); font-weight:600; }}
.readout .val.pass {{ color:var(--prov); }} .readout .val.warn {{ color:var(--conj); }}
.meaning {{ padding:1rem 1.4rem 1.2rem; font-size:.95rem; color:var(--ink-soft); }}
.meaning b {{ color:var(--ink); }}
.file {{ font-family:var(--mono); font-size:.76rem; color:var(--ink-faint); padding:0 1.4rem 1.15rem; }}

h3.divider {{ font-family:var(--mono); font-size:.74rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--ink-faint); margin:2.8rem 0 1.3rem; padding-bottom:.5rem; border-bottom:1px solid var(--line);
  font-weight:600; }}
footer {{ margin-top:3rem; padding-top:1.6rem; border-top:1px solid var(--line); color:var(--ink-soft);
  font-size:.92rem; }}
footer h4 {{ font-family:var(--serif); font-size:1.1rem; color:var(--ink); margin:0 0 .6rem; }}
footer ul {{ margin:.3rem 0 1.3rem; padding-left:1.1rem; }} footer li {{ margin:.35rem 0; }}
footer .note {{ font-family:var(--mono); font-size:.78rem; color:var(--ink-faint); }}
code {{ font-family:var(--mono); font-size:.86em; background:var(--line-soft); padding:.1em .38em;
  border-radius:4px; }}
</style>

<div class="wrap">
  <p class="eyebrow">Tier-1 numerics · constraint-induced estimation sheaf</p>
  <h1>What the simulation actually shows</h1>
  <p class="lede">Executed results from the <code>tier1_sheaf</code> package built for the IEEE
  Transactions flagship. Every figure below was generated from committed data on a verified SE(2) core
  (25 regression tests green), and each is bound to the theorem it tests and its epistemic status.</p>
  <p class="scope"><b>Scope, honestly.</b> These are the theorem-validation experiments and one
  diagnostic — parametric sweeps and an estimation animation. This is <b>not</b> the Blind Harbor Transit
  (boats towing a barge through the channel): that closed-loop scenario is Tier-2 / RA-L, deferred by
  design, and not simulated. There is no harbor movie because there is no harbor sim yet.</p>

  <div class="summary">
    <div class="stat prov"><div class="k">1.999</div><div class="l">E3a floor slope (predicted 2 · PROV)</div></div>
    <div class="stat prov"><div class="k">3&rarr;0</div><div class="l">gauge kernel dim under pinning</div></div>
    <div class="stat signal"><div class="k">&eta;=0 ✓</div><div class="l">switch-off the pilot failed, E3a passes</div></div>
    <div class="stat diag"><div class="k">1.0000</div><div class="l">m=2 coefficient ratio (Q3: &alpha;=1)</div></div>
  </div>

  <h3 class="divider">Theorem validations · proved objects</h3>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip prov">PROV</span>
        <span class="thm">Thm 7.2 [thm:floor] · Cor 7.3 [cor:sym]</span></div>
      <h2>E3a — the latency&ndash;curvature floor, measured correctly</h2>
      <p>The deterministic holonomy amplitude <code>&#8214;log Hol(&gamma;_c)&#8214;</code> of the conjugated
      error transports around the round-trip walk &mdash; the object Thm 7.2 actually bounds. The pilot
      measured a different, stochastic quantity; this is the first correct validation in the program.</p>
    </div>
    <div class="figwrap"><img src="{F4A}" alt="E3a holonomy amplitude vs latency, log-log, slope 2 with switch-offs collapsed"></div>
    <div class="readout">
      <div><span class="lab">generic slope </span><span class="val pass">1.999</span></div>
      <div><span class="lab">symmetric </span><span class="val pass">&rarr; 0</span></div>
      <div><span class="lab">&eta;=0 </span><span class="val pass">&rarr; 0</span></div>
      <div><span class="lab">&xi;=0 </span><span class="val pass">&rarr; 0</span></div>
      <div><span class="lab">coeff ratio </span><span class="val">1.0000</span></div>
    </div>
    <p class="meaning">Generic shapes give the proved <b>slope 2</b>. Every switch-off in the theorem's
    battery &mdash; symmetry, <code>&eta;=0</code>, <code>&xi;=0</code> &mdash; drives the amplitude to
    <b>machine zero</b>. This is the decisive contrast with the pilot: its <code>D_ss</code> survived
    <code>&eta;=0</code> (so it was never the floor); this amplitude vanishes exactly, because it is.
    The coefficient ratio <b>1.0000</b> confirms the unit combinatorial coefficient at m=2 (open question Q3).</p>
    <p class="file">results/e3a_amplitude.png · e3a_amplitude.csv → paper figure F4a</p>
  </section>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip prov">PROV</span>
        <span class="thm">Thm 5.1 [thm:gauge] · Cor 5.2 [cor:pin]</span></div>
      <h2>E1 — gauge structure and pinning collapse</h2>
      <p>The sheaf Laplacian's kernel is exactly the <code>se(2)</code> gauge (dimension 3): the team is
      observable modulo one global rigid motion. A single absolute anchor removes it.</p>
    </div>
    <div class="figwrap"><img src="{F3}" alt="Left: kernel dimension collapses 3 to 0 with anchor strength. Right: lambda_min rises as the rate."></div>
    <div class="readout">
      <div><span class="lab">dim ker L_F </span><span class="val">3</span></div>
      <div><span class="lab">kernel = gauge sections </span><span class="val pass">1.3e-15</span></div>
      <div><span class="lab">one anchor </span><span class="val">dim ker &rarr; 0</span></div>
      <div><span class="lab">&lambda;_min </span><span class="val">becomes the rate</span></div>
    </div>
    <p class="meaning">The kernel <b>is</b> the gauge-section space to 1.3&times;10<sup>&minus;15</sup>
    (Thm 5.1), and the tiniest anchor collapses it (Cor 5.2). This also fixes a spec bug: the gauge is
    3-dimensional in <code>R^{{3N}}</code>, not a per-agent object, so the old <code>&sigma;_4/&sigma;_3</code>
    falsifier was never computable.</p>
    <p class="file">results/e1_gauge.png · e1_gauge.csv → paper figure F3</p>
  </section>

  <h3 class="divider">The gauge phenomenon · animated</h3>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip prov">PROV</span>
        <span class="thm">Thm 5.1 + Cor 5.2 · dynamic</span></div>
      <h2>Three estimates drifting along the gauge, then pinned</h2>
      <p>The abstract 3-agent estimation (not the harbor). The true load pose (black) moves; each agent
      dead-reckons and fuses. With no anchor the estimates stay consistent <i>with each other</i> but drift
      as a group <i>off the truth</i> &mdash; along the SE(2) gauge. At the beacon, agent 0 is pinned and
      all three snap home.</p>
    </div>
    <div class="figwrap"><video src="{MOV}" controls loop muted playsinline autoplay></video></div>
    <div class="readout">
      <div><span class="lab">gauge error pre-beacon </span><span class="val warn">~1.95</span></div>
      <div><span class="lab">gauge error post-beacon </span><span class="val pass">~0.14</span></div>
      <div><span class="lab">disagreement D </span><span class="val">~0.032 throughout</span></div>
    </div>
    <p class="meaning">The right panel is the whole point: the <b>disagreement</b> (agents vs each other)
    stays low the entire time, while the <b>gauge error</b> (agents vs truth) is large pre-beacon and
    collapses after. They are <b>different quantities</b> &mdash; the same distinction that separates the
    proved floor amplitude from the conjectural <code>D_ss</code>.</p>
    <p class="file">results/gauge_drift.mp4 · gauge_drift.gif</p>
  </section>

  <h3 class="divider">Diagnostic · why the pilot needed correcting</h3>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip diag">DIAGNOSTIC</span><span class="chip conj">CONJ object</span>
        <span class="thm">pilot D_ss vs paper rule</span></div>
      <h2>E3 diagnostic — the pilot's slope-2 is an artifact</h2>
      <p>Reproduces the original pilot to four decimals, then runs the switch-offs it never did.</p>
    </div>
    <div class="figwrap"><img src="{DIAG}" alt="Log-log D_ss vs tau: A2 arms ride slope-2; paper rule and symmetric-deterministic collapse to machine zero."></div>
    <div class="readout">
      <div><span class="lab">pilot &quot;generic&quot; </span><span class="val warn">slope 2.006</span></div>
      <div><span class="lab">at &eta;=0 </span><span class="val warn">still 2.000</span></div>
      <div><span class="lab">paper's own rule </span><span class="val">~1e-29 (no floor)</span></div>
      <div><span class="lab">symmetric &quot;1.59&quot; </span><span class="val">noise floor</span></div>
    </div>
    <p class="meaning">The pilot's headline slope-2 <b>survives at <code>&eta;=0</code></b> where the floor's
    mechanism vanishes &mdash; so it is a first-order per-edge artifact, squared, not the holonomy floor.
    The paper's <i>actual</i> fusion rule shows <b>no floor</b> (machine zero), and the symmetric
    slope-1.59 is a pure <b>noise floor</b>, not symmetry protection. Independently confirmed by the
    corpus audit (ES-11, ES-14).</p>
    <p class="file">results/e3_diagnostic.png · e3_diagnostic.csv</p>
  </section>

  <footer>
    <h4>What is not here (and why)</h4>
    <ul>
      <li><b>No Blind Harbor Transit movie.</b> The closed-loop towing scenario is Tier-2 / RA-L, deferred
      per open decision Q10. It needs the DIEKF-&Sigma; estimator, which is the next build.</li>
      <li><b>No E2 / E3b / E6 yet.</b> Contraction rate, the stochastic <code>D_ss</code> floor, and
      multi-topology &lambda;&#8322; scaling all require the estimator's filter loop.</li>
      <li><b>E4 / E5 (Maupertuis planner) deferred</b> to the RA-L companion.</li>
    </ul>
    <p class="note">tier1_sheaf · 25 tests green · figures reproducible via
    <code>python3 -m tier1_sheaf.experiments.&lt;name&gt;</code></p>
  </footer>
</div>
"""

with open(OUT, "w") as f:
    f.write(HTML)
print(f"wrote {OUT} ({len(HTML)/1024:.0f} KB)")
