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
     - パッシブ磁気慣性ホイール機構・電気仕様: [`docs/passive_inertia_wheel_spec.md`](docs/passive_inertia_wheel_spec.md)
     - キーボード全体ビルドガイド・BOM・発注仕様: [`docs/buildguide_jp.md`](docs/buildguide_jp.md)
     - 慣性ホイール単体評価ポッドビルドガイド: [`docs/inertia_wheel_eval_buildguide_jp.md`](docs/inertia_wheel_eval_buildguide_jp.md)
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
   - ボトムプレートは 3D プリント製トレイ型ボトムケース（`cases/left.step`, `right.step`）に統合済みのため、生成・出力しないこと。
   - `cases/` 直下にはケース・カップ実部品（`left.step/.stl`, `left-desk.step/.stl`, `right.step/.stl`, `right-desk.step/.stl`, `trackball-cup.step/.stl`）、`cases/inertia_wheel/` 配下にはパッシブ磁気慣性ホイール実部品（7種）、`cases/assemblies/` 配下には検証・確認用のアセンブリモデル（計9種）を分離して管理すること。
4. **ドキュメント・画像アセットの一元管理 (`docs/`)**:
   - `curcur40` に関するドキュメントおよびプレビュー・図解画像はすべて `docs/` および `docs/assets/` 配下に格納すること（ルート直下に `preview/` 等を作らない）。

---

## 3. PCB・回路図（KiCad 10.0）のルール

1. **実行環境**:
   - KiCad CLI: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe`
   - KiCad Python: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe`
2. **ライブラリ参照ポリシー（シャドウイングの禁止）**:
   - KiCad 公式標準ライブラリ（`MCU_RaspberryPi`, `Device`, `Diode`, `Connector`, `Capacitor_SMD`, `Resistor_SMD`, `Package_DFN_QFN`, `Package_SO`, `Jumper` 等）をプロジェクトローカルの `sym-lib-table` / `fp-lib-table` で上書き（シャドウイング）してはならない。
   - ローカル登録は `pcbs/common/kbd/` 配下の `kbd` および `PMW3360_PCB` のみとする。
3. **`pcbnew` Python API の注意事項**:
   - KiCad 10.0 では `PCB_VIA` オブジェクトに対してレイヤー引数なしで `GetWidth()` を呼び出したり `GetEnd()` を呼ぶと C++ アサーション（`assert "false" failed in GetWidth()`）で停止する。
   - `board.GetTracks()` を走査する際は必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を分岐させ、ビアには `t.GetWidth(pcbnew.F_Cu)` および `t.GetPosition()` を使用すること。
4. **右手基板 (`curcur40-right`) および 2種のセンサーサブ基板 (`curcur40-pmw3360`, `curcur40-wheel-sensor`) の固有仕様**:
   - トラックボールカップ開口面をトッププレート天面（$Z = -2.00\text{ mm}$）と同じ高さに揃える低プロファイル設計のため、PMW3360 センサー回路は独立サブ基板 [`pcbs/pmw3360/curcur40-pmw3360.kicad_pcb`](pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（$Z = -17.60 \sim -16.00\text{ mm}$）に分離し、右メイン基板 `rJ3` とセンサー基板 `J1` を **JST SH 1.0mm ピッチ 6ピン横向き SMD コネクタ（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160405`）** で接続する。
   - パッシブ磁気慣性ホイールは右手内側上部の $18.50 \times 18.50\text{ mm}$ 角穴（＋ $\varnothing 3.70\text{ mm} \times 3$ ポスト穴 `W1`〜`W3`）へ沈み込ませ、板厚 `0.80 mm` の極小サブ基板 [`pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb`](pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb)（`AS5600-ASOT` `Top Side` PCBA）と静音中クリック SW を右メイン基板 `B.Cu` の **`rJ5`（`SM06B-SRSS-TB`, `C160405`, Pin 1 `+3V3R`, Pin 2/6 `GNDR`, Pin 3 `/WHEEL_SDA` [`GP24`], Pin 4 `/WHEEL_SCL` [`GP25`], Pin 5 `/KEYEX1` [`GP7`]）** へ接続する。
   - `U1` (`PMW3360DM-T2QU`) の Pin 3 (`VDDPIX`) は内部レギュレータ出力（`power_out`）であるため、外部 1.8V 電源（`/+1V8_PMW`）とショートさせず `C1`/`C2` のみの独立ネット（`Net-(U1-VDDPIX)`）に保つこと。
   - `JP1` は `Jumper:SolderJumper_3_Bridged12`（`SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels`：Pad 1 `+3V3R` – Pad 2 `/V_{IO}` 基板内銅箔直結）を維持すること。
   - `R4` (28kΩ)、`C5` (22nF)、および左右のデバッグ端子 `J4` / `rJ4` は `DNP`（BOM/CPL/3Dモデル除外）を維持すること。
5. **DRC / ERC 合格基準および JLCPCB 発注前自動チェック (`scripts/export_jlcpcb.py`)**:
   - `kicad-cli pcb drc --schematic-parity`: 全5基板（`left`, `right`, `pmw3360`, `inertia-wheel-sensor`, `inertia-wheel-eval`）すべて **違反 0件・未接続 0件・回路図不一致 0件**（左右トッププレートも DRC 違反 0件）。
   - `kicad-cli sch erc`: 左右メイン基板は **エラー 0件、警告 1件**（`RP2040` Pin 32 `GPIO21` と `+3V3` / `GNDR` の左右判定ピン直結による正当な `pin_to_pin` 警告 1件のみを意図的に保持）、`curcur40-pmw3360`・`curcur40-wheel-sensor`・`curcur40-wheel-eval` の3基板は **エラー 0件、警告 0件**。
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
3. **14箇所 M2 5.50mm スペーサー統一締結構造・沈み込み慣性ホイール吊り下げ締結・干渉ゼロ検証**:
   - 左手外周 5箇所（`L1`〜`L5`）＋ 右手外周 5箇所（`R1`〜`R5`、親指側 `L5`/`R5` は $(\pm 62.0000, 64.6000)$ で完全左右対称、ボス上面 $Z = -9.10\text{ mm}$）＋ トラックボールカップ固定耳 4箇所（`TB1`〜`TB4`、ボス上面 $Z = -17.60\text{ mm}$、センサー基板サンドイッチ＋カップ耳高さ $5.50\text{ mm}$ 段付き穴）＝ **全 14箇所すべてを共通の M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\text{ mm}$、計 14個、PCB穴径 $\varnothing 3.30\text{ mm}$）** と上下 M2 × 4.0mm ネジ（28本、ボス上面〜ザグリ天井のクランプ肉厚は全14箇所とも $2.40\text{ mm}$ に統一、スペーサー内のネジ間隙間 $1.50\text{ mm}$）で締結し、さらに右手沈み込み慣性ホイール枠 `#04B`（`wheel-base-frame-sunk.step`）をトッププレート上から M2 × 4.0mm ネジ 3本（`W1`〜`W3`、合計 31本）で吊り下げ固定する仕様を維持すること。
   - モデル更新時は `scripts/generate_inertia_wheel.py` および `scripts/generate_full_assembly.py` を実行し、`cases/assemblies/assembly-full.step`（トッププレート水平基準）と `cases/assemblies/assembly-full-desk.step`（ケース底面＝デスク水平基準、全134パーツ）の双方を出力するとともに、全パーツ間の干渉体積（`overlap_volume`）が `0.00000000 mm³` であることを確認すること。
4. **JLC3DP 発注前チェック・極小隙間（クリアランス不足・狭小スリット）・肉厚 $0.80\text{ mm}$ 未満の自動検証ルール**:
   - 3Dモデル生成時（[`scripts/generate_cases.py`](scripts/generate_cases.py)、[`scripts/generate_trackball_cup.py`](scripts/generate_trackball_cup.py)、[`scripts/generate_full_assembly.py`](scripts/generate_full_assembly.py)）には、干渉体積チェックに加えて以下の3項目を自動検証し、違反が **0件** であることをアサートすること：
     1. **JLC3DP 基本造形ルール（水密多様体・造形サイズ・最小穴径・底面接地）**:
        - 水密・多様体かつ単一ソリッド（`solid.is_valid`, `is_sound(solid)`, `len(solid.solids()) == 1`, `solid.volume > 0`）であること。
        - 造形サイズが JLC3DP MJF/SLS 最小サイズ（$5 \times 5 \times 2\text{ mm}$）以上・最大造形サイズ（$380 \times 284 \times 380\text{ mm}$）以内であり、3Dプリント用モデル（`left-desk`, `right-desk`, `trackball-cup`）の底面が $Z = 0.0000\text{ mm}$ に水平接地していること。
        - すべての凹円筒面（穴・ザグリ・内角R）の直径が JLC3DP MJF/SLS 基準の **$\varnothing 1.50\text{ mm}$ 以上**（未硬化レジン・未焼結パウダー詰まり防止）であること。
     2. **極小隙間の検証（別パーツ間クリアランス & 同一ボディ内の微小隙間）**:
        - 干渉はしていなくても組立困難・清掃不能・製造時の造形トラブルにつながる極小隙間を防止するため、非接触パーツ間（センサーIC・`J1`/`rJ3` コネクタ・裏面SMD部品・USB-Cコネクタ4箇所・ネジ先端 vs ケース内底面・ボス・カップ・プレート等）および JLC3DP 推奨クリアランス（可動部 $\ge 0.30\text{ mm}$、静的嵌合部 $\ge 0.20\text{ mm}$）が規定閾値以上であることを `closest_points` で自動検証すること。
        - ケース内壁に近接する円筒ボス（右手 `R4, R5, TB1, TB3, TB4`、左手 `L4, L5`）は隣接内壁へU字・コーナーブリッジで直結・一体化させ、清掃不能な狭小隙間を残さないこと。また、小指側のメイン基板受けリブは下端を床面下（$Z = -8.50\text{ mm}$）まで延長して傾斜床と完全融合させ、微小アンダーカット隙間を作らないこと。
     3. **肉厚 $0.80\text{ mm}$ 未満の検証（確定除外箇所を除く）**:
        - 3Dプリント発注対象の3モデル（`left-desk.step`, `right-desk.step`, `trackball-cup.step`）について、OpenCascade `BRepExtrema_DistShapeShape` により全非隣接面ペア距離（$0.001 < d < 0.80\text{ mm}$）を自動走査し、**以下の意図的な確定除外箇所（ホワイトリスト）以外の $0.80\text{ mm}$ 未満箇所が 0件** であることを検証すること：
          - **左右ケース（`left` / `right`）の除外箇所**:
            - ① ケース上端フチ（$Z = 0.00\text{ mm}$）：壁厚 $1.50\text{ mm}$ に対する外周 $R = 0.95\text{ mm}$ フィレット残りの水平天面幅（$0.550\text{ mm}$、およびコーナー部の斜め距離 $0.629 \sim 0.743\text{ mm}$）。
            - ② 小指側内底面の水平スキム面（$Z = -8.00\text{ mm}$, $|X_{\text{step}}| \ge 132.81\text{ mm}$）と傾斜床／内角フィレット／小指リブ内面との境界段差（$0.459 \sim 0.549\text{ mm}$）、および `R3`/`L3` ボス天面（$Z = -9.10\text{ mm}$）が傾斜床から出る段差高さ（$0.746\text{ mm}$）。
            - ※北・南・親指内壁のメイン基板受けリブ先端垂直面高さは **$0.85\text{ mm}$**（$Z = -5.80 \sim -6.65\text{ mm}$）を維持し、$0.80\text{ mm}$ 未満としないこと。
          - **トラックボールカップ（`trackball-cup`）の除外箇所**:
            - ① グループA（約 $0.355\text{ mm}$、$Z_{\text{rel}} \in [7.0, 8.8]\text{ mm}$）：$\varnothing 2.00\text{ mm}$ セラミック支持球3箇所のスナップイン抜け止めリップ（入口 $\varnothing 1.95\text{ mm}$）。
            - ② グループB（$0.450\text{ mm}$、$Z_{\text{rel}} = 3.90\text{ mm}$）：固定耳4箇所（外径 $\varnothing 6.00\text{ mm}$、実外壁厚 $1.35 \sim 1.80\text{ mm}$）内部の段付き穴における下段 $\varnothing 3.30\text{ mm}$ スペーサー穴と上段 $\varnothing 2.40\text{ mm}$ M2ネジ穴の半径差（座面段差）。
            - ③ グループC（$0.650\text{ mm}$、$Z_{\text{rel}} \in [4.80, 5.55]\text{ mm}$）：固定耳天面（$Z_{\text{rel}} = 5.50\text{ mm}$）とレンズポケット天井面（$Z_{\text{rel}} = 4.85\text{ mm}$）のZ座標差（実際の覗き窓フチの天井鉛直肉厚は最薄部でも $1.24\text{ mm}$）。
            - ④ グループD（$0.700\text{ mm}$、$Z_{\text{rel}} \in [21.0, 22.8]\text{ mm}$）：ボール保持爪3箇所の上端導入面取りエッジ。

---

## 5. AI 監査・レビュー時の誤認防止ルール（確定設計仕様の根拠）

過去に AI 監査で誤認（フォールスポジティブ）が発生した以下の項目については、実部品・データシート・上流 OSS に基づく確定仕様であるため、再度の誤指摘や誤った改変を行わないこと：

1. **`PMW3360` / `LM19-LSI` の基板角穴（$16.90 \times 8.70\text{ mm}$）とガイドポスト位置**:
   - スクリプト内のプロシージャル生成モデルではなく、常に実フットプリント [`PMW3360DM-T2QU_16Pin.kicad_mod`](pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)（[`monkeypad/pmw3360-breakout`](https://github.com/monkeypad/pmw3360-breakout) / [`siderakb/pmw3360-pcb`](https://github.com/siderakb/pmw3360-pcb) 準拠）および実基板 `curcur40-right.kicad_pcb` を正とする。
   - 実部品の丸ガイドポスト穴は非対称配置（センサー中心基準で $(-7.10, +3.30)\text{ mm}$ および $(+6.70, -3.40)\text{ mm}$、穴径 $\varnothing 1.70\text{ mm}$）であり、$16.90 \times 8.70\text{ mm}$（$\pm 8.45 \times \pm 4.35\text{ mm}$）の基板角穴の内側に余裕をもって収まる。
2. **沈み込みパッシブ磁気慣性ホイール（`#04B` 枠 ＋ `#20` ツインカバー ＋ `#07` `AS5600` 3.3V 回路）の確定仕様**:
   - **ケース底面ボス不要のプレート吊り下げ構造**: `#04B`（[`wheel-base-frame-sunk.step`](cases/inertia_wheel/wheel-base-frame-sunk.step)）は3本の一体型樹脂ポスト（外径 $\varnothing 3.40\text{ mm}$、セルフタップ穴 $\varnothing 1.75\text{ mm}$）が右メイン基板の $\varnothing 3.70\text{ mm}$ 逃げ穴（`W1`〜`W3`）を通過して右トッププレート裏面（$Z = -3.60\text{ mm}$）へ密着し、上から M2 × 4.0mm ネジ 3本で締結される。クリック荷重はキー押下と同じくプレート→外周スペーサー（`R1`/`R2`）へ流れ、磁石〜`AS5600` 間距離はキャリッジ内で完結するため（トラックボールのレンズ距離のようにケース基準で保持する必要がない）、ケース側（`right-desk.step`）は無改造で $3.65\text{ mm}$ 以上の底面クリアランスを確保しており、ケース床面にホイール用ボスを追加してはならない（プレート側ネジ締結との二重拘束になるため）。
   - **`#20` ホイールカバー（[`wheel-cover.step`](cases/inertia_wheel/wheel-cover.step)）の $180^\circ$ 対称共用・外形・位置決め・揺動逃げ**: 西側（`#07` センサー基板格納）と東側のカバーは同一形状の `wheel-cover.step` を $180^\circ$ 水平回転させて共用する確定仕様である。以下を `generate_inertia_wheel.py` で自動検証しており、改変時も維持すること：
     - 軸方向から見たカバー側面シルエットは $\varnothing 16.80\text{ mm}$ ホイール外形より **$0.30\text{ mm}$ 以上内側**（現状 $0.48\text{ mm}$）に収め、上から見てもホイールからはみ出さないこと。
     - スナップ脚（幅 $1.34\text{ mm}$）はプレートのスナップ窓（幅 $1.54\text{ mm}$）で左右 **$\pm 0.10\text{ mm}$** に位置決めし、カバー〜ホイール間隙間は公称 $0.40\text{ mm}$（遊び最大時も $\ge 0.30\text{ mm}$）とすること。
     - カバー内部の逃げ形状は、キャリッジ揺動の全ストローク（静止 $0^\circ$ 〜 ストライカーが `#10` スイッチ本体に当たる $2.34^\circ$）を掃引した軸受丸耳・磁石・`AS5600`・`#07` 基板の包絡で作り、可動部とカバー（遊び込み）・トッププレート・メイン基板の隙間を全ストロークで $\ge 0.30\text{ mm}$ に保つこと（クリック揺動スイープ検証）。
     - `< 0.80 mm` 面ペアのホワイトリストはカバー底面より下のスナップ脚・面取り・ラッチ爪（`30` 面ペア）のみとし、ドーム本体（外装・逃げ形状）には `< 0.80 mm` 面ペアを作らないこと。
   - **`AS5600-ASOT` の 3.3V 単一電源結線**: `#07` [`curcur40-wheel-sensor`](pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_sch) において `U1` (`AS5600-ASOT`) の Pin 1 (`VDD5V`) と Pin 2 (`VDD3V3`) をともに `+3V3` へ直結しているのは、ams OSRAM 公式データシートの **3.3V Operation Mode**（内部 LDO バイパス規定）に厳密準拠した確定回路である。
3. **トラックボールカップ固定耳（`TB1`〜`TB4`）の高さ $5.50\text{ mm}$ 段付き穴とセンサー基板サンドイッチ・スペーサー貫通構造**:
   - `TB1`〜`TB4` のケース円筒ボス天面は **$Z = -17.60\text{ mm}$**（ネジ貫通穴 $\varnothing 2.40\text{ mm}$、クランプ肉厚 $2.40\text{ mm}$）であり、その上に **M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\text{ mm}$、$Z = -17.60 \sim -12.10\text{ mm}$）** と **センサーサブ基板 `curcur40-pmw3360`（板厚 $1.60\text{ mm}$、$Z = -17.60 \sim -16.00\text{ mm}$、貫通穴 $\varnothing 3.30\text{ mm}$）** が同時に着座し、上からトラックボールカップ底面（$Z = -16.00\text{ mm}$）でセンサー基板をサンドイッチする。
   - カップ固定耳（全高 $5.50\text{ mm}$、$Z_{\text{rel}} = 0.00 \sim +5.50\text{ mm}$ / $Z = -16.00 \sim -10.50\text{ mm}$）の内部は、下段 $3.90\text{ mm}$（$Z_{\text{rel}} = 0.00 \sim +3.90\text{ mm}$）がスペーサー進入を受ける **$\varnothing 3.30\text{ mm}$ ソケット穴**、上段 $1.60\text{ mm}$（$Z_{\text{rel}} = +3.90 \sim +5.50\text{ mm}$）がネジ頭およびスペーサーを止める **$\varnothing 2.40\text{ mm}$ ネジ貫通穴** の段付き構造である（上下の M2 × 4.0mm ネジ先端間に $1.50\text{ mm}$ の安全隙間を確保）。
4. **外周 10箇所（`L1`〜`L5`, `R1`〜`R5`）の $5.50\text{ mm}$ スペーサー・メイン基板保持・傾斜底面＋円筒ボスケース構造**:
   - 外周 10箇所（`L1`〜`L5`, `R1`〜`R5`）では、ケース円筒ボス天面（$Z = -9.10\text{ mm}$）から立った $5.50\text{ mm}$ スペーサー（$3.30 + 1.60 + 0.60 = 5.50\text{ mm}$）がメイン基板の $\varnothing 3.30\text{ mm}$ 穴を通過してトッププレート下面（$Z = -3.60\text{ mm}$）を直接支持する。メイン基板はトッププレートに嵌合したキースイッチ（左21個・右19個）とホットスワップソケットにより一体保持される。
   - ケース外底面は小指側外端（$Z = -10.00\text{ mm}$）から親指側内端（$Z = -26.90\text{ mm}$）へ約 $7.47^\circ$ 傾斜するビルトインテンティング構造であり、内底面も外底面と平行な肉厚 $2.40\text{ mm}$ の傾斜面（小指端のみ $Z = -8.00\text{ mm}$ 水平スキム）と円筒ボス台座で構成されている。
5. **Kailh Choc V2 スイッチのプレート厚（$1.60\text{ mm}$）・開口（$14.0 \times 14.0\text{ mm}$）と旧 $\varnothing 0.40\text{ mm}$ 穴**:
   - Kailh Choc V2（`CPG1353`）のラッチ溝高さは $1.65\text{ mm}$、ハウジング幅は $13.80 \times 13.80\text{ mm}$ であり、板厚 $1.60\text{ mm}$ の FR-4 トッププレートおよび $14.0 \times 14.0\text{ mm}$ 開口（Corne V4 準拠）に適合する。
   - `keyswitch_choc12_hotswap_1u` の `(-5.0, -5.15)` にあった $\varnothing 0.40\text{ mm}$ NPTH 穴は、Corne V3 のスイッチ回り止め樹脂ピン穴（$1.5 \times 2.0\text{ mm}$）を Corne V4 で配線通過のために縮小した残骸であったため削除済み。
