"""Fuse-rule registry — plan §3.1. Arm id travels in config, never a free label.

    paper : conjugated own-load-twist fast-forward (executed-composite; fuse.py)
    A1    : no lag compensation (transport = 0)
    A2    : un-conjugated own BODY twist (the pilot's mislabeled 'generic' arm)
    off   : no fusion at all (B0 dead-reckoning)

The A2 SIGNATURE PIN (tests) is the label-inversion vaccine: A2 must show the
first-order per-edge defect at frozen shapes where `paper` shows machine zero.
"""
from __future__ import annotations

import numpy as np

from tier1_sheaf.core.se2 import Exp, Log, inv
from .state import FilterState
from .fuse import fuse_paper, FusionRecord

__all__ = ["FUSE_RULES", "fuse_with_rule"]


def _fuse_transport(state, G_nb, realized_age, transport, alpha, w, sender):
    G_tilde = G_nb @ Exp(transport)
    r = Log(inv(state.G) @ G_tilde)
    G_new = state.G @ Exp(alpha * w * r)
    out = state.replace(G=G_new)
    rec = FusionRecord(t=state.t, sender=sender, realized_age=float(realized_age),
                       transport_log=np.asarray(transport, dtype=float).copy(),
                       residual=r.copy())
    return out, rec


def _fuse_a1(state, G_nb, s_nb, age, zeta_self, alpha, w, sender):
    return _fuse_transport(state, G_nb, age, np.zeros(3), alpha, w, sender)


def _fuse_a2(state, G_nb, s_nb, age, zeta_self, alpha, w, sender):
    transport = age * np.asarray(zeta_self, dtype=float)      # un-conjugated body twist
    return _fuse_transport(state, G_nb, age, transport, alpha, w, sender)


FUSE_RULES = {
    "paper": fuse_paper,
    "A1": _fuse_a1,
    "A2": _fuse_a2,
    "off": None,                       # B0 dead-reckoning: consume nothing
}


def fuse_with_rule(rule: str, state, G_nb, s_nb, age, zeta_self, alpha, w, sender):
    fn = FUSE_RULES[rule]
    if fn is None:
        return state, None
    return fn(state, G_nb, s_nb, age, zeta_self, alpha, w, sender)
