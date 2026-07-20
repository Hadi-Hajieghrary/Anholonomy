"""estimator_core — the ONE DIEKF-Σ implementation, shared by both tiers.

Pure NumPy. ZERO Drake imports (tested: tests/test_core.py::test_no_drake_imports).
Plan: docs/comprehensive_execution_plan.md §3.1. WS-0 scope: minimal P/U/F
skeleton, paper fusion rule only; full package (CI ω, weights, rules registry,
gauge alignment) lands weeks 3–4.
"""
from .state import (FilterState, vech, unvech, NERR, NVECH, CORE_LEN,
                    SL_G, SL_S, SL_P, IX_THETA, IX_BETA, IX_BG, IX_MV, SL_MXI,
                    core_to_vec, vec_to_core)
from .propagate import propagate, body_twist
from .update import update_direction, update_beacon
from .fuse import fuse_paper, FusionRecord, bias_schmidt_update
from .packets import pack, unpack, PACKET_LEN
from .rules import FUSE_RULES, fuse_with_rule
from .weights import iota, w_series
from .ci import ci_fuse_G
from .radial import radial_pair, solve_load_twist, solve_load_twist_wls

__version__ = "0.3.0-bias"
