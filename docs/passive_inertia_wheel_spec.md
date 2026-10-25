# パッシブ磁気慣性ホイールモジュール 設計仕様書（`curcur40-inertia-wheel`）

本書は、電磁クラッチ（ラチェット ⇔ フリースピン切替用のソレノイド・コイル・駆動回路）をあえて持たず、**「高比重ステンレス削り出しホイール × 脱脂ミニチュアベアリング × 渦電流ゼロの非接触磁気ラチェット」** のみによって **『普段は心地よいノッチ感があり、弾けば微振動を伴いながら慣性で回り続け、指で触れればピタッと止まる』** 高速スクロールホイールモジュールの確定設計・試作データ仕様書です。

> [!IMPORTANT]
> **確定した基本設計方針（シンプル・高信頼・省スペース）**
> 1. **単体試作先行 → `curcur40-right` Rev2 統合**: まずは単体 USB-C デスクトップ試作機（`Waveshare RP2040-Zero` キャリア基板 ＋ ホイールモジュール ＋ 専用3Dプリントスタンド）として製作・調整し、その後 `curcur40-right` Rev2（基板外形・プレート・ケース変更なし、`+3.3V` ＆ `I2C` コネクタのみ追加）へそのまま組み込める構造とします。
> 2. **電磁アクチュエータ＆変換マイコン全廃**: ソレノイド・巻線コイル・Hブリッジドライバ・変換用サブマイコン・`+5V` 電源配線をすべて廃止し、クラッチ消費電流 **`0.0 mA`**・故障箇所最小の純パッシブ機構とします。
> 3. **シルバー金属外観 ＋ Oリング着脱 2way 対応（$\varnothing 16.80\,\text{mm}$ `SUS304`）**: 既存のトッププレート開口（`18.20 × 18.20 mm`）を無改造で通過する $\varnothing 16.80 \times 5.60\,\text{mm}$ 非磁性ステンレス削り出しホイール（質量 **$7.96\,\text{g}$**）とし、普段は金属むき出しで美しく使え、好みで市販Oリングも装着できる 2way 外周溝を設けます。
> 4. **静音ミドルクリック標準搭載（一体揺動キャリッジ）**: `Kailh Square Silent (6.2 × 6.2 × 4.3 mm)` 静音スイッチを採用し、高速回転を指で止めた際に誤クリックせず、押し込み中も磁気ギャップが一切変化しない一体揺動構造とします。

---

## 1. 全体構造と空間パッケージング（`18.0 × 18.0 mm` 枠内完結・干渉ゼロ検証済み）

![Passive Magnetic Inertia Wheel Architecture](assets/passive_inertia_wheel_spec.png)

### 1.1 3D CAD / KiCad PCB プレビューギャラリー

| `SUS304` ホイール単体 (`7.96 g`) | ホイールモジュール単体 (24パーツ) |
| :---: | :---: |
| ![SUS304 Flywheel](assets/render_inertia_wheel_flywheel.png) | ![Inertia Wheel Module](assets/render_inertia_wheel_module.png) |
| **単体デスクトップ評価ポッド (`RP2040-Zero`)** | **無改造 `curcur40-right` 搭載検証 (`overlap = 0.000 mm³`)** |
| ![Eval Pod Assembly](assets/render_inertia_wheel_eval_pod.png) | ![curcur40-right Integration](assets/render_curcur40_right_inertia_wheel.png) |
| **`AS5600` センサーサブ基板 (`8.8 × 8.8 × 0.8 mm`)** | **単体評価キャリア基板 (`48.0 × 32.0 × 1.6 mm`)** |
| ![Wheel Sensor PCB](assets/render_pcb_wheel_sensor.png) | ![Wheel Eval PCB](assets/render_pcb_wheel_eval.png) |

### 1.2 `curcur40-right` 既存スペースとの整合性（実STEPモデル干渉検証結果）

| 項目 | 現行 `curcur40` 寸法・座標 | 本モジュール確定設計値 | 3D CAD 実測判定 |
| :--- | :---: | :---: | :--- |
| **モジュール平面枠** | `CKW12` 枠: $18.00 \times 18.00\,\text{mm}$ | **$17.60 \times 17.60\,\text{mm}$** ($\pm 8.80\,\text{mm}$) | **横方向はみ出し完全ゼロ** |
| **トッププレート開口** | $18.20 \times 18.20\,\text{mm}$ ($R=0.5\,\text{mm}$) | 静的クリアランス **$0.217\,\text{mm}$** ／ 可動部 **$0.330\,\text{mm}$** | **既存プレート無改造でそのまま通過** |
| **ホイール頂点高さ ($Z$)** | `CKW12`: $+8.88\,\text{mm}$ ／ `25mm` 球: $+14.80\,\text{mm}$ | **$Z = +14.50\,\text{mm}$**（軸中心 $Z = +6.10\,\text{mm}$） | トラックボール頂点以下で自然な指移動 |
| **南側キー (`rEXSW2`) 余裕** | キャップ北端 $Y = +10.45\,\text{mm}$ | ホイール南端 $Y = +8.30\,\text{mm}$ | **$2.150\,\text{mm}$ の安全な指先クリアランス** |
| **全パーツ間干渉体積** | [`cases/right.step`](../cases/right.step)（無改造） | **`overlap_volume = 0.00000000 mm³`**（全48パーツ） | **既存ケース・プレートを100%無改造で利用可能** |

---

## 2. コア機構設計（慣性・渦電流対策・磁力調整・静音クリック）

### 2.1 ホイール本体：`SUS304` シルバー削り出し（2way 外周仕上げ）
* **材質**: 非磁性オーステナイト系ステンレス **`SUS304`**（比重 **$7.93\,\text{g/cm}^3$**）。
  * 体積 **$1003.9\,\text{mm}^3$**、単体質量 **$7.96\,\text{g}$**（アルミホイールの約3倍、樹脂製 `CKW12` ホイールの約8倍以上の慣性モーメント）を持ち、サビや変色が起きない上質なシルバー切削外観を維持します。
* **MX Master 3S 風「2way 外周プロファイル」**:
  * 外周（外径 $\varnothing 16.80 \times$ 幅 $5.60\,\text{mm}$）には、金属むき出し（ゴムなし）の状態で指がしっかり掛かる **36本の横溝（フルート加工）** と、中央を走る **幅 $1.30\,\text{mm} \times$ 深さ $0.50\,\text{mm}$ のセンターアクセント溝** を加工しています。
  * **標準状態（金属むき出し）**: Logitech MX Master 3S のような精悍な削り出しシルバーホイールとしてそのまま機能します。
  * **高グリップ状態（オプション）**: センター溝に市販の極細シリコン／ニトリルOリング（内径 $\varnothing 15.0 \times$ 線径 $1.0\,\text{mm}$）を嵌めると、外周から $+0.5\,\text{mm}$ だけラバーが顔を出して指への吸い付きを強化でき、いつでも着脱できます。

### 2.2 「渦電流ブレーキ完全ゼロ ＆ JLC3DP 造形基準準拠」の絶縁11球・磁気ラチェット構造
* **なぜ金属ホイールに直接磁石を当てないのか**:
  * 導電体である金属ホイール（や金属一体ギヤ）に強い磁石を直接近づけて高速回転させると、金属内部に渦電流が流れて強力な電磁ブレーキ（アラゴーの円盤現象）が発生し、1秒足らずで回転が止まってしまいます。
* **解決策（絶縁SLAハブ $\varnothing 12.40 \times 3.75\,\text{mm}$ ＋ 独立 $\varnothing 2.00\,\text{mm}$ 鋼球 × 11個）**:
  * `SUS304` ホイール本体の東隣（$X_{\text{mod}} = +2.35 \sim +6.10\,\text{mm}$）に、非導電性 **SLA レジン製ラチェットハブ（外径 $\varnothing 12.40 \times$ 幅 $3.75\,\text{mm}$）** を同軸配置し、軌道半径 $R = 5.10\,\text{mm}$ の11箇所のスナップインポケット（入口径 $\varnothing 1.94\,\text{mm}$）に **市販の $\varnothing 2.00\,\text{mm}$ 精密鋼球（`SUJ2` ベアリング球）を11個（$32.73^\circ$ 刻み）** 圧入します。
  * $\varnothing 2.00\,\text{mm}$ 球を採用したことで、JLC3DP の最小穴径基準（**全凹穴 $\ge \varnothing 1.50\,\text{mm}$**）とポケット間最小肉厚基準（**$0.814\,\text{mm} \ge 0.80\,\text{mm}$**）を完全クリアし、ピンセット不要で手作業でも簡単にスナップイン組立できます。
  * 隣り合う鋼球同士が樹脂で完全に電気絶縁されているため **高速回転時の渦電流損失がゼロ** になり、弾いたときに「トトトトト…」という心地よい微振動を伝えながらスーーッと伸びやかに回り続け、止まった瞬間も振動の消失で指先にすぐ分かります。

### 2.3 分解不要の「北東 M2ネジ磁力（ノッチ感 ⇔ 空転伸び）無段階調整」
* インナーキャリッジ北東部（$X_{\text{mod}} = +4.525\,\text{mm}, Z_{\text{mod}} = +5.65\,\text{mm}$）に保持したラチェット用ネオジム磁石（$\varnothing 2.0 \times 1.5\,\text{mm}$, `N35`）の背面に、**M2 ステンレス調整ネジ（ピッチ $0.40\,\text{mm}$/回転）** を配置しています。
* 組み立てた後からでも北側から精密ドライバー／六角レンチ1本で磁石ギャップ $g$ を $0.15\,\text{mm} \sim 1.20\,\text{mm}$ の間で微調整できるため：
  * **ネジを少し締める（$g \approx 0.20\,\text{mm}$）**: 1ノッチごとのコリコリ感がはっきりした精密ラチェット寄り
  * **標準位置（$g \approx 0.35 \sim 0.45\,\text{mm}$）**: 適度なノッチ振動と 3〜7秒の気持ちよい慣性スピンの両立
  * **ネジを緩める（$g \ge 1.0\,\text{mm}$）**: ほぼ無抵抗のロングフリースピン
  を自分の指の感覚に合わせていつでも追い込めます。

### 2.4 静音ミドルクリック機構（スピン停止時の誤クリック防止設計）
* **一体揺動インナーキャリッジ**:
  * 北端ヒンジピン（$\varnothing 2.00\,\text{mm}$ `SUS304` 平行ピン、$Y_{\text{mod}} = -6.85\,\text{mm}, Z_{\text{mod}} = +2.15\,\text{mm}$）を支点として、`{ホイール ＋ 脱脂ベアリング2個 ＋ AS5600センサー基板 ＋ 11球ラチェット＆調整磁石}` を載せたキャリッジ全体が一体で揺動します。
  * ミドルクリックを押し込んでも **磁石とロータ、および角度センサーの相対距離は $0.000\,\text{mm}$ もズレない** ため、クリック時の誤スクロールや部品接触が原理的に起きません。
* **静音マイクロスイッチ ＆ 誤爆防止レバー配置**:
  * 南東コーナー（$(+5.70, +5.70)\,\text{mm}$）に静音角形マイクロスイッチ **`Kailh Square Silent Micro Switch (6.2 × 6.2 × 4.3 mm, Red Dot 荷重 0.74N)`** を配置しています。
  * 「コトッ」と静かで上品な押し心地でありながら、**高速スピン中のホイールを指の腹でサッと触れて止めるとき（接触荷重 $30 \sim 60\,\text{gf}$）にはミドルクリックが暴発しない** 適切な押下荷重を確保しています。

---

## 3. 製造・試作データ一式（Phase 2 成果物・全自動検証合格済み）

### 3.1 3D CAD モデル（[`cases/inertia_wheel/`](../cases/inertia_wheel/) ＆ [`cases/assemblies/`](../cases/assemblies/)）
生成・検証スクリプト：[`scripts/generate_inertia_wheel.py`](../scripts/generate_inertia_wheel.py)

| ファイル | 用途・発注プロセス | 外形寸法 [mm] | 検証結果 |
| :--- | :--- | :---: | :--- |
| [`sus304-flywheel.step`](../cases/inertia_wheel/sus304-flywheel.step) / `.stl` | JLCCNC `SUS304` 切削ホイール本体 (`7.96 g`) | $16.77 \times 16.77 \times 5.60$ | 水密単一ソリッド・最小穴径 $1.60\,\text{mm}$ **PASS** |
| [`ratchet-hub-11ball.step`](../cases/inertia_wheel/ratchet-hub-11ball.step) / `.stl` | JLC3DP SLA 絶縁11球ラチェットハブ | $12.40 \times 12.40 \times 3.75$ | 最小穴径 $1.94\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-carriage.step`](../cases/inertia_wheel/wheel-carriage.step) / `.stl` | JLC3DP SLA 一体揺動インナーキャリッジ | $13.57 \times 17.32 \times 16.70$ | 最小穴径 $1.76\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-base-frame.step`](../cases/inertia_wheel/wheel-base-frame.step) / `.stl` | JLC3DP SLA モジュール固定ベース枠 | $17.60 \times 17.60 \times 4.10$ | 最小穴径 $2.06\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`eval-pod-stand.step`](../cases/inertia_wheel/eval-pod-stand.step) / `.stl` | JLC3DP SLA/MJF 単体評価ポッド台座 | $52.00 \times 36.00 \times 6.60$ | 最小穴径 $2.00\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`inertia-wheel-module-assembly.step`](../cases/assemblies/inertia-wheel-module-assembly.step) | モジュール単体検証アセンブリ (24パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`inertia-wheel-eval-pod-assembly.step`](../cases/assemblies/inertia-wheel-eval-pod-assembly.step) | 単体デスクトップ評価ポッド検証 (28パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`curcur40-right-with-inertia-wheel.step`](../cases/assemblies/curcur40-right-with-inertia-wheel.step) | 無改造 `curcur40-right` 搭載検証 (48パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |

### 3.2 KiCad 10.0 回路図・基板・JLCPCB 発注ファイル
JLCPCB 出力・自動プリフライトスクリプト：[`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py)

1. **`AS5600` センサーサブ基板（[`pcbs/inertia-wheel-sensor/`](../pcbs/inertia-wheel-sensor/)）**:
   * 外形 **$8.80 \times 8.80\,\text{mm}$**（2層 FR-4、推奨板厚 **$0.80\,\text{mm}$**）。
   * 表面（`F.Cu`）：`U1 AS5600-ASOT`（LCSC `C499458`、3.3V直結モード）。裏面（`B.Cu`）：`C1 100nF`（`C1525`）、`C2 1uF`（`C52923`）、`J1` 4極極細配線パッド（`+3V3, GND, SDA, SCL`）。
   * **ERC エラー `0` / 警告 `0`**、**DRC 違反 `0` / 未接続 `0` / 回路図不一致 `0`**。
   * 発注ファイル：[`GERBER-curcur40-wheel-sensor.zip`](../pcbs/inertia-wheel-sensor/jlcpcb/production_files/GERBER-curcur40-wheel-sensor.zip)、[`BOM-curcur40-wheel-sensor.csv`](../pcbs/inertia-wheel-sensor/jlcpcb/production_files/BOM-curcur40-wheel-sensor.csv)、[`CPL-curcur40-wheel-sensor.csv`](../pcbs/inertia-wheel-sensor/jlcpcb/production_files/CPL-curcur40-wheel-sensor.csv)。
   * *(注：JLCPCB 単体PCBA最小寸法は $20 \times 20\,\text{mm}$ のため、生基板発注＋手ハンダ、またはパネル面付けPCBAに対応)*
2. **単体 USB-C 評価キャリア基板（[`pcbs/inertia-wheel-eval/`](../pcbs/inertia-wheel-eval/)）**:
   * 外形 **$48.00 \times 32.00\,\text{mm}$**（2層 FR-4、板厚 **$1.60\,\text{mm}$**、単体PCBA最小寸法 $20 \times 20\,\text{mm}$ 準拠）。
   * 表面実装（JLCPCB PCBA対応）：`J1 SM06B-SRSS-TB(LF)(SN)`（`curcur40` トラックボール基板と同一の JST SH 6ピン横型コネクタ、LCSC `C160405`）、`R1/R2 4.7kΩ` I2C プルアップ（`C25900`）、`C1 100nF`（`C1525`）。
   * 手実装モジュール・スイッチ：`U1 Waveshare RP2040-Zero`（西側端面スルーホール／端面半田対応）、`SW1 Kailh Square Silent 6.2×6.2×4.3mm`（東側モジュール搭載エリア内の南東クリック位置に直付け）、`J2` センサー配線直結4パッド、M2 固定穴 `H1..H6`（台座固定4箇所＋モジュール固定2箇所）。
   * **ERC エラー `0` / 警告 `0`**、**DRC 違反 `0` / 未接続 `0` / 回路図不一致 `0`**。
   * 発注ファイル：[`GERBER-curcur40-wheel-eval.zip`](../pcbs/inertia-wheel-eval/jlcpcb/production_files/GERBER-curcur40-wheel-eval.zip)、[`BOM-curcur40-wheel-eval.csv`](../pcbs/inertia-wheel-eval/jlcpcb/production_files/BOM-curcur40-wheel-eval.csv)、[`CPL-curcur40-wheel-eval.csv`](../pcbs/inertia-wheel-eval/jlcpcb/production_files/CPL-curcur40-wheel-eval.csv)。

### 3.3 単体評価用 QMK ファームウェア（[`kbd_firmware/keyboards/curcur40_wheel_eval/`](../kbd_firmware/keyboards/curcur40_wheel_eval/qmk/qmk_firmware/)）
* **ターゲットマイコン**: `RP2040`（`Waveshare RP2040-Zero`, `I2CD0`: `SDA=GP4`, `SCL=GP5` @ `400 kHz`, ミドルクリック `SW1=GP6` -> `MS_BTN3`）。
* **カスタムポインティングドライバ（[`wheel_eval.c`](../kbd_firmware/keyboards/curcur40_wheel_eval/qmk/qmk_firmware/rev1/wheel_eval.c)）**:
  * `AS5600` の 12-bit `RAW ANGLE`（`0..4095`）を `1 kHz` でポーリングし、モジュロ `4096` のラップアラウンド差分計算により `20 rev/s` 超の高速フリックでも取りこぼしゼロで追従します。
  * 静止時の微小磁気ノイズを完全に遮断するデッドバンドヒステリシス（`WHEEL_DEADBAND_LSB = 6`、約 $0.53^\circ$）と、1周あたり出力ステップ数のプリセット変更（`WHEEL_NOTCHES_PER_REV = 11 / 22 / 36`、既定値 `22`）、`Shift` キー押下時の水平スクロール自動切替、および JST SH ケーブル活線挿抜（未接続時もミドルクリックやUSB通信が一切ブロックしない自動再接続）を備えています。

---

## 4. 入手可能な実部品リスト（BOM ＆ 概算コスト）

特殊な海外専用部品や手巻きコイルを排除し、すべて **JLCCNC / JLC3DP / JLCPCB / LCSC / Amazon・国内通販** で簡単に揃う汎用品で構成しています。

| 分類 | 部品名・型番 | 仕様・寸法 | 主な入手先 / コード | 単価目安 (1台分) |
| :--- | :--- | :--- | :--- | :---: |
| **ホイール本体** | 特注ステンレスホイール (`SUS304`) | $\varnothing 16.80 \times 5.60\,\text{mm}$ ($7.96\,\text{g}$), シルバー切削 | JLC3DP (JLCCNC 切削: `sus304-flywheel.step`) | 約 \$6.00 (¥900) |
| **ベアリング (×2)** | ミニチュアステンレスベアリング<br>**`DDL-520` / `MR52`**（脱脂使用） | 内径 $\varnothing 2.0 \times$ 外径 $\varnothing 5.0 \times$ 幅 $2.5\,\text{mm}$ × 2個<br>*(シールドを外しパーツクリーナーでグリス除去)* | Amazon / MonotaRO / ラジコン店<br>*(ミネベア `DDL-520` 等)* | 約 \$2.60 (¥400 / 2個) |
| **ラチェット鋼球** | 精密ベアリング鋼球 (`SUJ2`) | **$\varnothing 2.00\,\text{mm}$** × 11個使用（`curcur40` 支持球と同径サイズ帯） | Amazon / MonotaRO (`2mm SUJ2 鋼球`) | 約 \$1.50 (¥230 / 100個) |
| **シャフト・ピン** | 非磁性ステンレス平行ピン (`SUS304`/`316`) | ホイール軸 $\varnothing 2.0 \times 15\,\text{mm}$ ×1、ヒンジ軸 $\varnothing 2.0 \times 17\,\text{mm}$ ×1 | Amazon / ミスミ / MonotaRO (`Ø2.0mm` に統一) | 約 \$1.00 (¥150) |
| **磁力調整ネジ** | M2 ステンレス小ねじ / ホーローセット | `M2 × 5〜6 mm`（北東磁力ギャップ調整用） | ホームセンター / Amazon (`curcur40` ネジ流用可) | 約 \$0.20 (¥30) |
| **角度センサーIC** | ams OSRAM **`AS5600-ASOT`** | `SOIC-8`, 12-bit I2C 非接触磁気角度センサー | **LCSC `C499458`** / 秋月電子 / Amazon | 約 \$1.10 (¥170) |
| **センサー用磁石** | 径方向2極着磁（Diametric）NdFeB磁石 | $\varnothing 3.0 \times 1.0 \sim 1.5\,\text{mm}$ (`N35`、軸端回転検出用) | AliExpress / Amazon / マグネット専門店 | 約 \$0.50 (¥80) |
| **ラチェット磁石** | 軸方向着磁 小型ネオジム磁石 | $\varnothing 2.0 \times 1.5\,\text{mm}$ (`N35`、ノッチ生成用) | Amazon / ハイキューパーツ / 極小磁石 | 約 \$0.30 (¥50) |
| **静音クリックSW** | **`Kailh Square Silent 6.2×6.2×4.3mm`** | 静音角形マイクロスイッチ（Red Dot, $0.74\,\text{N}$） | 遊舎工房 / Amazon / AliExpress | 約 \$0.35 (¥55) |
| **コネクタ** | JST SH 6ピン横型 **`SM06B-SRSS-TB`** | `curcur40` トラックボール基板と完全同一型番 | **LCSC `C160405`** | 約 \$0.15 (¥25) |
| **Oリング (任意)** | 極細シリコン / NBR Oリング | 内径 $\varnothing 15.0 \times$ 線径 $1.0\,\text{mm}$（2way グリップ比較用） | Amazon / MonotaRO | 約 \$0.20 (¥30) |
| **樹脂筐体パーツ** | ベース枠 ＋ キャリッジ ＋ 11球ハブ (＋台座) | 高精度 SLA レジン造形（モジュール3点＋評価台座1点） | JLC3DP SLA (`8001` / `Imagine Black` 等) | 約 \$3.00 (¥450) |
| **単体評価キャリア** | **`Waveshare RP2040-Zero`** ＋ 評価基板 | Stage 1 単体 USB-C テストベッド (`48 × 32 mm`) | Amazon / JLCPCB | 約 \$3.50 (¥530) |
| **合計（概算）** | ― | **ホイールモジュール単体 約 ¥2,570** ＋ 単体評価キャリア 約 ¥530 | ― | **約 ¥3,100** |
