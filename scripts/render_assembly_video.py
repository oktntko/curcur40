# -*- coding: utf-8 -*-
"""
Render a 1080p 60fps PBR 3D assembly animation video (`docs/assets/assembly_animation.mp4`)
and an inline-looping animated WebP (`docs/assets/assembly_animation.webp`) for curcur40,
following the real build guide assembly flow:

  Stage 1: Trackball Sub-Assembly (Sensor PCB + PMW3360 + LM19-LSI Lens + Cup + 3x Ceramic Balls)
  Stage 2: Under-Plate Passive Magnetic Inertia Wheel Sub-Assembly
           (#01 45# Steel Flywheel + #07 Bearings + #02 Magnet Holder & #08 Magnet
            + #03 Rocker + #04 Cradle C-clip snap + South Detent Adjuster & Spin Demo)
  Stage 3: Sealed White Bottom Cases + 16x Brass Heat-Set Inserts + Trackball Unit Mounting (TB1-TB4)
  Stage 4: Inertia Wheel Unit + Left/Right Black Main PCBs (WC1-WC2 & 12x Key-Valley M2x6 Screws)
  Stage 5: Black FR-4 Top Plates + 40x Kailh Choc V2 Switches + 40x White Keycaps + 25mm Ball
  Stage 6: Completed Showcase (Wheel Free-Spin + Smooth Turntable Camera Orbit)

Run with:
  & "$env:USERPROFILE\\.local\\bin\\uvx.exe" --no-config --managed-python --python 3.13 `
      --from "cadgen==0.7.26" --with pyvista --with imageio-ffmpeg --with pillow `
      python scripts/render_assembly_video.py
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import pyvista as pv
from cadgen import build123d as bd
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = Path(__file__).resolve().parent.parent
if str(WORKSPACE / "scripts") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "scripts"))

CASES_DIR = WORKSPACE / "cases"
ASSEMBLIES_DIR = CASES_DIR / "assemblies"
DEFAULT_OUT_MP4 = WORKSPACE / "docs" / "assets" / "assembly_animation.mp4"
DEFAULT_OUT_WEBP = WORKSPACE / "docs" / "assets" / "assembly_animation.webp"

from generate_full_assembly import (  # noqa: E402
    LEFT_PERIMETER_HOLES_PCB,
    LEFT_SWITCHES,
    RIGHT_PERIMETER_HOLES_PCB,
    RIGHT_SWITCHES,
    RIGHT_TB_HOLES_PCB,
    THETA_TENT_DEG,
    X_PINKY_OUTER,
    Z_PINKY_BOTTOM,
    _find_footprint_xy,
    build_top_plate_solid,
    export_kicad_pcb_solids,
    make_insert_and_screw,
    make_jst_shr06v_plug_from_header,
    to_step_left,
    to_step_right,
)
from generate_inertia_wheel import (  # noqa: E402
    U_PIV,
    W_PIV,
    WC1_PCB,
    WC2_PCB,
    X_AXLE_STEP,
    Y_AXLE_STEP,
    Z_AXLE_STEP,
    build_hardware_parts_local,
    build_magnet_holder_local,
    build_steel_flywheel_local,
    build_wheel_cradle_local,
    build_wheel_rocker_local,
)


# ---------------------------------------------------------------------------
# Math & Easing Utilities
# ---------------------------------------------------------------------------
def clamp01(x: float) -> float:
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)


def progress(t: float, t0: float, t1: float) -> float:
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp01((t - t0) / (t1 - t0))


def ease_in_out_cubic(u: float) -> float:
    u = clamp01(u)
    return 4.0 * u * u * u if u < 0.5 else 1.0 - ((-2.0 * u + 2.0) ** 3) / 2.0


def ease_out_cubic(u: float) -> float:
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 3


def ease_out_back(u: float, overshoot: float = 0.65) -> float:
    """Subtle crisp mechanical snap settle at the end of insertion."""
    u = clamp01(u)
    c1 = overshoot
    c3 = c1 + 1.0
    return 1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)


def mat_identity() -> np.ndarray:
    return np.eye(4, dtype=np.float64)


def mat_translate(dx: float, dy: float, dz: float) -> np.ndarray:
    m = np.eye(4, dtype=np.float64)
    m[0, 3] = dx
    m[1, 3] = dy
    m[2, 3] = dz
    return m


def mat_rot_x(deg: float) -> np.ndarray:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4, dtype=np.float64)
    m[1, 1], m[1, 2] = c, -s
    m[2, 1], m[2, 2] = s, c
    return m


def mat_rot_y(deg: float) -> np.ndarray:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4, dtype=np.float64)
    m[0, 0], m[0, 2] = c, s
    m[2, 0], m[2, 2] = -s, c
    return m


def mat_rot_z(deg: float) -> np.ndarray:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4, dtype=np.float64)
    m[0, 0], m[0, 1] = c, -s
    m[1, 0], m[1, 1] = s, c
    return m


def make_desk_matrix(is_right: bool) -> np.ndarray:
    """Exact 4x4 matrix equivalent of `transform_to_desk(shape, is_right)`."""
    px = X_PINKY_OUTER if is_right else -X_PINKY_OUTER
    pz = Z_PINKY_BOTTOM
    ry = THETA_TENT_DEG if is_right else -THETA_TENT_DEG
    return mat_translate(px, 0.0, 0.0) @ mat_rot_y(ry) @ mat_translate(-px, 0.0, -pz)


M_DESK_L = make_desk_matrix(is_right=False)
M_DESK_R = make_desk_matrix(is_right=True)
M_WHEEL_TO_STEP = mat_translate(X_AXLE_STEP, Y_AXLE_STEP, Z_AXLE_STEP)


# ---------------------------------------------------------------------------
# Mesh Conversion & Procedural Studio Environment
# ---------------------------------------------------------------------------
def solid_to_polydata(
    solid: bd.Solid,
    tol: float = 0.06,
    ang_tol: float = 0.18,
    feature_angle: float = 35.0,
) -> pv.PolyData:
    verts, tris = solid.tessellate(tol, angular_tolerance=ang_tol)
    if not verts or not tris:
        return pv.PolyData()
    pts = np.array([(float(v.X), float(v.Y), float(v.Z)) for v in verts], dtype=np.float32)
    tri_arr = np.asarray(tris, dtype=np.int64)
    faces = np.hstack([np.full((len(tri_arr), 1), 3, dtype=np.int64), tri_arr]).ravel()
    mesh = pv.PolyData(pts, faces)
    return mesh.compute_normals(
        cell_normals=False,
        point_normals=True,
        split_vertices=True,
        auto_orient_normals=True,
        feature_angle=feature_angle,
    )


def merge_solids_to_polydata(
    solids: list[bd.Solid],
    tol: float = 0.10,
    ang_tol: float = 0.25,
    feature_angle: float = 38.0,
) -> pv.PolyData:
    meshes = [
        solid_to_polydata(s, tol=tol, ang_tol=ang_tol, feature_angle=feature_angle)
        for s in solids
    ]
    meshes = [m for m in meshes if m.n_points > 0]
    if not meshes:
        return pv.PolyData()
    if len(meshes) == 1:
        return meshes[0]
    return pv.merge(meshes, merge_points=False)


def build_studio_env_texture(height: int = 256, width: int = 512) -> pv.Texture:
    """
    Create a crisp procedural studio softbox equirectangular reflection map
    so metallic steel, brass inserts, and glossy pearl-silver ball exhibit rich highlights.
    """
    v = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]  # 0 = zenith, 1 = nadir
    u = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]   # azimuth 0..2pi

    theta = v * math.pi
    phi = (u - 0.5) * 2.0 * math.pi

    dx = np.sin(theta) * np.cos(phi)
    dy = np.sin(theta) * np.sin(phi)
    dz = np.cos(theta)

    # Base sky-to-ground gradient
    sky_t = np.clip(dz * 0.5 + 0.5, 0.0, 1.0)
    base_r = 0.20 + 0.58 * (sky_t ** 0.85)
    base_g = 0.22 + 0.60 * (sky_t ** 0.85)
    base_b = 0.26 + 0.63 * (sky_t ** 0.82)
    rgb = np.broadcast_to(np.stack([base_r, base_g, base_b], axis=-1), (height, width, 3)).copy()

    # Studio softbox 1: Overhead main softbox
    sb1 = np.clip(dx * 0.15 - dy * 0.35 + dz * 0.92, 0.0, 1.0) ** 9.0
    rgb += sb1[..., None] * np.array([0.85, 0.86, 0.90], dtype=np.float32)

    # Studio softbox 2: Front-left warm-white strip
    sb2 = np.clip(-dx * 0.60 - dy * 0.65 + dz * 0.46, 0.0, 1.0) ** 14.0
    rgb += sb2[..., None] * np.array([0.65, 0.64, 0.60], dtype=np.float32)

    # Studio softbox 3: Back-right cool rim strip (catches machined wheel flutes)
    sb3 = np.clip(dx * 0.68 + dy * 0.52 + dz * 0.51, 0.0, 1.0) ** 16.0
    rgb += sb3[..., None] * np.array([0.62, 0.68, 0.78], dtype=np.float32)

    # Crisp horizon studio ring highlight
    horiz = np.exp(-((dz - 0.08) / 0.10) ** 2) * 0.16
    rgb += horiz[..., None]

    img_u8 = np.uint8(np.clip(rgb * 255.0, 0.0, 255.0))
    tex = pv.Texture(img_u8)
    tex.mipmap = True
    tex.interpolate = True
    return tex


# ---------------------------------------------------------------------------
# Visual Proxy Builders (Switches & Sculpted Low-Profile Keycaps)
# ---------------------------------------------------------------------------
def build_visual_choc_v2_meshes() -> tuple[pv.PolyData, pv.PolyData]:
    """
    Canonical Kailh Choc V2 switch at origin (0, 0) in Global STEP Z stackup:
      - Housing mesh (smoked dark grey): stem boss + plate body + upper flange + latches
      - Stem mesh (cool medium-dark grey): Ø 4.8 mm actuator + MX cross stem up to Z = +0.55 mm
    """
    stem_boss = bd.Cylinder(
        radius=2.40, height=1.57, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, -5.75)))
    with bd.BuildSketch(bd.Plane.XY.offset(-4.18)) as sk_body:
        bd.RectangleRounded(13.80, 13.80, 0.45)
    body = bd.extrude(sk_body.sketch, amount=2.19)
    with bd.BuildSketch(bd.Plane.XY.offset(-1.99)) as sk_flange:
        bd.RectangleRounded(14.50, 14.50, 0.55)
    flange = bd.extrude(sk_flange.sketch, amount=1.09)
    housing_solid = (stem_boss + body + flange).solids()[0]

    act_cyl = bd.Cylinder(
        radius=2.65, height=0.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    ).moved(bd.Location((0, 0, -0.90)))
    cross_x = bd.Box(4.00, 1.15, 1.45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, -0.90))
    )
    cross_y = bd.Box(1.15, 4.00, 1.45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).moved(
        bd.Location((0, 0, -0.90))
    )
    stem_solid = (act_cyl + cross_x + cross_y).solids()[0]

    return (
        solid_to_polydata(housing_solid, tol=0.07, ang_tol=0.22),
        solid_to_polydata(stem_solid, tol=0.06, ang_tol=0.20),
    )


def build_visual_keycap_mesh() -> pv.PolyData:
    """
    Canonical Choc V2 low-profile 1u keycap at origin (0, 0) (`Z = +1.30..+3.60 mm`)
    with tapered top profile & soft top bevel so individual white keycaps catch studio light.
    """
    with bd.BuildPart() as bp:
        with bd.BuildSketch(bd.Plane.XY.offset(1.30)):
            bd.RectangleRounded(18.00, 18.00, 1.60)
        with bd.BuildSketch(bd.Plane.XY.offset(3.60)):
            bd.RectangleRounded(16.20, 16.20, 1.85)
        bd.loft()
        top_face = bp.faces().sort_by(bd.Axis.Z)[-1]
        bd.fillet(top_face.edges(), radius=0.42)
    cap_solid = bp.part.solids()[0]
    return solid_to_polydata(cap_solid, tol=0.06, ang_tol=0.18, feature_angle=30.0)


def build_ceramic_ball_solids(tb_cx: float, tb_cy: float, tb_cz: float) -> list[tuple[bd.Solid, tuple[float, float, float]]]:
    """3x Ø2.00 mm zirconia support balls + their inward snap vectors in Global STEP frame."""
    r_orbit = 13.50
    z_ball_center = 18.30
    elev_rad = math.radians(52.0)
    out = []
    for az_deg in (30.0, 150.0, 270.0):
        az_rad = math.radians(az_deg)
        ux = math.cos(elev_rad) * math.cos(az_rad)
        uy = math.cos(elev_rad) * math.sin(az_rad)
        uz = -math.sin(elev_rad)
        bx = tb_cx + r_orbit * ux
        by = tb_cy + r_orbit * uy
        bz = tb_cz + z_ball_center + r_orbit * uz
        sph = bd.Sphere(radius=1.00).moved(bd.Location((bx, by, bz))).solids()[0]
        # Start slightly inward & above inside the cup bowl before snapping into the pocket
        start_offset = (-5.5 * ux, -5.5 * uy, 14.0)
        out.append((sph, start_offset))
    return out


# ---------------------------------------------------------------------------
# Material Palette & Scene Actor Wrapper
# ---------------------------------------------------------------------------
@dataclass
class MaterialSpec:
    color: str
    metallic: float = 0.05
    roughness: float = 0.45
    opacity: float = 1.0


MAT_CASE_WHITE = MaterialSpec(color="#F7F9FC", metallic=0.02, roughness=0.46)
MAT_KEYCAP_WHITE = MaterialSpec(color="#FFFFFF", metallic=0.03, roughness=0.30)
MAT_CUP_BLACK = MaterialSpec(color="#1B1F26", metallic=0.04, roughness=0.50)
MAT_WHEEL_RESIN_BLACK = MaterialSpec(color="#1C2028", metallic=0.04, roughness=0.48)
MAT_CRADLE_BLACK = MaterialSpec(color="#14171E", metallic=0.04, roughness=0.52)
MAT_PCB_BLACK = MaterialSpec(color="#0E1015", metallic=0.06, roughness=0.38)
MAT_PLATE_BLACK = MaterialSpec(color="#161920", metallic=0.12, roughness=0.34)
MAT_SWITCH_BODY = MaterialSpec(color="#3B424F", metallic=0.05, roughness=0.38)
MAT_SWITCH_STEM = MaterialSpec(color="#687385", metallic=0.05, roughness=0.34)
MAT_STEEL_WHEEL = MaterialSpec(color="#E0E7F0", metallic=0.93, roughness=0.19)
MAT_BEARING_STEEL = MaterialSpec(color="#D0D8E2", metallic=0.88, roughness=0.24)
MAT_SCREW_STEEL = MaterialSpec(color="#CCD5E0", metallic=0.86, roughness=0.25)
MAT_MAGNET_NI = MaterialSpec(color="#F0F5FA", metallic=0.96, roughness=0.12)
MAT_BRASS = MaterialSpec(color="#E4B24A", metallic=0.88, roughness=0.24)
MAT_BALL_PEARL = MaterialSpec(color="#EEF2F8", metallic=0.30, roughness=0.08)
MAT_CERAMIC_WHITE = MaterialSpec(color="#FFFFFF", metallic=0.08, roughness=0.08)
MAT_SENSOR_IC = MaterialSpec(color="#1E2229", metallic=0.06, roughness=0.44)
MAT_LENS_CLEAR = MaterialSpec(color="#C9E6FF", metallic=0.10, roughness=0.08, opacity=0.72)
MAT_SMD_DARK = MaterialSpec(color="#2D333E", metallic=0.08, roughness=0.44)
MAT_SMD_METAL = MaterialSpec(color="#CFD7E2", metallic=0.88, roughness=0.22)
MAT_JST_IVORY = MaterialSpec(color="#E2DDD0", metallic=0.03, roughness=0.46)
MAT_JST_PLUG = MaterialSpec(color="#303540", metallic=0.04, roughness=0.48)
MAT_REDDOT = MaterialSpec(color="#D94848", metallic=0.05, roughness=0.36)


class AnimPart:
    def __init__(self, plotter: pv.Plotter, mesh: pv.PolyData, mat: MaterialSpec, name: str = ""):
        self.name = name
        self.base_opacity = mat.opacity
        self.actor = plotter.add_mesh(
            mesh,
            color=mat.color,
            pbr=True,
            metallic=mat.metallic,
            roughness=mat.roughness,
            opacity=mat.opacity,
            smooth_shading=True,
        )
        self._visible = True
        self._last_opacity = mat.opacity
        self._backface_culled = False

    def update(self, matrix: np.ndarray, alpha: float = 1.0):
        a = clamp01(alpha)
        if a <= 0.002:
            if self._visible:
                self.actor.SetVisibility(False)
                self._visible = False
            return
        if a >= 0.999:
            a = 1.0
        if not self._visible:
            self.actor.SetVisibility(True)
            self._visible = True
        target_op = self.base_opacity if a >= 1.0 else (self.base_opacity * a)
        if target_op != self._last_opacity:
            self.actor.prop.opacity = target_op
            self._last_opacity = target_op
        if self.base_opacity >= 1.0:
            want_cull = target_op < 1.0
            if want_cull != self._backface_culled:
                self.actor.GetProperty().SetBackfaceCulling(want_cull)
                self._backface_culled = want_cull
        self.actor.user_matrix = matrix


def drop_state(
    t: float,
    t_start: float,
    duration: float,
    offset_vec: tuple[float, float, float],
    fade_frac: float = 0.30,
    snap: bool = False,
) -> tuple[np.ndarray, float]:
    """
    Returns `(local_translation_matrix, alpha)` for a part entering along `offset_vec` -> `(0, 0, 0)`.
    """
    if t < t_start:
        return mat_identity(), 0.0
    u = progress(t, t_start, t_start + duration)
    alpha = clamp01(u / max(fade_frac, 1e-4))
    e = ease_out_back(u, 0.45) if snap else ease_out_cubic(u)
    rem = 1.0 - e
    return mat_translate(offset_vec[0] * rem, offset_vec[1] * rem, offset_vec[2] * rem), alpha


# ---------------------------------------------------------------------------
# KiCad Component Classifier
# ---------------------------------------------------------------------------
def split_kicad_components(
    comps: list[bd.Solid],
    special_ivory: list[bd.Solid],
    special_red: list[bd.Solid],
) -> tuple[list[bd.Solid], list[bd.Solid], list[bd.Solid], list[bd.Solid]]:
    """Classify KiCad 3D solids into `(metal_solids, dark_solids, ivory_solids, red_solids)`."""
    ivory_ids = {id(s) for s in special_ivory}
    red_ids = {id(s) for s in special_red}
    metals, darks = [], []
    for c in comps:
        cid = id(c)
        if cid in ivory_ids or cid in red_ids:
            continue
        bb = c.bounding_box()
        vol = c.volume
        # USB-C stainless shells have wide footprint near board edges; small leads have tiny volume
        is_usbc_shell = max(bb.size.X, bb.size.Y) > 6.5 and bb.size.Z > 2.5 and vol < 180.0
        if is_usbc_shell or vol < 2.2:
            metals.append(c)
        else:
            darks.append(c)
    return metals, darks, special_ivory, special_red


def build_case_shadow_actor(plotter: pv.Plotter, left_case_mesh: pv.PolyData, right_case_mesh: pv.PolyData):
    """
    Smooth analytical studio contact-shadow quad at Z = -0.08 mm under Left & Right Cases:
    eliminates distant floor horizon/SSAO banding while grounding the white cases cleanly on the desk.
    """
    plane = pv.Plane(
        center=(0.0, -78.0, -0.08),
        direction=(0.0, 0.0, 1.0),
        i_size=360.0,
        j_size=210.0,
        i_resolution=110,
        j_resolution=70,
    )
    # Sample XY points across both desk-transformed cases (perimeter + interior bosses/walls)
    pts_l = (left_case_mesh.points @ M_DESK_L[:3, :3].T) + M_DESK_L[:3, 3]
    pts_r = (right_case_mesh.points @ M_DESK_R[:3, :3].T) + M_DESK_R[:3, 3]
    foot_pts = np.vstack([pts_l[:, :2], pts_r[:, :2]])
    step = max(1, len(foot_pts) // 900)
    sample_xy = foot_pts[::step]

    grid_xy = plane.points[:, :2]
    diff = grid_xy[:, None, :] - sample_xy[None, :, :]
    min_d2 = np.min(np.sum(diff * diff, axis=-1), axis=1)
    alpha = 0.22 * np.exp(-min_d2 / (2.0 * (12.5 ** 2)))

    rgba = np.zeros((plane.n_points, 4), dtype=np.uint8)
    rgba[:, 0] = 28
    rgba[:, 1] = 36
    rgba[:, 2] = 48
    rgba[:, 3] = np.uint8(np.clip(alpha * 255.0, 0.0, 255.0))
    plane.point_data["rgba"] = rgba

    return plotter.add_mesh(plane, scalars="rgba", rgba=True, lighting=False, smooth_shading=True)
def build_scene(plotter: pv.Plotter) -> dict:
    t0 = time.perf_counter()
    print("[1/3] Loading & tessellating curcur40 3D CAD & KiCad solids...")

    # 1. Left & Right Cases (in Global STEP pre-desk frame)
    left_case_s = bd.import_step(str(CASES_DIR / "left.step")).solids()[0]
    right_case_s = bd.import_step(str(CASES_DIR / "right.step")).solids()[0]
    left_case_mesh = solid_to_polydata(left_case_s, tol=0.07)
    right_case_mesh = solid_to_polydata(right_case_s, tol=0.07)
    floor_actor = build_case_shadow_actor(plotter, left_case_mesh, right_case_mesh)
    left_case = AnimPart(plotter, left_case_mesh, MAT_CASE_WHITE, "Left_Case")
    right_case = AnimPart(plotter, right_case_mesh, MAT_CASE_WHITE, "Right_Case")

    # 2. KiCad PCBs & 3D Components
    left_pcb_s, left_comps = export_kicad_pcb_solids(
        "pcbs/left/curcur40-left.kicad_pcb", (-14.2875, -57.1500, -5.8000), "Left_Main_PCB", "Left_PCB"
    )
    right_pcb_s, right_comps = export_kicad_pcb_solids(
        "pcbs/right/curcur40-right.kicad_pcb", (14.2875, -57.1500, -5.8000), "Right_Main_PCB", "Right_PCB"
    )
    sensor_pcb_s, pmw_comps = export_kicad_pcb_solids(
        "pcbs/pmw3360/curcur40-pmw3360.kicad_pcb", (14.2875, -57.1500, -17.6000), "PMW3360_Sensor_PCB", "Sensor_PCB"
    )

    sw_click_x, sw_click_y = to_step_right(-2.0125, -2.0000)
    rexsw1_plungers = [
        c
        for c in right_comps
        if math.hypot(c.bounding_box().center().X - sw_click_x, c.bounding_box().center().Y - sw_click_y) < 1.0
        and c.bounding_box().min.Z < -9.50
    ]

    rj3_px, rj3_py = _find_footprint_xy("pcbs/right/curcur40-right.kicad_pcb", "rJ3")
    rj3_x, rj3_y = to_step_right(rj3_px, rj3_py)
    rj3_solids = [
        c
        for c in right_comps
        if math.hypot(c.bounding_box().center().X - rj3_x, c.bounding_box().center().Y - rj3_y) < 5.0
        and c.bounding_box().min.Z < -7.00
    ]
    rj3_shroud = [max(rj3_solids, key=lambda s: s.volume)]
    rj3_plug_s = make_jst_shr06v_plug_from_header(rj3_solids, right_pcb_s, "Right_PCB_rJ3_SHR06V_Plug")

    j1_px, j1_py = _find_footprint_xy("pcbs/pmw3360/curcur40-pmw3360.kicad_pcb", "J1")
    j1_x, j1_y = to_step_right(j1_px, j1_py)
    j1_solids = [
        c
        for c in pmw_comps
        if math.hypot(c.bounding_box().center().X - j1_x, c.bounding_box().center().Y - j1_y) < 5.0
        and c.bounding_box().min.Z < -18.50
    ]
    j1_shroud = [max(j1_solids, key=lambda s: s.volume)]
    j1_plug_s = make_jst_shr06v_plug_from_header(j1_solids, sensor_pcb_s, "Sensor_PCB_J1_SHR06V_Plug")

    l_metals, l_darks, _, _ = split_kicad_components(left_comps, [], [])
    r_metals, r_darks, r_ivory, r_red = split_kicad_components(right_comps, rj3_shroud, rexsw1_plungers)
    p_metals, p_darks, p_ivory, _ = split_kicad_components(pmw_comps, j1_shroud, [])

    left_pcb_parts = [
        AnimPart(plotter, solid_to_polydata(left_pcb_s, tol=0.07), MAT_PCB_BLACK, "Left_PCB"),
        AnimPart(plotter, merge_solids_to_polydata(l_metals), MAT_SMD_METAL, "Left_SMD_Metal"),
        AnimPart(plotter, merge_solids_to_polydata(l_darks), MAT_SMD_DARK, "Left_SMD_Dark"),
    ]
    right_pcb_parts = [
        AnimPart(plotter, solid_to_polydata(right_pcb_s, tol=0.07), MAT_PCB_BLACK, "Right_PCB"),
        AnimPart(plotter, merge_solids_to_polydata(r_metals), MAT_SMD_METAL, "Right_SMD_Metal"),
        AnimPart(plotter, merge_solids_to_polydata(r_darks), MAT_SMD_DARK, "Right_SMD_Dark"),
        AnimPart(plotter, merge_solids_to_polydata(r_ivory), MAT_JST_IVORY, "Right_JST_Shroud"),
        AnimPart(plotter, merge_solids_to_polydata(r_red), MAT_REDDOT, "Right_rEXSW1_RedDot"),
        AnimPart(plotter, solid_to_polydata(rj3_plug_s, tol=0.06), MAT_JST_PLUG, "Right_rJ3_Plug"),
    ]
    sensor_pcb_parts = [
        AnimPart(plotter, solid_to_polydata(sensor_pcb_s, tol=0.06), MAT_PCB_BLACK, "Sensor_PCB"),
        AnimPart(plotter, merge_solids_to_polydata(p_metals), MAT_SMD_METAL, "Sensor_SMD_Metal"),
        AnimPart(plotter, merge_solids_to_polydata(p_darks), MAT_SMD_DARK, "Sensor_SMD_Dark"),
        AnimPart(plotter, merge_solids_to_polydata(p_ivory), MAT_JST_IVORY, "Sensor_JST_Shroud"),
    ]
    j1_plug = AnimPart(plotter, solid_to_polydata(j1_plug_s, tol=0.06), MAT_JST_PLUG, "Sensor_J1_Plug")

    # 3. Trackball Sub-Assembly Parts (in Global STEP frame)
    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, -16.0000
    cup_s = bd.import_step(str(CASES_DIR / "trackball-cup.step")).moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    ball_s = bd.Sphere(radius=12.50).moved(bd.Location((tb_cx, tb_cy, tb_cz + 18.30))).solids()[0]

    asm_opt = bd.import_step(str(ASSEMBLIES_DIR / "pmw3360-lens-pcb-assembly.step"))
    sensor_local, lens_local = None, None
    for s in asm_opt.solids():
        bb = s.bounding_box()
        if bb.min.Z < -3.5:
            sensor_local = s
        elif bb.max.Z > 3.0:
            lens_local = s
    sensor_s = sensor_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]
    lens_s = lens_local.moved(bd.Location((tb_cx, tb_cy, tb_cz))).solids()[0]

    tb_sensor = AnimPart(plotter, solid_to_polydata(sensor_s, tol=0.05), MAT_SENSOR_IC, "PMW3360")
    tb_lens = AnimPart(plotter, solid_to_polydata(lens_s, tol=0.05), MAT_LENS_CLEAR, "LM19_Lens")
    tb_cup = AnimPart(plotter, solid_to_polydata(cup_s, tol=0.05, ang_tol=0.14), MAT_CUP_BLACK, "Trackball_Cup")
    tb_ball = AnimPart(plotter, solid_to_polydata(ball_s, tol=0.03, ang_tol=0.10), MAT_BALL_PEARL, "Trackball_25mm")

    ceramic_balls = []
    for idx, (cb_s, cb_ofs) in enumerate(build_ceramic_ball_solids(tb_cx, tb_cy, tb_cz)):
        ceramic_balls.append(
            (AnimPart(plotter, solid_to_polydata(cb_s, tol=0.03, ang_tol=0.12), MAT_CERAMIC_WHITE, f"Ceramic_{idx}"), cb_ofs)
        )

    # 4. Inertia Wheel Sub-Assembly Parts (in Wheel Local `(u, v, w)` frame!)
    whl_s = build_steel_flywheel_local()
    hld_s = build_magnet_holder_local()
    rck_s = build_wheel_rocker_local()
    crd_s = build_wheel_cradle_local()
    mov_hw, stat_ins = build_hardware_parts_local()
    brg_w_s, brg_e_s, mag_d4_s, mag_det_s, ins_det_s, scr_det_s = mov_hw
    ins_wc1_s, ins_wc2_s = stat_ins

    wheel_parts = {
        "flywheel": AnimPart(plotter, solid_to_polydata(whl_s, tol=0.035, ang_tol=0.12), MAT_STEEL_WHEEL, "Steel_Flywheel"),
        "brg_w": AnimPart(plotter, solid_to_polydata(brg_w_s, tol=0.04), MAT_BEARING_STEEL, "Brg_W"),
        "brg_e": AnimPart(plotter, solid_to_polydata(brg_e_s, tol=0.04), MAT_BEARING_STEEL, "Brg_E"),
        "holder": AnimPart(plotter, solid_to_polydata(hld_s, tol=0.04), MAT_WHEEL_RESIN_BLACK, "Magnet_Holder"),
        "mag_d4": AnimPart(plotter, solid_to_polydata(mag_d4_s, tol=0.04), MAT_MAGNET_NI, "Mag_D4"),
        "rocker": AnimPart(plotter, solid_to_polydata(rck_s, tol=0.045), MAT_WHEEL_RESIN_BLACK, "Wheel_Rocker"),
        "cradle": AnimPart(plotter, solid_to_polydata(crd_s, tol=0.045), MAT_CRADLE_BLACK, "Wheel_Cradle"),
        "ins_wc1": AnimPart(plotter, solid_to_polydata(ins_wc1_s, tol=0.04), MAT_BRASS, "Ins_WC1"),
        "ins_wc2": AnimPart(plotter, solid_to_polydata(ins_wc2_s, tol=0.04), MAT_BRASS, "Ins_WC2"),
        "ins_det": AnimPart(plotter, solid_to_polydata(ins_det_s, tol=0.04), MAT_BRASS, "Ins_Det"),
        "scr_det": AnimPart(plotter, solid_to_polydata(scr_det_s, tol=0.04), MAT_SCREW_STEEL, "Scr_Det"),
        "mag_det": AnimPart(plotter, solid_to_polydata(mag_det_s, tol=0.04), MAT_MAGNET_NI, "Mag_Det"),
    }

    # 2x WC1/WC2 top-down screws (in Global STEP frame)
    wc_screws = []
    for idx, (px, py) in enumerate((WC1_PCB, WC2_PCB), 1):
        sx, sy = to_step_right(px, py)
        _, scr_s = make_insert_and_screw(sx, sy, -5.81, -4.19, f"WC{idx}")
        wc_screws.append(AnimPart(plotter, solid_to_polydata(scr_s, tol=0.05), MAT_SCREW_STEEL, f"Screw_WC{idx}"))

    # 5. Case Heat-Set Inserts (16x) & Screws (12x Valley + 4x TB)
    case_inserts_l = []
    valley_screws_l = []
    for tag, px, py, z_ins, z_scr in LEFT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_left(px, py)
        ins_s, scr_s = make_insert_and_screw(sx, sy, z_ins, z_scr, tag)
        case_inserts_l.append(AnimPart(plotter, solid_to_polydata(ins_s, tol=0.05), MAT_BRASS, f"Ins_{tag}"))
        valley_screws_l.append(AnimPart(plotter, solid_to_polydata(scr_s, tol=0.05), MAT_SCREW_STEEL, f"Scr_{tag}"))

    case_inserts_r = []
    valley_screws_r = []
    for tag, px, py, z_ins, z_scr in RIGHT_PERIMETER_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins_s, scr_s = make_insert_and_screw(sx, sy, z_ins, z_scr, tag)
        case_inserts_r.append(AnimPart(plotter, solid_to_polydata(ins_s, tol=0.05), MAT_BRASS, f"Ins_{tag}"))
        valley_screws_r.append(AnimPart(plotter, solid_to_polydata(scr_s, tol=0.05), MAT_SCREW_STEEL, f"Scr_{tag}"))

    tb_inserts_r = []
    tb_screws_r = []
    for tag, px, py, z_ins in RIGHT_TB_HOLES_PCB:
        sx, sy = to_step_right(px, py)
        ins_s, scr_s = make_insert_and_screw(sx, sy, z_ins, -13.99, tag)
        tb_inserts_r.append(AnimPart(plotter, solid_to_polydata(ins_s, tol=0.05), MAT_BRASS, f"Ins_{tag}"))
        tb_screws_r.append(AnimPart(plotter, solid_to_polydata(scr_s, tol=0.05), MAT_SCREW_STEEL, f"Scr_{tag}"))

    # 6. Top Plates
    left_plate_s = build_top_plate_solid(is_right=False)
    right_plate_s = build_top_plate_solid(is_right=True)
    left_plate = AnimPart(plotter, solid_to_polydata(left_plate_s, tol=0.06), MAT_PLATE_BLACK, "Left_Plate")
    right_plate = AnimPart(plotter, solid_to_polydata(right_plate_s, tol=0.06), MAT_PLATE_BLACK, "Right_Plate")

    # 7. 40x Switches & 40x White Keycaps (instancing canonical meshes via 4x4 matrices!)
    sw_body_mesh, sw_stem_mesh = build_visual_choc_v2_meshes()
    cap_mesh = build_visual_keycap_mesh()

    # Order switches from inner columns outward for a pleasing symmetric ripple wave
    left_sw_items = []
    for kx, ky in LEFT_SWITCHES:
        sx, sy = to_step_left(kx, ky)
        left_sw_items.append(
            (
                sx,
                sy,
                AnimPart(plotter, sw_body_mesh.copy(), MAT_SWITCH_BODY),
                AnimPart(plotter, sw_stem_mesh.copy(), MAT_SWITCH_STEM),
                AnimPart(plotter, cap_mesh.copy(), MAT_KEYCAP_WHITE),
            )
        )
    left_sw_items.sort(key=lambda item: (abs(item[0]), -item[1]))

    right_sw_items = []
    for kx, ky in RIGHT_SWITCHES:
        sx, sy = to_step_right(kx, ky)
        right_sw_items.append(
            (
                sx,
                sy,
                AnimPart(plotter, sw_body_mesh.copy(), MAT_SWITCH_BODY),
                AnimPart(plotter, sw_stem_mesh.copy(), MAT_SWITCH_STEM),
                AnimPart(plotter, cap_mesh.copy(), MAT_KEYCAP_WHITE),
            )
        )
    right_sw_items.sort(key=lambda item: (abs(item[0]), -item[1]))

    print(f"  Scene built in {time.perf_counter() - t0:.1f}s.")
    return {
        "floor_actor": floor_actor,
        "left_case": left_case,
        "right_case": right_case,
        "left_pcb_parts": left_pcb_parts,
        "right_pcb_parts": right_pcb_parts,
        "sensor_pcb_parts": sensor_pcb_parts,
        "j1_plug": j1_plug,
        "tb_sensor": tb_sensor,
        "tb_lens": tb_lens,
        "tb_cup": tb_cup,
        "tb_ball": tb_ball,
        "ceramic_balls": ceramic_balls,
        "wheel_parts": wheel_parts,
        "wc_screws": wc_screws,
        "case_inserts_l": case_inserts_l,
        "valley_screws_l": valley_screws_l,
        "case_inserts_r": case_inserts_r,
        "valley_screws_r": valley_screws_r,
        "tb_inserts_r": tb_inserts_r,
        "tb_screws_r": tb_screws_r,
        "left_plate": left_plate,
        "right_plate": right_plate,
        "left_sw_items": left_sw_items,
        "right_sw_items": right_sw_items,
    }


# ---------------------------------------------------------------------------
# Timeline & Per-Frame Kinematics (Total Duration = 26.5s)
# ---------------------------------------------------------------------------
TOTAL_DURATION = 26.5

STAGE_CAPTIONS = [
    (0.0, 4.3, "STEP 1 / 6", "トラックボールユニットの組み立て", "TBセンサー基板 + PMW3360 + LM19レンズ + カップ + セラミック支持球"),
    (4.3, 9.7, "STEP 2 / 6", "パッシブ磁気慣性ホイールの組み立て", "45#鋼一体軸ホイール + ベアリング + 磁石ホルダー + Cクリップ連結ロッカー/クレードル"),
    (9.7, 13.8, "STEP 3 / 6", "ボトムケース準備 ＆ トラックボール組み込み", "100%密閉ボトムケース（白） + 真鍮インサート圧入 + TB1〜TB4 ネジ固定"),
    (13.8, 18.2, "STEP 4 / 6", "慣性ホイール ＆ メインPCB（黒）の締結", "右メインPCB裏へホイール固定（WC1/WC2） → ケース着地 ＆ キー谷間12箇所ネジ固定"),
    (18.2, 23.6, "STEP 5 / 6", "トッププレート・スイッチ・キーキャップ・25mm球装着", "FR-4トッププレート（黒） + Choc V2 スイッチ40個 + 白キーキャップ40個 + 25mmボール"),
    (23.6, 26.6, "COMPLETE", "curcur40 完成（prototype/passive-inertia-wheel）", "25mmトラックボール + アンダープレート一体軸パッシブ磁気慣性ホイール"),
]


def get_desk_point_r(x_step: float, y_step: float, z_step: float) -> np.ndarray:
    v = M_DESK_R @ np.array([x_step, y_step, z_step, 1.0], dtype=np.float64)
    return v[:3]


def evaluate_camera(t: float) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Smooth keyframed camera `(position, focal_point)` across all 6 stages."""
    tb_focus_sub = get_desk_point_r(23.8125, -109.5375, -5.0 + 26.0)
    whl_focus_sub = get_desk_point_r(X_AXLE_STEP - 2.5, Y_AXLE_STEP - 3.5, Z_AXLE_STEP - 3.0 + 26.0)
    full_focus = np.array([0.0, -76.0, 12.0], dtype=np.float64)
    right_focus = np.array([22.0, -80.0, 13.0], dtype=np.float64)

    # Keyframes: (t_start, pos, focal)
    if t < 4.0:
        # Stage 1: Close-up orbiting gently around Trackball Sub-Assembly
        ang = math.radians(-32.0 + 22.0 * (t / 4.0))
        dist, elev = 92.0, 40.0
        pos = tb_focus_sub + np.array([dist * math.sin(ang), -dist * math.cos(ang), elev])
        return tuple(pos), tuple(tb_focus_sub)

    if t < 4.7:
        # Smooth camera glide from Trackball close-up to Inertia Wheel close-up
        u = ease_in_out_cubic(progress(t, 4.0, 4.7))
        ang1 = math.radians(-10.0)
        pos1 = tb_focus_sub + np.array([92.0 * math.sin(ang1), -92.0 * math.cos(ang1), 40.0])
        ang2 = math.radians(-38.0)
        pos2 = whl_focus_sub + np.array([92.0 * math.sin(ang2), -92.0 * math.cos(ang2), 38.0])
        pos = (1.0 - u) * pos1 + u * pos2
        foc = (1.0 - u) * tb_focus_sub + u * whl_focus_sub
        return tuple(pos), tuple(foc)

    if t < 9.4:
        # Stage 2: Close-up orbiting around Inertia Wheel Sub-Assembly
        ang = math.radians(-38.0 + 54.0 * progress(t, 4.7, 9.4))
        dist, elev = 92.0, 38.0
        pos = whl_focus_sub + np.array([dist * math.sin(ang), -dist * math.cos(ang), elev])
        return tuple(pos), tuple(whl_focus_sub)

    if t < 10.5:
        # Pull out to Full Split Keyboard view on Desk (wide enough to show both pinky edges with margin)
        u = ease_in_out_cubic(progress(t, 9.4, 10.5))
        ang1 = math.radians(16.0)
        pos1 = whl_focus_sub + np.array([92.0 * math.sin(ang1), -92.0 * math.cos(ang1), 38.0])
        pos2 = np.array([34.0, -430.0, 255.0], dtype=np.float64)
        pos = (1.0 - u) * pos1 + u * pos2
        foc = (1.0 - u) * whl_focus_sub + u * full_focus
        return tuple(pos), tuple(foc)

    if t < 13.8:
        # Stage 3: Full view with gentle drift toward Right Trackball area during TB mounting
        u = ease_in_out_cubic(progress(t, 10.5, 13.8))
        pos1 = np.array([34.0, -430.0, 255.0], dtype=np.float64)
        pos2 = np.array([56.0, -395.0, 236.0], dtype=np.float64)
        foc = (1.0 - 0.30 * u) * full_focus + (0.30 * u) * right_focus
        return tuple((1.0 - u) * pos1 + u * pos2), tuple(foc)

    if t < 18.2:
        # Stage 4: Wheel + Main PCBs descending onto both Left & Right Cases
        u = ease_in_out_cubic(progress(t, 13.8, 18.2))
        pos1 = np.array([56.0, -395.0, 236.0], dtype=np.float64)
        pos2 = np.array([-24.0, -435.0, 260.0], dtype=np.float64)
        foc1 = 0.70 * full_focus + 0.30 * right_focus
        foc = (1.0 - u) * foc1 + u * full_focus
        return tuple((1.0 - u) * pos1 + u * pos2), tuple(foc)

    if t < 23.6:
        # Stage 5: Plates + 40 Switches + 40 White Keycaps + 25mm Ball
        u = ease_in_out_cubic(progress(t, 18.2, 23.6))
        pos1 = np.array([-24.0, -435.0, 260.0], dtype=np.float64)
        pos2 = np.array([36.0, -418.0, 248.0], dtype=np.float64)
        return tuple((1.0 - u) * pos1 + u * pos2), tuple(full_focus)

    # Stage 6: Completed Hero Showcase Orbit (exact C0 match to pos2=(36, -418, 248) at u=0)
    u = ease_in_out_cubic(progress(t, 23.6, TOTAL_DURATION))
    ang0 = math.atan2(36.0, 342.0)
    rad0 = math.hypot(36.0, 342.0)
    ang = ang0 - math.radians(34.0) * math.sin(u * math.pi * 0.85)
    rad = rad0 - 14.0 * math.sin(u * math.pi * 0.5)
    dz = 236.0 - 22.0 * u
    pos = full_focus + np.array([rad * math.sin(ang), -rad * math.cos(ang), dz])
    return tuple(pos), tuple(full_focus)


def update_scene_at_time(scene: dict, t: float):
    # Smoothly fade in the desk contact shadow as the White Cases land in Stage 3
    if t < 9.75:
        scene["floor_actor"].SetVisibility(False)
    else:
        scene["floor_actor"].SetVisibility(True)
        scene["floor_actor"].prop.opacity = ease_out_cubic(progress(t, 9.75, 10.60))

    # -----------------------------------------------------------------------
    # 1. Trackball Sub-Assembly (Stage 1: 0..4.3s, Re-enters Stage 3: 11.1..13.6s)
    # -----------------------------------------------------------------------
    if t < 4.55:
        fade_out = 1.0 - ease_in_out_cubic(progress(t, 4.05, 4.50))
        m_tb_grp = M_DESK_R @ mat_translate(0.0, 0.0, 26.0)

        m_spcb_loc, a_spcb = drop_state(t, 0.05, 0.65, (0.0, 0.0, -8.0))
        for p in scene["sensor_pcb_parts"]:
            p.update(m_tb_grp @ m_spcb_loc, a_spcb * fade_out)

        m_sens_loc, a_sens = drop_state(t, 0.60, 0.80, (0.0, 0.0, -14.0), snap=True)
        scene["tb_sensor"].update(m_tb_grp @ m_sens_loc, a_sens * fade_out)

        m_lens_loc, a_lens = drop_state(t, 0.85, 0.80, (0.0, 0.0, 15.0), snap=True)
        scene["tb_lens"].update(m_tb_grp @ m_lens_loc, a_lens * fade_out)

        m_cup_loc, a_cup = drop_state(t, 1.55, 0.90, (0.0, 0.0, 24.0), snap=True)
        scene["tb_cup"].update(m_tb_grp @ m_cup_loc, a_cup * fade_out)

        for idx, (cb_part, cb_ofs) in enumerate(scene["ceramic_balls"]):
            m_cb_loc, a_cb = drop_state(t, 2.40 + idx * 0.16, 0.65, cb_ofs, snap=True)
            cb_part.update(m_tb_grp @ m_cb_loc, a_cb * fade_out)

        m_j1_loc, a_j1 = drop_state(t, 3.10, 0.65, (12.0, 0.0, 0.0), snap=True)
        scene["j1_plug"].update(m_tb_grp @ m_j1_loc, a_j1 * fade_out)
    elif t < 11.10:
        for p in scene["sensor_pcb_parts"]:
            p.update(M_DESK_R, 0.0)
        scene["tb_sensor"].update(M_DESK_R, 0.0)
        scene["tb_lens"].update(M_DESK_R, 0.0)
        scene["tb_cup"].update(M_DESK_R, 0.0)
        scene["j1_plug"].update(M_DESK_R, 0.0)
        for cb_part, _ in scene["ceramic_balls"]:
            cb_part.update(M_DESK_R, 0.0)
    else:
        # Stage 3+: Completed Trackball Unit lowers into Right Case lower pocket!
        m_tb_land, a_tb_land = drop_state(t, 11.10, 1.25, (0.0, 0.0, 34.0))
        m_tb_world = M_DESK_R @ m_tb_land
        for p in scene["sensor_pcb_parts"]:
            p.update(m_tb_world, a_tb_land)
        scene["tb_sensor"].update(m_tb_world, a_tb_land)
        scene["tb_lens"].update(m_tb_world, a_tb_land)
        scene["tb_cup"].update(m_tb_world, a_tb_land)
        scene["j1_plug"].update(m_tb_world, a_tb_land)
        for cb_part, _ in scene["ceramic_balls"]:
            cb_part.update(m_tb_world, a_tb_land)

    # TB1..TB4 Screws (12.35s .. 13.45s)
    for idx, scr in enumerate(scene["tb_screws_r"]):
        m_s, a_s = drop_state(t, 12.35 + idx * 0.12, 0.70, (0.0, 0.0, 26.0))
        scr.update(M_DESK_R @ m_s, a_s)

    # -----------------------------------------------------------------------
    # 2. Inertia Wheel Sub-Assembly (Stage 2: 4.3..9.7s, Re-enters Stage 4: 13.8s+)
    # -----------------------------------------------------------------------
    wp = scene["wheel_parts"]
    # Spin angle of rotor (#01 Steel Flywheel + #02 Magnet Holder + #08 D4 Magnet)
    spin_deg = 0.0
    if 8.55 <= t <= 9.65:
        spin_deg = 720.0 * ease_out_cubic(progress(t, 8.55, 9.65))
    elif t >= 23.60:
        spin_deg = 1080.0 * ease_out_cubic(progress(t, 23.60, TOTAL_DURATION))
    m_spin = mat_rot_x(spin_deg)

    # Subtle middle-click demo tap right at 8.15..8.55s
    click_deg = 0.0
    if 8.15 <= t <= 8.55:
        click_deg = 2.20 * math.sin(progress(t, 8.15, 8.55) * math.pi)
    m_seesaw = (
        mat_translate(U_PIV, 0.0, W_PIV)
        @ mat_rot_y(click_deg)
        @ mat_translate(-U_PIV, 0.0, -W_PIV)
    )

    if t < 4.25:
        for part in wp.values():
            part.update(M_DESK_R, 0.0)
    elif t < 9.95:
        fade_out_w = 1.0 - ease_in_out_cubic(progress(t, 9.45, 9.90))
        m_w_base = M_DESK_R @ mat_translate(0.0, 0.0, 26.0) @ M_WHEEL_TO_STEP

        # Rotor assembly first rises slightly during rocker insertion or drops cleanly into rocker
        # 4.30s: #01 Steel Flywheel appears
        m_fw, a_fw = drop_state(t, 4.30, 0.55, (0.0, 0.0, 8.0))
        # 4.85s: 2x DDL-520ZZ Bearings slide onto journals along ±u (X)
        m_bw, a_bw = drop_state(t, 4.85, 0.65, (-12.0, 0.0, 0.0), snap=True)
        m_be, a_be = drop_state(t, 4.85, 0.65, (12.0, 0.0, 0.0), snap=True)
        # 5.45s: #02 Magnet Holder + #08 D4x1mm Magnet slide onto West D-shaft
        m_hd, a_hd = drop_state(t, 5.45, 0.60, (-14.0, 0.0, 0.0), snap=True)
        m_md4, a_md4 = drop_state(t, 5.80, 0.55, (-16.0, 0.0, 0.0), snap=True)
        # 6.30s: #03 Seesaw Rocker rises up so bearings snap into C-clip seats
        m_rk, a_rk = drop_state(t, 6.30, 0.75, (0.0, 0.0, -18.0), snap=True)
        # 7.05s: #04 Cradle + WC1/WC2 Brass Inserts snap down onto Rocker trunnions
        m_cr, a_cr = drop_state(t, 7.05, 0.70, (0.0, 0.0, 16.0), snap=True)
        m_iwc1, a_iwc1 = drop_state(t, 6.95, 0.65, (0.0, 0.0, 22.0))
        m_iwc2, a_iwc2 = drop_state(t, 7.05, 0.65, (0.0, 0.0, 22.0))
        # 7.65s: South Detent Brass Insert + M2x6 Adjuster Screw + Ø2x2mm Magnet from South (-v)
        m_idet, a_idet = drop_state(t, 7.60, 0.50, (0.0, -12.0, 0.0))
        m_sdet, a_sdet = drop_state(t, 7.75, 0.55, (0.0, -16.0, 0.0))
        m_mdet, a_mdet = drop_state(t, 7.85, 0.55, (0.0, 8.0, 0.0), snap=True)

        wp["flywheel"].update(m_w_base @ m_seesaw @ m_fw @ m_spin, a_fw * fade_out_w)
        wp["brg_w"].update(m_w_base @ m_seesaw @ m_bw, a_bw * fade_out_w)
        wp["brg_e"].update(m_w_base @ m_seesaw @ m_be, a_be * fade_out_w)
        wp["holder"].update(m_w_base @ m_seesaw @ m_hd @ m_spin, a_hd * fade_out_w)
        wp["mag_d4"].update(m_w_base @ m_seesaw @ m_md4 @ m_spin, a_md4 * fade_out_w)
        wp["rocker"].update(m_w_base @ m_seesaw @ m_rk, a_rk * fade_out_w)
        wp["cradle"].update(m_w_base @ m_cr, a_cr * fade_out_w)
        wp["ins_wc1"].update(m_w_base @ m_iwc1, a_iwc1 * fade_out_w)
        wp["ins_wc2"].update(m_w_base @ m_iwc2, a_iwc2 * fade_out_w)
        wp["ins_det"].update(m_w_base @ m_seesaw @ m_idet, a_idet * fade_out_w)
        wp["scr_det"].update(m_w_base @ m_seesaw @ m_sdet, a_sdet * fade_out_w)
        wp["mag_det"].update(m_w_base @ m_seesaw @ m_mdet, a_mdet * fade_out_w)
    elif t < 13.80:
        for part in wp.values():
            part.update(M_DESK_R, 0.0)
    else:
        # Stage 4+: Assembled Inertia Wheel hovers at Z = +14 mm (13.8..15.3s) while Right Main PCB
        # mates on top of it and WC1/WC2 screws clamp it, then lowers together to Z = 0 (15.5..16.8s)!
        a_whl = clamp01(progress(t, 13.80, 14.25))
        if t < 14.50:
            z_whl = 26.0 - 12.0 * ease_out_cubic(progress(t, 13.80, 14.50))  # 26 -> 14 mm
        elif t < 15.55:
            z_whl = 14.0
        else:
            z_whl = 14.0 * (1.0 - ease_in_out_cubic(progress(t, 15.55, 16.75)))  # 14 -> 0 mm

        m_w_world = M_DESK_R @ mat_translate(0.0, 0.0, z_whl) @ M_WHEEL_TO_STEP
        for key, part in wp.items():
            if key in ("flywheel", "holder", "mag_d4"):
                part.update(m_w_world @ m_spin, a_whl)
            else:
                part.update(m_w_world, a_whl)

    # -----------------------------------------------------------------------
    # 3. White Cases & 16x Brass Heat-Set Inserts (Stage 3: 9.7s+)
    # -----------------------------------------------------------------------
    m_lc, a_lc = drop_state(t, 9.70, 0.85, (0.0, 0.0, -14.0))
    m_rc, a_rc = drop_state(t, 9.78, 0.85, (0.0, 0.0, -14.0))
    scene["left_case"].update(M_DESK_L @ m_lc, a_lc)
    scene["right_case"].update(M_DESK_R @ m_rc, a_rc)

    for idx, ins in enumerate(scene["case_inserts_l"]):
        m_i, a_i = drop_state(t, 10.35 + idx * 0.05, 0.55, (0.0, 0.0, 18.0))
        ins.update(M_DESK_L @ m_i, a_i)

    for idx, ins in enumerate(scene["case_inserts_r"] + scene["tb_inserts_r"]):
        m_i, a_i = drop_state(t, 10.35 + idx * 0.04, 0.55, (0.0, 0.0, 18.0))
        ins.update(M_DESK_R @ m_i, a_i)

    # -----------------------------------------------------------------------
    # 4. Left & Right Main PCBs + WC1/WC2 Screws + 12x Valley Screws (Stage 4: 14.1s+)
    # -----------------------------------------------------------------------
    if t < 14.15:
        for p in scene["left_pcb_parts"]:
            p.update(M_DESK_L, 0.0)
        for p in scene["right_pcb_parts"]:
            p.update(M_DESK_R, 0.0)
    else:
        a_pcb = clamp01(progress(t, 14.15, 14.60))
        if t < 14.95:
            # Descend from +30 mm to +14 mm (meeting the Inertia Wheel Unit cleanly!)
            z_pcb = 30.0 - 16.0 * ease_out_cubic(progress(t, 14.15, 14.95))
        elif t < 15.55:
            z_pcb = 14.0
        else:
            # Lower together with Inertia Wheel onto the White Cases (14 -> 0 mm)
            z_pcb = 14.0 * (1.0 - ease_in_out_cubic(progress(t, 15.55, 16.75)))

        m_lpcb = M_DESK_L @ mat_translate(0.0, 0.0, z_pcb)
        m_rpcb = M_DESK_R @ mat_translate(0.0, 0.0, z_pcb)
        for p in scene["left_pcb_parts"]:
            p.update(m_lpcb, a_pcb)
        for p in scene["right_pcb_parts"]:
            p.update(m_rpcb, a_pcb)

    # WC1 & WC2 Screws fasten Right Main PCB to Wheel Cradle at Z = +14 mm (14.90..15.50s), then move down together!
    for idx, wscr in enumerate(scene["wc_screws"]):
        t_ws = 14.90 + idx * 0.12
        if t < t_ws:
            wscr.update(M_DESK_R, 0.0)
        else:
            u_ws = progress(t, t_ws, t_ws + 0.55)
            a_ws = clamp01(u_ws / 0.30)
            extra_z = 16.0 * (1.0 - ease_out_cubic(u_ws))
            base_z = 14.0 if t < 15.55 else 14.0 * (1.0 - ease_in_out_cubic(progress(t, 15.55, 16.75)))
            wscr.update(M_DESK_R @ mat_translate(0.0, 0.0, base_z + extra_z), a_ws)

    # 12x Key-Valley M2x6 Screws (L1..L6 & R1..R6: 16.75..18.05s)
    for idx, scr in enumerate(scene["valley_screws_l"]):
        m_s, a_s = drop_state(t, 16.75 + idx * 0.09, 0.65, (0.0, 0.0, 22.0))
        scr.update(M_DESK_L @ m_s, a_s)
    for idx, scr in enumerate(scene["valley_screws_r"]):
        m_s, a_s = drop_state(t, 16.75 + idx * 0.09, 0.65, (0.0, 0.0, 22.0))
        scr.update(M_DESK_R @ m_s, a_s)

    # -----------------------------------------------------------------------
    # 5. Black Top Plates + 40x Switches + 40x White Keycaps + 25mm Ball (Stage 5: 18.2s+)
    # -----------------------------------------------------------------------
    m_lp, a_lp = drop_state(t, 18.20, 0.95, (0.0, 0.0, 26.0))
    m_rp, a_rp = drop_state(t, 18.30, 0.95, (0.0, 0.0, 26.0))
    scene["left_plate"].update(M_DESK_L @ m_lp, a_lp)
    scene["right_plate"].update(M_DESK_R @ m_rp, a_rp)

    # 40x Switches ripple in (19.25..21.05s), followed by 40x White Keycaps (20.85..22.65s)
    n_l = len(scene["left_sw_items"])
    for idx, (sx, sy, sw_b, sw_st, cap) in enumerate(scene["left_sw_items"]):
        m_pos = mat_translate(sx, sy, 0.0)
        t_sw = 19.25 + (idx / max(n_l - 1, 1)) * 1.15
        m_sw_z, a_sw = drop_state(t, t_sw, 0.55, (0.0, 0.0, 20.0), snap=True)
        m_sw_w = M_DESK_L @ m_sw_z @ m_pos
        sw_b.update(m_sw_w, a_sw)
        sw_st.update(m_sw_w, a_sw)

        t_cp = 20.85 + (idx / max(n_l - 1, 1)) * 1.15
        m_cp_z, a_cp = drop_state(t, t_cp, 0.55, (0.0, 0.0, 22.0), snap=True)
        cap.update(M_DESK_L @ m_cp_z @ m_pos, a_cp)

    n_r = len(scene["right_sw_items"])
    for idx, (sx, sy, sw_b, sw_st, cap) in enumerate(scene["right_sw_items"]):
        m_pos = mat_translate(sx, sy, 0.0)
        t_sw = 19.25 + (idx / max(n_r - 1, 1)) * 1.15
        m_sw_z, a_sw = drop_state(t, t_sw, 0.55, (0.0, 0.0, 20.0), snap=True)
        m_sw_w = M_DESK_R @ m_sw_z @ m_pos
        sw_b.update(m_sw_w, a_sw)
        sw_st.update(m_sw_w, a_sw)

        t_cp = 20.85 + (idx / max(n_r - 1, 1)) * 1.15
        m_cp_z, a_cp = drop_state(t, t_cp, 0.55, (0.0, 0.0, 22.0), snap=True)
        cap.update(M_DESK_R @ m_cp_z @ m_pos, a_cp)

    # 25mm Glossy Pearl-Silver Trackball Sphere drops in last (22.45..23.45s)
    m_ball, a_ball = drop_state(t, 22.45, 0.90, (0.0, 0.0, 32.0), snap=True)
    scene["tb_ball"].update(M_DESK_R @ m_ball, a_ball)


# ---------------------------------------------------------------------------
# Crisp 2x-Supersampled HUD Caption Overlay (Pillow)
# ---------------------------------------------------------------------------
def _load_jp_font(size_px: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    win_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = (
        ["meiryob.ttc", "YuGothB.ttc", "msgothic.ttc", "arialbd.ttf"]
        if bold
        else ["meiryo.ttc", "YuGothM.ttc", "msgothic.ttc", "arial.ttf"]
    )
    for name in candidates:
        fp = win_fonts / name
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size_px)
            except Exception:
                continue
    return ImageFont.load_default()


class HudOverlayRenderer:
    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        scale = width / 1920.0
        self.f_badge = _load_jp_font(max(14, int(round(19 * scale))), bold=True)
        self.f_title = _load_jp_font(max(18, int(round(27 * scale))), bold=True)
        self.f_sub = _load_jp_font(max(13, int(round(17 * scale))), bold=False)
        self.f_brand = _load_jp_font(max(13, int(round(17 * scale))), bold=True)
        self._cache: dict[str, Image.Image] = {}

    def _get_card(self, step_tag: str, title: str, subtitle: str) -> Image.Image:
        key = f"{step_tag}|{title}|{subtitle}"
        if key in self._cache:
            return self._cache[key]

        scale = self.w / 1920.0
        pad_x = int(round(28 * scale))
        card = Image.new("RGBA", (self.w, int(round(140 * scale))), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)

        # Measure text
        b_box = d.textbbox((0, 0), step_tag, font=self.f_badge)
        t_box = d.textbbox((0, 0), title, font=self.f_title)
        s_box = d.textbbox((0, 0), subtitle, font=self.f_sub)

        pill_w = (b_box[2] - b_box[0]) + int(round(24 * scale))
        pill_h = int(round(32 * scale))
        row1_w = pill_w + int(round(14 * scale)) + (t_box[2] - t_box[0])
        box_w = max(row1_w, s_box[2] - s_box[0]) + int(round(44 * scale))
        box_h = int(round(92 * scale))

        x0, y0 = pad_x, int(round(24 * scale))
        d.rounded_rectangle(
            [x0, y0, x0 + box_w, y0 + box_h],
            radius=int(round(14 * scale)),
            fill=(18, 22, 29, 208),
            outline=(255, 255, 255, 42),
            width=1,
        )

        is_done = step_tag == "COMPLETE"
        pill_fill = (42, 157, 112, 245) if is_done else (59, 130, 246, 240)
        px0, py0 = x0 + int(round(18 * scale)), y0 + int(round(15 * scale))
        d.rounded_rectangle(
            [px0, py0, px0 + pill_w, py0 + pill_h],
            radius=int(round(8 * scale)),
            fill=pill_fill,
        )
        d.text(
            (px0 + int(round(12 * scale)), py0 + int(round(4 * scale)) - b_box[1]),
            step_tag,
            font=self.f_badge,
            fill=(255, 255, 255, 255),
        )
        d.text(
            (px0 + pill_w + int(round(14 * scale)), y0 + int(round(14 * scale)) - t_box[1]),
            title,
            font=self.f_title,
            fill=(248, 250, 252, 255),
        )
        d.text(
            (px0, y0 + int(round(56 * scale)) - s_box[1]),
            subtitle,
            font=self.f_sub,
            fill=(192, 202, 216, 245),
        )

        # Subtle top-right watermark pill
        brand_txt = "curcur40  •  passive-inertia-wheel"
        br_box = d.textbbox((0, 0), brand_txt, font=self.f_brand)
        bw = (br_box[2] - br_box[0]) + int(round(28 * scale))
        bh = int(round(36 * scale))
        bx0 = self.w - pad_x - bw
        by0 = y0
        d.rounded_rectangle(
            [bx0, by0, bx0 + bw, by0 + bh],
            radius=int(round(10 * scale)),
            fill=(18, 22, 29, 165),
        )
        d.text(
            (bx0 + int(round(14 * scale)), by0 + int(round(8 * scale)) - br_box[1]),
            brand_txt,
            font=self.f_brand,
            fill=(226, 232, 240, 235),
        )

        self._cache[key] = card
        return card

    def apply(self, frame_rgb: np.ndarray, t: float) -> np.ndarray:
        step_tag, title, sub = STAGE_CAPTIONS[-1][2], STAGE_CAPTIONS[-1][3], STAGE_CAPTIONS[-1][4]
        for t0, t1, st, ti, su in STAGE_CAPTIONS:
            if t0 <= t < t1:
                step_tag, title, sub = st, ti, su
                break

        card = self._get_card(step_tag, title, sub)
        base = Image.fromarray(frame_rgb, mode="RGB").convert("RGBA")
        base.alpha_composite(card, (0, 0))

        # Bottom timeline progress bar (4px)
        bar_h = max(3, int(round(4 * self.w / 1920.0)))
        prog_w = int(round(self.w * clamp01(t / TOTAL_DURATION)))
        d = ImageDraw.Draw(base)
        d.rectangle([0, self.h - bar_h, self.w, self.h], fill=(20, 24, 32, 95))
        if prog_w > 0:
            d.rectangle([0, self.h - bar_h, prog_w, self.h], fill=(59, 130, 246, 235))

        return np.asarray(base.convert("RGB"), dtype=np.uint8)


# ---------------------------------------------------------------------------
# Main Plotter & Video Encoder Pipeline
# ---------------------------------------------------------------------------
def create_plotter(width: int, height: int) -> pv.Plotter:
    pv.OFF_SCREEN = True
    pl = pv.Plotter(off_screen=True, window_size=(width, height), lighting="none")
    pl.set_background("#D4DCE6", top="#EEF2F7")

    env_tex = build_studio_env_texture()
    pl.set_environment_texture(env_tex, is_srgb=True)

    # Three-point studio directional lights for crisp diffuse/specular form definition
    key_light = pv.Light(
        position=(-160.0, -340.0, 420.0),
        focal_point=(0.0, -78.0, 0.0),
        color="#FFFDF9",
        intensity=0.85,
        positional=False,
    )
    fill_light = pv.Light(
        position=(260.0, -220.0, 240.0),
        focal_point=(0.0, -78.0, 0.0),
        color="#E8F1FF",
        intensity=0.45,
        positional=False,
    )
    rim_light = pv.Light(
        position=(60.0, 240.0, 300.0),
        focal_point=(0.0, -78.0, 0.0),
        color="#FFFFFF",
        intensity=0.55,
        positional=False,
    )
    pl.add_light(key_light)
    pl.add_light(fill_light)
    pl.add_light(rim_light)

    pl.enable_ssao(radius=7.5, bias=0.04, kernel_size=128, blur=True)
    pl.enable_anti_aliasing("msaa", multi_samples=8)
    pl.camera.up = (0.0, 0.0, 1.0)
    pl.camera.view_angle = 28.0
    return pl


def render_preview_keyframes(preview_dir: Path, width: int, height: int):
    preview_dir.mkdir(parents=True, exist_ok=True)
    pl = create_plotter(width, height)
    scene = build_scene(pl)
    hud = HudOverlayRenderer(width, height)

    sample_times = [
        (3.85, "01_trackball_subassembly.png"),
        (8.90, "02_inertia_wheel_subassembly.png"),
        (13.20, "03_cases_and_trackball_mounted.png"),
        (15.20, "04_wheel_and_pcb_mating.png"),
        (20.40, "05_plates_and_switches_wave.png"),
        (25.80, "06_completed_curcur40.png"),
    ]
    print(f"[2/3] Rendering {len(sample_times)} preview keyframes to {preview_dir} ...")
    for t_sec, fname in sample_times:
        update_scene_at_time(scene, t_sec)
        cpos, cfoc = evaluate_camera(t_sec)
        pl.camera.position = cpos
        pl.camera.focal_point = cfoc
        pl.camera.up = (0.0, 0.0, 1.0)
        pl.reset_camera_clipping_range()
        pl.render()
        img = pl.screenshot(return_img=True)
        out_img = hud.apply(img, t_sec)
        Image.fromarray(out_img).save(preview_dir / fname)
        print(f"  Saved {fname} (t={t_sec:.2f}s)")
    pl.close()


def render_full_video(out_mp4: Path, width: int, height: int, fps: int):
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    pl = create_plotter(width, height)
    scene = build_scene(pl)
    hud = HudOverlayRenderer(width, height)

    n_frames = int(round(TOTAL_DURATION * fps))
    print(f"[2/3] Rendering {n_frames} frames ({TOTAL_DURATION:.1f}s @ {fps}fps, {width}x{height}) -> {out_mp4} ...")

    writer = imageio_ffmpeg.write_frames(
        str(out_mp4),
        size=(width, height),
        fps=fps,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        macro_block_size=8,
        quality=None,
        output_params=["-crf", "18", "-preset", "medium", "-movflags", "+faststart"],
    )
    writer.send(None)

    t_render_start = time.perf_counter()
    try:
        for frame_idx in range(n_frames):
            t_sec = frame_idx / float(fps)
            update_scene_at_time(scene, t_sec)
            cpos, cfoc = evaluate_camera(t_sec)
            pl.camera.position = cpos
            pl.camera.focal_point = cfoc
            pl.camera.up = (0.0, 0.0, 1.0)
            pl.reset_camera_clipping_range()
            pl.render()

            raw_rgb = pl.screenshot(return_img=True)
            composited = hud.apply(raw_rgb, t_sec)
            writer.send(np.ascontiguousarray(composited))

            if (frame_idx + 1) % (fps * 3) == 0 or frame_idx + 1 == n_frames:
                elapsed = time.perf_counter() - t_render_start
                rate = (frame_idx + 1) / max(elapsed, 1e-6)
                eta = (n_frames - (frame_idx + 1)) / max(rate, 1e-6)
                print(
                    f"  Frame {frame_idx + 1:4d}/{n_frames} ({100.0 * (frame_idx + 1) / n_frames:5.1f}%) "
                    f"| {rate:.1f} fps | ETA {eta:.1f}s"
                )
    finally:
        writer.close()
        pl.close()

    size_mb = out_mp4.stat().st_size / (1024.0 * 1024.0)
    print(f"[3/4] Successfully wrote {out_mp4} ({size_mb:.2f} MB)!")


def export_inline_webp(
    src_mp4: Path,
    out_webp: Path,
    width: int = 960,
    fps: int = 20,
    quality: int = 75,
):
    assert src_mp4.exists(), f"Source MP4 not found: {src_mp4}"
    out_webp.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    vf = f"fps={fps},scale={width}:-1:flags=lanczos"
    print(f"[4/4] Encoding inline animated WebP ({width}w @ {fps}fps, q={quality}) -> {out_webp} ...")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(src_mp4),
        "-vf",
        vf,
        "-c:v",
        "libwebp_anim",
        "-lossless",
        "0",
        "-compression_level",
        "4",
        "-q:v",
        str(quality),
        "-loop",
        "0",
        "-an",
        str(out_webp),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    webp_mb = out_webp.stat().st_size / (1024.0 * 1024.0)
    print(f"      Successfully wrote {out_webp} ({webp_mb:.2f} MB)!")


def main():
    parser = argparse.ArgumentParser(description="Render curcur40 3D PBR assembly animation video.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT_MP4, help="Output MP4 file path")
    parser.add_argument("--webp-output", type=Path, default=DEFAULT_OUT_WEBP, help="Output animated WebP file path")
    parser.add_argument("--webp-only", action="store_true", help="Convert existing MP4 to animated WebP without re-rendering 3D")
    parser.add_argument("--width", type=int, default=1920, help="Video width in pixels (even)")
    parser.add_argument("--height", type=int, default=1080, help="Video height in pixels (even)")
    parser.add_argument("--fps", type=int, default=60, help="Frames per second")
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Optional directory to output 6 keyframe PNGs instead of full MP4",
    )
    args = parser.parse_args()

    if args.preview_dir is not None:
        render_preview_keyframes(args.preview_dir, args.width, args.height)
    elif args.webp_only:
        export_inline_webp(args.output, args.webp_output)
    else:
        render_full_video(args.output, args.width, args.height, args.fps)
        export_inline_webp(args.output, args.webp_output)


if __name__ == "__main__":
    main()
