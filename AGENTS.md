# curcur40 AI エージェント運用ルール (AGENTS.md)

本ファイルは、ワークスペース `curcur40` において AI エージェントが作業を行う際に**必ず遵守すべき最上位の運用ルール**を定義します。

---

## 1. エージェントの基本行動原則（ワークフロー・Git運用）

1. **作業着手前の方針確認（いきなり生成に入らない）**:
   - 会話の中でファイルの変更や再生成が必要になると判断した場合でも、**いきなりコード変更やデータ生成に入らず、まずユーザーへ対応方針を提案・確認してから作業を行うこと**。
   - ただし、**ユーザーから明示的に作成・変更・生成の依頼があった場合は、事前確認なしで直ちに実行してよい**。
2. **タスク単位での Git コミット（差分の明確化）**:
   - 複数の作業を行う場合や、1つのタスクが完了した際は、**タスクごとに Git コミットを作成し、どのタスクでどのファイルがどう変わったのか（タスクごとの差分）が履歴から明確に追えるようにすること**。
3. **仕様書ファースト（Single Source of Truth）**:
   - 設計の正は以下の6つのドキュメントである。対象領域の作業を行う前に必ず該当ドキュメントを確認すること。
     - ケース・プレート・トラックボールカップ仕様: [`docs/case_spec.md`](docs/case_spec.md)
     - PCB・回路図・ライブラリ・スクリプト格納仕様: [`docs/pcb_spec.md`](docs/pcb_spec.md)
     - アンダープレート一体軸パッシブ磁気慣性ホイール仕様: [`docs/passive_inertia_wheel_spec.md`](docs/passive_inertia_wheel_spec.md)
     - 購入部材・製造委託パーツリファレンス: [`docs/parts_spec.md`](docs/parts_spec.md)
     - キーボード全体ビルドガイド・BOM・発注仕様: [`docs/buildguide_jp.md`](docs/buildguide_jp.md)
     - プロジェクト概要・3Dプレビューギャラリー: [`README.md`](README.md)
   - エラーや警告を回避するためだけに無理やり不要な配線を追加したり、DRC/ERC ルールを無効化するような対症療法は絶対に行わないこと。

---

## 2. ディレクトリ構成とファイル管理ルール

1. **一時ファイル・使い捨てスクリプトの残置禁止**:
   - `scratch/` や `tmp/`、ルート直下の `.json` / `.rpt` / `.net` / `.bak` / `.kicad_prl` 等を作業後にリポジトリへ残さないこと。
   - スクリプト内で DRC/ERC レポートや Gerber 一時ファイルを出力する場合は、Python 標準の `tempfile.TemporaryDirectory` を使用して自動削除すること。
2. **公式生成スクリプトの一元管理 (`scripts/`)**:
   - 3Dモデル・プレート・発注データ・図版・プレビュー画像の生成は [`scripts/`](scripts/) 配下の10本の公式スクリプト（詳細は [`scripts/README.md`](scripts/README.md) 参照）に集約し、1回限りの調査・デバッグ用スクリプトを `scripts/` に残さないこと。
   - スクリプト内でワークスペースや入出力パスを参照する際は、`c:\Users\...` 等の環境依存フルパスをハードコードせず、必ずスクリプト自身の位置からの相対解決（`WORKSPACE = Path(__file__).resolve().parent.parent`）で記述すること。
3. **ボトムプレートの作成禁止と `cases/` ディレクトリ構成**:
   - ボトムプレートは 3D プリント製 100% 密閉・底面穴なしトレイ型ボトムケース（`cases/left.step`, `right.step`）に統合済みのため、生成・出力しないこと。
   - `cases/` 直下にはケース・カップ実部品（`left.step/.stl`, `left-desk.step/.stl`, `right.step/.stl`, `right-desk.step/.stl`, `trackball-cup.step/.stl`）、`cases/inertia_wheel/` 配下にはアンダープレート慣性ホイール実部品 4種（`steel-flywheel.step/.stl`, `magnet-holder.step/.stl`, `wheel-rocker.step/.stl`, `wheel-cradle.step/.stl`）、`cases/assemblies/` 配下には検証・確認用のアセンブリモデル 7種（`assembly-full.step`, `assembly-full-desk.step`, `curcur40-right-wheel-assembly.step`, `inertia-wheel-assembly.step`, `trackball-cup-with-ball.step/.stl`, `pmw3360-lens-pcb-assembly.step`, `trackball-sensor-assembly.step`）を分離して管理すること。
4. **ドキュメント・画像アセットの一元管理 (`docs/`)**:
   - `curcur40` に関するドキュメントおよびプレビュー・図解画像はすべて `docs/` および `docs/assets/` 配下に格納すること（ルート直下に `preview/` 等を作らない）。

---

## 3. PCB・回路図（KiCad 10.0）のルール

1. **実行環境**:
   - KiCad CLI: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe`
   - KiCad Python: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe`
2. **ライブラリ参照ポリシー（シャドウイングの禁止）**:
   - KiCad 公式標準ライブラリ（`MCU_RaspberryPi`, `Device`, `Diode`, `Connector`, `Capacitor_SMD`, `Resistor_SMD`, `Package_DFN_QFN`, `Package_SO`, `Package_TO_SOT_SMD`, `Jumper` 等）をプロジェクトローカルの `sym-lib-table` / `fp-lib-table` で上書き（シャドウイング）してはならない。
   - ローカル登録は `pcbs/common/kbd/` 配下の `kbd` および `PMW3360_PCB` のみとする。
3. **`pcbnew` Python API の注意事項**:
   - KiCad 10.0 では `PCB_VIA` オブジェクトに対してレイヤー引数なしで `GetWidth()` を呼び出したり `GetEnd()` を呼ぶと C++ アサーション（`assert "false" failed in GetWidth()`）で停止する。
   - `board.GetTracks()` を走査する際は必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を分岐させ、ビアには `t.GetWidth(pcbnew.F_Cu)` および `t.GetPosition()` を使用すること。
4. **右手基板 (`curcur40-right`) および トラックボールセンサーサブ基板 (`curcur40-pmw3360`) の固有仕様**:
   - トラックボールカップ開口面をトッププレート天面（$Z = -2.00\text{ mm}$）と同じ高さに揃える低プロファイル設計のため、PMW3360 センサー回路は独立サブ基板 [`pcbs/pmw3360/curcur40-pmw3360.kicad_pcb`](pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（$Z = -17.60 \sim -16.00\text{ mm}$）に分離し、右メイン基板 `rJ3` とセンサー基板 `J1` を **JST SH 1.0mm ピッチ 6ピン横向き SMD コネクタ（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160405`）** で接続する。
   - アンダープレート一体軸パッシブ磁気慣性ホイール用のセンサーおよび中クリック回路は**サブ基板・手配線ハーネスを一切使わず右メイン基板 `B.Cu` へ直接統合**する：
     - **`rU6`（`TMAG5273A1QDBVR`, `SOT-23-6`, LCSC `C3716049`）**: 右メイン基板 `B.Cu` の `(3.0175, -2.00)`（回転 $-90^\circ$）へ PCBA 実装し、`I2C0`（`GP24` `/WHEEL_SDA`, `GP25` `/WHEEL_SCL`、プルアップ抵抗 `rR11`/`rR12` $4.7\text{ k}\Omega$、パスコン `rC18` $100\text{ nF}$）へ接続する。Pin 5（`~INT`）は `rR13`（$0\ \Omega$）を介して `GNDR` へ落とすことで、ピン互換の Infineon `TLV493D-A1B6` にも無改造でフォールバック可能とする。
     - **`rEXSW1`（`Kailh Square Silent 6.2×6.2×4.3mm`）**: 右メイン基板 `B.Cu` の `(-2.0125, -2.00)` へ THT 2ピン直付けし、`GP7`（`/KEYEX1`, マトリクス `[4, 6]`）へ直接配線する（PCBA 対象からは THT として自動除外）。
     - 右メイン基板のホイール貫通窓は南側キー `rEXSW2` (`x = 14.2875`) と左右中心軸を完全一致させた回転軸中心 `(14.2875, -2.00)` 基準の十字スロット（縦 $7.70 \times 23.00\text{ mm}$ ＋ 軸受・磁石ホルダー逃げ横翼 $x_{\text{pcb}} \in [4.8375, 21.3375]\text{ mm}, y_{\text{pcb}} \in [-5.75, +1.75]\text{ mm}$）、右トッププレート開口はカバー不要の角丸長穴（$7.70 \times 22.00\text{ mm}$, $R = 1.00\text{ mm}$）とする。
   - `U1` (`PMW3360DM-T2QU`) の Pin 3 (`VDDPIX`) は内部レギュレータ出力（`power_out`）であるため、外部 1.8V 電源（`/+1V8_PMW`）とショートさせず `C1`/`C2` のみの独立ネット（`Net-(U1-VDDPIX)`）に保つこと。
   - `JP1` は `Jumper:SolderJumper_3_Bridged12`（`SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels`：Pad 1 `+3V3R` – Pad 2 `/V_{IO}` 基板内銅箔直結）を維持すること。
   - `R4` (28kΩ)、`C5` (22nF)、および左右のデバッグ端子 `J4` / `rJ4` は `DNP`（BOM/CPL/3Dモデル除外）を維持すること。
5. **DRC / ERC 合格基準および JLCPCB 発注前自動チェック (`scripts/export_jlcpcb.py`)**:
   - `kicad-cli pcb drc --schematic-parity`: 全3基板（`left`, `right`, `pmw3360`）すべて **違反 0件・未接続 0件・回路図不一致 0件**（左右トッププレートも DRC 違反 0件）。
   - `kicad-cli sch erc`: 左右メイン基板は **エラー 0件、警告 1件**（`RP2040` Pin 32 `GPIO21` と `+3V3` / `GNDR` の左右判定ピン直結による正当な `pin_to_pin` 警告 1件のみを意図的に保持）、`curcur40-pmw3360` は **エラー 0件、警告 0件**。
   - **JLCPCB 2層 FR-4 標準製造ルール (`verify_jlcpcb_preflight`)**:
     - 基板外形（`Edge.Cuts`）サイズ：PCBA 対象基板は単体実装下限 $20.0 \times 20.0\text{ mm}$ 以上、最大 $400 \times 500\text{ mm}$ 以内。
     - 最小配線幅 $\ge 0.127\text{ mm}$（$5\text{ mil}$、1oz 銅箔標準。実基板は $\ge 0.200\text{ mm}$）。
     - 最小ビア外径 $\ge 0.450\text{ mm}$、ビアドリル径 $\ge 0.300\text{ mm}$（2層標準追加料金なし下限。実基板は $0.50/0.30\text{ mm}$ または $0.60/0.30\text{ mm}$）、ビアアニュラリング $\ge 0.075\text{ mm}$。
     - PTH ドリル径 $0.20 \sim 6.30\text{ mm}$、NPTH ドリル径 $\ge 0.50\text{ mm}$。
     - Gerber ZIP 内の全9レイヤー＋PTH/NPTH ドリルファイル存在確認、BOM/CPL の Designator 完全一致、全実装部品の有効な LCSC 番号（`Cxxxxxx`）、および `DNP`/THT 部品の除外を自動検証すること。

---

## 4. 3D CAD (`cadgen` / `build123d`) のルール

1. **実行環境**:
   - `& "$env:USERPROFILE\.local\bin\uvx.exe" --no-config --managed-python --python 3.13 --from "cadgen==0.7.26" python`
2. **光学距離基準点 (`Lens_Optical_Ref_Point`) の維持**:
   - 以下の5つの検証アセンブリ STEP モデル（[`cases/assemblies/`](cases/assemblies/) 配下）には、GUI（CAD Viewer 等）で直接選択して 25mm ボール（`Trackball_25mm`, 最下面 $Z_{\text{rel}} = +5.80\text{ mm}$ / フルアセンブリ $Z = -10.2000\text{ mm}$）との距離（設計値 **$2.40\text{ mm}$**）を計測できるよう、光軸中心のレンズフランジ着座面（$Z_{\text{rel}} = +3.4000\text{ mm}$ / フルアセンブリ $Z = -12.6000\text{ mm}$）に独立した名前付きオブジェクト **`Lens_Optical_Ref_Point`** を `bd.Compound(children=[...])` の子要素として必ず含めること：
     - `cases/assemblies/pmw3360-lens-pcb-assembly.step`
     - `cases/assemblies/trackball-sensor-assembly.step`
     - `cases/assemblies/trackball-cup-with-ball.step`
     - `cases/assemblies/assembly-full.step`
     - `cases/assemblies/assembly-full-desk.step`
3. **17箇所 真鍮ヒートセットインサート＋上方向統一 `M2 × 6.0mm` ネジ締結（四隅8箇所太径段付きトッププレート直固定・フラット円筒 `L4/R4`・Cクリップヒンジ）・100%密閉底面ケース・干渉ゼロ＆6-DOF拘束検証**:
   - `5.50mm` スペーサー、ケース底面ザグリ穴、およびケース外周内壁の受け突起リブは全面廃止し、キーボード全体の全 17箇所すべてを **`M2 × L=3.0 × OD=3.2mm` 真鍮ヒートセットインサート（計 17個、下穴 $\varnothing 2.85\text{ mm}$、全箇所フラットボス天面へツライチ熱圧入）** と **統一長さ `M2 × 6.0mm` ネジ（計 17本）** で締結する仕様を維持すること：
     - **左右ケース外周四隅 8箇所（`L1, L2, L3, L5` および `R1, R2, R3, R5`、`L2/R2 = (0, 18.00)`, `L5/R5 = (±62.00, 65.15)`）**: **太径段付きヒートセットボス**（下段肩 $\varnothing 7.84\text{ mm}$ が $Z = -5.80\text{ mm}$ でメイン基板 `B.Cu` を支持、上段首 $\varnothing 6.00\text{ mm}$［片側肉厚 $1.575\text{ mm}$］がメイン基板の $\varnothing 6.20\text{ mm}$ 穴／南U溝を通過して $Z = -3.60\text{ mm}$ でトッププレート裏面を直接支持、盲穴底 $Z = -9.60\text{ mm}$）とし、トッププレートの $\varnothing 2.40\text{ mm}$ 穴から `M2 × 6.0mm` ネジでスイッチ未装着でもトッププレートとメイン基板を直接ネジ固定する。
     - **小指側下 2箇所（`L4, R4`: `(±98.45, 38.15)`）**: 旧来の階段状段下げを廃止し、側面スイッチ `SMDSW1/2` から $\ge 0.30\text{ mm}$・パッドから $> 0.40\text{ mm}$ 離隔した **段差ゼロの $\varnothing 4.90\text{ mm}$ フラット円筒ボス（天面 $Z = -5.80\text{ mm}$、片側肉厚 $1.025\text{ mm}$、盲穴底 $Z = -10.50\text{ mm}$）** とし、トッププレートの $\varnothing 4.40\text{ mm}$ ネジ頭逃げ穴を通してメイン基板 `F.Cu`（$Z = -4.20\text{ mm}$、穴径 $\varnothing 2.40\text{ mm}$）を直接クランプする。
     - **トラックボールカップ固定耳 4箇所（`TB1`〜`TB4`）**: カップ固定耳を高さ **$2.00\text{ mm}$ のフラット耳（ストレート穴 $\varnothing 2.40\text{ mm}$、段付き穴なし）**とし、センサー基板（板厚 $1.60\text{ mm}$、ストレート穴 $\varnothing 2.40\text{ mm}$）ごとケースボス天面（**$Z = -17.60\text{ mm}$**、盲穴深さ $3.80\text{ mm}$）の真鍮インサートへ上から `M2 × 6.0mm` ネジで締結する（有効螺合 $2.40\text{ mm}$＝6山、穴底隙間 $1.40\text{ mm}$）。
     - **ホイールクレードル固定 2箇所（`WC1`: `(6.6375, -9.80)`, `WC2`: `(21.2375, 6.00)`）**: 右トッププレートの $\varnothing 4.40\text{ mm}$ 頭逃げ穴および右メイン基板の $\varnothing 2.40\text{ mm}$ 穴を通し、`wheel-cradle.step`（左右 Cクリップスナップインヒンジ付）の真鍮インサート 2箇所へ上から `M2 × 6.0mm` ネジで締結する。
     - **ホイール磁気デテント調整 1箇所（`wheel-rocker.step` 南ボス）**: 南ボス（$\varnothing 2.85\text{ mm}$ 穴）の真鍮インサートへ磁性鋼製 `M2 × 6.0mm` ネジを螺合し、ネジ先端に磁力で自己吸着させた $\varnothing 2.0 \times 2.0\text{ mm}$ ネオジム磁石（接着剤ゼロ）と 45#鋼ホイール 24溝のギャップでノッチ強弱を無段階調整する。
   - モデル更新時は `scripts/generate_inertia_wheel.py` および `scripts/generate_full_assembly.py` を実行し、静止姿勢（$0^\circ$）および中クリック押下姿勢（$2.20^\circ$）の双方で全パーツ間の干渉体積（`overlap_volume`）が `0.00000000 mm³` であること、ならびに **`verify_6dof_constraints()` により固定自由度の機械的ロックと稼働自由度の無干渉運動がすべて満たされること** を確認すること。
4. **JLC3DP / JLCCNC 発注前チェック・極小隙間・肉厚 $0.80\text{ mm}$ 未満の自動検証ルール**:
   - 3Dモデル生成時（[`scripts/generate_cases.py`](scripts/generate_cases.py)、[`scripts/generate_trackball_cup.py`](scripts/generate_trackball_cup.py)、[`scripts/generate_inertia_wheel.py`](scripts/generate_inertia_wheel.py)、[`scripts/generate_full_assembly.py`](scripts/generate_full_assembly.py)）には、干渉体積チェックに加えて以下の3項目を自動検証し、違反が **0件** であることをアサートすること：
     1. **JLC3DP 基本造形ルール（水密多様体・造形サイズ・最小穴径・底面接地）**:
        - 水密・多様体かつ単一ソリッド（`solid.is_valid`, `is_sound(solid)`, `len(solid.solids()) == 1`, `solid.volume > 0`）であること。
        - 造形サイズが JLC3DP MJF/SLS 最小サイズ（$5 \times 5 \times 2\text{ mm}$）以上・最大造形サイズ（$380 \times 284 \times 380\text{ mm}$）以内であり、全 3Dプリント用モデル（`left-desk`, `right-desk`, `trackball-cup`, `magnet-holder`, `wheel-rocker`, `wheel-cradle`）の底面が $Z = 0.0000\text{ mm}$ に水平接地していること。
        - すべての凹円筒面（穴・インサート下穴 $\varnothing 2.85\text{ mm}$・内角R）の直径が JLC3DP MJF/SLS 基準の **$\varnothing 1.50\text{ mm}$ 以上**であること。
     2. **極小隙間の検証（別パーツ間クリアランス & 同一ボディ内の微小隙間）**:
        - 非接触パーツ間（センサーIC・`J1`/`rJ3`・`rU6`・`rEXSW1`・裏面SMD部品・USB-Cコネクタ4箇所・ホイール可動部 vs ケース内底面・ボス・クレードル・プレート等）および JLC3DP 推奨クリアランス（可動部 $\ge 0.30\text{ mm}$、静的嵌合部 $\ge 0.20\text{ mm}$）が規定閾値以上であることを `closest_points` で自動検証すること。
        - ケース内壁に近接する円筒ボス（右手 `R4, R5, TB1, TB3, TB4`、左手 `L4, L5`）は隣接内壁へU字・コーナーブリッジで直結・一体化させ、清掃不能な狭小隙間を残さないこと。
     3. **肉厚 $0.80\text{ mm}$ 未満の検証（確定除外箇所を除く）**:
        - JLC3DP 発注対象の全6モデルについて、OpenCascade `BRepExtrema_DistShapeShape` により全非隣接面ペア距離（$0.001 < d < 0.80\text{ mm}$）を自動走査し、以下の意図的な確定除外箇所以外の $0.80\text{ mm}$ 未満箇所が **0件** であることを検証すること：
          - **`magnet-holder`, `wheel-rocker`, `wheel-cradle` の3モデル**: **除外箇所なし（`< 0.80 mm` 面ペア完全 0件）**。
          - **左右ケース（`left-desk` / `right-desk`）の除外箇所**:
            - ① ケース上端フチ（$Z = 0.00\text{ mm}$）：壁厚 $1.50\text{ mm}$ に対する外周 $R = 0.95\text{ mm}$ フィレット残りの水平天面幅（$0.550\text{ mm}$、およびコーナー部の斜め距離 $0.629 \sim 0.743\text{ mm}$）。
            - ② 小指側内底面の水平スキム面（$Z = -8.00\text{ mm}$, $|X_{\text{step}}| \ge 132.0\text{ mm}$）と傾斜床／内角フィレットとの境界段差（$0.459 \sim 0.549\text{ mm}$）。
          - **トラックボールカップ（`trackball-cup`）の除外箇所**:
            - ① グループA（約 $0.355\text{ mm}$、$Z_{\text{rel}} \in [7.0, 8.8]\text{ mm}$）：$\varnothing 2.00\text{ mm}$ セラミック支持球3箇所のスナップイン抜け止めリップ（入口 $\varnothing 1.95\text{ mm}$）。
            - ② グループD（$0.700\text{ mm}$、$Z_{\text{rel}} \in [21.0, 22.8]\text{ mm}$）：ボール保持爪3箇所の上端導入面取りエッジ（※固定耳を $2.00\text{ mm}$ フラット直穴化したことで旧グループB・Cは完全解消済み）。

---

## 5. AI 監査・レビュー時の誤認防止ルール（確定設計仕様の根拠）

過去に AI 監査で誤認（フォールスポジティブ）が発生しやすい以下の項目は、実部品・データシート・上流 OSS に基づく確定仕様であるため、誤指摘や誤った改変を行わないこと：

1. **`PMW3360` / `LM19-LSI` の基板角穴（$16.90 \times 8.70\text{ mm}$）とガイドポスト位置**:
   - スクリプト内のプロシージャル生成モデルではなく、常に実フットプリント [`PMW3360DM-T2QU_16Pin.kicad_mod`](pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)（[`monkeypad/pmw3360-breakout`](https://github.com/monkeypad/pmw3360-breakout) / [`siderakb/pmw3360-pcb`](https://github.com/siderakb/pmw3360-pcb) 準拠）および実基板 `curcur40-pmw3360.kicad_pcb` を正とする。
   - 実部品の丸ガイドポスト穴は非対称配置（センサー中心基準で $(-7.10, +3.30)\text{ mm}$ および $(+6.70, -3.40)\text{ mm}$、穴径 $\varnothing 1.70\text{ mm}$）であり、$16.90 \times 8.70\text{ mm}$（$\pm 8.45 \times \pm 4.35\text{ mm}$）の基板角穴の内側に余裕をもって収まる。
2. **アンダープレート 1ピース一体軸ホイール (`steel-flywheel.step`)・Cクリップヒンジ (`wheel-cradle.step`) と基板直付け 3D ホール (`rU6`) の確定仕様**:
   - [`steel-flywheel.step`](cases/inertia_wheel/steel-flywheel.step) は JLCCNC の `45# Steel`（S45C 強磁性炭素鋼）＋無電解ニッケルめっきによる **1ピース削り出し品**であり、外径 $\varnothing 22.00 \times 6.50\text{ mm}$ リム（外周 24フルート溝、質量 $19.31\text{ g}$）・内輪当たり面となる **$\varnothing 2.90\text{ mm}$ 一体段付き肩**（シムリング不要）・**$\varnothing 1.98\text{ mm}$ ベアリングジャーナル＆西側 Dカット軸**を一体加工する。別体平行ピンや内輪シムを追加してはならない。また、`wheel-rocker.step` の軸受座上開口 $4.56\text{ mm}$（Cクリップスナップイン保持）、`wheel-cradle.step` の **Cクリップスナップインヒンジ（内径 $\varnothing 3.06\text{ mm}$・入口スロート幅 $2.66\text{ mm}$・抱き角 $239^\circ$、支点 $Z = -8.15\text{ mm}$：基板未装着でも `#03` の $\varnothing 3.00\text{ mm}$ トラニオン支点軸を単体で抜け止め連結）**、および西側一体キーパータブはガタ・脱落防止のための確定形状である。
   - 強磁性 45#鋼リム自身の 24溝と南ボスの軸方向着磁ネオジム磁石（$\varnothing 2.0 \times 2.0\text{ mm}$、鉄製 `M2 × 6.0mm` ネジ先端に磁力で自己吸着・接着剤不要）で非接触磁気ラチェットを構成するため、旧設計のような別体ラチェットハブや鋼球は不要である。
   - 右メイン基板 `B.Cu` の `rU6`（`TMAG5273A1QDBVR`）は off-axis（軸端横）配置された `D4×1mm` 径方向2極着磁磁石の回転磁界 $(B_x, B_z)$ を `XZX` 擬似同時サンプリング＋適応包絡線正規化＋整数 CORDIC で直接角度復調する（同軸配置用のサブ基板は不要）。また、`rR13`（$0\ \Omega$）により Pin 5 を `GNDR` へ接続しているため、TI `TMAG5273`（`~INT` オープンドレイン出力、起動時無効）と Infineon `TLV493D-A1B6`（Pin 5 `GND` 必須）の双方にそのまま適合する。
3. **トッププレートの四隅8箇所太径段付きボス直接ネジ固定（$\varnothing 2.40\text{ mm}$）と4箇所ネジ頭逃げ穴（$\varnothing 4.40\text{ mm}$）の使い分け**:
   - 左右外周四隅の 8箇所（`L1, L2, L3, L5` および `R1, R2, R3, R5`）はケースの太径段付きインサートボス（下段肩 $\varnothing 7.84\text{ mm}$ でメイン基板 `B.Cu` $Z = -5.80\text{ mm}$ を支持、上段首 $\varnothing 6.00\text{ mm}$［片側肉厚 $1.575\text{ mm}$］がメイン基板の $\varnothing 6.20\text{ mm}$ 穴／南U溝を通過してトッププレート裏面 $Z = -3.60\text{ mm}$ を直接支持）により、トッププレートの $\varnothing 2.40\text{ mm}$ 貫通穴から `M2 × 6.0mm` ネジでスイッチ未装着でもプレート単体が完全固定される確定設計である。
   - 一方、小指下 2箇所（`L4, R4`: 天面 $Z = -5.80\text{ mm}$ の段差なしフラット円筒ボス $\varnothing 4.90\text{ mm}$）およびホイールクレードル 2箇所（`WC1, WC2`: 基板裏面のクレードル締結）の計 4箇所は、トッププレートを $\varnothing 4.40\text{ mm}$ ネジ頭逃げ穴とすることで `M2 × 6.0mm` ネジ頭をメイン基板 `F.Cu`（$Z = -4.20\text{ mm}$）へ直接着座させ、全 17箇所のネジ長を **`M2 × 6.0mm` 1種類に完全統一**している。
4. **Kailh Choc V2 スイッチのプレート厚（$1.60\text{ mm}$）・開口（$14.0 \times 14.0\text{ mm}$）と旧 $\varnothing 0.40\text{ mm}$ 穴**:
   - Kailh Choc V2（`CPG1353`）のラッチ溝高さは $1.65\text{ mm}$、ハウジング幅は $13.80 \times 13.80\text{ mm}$ であり、板厚 $1.60\text{ mm}$ の FR-4 トッププレートおよび $14.0 \times 14.0\text{ mm}$ 開口（Corne V4 準拠）に適合する。
   - `keyswitch_choc12_hotswap_1u` の `(-5.0, -5.15)` にあった $\varnothing 0.40\text{ mm}$ NPTH 穴は、Corne V3 のスイッチ回り止め樹脂ピン穴（$1.5 \times 2.0\text{ mm}$）を Corne V4 で配線通過のために縮小した残骸であったため削除済み。
