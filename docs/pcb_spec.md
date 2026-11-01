# curcur40 PCB・回路設計仕様書 (PCB & Schematic Specification)

本書は、エルゴノミクス分割キーボード **curcur40**（25mmトラックボール・アンダープレート一体軸パッシブ磁気慣性ホイール統合型、Choc v2 ロープロファイル）の左右メイン基板（`curcur40-left`, `curcur40-right`）およびトラックボール光学センサーサブ基板（`curcur40-pmw3360`）の全3基板に関する設計基準書です。
ケース設計仕様書（[case_spec.md](./case_spec.md)）およびパッシブ磁気慣性ホイール設計仕様書（[passive_inertia_wheel_spec.md](./passive_inertia_wheel_spec.md)）と対をなし、基板構成・回路仕様・ピンアサイン・ライブラリ管理・DRC/ERC検証基準を定義します。

> **【運用ルール】**
> 1. **対象バージョン**: KiCad **10.0**（10.0.7以降）を基準環境とします。
> 2. **標準ライブラリ準拠（シャドウ定義の禁止）**:
>    - KiCad公式標準ライブラリ（`MCU_RaspberryPi`, `Device`, `Diode`, `Connector`, `Capacitor_SMD`, `Resistor_SMD`, `Package_DFN_QFN`, `Package_SO`, `Package_TO_SOT_SMD`, `Sensor_Magnetic`, `Jumper` 等）をプロジェクトローカルのテーブルで上書き（シャドウイング）してはなりません。
>    - プロジェクト固有ライブラリは [pcbs/common/kbd/](../pcbs/common/kbd) 配下の `kbd` および `PMW3360_PCB` のみとします。
> 3. **設計変更の手順**:
>    - 回路・ピン配置・基板寸法を変更する場合、まず本書（[docs/pcb_spec.md](./pcb_spec.md)）の該当箇所を更新し、レビュー合意後に回路図（`.kicad_sch`）および基板（`.kicad_pcb`）へ反映します。
>    - 変更後は必ず `kicad-cli` による ERC および DRC（`--schematic-parity` 含む）、ならびに [`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py) のプリフライトチェックを実行し、第8節の品質基準を満たすことを検証します。

---

## 1. ファイル・ライブラリ構成 (Project & Library Structure)

### 1.1 プロジェクトファイル一覧（全3基板：すべて板厚 1.60 mm FR-4 Bottom PCBA）

アンダープレート一体軸慣性ホイール用の3Dホール磁気センサー（`rU6`: `TMAG5273A1QDBVR`）および静音中クリックスイッチ（`rEXSW1`: `Kailh Square Silent`）を右手メイン基板 `curcur40-right` 裏面（`B.Cu`）へ直接統合したことで、ホイール用の極小センサーサブ基板・単体評価基板・手配線ハーネスは一切不要となり、リポジトリ全体の基板は **以下の3基板のみ** のシンプルな構成となっています。

| 区分 | 左手メイン (`curcur40-left`) | 右手メイン (`curcur40-right`) | トラックボールセンサー (`curcur40-pmw3360`) | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| **プロジェクト設定** | [curcur40-left.kicad_pro](../pcbs/left/curcur40-left.kicad_pro) | [curcur40-right.kicad_pro](../pcbs/right/curcur40-right.kicad_pro) | [curcur40-pmw3360.kicad_pro](../pcbs/pmw3360/curcur40-pmw3360.kicad_pro) | デザインルール・DRC/ERC設定 |
| **回路図 (Schematic)** | [curcur40-left.kicad_sch](../pcbs/left/curcur40-left.kicad_sch) | [curcur40-right.kicad_sch](../pcbs/right/curcur40-right.kicad_sch) | [curcur40-pmw3360.kicad_sch](../pcbs/pmw3360/curcur40-pmw3360.kicad_sch) | 回路論理・シンボル定義 |
| **基板レイアウト (PCB)** | [curcur40-left.kicad_pcb](../pcbs/left/curcur40-left.kicad_pcb) | [curcur40-right.kicad_pcb](../pcbs/right/curcur40-right.kicad_pcb) | [curcur40-pmw3360.kicad_pcb](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb) | パターン配線・外形・シルク |
| **シンボルテーブル** | [left/sym-lib-table](../pcbs/left/sym-lib-table) | [right/sym-lib-table](../pcbs/right/sym-lib-table) | [pmw3360/sym-lib-table](../pcbs/pmw3360/sym-lib-table) | カスタムシンボル登録 |
| **フットプリントテーブル** | [left/fp-lib-table](../pcbs/left/fp-lib-table) | [right/fp-lib-table](../pcbs/right/fp-lib-table) | [pmw3360/fp-lib-table](../pcbs/pmw3360/fp-lib-table) | カスタムフットプリント登録 |

### 1.2 ライブラリ管理ポリシー

`sym-lib-table` および `fp-lib-table` には、以下の**プロジェクト固有カスタムライブラリのみ**を登録します。汎用部品（`Sensor_Magnetic:TMAG5273x1QDBV` / `Package_TO_SOT_SMD:SOT-23-6` や `SM06B-SRSS-TB` を含む）はすべて KiCad 10.0 標準ライブラリ（`${KICAD10_SYMBOL_DIR}` / `${KICAD10_FOOTPRINT_DIR}`）を直接参照します。

| ライブラリ名 | 種別 | パス | `curcur40` で使用している固有定義 |
| :--- | :--- | :--- | :--- |
| **`kbd`** | シンボル | [pcbs/common/kbd/kicad-symbols/kbd.kicad_sym](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | 右手用電源シンボル（`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`）、逆付けRGB LED（`YS-SK6812MINI-E`） |
| **`PMW3360_PCB`** | シンボル | [pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | 光学センサー（`PMW3360DM-T2QU`）、1.8V LDO（`TLV74318PDBVR`） |
| **`kbd`** | フットプリント | [pcbs/common/kbd/kicad-footprints/kbd.pretty](../pcbs/common/kbd/kicad-footprints/kbd.pretty) | 下記 **1.3節** の計6種類のカスタムフットプリントのみ使用 |

### 1.3 `curcur40` で使用するプロジェクト固有ライブラリデータの入手元と改変履歴

#### ① 回路図シンボルライブラリ（`.kicad_sym`）

| ライブラリ / シンボル名 | ファイルパス | データ入手元（公開リポジトリ） | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **`kbd`**<br>(`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`, `YS-SK6812MINI-E`) | [kbd.kicad_sym](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | **foostan/kbd**<br>(`https://github.com/foostan/kbd` — Corne v4 公式 KiCad ライブラリ、[MIT License](../pcbs/common/kbd/LICENSE)) | `2026-10-22`: 未使用シンボルを削除し、`YS-SK6812MINI-E` の Pin 2 (`DOUT`) を KiCad 10.0 ERC 対応としてデータシート通り `output` に修正 |
| **`PMW3360_PCB`**<br>(`PMW3360DM-T2QU`, `TLV74318PDBVR`) | [pmw3360_pcb.kicad_sym](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | **siderakb/pmw3360-pcb**<br>(`https://github.com/siderakb/pmw3360-pcb`、[CERN-OHL-P v2](../LICENSE_CERN_OHL_P_V2)) | `2026-10-22`: 未使用の `TXS0108E-QPWRQ1` を削除し、`PMW3360DM-T2QU` Pin 3 (`VDDPIX`) を `power_out` に修正 |

#### ② フットプリントライブラリ（`kbd.pretty/*.kicad_mod`、計6種）

| フットプリント名 (`kbd:`) | 対象部品 / 回路図シンボル | データ入手元・作成根拠 | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **[`keyswitch_choc12_hotswap_1u.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/keyswitch_choc12_hotswap_1u.kicad_mod)** | Kailh Choc ソケット (`CPG135001S30`)<br>`Switch:SW_Push` | **foostan/kbd** ([MIT License](../pcbs/common/kbd/LICENSE)) | 旧 Corne V3 由来の不要な $\varnothing 0.40\,\text{mm}$ NPTH 穴および個別マスクマージンを削除、相対3Dモデルパス化 |
| **[`YS-SK6812MINI-E.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/YS-SK6812MINI-E.kicad_mod)** | 逆付け RGB LED (`YS-SK6812MINI-E`)<br>`kbd:YS-SK6812MINI-E` | **foostan/kbd** ([MIT License](../pcbs/common/kbd/LICENSE)) | シルク重なり回避および相対3Dモデルパス化 |
| **[`TS-1088R-02026.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/TS-1088R-02026.kicad_mod)** | SMD タクトSW (`TS-1088R-02026`)<br>`Switch:SW_Push` | **foostan/kbd** ([MIT License](../pcbs/common/kbd/LICENSE)) | 相対3Dモデルパス化 |
| **[`USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod)** | USB-C 16ピン (`TYPE-C-31-M-13C`)<br>`Connector:USB_C_Receptacle_USB2.0_16P` | **foostan/kbd** ([MIT License](../pcbs/common/kbd/LICENSE)) | 標準シンボルのフィルタ適合リネーム、シールド脚 `SH` ピン名整合、相対3Dモデルパス化 |
| **[`PMW3360DM-T2QU_16Pin.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)** | 光学センサー (`PMW3360DM-T2QU`)<br>`PMW3360_PCB:PMW3360DM-T2QU` | **siderakb/pmw3360-pcb** ([CERN-OHL-P v2](../LICENSE_CERN_OHL_P_V2)) | KiCad 10.0 向けにスルーホールパッド層 `(layers "*.Cu" "*.Mask")` を補完 |
| **[`Kailh_Square_Silent_6.2x6.2mm.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/Kailh_Square_Silent_6.2x6.2mm.kicad_mod)** | 静音角形マイクロスイッチ (`rEXSW1`: `Kailh Square Silent 6.2×6.2×4.3mm`)<br>`Switch:SW_Push` | Kailh 公式データシート公表寸法（本体 $6.2 \times 6.2\,\text{mm}$、2ピンピッチ $5.00\,\text{mm}$、平端子 $0.8 \times 0.4\,\text{mm}$）に基づき新規作成 | ドリル径 $\varnothing 1.10\,\text{mm}$ PTH 2穴＋専用3Dモデル [`Kailh_Square_Silent_6.2x6.2mm.step`](../pcbs/common/kbd/kicad-packages3D/kbd.3dshapes/Kailh_Square_Silent_6.2x6.2mm.step) 登録（`curcur40-right` 裏面 `B.Cu` `(-2.0125, -2.00)` に直付け実装） |

---

## 2. 基板物理仕様・デザインルール (Board Physical Specs & Design Rules)

### 2.1 基板外形・層構成

| 項目 | 左手 PCB (`curcur40-left`) | 右手メイン PCB (`curcur40-right`) | センサーサブ PCB (`curcur40-pmw3360`) | 備考 |
| :--- | :---: | :---: | :---: | :--- |
| **基材・層数** | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | 銅箔厚 1 oz (35 µm) 標準 |
| **基板板厚** | **1.60 mm** | **1.60 mm** | **1.60 mm** | 全基板 **1.6 mm 統一**（0.8mm 薄板発注不要） |
| **PCBA 実装面** | **裏面 (`Bottom Side`)** | **裏面 (`Bottom Side`)** | **裏面 (`Bottom Side`)** | 全3基板とも裏面片面 Economic PCBA |
| **外形バウンディングボックス** | **124.325 × 91.8125 mm** | **124.325 × 91.8125 mm** | **29.575 × 29.200 mm** | JLCPCB PCBA 下限（$20\times 20\text{ mm}$）に余裕で適合 |
| **PCB座標範囲 ($X$)** | $-119.0625 \sim +5.2625 \, \text{mm}$ | $-5.2625 \sim +119.0625 \, \text{mm}$ | $-5.2625 \sim +24.3125 \, \text{mm}$ | |
| **PCB座標範囲 ($Y$)** | $-24.3125 \sim +67.5000 \, \text{mm}$ | $-24.3125 \sim +67.5000 \, \text{mm}$ | $+38.3000 \sim +67.5000 \, \text{mm}$ | |
| **内部切り欠き穴** | なし | **十字形ホイール窓**<br>（縦 $7.70 \times 23.00\,\text{mm}$ ＋ 横翼 $[4.8375..21.3375] \times [-5.75..+1.75]\,\text{mm}$） | **$8.70 \times 16.90 \, \text{mm}$ 角穴** | 右メイン $(14.2875, -2.0000)$（南キー `rEXSW2` と同軸）に幅 $6.50\,\text{mm}$ アンダープレートホイール窓、センサーサブ中央 $(9.525, 52.3875)$ に光学角穴 |
| **固定穴 (`Edge.Cuts`)** | **5 箇所** (`L1`〜`L5`: すべて $\varnothing 2.40\,\text{mm}$ 円穴) | **7 箇所** (`R1`〜`R5, WC1, WC2`: すべて $\varnothing 2.40\,\text{mm}$ 円穴) | **4 箇所** (`TB1`〜`TB4`: $\varnothing 2.40\,\text{mm}$ 円穴) | 全16箇所すべてシンプルな $\varnothing 2.40\,\text{mm}$ M2ネジ貫通円穴に統一（太穴・南U溝ゼロ） |
| **総フットプリント数** | 82 点（PCBA **81 点**） | 85 点（PCBA **83 点** / 24 BOMグループ） | 13 点（PCBA **9 点** / 7 BOMグループ） | 手ハンダ THT（右 `rEXSW1`、TBセンサー `U1`）および `DNP`（`J4`/`rJ4`, `R4`/`C5`）を除く全SMDをPCBA自動実装 |

### 2.2 DRC デザインルール（製造制約）

JLCPCB 標準 2層基板製造プロセス（追加料金なし）に準拠したデザインルールを設定しています：
* **最小クリアランス**: `0.19 mm`（0.5mmピッチ ESD保護IC `U3`/`U5`・`rU3`/`rU5` 通過部のみ `0.15 mm`）
* **最小配線幅**: `0.20 mm`（信号線 `0.20 mm` / `0.2032 mm`、電源ライン `0.25 mm` 〜 `0.508 mm`）
* **標準ビア寸法**: 外径 `0.50 mm` / ドリル径 `0.30 mm`（一部電源・信号ビアは外径 `0.60 mm` / ドリル径 `0.30 mm`）
* **ハンダマスク拡張 (`pad_to_mask_clearance`)**: **`0 mm`**（KiCad 10.0 標準 NSMD）
* **銅箔ゾーン (`GND` / `GNDR`)**: 表裏両面全面ベタGNDプレーン、サーマルリリーフ最小スポーク数 `2本`。

---

## 3. 左右基板の機能構成・相違点 (Left vs. Right Architecture)

| 機能ブロック | 左手 PCB (`curcur40-left`) | 右手 PCB (`curcur40-right`) | 詳細・備考 |
| :--- | :--- | :--- | :--- |
| **メインマイコン** | `U1` (`RP2040`) | `rU1` (`RP2040`) | 裏面（`B.Cu`）PCBA実装 |
| **QSPI フラッシュ** | `U4` (`W25Q128JVSIQ`, 16MB) | `rU4` (`W25Q128JVSIQ`, 16MB) | 裏面（`B.Cu`）PCBA実装、SOIC-8 |
| **3.3V LDO レギュレータ** | `U2` (`NCP1117LPST33T3G`) | `rU2` (`NCP1117LPST33T3G`) | 5V (`VBUS`) → 3.3V (`+3V3` / `+3V3R`) |
| **PC接続 / 左右間ポート** | 北側 `J1` ＋ 内側 `J2` (`TYPE-C-31-M-13C`) | 北側 `rJ1` ＋ 内側 `rJ2` (`TYPE-C-31-M-13C`) | すべてミッドマウント USB-C 16ピン（`B.Cu`、ESD保護・誤挿し保護回路付き） |
| **キースイッチ数 (Choc)** | **21 キー**（すべて 1u） | **19 キー**（すべて 1u） | ダイレクトピン接続（マトリクスダイオード不要） |
| **RGB LED (`YS-SK6812MINI-E`)** | **21 個** (`LED1`〜`18`, `EXLED1`〜`3`) | **19 個** (`rLED1`〜`18`, `rEXLED2`) | 各キースイッチ直下に配置 |
| **パッシブ磁気慣性ホイール回路** | なし（通常キースイッチ `EXSW1`） | **右メイン基板 `B.Cu` に直接オンボード統合！**<br>・**`rU6`**: `TMAG5273A1QDBVR`（3Dホール磁気センサ, `I2C0`, PCBA実装済）<br>・**`rEXSW1`**: `Kailh Square Silent`（静音中クリックSW, `/KEYEX1`, THT 2ピン直付け） | **ホイール用サブ基板・JST SH コネクタ（旧 `rJ5`）・手配線ハーネスを完全廃止**。回転軸西端の `D4×1mm` 径方向着磁磁石の3軸磁界 $(B_x, B_z)$ を `rU6` で直接読み取り |
| **トラックボールセンサー** | なし（親指4キー構成） | **JST SH 6ピンコネクタ (`rJ3`)** 経由で独立サブ基板 [`curcur40-pmw3360`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（`U1`: `PMW3360DM-T2QU` ＋ `U2`: `1.8V LDO` ＋ `J1`）と接続 | トラックボールカップ開口面をトッププレート天面（$Z = -2.00\,\text{mm}$）とフラッシュに沈み込ませるため、センサー基板のみ $-11.80\,\text{mm}$ 下段（$Z = -16.00\,\text{mm}$）へ分離配置 |
| **SWD デバッグ端子** | `J4` (`1x03` 2.54mm スルーホール) | `rJ4` (`1x03` 2.54mm スルーホール) | `/SWCLK`, `GND`, `/SWD`。**未実装 (`DNP`)**・BOM/Pos/3Dモデル非表示 |
| **左右判定ピン (`GPIO21`)** | **`+3V3` (HIGH) に直結** | **`GNDR` (LOW) に直結** | QMK `split.handedness.pin = GP21` による自動左右認識 |
| **固定穴 (`Edge.Cuts`)** | **5 箇所**（`L1`〜`L5`: すべて $\varnothing 2.40\,\text{mm}$ 円穴） | **右メイン 7 箇所**（`R1`〜`R5, WC1, WC2`: すべて $\varnothing 2.40\,\text{mm}$ 円穴）＋ **TBセンサー基板 4 箇所**（`TB1`〜`TB4`: $\varnothing 2.40\,\text{mm}$ 円穴） | 全16箇所すべて統一 `M2×6.0mm` ネジでケース $\varnothing 5.20\,\text{mm}$ フラットボス（TBは $\varnothing 6.00\,\text{mm}$）・クレードルボスへ基板を直接クランプ |

---

## 4. 回路ブロック別詳細仕様 (Detailed Circuit Specifications)

### 4.1 電源回路と左右間 USB-C 接続 (`J2` / `rJ2`)
1. **USB 5V 入力・逆流防止 (`ZD1` / `rZD1`: `RB521S30T1G`) と RGB LED 電源電圧降下 (`D1` / `rD1`: `1N4148WT`)**:
   - PC接続用 USB Type-C コネクタ（`J1` / `rJ1`）の `VBUS` から `ZD1` / `rZD1` を経由して `+5V` / `+5VR` を生成し、さらに `D1` / `rD1` の順方向電圧降下（約 $0.7\,\text{V}$）で RGB LED 電源（約 $4.3\,\text{V}$）を供給して $3.3\,\text{V}$ ロジック信号とのレベル整合を確保します（`keyboard.json` にて `max_brightness: 50` 制限）。
2. **VBUS 接続検出 (`/USB_VBUS_PIN`)**:
   - `ZD1`/`rZD1` 上流の PC `VBUS` を `R8` (`5.6kΩ`) / `R9` (`10kΩ`) で分圧して `RP2040` Pin 16 (`GPIO13`) へ入力し、マスター／スレーブを自動判定します。
3. **左右間 USB-C 接続 (`J2` / `rJ2`: リバーシブル ＆ PC誤挿しフェイルセーフ保護)**:
   - `A6, B6` (`D+` 同士を直結) を `/SPLIT_DP` とし、ESD保護 `U5` / `rU5` (`TPD4E05U06DQAR`) および直列保護抵抗 `R10` / `rR10` (`27Ω`) を介して `GPIO12` (`/TX`) へ接続します。`CC1`/`CC2` は意図的に `NC`（プルダウン抵抗非実装）としているため、万が一 PC や PD 充電器を内側ポートへ誤挿ししても `VBUS` が出力されないコールドソケット状態を維持します。

### 4.2 左右判定ピン (`RP2040` Pin 32 `GPIO21`) の設計と ERC 警告の扱い
* 左手 `U1` Pin 32 (`GPIO21`) は `+3V3`（HIGH）、右手 `rU1` Pin 32 (`GPIO21`) は `GNDR`（LOW）に直結しています。
* KiCad 10.0 純正 `MCU_RaspberryPi:RP2040` シンボルを無改変で維持するため、ERC 実行時に `[pin_to_pin]` 警告が左右 **1件のみ** 出力される状態を正式仕様とします。

### 4.3 右手専用：光学トラックボールセンサー基板 (`curcur40-pmw3360`) と JST SH 6ピン接続 (`rJ3` / `J1`)
* トラックボールカップを $-11.80\,\text{mm}$ 沈み込ませるため、`U1` (`PMW3360DM-T2QU`) と 1.8V LDO `U2` (`TLV74318PDBVR`) を独立サブ基板 [`curcur40-pmw3360.kicad_pcb`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（$Z = -17.60 \sim -16.00\,\text{mm}$）に分離し、右メイン基板唯一の JST SH 6ピンコネクタ **`rJ3`**（`B.Cu` $(46.5000, 63.0000)$, 西向き）とセンサーサブ基板 **`J1`**（`B.Cu` $(19.2000, 52.3875)$, 東向き）を **市販の JST SH 6ピン両端同方向フラットケーブル（`1-6, 2-5, 3-4, 4-3, 5-2, 6-1` 結線、50mm推奨）** でひねらず真っ直ぐ接続します：
  * 北端（`J1` Pin 1 / `rJ3` Pin 6）: `+3V3R` ／ 2番目: `GNDR` ／ 3番目: `/SCLK` (`GP14`) ／ 4番目: `/MOSI` (`GP11`) ／ 5番目: `/MISO` (`GP8`) ／ 南端（`J1` Pin 6 / `rJ3` Pin 1）: `/NCS` (`GP6`)。
* **`VDDPIX` 分離・`JP1` 銅箔ブリッジ・`R4`/`C5` DNP**: `U1` Pin 3 (`VDDPIX`) は `C1`/`C2` のみの独立ネット（`Net-(U1-VDDPIX)`）に保ち、`JP1` は `SolderJumper_3_Bridged12`（Pad 1 `+3V3R` – Pad 2 `/V_{IO}` 基板内銅箔直結）、`R4` (`28kΩ`) / `C5` (`22nF`) は `DNP` とします。

### 4.4 右手専用：アンダープレート一体軸慣性ホイール オンボード検出・クリック回路 (`rU6` / `rEXSW1`)
* **十字形ホイール開口と `WC1`/`WC2` 固定穴（南隣接キー `rEXSW2` と中心軸完全一致）**:
  * ホイール回転軸中心 **$(14.2875, -2.0000)\,\text{mm}$**（南キー `rEXSW2` $(14.2875, 19.0500)$ と左右中心軸一致）を基準に、$\varnothing 22.00 \times 6.50\,\text{mm}$ スチールホイール用の縦スロット（$7.70 \times 23.00\,\text{mm}$、$x_{\text{pcb}} \in [10.4375, 18.1375]$, $y_{\text{pcb}} \in [-13.50, +9.50]$）と、一体軸受 `DDL-520ZZ`・PA12 マグネットホルダー逃がし用の横翼（$x_{\text{pcb}} \in [4.8375, 21.3375]$, $y_{\text{pcb}} \in [-5.75, +1.75]$）を組み合わせた十字形切り欠きを設けています。
  * 周囲対角2箇所に [`wheel-cradle.step`](../cases/inertia_wheel/wheel-cradle.step) 固定用の $\varnothing 2.40\,\text{mm}$ 貫通穴 **`WC1` $(6.6375, -9.8000)$** および **`WC2` $(21.2375, +6.0000)$** を配置しています。
* **オンボード 3軸リニアホール磁気センサー `rU6`（PCBA自動実装済・手配線ゼロ）**:
  * **採用素子**: Texas Instruments **`TMAG5273A1QDBVR`**（`SOT-23-6`、LCSC **`C3716049`**、回路図シンボル `Sensor_Magnetic:TMAG5273x1QDBV`）
  * **配置座標**: 右メイン基板 `B.Cu` の **`(3.0175, -2.0000)`**（回転 $-90^\circ$）。西側の `D4×1mm` 径方向2極着磁ネオジム磁石（$x_{\text{pcb}} \in [5.2675, 6.2675]\,\text{mm}, y_{\text{pcb}} = -2.00\,\text{mm}, Z = -6.90\,\text{mm}$）と $2.25 \sim 3.25\,\text{mm}$ の距離で対向し、回転磁界ベクトル $(B_x, B_z)$ を高S/N比で検出します。
  * **ピン結線とピン互換フォールバック設計（`TLV493D-A1B6` 無改造対応）**:
    * **Pin 1 (`SCL`)**: `/WHEEL_SCL` → `rU1` Pin 37 (`GPIO25` / ハードウェア `I2C0 SCL`、`rR12` `4.7kΩ` で `+3V3R` へプルアップ)
    * **Pin 2 (`GND`)**: `GNDR`
    * **Pin 3 (`SDA`)**: `/WHEEL_SDA` → `rU1` Pin 36 (`GPIO24` / ハードウェア `I2C0 SDA`、`rR11` `4.7kΩ` で `+3V3R` へプルアップ)
    * **Pin 4 (`VCC`)**: `+3V3R`（直近にデカップリングコンデンサ `rC18` `100nF` を配置）
    * **Pin 5 (`~INT`)**: **`rR13` (`0Ω`, `0402`, LCSC `C17168`)** を介して `GNDR` へ接続。`TMAG5273` では起動時無効のオープンドレイン出力のため `GND` 接続で問題なく動作し、万が一の部品枯渇時にピン互換の Infineon **`TLV493D-A1B6`**（Pin 5 が必須 `GND` ピン）へ載せ替えても基板無改造・ファームウェア自動判別でそのまま動作します。
    * **Pin 6 (`GND`)**: `GNDR`
* **オンボード静音ミドルクリックスイッチ `rEXSW1`（基板 `B.Cu` 直付け THT）**:
  * **採用素子**: **`Kailh Square Silent 6.2×6.2×4.3mm`**（フットプリント `kbd:Kailh_Square_Silent_6.2x6.2mm`）
  * **配置座標**: 右メイン基板 `B.Cu` の **`(-2.0125, -2.0000)`**。Pin 1 を `/KEYEX1`（`rU1` Pin 9 `GPIO7`, マトリクス `[4, 6]`）、Pin 2 を `GNDR` へ基板内パターンで直結しています。
  * **実装方法**: THT 部品のため PCBA（BOM/CPL）からは自動除外されます。組み立て時に裏面 `B.Cu` へ密着挿入し、表面 `F.Cu` 側で2ピンをはんだ付けした後、Switch Gap（$0.60\,\text{mm}$）内でトッププレート裏面（$Z = -3.60\,\text{mm}$）に触れないよう飛び出しピン先端をニッパーで平切りします。

---

## 5. RP2040 ピンアサイン対応表 (MCU Pin Assignment Table)

| Pin番号 | RP2040 ピン名 | 左手 (`U1`) ネット名 | 左手 機能 | 右手 (`rU1`) ネット名 | 右手 機能 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **2** | `GPIO0` | `/KEY4` | キー `[0, 5]` | `/KEY11` | キー `[5, 3]` |
| **3** | `GPIO1` | `/KEY6` | キー `[1, 4]` | `/KEY5` | キー `[4, 4]` |
| **4** | `GPIO2` | `/KEY3` | キー `[1, 5]` | `/KEY12` | キー `[4, 3]` |
| **5** | `GPIO3` | `/KEY7` | キー `[2, 4]` | `/KEY13` | キー `[4, 2]` |
| **6** | `GPIO4` | `/KEYEX1` | キー `[0, 6]` | `/KEY14` | キー `[5, 2]` |
| **7** | `GPIO5` | `/KEYEX3` | キー `[3, 6]` | `/KEY15` | キー `[6, 2]` |
| **8** | `GPIO6` | 未接続 (`NC`) | （予備） | **`/NCS`** | **PMW3360 SPI CS (`rJ3` Pin 1)** |
| **9** | `GPIO7` | 未接続 (`NC`) | （予備） | **`/KEYEX1`** | **慣性ホイール 静音中クリックSW `rEXSW1` `[4, 6]`（基板直結）** |
| **11** | `GPIO8` | `/KEYEX2` | キー `[1, 6]` | **`/MISO`** | **PMW3360 SPI MISO (`rJ3` Pin 2)** |
| **12** | `GPIO9` | `/KEY2` | キー `[2, 5]` | `/KEY18` | キー `[4, 1]` |
| **13** | `GPIO10` | `/LED` | RGB LED `DIN` (`GP10`) | `/LED` | RGB LED `DIN` (`GP10`) |
| **14** | `GPIO11` | `/KEY1` | キー `[3, 5]` | **`/MOSI`** | **PMW3360 SPI MOSI (`rJ3` Pin 3)** |
| **15** | `GPIO12` | `/TX` | 左右間 USB-C シリアル通信 (`R10` 経由 `J2` `D+`) | `/TX` | 左右間 USB-C シリアル通信 (`rR10` 経由 `rJ2` `D+`) |
| **16** | `GPIO13` | `/USB_VBUS_PIN` | VBUS 検出 | `/USB_VBUS_PIN` | VBUS 検出 |
| **17** | `GPIO14` | `/KEY9` | キー `[3, 3]` | **`/SCLK`** | **PMW3360 SPI SCLK (`rJ3` Pin 4)** |
| **18** | `GPIO15` | `/KEY8` | キー `[3, 4]` | `/KEY17` | キー `[5, 1]` |
| **24** | `SWCLK` | `/SWCLK` | デバッグ SWCLK (`J4`) | `/SWCLK` | デバッグ SWCLK (`rJ4`) |
| **25** | `SWDIO` | `/SWD` | デバッグ SWDIO (`J4`) | `/SWD` | デバッグ SWDIO (`rJ4`) |
| **26** | `RUN` | `Net-(U1-RUN)` | リセットSW (`SMDSW2`) | `Net-(rU1-RUN)` | リセットSW (`rSMDSW2`) |
| **27** | `GPIO16` | `/KEY16` | キー `[2, 1]` | `/KEY9` | キー `[7, 3]` |
| **28** | `GPIO17` | 未接続 (`NC`) | ― | `/KEY8` | キー `[7, 4]` |
| **29** | `GPIO18` | `/KEY17` | キー `[1, 1]` | `/KEY16` | キー `[6, 1]` |
| **30** | `GPIO19` | 未接続 (`NC`) | ― | `/KEY1` | キー `[7, 5]` |
| **31** | `GPIO20` | `/KEY18` | キー `[0, 1]` | `/KEY7` | キー `[6, 4]` |
| **32** | **`GPIO21`** | **`+3V3`** | **左右判定 (Left = HIGH)** | **`GNDR`** | **左右判定 (Right = LOW)** |
| **34** | `GPIO22` | 未接続 (`NC`) | ― | `/KEY2` | キー `[6, 5]` |
| **35** | `GPIO23` | `/KEY13` | キー `[0, 2]` | `/KEYEX2` | キー `[5, 6]` |
| **36** | `GPIO24` | `/KEY14` | キー `[1, 2]` | **`/WHEEL_SDA`** | **オンボード3Dホール `rU6` (`TMAG5273`) `I2C0 SDA` (`rR11` 4.7kΩ プルアップ)** |
| **37** | `GPIO25` | `/KEY15` | キー `[2, 2]` | **`/WHEEL_SCL`** | **オンボード3Dホール `rU6` (`TMAG5273`) `I2C0 SCL` (`rR12` 4.7kΩ プルアップ)** |
| **38** | `GPIO26` | `/KEY12` | キー `[0, 3]` | `/KEY3` | キー `[5, 5]` |
| **39** | `GPIO27` | `/KEY11` | キー `[1, 3]` | `/KEY4` | キー `[4, 5]` |
| **40** | `GPIO28` | `/KEY10` | キー `[2, 3]` | `/KEY6` | キー `[5, 4]` |
| **41** | `GPIO29` | `/KEY5` | キー `[0, 4]` | `/KEY10` | キー `[6, 3]` |
| **46** | `USB_DM` | `Net-(U1-USB_DM)` | USB D- (`27Ω` 経由) | `Net-(rU1-USB_DM)` | USB D- (`27Ω` 経由) |
| **47** | `USB_DP` | `Net-(U1-USB_DP)` | USB D+ (`27Ω` 経由) | `Net-(rU1-USB_DP)` | USB D+ (`27Ω` 経由) |
| **51〜56** | `QSPI_*` | `/QSPI_*` | Flash `U4` & `SMDSW1` | `/QSPI_*` | Flash `rU4` & `rSMDSW1` |

---

## 6. 固定穴・機械的インターフェース仕様 (Mechanical Mounting & Holes)

ケース設計仕様書（[case_spec.md](./case_spec.md) 第2.3節）と完全一致する、全16箇所共通の統一 `M2 × 6.0mm` ネジ貫通円穴（$\varnothing 2.40\,\text{mm}$）の配置定義です（全箇所ともケース受けボス $\varnothing 5.20\,\text{mm}$／クレードルボス外径範囲内に SMD 部品・パッドが存在しない干渉ゼロ配置）。

| 基板 | 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 形状・寸法 (`Edge.Cuts`) | インターフェース相手（`M2×L3.0×OD3.2mm` 真鍮インサート） |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **左メイン (`curcur40-left`)** | **L1** | 内側上（PC側 USB-C 横） | $(0.0000, -15.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 左ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **左メイン (`curcur40-left`)** | **L2** | 内側下（左右間 USB-C 上） | $(0.0000, 18.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 左ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **左メイン (`curcur40-left`)** | **L3** | 小指側上 | $(-101.0000, -20.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 左ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **左メイン (`curcur40-left`)** | **L4** | 小指側南東（`SW15/16/17` 間） | $(-100.5000, 21.5000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 左ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **左メイン (`curcur40-left`)** | **L5** | 親指側下（`SW8`–`SW9` 南側） | $(-62.0000, 65.1500)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 左ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **R1** | 外周・内側上（PC側 USB-C 横） | $(0.0000, -15.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 右ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **R2** | 外周・内側下（左右間 USB-C 上） | $(0.0000, 18.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 右ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **R3** | 外周・小指側上 | $(101.0000, -20.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 右ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **R4** | 外周・小指側南東（`rSW15/16/17` 間） | $(100.5000, 21.5000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 右ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **R5** | 外周・親指側下（`rSW8`–`rSW9` 南側） | $(62.0000, 65.1500)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | 右ケースフラット円筒ボス ($\varnothing 5.20$, $Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **WC1** | ホイールクレードル北西固定 | $(6.6375, -9.8000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | `wheel-cradle.step` 北西ボス ($Z=-5.80$) へ基板クランプ |
| **右メイン (`curcur40-right`)** | **WC2** | ホイールクレードル南東固定 | $(21.2375, 6.0000)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | `wheel-cradle.step` 南東ボス ($Z=-5.80$) へ基板クランプ |
| **TBセンサー (`curcur40-pmw3360`)** | **TB1〜TB4** | トラックボール四隅 (`NW`, `NE`, `SW`, `SE`) | $(-2.475 / 21.525,\ 41.0875 / 63.6875)$ | $\varnothing 2.40 \, \text{mm}$ 円穴 | カップ $2.0\,\text{mm}$ 耳と共締めで右ケース下段ボス ($Z=-17.60$) |

---

## 7. 実装部品表 (BOM Summary)

| カテゴリ | リファレンス (左) | リファレンス (右メイン / TBセンサー) | 型番 / 値 (LCSC) | パッケージ / フットプリント | 実装面 | 左数量 | 右数量 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **MCU** | `U1` | `rU1` | `RP2040` (`C2040`) | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | `B.Cu` | 1 | 1 |
| **QSPI Flash** | `U4` | `rU4` | `W25Q128JVSIQ` (`C113767`) | `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | `B.Cu` | 1 | 1 |
| **3.3V LDO** | `U2` | `rU2` | `NCP1117LPST33T3G` (`C146799`) | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | `B.Cu` | 1 | 1 |
| **ESD 保護 IC** | `U3, U5` | `rU3, rU5` | `TPD4E05U06DQAR` (`C138714`) | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | `B.Cu` | 2 | 2 |
| **水晶振動子** | `Y1` | `rY1` | `12MHz 18pF` (`C91749`) | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` | `B.Cu` | 1 | 1 |
| **ショットキーD** | `ZD1` | `rZD1` | `RB521S30T1G` (`C145179`) | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **スイッチングD** | `D1` | `rD1` | `1N4148WT` (`C232841`) | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **3Dホール磁気センサ** | ― | `rU6` (右メイン PCBA実装) | `TMAG5273A1QDBVR` (`C3716049`) | `Package_TO_SOT_SMD:SOT-23-6` | `B.Cu` | 0 | 1 |
| **コンデンサ (0402)** | `C1`〜`C17` | `rC1`〜`rC18` | 左: `100n`(10), `1u`(3), `10u`(2), `27p`(2)<br>右: `100n`(11), `1u`(3), `10u`(2), `27p`(2) | `Capacitor_SMD:C_0402_1005Metric` | `B.Cu` | 17 | 18 |
| **抵抗 (0402)** | `R1`〜`R10` | `rR1`〜`rR13` | 左: `27`(3), `1k`(2), `5.1k`(2), `5.6k`(1), `10k`(2)<br>右: 上記 ＋ `4.7k`(2: `rR11, rR12`) ＋ `0Ω`(1: `rR13`) | `Resistor_SMD:R_0402_1005Metric` | `B.Cu` | 10 | 13 |
| **USB-C (16ピン)** | `J1, J2` | `rJ1, rJ2` | `TYPE-C-31-M-13C` (`C2848620`) | `kbd:USB_C_Receptacle_TYPE-C-31-M-13C` | `B.Cu` | 2 | 2 |
| **タクトSW** | `SMDSW1, SMDSW2` | `rSMDSW1, rSMDSW2` | `TS-1088R-02026` (`C455280`) | `kbd:TS-1088R-02026` | `B.Cu` | 2 | 2 |
| **逆付け RGB LED** | `LED1`〜`18`, `EXLED1`〜`3` | `rLED1`〜`18`, `rEXLED2` | `YS-SK6812MINI-E` (`C5149201`) | `kbd:YS-SK6812MINI-E` | `B.Cu` | 21 | 19 |
| **Choc ソケット (1u)** | `SW1`〜`18`, `EXSW1`〜`3` | `rSW1`〜`18`, `rEXSW2` | `CPG135001S30` (`C5333465`) | `kbd:keyswitch_choc12_hotswap_1u` | `B.Cu` | 21 | 19 |
| **静音中クリックSW** | ― | `rEXSW1` (右メイン手ハンダ THT) | `Kailh Square Silent 6.2×6.2×4.3mm` | `kbd:Kailh_Square_Silent_6.2x6.2mm` | `B.Cu` | 0 | 1 (手ハンダ) |
| **JST SH 6ピンコネクタ** | ― | `rJ3` (右メイン) / `J1` (TBセンサー) | `SM06B-SRSS-TB(LF)(SN)` (`C160405`) | `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` | `B.Cu` | 0 | 1 + 1 |
| **光学センサー** | ― | `U1` (TBセンサー手ハンダ THT) | `PMW3360DM-T2QU` | `kbd:PMW3360DM-T2QU_16Pin` | `B.Cu` | 0 | 1 (手ハンダ) |
| **1.8V LDO** | ― | `U2` (TBセンサー) | `TLV74318PDBVR` (`C485152`) | `Package_TO_SOT_SMD:SOT-23-5` | `B.Cu` | 0 | 1 |
| **コンデンサ (0603)** | ― | `C1`〜`C4` (`C5` は `DNP`, TBセンサー) | `4.7uF`(1), `1uF`(2), `100nF`(1) | `Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder` | `B.Cu` | 0 | 4 (+1 `DNP`) |
| **抵抗 (0603)** | ― | `R1`〜`R3` (`R4` は `DNP`, TBセンサー) | `10k`(2), `39R`(1) | `Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder` | `B.Cu` | 0 | 3 (+1 `DNP`) |
| **電圧選択ジャンパ** | ― | `JP1` (Pad 1–2 基板直結, TBセンサー) | `SolderJumper_3_Bridged12` | `Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels` | `B.Cu` | 0 | 0 (銅箔パターン) |
| **SWD デバッグ端子** | `J4` (`DNP`) | `rJ4` (`DNP`) | `Conn_01x03` | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | `B.Cu` | 0 (`DNP`) | 0 (`DNP`) |

---

## 8. 品質検証基準 (DRC / ERC Verification Criteria)

### 8.1 検証コマンド
```powershell
# 左手 ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/left/curcur40-left.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/left/curcur40-left.kicad_pcb

# 右手メイン ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/right/curcur40-right.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/right/curcur40-right.kicad_pcb

# トラックボールセンサーサブ基板 ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/pmw3360/curcur40-pmw3360.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/pmw3360/curcur40-pmw3360.kicad_pcb

# JLCPCB 発注前自動検証（全実装部品の .step 3Dモデル存在チェック含む）
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe" scripts/export_jlcpcb.py

# ★ PCB・部品配置・外形変更時の必須ステップ：KiCad 3D STEP エクスポート ＆ 3DP筐体・機構との干渉／6-DOF検証
& "$env:USERPROFILE\.local\bin\uvx.exe" --no-config --managed-python --python 3.13 --from "cadgen==0.7.26" python scripts/generate_full_assembly.py
```

### 8.2 合格基準（現在の達成状態）

| チェック対象 | エラー数 | 警告数 | 未配線 / 回路図不一致 | 無視設定 (Ignored Checks) | 許容される唯一の警告・除外内容 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **左手 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **右手メイン PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **トラックボールセンサー PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **左右トッププレート DRC** | **0 件** | **0 件** | **0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **左手 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `U1` Pin 32 (`GPIO21`) と `+3V3` の直結（左右判定ピン） |
| **右手メイン 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `rU1` Pin 32 (`GPIO21`) と `GNDR` の直結（左右判定ピン） |
| **トラックボールセンサー 回路図 ERC** | **0 件** | **0 件** | ― | **なし (0 件)** | なし（完全ゼロ） |
| **全実装部品 3D STEP モデル解決チェック** | **0 件** | **0 件** | ― | **固定除外 2点のみ** | 左81部品・右84部品・センサー9部品すべて `.step` 解決済（除外は銅箔 `JP1` と光学側配置 `PMW3360 U1` のみ） |
| **3DPケース・ボス・ホイール機構 3D干渉検証** | **0 件** | **0 件** | ― | **なし (0 件)** | 全668ソリッド間 `overlap_volume == 0.00000000 mm³`・最小クリアランス＆6-DOF拘束 PASS |

* **JLCPCB 2層 FR-4 PCB / PCBA 発注前自動検証（[`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py)）**:
  全3基板（`left`, `right`, `pmw3360`）および左右トッププレートについて、DRC/ERC 合格に加えて基板外形サイズ（$\ge 20 \times 20\text{ mm}$）、最小配線幅（$\ge 0.127\text{ mm}$、実測 $\ge 0.200\text{ mm}$）、最小ビア（$\ge 0.45/0.30\text{ mm}$、実測 $0.50/0.30\text{ mm}$）、PTH/NPTH ドリル径、Gerber 全9レイヤー＋ドリル存在、BOM/CPL の Designator 100% 一致、有効な LCSC 番号、THT/`DNP` 部品（`rEXSW1`, `U1(PMW3360)`, `JP1`, `R4`, `C5`, `J4`, `rJ4`）の自動除外、および**全非 `DNP` 部品に有効な `.step`/`.stp` 3Dモデルが紐付いていること**をアサートします。
* **PCB変更時の 3DPモデル干渉検証の必須化と 3Dモデル未設定NG時の運用ルール（[`scripts/generate_full_assembly.py`](../scripts/generate_full_assembly.py)）**:
  * PCB（`Edge.Cuts`、部品配置、フットプリント、3Dモデル）に変更が入った際は必ず `scripts/generate_full_assembly.py` を実行し、KiCad から直接エクスポートした STEP モデルと 3DP ケース・受けボス・ホイールクレードル・プレート等との干渉体積ゼロ（`0.00000000 mm³`）を確認のうえ `cases/assemblies/*.step` を更新します。
  * **3Dモデル未設定・リンク切れ（NG）が発生した場合、チェックを通すために独断で簡易・推測3Dモデル（ダミー形状等）を定義したり除外リストへ追加して素通りさせてはなりません**。NGのまま停止して対象部品を報告し、公式3Dモデルやデータシートの調達・レビュー方針を合意してから対応します。

### 8.3 KiCad 10.0 `pcbnew` Python API 注意事項
* `board.GetTracks()` を走査する際は、必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を分岐させ、ビアには `t.GetWidth(pcbnew.F_Cu)` および `t.GetPosition()` を使用してください（引数なし `GetWidth()` は C++ アサーション停止を招きます）。

---

## 9. リポジトリのフォルダ構成・生成スクリプト格納ルール (Directory & Script Rules)

| ディレクトリ | 格納対象・役割 | 運用ルール |
| :--- | :--- | :--- |
| **[`docs/`](../docs)** | 設計仕様書（`case_spec.md`, `pcb_spec.md`, `passive_inertia_wheel_spec.md`, `parts_spec.md`）、ビルドガイド（`buildguide_jp.md`）、および図版・3Dレンダリング資産（`assets/`） | すべての仕様書・画像アセットを一元管理する |
| **[`pcbs/`](../pcbs)** | 全3基板の KiCad プロジェクト（`left/`, `right/`, `pmw3360/`）、共通ライブラリ（`common/kbd/`）、および JLCPCB 発注データ（`*/jlcpcb/production_files/`） | `.rpt`, `.net`, `.bak`, `.kicad_prl` 等の一時ファイルを残さない |
| **[`plates/`](../plates)** | FR-4 トッププレート基板（`pcb/plate-top-{left,right}.kicad_pcb`）、JLCPCB Gerber（`pcb/jlcpcb/production_files/`）、レーザーカット用 SVG（`svg/`） | ボトムプレートは密閉トレイ型ケースに統合済みのため作成しない |
| **[`cases/`](../cases)** | 直下にケース・カップ実部品（5種）、[`cases/inertia_wheel/`](../cases/inertia_wheel) にアンダープレート一体軸ホイール実部品（4種）、[`cases/assemblies/`](../cases/assemblies) に7種の3D検証アセンブリモデル | すべて [`scripts/`](../scripts) 配下の10本の公式スクリプト（詳細は [`scripts/README.md`](../scripts/README.md) 参照）から再現可能に生成する |
