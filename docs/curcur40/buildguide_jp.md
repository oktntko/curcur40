# curcur40 ビルドガイド — Step 1: 資材一覧と入手経路・発注ガイド

**curcur40** は、Corne Chocolate v4 をベースに全キー 1u 化（計40キー：左21キー＋右19キー）、右手人差し指内側に水平スクロールエンコーダ（**CKW12**）、右手親指上部に **25mm トラックボール（PMW3360 光学センサー）** を統合した左右分割型ロープロファイルキーボードです。

本ドキュメントでは、ビルドガイドの **Step 1** として、製造サービス（**JLCPCB** / **JLC3DP**）へ発注するデータ一覧と、別途購入・調達するパーツ一覧および入手経路をまとめています。

---

## 1. 全体構成の概要

curcur40 を1台組み立てるために必要な資材は、大きく分けて以下の **3つのルート** で揃えます。

1. **JLCPCB への発注（基板製造 ＋ 表面実装 PCBA ＋ FR-4 スイッチプレート）**
   - 左右メイン基板および PMW3360 センサー基板は、マイコン（RP2040）やダイオード、Kailh Choc ソケット、LED、USB-C、TRRS ジャック等の細かい表面実装部品（SMD）がすべて **PCBA（部品実装サービス）用の BOM / CPL ファイル付き** で用意されています。
2. **JLC3DP への発注（3Dプリントケース ＋ トラックボールカップ）**
   - 左右の専用ケースと、25mm トラックボールを保持するカップ（ホルダー）を 3D プリントで造形します。
3. **別途購入するパーツ（スイッチ、キーキャップ、センサーIC、トラックボール球、CKW12、ネジ類など）**
   - PCBA で実装されない手ハンダ部品（`CKW12`、`PMW3360DM-T2QU`、6ピンヘッダ）と、組み立て用の機構部品・外装パーツを国内ショップや通販で揃えます。

---

## 2. JLCPCB に発注するもの（PCB / PCBA / プレート）

JLCPCB（[https://jlcpcb.com/](https://jlcpcb.com/)）には、**PCBA 付き基板 3種** と **PCB のみ（FR-4 プレート）2種** の計5アイテムを発注します。

### 2-1. 発注ファイル一覧

| 対象 | 発注種別 | 最小発注数 | ガーバーファイル (ZIP) | BOM (部品表 CSV) | CPL (座標データ CSV) |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **① 左メイン基板**<br>(`curcur40-left`) | **PCB + PCBA**<br>（裏面 `B.Cu` 実装） | 5枚<br>（PCBAは2枚〜可） | [GERBER-curcur40-left.zip](../../pcbs/curcur40/left/jlcpcb/production_files/GERBER-curcur40-left.zip) | [BOM-curcur40-left.csv](../../pcbs/curcur40/left/jlcpcb/production_files/BOM-curcur40-left.csv) | [CPL-curcur40-left.csv](../../pcbs/curcur40/left/jlcpcb/production_files/CPL-curcur40-left.csv) |
| **② 右メイン基板**<br>(`curcur40-right`) | **PCB + PCBA**<br>（裏面 `B.Cu` 実装） | 5枚<br>（PCBAは2枚〜可） | [GERBER-curcur40-right.zip](../../pcbs/curcur40/right/jlcpcb/production_files/GERBER-curcur40-right.zip) | [BOM-curcur40-right.csv](../../pcbs/curcur40/right/jlcpcb/production_files/BOM-curcur40-right.csv) | [CPL-curcur40-right.csv](../../pcbs/curcur40/right/jlcpcb/production_files/CPL-curcur40-right.csv) |
| **③ PMW3360 センサー基板**<br>(`curcur40-pmw3360`) | **PCB + PCBA**<br>（表面 `F.Cu` 実装） | 5枚<br>（PCBAは2枚〜可） | [GERBER-curcur40-pmw3360.zip](../../pcbs/curcur40/pmw3360/jlcpcb/production_files/GERBER-curcur40-pmw3360.zip) | [BOM-curcur40-pmw3360.csv](../../pcbs/curcur40/pmw3360/jlcpcb/production_files/BOM-curcur40-pmw3360.csv) | [CPL-curcur40-pmw3360.csv](../../pcbs/curcur40/pmw3360/jlcpcb/production_files/CPL-curcur40-pmw3360.csv) |
| **④ 左トッププレート**<br>(`plate-top-left`) | **PCB のみ**<br>（FR-4 1.6mm） | 5枚 | [GERBER-plate-top-left.zip](../../plates/curcur40/pcb/jlcpcb/production_files/GERBER-plate-top-left.zip) | 不要（PCBAなし） | 不要（PCBAなし） |
| **⑤ 右トッププレート**<br>(`plate-top-right`) | **PCB のみ**<br>（FR-4 1.6mm） | 5枚 | [GERBER-plate-top-right.zip](../../plates/curcur40/pcb/jlcpcb/production_files/GERBER-plate-top-right.zip) | 不要（PCBAなし） | 不要（PCBAなし） |

> **補足（ボトムプレートについて）**:
> 3Dプリントケース（`cases/curcur40/left.step`, `right.step`）を使用する場合、ボトムプレートは不要です。万が一 3Dプリントケースを使わずサンドイッチ構造にしたい場合のみ、[GERBER-plate-bottom-left.zip](../../plates/curcur40/pcb/jlcpcb/production_files/GERBER-plate-bottom-left.zip) および [GERBER-plate-bottom-right.zip](../../plates/curcur40/pcb/jlcpcb/production_files/GERBER-plate-bottom-right.zip) を追加で発注してください。
> また、アクリル等のレーザーカットでプレートを作る場合は [plate-curcur40.svg](../../plates/curcur40/svg/plate-curcur40.svg)（およびポロンフォーム用 [foam-curcur40.svg](../../plates/curcur40/svg/foam-curcur40.svg)）を使用できます。

### 2-2. JLCPCB 推奨発注オプション

- **Base Material**: `FR-4`
- **Layers**: `2 Layers`
- **PCB Thickness**: **`1.6 mm`**（メイン基板・センサー基板・トッププレートすべて `1.6 mm`）
- **PCB Color**: お好みの色（`Black` / `Matte Black` / `White` など）
- **Surface Finish**: `HASL(with lead)` または `LeadFree HASL` / `ENIG`（プレートやメイン基板の見た目にこだわる場合は `ENIG` も人気です）
- **Remove Order Number**: **`Specify a location`** または **`Yes`（有料オプション）** ※特にトッププレートは表面に製造番号が入らないよう `Remove Order Number: Yes` を推奨します。
- **PCBA Assembly Side**:
  - 左メイン基板 (`curcur40-left`)：**`Bottom Side`**
  - 右メイン基板 (`curcur40-right`)：**`Bottom Side`**
  - PMW3360 センサー基板 (`curcur40-pmw3360`)：**`Top Side`**
- **PCBA 実装内容の確認**:
  - 左右メイン基板には RP2040 マイコン、Flash メモリ、水晶振動子、LDO、Kailh Choc ホットスワップソケット（左21個・右19個）、ダイオード、RGB LED、USB Type-C コネクタ、TRRS ジャック、リセット/ブートスイッチ、抵抗・コンデンサ類がすべて実装されます。
  - 右メイン基板の **`rEXSW1`（CKW12）** と **`rJ3`（6ピンヘッダ）**、およびセンサー基板の **`U1`（PMW3360）** と **`J1`（ピンヘッダ）** は手ハンダ対象のため PCBA からは除外されています（確認画面で Unplaced となっても正常です）。

---

## 3. JLC3DP に発注するもの（3Dプリント造形）

JLC3DP（[https://jlc3dp.com/](https://jlc3dp.com/)）または手持ちの 3D プリンタで、以下の **3つのパーツ** を造形します（JLC3DP へは形状精度の高い `.step` ファイルのアップロードを推奨します）。

| 対象パーツ | 数量 | アップロード用ファイル (STEP 推奨) | STL ファイル（予備・スライサー用） | 推奨素材・方式 |
| :--- | :---: | :--- | :--- | :--- |
| **① 左手用ケース** | **1個** | [left.step](../../cases/curcur40/left.step) | [left.stl](../../cases/curcur40/left.stl) | **MJF (PA12 ナイロン)** / **SLS (PA12)**<br>または **SLA (タフレジン / Black Resin)** |
| **② 右手用ケース** | **1個** | [right.step](../../cases/curcur40/right.step) | [right.stl](../../cases/curcur40/right.stl) | **MJF (PA12 ナイロン)** / **SLS (PA12)**<br>または **SLA (タフレジン / Black Resin)** |
| **③ 25mm トラックボールカップ** | **1個** | [trackball-cup.step](../../cases/curcur40/trackball-cup.step) | [trackball-cup.stl](../../cases/curcur40/trackball-cup.stl) | **SLA (高精細レジン)** または **MJF (PA12)**<br>※直径2mm支持球を圧入するため寸法精度の高い方式を推奨 |

> **オプション（CKW12 の 3D プリントパーツを自前で造形する場合）**:
> 後述する「CKW12 キット」を Booth で購入する場合は、キット内に 3D プリントパーツ（ハウジング・ホイール・ステム）が含まれているため発注不要です。
> 電子部品のみを個別購入して CKW12 を自作する場合は、[3dmodels/curcur40.3dshapes/](../../3dmodels/curcur40.3dshapes/) 内の以下の3ファイル（または本家 [kumamuk-git/CKW12](https://github.com/kumamuk-git/CKW12) の STL）も一緒に JLC3DP（SLA レジン推奨）で造形してください。
> - ハウジング: [CKW12_housing.step](../../3dmodels/curcur40.3dshapes/CKW12_housing.step) × 1個
> - ホイール: [CKW12_wheel_d18_t5.step](../../3dmodels/curcur40.3dshapes/CKW12_wheel_d18_t5.step) × 1個
> - ステム: [CKW12_stem.step](../../3dmodels/curcur40.3dshapes/CKW12_stem.step) × 1個

---

## 4. 別で入手・購入するパーツ一覧

JLCPCB / JLC3DP 以外で、キーボードショップ・電子部品通販・Amazon 等から入手するパーツの一覧です。

### 4-1. キースイッチ・キーキャップ

| 品名 | 必要数 | 仕様・備考 | 主な入手先 |
| :--- | :---: | :--- | :--- |
| **Kailh Choc V1 / V2 キースイッチ** | **40個** | 左手21個 ＋ 右手19個。<br>Kailh Choc V1（Red / White / Sunset Tactile 等）または Choc V2 ロープロファイルスイッチに対応。 | 遊舎工房 / Talp Keyboard / Daily Craft Keyboard / AliExpress 等 |
| **Choc 用 1u キーキャップ** | **40個** | **全キー 1u サイズ（40個）** です。<br>※選ぶスイッチ（Choc V1 ステム / Choc V2 十字ステム）に適合するロープロファイルキーキャップを用意してください。 | 遊舎工房 / Booth / Talp Keyboard / AliExpress 等 |

### 4-2. 右手スクロールエンコーダ（CKW12）関連

右手人差し指内側（`rEXSW1`）に搭載する水平ロータリーエンコーダです。**方法A（キット購入）** が最も簡単で確実です。

#### 方法A：キットを購入する場合（推奨）
| 品名 | 必要数 | 仕様・備考 | 主な入手先 |
| :--- | :---: | :--- | :--- |
| **CKW12 水平ロータリーエンコーダキット** | **1セット** | エンコーダ、タクトスイッチ、コンスルーピン（5本）、M2皿ネジ、3Dプリントパーツ一式がすべて揃ったキット。 | Booth（[kumamuk 氏のショップ](https://kumamuk.booth.pm/items/5487792)） |

#### 方法B：部品を個別に揃える場合（キット在庫切れ時など）
| 品名 | 必要数 | 型番・仕様 | 主な入手先 |
| :--- | :---: | :--- | :--- |
| **中空軸ロータリーエンコーダ** | **1個** | Alps Alpine **`EC05E1220202`** | 秋月電子 / Mouser / DigiKey |
| **横押しタクトスイッチ** | **1個** | Alps Alpine **`SKQYACE010`**（または `SKQGAFE010`） | Mouser / DigiKey / AliExpress |
| **コンスルー（スプリングピンヘッダ）** | **5ピン分** | 2.54mmピッチ、高さ 2.0mm または 2.5mm（12ピン等をニッパーで1ピンずつ5個に切り分けて使用） | 遊舎工房 / 千石電商 / 秋月電子 |
| **M2 皿ネジ（CKW12固定用）** | **2本** | M2 × 長さ 3mm〜4mm（基板表側からCKW12ハウジングへネジ止め） | ホームセンター / Amazon / モノタロウ |

### 4-3. 右手トラックボール・PMW3360 センサー関連

| 品名 | 必要数 | 仕様・備考 | 主な入手先 |
| :--- | :---: | :--- | :--- |
| **25mm トラックボール球** | **1個** | 直径 **25mm** のトラックボール交換球。<br>定番は **Perixx（ペリックス）PERIPRO-303 25mm**、または Keyball / killerwhale 用 25mm 球。 | Amazon（Perixx公式）/ 遊舎工房 / Booth |
| **直径 2.0mm（$\varnothing 2.0\text{ mm}$）支持球** | **3個** | `trackball-cup` 内部の3つのくぼみに圧入してトラックボールを滑らかに支えるベアリング球。<br>**$\varnothing 2.0\text{ mm}$ セラミック球（$\text{ZrO}_2$ ジルコニア または $\text{Si}_3\text{N}_4$ 窒化ケイ素）** または高精密ステンレス球（G10〜G20）。 | Amazon / モノタロウ / AliExpress / Booth |
| **PMW3360DM-T2QU センサーIC ＋ レンズ（LM19-LSI）** | **1セット** | 光学センサー IC 本体（16-pin DIP形状）と専用レンズのセット。`curcur40-pmw3360` 基板の `U1` に手ハンダします。<br>※組立時の注意：`curcur40-pmw3360` 基板裏面のジャンパ **`JP1` の 1-2 パッド（3.3V動作）をハンダブリッジ** して使用します。 | AliExpress / Tindie / Booth |
| **2.54mmピッチ 6ピン ピンヘッダ / ソケット（または配線材）** | **1組（6ピン）** | 右メイン基板の `rJ3`（6ピン：`GND, +3V3, CS, MISO, MOSI, SCLK`）とセンサー基板の `J1`（1〜6番ピン）を接続します。<br>ピンヘッダ＋ソケット、またはリボンケーブルの直付けで接続可能です。 | 秋月電子 / 千石電商 / Amazon |

### 4-4. ネジ・スペーサー・ゴム足・ケーブル類

Corne Chocolate v4 準拠の筐体固定用ネジ・スペーサーと、トラックボールモジュール固定用のネジ、および接続ケーブルです。

| 品名 | 必要数 | 仕様・備考 | 主な入手先 |
| :--- | :---: | :--- | :--- |
| **M2 スペーサー（長さ 5.5mm）** | **8個** | 左手4個 ＋ 右手4個（両メス、丸型または六角）。<br>トッププレート（1.6mm）と 3D ケース底面の間隔を保持し、PCB（1.6mm）の穴を貫通します。 | 遊舎工房 / Hirosugi-Net（廣杉計器）/ Amazon / AliExpress |
| **M2 ネジ（長さ 4.5mm または 4.0mm）** | **16本** | トッププレート側 8本 ＋ ケース底面側 8本。<br>精密低頭ネジまたは平頭ネジ推奨。 | 遊舎工房 / Amazon / モノタロウ / 秋月電子 |
| **M2 ネジ（長さ 5.0mm〜6.0mm）** | **4本** | 右手ケースへの `trackball-cup` 固定用（2本）および `curcur40-pmw3360` センサー基板固定用（2本）。※必要に応じて M2 ナット 2〜4個を併用。 | ホームセンター / Amazon / モノタロウ |
| **ゴム足（クッションゴム）** | **8〜10個** | 直径 6mm〜8mm、厚み 1.5mm〜2mm 程度の貼り付け式ゴム足（左右ケース底面の四隅＋トラックボール下部に貼付）。 | Amazon / 100円ショップ / ホームセンター |
| **TRRS ケーブル（4極・3.5mm）** | **1本** | 左右分割キーボード間を接続するケーブル。<br>⚠️ **必ず「4極（TRRS）」を使用してください（3極 TRS ケーブルは VCC と GND がショートするため使用不可）。** | 遊舎工房 / Amazon |
| **USB Type-C ケーブル** | **1本** | PC との接続用（データ通信対応のもの）。 | Amazon / 家電量販店 |

---

## 5. 発注前チェックリスト

- [ ] **JLCPCB**:
  - [ ] `curcur40-left`（PCB + PCBA / Bottom実装 / 1.6mm）
  - [ ] `curcur40-right`（PCB + PCBA / Bottom実装 / 1.6mm）
  - [ ] `curcur40-pmw3360`（PCB + PCBA / Top実装 / 1.6mm）
  - [ ] `plate-top-left`（PCBのみ / 1.6mm / 注文番号削除推奨）
  - [ ] `plate-top-right`（PCBのみ / 1.6mm / 注文番号削除推奨）
- [ ] **JLC3DP**:
  - [ ] `left.step` × 1
  - [ ] `right.step` × 1
  - [ ] `trackball-cup.step` × 1
- [ ] **別調達パーツ**:
  - [ ] Kailh Choc スイッチ × 40個 ＆ 1u キーキャップ × 40個
  - [ ] CKW12 キット × 1セット
  - [ ] 25mm トラックボール球 × 1個 ＆ $\varnothing 2.0\text{ mm}$ 支持球 × 3個
  - [ ] PMW3360DM-T2QU センサー ＋ LM19-LSI レンズ × 1セット ＆ 6ピンヘッダ/配線材
  - [ ] M2 スペーサー（5.5mm × 8個）、M2 ネジ（4.5mm × 16本、5〜6mm × 4本）、ゴム足
  - [ ] 4極 TRRS ケーブル × 1本 ＆ USB-C ケーブル × 1本
