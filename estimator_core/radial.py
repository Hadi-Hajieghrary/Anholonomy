"""Radial-constraint load-twist observer — the principled Tier-2 propagate.

EXACT rigid-cable kinematics, PLANT-INDEPENDENT (FD-verified: l_dot = rho − b·ξ):
per vessel, the taut cable transfers exactly one scalar,
    b·ξ_L = ρ,   b = [cos σ, sin σ, a_x sin σ − a_y cos σ],
                 ρ = ζ_v · (cos σ_i, sin σ_i)
(σ, σ_i the load/body-frame cable angles; a the attach offset; ζ_v own odometry).
One vessel is rank-1; the remaining directions arrive THROUGH FUSION — neighbors'
pairs ride in packets (with their latency: the constraint-channel thesis at the
velocity level). ≥3 well-conditioned rows determine ξ̂_L; otherwise the caller
falls back to the slaved model.
"""
from __future__ import annotations

import numpy as np

from .state import FilterState

__all__ = ["radial_pair", "solve_load_twist", "solve_load_twist_wls", "COND_MIN_SV"]

COND_MIN_SV = 0.3      # smallest singular value gate for a trustworthy solve


def radial_pair(state: FilterState, zeta_corr: np.ndarray):
    """This agent's (b, rho) from its own observables (bias-corrected twist)."""
    sig, sig_i = state.s
    ax, ay = state.attach
    b = np.array([np.cos(sig), np.sin(sig),
                  ax * np.sin(sig) - ay * np.cos(sig)])
    rho = float(zeta_corr[0] * np.cos(sig_i) + zeta_corr[1] * np.sin(sig_i))
    return b, rho


def solve_load_twist(B: np.ndarray, rhos: np.ndarray, xi_prior=None, lam: float = 1.0):
    """Tikhonov-blended ξ̂_L: argmin |Bξ − ρ|² + λ|ξ − ξ_prior|².

    The settled tow is geometrically degenerate for the radial pairs (cables
    near-parallel ⇒ v_y weakly determined); a raw lstsq amplifies odometry noise
    along exactly those directions [measured: perp 3.5 → 19]. The blend applies
    the exact radial information only along directions the geometry supports,
    falling back to the (slaved-model) prior elsewhere. With no prior: gated lstsq.
    """
    B = np.atleast_2d(np.asarray(B, dtype=float))
    r = np.asarray(rhos, dtype=float)
    if xi_prior is None:
        if B.shape[0] < 3:
            return None
        if np.linalg.svd(B, compute_uv=False)[-1] < COND_MIN_SV:
            return None
        xi, *_ = np.linalg.lstsq(B, r, rcond=None)
        return xi
    A = B.T @ B + lam * np.eye(3)
    return np.linalg.solve(A, B.T @ r + lam * np.asarray(xi_prior, dtype=float))


def solve_load_twist_wls(B, rhos, xi_prior, Sigma_prior, sigma_rho2):
    """Bayesian WLS: the radial P-block's heart.

    ρ_j = b_j·ξ + ν_j, ν_j ~ N(0, σ²_ρ,j); prior ξ ~ N(ξ_model, Σ_prior).
    Posterior:  Σ = (Σ_p⁻¹ + Bᵀ R⁻¹ B)⁻¹,  ξ̂ = Σ (Σ_p⁻¹ ξ_model + Bᵀ R⁻¹ ρ).
    Σ is LARGE exactly in geometry-degenerate directions (lateral in steady tow)
    and small along-track — the honest per-direction twist uncertainty the
    G-propagation needs (the anchored-ANEES failure was P underclaiming
    laterally). Returns (ξ̂, Σ). Pure function.
    """
    B = np.atleast_2d(np.asarray(B, dtype=float))
    r = np.asarray(rhos, dtype=float)
    w = 1.0 / np.asarray(sigma_rho2, dtype=float)
    Sp_inv = np.linalg.inv(np.asarray(Sigma_prior, dtype=float))
    A = Sp_inv + (B.T * w) @ B
    Sigma = np.linalg.inv(A)
    xi = Sigma @ (Sp_inv @ np.asarray(xi_prior, dtype=float) + (B.T * w) @ r)
    return xi, 0.5 * (Sigma + Sigma.T)
