"""Truth-isolation lint — plan §3.3: a TEST, not a convention.

Walks the built Diagram's connection map and FAILS if any input of an
estimator/controller-classified system connects to a MultibodyPlant output.
Exemptions are mechanical: (i) plant-side BY CLASS (HydroDrag, Thruster,
sensors — the sanctioned readers); (ii) a config-declared per-arm exemption set,
asserted EMPTY in every GNSS-denied/theory cell.
"""
from __future__ import annotations

from pydrake.multibody.plant import MultibodyPlant
from pydrake.geometry import SceneGraph
from pydrake.systems.primitives import VectorLogSink

from tier2_drake.blind_harbor.controller import PLANT_SIDE_CLASSES
from tier2_drake.blind_harbor.sensors import SensorSuite

__all__ = ["truth_isolation_lint"]

# sanctioned BY CLASS (plan §3.3): plant-side physics, sensors (the sanctioned
# readers), truth-monitors/loggers (observation), and plant infrastructure
_SANCTIONED = PLANT_SIDE_CLASSES + (SensorSuite, VectorLogSink, SceneGraph)


def truth_isolation_lint(diagram, plant, *, exemptions: set[str] = frozenset(),
                         require_empty_exemptions: bool = True):
    """Raise AssertionError on any estimator/controller input fed by the plant.

    exemptions: system names granted truth access by config (b1 oracle,
    use_truth ablations). In GNSS-denied/theory cells this set must be empty.
    """
    if require_empty_exemptions and exemptions:
        raise AssertionError(f"GNSS-denied cell with non-empty exemption set: {exemptions}")
    violations = []
    cmap = diagram.connection_map()
    for (in_sys, in_idx), (out_sys, out_idx) in cmap.items():
        if out_sys is not plant and not isinstance(out_sys, MultibodyPlant):
            continue
        if isinstance(in_sys, _SANCTIONED):
            continue
        if in_sys.get_name() in exemptions:
            continue
        violations.append(
            f"{in_sys.get_name()}.{in_sys.get_input_port(in_idx).get_name()} "
            f"<- plant.{out_sys.get_output_port(out_idx).get_name()}")
    if violations:
        raise AssertionError("truth-isolation violations:\n  " + "\n  ".join(violations))
    return True
