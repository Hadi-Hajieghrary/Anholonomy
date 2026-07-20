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


class DropJitterGate(LeafSystem):
    """Erasure + jitter AFTER the delay (plan §5.2; D10(b) robustness arm).

    Per NEW packet stamp observed on the input: draw drop ~ Bernoulli(p) and
    jitter ~ U{0..J} extra T_c ticks. A dropped packet is never forwarded (the
    gate keeps emitting the previous accepted packet — erasure at reception).
    A jittered packet is forwarded after its extra hold. Seeded per edge;
    protocol class P (p = 0, J = 0) passes packets through bit-exactly.
    """

    def __init__(self, drop_p: float, jitter_max_ticks: int, seed: int):
        super().__init__()
        self._p = float(drop_p)
        self._J = int(jitter_max_ticks)
        self._rng = np.random.default_rng(np.random.SeedSequence([seed, 77]))
        # state: [held output PACKET_LEN | pending PACKET_LEN | pending_ticks | last_stamp]
        n = 2 * PACKET_LEN + 2
        x0 = np.zeros(n); x0[-2] = -1.0; x0[-1] = -1.0
        self._state_index = self.DeclareDiscreteState(x0)
        self._in = self.DeclareVectorInputPort("pkt_in", BasicVector(PACKET_LEN))
        self.DeclareVectorOutputPort("pkt_out", BasicVector(PACKET_LEN),
                                     lambda c, o: o.set_value(
                                         c.get_discrete_state(self._state_index)
                                         .get_value()[:PACKET_LEN]),
                                     prerequisites_of_calc={self.all_state_ticket()})
        self.DeclarePeriodicDiscreteUpdateEvent(T_C, 0.0, self._tick)

    def _tick(self, context, discrete_state):
        x = context.get_discrete_state(self._state_index).get_value().copy()
        pkt = np.asarray(self._in.Eval(context))
        held, pend = x[:PACKET_LEN], x[PACKET_LEN:2 * PACKET_LEN]
        ticks, last = x[-2], x[-1]
        if ticks > 0:                                    # pending jittered packet
            ticks -= 1
            if ticks == 0:
                held = pend.copy()
        if pkt[0] > last and pkt[-1] > 0.5:              # new valid stamp arrived
            last = pkt[0]
            if self._rng.random() >= self._p:            # not dropped
                j = int(self._rng.integers(0, self._J + 1)) if self._J > 0 else 0
                if j == 0:
                    held = pkt.copy(); ticks = 0
                else:
                    pend = pkt.copy(); ticks = j
        x[:PACKET_LEN] = held; x[PACKET_LEN:2 * PACKET_LEN] = pend
        x[-2] = ticks; x[-1] = last
        discrete_state.get_mutable_vector(self._state_index).set_value(x)
