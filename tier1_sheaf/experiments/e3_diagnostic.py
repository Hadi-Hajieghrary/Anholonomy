"""E3 diagnostic: is the pilot's slope-2 the holonomy floor, or an artifact?

Reproduces pilot_e3.py's frozen-shape fusion loop on the verified SE(2) core, with
switches that isolate the mechanism Thm 7.2 actually names:

  fuse_rule:
    'A2'    -> un-conjugated own-twist   Exp(tau * zeta_a)            (pilot 'generic')
    'paper' -> sim_design.tex:54 rule    Exp(tau * Ad_{m_b^-1 m_a} zeta_a)  (pilot 'compensated')
  eta_on   : if False, heading rate omega == 0  (Thm 7.2 leading term ∝ eta ⇒ must vanish)
  noise_on : if False, deterministic (bias=0, sigma=0)
  topology : 'triangle' (cycle) or 'path' (no 3-cycle; only length-2 round trips)
  kappa    : consensus gain (alpha = kappa * Dc); sweep to test gain/geometry entanglement

Decision rules (plan §0, §4.1):
  * If A2 slope survives at eta=0  -> the pilot floor is a first-order per-edge
    artifact, NOT Thm 7.2's holonomy (which vanishes at eta=0).
  * If 'paper' rule gives D_ss ~ machine-zero (noise off) -> the deployed DIEKF-Sigma
    rule exhibits no floor from this mechanism at frozen shapes (Q1).
  * If the symmetric arm collapses to machine-zero with noise off -> its slope-1.59
    with noise on is a noise floor, not Cor 7.3 protection.
"""
from __future__ import annotations

import numpy as np

from tier1_sheaf.core.se2 import Exp, Log, inv
from tier1_sheaf.core.shapes import m_of, Ad_m

TRIANGLE = [(0, 1), (1, 2), (2, 0)]
PATH = [(0, 1), (1, 2)]


def run(shapes, tau, seed, *, fuse_rule="A2", eta_on=True, noise_on=True,
        topology="triangle", kappa=2.0, Tend=90.0, dt=0.02, Dc=0.1, l=1.0):
    """One frozen-shape run. Returns (D_ss, aligned_residual)."""
    rng = np.random.default_rng(seed)
    N = len(shapes)
    edges = TRIANGLE if topology == "triangle" else PATH
    m = [m_of(sig, sigi, l) for (sig, sigi) in shapes]
    Adm = [Ad_m(sig, sigi, l) for (sig, sigi) in shapes]
    Admi = [np.linalg.inv(A) for A in Adm]

    G = np.eye(3)
    Gh = [np.eye(3) for _ in range(N)]
    if noise_on:
        bias = [np.array([rng.normal(0, 0.004), 0.0, rng.normal(0, 0.005)]) for _ in range(N)]
        sig_noise = np.array([0.01, 0.0, 0.005])
    else:
        bias = [np.zeros(3) for _ in range(N)]
        sig_noise = np.zeros(3)

    steps = int(Tend / dt)
    per = int(Dc / dt)
    lag = int(round(tau / Dc))
    buf = [[] for _ in range(N)]
    zeta_last = [np.zeros(3) for _ in range(N)]
    Dhist = []
    alpha = kappa * Dc
    directed = edges + [(b, a) for (a, b) in edges]

    for k in range(steps):
        t = k * dt
        omega = (0.12 * np.sin(0.15 * t) + 0.05) if eta_on else 0.0
        xi = np.array([0.4, 0.0, omega])
        G = G @ Exp(dt * xi)
        for j in range(N):
            zeta = Admi[j] @ xi
            zh = zeta + bias[j] + sig_noise * rng.standard_normal(3)
            zeta_last[j] = zh
            Gh[j] = Gh[j] @ Exp(dt * (Adm[j] @ zh))
        if k % per == 0:
            for j in range(N):
                buf[j].append(Gh[j] @ m[j])
            idx = len(buf[0]) - 1 - lag
            if idx >= 0:
                for (a, b) in directed:
                    Hst = buf[b][idx]
                    if fuse_rule == "paper":       # sim_design.tex:54 (conjugated to sender)
                        Tt = Hst @ Exp(tau * (Admi[b] @ (Adm[a] @ zeta_last[a])))
                    else:                           # 'A2' un-conjugated own-twist
                        Tt = Hst @ Exp(tau * zeta_last[a])
                    r = Log(inv(Gh[a]) @ (Tt @ inv(m[b])))
                    Gh[a] = Gh[a] @ Exp(alpha * r)
            if t > 0.7 * Tend:
                D = np.mean([np.sum(Log(inv(Gh[i]) @ Gh[j]) ** 2) for (i, j) in edges])
                Dhist.append(D)

    errs = np.array([Log(Gh[j] @ inv(G)) for j in range(N)])
    aligned = np.linalg.norm(errs - errs.mean(0))
    return float(np.mean(Dhist)), float(aligned)


def slope(shapes, taus, seeds, **kw):
    """Fit log D_ss vs log tau; return (slope, mean D_ss per tau)."""
    M = np.array([[run(shapes, t, s, **kw)[0] for s in seeds] for t in taus])
    mu = M.mean(1)
    # guard against machine-zero D_ss (log of ~1e-30) — report separately
    if (mu <= 0).any() or mu.min() < 1e-20:
        return float("nan"), mu
    return float(np.polyfit(np.log(taus), np.log(mu), 1)[0]), mu


GEN = [(0.4, 0.3), (0.9, -0.5), (-0.7, 0.6)]
SYM = [(0.5, 0.2)] * 3
TAUS = [0.1, 0.2, 0.4, 0.8, 1.6]
