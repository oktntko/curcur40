# `scripts/` — curcur40 公式ジェネレータ・出力スクリプト集

本ディレクトリには、**curcur40** の 3D CAD モデル（STEP / STL）、FR-4 トッププレート基板（`.kicad_pcb` / `.svg`）、JLCPCB 発注用製造データ（`GERBER` / `BOM` / `CPL`）、およびドキュメント用図版・3Dプレビュー画像を再現可能に生成・更新する公式スクリプトのみを格納します。

---

## 1. ディレクトリ格納・運用ルール

1. **恒久スクリプトのみを `scripts/` に格納する**:
   - 設計仕様書（[`docs/case_spec.md`](../docs/case_spec.md), [`docs/pcb_spec.md`](../docs/pcb_spec.md)）のパラメータ変更時に再実行するジェネレータ・エクスポータのみを本ディレクトリで管理します。
2. **一時ファイル・使い捨てスクリプトを残さない**:
   - 1回限りの調査スクリプトや DRC/ERC の一時レポートファイル（`.rpt`, `.net`, `.bak`, `.kicad_prl`）、および作業用の `scratch/`・`tmp/` ディレクトリは、作業完了時に削除しリポジトリ内に残しません（スクリプト内で DRC 検証等を行う場合は Python 標準の `tempfile.TemporaryDirectory` を使用します）。
3. **環境非依存の相対パス記述（フルパス直書きの禁止）**:
   - スクリプト内のワークスペースパスや入出力先パスには `c:\Users\...` 等の環境依存フルパスをハードコードせず、必ずスクリプト自身の位置からの相対解決（`WORKSPACE = Path(__file__).resolve().parent.parent`）を起点として記述します（カレントディレクトリに依存せずどこからでも実行可能）。
4. **出力先ディレクトリ**:
   - **3Dプリント単体部品 (STEP / STL)**: [`cases/`](../cases/) 直下
   - **検証・確認用アセンブリモデル (STEP / STL)**: [`cases/assemblies/`](../cases/assemblies/)
   - **トッププレート PCB / SVG**: [`plates/pcb/`](../plates/pcb/), [`plates/svg/`](../plates/svg/)
   - **JLCPCB 発注用データ**:
     - 左メイン基板: [`pcbs/left/jlcpcb/production_files/`](../pcbs/left/jlcpcb/production_files/)
     - 右メイン基板: [`pcbs/right/jlcpcb/production_files/`](../pcbs/right/jlcpcb/production_files/)
     - センサーサブ基板: [`pcbs/pmw3360/jlcpcb/production_files/`](../pcbs/pmw3360/jlcpcb/production_files/)
     - トッププレート: [`plates/pcb/jlcpcb/production_files/`](../plates/pcb/jlcpcb/production_files/)
   - **ドキュメント・プレビュー画像**: [`docs/`](../docs/), [`docs/assets/`](../docs/assets/)

---

## 2. スクリプト一覧と実行方法

### ① 3D CAD 生成スクリプト（`cadgen` / `build123d` 環境で実行）
```powershell
$CADGEN_PY = "$env:USERPROFILE\.local\bin\uvx.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_cases.py`](./generate_cases.py)** | 左右の3Dプリント用トレイ型ボトムケース（トッププレート水平基準 `cases/left.step`, `left.stl`, `right.step`, `right.stl` およびデスク水平基準 `left-desk.step`, `left-desk.stl`, `right-desk.step`, `right-desk.stl`）を生成し、極小隙間・0.80mm未満薄肉検証（確定除外箇所を除く違反0件）を実行します。 |
| **[`generate_trackball_cup.py`](./generate_trackball_cup.py)** | 25mm トラックボールカップ（`cases/trackball-cup.step`, `trackball-cup.stl`）および 25mm 球＋光学距離基準点（`Lens_Optical_Ref_Point`, $Z_{\text{rel}} = +3.40\text{ mm}$）付き検証アセンブリ（`cases/assemblies/trackball-cup-with-ball.step`, `trackball-cup-with-ball.stl`）を生成し、極小隙間・0.80mm未満薄肉検証を実行します。 |
| **[`generate_sensor_assemblies.py`](./generate_sensor_assemblies.py)** | PMW3360DM-T2QU + LM19-LSI レンズ + PCB の光学アセンブリ（`cases/assemblies/pmw3360-lens-pcb-assembly.step`）およびカップ＋ボール統合検証モデル（`cases/assemblies/trackball-sensor-assembly.step`）を生成します（両モデルとも `Lens_Optical_Ref_Point` を収録）。 |
| **[`generate_full_assembly.py`](./generate_full_assembly.py)** | 左右ケース・左右メイン基板・センサーサブ基板・左右トッププレート・トラックボールカップ・25mm球・センサー・レンズ・`Lens_Optical_Ref_Point`・CKW12・デュアルUSB-C（PC用＆左右間用）・M2 5.50mmスペーサー14本・M2×4mmネジ28本・キーキャップ40個を統合したフルアセンブリ（`cases/assemblies/assembly-full.step`, `assembly-full-desk.step`、全107パーツ）を生成し、①全パーツ間の干渉体積ゼロ（`0.00000000 mm³`）、②非接触パーツ間の最小クリアランス（極小隙間ゼロ）、③3Dプリント部品の0.80mm未満肉厚・微小隙間チェック（確定除外箇所を除く違反0件）を一括検証します。 |

### ② KiCad 基板・プレート・JLCPCB 発注データ・図版スクリプト（KiCad 10.0 Python で実行）
```powershell
$KICAD_PY = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_plates.py`](./generate_plates.py)** | 左右 FR-4 トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成し、DRC を検証します。 |
| **[`export_jlcpcb.py`](./export_jlcpcb.py)** | 全3基板（`curcur40-left`, `curcur40-right`, `curcur40-pmw3360`）の Gerber ZIP・BOM CSV・CPL CSV、および左右トッププレートの Gerber ZIP を一括出力し、JLCPCB 公式製造ルール（DRC/ERC、基板サイズ、最小配線幅 $\ge 0.127\text{ mm}$、最小ビア $\ge 0.45/0.30\text{ mm}$、PTH/NPTH穴径、BOM/CPL/LCSC整合性）を発注前自動チェックします。 |
| **[`generate_spec_diagrams.py`](./generate_spec_diagrams.py)** | `docs/assets/` 配下のスタックアップ断面図・トラックボールカップ詳細図面等の解説図版 PNG を生成します。 |
| **[`render_previews.py`](./render_previews.py)** | `docs/assets/render_*.png`（フルアセンブリ・全3基板・左右トッププレートの3Dレンダリング画像）を一括更新します。 |
