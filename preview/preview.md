# curcur40 3D完成イメージ & プレビューガイド

設計完了した **curcur40** のフルアセンブリ（3Dプリントケース＋スイッチプレート＋Kailh Choc v1 キーキャップ40個＋CKW12水平ロータリーエンコーダ＋25mmトラックボール）および各基板の3Dレンダリング画像です。

---

## 1. フルアセンブリ完成イメージ（ケース＋プレート＋キー＋エンコーダ＋25mmトラックボール）

![curcur40 フルアセンブリ 3Dアイソメトリックビュー](./render_full_assembly_iso.png)

![curcur40 フルアセンブリ 上面ビュー](./render_full_assembly_top.png)

- **左手側（21キー）**: 3×5 メインキー ＋ 内側2キー（`EXSW1`, `EXSW2`）＋ 下段親指4キー（`SW9`, `SW8`, `SW1`, `EXSW3`）
- **右手側（19キー ＋ エンコーダ ＋ 25mmトラックボール）**:
  - 内側上段（`rEXSW1`）: **CKW12 水平ローラーエンコーダ**（水色ホイール）
  - 内側中段（`rEXSW2`）: 1u Choc キー
  - 親指内側: **25mm トラックボール**（赤色球体 ＋ ベアリング保持カップ）
  - 親指下段3キー: `rSW1`, `rSW8`, `rSW9`

---

## 2. メインPCB & PMW3360基板（KiCad 3Dレイトレーシング）

![左手メインPCB 3D斜視図](./render_left_iso.png)
![右手メインPCB 3D斜視図](./render_right_iso.png)
![左手メインPCB 表面 (F.Cu)](./render_left_top.png)
![左手メインPCB 裏面実装面 (B.Cu)](./render_left_bottom.png)
![右手メインPCB 表面 (F.Cu)](./render_right_top.png)
![右手メインPCB 裏面実装面 (B.Cu)](./render_right_bottom.png)
![PMW3360 トラックボールセンサー基板](./render_pmw3360_top.png)

---

## 3. スイッチプレート（FR-4 1.6mm トッププレート）

![左手トッププレート](./render_plate_left.png)
![右手トッププレート（CKW12切り欠き＆トラックボールU字逃がし付き）](./render_plate_right.png)

---

## 4. 手元のツールでインタラクティブに3D確認する方法

### 方法A：KiCad の「3D ビューアー」で見る（基板・実装部品・プレート）
1. **KiCad 10.0** で以下の `.kicad_pcb` ファイルを開きます：
   - 左手メイン基板: [curcur40-left.kicad_pcb](../pcbs/curcur40/left/curcur40-left.kicad_pcb)
   - 右手メイン基板: [curcur40-right.kicad_pcb](../pcbs/curcur40/right/curcur40-right.kicad_pcb)
   - PMW3360センサー基板: [curcur40-pmw3360.kicad_pcb](../pcbs/curcur40/pmw3360/curcur40-pmw3360.kicad_pcb)
   - トッププレート（左／右）: [plate-top-left.kicad_pcb](../plates/curcur40/pcb/plate-top-left.kicad_pcb) / [plate-top-right.kicad_pcb](../plates/curcur40/pcb/plate-top-right.kicad_pcb)
   - ボトムプレート（左／右）: [plate-bottom-left.kicad_pcb](../plates/curcur40/pcb/plate-bottom-left.kicad_pcb) / [plate-bottom-right.kicad_pcb](../plates/curcur40/pcb/plate-bottom-right.kicad_pcb)
2. メニューの **「表示 (View)」→「3D ビューアー (3D Viewer)」**（ショートカット: **`Alt + 3`**）を押すと、マウスドラッグで自由に360°回転・ズームして確認できます。

### 方法B：3D CAD / スライサーソフトで完成品アセンブリやケースを見る
3Dプリント用ケースと、キーキャップ・エンコーダ・25mmトラックボールを組み合わせたフルアセンブリの3Dモデルも出力済みです：
- **フルアセンブリ（左右ケース＋プレート＋全キー＋エンコーダ＋25mmトラックボール）**:
  - [assembly-full.step](../cases/curcur40/assembly-full.step)
- **単体3Dモデル（STEP / STL）**:
  - 左ケース: [left.step](../cases/curcur40/left.step) / [left.stl](../cases/curcur40/left.stl)
  - 右ケース: [right.step](../cases/curcur40/right.step) / [right.stl](../cases/curcur40/right.stl)
  - トラックボール保持カップ: [trackball-cup.step](../cases/curcur40/trackball-cup.step) / [trackball-cup.stl](../cases/curcur40/trackball-cup.stl)

これらは **FreeCAD**、**Fusion 360**、3Dプリンタ用スライサー（**Bambu Studio** / **PrusaSlicer** / **Cura**）、またはブラウザの [3dviewer.net](https://3dviewer.net/) などにドラッグ＆ドロップするだけでインタラクティブに回転・断面確認ができます。
