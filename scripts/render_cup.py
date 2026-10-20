# -*- coding: utf-8 -*-
"""
Render trackball-cup.stl and trackball-cup-with-ball.stl to high-resolution PNGs.
"""
import shutil
from pathlib import Path
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

WORKSPACE = Path(r"c:\Users\oktnt\workspace\curcur40")
CASES_DIR = WORKSPACE / "cases" / "curcur40"
DOCS_ASSETS = WORKSPACE / "docs" / "curcur40" / "assets"
DOCS_ASSETS.mkdir(parents=True, exist_ok=True)
BRAIN_DIR = Path(r"C:\Users\oktnt\.gemini\antigravity\brain\86c4b6c7-3e68-48fa-956a-9d1b47163c48")

def render_mesh(stl_path: Path, out_png: Path, title: str, has_ball: bool = False):
    mesh = trimesh.load(str(stl_path))
    
    fig = plt.figure(figsize=(10, 8), dpi=150)
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=28, azim=-55)
    
    # Light direction
    light_dir = np.array([0.5, -0.7, 1.0])
    light_dir /= np.linalg.norm(light_dir)

    # Downsample if too many faces for fast matplotlib rendering
    triangles = mesh.triangles
    normals = mesh.face_normals
    if len(triangles) > 30000:
        step = len(triangles) // 25000 + 1
        triangles = triangles[::step]
        normals = normals[::step]
    intensity = np.clip(np.dot(normals, light_dir), 0.2, 1.0)
    
    n_tri = len(triangles)
    if has_ball:
        # Differentiate ball vs cup: ball faces are spherical near (0, 0, 18.30)
        face_centers = triangles.mean(axis=1)
        dist_from_ball = np.linalg.norm(face_centers - np.array([0, 0, 18.30]), axis=1)
        is_ball = np.abs(dist_from_ball - 12.50) < 0.25
        
        face_colors = np.zeros((n_tri, 4))
        # Cup: slate blue
        cup_base = np.array([0.22, 0.45, 0.65])
        # Ball: glossy ruby red
        ball_base = np.array([0.85, 0.18, 0.22])
        
        for i in range(n_tri):
            base = ball_base if is_ball[i] else cup_base
            face_colors[i, :3] = base * intensity[i]
            face_colors[i, 3] = 0.95 if is_ball[i] else 1.0
    else:
        base_color = np.array([0.22, 0.48, 0.72])
        face_colors = np.zeros((n_tri, 4))
        for i in range(n_tri):
            face_colors[i, :3] = base_color * intensity[i]
            face_colors[i, 3] = 1.0

    poly = Poly3DCollection(triangles, facecolors=face_colors, edgecolor='none', linewidths=0.1)
    ax.add_collection3d(poly)
    
    # Bounds
    bounds = mesh.bounds
    max_range = np.array([bounds[1, 0] - bounds[0, 0],
                          bounds[1, 1] - bounds[0, 1],
                          bounds[1, 2] - bounds[0, 2]]).max() / 2.0
    mid_x = (bounds[1, 0] + bounds[0, 0]) * 0.5
    mid_y = (bounds[1, 1] + bounds[0, 1]) * 0.5
    mid_z = (bounds[1, 2] + bounds[0, 2]) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(0, mid_z + max_range)
    
    ax.set_axis_off()
    fig.patch.set_facecolor('#181a1f')
    ax.set_facecolor('#181a1f')
    
    plt.title(title, color='#e0e6ed', fontsize=14, pad=12, fontweight='bold', family='sans-serif')
    plt.tight_layout()
    plt.savefig(str(out_png), dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Saved render to {out_png}")

if __name__ == "__main__":
    cup_stl = CASES_DIR / "trackball-cup.stl"
    cup_with_ball_stl = CASES_DIR / "trackball-cup-with-ball.stl"
    
    # 1. Cup alone
    cup_png = DOCS_ASSETS / "trackball_cup_render.png"
    render_mesh(cup_stl, cup_png, "curcur40 Trackball Cup (Section 4 Parametric CAD)", has_ball=False)
    if BRAIN_DIR.exists():
        shutil.copy2(cup_png, BRAIN_DIR / "trackball_cup_generated_render.png")
        
    # 2. Cup with Ball
    cup_ball_png = DOCS_ASSETS / "trackball_cup_with_ball_render.png"
    render_mesh(cup_with_ball_stl, cup_ball_png, "curcur40 Trackball Cup with 25mm Ball Assembly (Non-Contact Seated)", has_ball=True)
    if BRAIN_DIR.exists():
        shutil.copy2(cup_ball_png, BRAIN_DIR / "trackball_cup_with_ball_render.png")
