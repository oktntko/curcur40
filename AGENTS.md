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
   - 設計の正は以下の4つのドキュメントである。対象領域の作業を行う前に必ず該当ドキュメントを確認すること。
     - ケース・プレート・トラックボールカップ仕様: [`docs/case_spec.md`](docs/case_spec.md)
     - PCB・回路図・ライブラリ・スクリプト格納仕様: [`docs/pcb_spec.md`](docs/pcb_spec.md)
     - ビルドガイド・BOM・発注仕様: [`docs/buildguide_jp.md`](docs/buildguide_jp.md)
     - プロジェクト概要・3Dプレビューギャラリー: [`README.md`](README.md)
   - エラーや警告を回避するためだけに無理やり不要な配線を追加したり、DRC/ERC ルールを無効化するような対症療法は絶対に行わないこと。

---

## 2. ディレクトリ構成とファイル管理ルール

1. **一時ファイル・使い捨てスクリプトの残置禁止**:
   - `scratch/` や `tmp/`、ルート直下の `.json` / `.rpt` / `.net` / `.bak` / `.kicad_prl` 等を作業後にリポジトリへ残さないこと。
   - スクリプト内で DRC/ERC レポートや Gerber 一時ファイルを出力する場合は、Python 標準の `tempfile.TemporaryDirectory` を使用して自動削除すること。
2. **公式生成スクリプトの一元管理 (`scripts/`)**:
   - 3Dモデル・プレート・発注データ・図版・プレビュー画像の生成は [`scripts/`](scripts/) 配下の8本の公式スクリプト（詳細は [`scripts/README.md`](scripts/README.md) 参照）に集約し、1回限りの調査・デバッグ用スクリプトを `scripts/` に残さないこと。
   - スクリプト内でワークスペースや入出力パスを参照する際は、`c:\Users\...` 等の環境依存フルパスをハードコードせず、必ずスクリプト自身の位置からの相対解決（`WORKSPACE = Path(__file__).resolve().parent.parent`）で記述すること。
3. **ボトムプレートの作成禁止**:
   - ボトムプレートは 3D プリント製トレイ型ボトムケース（`cases/left.step`, `right.step`）に統合済みのため、生成・出力しないこと。
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
4. **右手基板 (`curcur40-right`) および トラックボールセンサーサブ基板 (`curcur40-pmw3360`) の固有仕様**:
   - トラックボールカップ開口面をトッププレート天面（$Z = -2.00\text{ mm}$）と同じ高さに揃える低プロファイル設計のため、PMW3360 センサー回路は独立サブ基板 [`pcbs/pmw3360/curcur40-pmw3360.kicad_pcb`](pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（$Z = -17.60 \sim -16.00\text{ mm}$）に分離し、右メイン基板 `rJ3` とセンサー基板 `J1` を **JST SH 1.0mm ピッチ 6ピン横向き SMD コネクタ（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160404`）** で接続する。
   - `U1` (`PMW3360DM-T2QU`) の Pin 3 (`VDDPIX`) は内部レギュレータ出力（`power_out`）であるため、外部 1.8V 電源（`/+1V8_PMW`）とショートさせず `C1`/`C2` のみの独立ネット（`Net-(U1-VDDPIX)`）に保つこと。
   - `JP1` は `Jumper:SolderJumper_3_Bridged12`（`SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels`：Pad 1 `+3V3R` – Pad 2 `/V_{IO}` 基板内銅箔直結）を維持すること。
   - `R4` (28kΩ)、`C5` (22nF)、および左右のデバッグ端子 `J4` / `rJ4` は `DNP`（BOM/CPL/3Dモデル除外）を維持すること。
5. **DRC / ERC 合格基準**:
   - `kicad-cli pcb drc --schematic-parity`: 3基板（`left`, `right`, `pmw3360`）すべて **違反 0件・未接続 0件・回路図不一致 0件**。
   - `kicad-cli sch erc`: 左右メイン基板は **エラー 0件、警告 1件**（`RP2040` Pin 32 `GPIO21` と `+3V3` / `GNDR` の左右判定ピン直結による正当な `pin_to_pin` 警告 1件のみを意図的に保持）、センサーサブ基板 `curcur40-pmw3360` は **エラー 0件、警告 0件**。

---

## 4. 3D CAD (`cadgen` / `build123d`) のルール

1. **実行環境**:
   - `& "$env:USERPROFILE\.local\bin\uvx.exe" --no-config --managed-python --python 3.13 --from "cadgen==0.7.21" python`
2. **光学距離基準点 (`Lens_Optical_Ref_Point`) の維持**:
   - 以下の4つの STEP モデルには、GUI（CAD Viewer 等）で直接選択して 25mm ボール（`Trackball_25mm`, 最下面 $Z_{\text{rel}} = +5.80\text{ mm}$ / フルアセンブリ $Z = -10.2000\text{ mm}$）との距離（設計値 **$2.40\text{ mm}$**）を計測できるよう、光軸中心のレンズフランジ着座面（$Z_{\text{rel}} = +3.4000\text{ mm}$ / フルアセンブリ $Z = -12.6000\text{ mm}$）に独立した名前付きオブジェクト **`Lens_Optical_Ref_Point`** を `bd.Compound(children=[...])` の子要素として必ず含めること：
     - `cases/pmw3360-lens-pcb-assembly.step`
     - `cases/trackball-sensor-assembly.step`
     - `cases/trackball-cup-with-ball.step`
     - `cases/assembly-full.step`
3. **14箇所 M2 スペーサー締結構造・ビルトインテンティングケース・干渉ゼロ検証**:
   - 左手外周 5箇所（`L1`〜`L5`）＋ 右手外周 5箇所（`R1`〜`R5`、親指側 `L5`/`R5` は $(\pm 33.3375, 64.3000)$ で完全左右対称）＝ 計 10箇所を M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\text{ mm}$、基板 $\varnothing 3.25\text{ mm}$ 貫通穴を通ってトッププレート下面 $Z = -3.60\text{ mm}$ を直接支持）、トラックボールカップ固定耳 4箇所（`TB1`〜`TB4`）を M2 6.0〜7.0mm メス-メス スペーサー（外径 $\varnothing 3.0\text{ mm}$、センサー基板 $\varnothing 3.25\text{ mm}$ 穴を貫通してカップ耳 $\varnothing 3.60\text{ mm}$ 穴内部へ進入）と上下 M2 × 4.0mm ネジ（計 28本）で締結する仕様を維持すること。
   - モデル更新時は `scripts/generate_full_assembly.py` を実行し、全パーツ間の干渉体積（`overlap_volume`）が `0.00000000 mm³` であることを確認すること。

---

## 5. AI 監査・レビュー時の誤認防止ルール（確定設計仕様の根拠）

過去に AI 監査で誤認（フォールスポジティブ）が発生した以下の項目については、実部品・データシート・上流 OSS に基づく確定仕様であるため、再度の誤指摘や誤った改変を行わないこと：

1. **`PMW3360` / `LM19-LSI` の基板角穴（$16.90 \times 8.70\text{ mm}$）とガイドポスト位置**:
   - スクリプト内のプロシージャル生成モデルではなく、常に実フットプリント [`PMW3360DM-T2QU_16Pin.kicad_mod`](pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)（[`monkeypad/pmw3360-breakout`](https://github.com/monkeypad/pmw3360-breakout) / [`siderakb/pmw3360-pcb`](https://github.com/siderakb/pmw3360-pcb) 準拠）および実基板 `curcur40-right.kicad_pcb` を正とする。
   - 実部品の丸ガイドポスト穴は非対称配置（センサー中心基準で $(-7.10, +3.30)\text{ mm}$ および $(+6.70, -3.40)\text{ mm}$、穴径 $\varnothing 1.70\text{ mm}$）であり、$16.90 \times 8.70\text{ mm}$（$\pm 8.45 \times \pm 4.35\text{ mm}$）の基板角穴の内側に余裕をもって収まる。
2. **`CKW12` ロータリーエンコーダ（`rEXSW1`）の実装構造・ネジ穴・3Dモデル回転角**:
   - **メイン基板にネジ穴がなくて正常**: 公式 [`kumamuk-git/CKW12`](https://github.com/kumamuk-git/CKW12) キットは、付属の専用サブ基板 `CKW12_top`（厚さ約 $0.50\text{ mm}$）の裏側から M2 × 3.5mm ネジ 4本で 3Dプリントハウジング四隅を固定し、`CKW12_top` から下に出たコンスルー 5ピン（`2.54 mm` ピッチ）をメイン基板 `rEXSW1` の 5穴（`A, B, C, S1, S2`）に挿して実装する構造である。メイン基板自体に M2 ネジ穴は不要。
   - **3Dモデルの回転角を 90° 曲げないこと**: `CKW12` のホイールは人差し指で**上下方向（南北方向）に転がす向き**が正しい。`rEXSW1` のスルーホール 5ピンが北側3ピン・南側2ピンに並んでいるのは `CKW12_top` サブ基板内の引き回しによるものであり、フットプリント [`RotaryEncoder_Switch_CKW12.kicad_mod`](pcbs/common/kbd/kicad-footprints/kbd.pretty/RotaryEncoder_Switch_CKW12.kicad_mod) の `(rotate (xyz 0 0 90))`（および [`scripts/generate_full_assembly.py`](scripts/generate_full_assembly.py) の `(0, 0, -90)`）が正しい向きである。
3. **トラックボールカップ固定耳（`TB1`〜`TB4`）の穴径 $\varnothing 3.60\text{ mm}$ とスペーサー貫通構造**:
   - ケース内底面（$Z = -9.10\text{ mm}$）からメイン基板下面（$Z = -5.80\text{ mm}$）までの空間は **$3.30\text{ mm}$**、メイン基板厚は **$1.60\text{ mm}$** であり、メイン基板上面（`F.Cu`, $Z = -4.20\text{ mm}$）までの高さは **$4.90\text{ mm}$** である。
   - したがって、`TB1`〜`TB4` のスペーサー（外径 $\varnothing 3.0\text{ mm}$、長さ $6.0\sim 7.0\text{ mm}$）はメイン基板（$\varnothing 3.25\text{ mm}$ 穴）を貫通して、その上に乗るカップ固定耳（厚さ $2.40\text{ mm}$、$Z = -4.20 \sim -1.80\text{ mm}$）の **$\varnothing 3.60\text{ mm}$ 穴の内部へ下から進入する**。カップ耳の穴径が $\varnothing 2.40\text{ mm}$ ではなく $\varnothing 3.60\text{ mm}$ なのはこのスペーサー進入を受けるための正当な設計である。
4. **外周 9箇所の $5.50\text{ mm}$ スペーサー・メイン基板保持・ケース側壁高さ $9.10\text{ mm}$**:
   - 外周 9箇所（`L1`〜`L5`, `R1`〜`R4`）では、ケース内底面（$Z = -9.10\text{ mm}$）から立った $5.50\text{ mm}$ スペーサー（$3.30 + 1.60 + 0.60 = 5.50\text{ mm}$）がメイン基板の $\varnothing 3.25\text{ mm}$ 穴を通過してトッププレート下面（$Z = -3.60\text{ mm}$）を直接支持する（空中ギャップは存在しない）。メイン基板はトッププレートに嵌合したキースイッチ（左21個・右19個）とホットスワップソケットにより一体保持される。
   - ケース側壁内深さ $9.10\text{ mm}$（全高 $12.30\text{ mm}$、トッププレート天面 $Z = -2.00\text{ mm}$ に対してリム天面 $Z = 0.00\text{ mm}$ が $2.00\text{ mm}$ 高い形状）およびケース底面フラット構造（`BOOT`/`RESET` 用の底面穴を設けない仕様）は確定仕様であり、変更しない。
5. **Kailh Choc V2 スイッチのプレート厚（$1.60\text{ mm}$）・開口（$14.0 \times 14.0\text{ mm}$）と旧 $\varnothing 0.40\text{ mm}$ 穴**:
   - Kailh Choc V2（`CPG1353`）のラッチ溝高さは $1.65\text{ mm}$、ハウジング幅は $13.80 \times 13.80\text{ mm}$ であり、板厚 $1.60\text{ mm}$ の FR-4 トッププレートおよび $14.0 \times 14.0\text{ mm}$ 開口（Corne V4 準拠）に適合する。
   - `keyswitch_choc12_hotswap_1u` の `(-5.0, -5.15)` にあった $\varnothing 0.40\text{ mm}$ NPTH 穴は、Corne V3 のスイッチ回り止め樹脂ピン穴（$1.5 \times 2.0\text{ mm}$）を Corne V4 で配線通過のために縮小した残骸であったため削除済み。
