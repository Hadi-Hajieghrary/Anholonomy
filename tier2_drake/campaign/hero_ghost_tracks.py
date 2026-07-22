"""Re-run the hero dogleg transit for the paper rule and the B0 (dead-reckon)
baseline, saving the per-agent GHOST load-pose tracks + truth so the RA-L
gauge-orbit and baseline-divergence scenario figures are grounded in recorded
data (the base hero_dogleg_series.npz stores only scalar D/kern/comp, not the
ghost poses). One seed, HERO_CFG. Saves -> results/s1/hero_ghost_tracks.npz.
"""
import sys, os
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np
import estimator_core as ec
from tier2_drake.blind_harbor.s1 import CFG, run_seed

OUT = "/workspaces/Anholonomy/tier2_drake/results/s1/hero_ghost_tracks.npz"
SEED = 3
HERO = dict(CFG, Tend=450.0, tau=0.31, dogleg=(200.0, 60.0, np.pi / 3),
            t_on=410.0, eval_from=430.0)


def ghost_tracks(cfg):
    out = run_seed(cfg, SEED)
    ts, tq, ests = out["ts"], out["truth"], out["ests"]
    N = cfg["N"]
    K = len(ts)
    # ghost load-pose (x,y,yaw) per agent per time
    ghosts = np.zeros((N, K, 3))
    for i in range(N):
        for k in range(K):
            G = ests[i][k][ec.SL_G].reshape(3, 3)
            ghosts[i, k] = [G[0, 2], G[1, 2], np.arctan2(G[1, 0], G[0, 0])]
    return ts, tq, ghosts


ts, tq, g_paper = ghost_tracks(HERO)
_, _, g_b0 = ghost_tracks(dict(HERO, fuse_rule="off"))
np.savez(OUT, ts=ts, truth=tq, ghost_paper=g_paper, ghost_b0=g_b0,
         t_on=HERO["t_on"], seed=SEED)
print("wrote", OUT, "| ts", ts.shape, "ghost_paper", g_paper.shape)
