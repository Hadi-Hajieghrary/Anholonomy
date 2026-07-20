"""Tier-2 Drake multibody model of N-vessel cooperative barge towing.

Full-multibody counterpart to the Tier-1 reduced-coordinate sim, per
refs/blind_harbor_drake_simulation_plan.md. Planar problem embedded in Drake's
3-D discrete MultibodyPlant (SAP): a barge (load) and N autonomous surface
vessels (ASVs), each a PlanarJoint body, coupled by N taut cables modeled as SAP
distance constraints. Hydrodynamic linear drag gives terminal tow speed; each
vessel applies forward thrust. Cable tension is recovered analytically
(TensionObserver) from documented plant queries — never from a private solver field.

Config-driven: agent count, formation, and physical params live only in ScenarioConfig;
builders loop over cfg.N. N in {3,4,5,...} with zero code changes (plan §2.1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from pydrake.multibody.plant import (
    AddMultibodyPlantSceneGraph, ExternallyAppliedSpatialForce)
from pydrake.multibody.tree import (
    PlanarJoint, SpatialInertia, UnitInertia, RigidBody)
from pydrake.multibody.math import SpatialForce
from pydrake.systems.framework import DiagramBuilder, LeafSystem
from pydrake.common.value import Value
from pydrake.geometry import Box, Cylinder
from pydrake.math import RigidTransform


@dataclass
class ScenarioConfig:
    N: int = 4
    load_shape: str = "pentagon"    # "pentagon" (pointed caisson) or "box" (barge)
    load_radius: float = 4.0        # pentagon circumradius (m) — the load's overall size
    load_phase: float = 0.0         # rad; 0 => one vertex points forward (+x), a bow
    load_len: float = 20.0          # box mode only: x-extent (m)
    load_wid: float = 8.0           # box mode only: y-extent (m)
    load_mass: float = 2500.0       # kg (smaller caisson)
    asv_len: float = 3.0
    asv_wid: float = 1.0
    asv_mass: float = 600.0
    cable_len: float = 12.0         # m (taut distance constraint)
    front_arc: float = 1.15         # rad; attach points spread over +/- this on the front
    thrust: float = 4000.0          # N per vessel, forward (+x), ramped
    thrust_ramp: float = 8.0        # s to full thrust
    drag_lin_load: float = 2500.0   # N/(m/s)
    drag_lin_asv: float = 350.0
    drag_ang_load: float = 2.0e4    # N·m/(rad/s)
    drag_ang_asv: float = 800.0
    dt: float = 1.0e-3
    perturb: float = 0.0            # rad; asymmetry added to the initial fan (0 = symmetric)
    thrust_scale: tuple = ()        # per-vessel thrust multipliers; () = all 1.0 (symmetric)
    thrust_frame: str = "world"     # "world" (legacy; executed artifacts) | "body_weathervane"
    formation: str = "fan"          # "fan" (generic: distinct shapes) | "parallel"
                                    # (THE THEOREM'S symmetric class: all cables along +x
                                    # from their attach points => IDENTICAL (sigma, sigma_i)
                                    # across agents — Cor 7.3's s_i ≡ s_j, which equal fan
                                    # ANGLES do not give [measured: fan arms show equal
                                    # floors because both are generic])
    k_align: float = 500.0          # N·m/rad weathervane stiffness (body mode) [DESIGN]


def pentagon_vertices(R: float, phase: float = 0.0):
    """5 vertices of a regular pentagon, circumradius R. phase=0 puts a vertex at +x (bow)."""
    ang = phase + 2 * np.pi * np.arange(5) / 5.0
    return np.stack([R * np.cos(ang), R * np.sin(ang)], axis=1)   # (5,2)


def _ray_polygon_hit(verts, theta):
    """Distance from center along direction theta to the polygon boundary."""
    d = np.array([np.cos(theta), np.sin(theta)])
    best = np.inf
    M = len(verts)
    for k in range(M):
        a, b = verts[k], verts[(k + 1) % M]
        e = b - a
        # solve a + s e = r d  =>  [e, -d] [s, r]^T = -a
        A = np.array([[e[0], -d[0]], [e[1], -d[1]]])
        try:
            s, r = np.linalg.solve(A, -a)
        except np.linalg.LinAlgError:
            continue
        if -1e-9 <= s <= 1 + 1e-9 and r > 1e-9:
            best = min(best, r)
    return best


def front_attachments(cfg: ScenarioConfig):
    """N attach points on the load's front boundary, spread across +/- front_arc (load frame)."""
    N = cfg.N
    if cfg.load_shape == "pentagon":
        verts = pentagon_vertices(cfg.load_radius, cfg.load_phase)
        angs = np.linspace(-cfg.front_arc, cfg.front_arc, N) if N > 1 else np.array([0.0])
        pts = []
        for th in angs:
            rr = _ray_polygon_hit(verts, th)
            pts.append(np.array([rr * np.cos(th), rr * np.sin(th), 0.0]))
        return pts, angs
    # box fallback: spread across the bow face
    ys = np.linspace(-cfg.load_wid * 0.5, cfg.load_wid * 0.5, N)
    return [np.array([cfg.load_len * 0.5, y, 0.0]) for y in ys], np.zeros(N)


def _planar_box_body(plant, name, mass, lx, ly, color):
    """Rigid planar box body (used for vessels, and the box-mode load)."""
    G = UnitInertia.SolidBox(lx, ly, 1.0)
    M = SpatialInertia(mass, np.zeros(3), G)
    body = plant.AddRigidBody(name, M)
    plant.RegisterVisualGeometry(body, RigidTransform(), Box(lx, ly, 0.6),
                                 name + "_vis", np.asarray(color))
    plant.AddJoint(PlanarJoint(name + "_joint", plant.world_frame(), body.body_frame()))
    return body


def _planar_disk_body(plant, name, mass, radius, color):
    """Rigid planar body with a disk (cylinder) inertia proxy — for the pentagon load.

    Drake has no pentagon primitive; the physics uses a solid-cylinder inertia about z
    (I_zz = 1/2 m r^2), which is the right order for a compact polygon. The pentagon
    outline is drawn by the renderer, not by Drake's visual geometry.
    """
    G = UnitInertia.SolidCylinder(radius, 0.6, [0.0, 0.0, 1.0])
    M = SpatialInertia(mass, np.zeros(3), G)
    body = plant.AddRigidBody(name, M)
    plant.RegisterVisualGeometry(body, RigidTransform(), Cylinder(radius, 0.6),
                                 name + "_vis", np.asarray(color))
    plant.AddJoint(PlanarJoint(name + "_joint", plant.world_frame(), body.body_frame()))
    return body


def attachment_and_start(cfg: ScenarioConfig):
    """Front attachment points on the load and initial vessel poses (cables taut)."""
    attach, arc_angles = front_attachments(cfg)
    if cfg.formation == "parallel":
        arc_angles = np.zeros(cfg.N)          # identical shapes: all cables along +x
    angles = arc_angles + cfg.perturb * np.linspace(0, 1, cfg.N)   # break symmetry if asked
    starts = []
    for k in range(cfg.N):
        a = attach[k][:2]
        if cfg.formation == "parallel":
            # epsilon-perturbation: perturb grades the cable directions away from
            # exact parallel (the C9b near-symmetric ladder) — angles[k] carries it
            dirn = np.array([np.cos(angles[k]), np.sin(angles[k])])
        else:
            outward = a / (np.linalg.norm(a) + 1e-9)
            d = np.array([np.cos(angles[k]), np.sin(angles[k])])
            dirn = 0.5 * outward + 0.5 * d
            dirn = dirn / np.linalg.norm(dirn)
        pos = a + cfg.cable_len * dirn
        starts.append((pos[0], pos[1], float(np.arctan2(dirn[1], dirn[0]))))
    return attach, starts, angles


class TowController(LeafSystem):
    """Hydrodynamic drag on every body + ramped forward thrust on each vessel.

    Reads body spatial velocities and poses; outputs the list of
    ExternallyAppliedSpatialForce the plant's applied_spatial_force port consumes.
    """
    def __init__(self, plant, cfg: ScenarioConfig, load_idx, asv_idxs):
        super().__init__()
        self._plant = plant
        self._cfg = cfg
        self._load = load_idx
        self._asvs = asv_idxs
        self._attach = [a[:2] for a in front_attachments(cfg)[0]]   # for weathervane mode
        from pydrake.multibody.math import SpatialVelocity
        self._V_in = self.DeclareAbstractInputPort(
            "body_spatial_velocities", Value([SpatialVelocity()]))
        self._X_in = self.DeclareAbstractInputPort(
            "body_poses", Value([RigidTransform()]))
        self.DeclareAbstractOutputPort(
            "spatial_forces", lambda: Value([ExternallyAppliedSpatialForce()]),
            self._calc)

    def _calc(self, context, output):
        cfg = self._cfg
        Vs = self._V_in.Eval(context)
        Xs = self._X_in.Eval(context)
        t = context.get_time()
        ramp = min(1.0, t / cfg.thrust_ramp)
        forces = []

        def drag(body_idx, c_lin, c_ang, extra_force_W=None, extra_tau_z=0.0):
            V = Vs[int(body_idx)]
            v = V.translational()
            w = V.rotational()
            F = -c_lin * v
            if extra_force_W is not None:
                F = F + extra_force_W
            tau = np.array([0.0, 0.0, -c_ang * w[2] + extra_tau_z])
            easf = ExternallyAppliedSpatialForce()
            easf.body_index = body_idx
            easf.p_BoBq_B = np.zeros(3)                       # at CoM
            easf.F_Bq_W = SpatialForce(tau, F)
            forces.append(easf)

        drag(self._load, cfg.drag_lin_load, cfg.drag_ang_load)
        scales = cfg.thrust_scale if cfg.thrust_scale else (1.0,) * len(self._asvs)
        X_load = Xs[int(self._load)]
        thL = np.arctan2(X_load.rotation().matrix()[1, 0], X_load.rotation().matrix()[0, 0])
        Rl = np.array([[np.cos(thL), -np.sin(thL)], [np.sin(thL), np.cos(thL)]])
        for k, ai in enumerate(self._asvs):
            mag = cfg.thrust * ramp * scales[k]
            if cfg.thrust_frame == "body_weathervane":
                X_a = Xs[int(ai)]
                thA = np.arctan2(X_a.rotation().matrix()[1, 0], X_a.rotation().matrix()[0, 0])
                thrust_W = mag * np.array([np.cos(thA), np.sin(thA), 0.0])   # body +x
                attach_w = X_load.translation()[:2] + Rl @ np.asarray(self._attach[k])
                d = X_a.translation()[:2] - attach_w
                cable_ang = np.arctan2(d[1], d[0])            # attach -> vessel (pull dir)
                err = (thA - cable_ang + np.pi) % (2 * np.pi) - np.pi
                tau_z = -cfg.k_align * np.sin(err)            # weathervane toward the cable
                drag(ai, cfg.drag_lin_asv, cfg.drag_ang_asv, extra_force_W=thrust_W,
                     extra_tau_z=tau_z)
            else:                                             # legacy world-frame (executed)
                thrust_W = np.array([mag, 0.0, 0.0])
                drag(ai, cfg.drag_lin_asv, cfg.drag_ang_asv, extra_force_W=thrust_W)
        output.set_value(forces)


def build_scenario(cfg: ScenarioConfig):
    """Assemble the diagram. Returns (diagram, plant, scene_graph, info)."""
    builder = DiagramBuilder()
    plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=cfg.dt)

    load_color = np.array([0.20, 0.28, 0.38, 1.0])
    if cfg.load_shape == "pentagon":
        load = _planar_disk_body(plant, "load", cfg.load_mass, cfg.load_radius, load_color)
    else:
        load = _planar_box_body(plant, "load", cfg.load_mass, cfg.load_len, cfg.load_wid, load_color)
    asvs = []
    for i in range(cfg.N):
        b = _planar_box_body(plant, f"asv_{i}", cfg.asv_mass, cfg.asv_len, cfg.asv_wid,
                             np.array([0.75, 0.28, 0.22, 1.0]))
        asvs.append(b)

    attach, starts, angles = attachment_and_start(cfg)
    for i in range(cfg.N):
        plant.AddDistanceConstraint(load, attach[i], asvs[i], np.zeros(3), cfg.cable_len)

    plant.mutable_gravity_field().set_gravity_vector([0, 0, 0])  # inert for planar DOFs
    plant.Finalize()

    ctrl = builder.AddSystem(TowController(
        plant, cfg, load.index(), [b.index() for b in asvs]))
    builder.Connect(plant.get_body_spatial_velocities_output_port(),
                    ctrl.GetInputPort("body_spatial_velocities"))
    builder.Connect(plant.get_body_poses_output_port(),
                    ctrl.GetInputPort("body_poses"))
    builder.Connect(ctrl.GetOutputPort("spatial_forces"),
                    plant.get_applied_spatial_force_input_port())

    diagram = builder.Build()
    info = {"load": load, "asvs": asvs, "attach": attach, "starts": starts,
            "angles": angles, "cfg": cfg}
    return diagram, plant, scene_graph, info


def set_initial_state(plant, plant_context, info):
    """Place the load at origin and vessels in the taut fan formation."""
    cfg = info["cfg"]
    load_joint = plant.GetJointByName("load_joint")
    load_joint.set_translation(plant_context, [0.0, 0.0])
    load_joint.set_rotation(plant_context, 0.0)
    for i in range(cfg.N):
        j = plant.GetJointByName(f"asv_{i}_joint")
        x, y, yaw = info["starts"][i]
        j.set_translation(plant_context, [x, y])
        j.set_rotation(plant_context, yaw)
