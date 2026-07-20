"""Fixed-width packet: [stamp, sender, vec(G) 9, vech(P) 28, ŝ 2, radial b 3,
radial ρ 1, valid] = 47 + 7 = 54 floats. The radial pair is the constraint-channel
payload (radial.py) — the neighbor's one-scalar velocity constraint, aged by τ."""
from __future__ import annotations

import numpy as np

from .state import FilterState, vech, unvech, NVECH

__all__ = ["PACKET_LEN", "pack", "unpack"]

_OFF_S = 11 + NVECH            # 39
_OFF_B = _OFF_S + 2            # 41
_OFF_RHO = _OFF_B + 3
_OFF_MXI = _OFF_RHO + 1
_OFF_VALID = _OFF_MXI + 3

PACKET_LEN = 2 + 9 + NVECH + 2 + 3 + 1 + 3 + 1


def pack(stamp: float, sender: int, state: FilterState, valid: bool = True,
         radial=None) -> np.ndarray:
    v = np.zeros(PACKET_LEN)
    v[0] = stamp
    v[1] = float(sender)
    v[2:11] = state.G.ravel()
    v[11:11 + NVECH] = vech(state.P)
    v[_OFF_S:_OFF_S + 2] = state.s
    if radial is not None:
        b, rho = radial
        v[_OFF_B:_OFF_B + 3] = b
        v[_OFF_RHO] = rho
    v[_OFF_MXI:_OFF_MXI + 3] = state.m_xi
    v[_OFF_VALID] = 1.0 if valid else 0.0
    return v


def unpack(v: np.ndarray):
    """-> (stamp, sender, G, P, s, b (3,), rho, m_xi (3,), valid)."""
    v = np.asarray(v, dtype=float)
    assert v.shape == (PACKET_LEN,), f"packet must be {PACKET_LEN} floats"
    return (float(v[0]), int(v[1]), v[2:11].reshape(3, 3), unvech(v[11:11 + NVECH]),
            v[_OFF_S:_OFF_S + 2].copy(), v[_OFF_B:_OFF_B + 3].copy(),
            float(v[_OFF_RHO]), v[_OFF_MXI:_OFF_MXI + 3].copy(),
            bool(v[_OFF_VALID] > 0.5))
