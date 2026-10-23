# curcur40 PCB・回路設計仕様書 (PCB & Schematic Specification)

本書は、エルゴノミクス分割キーボード **curcur40**（トラックボール・CKW12ホイール一体型、Choc v2 ロープロファイル）の左右メイン基板（PCB）および回路図の設計基準書です。
ケース設計仕様書（[case_spec.md](./case_spec.md)）と対をなし、基板構成・回路仕様・ピンアサイン・ライブラリ管理・DRC/ERC検証基準を定義します。

> **【運用ルール】**
> 1. **対象バージョン**: KiCad **10.0**（10.0.7以降）を基準環境とします。
> 2. **標準ライブラリ準拠（シャドウ定義の禁止）**:
>    - KiCad公式標準ライブラリ（`MCU_RaspberryPi`, `Device`, `Diode`, `Connector`, `Capacitor_SMD`, `Resistor_SMD`, `Package_DFN_QFN`, `Package_SO` 等）をプロジェクトローカルのテーブルで上書き（シャドウイング）してはなりません。
>    - プロジェクト固有ライブラリは [pcbs/common/kbd/](../pcbs/common/kbd) 配下の `kbd` および `PMW3360_PCB` のみとします。
> 3. **設計変更の手順**:
>    - 回路・ピン配置・基板寸法を変更する場合、まず本書（[docs/pcb_spec.md](./pcb_spec.md)）の該当箇所を更新し、レビュー合意後に回路図（`.kicad_sch`）および基板（`.kicad_pcb`）へ反映します。
>    - 変更後は必ず `kicad-cli` による ERC および DRC（`--schematic-parity` 含む）を実行し、本書の第6節に定める品質基準を満たすことを検証します。

---

## 1. ファイル・ライブラリ構成 (Project & Library Structure)

### 1.1 プロジェクトファイル一覧

| 区分 | 左手用 (`curcur40-left`) | 右手メイン (`curcur40-right`) | トラックボールセンサー (`curcur40-pmw3360`) | 役割 |
| :--- | :--- | :--- | :--- | :--- |
| **プロジェクト設定** | [curcur40-left.kicad_pro](../pcbs/left/curcur40-left.kicad_pro) | [curcur40-right.kicad_pro](../pcbs/right/curcur40-right.kicad_pro) | [curcur40-pmw3360.kicad_pro](../pcbs/pmw3360/curcur40-pmw3360.kicad_pro) | デザインルール・DRC/ERC設定 |
| **回路図 (Schematic)** | [curcur40-left.kicad_sch](../pcbs/left/curcur40-left.kicad_sch) | [curcur40-right.kicad_sch](../pcbs/right/curcur40-right.kicad_sch) | [curcur40-pmw3360.kicad_sch](../pcbs/pmw3360/curcur40-pmw3360.kicad_sch) | 回路論理・シンボル定義 |
| **基板レイアウト (PCB)** | [curcur40-left.kicad_pcb](../pcbs/left/curcur40-left.kicad_pcb) | [curcur40-right.kicad_pcb](../pcbs/right/curcur40-right.kicad_pcb) | [curcur40-pmw3360.kicad_pcb](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb) | パターン配線・外形・シルク |
| **シンボルテーブル** | [left/sym-lib-table](../pcbs/left/sym-lib-table) | [right/sym-lib-table](../pcbs/right/sym-lib-table) | [pmw3360/sym-lib-table](../pcbs/pmw3360/sym-lib-table) | カスタムシンボル登録 |
| **フットプリントテーブル** | [left/fp-lib-table](../pcbs/left/fp-lib-table) | [right/fp-lib-table](../pcbs/right/fp-lib-table) | [pmw3360/fp-lib-table](../pcbs/pmw3360/fp-lib-table) | カスタムフットプリント登録 |

### 1.2 ライブラリ管理ポリシー

`sym-lib-table` および `fp-lib-table` には、以下の**プロジェクト固有カスタムライブラリのみ**を登録します。汎用部品はすべて KiCad 10.0 標準ライブラリ（`${KICAD10_SYMBOL_DIR}` / `${KICAD10_FOOTPRINT_DIR}`）を直接参照します（同ディレクトリ内に存在する `corne-cherry` / `corne-chocolate` 専用のファイル群は `curcur40` では使用しません）。

| ライブラリ名 | 種別 | パス | `curcur40` で使用している固有定義 |
| :--- | :--- | :--- | :--- |
| **`kbd`** | シンボル | [pcbs/common/kbd/kicad-symbols/kbd.kicad_sym](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | 右手用電源シンボル（`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`）、逆付けRGB LED（`YS-SK6812MINI-E`） |
| **`PMW3360_PCB`** | シンボル | [pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | 光学センサー（`PMW3360DM-T2QU`）、1.8V LDO（`TLV74318PDBVR`） |
| **`kbd`** | フットプリント | [pcbs/common/kbd/kicad-footprints/kbd.pretty](../pcbs/common/kbd/kicad-footprints/kbd.pretty) | 下記 **1.3節** の計7種類のカスタムフットプリントのみ使用 |

### 1.3 `curcur40` で使用するプロジェクト固有ライブラリデータの入手元と改変履歴

`pcbs/common/kbd/` 配下のうち、`curcur40` で実際に使用している**回路図シンボル（2ファイル）**および**フットプリント（7ファイル）**のデータ入手元（公開リポジトリ）と、KiCad 10.0 対応時のローカル調整内容は以下の通りです。

#### ① 回路図シンボルライブラリ（`.kicad_sym`）

| ライブラリ / シンボル名 | ファイルパス | データ入手元（公開リポジトリ） | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **`kbd`**<br>(`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`, `YS-SK6812MINI-E`) | [kbd.kicad_sym](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | **foostan/kbd**<br>(`https://github.com/foostan/kbd` — Corne v4 公式 KiCad ライブラリ、[MIT License](../pcbs/common/kbd/LICENSE)。`git subtree` で取得) | `2026-10-22`: 未使用シンボルを削除し、`YS-SK6812MINI-E` の Pin 2 (`DOUT`) が元データで `power_in` になっていたため、KiCad 10.0 ERC 対応としてデータシート通り `output` にローカル修正 |
| **`PMW3360_PCB`**<br>(`PMW3360DM-T2QU`, `TLV74318PDBVR`) | [pmw3360_pcb.kicad_sym](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | **siderakb/pmw3360-pcb**<br>(`https://github.com/siderakb/pmw3360-pcb` — PMW3360 ブレイクアウト基板 OSS、[CERN-OHL-P v2](../LICENSE_CERN_OHL_P_V2)) | `2026-10-22`: 未使用の `TXS0108E-QPWRQ1` シンボルを削除し、`PMW3360DM-T2QU` の Pin 3 (`VDDPIX`) を内部レギュレータ出力仕様に合わせて `power_in` から `power_out` にローカル修正 |

#### ② フットプリントライブラリ（`kbd.pretty/*.kicad_mod`）および 3Dモデル

| フットプリント名 (`kbd:`) | 対象部品 / 回路図シンボル | データ入手元（公開リポジトリ） | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **[`keyswitch_choc12_hotswap_1u.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/keyswitch_choc12_hotswap_1u.kicad_mod)** | Kailh Choc ソケット (`CPG135001S30`)<br>`Switch:SW_Push` | **foostan/kbd**<br>(`keyswitch_choc12_hotswap_1u.kicad_mod` ＋ `kailh_choc_socket.step`, [MIT License](../pcbs/common/kbd/LICENSE)) | `2026-10-22`: 旧 Corne V3 由来の不要な $\varnothing 0.40\,\text{mm}$ NPTH 穴（`(-5, -5.15)`）および個別の `(solder_mask_margin -0.2)` 指定を削除し、3D モデル参照パスを環境非依存の `${KIPRJMOD}/../common/kbd/...` に修正 |
| **[`YS-SK6812MINI-E.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/YS-SK6812MINI-E.kicad_mod)** | 逆付け RGB LED (`YS-SK6812MINI-E`)<br>`kbd:YS-SK6812MINI-E` | **foostan/kbd**<br>(`YS-SK6812MINI-E.kicad_mod` ＋ `YS-SK6812MINI-E.step`, [MIT License](../pcbs/common/kbd/LICENSE)) | `2026-10-22`: パッド上のシルク重なり回避微調整、および 3D モデル参照パス（元データの `/Users/foostan/...`）を `${KIPRJMOD}/../common/kbd/...` に修正 |
| **[`TS-1088R-02026.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/TS-1088R-02026.kicad_mod)** | SMD タクトSW (`TS-1088R-02026`)<br>`Switch:SW_Push` | **foostan/kbd**<br>(`TS-1088R-02026.kicad_mod` ＋ `TS-1088R-02026.step`, [MIT License](../pcbs/common/kbd/LICENSE)) | `2026-10-22`: 形状変更なし。3D モデル参照パスを環境非依存の `${KIPRJMOD}/../common/kbd/...` に修正 |
| **[`USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod)** | USB-C 16ピン (`TYPE-C-31-M-13C`)<br>`Connector:USB_C_Receptacle_USB2.0_16P` | **foostan/kbd** の `TYPE-C-31-M-13C.kicad_mod`（＋ `TYPE-C-31-M-13C.step`, [MIT License](../pcbs/common/kbd/LICENSE)）が元データ | `2026-10-22`: 標準シンボル `USB_C_Receptacle_USB2.0_16P` のフィルタ（`USB*C*Receptacle*`）に適合するよう**ローカルでリネーム**し、シールド脚 `SH` のピン名整合・3D モデルパス修正を実施 |
| **[`Jack_PJ-398A-5A_PJ-399B-6A.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/Jack_PJ-398A-5A_PJ-399B-6A.kicad_mod)** | 3.5mm ジャック (`PJ-398A-5A`)<br>`Connector_Audio:AudioJack3` | **foostan/kbd** の `PJ-398A-5A_PJ-399B-6A.kicad_mod`（＋ `PJ-398A-5A.step`, [MIT License](../pcbs/common/kbd/LICENSE)）が元データ | `2026-10-22`: 標準シンボル `AudioJack3` のフィルタ（`Jack*`）に適合するよう**ローカルでリネーム**し、パッド番号を `1/2/3` から `T/R/S` に変更・3D モデルパス修正を実施 |
| **[`RotaryEncoder_Switch_CKW12.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/RotaryEncoder_Switch_CKW12.kicad_mod)** | ホイールエンコーダ (`CKW12`)<br>`Device:RotaryEncoder_Switch` | **kumamuk-git/CKW12** & **kumamuk-git/roBa**<br>(`https://github.com/kumamuk-git/CKW12` の `pcb/_footprint/CKW12.kicad_mod` ＋ `3dmodel/ckw12_*.stp` / `roBa` GPL-3.0) | `2026-10-22`: 標準シンボル `RotaryEncoder_Switch` のフィルタ（`RotaryEncoder*Switch*`）に適合するよう `CKW12.kicad_mod` から**ローカルでリネーム**し、3D モデル参照パスを `${KIPRJMOD}/../common/kbd/3dmodels/...` に設定、さらに `CKW12_top` サブ基板厚（$0.50\,\text{mm}$）に合わせて 3D オフセット `(0, 0, 0.5)` に補正 |
| **[`PMW3360DM-T2QU_16Pin.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)** | 光学センサー (`PMW3360DM-T2QU`)<br>`PMW3360_PCB:PMW3360DM-T2QU` | **siderakb/pmw3360-pcb**<br>(`https://github.com/siderakb/pmw3360-pcb` の `PMW3360DM-T2QU_16Pin.kicad_mod`, [CERN-OHL-P v2](../LICENSE_CERN_OHL_P_V2)) | `2026-10-22`: 元データをベースに、KiCad 10.0 でスルーホールパッドの銅箔定義欠落エラーを防ぐため `(layers "*.Cu" "*.Mask")` をローカル補完 |

> **【補足：`SW1` / `rSW1` のソケットフットプリント統一について】**
> 派生元の Corne Chocolate では内側親指キー（`SW1` / `rSW1`）に 1.5u キーキャップ用のガイド枠を持つ `keyswitch_choc12_hotswap_1.5u` が割り当てられていましたが、物理的なホットスワップソケット部品および銅箔パッド・穴径は `1u` と完全に同一であり、かつ `curcur40` では全キーが **1u キーキャップ構成** であるため、回路図・PCBともに全キーを `kbd:keyswitch_choc12_hotswap_1u` に統一しています。

---

## 2. 基板物理仕様・デザインルール (Board Physical Specs & Design Rules)

### 2.1 基板外形・層構成

| 項目 | 左手 PCB (`curcur40-left`) | 右手メイン PCB (`curcur40-right`) | センサーサブ PCB (`curcur40-pmw3360`) | 備考 |
| :--- | :---: | :---: | :---: | :--- |
| **基材・層数** | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | 銅箔厚 1 oz (35 µm) 標準 |
| **基板板厚** | **1.60 mm** | **1.60 mm** | **1.60 mm** | [case_spec.md](./case_spec.md) 第1節と完全同期 |
| **外形バウンディングボックス** | 幅 **124.325 mm** × 高さ **91.8125 mm** | 幅 **124.325 mm** × 高さ **91.8125 mm** | 幅 **29.575 mm** × 高さ **29.200 mm** | 右メイン基板は親指トラックボール領域を切欠き分離 |
| **PCB座標範囲 ($X$)** | $-119.0625 \sim +5.2625 \, \text{mm}$ | $-5.2625 \sim +119.0625 \, \text{mm}$ | $-5.2625 \sim +24.3125 \, \text{mm}$ | |
| **PCB座標範囲 ($Y$)** | $-24.3125 \sim +67.5000 \, \text{mm}$ | $-24.3125 \sim +67.5000 \, \text{mm}$ | $+38.3000 \sim +67.5000 \, \text{mm}$ | |
| **内部切り欠き穴** | なし | なし（親指内側は L字ノッチ切欠き） | **$8.70 \times 16.90 \, \text{mm}$ 角穴** | センサーサブ基板中央 $(9.525, 52.3875)$ に PMW3360/LM19 光学角穴 |
| **総フットプリント数** | 79 点 | 77 点 | 12 点 | |
| **総ネット数** | 78 ネット | 85 ネット | 10 ネット | |

### 2.2 DRC デザインルール（製造制約）

JLCPCB 等の標準 2層基板製造プロセスで追加料金なく高い歩留まりを確保できるルールを設定しています。

* **最小クリアランス**: `0.19 mm`（一部ネットクラス `0.20 mm`、0.5mmピッチ ESD保護IC `U3`/`rU3` のみ差動ペア通過部で `0.15 mm`）
* **最小配線幅**: `0.20 mm`（信号線標準 `0.20 mm` / `0.2032 mm`、電源ライン `0.25 mm` 〜 `0.508 mm`）
* **標準ビア寸法**: 外径 `0.50 mm` / ドリル径 `0.30 mm`（一部電源・信号ビアは外径 `0.60 mm` / ドリル径 `0.30 mm`）
* **ハンダマスク拡張 (`pad_to_mask_clearance`)**: **`0 mm`**（KiCad 10.0 標準の NSMD 設定。フットプリント個別のハンダマスクマージン上書きは一切使用しない）
* **銅箔ゾーン (` GND ` / ` GNDR `)**:
  * 表裏両面（`F.Cu` / `B.Cu`）全面ベタGNDプレーン配置。
  * サーマルリリーフ最小スポーク数: `2本`（すべてのGNDスルーホール・SMDパッドで2本以上のスポーク接続を確保）。

---

## 3. 左右基板の機能構成・相違点 (Left vs. Right Architecture)

curcur40 は Corne Chocolate (v4系 RP2040 オンボード設計) をベースとしつつ、左右で親指・人差し指内側の機能デバイスが非対称に構成されています。

| 機能ブロック | 左手 PCB (`curcur40-left`) | 右手 PCB (`curcur40-right`) | 詳細・備考 |
| :--- | :--- | :--- | :--- |
| **メインマイコン** | `U1` (`RP2040`) | `rU1` (`RP2040`) | 裏面（`B.Cu`）実装 |
| **QSPI フラッシュ** | `U4` (`W25Q128JVSIQ`, 16MB) | `rU4` (`W25Q128JVSIQ`, 16MB) | 裏面（`B.Cu`）実装、SOIC-8 (5.3×5.3mm) |
| **3.3V LDO レギュレータ** | `U2` (`NCP1117LPST33T3G`) | `rU2` (`NCP1117LPST33T3G`) | 5V (`VBUS`) → 3.3V (`+3V3` / `+3V3R`) |
| **キースイッチ数 (Choc)** | **21 キー**（すべて 1u） | **19 キー**（すべて 1u） | ダイレクトピン接続（マトリクスダイオード不要） |
| **RGB LED (SK6812MINI-E)** | **21 個** (`LED1`〜`18`, `EXLED1`〜`3`) | **19 個** (`rLED1`〜`18`, `rEXLED2`) | 各キースイッチ直下に配置（右親指トラックボール位置はLEDなし） |
| **ロータリーエンコーダ** | なし（通常キースイッチ `EXSW1`） | **CKW12 ホイール** (`rEXSW1`) | 右手内側上部に配置（A/B相回転 ＋ プッシュスイッチ `/KEYEX1`） |
| **トラックボールセンサー** | なし（親指4キー構成） | **JST SH 6ピンコネクタ (`rJ3`)** 経由で独立サブ基板 [`curcur40-pmw3360`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（`U1`: `PMW3360DM-T2QU` ＋ `U2`: `1.8V LDO` ＋ `J1`）と接続 | トラックボールカップ開口面をトッププレート天面（$Z = -2.00\,\text{mm}$）とフラッシュに沈み込ませるため、センサー基板を $-11.80\,\text{mm}$ 下段（$Z = -16.00\,\text{mm}$）へ分離配置 |
| **SWD デバッグ端子** | `J4` (`1x03` 2.54mm スルーホール) | `rJ4` (`1x03` 2.54mm スルーホール) | `/SWCLK`, `GND`, `/SWD`。**未実装 (`DNP`)**・BOM/Pos/3Dモデル非表示 |
| **左右判定ピン (`GPIO21`)** | **`+3V3` (HIGH) に直結** | **`GNDR` (LOW) に直結** | QMK `split.handedness.pin = GP21` による自動左右認識 |
| **M2 スペーサー貫通穴** | **5 箇所**（外周 `L1`〜`L5`） | **右メイン 5 箇所**（外周 `R1`〜`R5`、左手と完全対称）＋ **センサー基板 4 箇所**（`TB1`〜`TB4`） | すべて **$\varnothing 3.30 \, \text{mm}$** 非スルーホール（NPTH相当のEdge.Cuts円穴） |

---

## 4. 回路ブロック別詳細仕様 (Detailed Circuit Specifications)

### 4.1 電源回路と左右間電源分離
1. **USB 5V 入力と逆流防止**:
   - USB Type-C コネクタ（`J1` / `rJ1`）の `VBUS` ピンから逆流防止ショットキーバリアダイオード **`ZD1` / `rZD1` (`RB521S30T1G`)** を経由して内部 5V ライン（`+5V` / `+5VR`：RGB LED 電源、3.3V LDO 入力、および TRRS ジャック経由の対向基板電源）へ供給されます（なお `D1` / `rD1` [`1N4148WT`] は `QSPI_SS` の BOOT スイッチ回路に使用されます）。
2. **VBUS 接続検出 (`/USB_VBUS_PIN`)**:
   - USB `VBUS` を **`R8` (`5.6kΩ`) および `R9` (`10kΩ`)**（右手は `rR8` / `rR9`）で分圧し、`RP2040` の Pin 16 (`GPIO13` / `/USB_VBUS_PIN`) に入力することで、どちらの基板に USB ケーブルが挿さっているか（マスター/スレーブ判定）を検出します。
3. **3.3V ロジック電源 (`+3V3` / `+3V3R`) と左右間 TRRS 接続 (`J2` / `rJ2`)**:
   - TRRS/TRS ジャック `J2` / `rJ2`（`PJ-398A-5A`）は **`+5V` (`+5VR`)**、`GND` (`GNDR`)、およびシリアル通信線 `/TX` の 3本を左右基板間で接続し、各基板上の LDO `U2` / `rU2` (`NCP1117LPST33T3G`) が `+5V` (`+5VR`) からそれぞれのローカル `+3V3` / `+3V3R` を生成して `RP2040` の `IOVDD` / `USB_VDD` / `ADC_AVDD`、QSPI フラッシュ、および右手 PMW3360 用 1.8V LDO `U2` (`TLV74318PDBVR`) へ供給します。

### 4.2 左右判定ピン (`RP2040` Pin 32 `GPIO21`) の設計と ERC 警告の扱い
* **設計意図**:
  * [kbd_firmware/keyboards/curcur40/qmk/qmk_firmware/rev1/keyboard.json](../kbd_firmware/keyboards/curcur40/qmk/qmk_firmware/rev1/keyboard.json#L50-L52) において `"handedness": { "pin": "GP21" }` が設定されています。
  * 左右の基板に同一のファームウェアバイナリを書き込んでも起動時に自動で左右を判別できるよう、ハードウェア上で以下の通り固定結線しています：
    * **左手 (`U1` Pin 32 `GPIO21`)**: **`+3V3`**（HIGH）に直結
    * **右手 (`rU1` Pin 32 `GPIO21`)**: **`GNDR`**（LOW）に直結
* **KiCad ERC 警告の扱い（意図的な保持）**:
  * KiCad 10.0 純正の `MCU_RaspberryPi:RP2040` シンボルでは Pin 32 (`GPIO21`) が `Bidirectional` 属性であり、電源出力（`Power output`）である `+3V3` / `GNDR`（`PWR_FLAG` 付）と直結されるため、ERC 実行時に `[pin_to_pin]: ピンのタイプ Bidirectional と Power output が接続されています` という警告が左右それぞれ **1件のみ** 出力されます。
  * この警告を消すために標準シンボルを改変したり ERC の `pin_to_pin` チェック自体を無効化すると、他のピンでの意図しない電源ショートを見落とすリスクが生じるため、**標準シンボルを維持したままこの正当な警告 1件のみを残す** のを curcur40 の正式仕様とします。

### 4.3 右手専用：光学トラックボールセンサー基板 (`curcur40-pmw3360`) と JST SH 6ピン接続 (`rJ3` / `J1`)

トラックボールカップの円形リム天面をトッププレート表面（$Z = -2.00\,\text{mm}$）と同じ高さまで $-11.80\,\text{mm}$ 沈み込ませる低プロファイル設計に伴い、光学センサー `U1` (`PMW3360DM-T2QU`) とその周辺回路は独立したセンサーサブ基板 **[`pcbs/pmw3360/curcur40-pmw3360.kicad_pcb`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)**（配置高さ $Z = -17.60 \sim -16.00\,\text{mm}$）に分離し、右手メイン基板（$Z = -5.80 \sim -4.20\,\text{mm}$）と **JST SH 1.0mm ピッチ 6ピン横向き SMD コネクタ（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160404`）および 6ピン両端ハーネス** で接続します。

#### ⓪ 基板間コネクタ `rJ3`（右メイン基板）↔ `J1`（センサーサブ基板）のピンアサイン
* **回路図シンボル**: `Connector_Generic_MountingPin:Conn_01x06_MountingPin`
* **フットプリント**: `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal`
* **配置座標**:
  * 右メイン基板 `rJ3`: `B.Cu` $(46.5000, 63.0000)\,\text{mm}$, 回転 $+90^\circ$（ケーブル挿入口は西向き $-X$、`rSW1` ソケット東端との間に $6.34\,\text{mm}$ の挿抜クリアランスを確保してセンサー基板 `J1` と正対）
  * センサーサブ基板 `J1`: `B.Cu` $(20.2000, 52.3875)\,\text{mm}$, 回転 $-90^\circ$（ケーブル挿入口は東向き $+X$、メイン基板 `rJ3` と正対）
* **ピン割り当て（北側 $-Y$ から南側 $+Y$ への物理並び順を両基板で完全一致させ、市販の両端同方向フラットケーブルをひねらず真っ直ぐ接続可能）**:
  * **北端（`J1` Pin 1 / `rJ3` Pin 6）**: `+3V3R`（3.3V 電源）
  * **北から2番目（`J1` Pin 2 / `rJ3` Pin 5）**: `GNDR`（グラウンド）
  * **北から3番目（`J1` Pin 3 / `rJ3` Pin 4）**: `/SCLK`（SPI クロック、`rU1` `GPIO14`）
  * **北から4番目（`J1` Pin 4 / `rJ3` Pin 3）**: `/MOSI`（SPI MOSI、`rU1` `GPIO11`）
  * **北から5番目（`J1` Pin 5 / `rJ3` Pin 2）**: `/MISO`（SPI MISO、`rU1` `GPIO8`）
  * **南端（`J1` Pin 6 / `rJ3` Pin 1）**: `/NCS`（SPI チップセレクト、`rU1` `GPIO6`）
  * **Pin MP (補強タブ)**: `GNDR`

#### ① `VDDPIX`（内部ピクセルアレイ電源）と `/+1V8_PMW`（1.8V供給電源）の完全分離
> **【重要設計ルール】**
> `PMW3360DM-T2QU` の **Pin 3 (`VDDPIX`)** はセンサー内部レギュレータの出力ピン（`power_out`）であり、外部 1.8V 電源ライン（`/+1V8_PMW`）とショートさせてはなりません。

| ネット名 | 接続ピン・部品 | 役割・仕様 |
| :--- | :--- | :--- |
| **`Net-(U1-VDDPIX)`** | `U1` Pin 3 (`VDDPIX`), `C1` Pad 1 (`4.7uF`), `C2` Pad 1 (`100nF`) | 内部ピクセル電源のデカップリング専用独立ネット。他の電源へは一切接続しない |
| **`/+1V8_PMW`** | `U2` Pin 5 (`OUT`), `C4` Pad 1 (`1uF`), `U1` Pin 4 (`VDD`), `R3` Pad 1 (`39Ω`), `R4` Pad 1 (`28kΩ`, `DNP`), `JP1` Pad 3 | 1.8V LDO (`TLV74318PDBVR`) 出力。センサーコア電源 (`VDD`) および内部LED電流供給 (`R3` 経由 `LED_P`) |
| **`/V_{IO}`** | `JP1` Pad 2 (Pad 1 `+3V3R` と基板内銅箔直結), `U1` Pin 5 (`VDDIO`), `R1` Pad 1 (`10kΩ` `/RESET` プルアップ), `R2` Pad 1 (`10kΩ` `/MISO` プルアップ) | センサー I/O 電圧ライン。`JP1` の内蔵銅箔ブリッジにより `+3V3R` (3.3V) が供給される |

#### ② 電圧選択ソルダージャンパー `JP1`（Pad 1–2 基板内直結仕様）および `R4` / `C5`（DNP）
* **`JP1` (`Jumper:SolderJumper_3_Bridged12` / `Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels`)**:
  * 基板裏面（`B.Cu`）の `(17.775, 50.1457)` に配置されています：
    * **Pad 1**: `+3V3R`
    * **Pad 2**: `/V_{IO}` (`U1` Pin 5 `VDDIO`)
    * **Pad 3**: `/+1V8_PMW`
  * はんだブリッジ忘れや逆ブリッジ（Pad 2–3 短絡）による動作不良を防ぐため、KiCad 10.0 標準のブリッジ済みフットプリント（`(net_tie_pad_groups "1, 2")` により **Pad 1–2 間が `B.Cu` 銅箔ポリゴンで最初から直結**、Pad 3 は開放）を採用しています。組み立て時の手作業によるジャンパはんだ付けは不要です。
* **`R4` (`28kΩ`) および `C5` (`22nF`) の DNP（未実装）化**:
  * 派生元回路（可変出力または別型番 LDO 使用時）の名残であり、現在の固定 1.8V LDO `U2` (`TLV74318PDBVR`) では Pin 4 が `NC`（未接続）であるため機能しません。
  * パターン・フットプリントは基板上に残しつつ、回路図および PCB の双方で **未実装（`DNP`）・部品表（BOM）除外・実装座標（CPL/Pos）除外・3Dモデル非表示** に設定しています。

### 4.4 右手専用：ロータリーエンコーダ `CKW12` (`rEXSW1`)
* 遊舎工房 / kumamuk 氏設計の **CKW12**（薄型ホイールエンコーダ＋プッシュスイッチ）を右手内側上部 `(14.2875, 0.0)` の表面（`F.Cu`）に配置。
* **ピン接続**:
  * **Pad A**: `/RE0A` → `rU1` Pin 36 (`GPIO24`)
  * **Pad B**: `/REB` → `rU1` Pin 9 (`GPIO7`)
  * **Pad C**: `GNDR`
  * **Pad S1**: `GNDR`
  * **Pad S2**: `/KEYEX1` → `rU1` Pin 37 (`GPIO25`、マトリクス座標 `[4, 6]` のプッシュスイッチとして動作)
* **実装構造と 3D モデルの向き（AI 監査時の誤認防止ルール）**:
  1. **メイン基板に M2 ネジ穴がなくて正常**: 公式 [`kumamuk-git/CKW12`](https://github.com/kumamuk-git/CKW12) キットは、付属の専用サブ基板 **`CKW12_top`（板厚約 $0.50\,\text{mm}$）** の裏側から **M2 × 3.5mm ネジ 4本** で 3Dプリントハウジング（`ckw12_housing`）四隅を固定し、その `CKW12_top` から下へ突き出た **コンスルー 5ピン（2.54mm ピッチ）** をメイン基板 `rEXSW1` の 5つのスルーホール（`A, B, C, S1, S2`）に挿して実装する構造です。メイン基板自体に M2 ネジ穴を設ける必要はありません。
  2. **3D モデルの回転角 `(rotate (xyz 0 0 90))` を変更しないこと**: `CKW12` は人差し指で**上下方向（南北方向）に転がすホイール**です。メイン基板上の 5ピンが北側3ピン（`A, B, C`）・南側2ピン（`S1, S2`）に並んでいるのは `CKW12_top` サブ基板内の配線引き回しによるものであり、フットプリント [`RotaryEncoder_Switch_CKW12.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/RotaryEncoder_Switch_CKW12.kicad_mod) の 3D モデル設定 `(rotate (xyz 0 0 90))`（および [`scripts/generate_full_assembly.py`](../scripts/generate_full_assembly.py) の `Rotation(0, 0, -90)`）が正しい向きです。

### 4.5 SWD デバッグ用スルーホール端子 (`J4` / `rJ4`)
* ベース基板（Corne Chocolate v4）由来の RP2040 SWD デバッグ端子（Pad 1: `/SWCLK`, Pad 2: `GND`/`GNDR`, Pad 3: `/SWD`）として、小指側外周付近（左 `J4`: `(-106.8675, 22.37625)`、右 `rJ4`: `(111.8475, 22.43125)`）に `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` フットプリントが配置されています。
* **通常使用時はピンヘッダを実装しない（空きランドのままにする）** ため、回路図およびPCBの双方で **未実装（`DNP`）・部品表（BOM）除外・実装座標（Pos）除外** に設定しています（これにより KiCad の 3D ビューアでもピンヘッダの 3D モデルは非表示となります）。

---

## 5. RP2040 ピンアサイン対応表 (MCU Pin Assignment Table)

左右の `RP2040`（左 `U1` / 右 `rU1`）の全GPIO・制御ピンの割り当て一覧です。

| Pin番号 | RP2040 ピン名 | 左手 (`U1`) ネット名 | 左手 機能 | 右手 (`rU1`) ネット名 | 右手 機能 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **2** | `GPIO0` | `/KEY4` | キー `[0, 5]` | `/KEY11` | キー `[5, 3]` |
| **3** | `GPIO1` | `/KEY6` | キー `[1, 4]` | `/KEY5` | キー `[4, 4]` |
| **4** | `GPIO2` | `/KEY3` | キー `[1, 5]` | `/KEY12` | キー `[4, 3]` |
| **5** | `GPIO3` | `/KEY7` | キー `[2, 4]` | `/KEY13` | キー `[4, 2]` |
| **6** | `GPIO4` | `/KEYEX1` | キー `[0, 6]` | `/KEY14` | キー `[5, 2]` |
| **7** | `GPIO5` | `/KEYEX3` | キー `[3, 6]` | `/KEY15` | キー `[6, 2]` |
| **8** | `GPIO6` | 未接続 (`NC`) | （エンコーダA予備） | **`/NCS`** | **PMW3360 SPI CS** |
| **9** | `GPIO7` | 未接続 (`NC`) | （エンコーダB予備） | **`/REB`** | **CKW12 エンコーダ B相** |
| **11** | `GPIO8` | `/KEYEX2` | キー `[1, 6]` | **`/MISO`** | **PMW3360 SPI MISO** |
| **12** | `GPIO9` | `/KEY2` | キー `[2, 5]` | `/KEY18` | キー `[4, 1]` |
| **13** | `GPIO10` | `/LED` | RGB LED `DIN` (`GP10`) | `/LED` | RGB LED `DIN` (`GP10`) |
| **14** | `GPIO11` | `/KEY1` | キー `[3, 5]` | **`/MOSI`** | **PMW3360 SPI MOSI** |
| **15** | `GPIO12` | `/TX` | 左右間 TRRS シリアル通信 | `/TX` | 左右間 TRRS シリアル通信 |
| **16** | `GPIO13` | `/USB_VBUS_PIN` | VBUS 検出 | `/USB_VBUS_PIN` | VBUS 検出 |
| **17** | `GPIO14` | `/KEY9` | キー `[3, 3]` | **`/SCLK`** | **PMW3360 SPI SCLK** |
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
| **36** | `GPIO24` | `/KEY14` | キー `[1, 2]` | **`/RE0A`** | **CKW12 エンコーダ A相** |
| **37** | `GPIO25` | `/KEY15` | キー `[2, 2]` | **`/KEYEX1`** | **CKW12 プッシュSW `[4, 6]`** |
| **38** | `GPIO26` | `/KEY12` | キー `[0, 3]` | `/KEY3` | キー `[5, 5]` |
| **39** | `GPIO27` | `/KEY11` | キー `[1, 3]` | `/KEY4` | キー `[4, 5]` |
| **40** | `GPIO28` | `/KEY10` | キー `[2, 3]` | `/KEY6` | キー `[5, 4]` |
| **41** | `GPIO29` | `/KEY5` | キー `[0, 4]` | `/KEY10` | キー `[6, 3]` |
| **46** | `USB_DM` | `Net-(U1-USB_DM)` | USB D- (`27Ω` 経由) | `Net-(rU1-USB_DM)` | USB D- (`27Ω` 経由) |
| **47** | `USB_DP` | `Net-(U1-USB_DP)` | USB D+ (`27Ω` 経由) | `Net-(rU1-USB_DP)` | USB D+ (`27Ω` 経由) |
| **51〜56** | `QSPI_*` | `/QSPI_*` | Flash `U4` & `SMDSW1` | `/QSPI_*` | Flash `rU4` & `rSMDSW1` |

---

## 6. 固定穴・機械的インターフェース仕様 (Mechanical Mounting & Holes)

ケース設計仕様書（[case_spec.md](./case_spec.md) 第2.3節）と完全一致する、M2 メスメススペーサー（外径 $\varnothing 3.0\,\text{mm}$）貫通用の円穴（`Edge.Cuts` レイヤー、直径 **$\varnothing 3.30 \, \text{mm}$**）の配置定義です。

### 6.1 左手 PCB (`curcur40-left.kicad_pcb`) — 計5箇所

| 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 穴径 (`Edge.Cuts`) | 備考 |
| :---: | :--- | :---: | :---: | :--- |
| **L1** | 内側上（USB-C横） | $(0.0000, -15.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L2** | 内側下（TRRS上） | $(0.0000, 25.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L3** | 小指側上 | $(-109.5375, -20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L4** | 小指側下 | $(-98.0000, 38.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L5** | 親指側下（`SW1` 南側） | $(-33.3375, 64.3000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周スペーサー貫通穴（右手 `R5` と完全左右対称） |

### 6.2 右手メイン PCB (`curcur40-right.kicad_pcb`) — 計5箇所（左手と完全対称）および センサーサブ PCB (`curcur40-pmw3360.kicad_pcb`) — 計4箇所

右手メイン基板は親指トラックボール領域が分離されているため、`rSW1` 南側の $(33.3375, 64.3000)$ に親指外周穴 **`R5`**（左手 `L5` と完全対称）を配置して親指キー領域のたわみを防止します。分離されたセンサーサブ基板（`curcur40-pmw3360`）は `TB1`〜`TB4` の4箇所でケース下段ボス天面（$Z = -17.60\,\text{mm}$）とトラックボールカップ底面（$Z = -16.00\,\text{mm}$）にサンドイッチ固定されます（スペーサーがセンサー基板の $\varnothing 3.30\,\text{mm}$ 穴を貫通してカップ耳下段の深さ $3.90\,\text{mm}$・穴径 $\varnothing 3.30\,\text{mm}$ 受け穴に進入）。

| 基板 | 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 穴径 (`Edge.Cuts`) | 備考 |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **右メイン (`curcur40-right`)** | **R1** | 外周・内側上（USB-C横） | $(0.0000, -15.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R2** | 外周・内側下（TRRS上） | $(0.0000, 25.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R3** | 外周・小指側上 | $(109.5375, -20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R4** | 外周・小指側下 | $(98.0000, 38.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R5** | 外周・親指側下（`rSW1` 南側） | $(33.3375, 64.3000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴（左手 `L5` と左右対称） |
| **センサー (`curcur40-pmw3360`)** | **TB1** | トラックボール北西 (NW) | $(-2.4750, 41.0875)$ | $\varnothing 3.30 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(-12.0, -11.3)$、5.50mm スペーサー貫通 |
| **センサー (`curcur40-pmw3360`)** | **TB2** | トラックボール北東 (NE) | $(21.5250, 41.0875)$ | $\varnothing 3.30 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(+12.0, -11.3)$、5.50mm スペーサー貫通 |
| **センサー (`curcur40-pmw3360`)** | **TB3** | トラックボール南西 (SW) | $(-2.4750, 63.6875)$ | $\varnothing 3.30 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(-12.0, +11.3)$、5.50mm スペーサー貫通 |
| **センサー (`curcur40-pmw3360`)** | **TB4** | トラックボール南東 (SE) | $(21.5250, 63.6875)$ | $\varnothing 3.30 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(+12.0, +11.3)$、5.50mm スペーサー貫通 |

---

## 7. 実装部品表 (BOM Summary)

| カテゴリ | リファレンス (左) | リファレンス (右) | 型番 / 値 | パッケージ / フットプリント | 実装面 | 左数量 | 右数量 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **MCU** | `U1` | `rU1` | `RP2040` | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | `B.Cu` | 1 | 1 |
| **QSPI Flash** | `U4` | `rU4` | `W25Q128JVSIQ` | `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | `B.Cu` | 1 | 1 |
| **3.3V LDO** | `U2` | `rU2` | `NCP1117LPST33T3G` | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | `B.Cu` | 1 | 1 |
| **ESD 保護 IC** | `U3` | `rU3` | `TPD4E05U06DQAR` | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | `B.Cu` | 1 | 1 |
| **水晶振動子** | `Y1` | `rY1` | `12MHz 18pF` | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` | `B.Cu` | 1 | 1 |
| **ショットキーD** | `ZD1` | `rZD1` | `RB521S30T1G` | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **スイッチングD** | `D1` | `rD1` | `1N4148WT` | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **コンデンサ (0402)** | `C1`〜`C16` | `rC1`〜`rC16` | `100n`(9), `1u`(3), `10u`(2), `27p`(2) | `Capacitor_SMD:C_0402_1005Metric` | `B.Cu` | 16 | 16 |
| **抵抗 (0402)** | `R1`〜`R9` | `rR1`〜`rR9` | `27`(2), `1k`(2), `5.1k`(2), `5.6k`(1), `10k`(2) | `Resistor_SMD:R_0402_1005Metric` | `B.Cu` | 9 | 9 |
| **USB-C (16ピン)** | `J1` | `rJ1` | `TYPE-C-31-M-13C` | `kbd:USB_C_Receptacle_TYPE-C-31-M-13C` | `B.Cu` | 1 | 1 |
| **TRRS ジャック** | `J2` | `rJ2` | `PJ-398A-5A` | `kbd:Jack_PJ-398A-5A_PJ-399B-6A` | `B.Cu` | 1 | 1 |
| **タクトSW** | `SMDSW1, SMDSW2` | `rSMDSW1, rSMDSW2` | `TS-1088R-02026` | `kbd:TS-1088R-02026` | `B.Cu` | 2 | 2 |
| **逆付け RGB LED** | `LED1`〜`18`, `EXLED1`〜`3` | `rLED1`〜`18`, `rEXLED2` | `YS-SK6812MINI-E` | `kbd:YS-SK6812MINI-E` | `B.Cu` | 21 | 19 |
| **Choc ソケット (1u)** | `SW1`〜`18`, `EXSW1`〜`3` | `rSW1`〜`18`, `rEXSW2` | `CPG135001S30` | `kbd:keyswitch_choc12_hotswap_1u` | `B.Cu` | 21 | 19 (右メイン) |
| **ホイールエンコーダ** | ― | `rEXSW1` (右メイン手ハンダ) | `CKW12` | `kbd:RotaryEncoder_Switch_CKW12` | `F.Cu` | 0 | 1 (右メイン) |
| **JST SH 6ピンコネクタ** | ― | `rJ3` (右メイン) / `J1` (センサー基板) | `SM06B-SRSS-TB(LF)(SN)` | `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` | `B.Cu` | 0 | 1 (右メイン) + 1 (センサー) |
| **光学センサー** | ― | `U1` (センサー基板手ハンダ) | `PMW3360DM-T2QU` | `kbd:PMW3360DM-T2QU_16Pin` | `B.Cu` | 0 | 1 (センサー) |
| **1.8V LDO** | ― | `U2` (センサー基板) | `TLV74318PDBVR` | `Package_TO_SOT_SMD:SOT-23-5` | `B.Cu` | 0 | 1 (センサー) |
| **コンデンサ (0603)** | ― | `C1`〜`C4` (`C5` は `DNP`, センサー基板) | `4.7uF`(1), `1uF`(2), `100nF`(1) | `Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder` | `B.Cu` | 0 | 4 (実装) + 1 (`DNP`) |
| **抵抗 (0603)** | ― | `R1`〜`R3` (`R4` は `DNP`, センサー基板) | `10k`(2), `39R`(1) | `Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder` | `B.Cu` | 0 | 3 (実装) + 1 (`DNP`) |
| **電圧選択ジャンパ** | ― | `JP1` (Pad 1–2 基板直結, センサー基板) | `SolderJumper_3_Bridged12` | `Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels` | `B.Cu` | 0 | 0 (銅箔パターン) |
| **SWD デバッグ端子** | `J4` (`DNP`) | `rJ4` (`DNP`) | `Conn_01x03` | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | `B.Cu` | 0 (`DNP`) | 0 (`DNP`) |

---

## 8. 品質検証基準 (DRC / ERC Verification Criteria)

回路図またはPCBを編集した際は、以下のコマンドで検証を行い、すべての基準を満たしていることを確認します。

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
```

### 8.2 合格基準（現在の達成状態）

| チェック対象 | エラー数 | 警告数 | 未配線 / 回路図不一致 | 無視設定 (Ignored Checks) | 許容される唯一の警告内容 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **左手 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **右手メイン PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **センサーサブ PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **左手 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `U1` Pin 32 (`GPIO21`) と `+3V3` の直結（左右判定ピン） |
| **右手メイン 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `rU1` Pin 32 (`GPIO21`) と `GNDR` の直結（左右判定ピン） |
| **センサーサブ 回路図 ERC** | **0 件** | **0 件** | ― | **なし (0 件)** | なし（完全ゼロ） |

* **ERC グリッド整合・ジャンクション規約**: `endpoint_off_grid` および `four_way_junction` を含む全 ERC ルールを有効化（`Ignored checks: None`）した状態で検証します。すべてのシンボルピン・ワイヤー端点は `50 mil` (`1.27 mm`) グリッド上に配置し、RGB LED マトリックスの電源・GND バス接続は偶数列を `1.27 mm` オフセット配置した3方向 T 字接続（`junction`）とすることで 4方向十字接続（`four_way_junction`）をゼロに保ちます。
* **DRC 回路図等価性（Schematic Parity）規約**: PCB 上の全フットプリントに回路図シンボルの UUID 参照（`(path "/<symbol-uuid>")`）を保持し、フットプリント名・Value・Description・属性（`DNP` / `exclude_from_bom` / `exclude_from_pos_files`）を回路図と完全一致させます。外部スクリプト等でファイルを更新した後に KiCad GUI 上で DRC/ERC を実行する場合は、メモリ上の古いキャッシュによる不一致警告（旧 `JP1` Open ジャンパや `R4`/`C5`/`R1` 属性の差分など）を防ぐため、必ず KiCad でプロジェクトを再読み込みしてから実行してください。

### 8.3 KiCad 10.0 `pcbnew` Python スクリプト操作時の注意事項
* KiCad 10.0 (Windows版) の `pcbnew` Python API では、`PCB_VIA` オブジェクトに対してレイヤー引数なしで `t.GetWidth()` を呼び出したり、`t.GetEnd()` を呼び出すと、C++ 内部アサーションダイアログ（`assert "false" failed in GetWidth(): Warning: PCB_VIA::GetWidth called without a layer argument`）が発生してプロセスが停止します。
* スクリプトで `board.GetTracks()` を走査する際は、必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を先に分岐させ、ビアの幅取得には `t.GetWidth(pcbnew.F_Cu)`、座標取得には `t.GetPosition()` を使用してください。
* また、`pcbnew.LoadBoard()` / `pcbnew.SaveBoard()` を単体で呼び出すとフットプリントの `(path "/<symbol-uuid>")` が消去される場合があるため、保存時は回路図シンボル UUID とのリンク（`(path ...)`）が維持されていることを確認してください。

---

## 9. リポジトリのフォルダ構成・生成スクリプト格納ルール (Directory & Script Rules)

リポジトリ内の一時ファイル散乱や仕様不整合を防ぐため、ディレクトリ役割と生成スクリプトの格納ルールを以下の通り定めます。

| ディレクトリ | 格納対象・役割 | 運用ルール |
| :--- | :--- | :--- |
| **[`docs/`](../docs)** | 設計仕様書（`case_spec.md`, `pcb_spec.md`）、ビルドガイド（`buildguide_jp.md`）、および図版・3Dレンダリング資産（`assets/`） | すべての仕様書・画像アセットをこの配下に一元管理する（3Dプレビューギャラリーはルート [`README.md`](../README.md) に統合） |
| **[`pcbs/`](../pcbs)** | 左右メイン基板の KiCad プロジェクト（`left/`, `right/`）および JLCPCB 発注データ（`*/jlcpcb/production_files/`） | `.rpt`, `.net`, `.bak`, `.kicad_prl` 等の一時ファイルや廃止された旧子基板ディレクトリを残さない |
| **[`plates/`](../plates)** | FR-4 トッププレート基板（`pcb/plate-top-{left,right}.kicad_pcb`）、JLCPCB Gerber（`pcb/jlcpcb/production_files/`）、レーザーカット用 SVG（`svg/`） | ボトムプレートはトレイ型ケースに統合済みのため作成・保持しない |
| **[`cases/`](../cases)** | 左右ボトムケース（`left.step/.stl`, `right.step/.stl`）、トラックボールカップ（`trackball-cup.step/.stl`）、および4種の3D検証アセンブリ STEP | すべて [`scripts/`](../scripts) 配下のジェネレータから再現可能に生成する |
| **[`scripts/`](../scripts)** | 恒久的に使用する公式生成・出力スクリプト群（下記一覧参照） | 1回限りのデバッグ用・調査用スクリプトや一時レポート（`scratch/`, `tmp/`）は作業完了後に削除し、リポジトリに残さない |

### `scripts/` 配下の公式スクリプト一覧
1. **[`scripts/generate_cases.py`](../scripts/generate_cases.py)**: 左右 3D プリントボトムケース（`left.step/.stl`, `right.step/.stl`）を生成
2. **[`scripts/generate_trackball_cup.py`](../scripts/generate_trackball_cup.py)**: トラックボールカップ（`trackball-cup.step/.stl`）および `trackball-cup-with-ball.step/.stl`（光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
3. **[`scripts/generate_sensor_assemblies.py`](../scripts/generate_sensor_assemblies.py)**: 光学センサー検証アセンブリ（`pmw3360-lens-pcb-assembly.step`, `trackball-sensor-assembly.step`、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
4. **[`scripts/generate_full_assembly.py`](../scripts/generate_full_assembly.py)**: フルアセンブリ（`assembly-full.step`、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成し、全パーツ間の干渉ゼロ（`0.00000000 mm³`）を検証
5. **[`scripts/generate_plates.py`](../scripts/generate_plates.py)**: 左右トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成・DRC検証
6. **[`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py)**: 左右メイン基板および左右トッププレートの JLCPCB 発注用データ（`GERBER-*.zip`, `BOM-*.csv`, `CPL-*.csv`）を一括出力
7. **[`scripts/generate_spec_diagrams.py`](../scripts/generate_spec_diagrams.py)**: `docs/assets/` 内の設計図解 PNG を生成
8. **[`scripts/render_previews.py`](../scripts/render_previews.py)**: `docs/assets/render_*.png` の 3D プレビュー画像を一括レンダリング

