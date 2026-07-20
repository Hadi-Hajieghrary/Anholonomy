"""Comms fabric — plan §3.1/§5.2. WS-0 scope: VectorRingDelay (own ring buffer,
do NOT bet on DiscreteTimeDelay API) + DropGate. Jitter/loss land at M-FAB;
WS-0 runs p = 0, jitter = 0 (protocol class 𝒫, zero-collision assert free).
"""
from __future__ import annotations

import numpy as np
from pydrake.systems.framework import DiagramBuilder, LeafSystem, BasicVector

from estimator_core.packets import PACKET_LEN

__all__ = ["VectorRingDelay", "T_C"]

T_C = 0.01   # delay quantum (s) — the 100 Hz comms grid (plan §3.3)


class VectorRingDelay(LeafSystem):
    """k-step delay of PACKET_LEN vectors on the T_c grid.

    Discrete state: ring of (k+1) slots x PACKET_LEN + write cursor.
    At each T_c tick: write input packet at cursor, emit the slot k steps back.
    Slot-collision policy (plan §3.1): keep-newest-stamp — trivially satisfied
    here since jitter = 0 in WS-0 (one write per tick; asserted upstream).
    """

    def __init__(self, k_delay: int):
        super().__init__()
        assert k_delay >= 1, "lag >= 1 (plan §3.3: tau_e exact multiple of T_c, lag >= 1)"
        self._k = int(k_delay)
        self._slots = self._k + 1
        n = self._slots * PACKET_LEN + 1                      # + cursor
        self._state_index = self.DeclareDiscreteState(n)
        self._in = self.DeclareVectorInputPort("pkt_in", BasicVector(PACKET_LEN))
        self.DeclareVectorOutputPort("pkt_out", BasicVector(PACKET_LEN), self._calc_out,
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclarePeriodicDiscreteUpdateEvent(T_C, 0.0, self._tick)

    def _tick(self, context, discrete_state):
        x = context.get_discrete_state(self._state_index).get_value().copy()
        cur = int(round(x[-1]))
        pkt = self._in.Eval(context)
        base = cur * PACKET_LEN
        x[base:base + PACKET_LEN] = pkt
        x[-1] = (cur + 1) % self._slots
        discrete_state.get_mutable_vector(self._state_index).set_value(x)

    def _calc_out(self, context, output):
        x = context.get_discrete_state(self._state_index).get_value()
        cur = int(round(x[-1]))
        read = (cur - self._k) % self._slots                  # k steps back from next write
        base = read * PACKET_LEN
        output.set_value(x[base:base + PACKET_LEN])
