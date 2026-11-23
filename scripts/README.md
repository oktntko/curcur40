# `scripts/` — curcur40 公式生成・自動検証スクリプト集

本ディレクトリには、**curcur40** の 3D CAD モデル（STEP / 2D PDF）、FR-4 トッププレート基板（`.kicad_pcb` / `.svg`）、JLCPCB 発注用製造データ（`GERBER` / `BOM` / `CPL`）、およびドキュメント用図版・プレビュー画像・3D 組み立て動画を再現可能に生成・検証する公式スクリプト（全 12本）を格納します。

---

## 1. 運用ルールと出力先ディレクトリ

1. **恒久スクリプトのみを管理**: 1回限りの調査スクリプトや一時レポート（`.rpt`, `.net`, `.bak`, `.kicad_prl`）は残さず、DRC 検証や一時プロットには `tempfile.TemporaryDirectory` を使用します。
2. **環境非依存の相対パス**: フルパスをハードコードせず、`WORKSPACE = Path(__file__).resolve().parent.parent` を起点に解決します。
3. **STEP 一本化（STL 非出力）**: 3Dプリント・CNC 発注および CAD 検証はすべて高精度な `.step`（および CNC 2D 図面 `.pdf`）に統一しており、重複する `.stl` は出力しません。
4. **主な出力先**:
   - ケース・カップ・ボックス単体モデル: [`cases/`](../cases/)（`left.step`, `left-desk.step`, `right.step`, `right-desk.step`, `trackball-cup.step`, `carrying-box.step`, `carrying-box-lid.step`）
   - 慣性ホイール単体モデル・2D公差図面: [`cases/inertia_wheel/`](../cases/inertia_wheel/)（`steel-flywheel.step`, `steel-flywheel.pdf`, `magnet-holder.step`, `wheel-rocker.step`, `wheel-cradle.step`）
   - 検証・レンダリング用アセンブリ（8種）: [`cases/assemblies/`](../cases/assemblies/)（`assembly-full.step`, `assembly-full-desk.step`, `carrying-box-assembly.step`, `carrying-box-with-lid-assembly.step`, `curcur40-right-wheel-assembly.step`, `inertia-wheel-assembly.step`, `pmw3360-lens-pcb-assembly.step`, `trackball-cup-with-ball.step`）
   - トッププレート・SVG: [`plates/pcb/`](../plates/pcb/), [`plates/svg/`](../plates/svg/)
   - JLCPCB 発注データ: [`pcbs/panel/jlcpcb/production_files/`](../pcbs/panel/jlcpcb/production_files/)（単体基板用は `pcbs/{left,right,pmw3360}/jlcpcb/production_files/`、プレート用は `plates/pcb/jlcpcb/production_files/`）
   - 図版・プレビュー画像・動画: [`docs/assets/`](../docs/assets/)

---

## 2. スクリプト一覧と担当仕様書の対応（全 12本）

### ① 3D CAD 生成・検証スクリプト（`cadgen==0.7.26` / Python 3.13 環境）

実行コマンドプレフィックス（PowerShell）:
```powershell
& "$env:USERPROFILE\.local\bin\uvx.exe" --no-config --managed-python --python 3.13 --from "cadgen==0.7.26" python <script.py>
```

| スクリプト | 対応仕様書 | 役割・出力ファイル |
| :--- | :--- | :--- |
| **[`generate_cases.py`](./generate_cases.py)** | [`case_spec.md`](../docs/case_spec.md) | 左右の密閉ボトムケース（内部基準 `left.step`, `right.step` および JLC3DP 用の底面水平接地 `left-desk.step`, `right-desk.step`）を生成し、JLC3DP 造形基準・極小隙間・薄肉チェックを実行します。 |
| **[`generate_trackball_cup.py`](./generate_trackball_cup.py)** | [`trackball_spec.md`](../docs/trackball_spec.md) | 25 mm トラックボールカップ（`trackball-cup.step`）および 25 mm 球＋光学基準面付きアセンブリ（`trackball-cup-with-ball.step`）を生成し、干渉・薄肉チェックを実行します。 |
| **[`generate_sensor_assemblies.py`](./generate_sensor_assemblies.py)** | [`trackball_spec.md`](../docs/trackball_spec.md) | PMW3360 + LM19-LSI + サブ基板の光学基準アセンブリ（`pmw3360-lens-pcb-assembly.step`, `Lens_Optical_Ref_Point` 収録）を生成し、規定光学距離 `2.4000 mm` と非接触を検証します。 |
| **[`generate_inertia_wheel.py`](./generate_inertia_wheel.py)** | [`wheel_spec.md`](../docs/wheel_spec.md) | 慣性ホイール実部品 4種（`steel-flywheel.step` ＋ 2D公差図面 `steel-flywheel.pdf`, `magnet-holder.step`, `wheel-rocker.step`, `wheel-cradle.step`）と単体アセンブリ（`inertia-wheel-assembly.step`）を生成し、DFM・干渉・単体 6-DOF 拘束・垂直挿入軌道を検証します。 |
| **[`generate_full_assembly.py`](./generate_full_assembly.py)** | [`case_spec.md`](../docs/case_spec.md) | KiCad 10.0 から全3基板＋実 3D 部品モデルを直接 STEP 出力・同期し、全パーツを統合したフルアセンブリ（`assembly-full.step`, `assembly-full-desk.step`）および右手ホイール検証モデル（`curcur40-right-wheel-assembly.step`）を生成して、干渉ゼロ・最小クリアランス・全体 6-DOF 拘束を一括検証します。 |
| **[`generate_carrying_box.py`](./generate_carrying_box.py)** | [`carrying_box_spec.md`](../docs/carrying_box_spec.md) | 上下リバーシブル収納ボックス（`carrying-box.step`）・浅角カムスナップフタ（`carrying-box-lid.step`）および収納検証アセンブリ 2種（`carrying-box-with-lid-assembly.step`, `carrying-box-assembly.step`）を生成し、スナップ力学・点対称性・正逆両向きの干渉ゼロ＆ 6-DOF 拘束を検証します。 |

### ② KiCad 基板・プレート・JLCPCB 出力スクリプト（KiCad 10.0 Python 環境）

実行コマンドプレフィックス（PowerShell）:
```powershell
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" <script.py>
```

| スクリプト | 対応仕様書 | 役割・出力ファイル |
| :--- | :--- | :--- |
| **[`generate_plates.py`](./generate_plates.py)** | [`case_spec.md`](../docs/case_spec.md) | 左右 FR-4 トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`：裏面ガーバー認識用マーカー付）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成し、DRC 違反 0件を検証します。 |
| **[`export_jlcpcb.py`](./export_jlcpcb.py)** | [`pcb_spec.md`](../docs/pcb_spec.md) | 3-in-1 統合パネル（`curcur40-panel-3in1`）の自動合成、全基板・パネルの Gerber ZIP / BOM CSV / CPL CSV、およびトッププレート Gerber ZIP を出力し、JLCPCB プリフライト検証を一括実行します（※基板・プレート変更時は続けて必ず `generate_full_assembly.py` も実行）。 |

### ③ 図版・プレビュー画像・動画レンダリングスクリプト

| スクリプト | 役割・出力アセット |
| :--- | :--- |
| **[`generate_spec_diagrams.py`](./generate_spec_diagrams.py)** | スタックアップ断面図、ファスナ配置図、トラックボールカップ詳細図面、工具クリアランスガイド等の解説図版 PNG を生成（`--with matplotlib --with pillow` を付与して実行）。 |
| **[`generate_inertia_wheel_diagram.py`](./generate_inertia_wheel_diagram.py)** | 慣性ホイールの 3D レンダリング画像、部品構成ガイド、断面解説図、3要素しくみ図解 PNG を生成（`--with matplotlib --with pillow`）。 |
| **[`render_previews.py`](./render_previews.py)** | フルアセンブリ、キャリングボックス、全3基板、左右トッププレート、トラックボールカップの 3D プレビュー画像を `docs/assets/` へ一括レンダリング。 |
| **[`render_assembly_video.py`](./render_assembly_video.py)** | 1080p 60fps PBR 3D 組み立てアニメーション動画（`assembly_animation.mp4`）および WebP（`assembly_animation.webp`）を生成（`--with pyvista --with imageio-ffmpeg --with pillow`）。 |

---

## 3. 自動検証・合格基準の定義（Validation Criteria）

### 3.1 PCB DRC / ERC ＆ JLCPCB プリフライト基準 (`export_jlcpcb.py`)
- **DRC (`kicad-cli pcb drc --schematic-parity`)**: 全3基板・3-in-1 パネル・左右トッププレートすべて **違反 0件・未配線 0件・回路図不一致 0件**。
- **ERC (`kicad-cli sch erc`)**: `curcur40-pmw3360` は **エラー 0件・警告 0件**。左右メイン基板は **エラー 0件・警告 1件**（左右判定ピン `GPIO21` と `+3V3` / `GNDR` 直結による意図的な `pin_to_pin` 警告のみ）。
- **製造制約チェック**:
  - 外形サイズ: 単体基板 `≥ 20 × 20 mm`、パネル `70 × 70 〜 250 × 250 mm` 以内（実測 `131.05 × 207.25 mm`、全 88箇所のマウスバイト穴端から銅箔まで `≥ 0.48 mm`）。
  - 最小配線幅 `≥ 0.127 mm`（実基板 `≥ 0.200 mm`）、最小ビア `≥ 0.45 / 0.30 mm`（実基板 `0.50 / 0.30 mm` または `0.60 / 0.30 mm`）、アニュラリング `≥ 0.075 mm`、Via-in-Pad ゼロ。
  - PTH ドリル `0.20 〜 6.30 mm`、NPTH ドリル `≥ 0.50 mm`、固定穴周囲の銅箔キープアウト確保。
  - Gerber 全 9レイヤー＋ドリル同梱、BOM / CPL Designator 完全一致、有効 LCSC 番号、THT / DNP 除外、および **全非 DNP 部品の有効な `.step` 3D モデル存在確認**（固定除外は銅箔ブリッジ `JP1` と光学側配置 `PMW3360 U1` の 2点のみ）。

### 3.2 JLC3DP / JLCCNC 造形ガイドライン＆薄肉検証基準
- **基本造形要件**: 1ファイル 1モデル（水密多様体単一ソリッド）、造形サイズ `5 × 5 × 5 〜 350 × 276 × 360 mm` 以内、最下面 `Z = 0.0000 mm` 水平接地、全凹円筒穴径 `≥ ⌀1.50 mm` かつ穴深さ比 `h/Φ ≤ 3.0`。
- **非隣接面ペア肉厚検証と確定除外箇所**:
  - `magnet-holder`, `wheel-rocker`: `< 1.20 mm` 面ペア **0件**（爪・突起 `≥ 1.50 mm`）。
  - `wheel-cradle`: `< 1.00 mm` 面ペア **0件**（爪・脚 `≥ 1.55 mm`）。
  - `carrying-box`, `carrying-box-lid`: `< 0.80 mm` 面ペア **0件**。
  - `left-desk`, `right-desk`: 壁厚 `1.50 mm` に対する上端外周 `R = 0.95 mm` フィレット残りの水平リム幅（`0.550 mm`）およびコーナー斜め距離のみを確定除外とし、その他 `< 0.80 mm` 違反 **0件**。
  - `trackball-cup`: セラミック支持球 3箇所の抜け止めリップ（約 `0.455 mm`）とボール保持爪 3箇所の上端面取りエッジ（`0.700 mm`）のみを確定除外とし、その他 `< 0.80 mm` 違反 **0件**。

### 3.3 3D 干渉ゼロ・最小クリアランス・6-DOF 機械拘束検証 (`generate_full_assembly.py` 等)
- **干渉体積ゼロ**: KiCad 実 3D 部品モデル・嵌合 JST `SHR-06V-S-B` ハウジング・折りたたみスタンド・ネジ・インサートを含む全ソリッド間で `overlap_volume == 0.00000000 mm³`（静止姿勢・`2.95°` クリック押下姿勢・キャリングボックス正逆両収納姿勢）。
- **最小クリアランス・光学距離**: 全 SMD 部品 vs ケース `≥ 0.30 mm`、ホイール可動部 vs ケース床 `≥ 0.40 mm`・vs プレート/基板 `≥ 0.30 mm`、25 mm 球 vs カップ `0.25 mm`、ボール最下面 vs `Lens_Optical_Ref_Point` 距離 **`2.4000 mm`**。
- **6-DOF 拘束＆挿入軌道**: 基板・カップ・クレードルがボス＆ネジで、トッププレートが 39個の Choc V2 スイッチ嵌合で `±X, ±Y, ±Z` すべて機械ロックされ、ホイール機構は回転（`Rx 360°`）とクリック揺動（`0° 〜 2.95°` ＋ ハードストップ）のみが許容され、上からの垂直組み込み軌道で干渉ゼロであること。
