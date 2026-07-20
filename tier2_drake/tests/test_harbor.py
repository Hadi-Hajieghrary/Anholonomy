"""Regression tests for the Tier-2 Drake towing scene.

Covers the hand-written geometry (pentagon vertices, ray-polygon intersection,
front-edge attachments) and a short physics smoke test (cables taut, tensions
positive, load advances). Run: python3 -m pytest tier2_drake/tests/ -q
"""
import numpy as np
import pytest

from tier2_drake.harbor import (
    ScenarioConfig, pentagon_vertices, _ray_polygon_hit, front_attachments,
    attachment_and_start)


def test_pentagon_vertices_on_circle():
    R = 4.0
    v = pentagon_vertices(R, 0.0)
    assert v.shape == (5, 2)
    assert np.allclose(np.linalg.norm(v, axis=1), R)
    # phase 0 => first vertex is the bow at (+R, 0)
    assert np.allclose(v[0], [R, 0.0])


def test_ray_hit_vertex_and_edge():
    R = 4.0
    verts = pentagon_vertices(R, 0.0)
    # ray straight at the bow vertex hits at exactly R
    assert _ray_polygon_hit(verts, 0.0) == pytest.approx(R, rel=1e-9)
    # ray at an edge midpoint direction hits at the apothem R*cos(pi/5)
    mid_angle = np.pi / 5.0            # between vertex 0 (0 rad) and vertex 1 (2pi/5)
    assert _ray_polygon_hit(verts, mid_angle) == pytest.approx(R * np.cos(np.pi / 5), rel=1e-9)


def test_ray_hit_bounded_by_apothem_and_circumradius():
    R = 4.0
    verts = pentagon_vertices(R, 0.0)
    for th in np.linspace(-np.pi, np.pi, 73):
        r = _ray_polygon_hit(verts, th)
        assert R * np.cos(np.pi / 5) - 1e-9 <= r <= R + 1e-9


def test_front_attachments_on_boundary_and_symmetric():
    cfg = ScenarioConfig(N=4)
    att, angs = front_attachments(cfg)
    assert len(att) == 4
    R, apo = cfg.load_radius, cfg.load_radius * np.cos(np.pi / 5)
    for a in att:
        r = np.linalg.norm(a[:2])
        assert apo - 1e-9 <= r <= R + 1e-9          # on the pentagon boundary
    # symmetric arc => attachment k mirrors attachment N-1-k in y
    for k in range(4):
        m = att[3 - k]
        assert att[k][0] == pytest.approx(m[0], abs=1e-9)
        assert att[k][1] == pytest.approx(-m[1], abs=1e-9)


def test_starts_are_cable_length_from_attachments():
    cfg = ScenarioConfig(N=5)
    att, starts, _ = attachment_and_start(cfg)
    for k in range(5):
        d = np.hypot(starts[k][0] - att[k][0], starts[k][1] - att[k][1])
        assert d == pytest.approx(cfg.cable_len, rel=1e-9)


@pytest.mark.parametrize("N", [3, 4, 5])
def test_short_transit_taut_and_advancing(N):
    from tier2_drake.run import run_transit
    d = run_transit(ScenarioConfig(N=N), Tend=6.0, log_dt=1.0)
    # load advances forward
    assert d["load"][-1, 0] > d["load"][0, 0]
    # all tensions positive once thrust is on (skip the t=0 sample)
    assert (d["tension"][1:] > 0).all()
    # cable lengths hold: check attach-to-asv distance at the final sample
    cfg = d["cfg"]
    x, y, th = d["load"][-1]
    c, s = np.cos(th), np.sin(th)
    Rm = np.array([[c, -s], [s, c]])
    for k in range(N):
        aw = Rm @ d["attach"][k] + np.array([x, y])
        dist = np.hypot(d["asv"][-1, k, 0] - aw[0], d["asv"][-1, k, 1] - aw[1])
        assert dist == pytest.approx(cfg.cable_len, abs=1e-6)
