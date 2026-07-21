# Anholonomy
Decentralized estimation in constrained multi-agent systems - constraint-induced sheaves, SE(2) gauge freedom, and the latency-curvature floor.

## Papers and reproduction

Three publication units live under `papers/` (see `papers/README.md` for the
binding split): the L-CSS floor letter (`lcss_letter/`), the T-CNS flagship's
§VIII numerics (`tcns_section8/`, Tier-1 evidence only), and the RA-L
"Blind Harbor" multibody companion (`ral_blind_harbor/`). Each bundles its
figures and supplementary movies with a captioned `multimedia/README.md`.

Reproduction:
- Environment: `pip install -r requirements.lock.txt` (pinned; no GPU).
- Every campaign cell: `python3 campaign_replay.py --list` shows the manifest
  (cell → driver → committed record → probe class); `--verify CELL`
  re-executes a per-run probe that must match the committed record
  (Tier-1 exact to 1e-9, Drake to 1e-6); `--run CELL` regenerates a campaign.
- Paper figures: `python3 tier1_sheaf/campaign/paper_artifacts.py` (asserts a
  seed-exact replay of the extension datasets before plotting) and
  `python3 analysis/figures/ral_artifacts.py` (reads only committed records).
- Movies: seeded generators beside the drivers (`*_movie.py`,
  `tier1_sheaf/experiments/anim_gauge.py`, `tier2_drake/blind_harbor/hero*.py`).

The frozen adjudication ledger (claims, falsifiers, verdicts, evidence files)
is `docs/ral_package.md`.
