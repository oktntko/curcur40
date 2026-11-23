# curcur40 PCB・回路設計仕様書 (`pcb_spec.md`)

本書は、左右メイン基板（`curcur40-left`, `curcur40-right`）、トラックボールセンサーサブ基板（`curcur40-pmw3360`）、および 3-in-1 統合 PCBA パネル（`curcur40-panel-3in1`）の回路構成・物理ルール・ピンアサイン・実装部品（LCSC）・設計根拠を定義します。

- 対象環境: KiCad **10.0**（10.0.7 以降）
- 対応スクリプト: [`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py)
- 関連仕様書: 固定穴座標と筐体スタックアップは [`docs/case_spec.md`](./case_spec.md)、トラックボール光学系は [`docs/trackball_spec.md`](./trackball_spec.md)、慣性ホイール磁気検出は [`docs/wheel_spec.md`](./wheel_spec.md)、検証コマンド詳細は [`scripts/README.md`](../scripts/README.md) を参照してください。

---

## 1. 基板ファイル・カスタムライブラリ構成

### 1.1 プロジェクト構成（全3基板 ＋ 3-in-1 パネル：すべて板厚 `1.60 mm` FR-4 裏面 PCBA）

慣性ホイール用の 3D ホールセンサー（`rU6`）と静音中クリックスイッチ（`rEXSW1`）を右メイン基板 `B.Cu` へ直接統合しているため、リポジトリ全体の単体基板は以下の 3種のみです。さらに [`export_jlcpcb.py`](../scripts/export_jlcpcb.py) により、3枚を 1枚の捨て基板フレームへまとめた [`curcur40-panel-3in1.kicad_pcb`](../pcbs/panel/curcur40-panel-3in1.kicad_pcb) が自動生成されます。

| 区分 | 左手メイン (`curcur40-left`) | 右手メイン (`curcur40-right`) | TBセンサー (`curcur40-pmw3360`) |
| :--- | :--- | :--- | :--- |
| **プロジェクト** | [curcur40-left.kicad_pro](../pcbs/left/curcur40-left.kicad_pro) | [curcur40-right.kicad_pro](../pcbs/right/curcur40-right.kicad_pro) | [curcur40-pmw3360.kicad_pro](../pcbs/pmw3360/curcur40-pmw3360.kicad_pro) |
| **回路図** | [curcur40-left.kicad_sch](../pcbs/left/curcur40-left.kicad_sch) | [curcur40-right.kicad_sch](../pcbs/right/curcur40-right.kicad_sch) | [curcur40-pmw3360.kicad_sch](../pcbs/pmw3360/curcur40-pmw3360.kicad_sch) |
| **基板レイアウト** | [curcur40-left.kicad_pcb](../pcbs/left/curcur40-left.kicad_pcb) | [curcur40-right.kicad_pcb](../pcbs/right/curcur40-right.kicad_pcb) | [curcur40-pmw3360.kicad_pcb](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb) |

### 1.2 ローカルライブラリ管理ポリシー（標準ライブラリ上書き禁止）
汎用部品（`RP2040`, `TMAG5273x1QDBV`, `SOT-23-6`, `SM06B-SRSS-TB`, `SolderJumper_3_Bridged12`, 受動部品・ダイオード等）はすべて KiCad 10.0 公式標準ライブラリを直接参照し、プロジェクトローカルの `sym-lib-table` / `fp-lib-table` で標準ライブラリをシャドウイングしてはなりません。ローカル登録は [`pcbs/common/kbd/`](../pcbs/common/kbd/) 配下の以下の固有定義のみとします：

- **回路図シンボル（2ライブラリ）**:
  - [`kbd.kicad_sym`](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym)（由来: `foostan/kbd`, MIT）: 右手用電源シンボル（`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`）、逆付け RGB LED `YS-SK6812MINI-E`（Pin 2 `DOUT` を `output` に整合済）。
  - [`pmw3360_pcb.kicad_sym`](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym)（由来: `siderakb/pmw3360-pcb`, CERN-OHL-P v2）: `PMW3360DM-T2QU`（Pin 3 `VDDPIX` を内部レギュレータ出力 `power_out` に修正済）、`TLV74318PDBVR`。
- **フットプリント（`kbd.pretty` 計 6種・3Dモデル相対パス設定済）**:
  1. [`keyswitch_choc12_hotswap_1u.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/keyswitch_choc12_hotswap_1u.kicad_mod): Kailh Choc ホットスワップソケット `CPG135001S30`（不要な `⌀0.40 mm` NPTH 穴を削除済）。
  2. [`YS-SK6812MINI-E.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/YS-SK6812MINI-E.kicad_mod): 逆付け RGB LED。
  3. [`TS-1088R-02026.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/TS-1088R-02026.kicad_mod): SMD タクトスイッチ（BOOT / RESET）。
  4. [`USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod): ミッドマウント USB-C 16ピン（シールド脚 `SH` 整合済）。
  5. [`PMW3360DM-T2QU_16Pin.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod): 光学センサー 16ピン DIP（角穴 `16.90 × 8.70 mm`・非対称ガイドポスト穴付き）。
  6. [`Kailh_Square_Silent_6.2x6.2mm.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/Kailh_Square_Silent_6.2x6.2mm.kicad_mod): 静音角形マイクロスイッチ（2ピンピッチ `5.00 mm`、ドリル `⌀1.15 mm` PTH）。

---

## 2. 基板物理仕様・デザインルール・3-in-1 パネル設計

### 2.1 外形・層構成・固定穴ルール

| 項目 | 左手 (`curcur40-left`) | 右手 (`curcur40-right`) | TBセンサー (`curcur40-pmw3360`) | 3-in-1 パネル (`curcur40-panel-3in1`) |
| :--- | :---: | :---: | :---: | :---: |
| **層数・板厚・銅箔** | 2層 / `1.60 mm` / `1 oz` | 2層 / `1.60 mm` / `1 oz` | 2層 / `1.60 mm` / `1 oz` | 2層 / `1.60 mm` / `1 oz` |
| **PCBA 実装面・種別** | 裏面 (`Bottom Side`) | 裏面 (`Bottom Side`) | 裏面 (`Bottom Side`) | 裏面 (`Bottom Side`) / `Standard PCBA`※ |
| **外形サイズ** | `114.35 × 90.45 mm` | `114.35 × 90.45 mm` | `29.73 × 29.35 mm` | **`131.05 × 207.25 mm`** |
| **PCB座標範囲 (`X`)** | `-119.0625 〜 -4.7625 mm` | `+4.7625 〜 +119.0625 mm` | `+13.7875 〜 +43.3625 mm` | `0.00 〜 131.00 mm` |
| **PCB座標範囲 (`Y`)** | `-27.6625 〜 +62.7375 mm` | `-27.6625 〜 +62.7375 mm` | `+33.5375 〜 +62.7375 mm` | `0.00 〜 207.20 mm` |
| **内部切り欠き窓** | なし | 十字形ホイール窓<br>（縦 `7.95 × 23.00` ＋ 横翼） | 光学角穴<br>（`8.70 × 16.90 mm`） | USB-C 前方 `3.70 mm` ルーター逃げ溝×4 |
| **M2 ネジ固定穴** | 6箇所 (`L1`〜`L6`: `⌀2.40 mm`) | 8箇所 (`R1`〜`R6, WC1, WC2`: `⌀2.40 mm`) | 4箇所 (`TB1`〜`TB4`: `⌀2.40 mm`) | 計 18箇所（座標は [`case_spec.md`](./case_spec.md) 参照） |
| **PCBA 実装点数** | **81 点** / 20 BOM種 | **81 点** / 24 BOM種 | **9 点** / 7 BOM種 | **171 点** / 30 BOM種 |

> ※ `SK6812MINI-E`（`C5149201`, MSL ベーキング対象）および `TYPE-C-31-M-13C`（`C2848620`）が JLCPCB で `Standard Only` 指定のため、PCBA 発注時は `Standard PCBA`（`Different Design: 3` / `Edge Rails: Added by Customer`）を使用します。

### 2.2 配線・ビア・切り欠き・キープアウト・パネル設計ルール
- **最小クリアランス / 配線幅**: クリアランス `0.19 mm`（`0.5 mm` ピッチ ESD 保護 IC 周辺のみ `0.15 mm`）、最小配線幅 `0.20 mm`（電源ライン `0.25 〜 0.508 mm`）。
- **標準ビア**: 外径 `0.50 mm`（一部 `0.60 mm`）/ ドリル径 `0.30 mm`（JLCPCB 2層標準上限内、Via-in-Pad ゼロ）。
- **右メイン基板 (`curcur40-right`) の切り欠き境界座標（`Edge.Cuts` 正本寸法）**:
  - **十字形ホイール窓**（各角 `R = 0.50 mm`）: 縦スロット `x_pcb ∈ [10.1875, 18.1375], y_pcb ∈ [-8.7375, +14.2625] mm`（`7.95 × 23.00 mm`）＋ 軸受・東側ホルダー逃がし横翼 `x_pcb ∈ [6.9375, 23.6475], y_pcb ∈ [-0.9875, +6.5125] mm`。
  - **トラックボール部 南側 U字切り欠き**: `x_pcb ∈ [14.1500, 42.8375], y_pcb ≥ 32.9000 mm`（沈み込みカップ外周 `⌀28.00 mm` との非接触通過を確保）。
- **USB-C 切り欠き内角逃げ**: 全 4箇所のミッドマウント USB-C 切り欠き内角には、JLCPCB 標準 `⌀1.60 mm` ルータービットでもシェル角が干渉しない **`R = 0.90 mm` ドッグボーン逃げ** を設けています。
- **ネジ座面・インサート短絡防止キープアウト**: 表面 `F.Cu` 全面ベタ GND（裏面 `B.Cu` はゾーンなしストラップ配線）に対し、全固定穴周囲（`L1`〜`L6`, `R1`〜`R6, WC1, WC2`: `F.Cu r = 2.30 mm` / `B.Cu r = 2.00 mm`；`TB1`〜`TB4`: 両面 `r = 2.00 mm`）に円形 `Rule Area` 銅箔禁止領域を設け、ネジ頭や真鍮インサート接触による短絡を遮断しています。
- **3-in-1 パネル構造**: 外周 `5.00 mm` コンベヤレール、中央 H形補強リブ、非対称フィデューシャル 3点（`FID1`〜`FID3`）、ツール穴 4点（`TH1`〜`TH4`: `⌀2.00 mm`）、および基板輪郭から `0.10 mm` 内側へ引いた 22箇所（計 88穴、`⌀0.55 mm` NPTH、全銅箔から `≥ 0.48 mm` 離隔）のマウスバイトタブを備えます。

---

## 3. 回路ブロック別設計根拠

1. **電源・逆流防止・LED ロジック閾値マージン**:
   - PC側 `VBUS` 逆流防止ダイオード `ZD1` / `rZD1` には **`40V 1A` ショットキーバリアダイオード `1N5819WS`（`C191023` Basic）** を採用。
   - RGB LED 電源ラインの `D1` / `rD1` には **シリコンスイッチングダイオード `1N4148WS`（`C2128` Basic、連続定格 `150 mA`）** を直列挿入し、約 `0.6 〜 0.7 V` の順方向電圧降下によって高 `VBUS` 時でも `YS-SK6812MINI-E` の入力 High 閾値（`V_IH = 0.7 × V_DD < 3.3 V`）を確実に満たします（ダイオード定格保護のためファームウェア `keyboard.json` の `max_brightness: 50` を維持）。
   - `3.3 V` 生成にはセラミックコンデンサ（MLCC）で安定動作する低ドロップアウト LDO **`LDL1117S33R`（`SOT-223-3_TabPin2`, `1.2 A`, `C435835`）** を使用。`ZD1` / `rZD1` 上流の `VBUS` を `5.6 kΩ` / `10 kΩ` で分圧して `GPIO13`（`/USB_VBUS_PIN`）へ入力しマスター／スレーブを自動判定します。
2. **左右間 USB-C コールドソケット保護（`J2` / `rJ2`）**:
   - `A6, B6`（`D+`）を ESD 保護 IC `USBLC6-2SC6`（`U5` / `rU5`, `C7519`）および直列抵抗 `27 Ω`（`R10` / `rR10`）経由で `GPIO12`（`/TX`）へ接続。`CC1` / `CC2` は意図的に未接続（`NC`）としているため、誤って PD 充電器や PC を内側ポートへ挿しても `VBUS` が出力されないフェイルセーフ構造です。
3. **左右自動判定ピン（`RP2040` Pin 32 `GPIO21`）と許容 ERC 警告**:
   - 左手 `U1` の `GPIO21` は `+3V3`（HIGH）、右手 `rU1` の `GPIO21` は `GNDR`（LOW）へ直結し、QMK の `split.handedness.pin = GP21` で左右自動認識を行います。純正 `MCU_RaspberryPi:RP2040` シンボルを無改変で使うため、左右回路図の ERC で出力される `[pin_to_pin]` 警告 **1件のみ** を意図的な正常仕様とします。
4. **右手 トラックボールセンサーサブ基板インターフェース（`rJ3` ⇔ `J1`）**:
   - 右メイン `rJ3`（`(46.80, 36.35)` 西向き）とセンサー基板 `J1`（`(38.25, 47.625)` 東向き、ともに JST SH 6P `SM06B-SRSS-TB(LF)(SN)` `C160405`）を、**両端同方向フラットケーブル（`1-6` 結線、長さ `100 mm`）** でひねらず接続します（北端 `J1` Pin 1 / `rJ3` Pin 6 から順に `+3V3R`, `GNDR`, `/SCLK`, `/MOSI`, `/MISO`, `/NCS`）。
   - `PMW3360DM-T2QU`（`U1`）の Pin 3（`VDDPIX`）は内部レギュレータ出力のため外部 `1.8 V`（`TLV74318PDBVR` 出力）とは接続せず、`C1`（`4.7 µF`）/ `C2`（`100 nF`）のみの独立ネットに保ちます。`JP1` は基板内銅箔で Pad 1（`+3V3R`）– Pad 2（`/V_IO`）直結済、`R4` / `C5` および左右 SWD 端子 `J4` / `rJ4` は `DNP` です。
5. **右手 オンボード慣性ホイール検出・クリック回路（`rU6` / `rEXSW1`）**:
   - **`rU6`（`TMAG5273A1QDBVR`, `SOT-23-6`, `C3716049`）**: 右メイン `B.Cu` の `(25.3200, +2.7625)`（回転 `+90°`）に配置し、`I2C0`（Pin 6 `SDA` → `GPIO24`、Pin 1 `SCL` → `GPIO25`、`4.7 kΩ` プルアップ `rR11`/`rR12`、パスコン `rC18` `100 nF`）へ接続。Pin 5（`~INT`）を **`rR13`（`0 Ω`, `C17168`）で `GNDR` に落とす** ことで、ピン互換の Infineon `TLV493D-A1B6`（Pin 5 `GND` 必須）へも基板無改造で載せ替え可能です。
   - **`rEXSW1`（`Kailh Square Silent`）**: 右メイン `B.Cu` の `(25.3000, -4.7500)` に THT 直付けし、`GPIO7`（`/KEYEX1`, マトリクス `[4, 6]`）へ接続します（THT のため PCBA からは自動除外）。

---

## 4. RP2040 ピンアサイン対応表

| Pin番号 | RP2040 ピン名 | 左手 (`U1`) ネット | 左手 機能 | 右手 (`rU1`) ネット | 右手 機能 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **2** | `GPIO0` | `/KEY4` | キー `[0, 5]` | `/KEY11` | キー `[5, 3]` |
| **3** | `GPIO1` | `/KEY6` | キー `[1, 4]` | `/KEY5` | キー `[4, 4]` |
| **4** | `GPIO2` | `/KEY3` | キー `[1, 5]` | `/KEY12` | キー `[4, 3]` |
| **5** | `GPIO3` | `/KEY7` | キー `[2, 4]` | `/KEY13` | キー `[4, 2]` |
| **6** | `GPIO4` | `/KEYEX1` | キー `[0, 6]` | `/KEY14` | キー `[5, 2]` |
| **7** | `GPIO5` | `/KEYEX3` | キー `[3, 6]` | `/KEY15` | キー `[6, 2]` |
| **8** | `GPIO6` | `NC` | 予備 | **`/NCS`** | **PMW3360 SPI CS (`rJ3` Pin 1)** |
| **9** | `GPIO7` | `NC` | 予備 | **`/KEYEX1`** | **ホイール中クリック `rEXSW1` `[4, 6]`** |
| **11** | `GPIO8` | `/KEYEX2` | キー `[1, 6]` | **`/MISO`** | **PMW3360 SPI MISO (`rJ3` Pin 2)** |
| **12** | `GPIO9` | `/KEY2` | キー `[2, 5]` | `/KEY18` | キー `[4, 1]` |
| **13** | `GPIO10` | `/LED` | RGB LED `DIN` | `/LED` | RGB LED `DIN` |
| **14** | `GPIO11` | `/KEY1` | キー `[3, 5]` | **`/MOSI`** | **PMW3360 SPI MOSI (`rJ3` Pin 3)** |
| **15** | `GPIO12` | `/TX` | 左右間シリアル (`J2` `D+`) | `/TX` | 左右間シリアル (`rJ2` `D+`) |
| **16** | `GPIO13` | `/USB_VBUS_PIN` | VBUS 検出 | `/USB_VBUS_PIN` | VBUS 検出 |
| **17** | `GPIO14` | `/KEY9` | キー `[3, 3]` | **`/SCLK`** | **PMW3360 SPI SCLK (`rJ3` Pin 4)** |
| **18** | `GPIO15` | `/KEY8` | キー `[3, 4]` | `/KEY17` | キー `[5, 1]` |
| **24 / 25** | `SWCLK / SWDIO` | `/SWCLK, /SWD` | `J4` (`DNP`) | `/SWCLK, /SWD` | `rJ4` (`DNP`) |
| **26** | `RUN` | `Net-(U1-RUN)` | リセット `SMDSW2` | `Net-(rU1-RUN)` | リセット `rSMDSW2` |
| **27** | `GPIO16` | `/KEY16` | キー `[2, 1]` | `/KEY9` | キー `[7, 3]` |
| **28** | `GPIO17` | `NC` | ― | `/KEY8` | キー `[7, 4]` |
| **29** | `GPIO18` | `/KEY17` | キー `[1, 1]` | `/KEY16` | キー `[6, 1]` |
| **30** | `GPIO19` | `NC` | ― | `NC` | ― |
| **31** | `GPIO20` | `/KEY18` | キー `[0, 1]` | `/KEY7` | キー `[6, 4]` |
| **32** | **`GPIO21`** | **`+3V3`** | **左右判定 (HIGH)** | **`GNDR`** | **左右判定 (LOW)** |
| **34** | `GPIO22` | `NC` | ― | `/KEY2` | キー `[6, 5]` |
| **35** | `GPIO23` | `/KEY13` | キー `[0, 2]` | `/KEYEX2` | キー `[5, 6]` |
| **36** | `GPIO24` | `/KEY14` | キー `[1, 2]` | **`/WHEEL_SDA`** | **`rU6` (`TMAG5273`) `I2C0 SDA`** |
| **37** | `GPIO25` | `/KEY15` | キー `[2, 2]` | **`/WHEEL_SCL`** | **`rU6` (`TMAG5273`) `I2C0 SCL`** |
| **38** | `GPIO26` | `/KEY12` | キー `[0, 3]` | `/KEY3` | キー `[5, 5]` |
| **39** | `GPIO27` | `/KEY11` | キー `[1, 3]` | `/KEY4` | キー `[4, 5]` |
| **40** | `GPIO28` | `/KEY10` | キー `[2, 3]` | `/KEY6` | キー `[5, 4]` |
| **41** | `GPIO29` | `/KEY5` | キー `[0, 4]` | `/KEY10` | キー `[6, 3]` |
| **46 / 47** | `USB_DM / DP` | `Net-(U1-USB_*)` | PC側 USB (`27 Ω` 経由) | `Net-(rU1-USB_*)` | PC側 USB (`27 Ω` 経由) |
| **51〜56** | `QSPI_*` | `/QSPI_*` | Flash `U4` ＆ `SMDSW1` | `/QSPI_*` | Flash `rU4` ＆ `rSMDSW1` |

---

## 5. PCBA 実装部品・THT 部品一覧（LCSC 番号リファレンス）

3-in-1 パネル上では、左手はそのまま、右手は `r*`、TBセンサー基板は `p*` のプレフィックスが付与されます。

| カテゴリ | 左リファレンス | 右メイン / TBセンサー | 型番・値 | LCSC 番号 | パッケージ | 左数 | 右+TB数 |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **MCU** | `U1` | `rU1` | `RP2040` | `C2040` | `QFN-56-1EP_7x7mm` | 1 | 1 |
| **QSPI Flash** | `U4` | `rU4` | `W25Q128JVSIQ` (16MB) | `C113767` (Basic互換 `C97521`) | `SOIC-8_5.3x5.3mm` | 1 | 1 |
| **3.3V LDO** | `U2` | `rU2` | `LDL1117S33R` | `C435835` | `SOT-223-3_TabPin2` | 1 | 1 |
| **ESD 保護 IC** | `U3, U5` | `rU3, rU5` | `USBLC6-2SC6` | `C7519` | `SOT-23-6` | 2 | 2 |
| **水晶振動子** | `Y1` | `rY1` | `12MHz 18pF` | `C91749` | `SMD_3225-4Pin` | 1 | 1 |
| **ショットキーD** | `ZD1` | `rZD1` | `1N5819WS` | `C191023` (Basic) | `D_SOD-323` | 1 | 1 |
| **スイッチングD** | `D1` | `rD1` | `1N4148WS` | `C2128` (Basic) | `D_SOD-323` | 1 | 1 |
| **3DホールIC** | ― | `rU6` | `TMAG5273A1QDBVR` | `C3716049` | `SOT-23-6` | 0 | 1 |
| **USB-C (16P)** | `J1, J2` | `rJ1, rJ2` | `TYPE-C-31-M-13C` | `C2848620` (Standard) | `kbd:TYPE-C-31-M-13C` | 2 | 2 |
| **タクトSW** | `SMDSW1, 2` | `rSMDSW1, 2` | `TS-1088R-02026` | `C455280` | `kbd:TS-1088R-02026` | 2 | 2 |
| **逆付け RGB LED** | `LED1..18, EXLED1..3` | `rLED2..18, rEXLED2` | `YS-SK6812MINI-E` | `C5149201` (Standard/Bake) | `kbd:YS-SK6812MINI-E` | 21 | 18 |
| **Choc ソケット** | `SW1..18, EXSW1..3` | `rSW2..18, rEXSW2` | `CPG135001S30` | `C5333465` | `kbd:choc12_hotswap` | 21 | 18 |
| **MLCC (0402)** | `C1`〜`C17` | `rC1`〜`rC18` | `100nF` / `1uF` / `10uF` / `27pF` | `C1525` / `C52923` / `C15525` / `C1557` | `0402` (Basic/Ext) | 17 | 18 |
| **抵抗 (0402)** | `R1`〜`R10` | `rR1`〜`rR13` | `27` / `1k` / `5.1k` / `5.6k` / `10k` / `4.7k` / `0` | `C2909343` / `C11702` / `C25905` / `C25908` / `C25744` / `C25900` / `C17168` | `0402` | 10 | 13 |
| **JST SH 6P** | ― | `rJ3` / `pJ1` (`J1`) | `SM06B-SRSS-TB(LF)(SN)` | `C160405` | `JST_SH_1x06_Horiz` | 0 | 1 + 1 |
| **1.8V LDO** | ― | `pU2` (`U2`) | `TLV74318PDBVR` | `C485152` | `SOT-23-5` | 0 | 1 |
| **MLCC (0603)** | ― | `pC1`〜`pC4` (`C5` DNP) | `4.7uF` / `100nF` / `1uF`(2) | `C19666` / `C14663` / `C15849` | `0603` (Basic) | 0 | 4 |
| **抵抗 (0603)** | ― | `pR1`〜`pR3` (`R4` DNP) | `10k`(2) / `39R`(1) | `C25804` / `C23154` | `0603` | 0 | 3 |
| **手ハンダ THT** | ― | `rEXSW1` / `pU1` (`U1`) | `Kailh Square Silent` / `PMW3360DM-T2QU` | PCBA 除外（手ハンダ） | 専用 THT | 0 | 1 + 1 |
| **銅箔 / DNP** | `J4` (DNP) | `rJ4`, `pR4`, `pC5`, `pJP1` | SWD 端子 / 予備 RC / ブリッジ済ジャンパ | PCBA 除外 | ― | 0 | 0 |
