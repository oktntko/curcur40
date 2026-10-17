# -*- coding: utf-8 -*-
"""
Update curcur40 full assembly (cases/curcur40/assembly-full.step)
and generate rendered preview images.
Incorporates:
- New right case (right.step) with +2.0mm shift, L-shaped TRRS opening, no double wall, solid screw bosses
- New trackball cup (trackball-cup.step) placed at (23.8125, -109.5375, 10.60)
- 25mm trackball sphere at (23.8125, -109.5375, 10.60)
- Left case, top plates, keycaps, CKW12 encoder
"""
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
ARTIFACTS_DIR = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\dab819aa-2c9f-4dd2-be5e-39a298725eca")

sys.path.insert(0, str(ARTIFACTS_DIR / "scratch"))

from OCP.gp import gp_Pnt, gp_Dir, gp_Vec, gp_Ax1, gp_Ax2, gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.TopoDS import TopoDS_Compound, TopoDS_Builder
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopLoc import TopLoc_Location
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

import build_cases

# Switches and mounting holes definitions (self-contained, no pcbnew dependency)
LEFT_MOUNTING_HOLES = [
    (-100.0000, -22.5000, 1.1),
    ( -23.8125, -22.5000, 1.1),
    ( -98.0000,  38.0000, 1.1),
    ( -23.8125,  64.0000, 1.1),
]

RIGHT_MOUNTING_HOLES = [
    (100.0000, -22.5000, 1.1),
    ( 23.8125, -22.5000, 1.1),
    ( 98.0000,  38.0000, 1.1),
]

LEFT_SWITCHES = [
    (-109.5375, -7.14375),
    (-109.5375, 11.90625),
    (-109.5375, 30.95625),
    (-90.4875, -11.90625),
    (-90.4875, 7.14375),
    (-90.4875, 26.19375),
    (-71.4375, -14.28750),
    (-71.4375, 4.76250),
    (-71.4375, 23.81250),
    (-52.3875, -11.90625),
    (-52.3875, 7.14375),
    (-52.3875, 26.19375),
    (-33.3375, -9.52500),
    (-33.3375, 9.52500),
    (-33.3375, 28.57500),
    (-14.2875, 0.00000),
    (-14.2875, 19.05000),
    (-71.4375, 52.38750),
    (-52.3875, 52.38750),
    (-33.3375, 52.38750),
    (-14.2875, 52.38750),
]

RIGHT_SWITCHES = [
    (109.5375, -7.14375),
    (109.5375, 11.90625),
    (109.5375, 30.95625),
    (90.4875, -11.90625),
    (90.4875, 7.14375),
    (90.4875, 26.19375),
    (71.4375, -14.28750),
    (71.4375, 4.76250),
    (71.4375, 23.81250),
    (52.3875, -11.90625),
    (52.3875, 7.14375),
    (52.3875, 26.19375),
    (33.3375, -9.52500),
    (33.3375, 9.52500),
    (33.3375, 28.57500),
    (14.2875, 19.05000),
    (33.3375, 52.38750),
    (52.3875, 52.38750),
    (71.4375, 52.38750),
]

RIGHT_ENCODER = (14.2875, 0.00000)

def get_left_plate_outer_pts():
    # Left Plate Plan B (smooth un-notched rectangle with pinky step)
    return [
        (   5.6625, -24.71250, 1.0),
        (-119.4625, -24.71250, 1.0),
        (-119.4625,  41.38125, 1.0),
        ( -82.8625,  41.38125, 1.0),
        ( -82.8625,  67.90000, 1.0),
        (   5.6625,  67.90000, 1.0),
    ]

def get_right_plate_outer_pts():
    # Right Plate Plan B with trackball bay (no TRRS notch)
    return [
        ( -5.6625, -24.71250, 1.0),
        (119.4625, -24.71250, 1.0),
        (119.4625,  41.38125, 1.0),
        ( 82.8625,  41.38125, 1.0),
        ( 82.8625,  67.90000, 1.0),
        ( 24.8375,  67.90000, 1.0),
        ( 24.8375,  37.40000, 1.0),
        ( -5.6625,  37.40000, 1.0),
    ]

def load_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone or reader.TransferRoots() == 0:
        raise RuntimeError(f"Could not read STEP: {path}")
    return reader.OneShape()

def translate_shape(shape, dx, dy, dz):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()

def make_keycap_shape(cx, cy):
    cap_pts = [
        (cx - 8.6, cy - 8.1, 1.5),
        (cx + 8.6, cy - 8.1, 1.5),
        (cx + 8.6, cy + 8.1, 1.5),
        (cx - 8.6, cy + 8.1, 1.5),
    ]
    return build_cases.make_extruded_polygon(cap_pts, 1.2, 5.6)

def build_plate_with_cutouts(outer_pts, switch_centers, mounting_holes, x_offset, encoder=False):
    plate = build_cases.make_extruded_polygon(outer_pts, -1.9, -0.3)
    tools = TopoDS_Compound()
    tools_builder = TopoDS_Builder()
    tools_builder.MakeCompound(tools)

    def to_step(x, y):
        return x + x_offset, -(y + 57.1500)

    def add_rounded_cutout(cx, cy, width, height, radius):
        x, y = to_step(cx, cy)
        points = [
            (x - width / 2, y - height / 2, radius),
            (x + width / 2, y - height / 2, radius),
            (x + width / 2, y + height / 2, radius),
            (x - width / 2, y + height / 2, radius),
        ]
        tools_builder.Add(
            tools, build_cases.make_extruded_polygon(points, -2.0, 0.0)
        )

    for cx, cy in switch_centers:
        add_rounded_cutout(cx, cy, 14.0, 14.0, 0.5)
    if encoder:
        add_rounded_cutout(*RIGHT_ENCODER, 18.2, 18.2, 0.5)

    for cx, cy, radius in mounting_holes:
        x, y = to_step(cx, cy)
        tool = BRepPrimAPI_MakeCylinder(
            gp_Ax2(gp_Pnt(x, y, -2.0), gp_Dir(0, 0, 1)), radius, 2.0
        ).Shape()
        tools_builder.Add(tools, tool)

    cut = BRepAlgoAPI_Cut(plate, tools)
    cut.Build()
    if not cut.IsDone():
        raise RuntimeError("Failed to cut the top-plate openings from the assembly model.")
    return cut.Shape()

def make_ckw12_shape(cx, cy):
    trsf_rot = gp_Trsf()
    trsf_rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), -math.pi / 2.0)

    r_h = STEPControl_Reader()
    r_h.ReadFile(r"c:\Users\oktnt\workspace\curcur40\pcbs\common\kbd\3dmodels\ckw12_housing.stp")
    r_h.TransferRoots()
    housing_rot = BRepBuilderAPI_Transform(r_h.OneShape(), trsf_rot, True).Shape()
    housing = translate_shape(housing_rot, cx, cy, -5.0)

    r_w = STEPControl_Reader()
    r_w.ReadFile(r"c:\Users\oktnt\workspace\curcur40\pcbs\common\kbd\3dmodels\ckw12_wheel.stp")
    r_w.TransferRoots()
    wheel_rot = BRepBuilderAPI_Transform(r_w.OneShape(), trsf_rot, True).Shape()
    wheel = translate_shape(wheel_rot, cx, cy, -5.0)

    r_s = STEPControl_Reader()
    r_s.ReadFile(r"c:\Users\oktnt\workspace\curcur40\pcbs\common\kbd\3dmodels\ckw12_stem.stp")
    r_s.TransferRoots()
    stem_rot = BRepBuilderAPI_Transform(r_s.OneShape(), trsf_rot, True).Shape()
    stem = translate_shape(stem_rot, cx, cy, -5.0)

    return housing, wheel, stem

from OCP.TopoDS import TopoDS_Compound, TopoDS_Builder, TopoDS

# ... in extract_triangles:
def extract_triangles(shape, color_rgb):
    BRepMesh_IncrementalMesh(shape, 0.15, False, 0.3, True)
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    loc = TopLoc_Location()
    triangles = []
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        facing = face.Orientation()
        triangulation = BRep_Tool.Triangulation_s(face, loc)
        if triangulation is not None:
            trsf = loc.Transformation()
            nodes = [triangulation.Node(i) for i in range(1, triangulation.NbNodes() + 1)]
            trans_nodes = []
            for n in nodes:
                p = n.Transformed(trsf)
                trans_nodes.append((p.X(), p.Y(), p.Z()))
            for i in range(1, triangulation.NbTriangles() + 1):
                tri = triangulation.Triangle(i)
                i1, i2, i3 = tri.Get()
                p1, p2, p3 = trans_nodes[i1 - 1], trans_nodes[i2 - 1], trans_nodes[i3 - 1]
                if facing != 0:
                    triangles.append((p1, p3, p2, color_rgb))
                else:
                    triangles.append((p1, p2, p3, color_rgb))
        exp.Next()
    return triangles

def subdivide_large_triangles(v0, v1, v2, colors, max_edge=3.5, passes=6):
    for _ in range(passes):
        d01 = np.linalg.norm(v1 - v0, axis=1)
        d12 = np.linalg.norm(v2 - v1, axis=1)
        d20 = np.linalg.norm(v0 - v2, axis=1)
        max_lens = np.maximum(d01, np.maximum(d12, d20))
        split_mask = max_lens > max_edge
        if not np.any(split_mask):
            break
        keep_v0, keep_v1, keep_v2 = v0[~split_mask], v1[~split_mask], v2[~split_mask]
        keep_c = colors[~split_mask]

        sv0, sv1, sv2 = v0[split_mask], v1[split_mask], v2[split_mask]
        sc = colors[split_mask]
        s01, s12, s20 = d01[split_mask], d12[split_mask], d20[split_mask]

        c01 = (s01 >= s12) & (s01 >= s20)
        c12 = (~c01) & (s12 >= s20)
        c20 = (~c01) & (~c12)

        m01 = (sv0 + sv1) * 0.5
        m12 = (sv1 + sv2) * 0.5
        m20 = (sv2 + sv0) * 0.5

        new_v0, new_v1, new_v2, new_c = [], [], [], []
        if np.any(c01):
            new_v0.extend([sv0[c01], m01[c01]])
            new_v1.extend([m01[c01], sv1[c01]])
            new_v2.extend([sv2[c01], sv2[c01]])
            new_c.extend([sc[c01], sc[c01]])
        if np.any(c12):
            new_v0.extend([sv0[c12], sv0[c12]])
            new_v1.extend([sv1[c12], m12[c12]])
            new_v2.extend([m12[c12], sv2[c12]])
            new_c.extend([sc[c12], sc[c12]])
        if np.any(c20):
            new_v0.extend([sv0[c20], m20[c20]])
            new_v1.extend([sv1[c20], sv1[c20]])
            new_v2.extend([m20[c20], sv2[c20]])
            new_c.extend([sc[c20], sc[c20]])

        v0 = np.vstack([keep_v0] + new_v0)
        v1 = np.vstack([keep_v1] + new_v1)
        v2 = np.vstack([keep_v2] + new_v2)
        colors = np.vstack([keep_c] + new_c)
    return v0, v1, v2, colors

def render_scene(all_tris, out_png, width=1280, height=720, pitch_deg=34.0, yaw_deg=-10.0, roll_deg=0.0):
    v0 = np.array([t[0] for t in all_tris], dtype=np.float64)
    v1 = np.array([t[1] for t in all_tris], dtype=np.float64)
    v2 = np.array([t[2] for t in all_tris], dtype=np.float64)
    base_colors = np.array([t[3] for t in all_tris], dtype=np.float64)

    v0, v1, v2, base_colors = subdivide_large_triangles(v0, v1, v2, base_colors, max_edge=3.5, passes=6)

    all_pts = np.vstack([v0, v1, v2])
    center = (all_pts.min(axis=0) + all_pts.max(axis=0)) * 0.5
    v0 -= center
    v1 -= center
    v2 -= center

    e1 = v1 - v0
    e2 = v2 - v0
    normals = np.cross(e1, e2)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    valid = (norms[:, 0] > 1e-9)
    v0, v1, v2, base_colors, normals, norms = (
        v0[valid], v1[valid], v2[valid], base_colors[valid], normals[valid], norms[valid]
    )
    normals = normals / norms

    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)

    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]], dtype=np.float64)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float64)
    R = Rx @ Rz

    rv0 = v0 @ R.T
    rv1 = v1 @ R.T
    rv2 = v2 @ R.T
    rn = normals @ R.T

    light1 = np.array([-0.35, 0.45, 0.82])
    light1 /= np.linalg.norm(light1)
    light2 = np.array([0.40, -0.30, 0.86])
    light2 /= np.linalg.norm(light2)

    ndotl1 = np.abs(rn @ light1)
    ndotl2 = np.abs(rn @ light2)
    shade = 0.28 + 0.52 * ndotl1 + 0.25 * ndotl2
    spec = np.power(np.clip(ndotl1, 0, 1), 16) * 28.0
    shaded_colors = np.clip(base_colors * shade[:, None] + spec[:, None], 0, 255).astype(np.uint8)

    avg_z = (rv0[:, 2] + rv1[:, 2] + rv2[:, 2]) / 3.0
    order = np.argsort(avg_z)
    rv0, rv1, rv2, shaded_colors = rv0[order], rv1[order], rv2[order], shaded_colors[order]

    ss = 2
    W, H = width * ss, height * ss
    pts_2d = np.vstack([rv0[:, :2], rv1[:, :2], rv2[:, :2]])
    min_xy = pts_2d.min(axis=0)
    max_xy = pts_2d.max(axis=0)
    span_x, span_y = max_xy[0] - min_xy[0], max_xy[1] - min_xy[1]
    scale = min((W * 0.88) / span_x, (H * 0.86) / span_y)
    mid_x, mid_y = (min_xy[0] + max_xy[0]) * 0.5, (min_xy[1] + max_xy[1]) * 0.5

    def to_px(pts):
        px = (pts[:, 0] - mid_x) * scale + W * 0.5
        py = H * 0.5 - (pts[:, 1] - mid_y) * scale
        return np.column_stack([px, py])

    p0 = to_px(rv0)
    p1 = to_px(rv1)
    p2 = to_px(rv2)

    img = Image.new("RGB", (W, H), (24, 26, 32))
    draw = ImageDraw.Draw(img)

    for i in range(len(p0)):
        c = tuple(int(x) for x in shaded_colors[i])
        poly = [(float(p0[i, 0]), float(p0[i, 1])), (float(p1[i, 0]), float(p1[i, 1])), (float(p2[i, 0]), float(p2[i, 1]))]
        draw.polygon(poly, fill=c)

    img_final = img.resize((width, height), Image.Resampling.LANCZOS)
    img_final.save(out_png)
    print("Saved rendered preview:", out_png)

def main():
    print("Loading cases and parts...")
    left_case = load_step(CASES_DIR / "left.step")
    right_case = load_step(CASES_DIR / "right.step")
    tb_cup_raw = load_step(CASES_DIR / "trackball-cup.step")

    # Plates
    left_plate_pts = [(x - 14.2875, -(y + 57.1500), r) for (x, y, r) in reversed(get_left_plate_outer_pts())]
    left_plate = build_plate_with_cutouts(
        left_plate_pts,
        LEFT_SWITCHES,
        LEFT_MOUNTING_HOLES,
        x_offset=-14.2875,
    )

    right_plate_pts = [(x + 14.2875, -(y + 57.1500), r) for (x, y, r) in reversed(get_right_plate_outer_pts())]
    right_holes = RIGHT_MOUNTING_HOLES
    right_plate = build_plate_with_cutouts(
        right_plate_pts,
        RIGHT_SWITCHES,
        right_holes,
        x_offset=14.2875,
        encoder=True,
    )

    # Trackball Cup placed at new center (23.8125, -109.5375, 10.60)
    # Cup local z_bottom is -14.0. Right Main PCB F.Cu is at Z = -3.40.
    # dz = -3.40 - (-14.0) = +10.60
    tb_cx, tb_cy, tb_cz = 23.8125, -109.5375, 10.60
    tb_cup = translate_shape(tb_cup_raw, tb_cx, tb_cy, tb_cz)
    tb_ball = BRepPrimAPI_MakeSphere(gp_Pnt(tb_cx, tb_cy, tb_cz), 12.50).Shape()

    # Keycaps & CKW12
    keycaps = []
    for (kx, ky) in LEFT_SWITCHES:
        keycaps.append(make_keycap_shape(kx - 14.2875, -(ky + 57.1500)))
    for (kx, ky) in RIGHT_SWITCHES:
        keycaps.append(make_keycap_shape(kx + 14.2875, -(ky + 57.1500)))

    enc_x, enc_y = RIGHT_ENCODER[0] + 14.2875, -(RIGHT_ENCODER[1] + 57.1500)
    ckw_housing, ckw_wheel, ckw_stem = make_ckw12_shape(enc_x, enc_y)

    print("Building assembly compound...")
    assembly = TopoDS_Compound()
    builder = TopoDS_Builder()
    builder.MakeCompound(assembly)
    for s in [left_case, right_case, left_plate, right_plate, tb_cup, tb_ball, ckw_housing, ckw_wheel, ckw_stem] + keycaps:
        builder.Add(assembly, s)

    print("Writing cases/curcur40/assembly-full.step...")
    writer = STEPControl_Writer()
    writer.Transfer(assembly, STEPControl_AsIs)
    writer.Write(str(CASES_DIR / "assembly-full.step"))
    print("STEP export complete.")

    print("Extracting triangles for rendering...")
    tris = []
    tris.extend(extract_triangles(left_case, (55, 62, 74)))
    tris.extend(extract_triangles(right_case, (55, 62, 74)))
    tris.extend(extract_triangles(left_plate, (35, 38, 44)))
    tris.extend(extract_triangles(right_plate, (35, 38, 44)))
    for kc in keycaps:
        tris.extend(extract_triangles(kc, (215, 220, 228)))
    tris.extend(extract_triangles(ckw_housing, (45, 50, 58)))
    tris.extend(extract_triangles(ckw_stem, (235, 235, 240)))
    tris.extend(extract_triangles(ckw_wheel, (64, 190, 215)))
    tris.extend(extract_triangles(tb_cup, (45, 50, 58)))
    tris.extend(extract_triangles(tb_ball, (210, 48, 52)))

    print("Rendering ISO view...")
    render_scene(tris, str(ARTIFACTS_DIR / "final_assembly_iso.png"), pitch_deg=34.0, yaw_deg=-10.0)
    print("Rendering Top view...")
    render_scene(tris, str(ARTIFACTS_DIR / "final_assembly_top.png"), pitch_deg=0.0, yaw_deg=0.0)
    print("Rendering Bottom view...")
    render_scene(tris, str(ARTIFACTS_DIR / "final_assembly_bottom.png"), pitch_deg=180.0, yaw_deg=0.0)
    print("All renders completed successfully!")

if __name__ == "__main__":
    main()
