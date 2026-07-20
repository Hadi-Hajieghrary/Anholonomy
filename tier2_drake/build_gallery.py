"""Build a self-contained Tier-2 Drake results gallery (media web-optimized + embedded)."""
import base64
import os
import subprocess
import tempfile

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
OUT = "/tmp/claude-1000/-workspaces-Anholonomy/3a36d322-c72b-4eff-acdc-cc60e2f82f83/scratchpad/drake_results_gallery.html"


def opt_mp4(name, width=820, crf=30):
    """Re-encode smaller for web embedding; returns a data URI."""
    src = os.path.join(RES, name)
    tmp = os.path.join(tempfile.gettempdir(), "opt_" + name)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", src,
         "-vf", f"scale={width}:-2", "-c:v", "libx264", "-crf", str(crf),
         "-preset", "slow", "-movflags", "+faststart", "-an", tmp], check=True)
    with open(tmp, "rb") as f:
        b = f.read()
    print(f"{name}: {os.path.getsize(src)//1024} KB -> {len(b)//1024} KB")
    return "data:video/mp4;base64," + base64.b64encode(b).decode()


def data_uri(name, mime):
    with open(os.path.join(RES, name), "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


N4 = opt_mp4("tow_N4.mp4")
N5 = opt_mp4("tow_N5.mp4")
ASYM = opt_mp4("tow_N4_asym.mp4")
CMP = data_uri("tow_comparison.png", "image/png")

HTML = f"""<style>
:root {{
  --paper:#f4f6f8; --panel:#ffffff; --ink:#121821; --ink-soft:#3a4653; --ink-faint:#69737f;
  --line:#e0e5ea; --line-soft:#eef1f4;
  --accent:#1c6091; --sea:#2a6f97; --hull:#b23b2a; --prov:#1b7837; --warn:#a8741a;
  --accent-bg:#e5eef5; --hull-bg:#f7e7e4; --prov-bg:#e9f3ec; --warn-bg:#f6efe0;
  --shadow:0 1px 2px rgba(18,24,33,.05), 0 8px 30px rgba(18,24,33,.07);
  --serif:Charter,'Bitstream Charter','Iowan Old Style',Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --paper:#0c1118; --panel:#141b24; --ink:#e7ecf1; --ink-soft:#b1bbe6; --ink-faint:#7a8592;
    --line:#232c37; --line-soft:#1a212a; --accent:#5aa0d0; --sea:#5b98c4; --hull:#e0705e;
    --prov:#5fb87f; --warn:#d6a94a; --accent-bg:#132433; --hull-bg:#2a1712; --prov-bg:#16241b;
    --warn-bg:#271f10; --shadow:0 1px 2px rgba(0,0,0,.35),0 10px 32px rgba(0,0,0,.4); }}
}}
:root[data-theme="light"] {{ --paper:#f4f6f8; --panel:#fff; --ink:#121821; --ink-soft:#3a4653;
  --ink-faint:#69737f; --line:#e0e5ea; --line-soft:#eef1f4; --accent:#1c6091; --sea:#2a6f97;
  --hull:#b23b2a; --prov:#1b7837; --warn:#a8741a; --accent-bg:#e5eef5; --hull-bg:#f7e7e4;
  --prov-bg:#e9f3ec; --warn-bg:#f6efe0; }}
:root[data-theme="dark"] {{ --paper:#0c1118; --panel:#141b24; --ink:#e7ecf1; --ink-soft:#b1bbc6;
  --ink-faint:#7a8592; --line:#232c37; --line-soft:#1a212a; --accent:#5aa0d0; --sea:#5b98c4;
  --hull:#e0705e; --prov:#5fb87f; --warn:#d6a94a; --accent-bg:#132433; --hull-bg:#2a1712;
  --prov-bg:#16241b; --warn-bg:#271f10; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans); line-height:1.6;
  -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:920px; margin:0 auto; padding:clamp(1.4rem,4vw,3.5rem) clamp(1rem,4vw,2rem) 5rem; }}
.eyebrow {{ font-family:var(--mono); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--sea); margin:0 0 .9rem; }}
h1 {{ font-family:var(--serif); font-weight:600; font-size:clamp(1.9rem,5vw,2.9rem); line-height:1.08;
  letter-spacing:-.01em; margin:0 0 1rem; text-wrap:balance; }}
.lede {{ font-size:1.08rem; color:var(--ink-soft); max-width:64ch; margin:0 0 1.4rem; }}
.scope {{ font-size:.92rem; color:var(--ink-soft); background:var(--panel); border:1px solid var(--line);
  border-left:3px solid var(--warn); border-radius:8px; padding:.85rem 1.05rem; max-width:66ch; margin:0 0 2.6rem; }}
.scope b {{ color:var(--ink); }}
.summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:10px; overflow:hidden; margin:0 0 3rem; }}
.stat {{ background:var(--panel); padding:1rem 1.1rem; }}
.stat .k {{ font-family:var(--mono); font-size:1.5rem; font-weight:600; font-variant-numeric:tabular-nums; line-height:1; }}
.stat .l {{ font-size:.78rem; color:var(--ink-faint); margin-top:.4rem; }}
.stat.sea .k {{ color:var(--sea); }} .stat.hull .k {{ color:var(--hull); }} .stat.prov .k {{ color:var(--prov); }}
section.card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; box-shadow:var(--shadow);
  overflow:hidden; margin:0 0 1.8rem; }}
.card-head {{ padding:1.25rem 1.4rem .9rem; }}
.tagrow {{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:0 0 .7rem; }}
.chip {{ font-family:var(--mono); font-size:.7rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  padding:.28rem .6rem; border-radius:5px; }}
.chip.sea {{ color:var(--sea); background:var(--accent-bg); }}
.chip.prov {{ color:var(--prov); background:var(--prov-bg); }}
.chip.warn {{ color:var(--warn); background:var(--warn-bg); }}
.thm {{ font-family:var(--mono); font-size:.78rem; color:var(--ink-faint); }}
.card-head h2 {{ font-family:var(--serif); font-weight:600; font-size:1.42rem; letter-spacing:-.01em;
  margin:.1rem 0 .35rem; text-wrap:balance; }}
.card-head p {{ margin:0; color:var(--ink-soft); font-size:.96rem; max-width:64ch; }}
.media {{ background:#000; border-top:1px solid var(--line-soft); border-bottom:1px solid var(--line-soft); }}
.media video, .media img {{ display:block; width:100%; height:auto; }}
.readout {{ display:flex; flex-wrap:wrap; gap:0 2.2rem; padding:1rem 1.4rem; font-family:var(--mono);
  font-size:.85rem; font-variant-numeric:tabular-nums; border-bottom:1px solid var(--line-soft); }}
.readout .lab {{ color:var(--ink-faint); }} .readout .val {{ color:var(--ink); font-weight:600; }}
.readout .val.pass {{ color:var(--prov); }} .readout .val.warn {{ color:var(--warn); }}
.meaning {{ padding:1rem 1.4rem 1.2rem; font-size:.95rem; color:var(--ink-soft); }}
.meaning b {{ color:var(--ink); }}
.file {{ font-family:var(--mono); font-size:.76rem; color:var(--ink-faint); padding:0 1.4rem 1.15rem; }}
h3.divider {{ font-family:var(--mono); font-size:.74rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--ink-faint); margin:2.8rem 0 1.3rem; padding-bottom:.5rem; border-bottom:1px solid var(--line); font-weight:600; }}
footer {{ margin-top:3rem; padding-top:1.6rem; border-top:1px solid var(--line); color:var(--ink-soft); font-size:.92rem; }}
footer h4 {{ font-family:var(--serif); font-size:1.1rem; color:var(--ink); margin:0 0 .6rem; }}
footer ul {{ margin:.3rem 0 1.3rem; padding-left:1.1rem; }} footer li {{ margin:.35rem 0; }}
footer .note {{ font-family:var(--mono); font-size:.78rem; color:var(--ink-faint); }}
code {{ font-family:var(--mono); font-size:.86em; background:var(--line-soft); padding:.1em .38em; border-radius:4px; }}
</style>

<div class="wrap">
  <p class="eyebrow">Tier-2 · Drake 1.51 · full multibody (SAP)</p>
  <h1>Cooperative towing of a pentagonal caisson — realistic multibody simulation</h1>
  <p class="lede">A 2,500&nbsp;kg pentagonal caisson towed by N autonomous surface vessels through taut cables, built
  on Drake's discrete <code>MultibodyPlant</code>. Each vessel is a rigid
  <code>PlanarJoint</code> body; each cable is a SAP <b>distance constraint</b>; cable tensions are
  recovered analytically from the constrained dynamics. Agent count is one config field — shown here at
  <b>N = 4</b> and <b>N = 5</b>. The load is a regular pentagon (circumradius 4 m, bow vertex leading); attachment points sit on its front edges. Drake carries the physics with a cylinder-inertia proxy; the pentagon outline is exact in the renderer.</p>
  <p class="scope"><b>Where this sits.</b> This is the <b>Tier-2 / RA-L</b> platform &mdash; the realistic
  full-physics counterpart to the reduced-coordinate Tier-1 flagship sim, and its cross-validation oracle.
  The vessels run a thrust-and-drag towing controller; the <b>DIEKF-&Sigma; estimator is not yet in the
  loop</b>, so this demonstrates the constrained plant and the tension instrument, not yet closed-loop
  GNSS-denied estimation. That is the next layer.</p>

  <div class="summary">
    <div class="stat sea"><div class="k">4 &amp; 5</div><div class="l">vessels — one config field</div></div>
    <div class="stat prov"><div class="k">1e&minus;8 m</div><div class="l">cable taut deviation (machine-tight)</div></div>
    <div class="stat hull"><div class="k">2.6 / 2.4</div><div class="l">steady tension kN/cable (N=4 / N=5)</div></div>
    <div class="stat sea"><div class="k">SAP</div><div class="l">discrete contact solver, dt=1 ms</div></div>
  </div>

  <h3 class="divider">Symmetric formations · N = 4 and N = 5</h3>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip sea">N = 4</span><span class="chip prov">taut · stable</span>
        <span class="thm">discrete MultibodyPlant · 4 distance constraints</span></div>
      <h2>Four vessels towing the caisson</h2>
      <p>A symmetric bow fan. Left: the top-down transit (cable width and colour track tension). Right: the
      analytically recovered cable tensions ramping to steady tow.</p>
    </div>
    <div class="media"><video src="{N4}" controls loop muted playsinline autoplay></video></div>
    <div class="readout">
      <div><span class="lab">caisson travel </span><span class="val">141 m in 40 s</span></div>
      <div><span class="lab">steady tension </span><span class="val">2.56 kN &times; 4</span></div>
      <div><span class="lab">cable taut </span><span class="val pass">&plusmn;1e-8 m</span></div>
    </div>
    <p class="meaning">The symmetric fan holds the centreline with equal tensions &mdash; the full-multibody
    analogue of the reduced-coordinate symmetric formation. The SAP distance constraint keeps every cable at exactly 12&nbsp;m to machine precision, which is the realism the Tier-1 sim <i>assumes</i>.</p>
    <p class="file">tier2_drake/results/tow_N4.mp4</p>
  </section>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip sea">N = 5</span><span class="chip prov">taut · stable</span>
        <span class="thm">discrete MultibodyPlant · 5 distance constraints</span></div>
      <h2>Five vessels — same code, one changed field</h2>
      <p>The scalability contract: <code>ScenarioConfig(N=5)</code> and nothing else.</p>
    </div>
    <div class="media"><video src="{N5}" controls loop muted playsinline autoplay></video></div>
    <div class="readout">
      <div><span class="lab">caisson travel </span><span class="val">162 m in 40 s</span></div>
      <div><span class="lab">steady tension </span><span class="val">2.35 kN &times; 5</span></div>
      <div><span class="lab">agent count </span><span class="val">config-only</span></div>
    </div>
    <p class="meaning">Five vessels share the tow: lower per-cable tension (2.35 vs 2.56&nbsp;kN) for the same caisson. No code changed between N=4 and N=5 &mdash; builders loop over <code>cfg.N</code>.</p>
    <p class="file">tier2_drake/results/tow_N5.mp4</p>
  </section>

  <h3 class="divider">Broken symmetry · a weaker thruster</h3>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip warn">asymmetric</span>
        <span class="thm">N = 4 · thrust scale (1.3, 1.1, 0.9, 0.7)</span></div>
      <h2>Unequal thrust imbalances the cables and yaws the caisson</h2>
      <p>The same scene with a thrust gradient across the four vessels &mdash; a realistic weaker-starboard
      fault. Watch the tension traces fan apart.</p>
    </div>
    <div class="media"><video src="{ASYM}" controls loop muted playsinline autoplay></video></div>
    <div class="readout">
      <div><span class="lab">tension spread </span><span class="val warn">94%</span></div>
      <div><span class="lab">tensions </span><span class="val">3.8 / 3.0 / 2.2 / 1.4 kN</span></div>
      <div><span class="lab">caisson yaw </span><span class="val warn">+21&deg;</span></div>
    </div>
    <p class="meaning">Symmetric thrust gives equal tensions and zero yaw; a thrust gradient produces an
    <b>94% tension spread</b> and a persistent +21&deg; yaw — the lighter caisson has far less yaw inertia than the old 6-tonne barge, so the same fault costs more. This is the multibody, closed-physics face of the
    symmetry theme that runs through the whole framework &mdash; asymmetry has measurable, uneven cost.</p>
    <p class="file">tier2_drake/results/tow_N4_asym.mp4</p>
  </section>

  <section class="card">
    <div class="card-head">
      <div class="tagrow"><span class="chip sea">summary</span><span class="thm">N=4 · N=5 · asymmetric</span></div>
      <h2>The three runs, side by side</h2>
    </div>
    <div class="media"><img src="{CMP}" alt="Left: caisson heading vs time — symmetric flat, unequal thrust yaws. Right: steady tensions — symmetric equal, unequal spread."></div>
    <p class="meaning">Left: caisson heading holds at 0&deg; under symmetric thrust, diverges under the
    gradient. Right: steady cable tensions are equal for both symmetric formations and imbalanced under
    unequal thrust.</p>
    <p class="file">tier2_drake/results/tow_comparison.png</p>
  </section>

  <footer>
    <h4>How it is built (and what is next)</h4>
    <ul>
      <li><b>Real constrained dynamics.</b> Discrete <code>MultibodyPlant</code> + SAP; cables are
      <code>AddDistanceConstraint</code>; tensions from
      <code>&lambda; = &minus;(J M&#8315;&sup1;J&#7488;)&#8315;&sup1;[J&#775;v + J M&#8315;&sup1;(&tau;&#8331; &minus; Cv)]</code>
      using only documented plant queries &mdash; no private solver fields.</li>
      <li><b>Config-driven &amp; scalable.</b> N, formation, thrust, drag, cable length all live in
      <code>ScenarioConfig</code>; N&nbsp;&isin;&nbsp;{{3,4,5,&hellip;}} with zero code changes.</li>
      <li><b>Next layer:</b> put the DIEKF-&Sigma; estimator in the loop (GNSS-denied), then reproduce the
      latency&ndash;curvature floor on the full model and cross-validate against the Tier-1 amplitude.</li>
    </ul>
    <p class="note">tier2_drake · pydrake 1.51.1 · discrete SAP · dt = 1&nbsp;ms · reproducible via
    <code>python3 -m tier2_drake.render</code></p>
  </footer>
</div>
"""

with open(OUT, "w") as f:
    f.write(HTML)
print(f"\nwrote {OUT} ({len(HTML)/1024:.0f} KB)")
