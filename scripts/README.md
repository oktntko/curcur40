# `scripts/` — curcur40 公式ジェネレータ・出力スクリプト集

本ディレクトリには、**curcur40** の 3D CAD モデル（STEP / STL）、FR-4 トッププレート基板（`.kicad_pcb` / `.svg`）、JLCPCB 発注用製造データ（`GERBER` / `BOM` / `CPL`）、およびドキュメント用図版・3Dプレビュー画像を再現可能に生成・更新する公式スクリプトのみを格納します。

---

## 1. ディレクトリ格納・運用ルール

1. **恒久スクリプトのみを `scripts/` に格納する**:
   - 設計仕様書（[`docs/case_spec.md`](../docs/case_spec.md), [`docs/pcb_spec.md`](../docs/pcb_spec.md), [`docs/passive_inertia_wheel_spec.md`](../docs/passive_inertia_wheel_spec.md), [`docs/parts_spec.md`](../docs/parts_spec.md)）のパラメータ変更時に再実行するジェネレータ・エクスポータのみを本ディレクトリで管理します。
2. **一時ファイル・使い捨てスクリプトを残さない**:
   - 1回限りの調査スクリプトや DRC/ERC の一時レポートファイル（`.rpt`, `.net`, `.bak`, `.kicad_prl`）、および作業用の `scratch/`・`tmp/` ディレクトリは、作業完了時に削除しリポジトリ内に残しません（スクリプト内で DRC 検証や一時レンダリングを行う場合は Python 標準の `tempfile.TemporaryDirectory` を使用します）。
3. **環境非依存の相対パス記述（フルパス直書きの禁止）**:
   - スクリプト内のワークスペースパスや入出力先パスには `c:\Users\...` 等の環境依存フルパスをハードコードせず、必ずスクリプト自身の位置からの相対解決（`WORKSPACE = Path(__file__).resolve().parent.parent`）を起点として記述します（カレントディレクトリに依存せずどこからでも実行可能）。
4. **出力先ディレクトリ**:
   - **ケース・カップ単体部品 (STEP / STL)**: [`cases/`](../cases/) 直下
   - **アンダープレート一体軸パッシブ磁気慣性ホイール単体部品 (STEP / STL)**: [`cases/inertia_wheel/`](../cases/inertia_wheel/)
   - **検証・確認用アセンブリモデル (STEP / STL)**: [`cases/assemblies/`](../cases/assemblies/)
   - **トッププレート PCB / SVG**: [`plates/pcb/`](../plates/pcb/), [`plates/svg/`](../plates/svg/)
   - **JLCPCB 発注用データ**:
     - 左メイン基板: [`pcbs/left/jlcpcb/production_files/`](../pcbs/left/jlcpcb/production_files/)
     - 右メイン基板: [`pcbs/right/jlcpcb/production_files/`](../pcbs/right/jlcpcb/production_files/)
     - TBセンサーサブ基板: [`pcbs/pmw3360/jlcpcb/production_files/`](../pcbs/pmw3360/jlcpcb/production_files/)
     - トッププレート: [`plates/pcb/jlcpcb/production_files/`](../plates/pcb/jlcpcb/production_files/)
   - **ドキュメント・プレビュー画像**: [`docs/`](../docs/), [`docs/assets/`](../docs/assets/)

---

## 2. スクリプト一覧と実行方法（全12本）

### ① 3D CAD 生成スクリプト（`cadgen` / `build123d` 環境で実行）
```powershell
$CADGEN_PY = "$env:USERPROFILE\.local\bin\uvx.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_cases.py`](./generate_cases.py)** | 左右の3Dプリント用 100% 密閉底面・真鍮ヒートセットインサート単段フラット円筒ボス（左右完全対称のキー谷間12箇所 `L1`〜`L6`/`R1`〜`R6` 均一 $\varnothing 5.20\text{ mm}$［天面 $Z = -5.80\text{ mm}$・片側肉厚 $1.175\text{ mm}$］＋ 右 `TB1`〜`TB4` $\varnothing 6.00\text{ mm}$［天面 $Z = -17.60\text{ mm}$］＋ USB-C ポート近傍の内壁一体基板受け棚 片側3箇所［天面 $Z = -5.80\text{ mm}$］＋ 右ケース `J1` ハウジング＆配線引き出し用 残肉厚 $1.40\text{ mm}$ 局所逃がしポケット）付きトレイ型ボトムケース（トッププレート水平基準 `cases/left.step`, `left.stl`, `right.step`, `right.stl` およびデスク水平基準 `left-desk.step`, `left-desk.stl`, `right-desk.step`, `right-desk.stl`）を生成し、JLC3DP 基本造形ルール・極小隙間・0.80mm未満薄肉検証（確定除外箇所を除く違反0件）を実行します。 |
| **[`generate_trackball_cup.py`](./generate_trackball_cup.py)** | 25mm トラックボールカップ（`cases/trackball-cup.step`, `trackball-cup.stl`、高さ $2.00\text{ mm}$ フラット固定耳・ストレート $\varnothing 2.40\text{ mm}$ 穴）および 25mm 球＋光学距離基準点（`Lens_Optical_Ref_Point`, $Z_{\text{rel}} = +3.40\text{ mm}$）付き検証アセンブリ（`cases/assemblies/trackball-cup-with-ball.step`, `trackball-cup-with-ball.stl`）を生成し、極小隙間・0.80mm未満薄肉検証を実行します。 |
| **[`generate_sensor_assemblies.py`](./generate_sensor_assemblies.py)** | PMW3360DM-T2QU + LM19-LSI レンズ + PCB の光学アセンブリ（`cases/assemblies/pmw3360-lens-pcb-assembly.step`）およびカップ＋ボール統合検証モデル（`cases/assemblies/trackball-sensor-assembly.step`）を生成します（両モデルとも `Lens_Optical_Ref_Point` を収録）。 |
| **[`generate_inertia_wheel.py`](./generate_inertia_wheel.py)** | アンダープレート 1ピース一体軸パッシブ磁気慣性ホイール実部品 4種（[`cases/inertia_wheel/`](../cases/inertia_wheel/) 配下の JLCCNC `45# Steel + 無電解Ni` 削り出し $\varnothing 22.0 \times 6.50\text{ mm}$ `steel-flywheel`、および JLC3DP MJF/SLS PA12 造形 `magnet-holder`, `wheel-rocker`, `wheel-cradle`［Cクリップスナップインヒンジ付］の STEP/STL）ならびに検証アセンブリ（`cases/assemblies/inertia-wheel-assembly.step`）を生成し、JLCCNC/JLC3DP 造形ルール・0.80mm未満薄肉完全ゼロ（除外0件）・静止姿勢（$0^\circ$）〜中クリック押下姿勢（$2.20^\circ$）の全パーツ間干渉ゼロ（`0.00000000 mm³`）・最小可動クリアランス・**6自由度（6-DOF）固定＆稼働拘束検証（`verify_6dof_constraints()`：基板未装着での `#03/#04` 一体保持含む）** を一括検証します。 |
| **[`generate_full_assembly.py`](./generate_full_assembly.py)** | `kicad-cli pcb export step --subst-models --no-dnp` により全3基板（`left`, `right`, `pmw3360`）と **全535個のKiCad実3D部品モデル** を直接出力・同期したうえで、嵌合する **JST `SHR-06V-S-B` ハウジング 2個**・左右ケース・左右トッププレート・Kailh Choc V2 スイッチ 40個・キーキャップ 40個・トラックボールカップ・25mm球・PMW3360・LM19レンズ・`Lens_Optical_Ref_Point`・アンダープレート一体軸慣性ホイール一式・`M2×L3.0×OD3.2mm` 真鍮ヒートセットインサート 19個・統一 `M2×6.0mm` ネジ 19本を統合したフルアセンブリ（`cases/assemblies/assembly-full.step`, `assembly-full-desk.step`、全674ソリッド）および右手ホイール検証モデル（`cases/assemblies/curcur40-right-wheel-assembly.step`、全349ソリッド）を生成し、①全パーツ間の干渉体積ゼロ（`0.00000000 mm³`）、②非接触パーツ間の最小クリアランス、③3Dプリント部品全6種の0.80mm未満肉厚チェック（確定除外箇所を除く違反0件）、④**スイッチ嵌合トッププレート・フラットボス＆内壁受け棚締結基板・カップ＆ホイール全体の 6-DOF 機械的拘束検証** を一括検証します。 |
| **[`generate_carrying_case.py`](./generate_carrying_case.py)** | 持ち運び用 1ピース・スナップイン・キャリングフレーム（`cases/carrying-frame.step`, `carrying-frame.stl`：互い違いウェッジ相殺対面構造・全4箇所 USB-C マグネット端子 `CIO-SLMG-T-C` 用 幅 $18.0\text{ mm}$ 完全開放 U字切り欠き・親指側＆小指側両側ワンタッチカンチレバーパドルラッチ・25mm球非接触ハローキーパー・L字欠きシールド一体造形）および `assembly-full.step` 全674ソリッド＋ゴム足10個＋`CIO-SLMG-T-C` 4個を統合した収納アセンブリ（`cases/assemblies/carrying-assembly.step`、全689ソリッド、外寸 $144.76 \times 103.51 \times 59.92\text{ mm}$）を生成し、JLC3DP 基本造形ルール・0.80mm未満薄肉完全ゼロ（除外0件）・全689ソリッド間干渉ゼロ（`0.00000000 mm³`）・ストレート着脱経路クリアランス・最小表面クリアランス・6-DOF 保持拘束を一括検証します。 |

### ② KiCad 基板・プレート・JLCPCB 発注データ・図版スクリプト
```powershell
$KICAD_PY = "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe"
```

| スクリプト | 役割・出力ファイル |
| :--- | :--- |
| **[`generate_plates.py`](./generate_plates.py)** | 左右 FR-4 トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`：全14箇所すべてキー谷間のネジ頭沈み込み用 $\varnothing 4.40\text{ mm}$ 逃げ穴［スイッチ嵌合保持・外周余白穴ゼロ］、および右手カバー不要 $7.70 \times 22.00\text{ mm}$ ホイール長穴）ならびにレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成し、DRC（違反0件）を検証します。 |
| **[`export_jlcpcb.py`](./export_jlcpcb.py)** | 全3基板（`curcur40-left`, `curcur40-right`, `curcur40-pmw3360`：すべて `1.6mm` FR-4 Bottom PCBA）の Gerber ZIP・BOM CSV・CPL CSV、および左右トッププレートの Gerber ZIP を一括出力し、JLCPCB 公式製造ルール（DRC/ERC、基板サイズ、最小配線幅 $\ge 0.127\text{ mm}$、最小ビア $\ge 0.45/0.30\text{ mm}$、PTH/NPTH穴径、ネジ穴・インサート座面周囲の銅箔キープアウト、BOM/CPL/LCSC整合性、DNP/THT除外、および全非`DNP`部品の `.step` 3Dモデル解決チェック）を発注前自動チェックします（※PCB変更時は続けて必ず `generate_full_assembly.py` を実行して3DP干渉を検証すること）。 |
| **[`generate_spec_diagrams.py`](./generate_spec_diagrams.py)** | `docs/assets/` 配下のスタックアップ断面図・コンパクト $\varnothing 5.20\text{ mm}$ フラットインサートボス＆統一 `M2×6mm` 締結図・トラックボールカップ詳細図面・**組み立て時の工具サイズ制限＆配線ガイド（`assembly_tool_clearance_guide.png`）** 等の解説図版 PNG を生成します（`uvx --from "cadgen==0.7.26" --with matplotlib --with pillow python` で実行）。 |
| **[`generate_inertia_wheel_diagram.py`](./generate_inertia_wheel_diagram.py)** | アンダープレート一体軸パッシブ磁気慣性ホイールの3Dプレビュー画像（`render_inertia_wheel_flywheel.png`, `render_inertia_wheel_module.png`, `render_curcur40_right_wheel.png`）、部品構成・組立ビジュアルガイド（`inertia_wheel_parts_guide.png`）、`#01`〜`#12` 全番号入り断面・機構解説図版（`passive_inertia_wheel_spec.png`）、および **小学生でもわかる3つのしくみ図解（`inertia_wheel_easy_guide.png`）** を生成します（`uvx --from "cadgen==0.7.26" --with matplotlib --with pillow python` で実行）。 |
| **[`render_previews.py`](./render_previews.py)** | `docs/assets/render_*.png` および `trackball_cup*.png`（フルアセンブリ表裏斜視・キャリングフレーム＆収納アセンブリ・全3基板・左右トッププレート・トラックボールカップの3Dレンダリング画像）を一括更新します。 |
| **[`render_assembly_video.py`](./render_assembly_video.py)** | トラックボールユニット組立 → アンダープレート慣性ホイール組立 → 密閉ボトムケース（白）・PCB（黒）・トッププレート（黒）・Choc V2 スイッチ40個・キーキャップ（白）40個・25mmボールの積み上げ工程を再現した **1080p 60fps PBR 3D組み立てアニメーション動画（`docs/assets/assembly_animation.mp4`）** および **インライン埋め込み用アニメーション WebP（`docs/assets/assembly_animation.webp`）** を生成します（`uvx --from "cadgen==0.7.26" --with pyvista --with imageio-ffmpeg --with pillow python` で実行、WebP のみ再生成する場合は `--webp-only` を付与）。 |
