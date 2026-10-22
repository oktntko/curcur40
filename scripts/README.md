# `scripts/` — curcur40 公式ジェネレータ・出力スクリプト集

本ディレクトリには、**curcur40** の 3D CAD モデル（STEP / STL）、FR-4 トッププレート基板（`.kicad_pcb` / `.svg`）、JLCPCB 発注用製造データ（`GERBER` / `BOM` / `CPL`）、およびドキュメント用図版・3Dプレビュー画像を再現可能に生成・更新する公式スクリプトのみを格納します。

---

## 1. ディレクトリ格納・運用ルール

1. **恒久スクリプトのみを `scripts/` に格納する**:
   - 設計仕様書（[`docs/curcur40/case_spec.md`](../docs/curcur40/case_spec.md), [`docs/curcur40/pcb_spec.md`](../docs/curcur40/pcb_spec.md)）のパラメータ変更時に再実行するジェネレータ・エクスポータのみを本ディレクトリで管理します。
2. **一時ファイル・使い捨てスクリプトを残さない**:
   - 1回限りの調査スクリプトや DRC/ERC の一時レポートファイル（`.rpt`, `.net`, `.bak`, `.kicad_prl`）、および作業用の `scratch/`・`tmp/` ディレクトリは、作業完了時に削除しリポジトリ内に残しません（スクリプト内で DRC 検証等を行う場合は Python 標準の `tempfile.TemporaryDirectory` を使用します）。
3. **出力先ディレクトリ**:
   - **3D CAD (STEP / STL)**: [`cases/curcur40/`](../cases/curcur40/)
   - **トッププレート PCB / SVG**: [`plates/curcur40/pcb/`](../plates/curcur40/pcb/), [`plates/curcur40/svg/`](../plates/curcur40/svg/)
   - **JLCPCB 発注用データ**:
     - 左メイン基板: [`pcbs/curcur40/left/jlcpcb/production_files/`](../pcbs/curcur40/left/jlcpcb/production_files/)
     - 右メイン基板: [`pcbs/curcur40/right/jlcpcb/production_files/`](../pcbs/curcur40/right/jlcpcb/production_files/)
     - トッププレート: [`plates/curcur40/pcb/jlcpcb/production_files/`](../plates/curcur40/pcb/jlcpcb/production_files/)
   - **ドキュメント・プレビュー画像**: [`docs/curcur40/`](../docs/curcur40/), [`docs/curcur40/assets/`](../docs/curcur40/assets/)

---

## 2. スクリプト一覧と実行方法

### ① 3D CAD 生成スクリプト（`cadgen` / `build123d` 環境で実行）
```powershell
$CADGEN_PY = "$env:USERPROFILE\.local\bin\uvx.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_cases.py`](./generate_cases.py)** | 左右の3Dプリント用トレイ型ボトムケース（`cases/curcur40/left.step`, `left.stl`, `right.step`, `right.stl`）を生成します。 |
| **[`generate_trackball_cup.py`](./generate_trackball_cup.py)** | 25mm トラックボールカップ（`trackball-cup.step`, `trackball-cup.stl`）および 25mm 球＋光学距離基準点（`Lens_Optical_Ref_Point`, $Z_{\text{rel}} = +3.40\text{ mm}$）付きアセンブリ（`trackball-cup-with-ball.step`, `trackball-cup-with-ball.stl`）を生成します。 |
| **[`generate_sensor_assemblies.py`](./generate_sensor_assemblies.py)** | PMW3360DM-T2QU + LM19-LSI レンズ + PCB の光学アセンブリ（`pmw3360-lens-pcb-assembly.step`）およびカップ＋ボール統合検証モデル（`trackball-sensor-assembly.step`）を生成します（両モデルとも `Lens_Optical_Ref_Point` を収録）。 |
| **[`generate_full_assembly.py`](./generate_full_assembly.py)** | 左右ケース・左右メイン基板・左右トッププレート・トラックボールカップ・25mm球・センサー・レンズ・`Lens_Optical_Ref_Point`・CKW12・M2スペーサー13本・M2ネジ26本・キーキャップ40個を統合したフルアセンブリ（`assembly-full.step`）を生成し、全パーツ間の干渉体積ゼロ（`0.00000000 mm³`）を検証します。 |

### ② KiCad 基板・プレート・JLCPCB 発注データ・図版スクリプト（KiCad 10.0 Python で実行）
```powershell
$KICAD_PY = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_plates.py`](./generate_plates.py)** | 左右 FR-4 トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成し、DRC を検証します。 |
| **[`export_jlcpcb.py`](./export_jlcpcb.py)** | 左右メイン基板（`curcur40-left`, `curcur40-right`）の Gerber ZIP・BOM CSV・CPL CSV、および左右トッププレートの Gerber ZIP を一括出力します。 |
| **[`generate_spec_diagrams.py`](./generate_spec_diagrams.py)** | `docs/curcur40/assets/` 配下のスタックアップ断面図・トラックボールカップ詳細図面等の解説図版 PNG を生成します。 |
| **[`render_previews.py`](./render_previews.py)** | `docs/curcur40/assets/render_*.png`（フルアセンブリ・左右メイン基板・左右トッププレートの3Dレンダリング画像）を一括更新します。 |
