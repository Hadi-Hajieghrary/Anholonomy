# Publication units (the three-paper split)

| Unit | Venue | Source | Status |
|---|---|---|---|
| Floor letter | L-CSS | `lcss_letter/main.tex` | skeleton; E3a package submission-ready (Q12 satisfied); theory source is the author's `refs/estimation_sheaf.tex` (unversioned) |
| Flagship | IEEE T-CNS | author's `refs/estimation_sheaf.tex` + `tcns_section8/section8.tex` (the §VIII numerics section, Tier-1-only per the publication split) | §VIII fragment scaffolded; Q11 corrections pending author |
| Blind Harbor companion | RA-L | `ral_blind_harbor/main.tex` | full skeleton with abstract, results structure, hedged captions; content source = `docs/ral_package.md` |

Rules of the split (binding):
- The flagship §VIII carries **Tier-1 evidence only** (R9 defense); the
  straight-line-in-Drake switch-off row appears only in the RA-L rendition.
- Every figure caption naming a theorem carries its registered hedge verbatim.
- Every number traces to `campaign_replay.py` (`--list` for the manifest,
  `--verify-all` for per-run replay checks).
- Every M-FAB/ANEES mention discloses the author-ruled gate widening and the
  failed complement sanity bound.
