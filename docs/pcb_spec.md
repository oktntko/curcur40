# curcur40 PCB・回路設計仕様書 (PCB & Schematic Specification)

本書は、エルゴノミクス分割キーボード **curcur40**（トラックボール・パッシブ磁気慣性ホイール一体型、Choc v2 ロープロファイル）の左右メイン基板、各種センサーサブ基板（`curcur40-pmw3360`, `curcur40-wheel-sensor`）、および単体評価基板（`curcur40-wheel-eval`）の設計基準書です。
ケース設計仕様書（[case_spec.md](./case_spec.md)）およびパッシブ磁気慣性ホイール設計仕様書（[passive_inertia_wheel_spec.md](./passive_inertia_wheel_spec.md)）と対をなし、基板構成・回路仕様・ピンアサイン・ライブラリ管理・DRC/ERC検証基準を定義します。

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

| 区分 | 左手用 (`curcur40-left`) | 右手メイン (`curcur40-right`) | トラックボールセンサー (`curcur40-pmw3360`) | ホイールセンサー (`curcur40-wheel-sensor`) | 役割 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **プロジェクト設定** | [curcur40-left.kicad_pro](../pcbs/left/curcur40-left.kicad_pro) | [curcur40-right.kicad_pro](../pcbs/right/curcur40-right.kicad_pro) | [curcur40-pmw3360.kicad_pro](../pcbs/pmw3360/curcur40-pmw3360.kicad_pro) | [curcur40-wheel-sensor.kicad_pro](../pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pro) | デザインルール・DRC/ERC設定 |
| **回路図 (Schematic)** | [curcur40-left.kicad_sch](../pcbs/left/curcur40-left.kicad_sch) | [curcur40-right.kicad_sch](../pcbs/right/curcur40-right.kicad_sch) | [curcur40-pmw3360.kicad_sch](../pcbs/pmw3360/curcur40-pmw3360.kicad_sch) | [curcur40-wheel-sensor.kicad_sch](../pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_sch) | 回路論理・シンボル定義 |
| **基板レイアウト (PCB)** | [curcur40-left.kicad_pcb](../pcbs/left/curcur40-left.kicad_pcb) | [curcur40-right.kicad_pcb](../pcbs/right/curcur40-right.kicad_pcb) | [curcur40-pmw3360.kicad_pcb](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb) | [curcur40-wheel-sensor.kicad_pcb](../pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb) | パターン配線・外形・シルク |
| **シンボルテーブル** | [left/sym-lib-table](../pcbs/left/sym-lib-table) | [right/sym-lib-table](../pcbs/right/sym-lib-table) | [pmw3360/sym-lib-table](../pcbs/pmw3360/sym-lib-table) | 標準ライブラリのみ使用 | カスタムシンボル登録 |
| **フットプリントテーブル** | [left/fp-lib-table](../pcbs/left/fp-lib-table) | [right/fp-lib-table](../pcbs/right/fp-lib-table) | [pmw3360/fp-lib-table](../pcbs/pmw3360/fp-lib-table) | 標準ライブラリのみ使用 | カスタムフットプリント登録 |

> ※上記のキーボード本体用 4 基板に加え、パッシブ磁気慣性ホイールを単体デスクトップデバイスとして評価・利用できるキャリア基板 [`pcbs/inertia-wheel-eval/curcur40-wheel-eval.{kicad_pro,kicad_sch,kicad_pcb}`](../pcbs/inertia-wheel-eval/curcur40-wheel-eval.kicad_pcb) もリポジトリに同梱しています（詳細は [passive_inertia_wheel_spec.md](./passive_inertia_wheel_spec.md) を参照）。

### 1.2 ライブラリ管理ポリシー

`sym-lib-table` および `fp-lib-table` には、以下の**プロジェクト固有カスタムライブラリのみ**を登録します。汎用部品（`AS5600-ASOT` や `SM06B-SRSS-TB` を含む）はすべて KiCad 10.0 標準ライブラリ（`${KICAD10_SYMBOL_DIR}` / `${KICAD10_FOOTPRINT_DIR}`）を直接参照します（同ディレクトリ内に存在する `corne-cherry` / `corne-chocolate` 専用のファイル群は `curcur40` では使用しません）。

| ライブラリ名 | 種別 | パス | `curcur40` で使用している固有定義 |
| :--- | :--- | :--- | :--- |
| **`kbd`** | シンボル | [pcbs/common/kbd/kicad-symbols/kbd.kicad_sym](../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | 右手用電源シンボル（`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`）、逆付けRGB LED（`YS-SK6812MINI-E`） |
| **`PMW3360_PCB`** | シンボル | [pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym](../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | 光学センサー（`PMW3360DM-T2QU`）、1.8V LDO（`TLV74318PDBVR`） |
| **`kbd`** | フットプリント | [pcbs/common/kbd/kicad-footprints/kbd.pretty](../pcbs/common/kbd/kicad-footprints/kbd.pretty) | 下記 **1.3節** の計5種類のカスタムフットプリントのみ使用 |

### 1.3 `curcur40` で使用するプロジェクト固有ライブラリデータの入手元と改変履歴

`pcbs/common/kbd/` 配下のうち、`curcur40` で実際に使用している**回路図シンボル（2ファイル）**および**フットプリント（5ファイル）**のデータ入手元（公開リポジトリ）と、KiCad 10.0 対応時のローカル調整内容は以下の通りです。

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
| **[`USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod)** | USB-C 16ピン (`TYPE-C-31-M-13C`：PC接続 `J1`/`rJ1` ＆ 左右間接続 `J2`/`rJ2`)<br>`Connector:USB_C_Receptacle_USB2.0_16P` | **foostan/kbd** の `TYPE-C-31-M-13C.kicad_mod`（＋ `TYPE-C-31-M-13C.step`, [MIT License](../pcbs/common/kbd/LICENSE)）が元データ | `2026-10-22`: 標準シンボル `USB_C_Receptacle_USB2.0_16P` のフィルタ（`USB*C*Receptacle*`）に適合するよう**ローカルでリネーム**し、シールド脚 `SH` のピン名整合・3D モデルパス修正を実施 |
| **[`PMW3360DM-T2QU_16Pin.kicad_mod`](../pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)** | 光学センサー (`PMW3360DM-T2QU`)<br>`PMW3360_PCB:PMW3360DM-T2QU` | **siderakb/pmw3360-pcb**<br>(`https://github.com/siderakb/pmw3360-pcb` の `PMW3360DM-T2QU_16Pin.kicad_mod`, [CERN-OHL-P v2](../LICENSE_CERN_OHL_P_V2)) | `2026-10-22`: 元データをベースに、KiCad 10.0 でスルーホールパッドの銅箔定義欠落エラーを防ぐため `(layers "*.Cu" "*.Mask")` をローカル補完 |

> **【補足：`SW1` / `rSW1` のソケットフットプリント統一について】**
> 派生元の Corne Chocolate では内側親指キー（`SW1` / `rSW1`）に 1.5u キーキャップ用のガイド枠を持つ `keyswitch_choc12_hotswap_1.5u` が割り当てられていましたが、物理的なホットスワップソケット部品および銅箔パッド・穴径は `1u` と完全に同一であり、かつ `curcur40` では全キーが **1u キーキャップ構成** であるため、回路図・PCBともに全キーを `kbd:keyswitch_choc12_hotswap_1u` に統一しています。

---

## 2. 基板物理仕様・デザインルール (Board Physical Specs & Design Rules)

### 2.1 基板外形・層構成

| 項目 | 左手 PCB (`curcur40-left`) | 右手メイン PCB (`curcur40-right`) | センサーサブ PCB (`curcur40-pmw3360`) | ホイールセンサー PCB (`curcur40-wheel-sensor`) | 備考 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **基材・層数** | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | 銅箔厚 1 oz (35 µm) 標準 |
| **基板板厚** | **1.60 mm** | **1.60 mm** | **1.60 mm** | **0.80 mm** | ホイールセンサーのみ `#20` カバー内格納のため **0.8 mm 指定** |
| **外形バウンディングボックス** | **124.325 × 91.8125 mm** | **124.325 × 91.8125 mm** | **29.575 × 29.200 mm** | **22.000 × 22.000 mm**<br>（折り取り後 **8.80/7.90 × 8.66 mm**） | ホイールセンサーは JLCPCB PCBA 下限（$20\times 20\text{ mm}$）を満たすブレークアウェイ外枠付き |
| **PCB座標範囲 ($X$)** | $-119.0625 \sim +5.2625 \, \text{mm}$ | $-5.2625 \sim +119.0625 \, \text{mm}$ | $-5.2625 \sim +24.3125 \, \text{mm}$ | $-11.0000 \sim +11.0000 \, \text{mm}$ | |
| **PCB座標範囲 ($Y$)** | $-24.3125 \sim +67.5000 \, \text{mm}$ | $-24.3125 \sim +67.5000 \, \text{mm}$ | $+38.3000 \sim +67.5000 \, \text{mm}$ | $-11.0000 \sim +11.0000 \, \text{mm}$ | |
| **内部切り欠き穴** | なし | **$18.50 \times 18.50 \, \text{mm}$ ($R=0.50$) 角穴** | **$8.70 \times 16.90 \, \text{mm}$ 角穴** | 枠内スナップスリット 2箇所 | 右メイン $(14.2875, 0.0000)$ に沈み込みホイール窓、センサーサブ中央 $(9.525, 52.3875)$ に光学角穴 |
| **総フットプリント数** | 82 点（PCBA 81 点） | 83 点（PCBA 82 点） | 13 点（PCBA 9 点） | 7 点（PCBA 3 点＋ワイヤパッド 4 点） | `DNP` 部品（左右 `J4`/`rJ4`、センサー基板 `R4`/`C5`）および `JP1` を含む |
| **総ネット数** | 88 ネット（実配線 70） | 87 ネット（実配線 74） | 18 ネット（実配線 12） | 7 ネット（実配線 5） | 未接続パッド（`NC`）ネットを含む |

### 2.2 DRC デザインルール（製造制約）

JLCPCB 等の標準 2層基板製造プロセスで追加料金なく高い歩留まりを確保できるルールを設定しています。

* **最小クリアランス**: `0.19 mm`（一部ネットクラス `0.20 mm`、0.5mmピッチ ESD保護IC `U3`/`U5`・`rU3`/`rU5` の通過部で `0.15 mm`）
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
| **PC接続 / 左右間ポート** | 北側 `J1` ＋ 内側 `J2` (`TYPE-C-31-M-13C`) | 北側 `rJ1` ＋ 内側 `rJ2` (`TYPE-C-31-M-13C`) | すべてミッドマウント USB-C 16ピン（`B.Cu`、ESD保護・誤挿し保護回路付き） |
| **キースイッチ数 (Choc)** | **21 キー**（すべて 1u） | **19 キー**（すべて 1u） | ダイレクトピン接続（マトリクスダイオード不要） |
| **RGB LED (SK6812MINI-E)** | **21 個** (`LED1`〜`18`, `EXLED1`〜`3`) | **19 個** (`rLED1`〜`18`, `rEXLED2`) | 各キースイッチ直下に配置（右親指トラックボール位置・ホイール位置はLEDなし） |
| **パッシブ磁気慣性ホイール** | なし（通常キースイッチ `EXSW1`） | **JST SH 6ピンコネクタ (`rJ5`)** 経由で [`curcur40-wheel-sensor`](../pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb)（`AS5600` 非接触12bit磁気角度センサ、`I2C0`）＋ 静音中クリックスイッチ（`Kailh Square Silent`、`/KEYEX1`）と接続 | 右手内側上部の $18.50 \times 18.50\,\text{mm}$ 角穴へ `#04B` 沈み込みフレームを落とし込み、ホイール回転中心をプレート天面（$Z = -2.00\,\text{mm}$）と一致させた低プロファイル構造 |
| **トラックボールセンサー** | なし（親指4キー構成） | **JST SH 6ピンコネクタ (`rJ3`)** 経由で独立サブ基板 [`curcur40-pmw3360`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（`U1`: `PMW3360DM-T2QU` ＋ `U2`: `1.8V LDO` ＋ `J1`）と接続 | トラックボールカップ開口面をトッププレート天面（$Z = -2.00\,\text{mm}$）とフラッシュに沈み込ませるため、センサー基板を $-11.80\,\text{mm}$ 下段（$Z = -16.00\,\text{mm}$）へ分離配置 |
| **SWD デバッグ端子** | `J4` (`1x03` 2.54mm スルーホール) | `rJ4` (`1x03` 2.54mm スルーホール) | `/SWCLK`, `GND`, `/SWD`。**未実装 (`DNP`)**・BOM/Pos/3Dモデル非表示 |
| **左右判定ピン (`GPIO21`)** | **`+3V3` (HIGH) に直結** | **`GNDR` (LOW) に直結** | QMK `split.handedness.pin = GP21` による自動左右認識 |
| **M2 スペーサー貫通穴** | **5 箇所**（外周 `L1`〜`L5`：$\varnothing 3.30\,\text{mm}$） | **右メイン外周 5 箇所**（`R1`〜`R5`：$\varnothing 3.30\,\text{mm}$）＋ **ホイール 3 箇所**（`W1`〜`W3`：$\varnothing 3.30\,\text{mm}$）＋ **センサー基板 4 箇所**（`TB1`〜`TB4`：$\varnothing 3.30\,\text{mm}$） | 全17箇所すべて非スルーホール（`Edge.Cuts` 円穴、$\varnothing 3.30\,\text{mm}$）。共通の M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\,\text{mm}$）貫通用 |

---

## 4. 回路ブロック別詳細仕様 (Detailed Circuit Specifications)

### 4.1 電源回路と左右間電源分離・左右間 USB-C 接続 (`J2` / `rJ2`)
1. **USB 5V 入力・逆流防止 (`ZD1` / `rZD1`) と RGB LED 電源電圧降下 (`D1` / `rD1`)**:
   - PC接続用 USB Type-C コネクタ（`J1` / `rJ1`）の `VBUS` ピンから逆流防止ショットキーバリアダイオード **`ZD1` / `rZD1` (`RB521S30T1G`, 定格平均順電流 $200\,\text{mA}$)** を経由して内部 5V ライン（`+5V` / `+5VR`：3.3V LDO 入力、および左右間 USB-C コネクタ `J2`/`rJ2` 経由の対向基板電源）へ供給されます。
   - さらに `+5V` / `+5VR` からスイッチングダイオード **`D1` / `rD1` (`1N4148WT`, 定格平均整流電流 $150\,\text{mA}$)** の順方向電圧降下（約 $0.7\,\text{V}$）を経由して RGB LED 電源ライン（`Net-(D1-K)` / `Net-(rD1-K)` $\approx 4.3\,\text{V}$）を生成し、`SK6812MINI-E` のロジック High 閾値（$0.7 \times V_{DD}$）を `RP2040` の $3.3\,\text{V}$ 出力信号（`GPIO10`）に対して確実に満たす設計としています（`ZD1` および `D1` の定格電流内に収めるため、ファームウェア [`keyboard.json`](../kbd_firmware/keyboards/curcur40/qmk/qmk_firmware/rev1/keyboard.json) にて `max_brightness: 50` に制限しています）。
2. **VBUS 接続検出 (`/USB_VBUS_PIN`)**:
   - PC接続側 USB `VBUS`（`ZD1`/`rZD1` の上流側）を **`R8` (`5.6kΩ`) および `R9` (`10kΩ`)**（右手は `rR8` / `rR9`）で分圧し、`RP2040` の Pin 16 (`GPIO13` / `/USB_VBUS_PIN`) に入力することで、どちらの基板の北側ポート（`J1` / `rJ1`）に PC の USB ケーブルが挿さっているか（マスター/スレーブ判定）を検出します。
3. **3.3V ロジック電源 (`+3V3` / `+3V3R`) と左右間 USB-C 接続 (`J2` / `rJ2`：リバーシブル ＆ PC誤挿し保護設計)**:
   - 左右間接続ポート `J2` / `rJ2` には、PC接続側（`J1` / `rJ1`）と完全同一のミッドマウント 16ピン USB Type-C レセプタクル **`TYPE-C-31-M-13C`（LCSC `C2848620`）** を採用し、内側親指側面（左手 `J2`: $(+4.0075, 29.5000)\,\text{mm}$, 回転 $-90^\circ$ / 右手 `rJ2`: $(-4.0075, 29.5000)\,\text{mm}$, 回転 $+90^\circ$、`Edge.Cuts` 切り欠き幅 $9.2400\,\text{mm}$・奥行き $5.8025\,\text{mm}$）の `B.Cu` 面に配置します。
   - **表裏リバーシブル結線とホットプラグ保護**:
     - **`A4, A9, B4, B9` (`VBUS`)**: 内部 `+5V`（右手は `+5VR`）に接続し、コネクタ直近にデカップリングコンデンサ **`C17` / `rC17` (`100nF`, `0402`)** を配置します。各基板上の LDO `U2` / `rU2` (`NCP1117LPST33T3G`) が `+5V` (`+5VR`) からローカル `+3V3` / `+3V3R` を生成します。
     - **`A6, B6` (`D+` 同士を基板上で直結)**: 市販のあらゆる USB 2.0 C-to-C ケーブルで表裏・左右の向きを問わず導通するシリアル通信ライン **`/SPLIT_DP`** とし、コネクタ直近で ESD 保護ダイオードアレイ **`U5` / `rU5` (`TPD4E05U06DQAR`, `USON-10`)** により静電気クランプを行ったうえで、直列ダンピング・電流制限抵抗 **`R10` / `rR10` (`27Ω`, `0402`)** を介して `RP2040` Pin 15 (`GPIO12` / `/TX`) に接続します（ファームウェアの 1線式 PIO 半二重シリアル設定と完全互換）。
     - **`A1, A12, B1, B12, SH`**: `GND`（右手は `GNDR`）に接続（USB-C の端子構造により挿抜時は必ず `GND` → `VBUS` → 信号線の順で接触し、旧 TRRS ジャックのような活線挿抜時の電源–信号間ショートが発生しません）。
   - **PC ケーブル誤挿し時のフェイルセーフ保護**:
     - **`A5` (`CC1`)・`B5` (`CC2`)・`A7/B7` (`D-`)・`A8/B8` (`SBU1/2`) はすべて意図的に未接続 (`NC`)** とします（`5.1kΩ` プルダウン抵抗を実装しない）。これにより、万が一 PC や USB PD 充電器の Type-C ケーブルを誤って左右間ポート（`J2` / `rJ2`）に挿しても、ホスト側がデバイス接続を認識せず **`VBUS` が出力されないコールドソケット状態（0V）** に保たれます。
     - さらに、レガシーな USB-A to C ケーブルを誤挿しして常時 $5\,\text{V}$ が印加された場合でも、逆流防止ダイオード `ZD1`/`rZD1` により `/USB_VBUS_PIN`（`GPIO13`）は LOW のまま維持されるため `RP2040` はスレーブ（`GPIO12` 入力待機状態）に留まり、`27Ω` 直列抵抗 `R10`/`rR10` と ESD 保護 `U5`/`rU5` によってバス衝突や素子破損を防止します（※左右間ケーブルには E-Marker 非搭載の一般的な USB 2.0 C-to-C ケーブルを使用します）。

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

トラックボールカップの円形リム天面をトッププレート表面（$Z = -2.00\,\text{mm}$）と同じ高さまで $-11.80\,\text{mm}$ 沈み込ませる低プロファイル設計に伴い、光学センサー `U1` (`PMW3360DM-T2QU`) とその周辺回路は独立したセンサーサブ基板 **[`pcbs/pmw3360/curcur40-pmw3360.kicad_pcb`](../pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)**（配置高さ $Z = -17.60 \sim -16.00\,\text{mm}$）に分離し、右手メイン基板（$Z = -5.80 \sim -4.20\,\text{mm}$）と **JST SH 1.0mm ピッチ 6ピン横向き SMD コネクタ（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160405`）および 6ピン両端ハーネス** で接続します。

#### ⓪ 基板間コネクタ `rJ3`（右メイン基板）↔ `J1`（センサーサブ基板）のピンアサイン
* **回路図シンボル**: `Connector_Generic_MountingPin:Conn_01x06_MountingPin`
* **フットプリント**: `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal`
* **配置座標**:
  * 右メイン基板 `rJ3`: `B.Cu` $(46.5000, 63.0000)\,\text{mm}$, 回転 $+90^\circ$（ケーブル挿入口は西向き $-X$、`rSW1` ソケット東端との間に $6.34\,\text{mm}$ の挿抜クリアランスを確保してセンサー基板 `J1` と正対）
  * センサーサブ基板 `J1`: `B.Cu` $(19.2000, 52.3875)\,\text{mm}$, 回転 $-90^\circ$（ケーブル挿入口は東向き $+X$、メイン基板 `rJ3` と正対）
* **ピン割り当て（北側 $-Y$ から南側 $+Y$ への物理並び順を両基板で完全一致させ、市販の両端同方向フラットケーブル［平置き時に両端コネクタが同じ向きになり一方の Pin 1 が他方の Pin 6 に繋がる `1-6, 2-5, 3-4, 4-3, 5-2, 6-1` 結線］をひねらず真っ直ぐ接続可能）**:
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
  * 基板裏面（`B.Cu`）の西側 `(0.5000, 51.4355)` に配置されています：
    * **Pad 1**: `+3V3R`
    * **Pad 2**: `/V_{IO}` (`U1` Pin 5 `VDDIO`)
    * **Pad 3**: `/+1V8_PMW`
  * はんだブリッジ忘れや逆ブリッジ（Pad 2–3 短絡）による動作不良を防ぐため、KiCad 10.0 標準のブリッジ済みフットプリント（`(net_tie_pad_groups "1, 2")` により **Pad 1–2 間が `B.Cu` 銅箔ポリゴンで最初から直結**、Pad 3 は開放）を採用しています。組み立て時の手作業によるジャンパはんだ付けは不要です。
* **`R4` (`28kΩ`) および `C5` (`22nF`) の DNP（未実装）化**:
  * 派生元回路（可変出力または別型番 LDO 使用時）の名残であり、現在の固定 1.8V LDO `U2` (`TLV74318PDBVR`) では Pin 4 が `NC`（未接続）であるため機能しません。
  * パターン・フットプリントは基板上に残しつつ、回路図および PCB の双方で **未実装（`DNP`）・部品表（BOM）除外・実装座標（CPL/Pos）除外・3Dモデル非表示** に設定しています。

### 4.4 右手専用：沈み込みパッシブ磁気慣性ホイール基板 (`curcur40-wheel-sensor`) と JST SH 6ピン接続 (`rJ5`)
* 右手内側上部 $(14.2875, 0.0000)\,\text{mm}$ を中心に、**$18.50 \times 18.50\,\text{mm}$（四隅 $R = 0.50\,\text{mm}$）の内部 `Edge.Cuts` 切り欠き窓** と **3箇所の M2 5.50mm スペーサー貫通穴 `W1`〜`W3`（$\varnothing 3.30\,\text{mm}$）** を設け、パッシブ磁気慣性ホイール（`#01` `SUS304` カップ型フライホイール ＋ `#04B` 沈み込みベースフレーム ＋ `#20` ツインスナップカバー）を回転軸中心がトッププレート天面（$Z = -2.00\,\text{mm}$）に一致する高さまで沈み込ませて搭載します（機構詳細は [passive_inertia_wheel_spec.md](./passive_inertia_wheel_spec.md) を参照）。
* **右メイン基板側インターフェース（`rJ5` ＋ `I2C0` プルアップ抵抗 `rR11`/`rR12` ＋ パスコン `rC18`）**:
  * **コネクタ `rJ5`**: `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal`（`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160405`、トラックボール用 `rJ3` と完全同一型番）を裏面 `B.Cu` の $(15.8000, 32.0000)\,\text{mm}$、回転 $+90^\circ$（ケーブル挿入口は西向き $-X$、直下のケース傾斜内底面とのクリアランス **$9.13\,\text{mm}$**）に配置します。
  * **ピン接続（単体評価基板 `curcur40-wheel-eval` の `J1` と 1〜6番ピン完全互換）**:
    * **Pin 1**: `+3V3R`（近傍 $(20.1000, 34.0000)$ にデカップリングコンデンサ `rC18` `100nF` を配置）
    * **Pin 2**: `GNDR`（センサー GND）
    * **Pin 3**: `/WHEEL_SDA` → `rU1` Pin 36 (`GPIO24` / ハードウェア `I2C0 SDA`、`rR11` `4.7kΩ` で `+3V3R` へプルアップ)
    * **Pin 4**: `/WHEEL_SCL` → `rU1` Pin 37 (`GPIO25` / ハードウェア `I2C0 SCL`、`rR12` `4.7kΩ` で `+3V3R` へプルアップ)
    * **Pin 5**: `/KEYEX1` → `rU1` Pin 9 (`GPIO7`、静音中クリックスイッチ `#10` `Kailh Square Silent` 入力、マトリクス座標 `[4, 6]`)
    * **Pin 6**: `GNDR`（静音中クリックスイッチ GND リターン）
    * **Pin MP (補強タブ)**: `GNDR`
* **ホイールセンサー極小サブ基板 [`curcur40-wheel-sensor`](../pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb)（`#07`、板厚 $0.80\,\text{mm}$ Top PCBA）**:
  * JLCPCB Economic PCBA の最小基板寸法（$20 \times 20\,\text{mm}$）を満たすため **$22.0 \times 22.0\,\text{mm}$ のブレークアウェイ（捨て基板）外枠** 付きで製造し、組み立て時に上下のスナップタブを手で折り取ることで **段付き $8.80/7.90 \times 8.66 \times 0.80\,\text{mm}$** の極小基板となって西側 `#20` カバー（`wheel-cover.step`）内部へ垂直格納されます。
  * 表面（`F.Cu`）に非接触 12bit 磁気角度センサ **`U1` (`AS5600-ASOT`, SOIC-8, LCSC `C499458`)** およびパスコン **`C1` (`100nF`, `0402`)・`C2` (`1uF`, `0402`)** を PCBA 自動実装済みとし、データシートの **3.3V 単一電源動作仕様** に従い `VDD5V` (Pin 1) と `VDD3V3` (Pin 2) を基板上で `+3V3` に共通接続、`DIR` (Pin 8) を `GND` 直結、`PGO` (Pin 5) を未接続（`NC`）としています。下部4箇所のワイヤパッド（`1:+3V3`, `2:GND`, `3:SDA`, `4:SCL`, ドリル径 $\varnothing 0.65\,\text{mm}$）から極細線を引き出し、静音スイッチ `#10` の2線と合わせて 6ピン JST SH ハーネスで `rJ5` に接続します。

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
| **8** | `GPIO6` | 未接続 (`NC`) | （予備） | **`/NCS`** | **PMW3360 SPI CS** |
| **9** | `GPIO7` | 未接続 (`NC`) | （予備） | **`/KEYEX1`** | **慣性ホイール 静音中クリックSW `[4, 6]` (`rJ5` Pin 5)** |
| **11** | `GPIO8` | `/KEYEX2` | キー `[1, 6]` | **`/MISO`** | **PMW3360 SPI MISO** |
| **12** | `GPIO9` | `/KEY2` | キー `[2, 5]` | `/KEY18` | キー `[4, 1]` |
| **13** | `GPIO10` | `/LED` | RGB LED `DIN` (`GP10`) | `/LED` | RGB LED `DIN` (`GP10`) |
| **14** | `GPIO11` | `/KEY1` | キー `[3, 5]` | **`/MOSI`** | **PMW3360 SPI MOSI** |
| **15** | `GPIO12` | `/TX` | 左右間 USB-C シリアル通信 (`R10` 経由 `J2` `D+`) | `/TX` | 左右間 USB-C シリアル通信 (`rR10` 経由 `rJ2` `D+`) |
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
| **36** | `GPIO24` | `/KEY14` | キー `[1, 2]` | **`/WHEEL_SDA`** | **AS5600 `I2C0 SDA` (`rJ5` Pin 3, `rR11` 4.7kΩ プルアップ)** |
| **37** | `GPIO25` | `/KEY15` | キー `[2, 2]` | **`/WHEEL_SCL`** | **AS5600 `I2C0 SCL` (`rJ5` Pin 4, `rR12` 4.7kΩ プルアップ)** |
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
| **L1** | 内側上（PC側 USB-C 横） | $(0.0000, -15.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **L2** | 内側下（左右間 USB-C 上） | $(0.0000, 20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **L3** | 小指側上 | $(-101.0000, -20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **L4** | 小指側下 | $(-98.0000, 38.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **L5** | 親指側下（`SW8`–`SW9` 南側） | $(-62.0000, 64.6000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴（右手 `R5` と完全左右対称） |

### 6.2 右手メイン PCB (`curcur40-right.kicad_pcb`) — 外周5箇所＋ホイール3箇所 および センサーサブ PCB (`curcur40-pmw3360.kicad_pcb`) — 計4箇所

右手メイン基板は親指トラックボール領域が分離されているため、`rSW8`–`rSW9` 南側の $(62.0000, 64.6000)$ に親指外周穴 **`R5`**（左手 `L5` と完全対称）を配置して親指キー領域のたわみを防止します。また、内側上部の $18.50 \times 18.50\,\text{mm}$ ホイール切り欠き周囲には、沈み込みベース枠 `#04B`（`wheel-base-frame-sunk.step`、フランジ天面 $Z = -9.10\,\text{mm}$）とトッププレート裏面（$Z = -3.60\,\text{mm}$）を繋ぐ共通の M2 5.50mm メス-メス スペーサー 3個を貫通させる **`W1`〜`W3`（$\varnothing 3.30\,\text{mm}$）** を配置しています。分離されたセンサーサブ基板（`curcur40-pmw3360`）は `TB1`〜`TB4` の4箇所でケース下段ボス天面（$Z = -17.60\,\text{mm}$）とトラックボールカップ底面（$Z = -16.00\,\text{mm}$）にサンドイッチ固定されます（スペーサーがセンサー基板の $\varnothing 3.30\,\text{mm}$ 穴を貫通してカップ耳下段の深さ $3.90\,\text{mm}$・穴径 $\varnothing 3.30\,\text{mm}$ 受け穴に進入）。

| 基板 | 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 穴径 (`Edge.Cuts`) | 備考 |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **右メイン (`curcur40-right`)** | **R1** | 外周・内側上（PC側 USB-C 横） | $(0.0000, -15.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R2** | 外周・内側下（左右間 USB-C 上） | $(0.0000, 20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R3** | 外周・小指側上 | $(101.0000, -20.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R4** | 外周・小指側下 | $(98.0000, 38.0000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴 |
| **右メイン (`curcur40-right`)** | **R5** | 外周・親指側下（`rSW8`–`rSW9` 南側） | $(62.0000, 64.6000)$ | $\varnothing 3.30 \, \text{mm}$ | 外周 5.50mm スペーサー貫通穴（左手 `L5` と左右対称） |
| **右メイン (`curcur40-right`)** | **W1** | ホイール西上スペーサー（`#04B` 固定） | $(2.0875, -1.9000)$ | $\varnothing 3.30 \, \text{mm}$ | 5.50mm スペーサー貫通穴（上下 M2×4mm ネジ締結） |
| **右メイン (`curcur40-right`)** | **W2** | ホイール西下スペーサー（`#04B` 固定） | $(2.0875, 5.8000)$ | $\varnothing 3.30 \, \text{mm}$ | 5.50mm スペーサー貫通穴（上下 M2×4mm ネジ締結） |
| **右メイン (`curcur40-right`)** | **W3** | ホイール北側スペーサー（`#04B` 固定） | $(16.2875, -12.2000)$ | $\varnothing 3.30 \, \text{mm}$ | 5.50mm スペーサー貫通穴（上下 M2×4mm ネジ締結） |
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
| **ESD 保護 IC** | `U3, U5` | `rU3, rU5` | `TPD4E05U06DQAR` | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | `B.Cu` | 2 | 2 |
| **水晶振動子** | `Y1` | `rY1` | `12MHz 18pF` | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` | `B.Cu` | 1 | 1 |
| **ショットキーD** | `ZD1` | `rZD1` | `RB521S30T1G` | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **スイッチングD** | `D1` | `rD1` | `1N4148WT` | `Diode_SMD:D_SOD-523` | `B.Cu` | 1 | 1 |
| **コンデンサ (0402)** | `C1`〜`C17` | `rC1`〜`rC18` (右メイン) / `C1, C2` (ホイールセンサー) | 左: `100n`(10), `1u`(3), `10u`(2), `27p`(2)<br>右メイン: `100n`(11), `1u`(3), `10u`(2), `27p`(2)<br>ホイール: `100n`(1), `1u`(1) | `Capacitor_SMD:C_0402_1005Metric` | `B.Cu` (ホイールのみ `F.Cu`) | 17 | 18 (右メイン) + 2 (ホイール) |
| **抵抗 (0402)** | `R1`〜`R10` | `rR1`〜`rR12` | 左: `27`(3), `1k`(2), `5.1k`(2), `5.6k`(1), `10k`(2)<br>右: 上記 ＋ `4.7k`(2: `rR11, rR12`) | `Resistor_SMD:R_0402_1005Metric` | `B.Cu` | 10 | 12 |
| **USB-C (16ピン)** | `J1, J2` | `rJ1, rJ2` | `TYPE-C-31-M-13C` | `kbd:USB_C_Receptacle_TYPE-C-31-M-13C` | `B.Cu` | 2 | 2 |
| **タクトSW** | `SMDSW1, SMDSW2` | `rSMDSW1, rSMDSW2` | `TS-1088R-02026` | `kbd:TS-1088R-02026` | `B.Cu` | 2 | 2 |
| **逆付け RGB LED** | `LED1`〜`18`, `EXLED1`〜`3` | `rLED1`〜`18`, `rEXLED2` | `YS-SK6812MINI-E` | `kbd:YS-SK6812MINI-E` | `B.Cu` | 21 | 19 |
| **Choc ソケット (1u)** | `SW1`〜`18`, `EXSW1`〜`3` | `rSW1`〜`18`, `rEXSW2` | `CPG135001S30` | `kbd:keyswitch_choc12_hotswap_1u` | `B.Cu` | 21 | 19 (右メイン) |
| **磁気角度センサ IC** | ― | `U1` (ホイールセンサー基板 PCBA実装) | `AS5600-ASOT` (LCSC `C499458`) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | `F.Cu` | 0 | 1 (ホイールセンサー) |
| **JST SH 6ピンコネクタ** | ― | `rJ3, rJ5` (右メイン) / `J1` (トラックボールセンサー) | `SM06B-SRSS-TB(LF)(SN)` | `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` | `B.Cu` | 0 | 2 (右メイン) + 1 (TBセンサー) |
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

# パッシブ慣性ホイールセンサーサブ基板 & 単体評価キャリア基板 ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/inertia-wheel-sensor/curcur40-wheel-sensor.kicad_pcb
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/inertia-wheel-eval/curcur40-wheel-eval.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/inertia-wheel-eval/curcur40-wheel-eval.kicad_pcb
```

### 8.2 合格基準（現在の達成状態）

| チェック対象 | エラー数 | 警告数 | 未配線 / 回路図不一致 | 無視設定 (Ignored Checks) | 許容される唯一の警告内容 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **左手 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **右手メイン PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **トラックボールセンサー PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **ホイールセンサー PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **ホイール単体評価 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **左手 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `U1` Pin 32 (`GPIO21`) と `+3V3` の直結（左右判定ピン） |
| **右手メイン 回路図 ERC** | **0 件** | **1 件** | ― | **なし (0 件)** | `[pin_to_pin]` `rU1` Pin 32 (`GPIO21`) と `GNDR` の直結（左右判定ピン） |
| **トラックボールセンサー 回路図 ERC** | **0 件** | **0 件** | ― | **なし (0 件)** | なし（完全ゼロ） |
| **ホイールセンサー 回路図 ERC** | **0 件** | **0 件** | ― | **なし (0 件)** | なし（完全ゼロ） |
| **ホイール単体評価 回路図 ERC** | **0 件** | **0 件** | ― | **なし (0 件)** | なし（完全ゼロ） |

* **ERC グリッド整合・ジャンクション規約**: `endpoint_off_grid` および `four_way_junction` を含む全 ERC ルールを有効化（`Ignored checks: None`）した状態で検証します。すべてのシンボルピン・ワイヤー端点は `50 mil` (`1.27 mm`) グリッド上に配置し、RGB LED マトリックスの電源・GND バス接続は偶数列を `1.27 mm` オフセット配置した3方向 T 字接続（`junction`）とすることで 4方向十字接続（`four_way_junction`）をゼロに保ちます。
* **DRC 回路図等価性（Schematic Parity）規約**: PCB 上の全フットプリントに回路図シンボルの UUID 参照（`(path "/<symbol-uuid>")`）を保持し、フットプリント名・Value・Description・属性（`DNP` / `exclude_from_bom` / `exclude_from_pos_files`）を回路図と完全一致させます。外部スクリプト等でファイルを更新した後に KiCad GUI 上で DRC/ERC を実行する場合は、メモリ上の古いキャッシュによる不一致警告（旧 `JP1` Open ジャンパや `R4`/`C5`/`R1` 属性の差分など）を防ぐため、必ず KiCad でプロジェクトを再読み込みしてから実行してください。
* **JLCPCB 2層 FR-4 PCB / PCBA 公式製造ルール自動チェック（[`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py) の `verify_jlcpcb_preflight`）**:
  発注データ出力時に、上記の DRC / ERC チェックに加えて以下の JLCPCB 公式製造基準（追加料金なしの標準2層1oz仕様）を自動検証・アサートします：
  1. **基板外形サイズ（`Edge.Cuts`）**: PCBA 対象基板は単体実装最小サイズ $20.0 \times 20.0\text{ mm}$ 以上、最大 $400 \times 500\text{ mm}$ 以内であること（実測：左 $124.45 \times 91.91\text{ mm}$、右 $124.45 \times 91.94\text{ mm}$、トラックボールセンサーサブ基板 $29.73 \times 29.35\text{ mm}$、ホイールセンサーサブ基板 $22.10 \times 22.10\text{ mm}$、ホイール単体評価基板 $48.10 \times 32.10\text{ mm}$、トッププレート $124.88 \times 92.36\text{ mm}$）。
  2. **最小配線幅**: $\ge 0.127\text{ mm}$（$5\text{ mil}$、1oz 銅箔標準。実測最小：$0.200\text{ mm}$）。
  3. **最小ビア外径・ドリル径・アニュラリング**: ビア外径 $\ge 0.450\text{ mm}$、ビアドリル径 $\ge 0.300\text{ mm}$（2層標準追加料金なし下限。実測：$0.50/0.30\text{ mm}$ または $0.60/0.30\text{ mm}$）、ビアアニュラリング $\ge 0.075\text{ mm}$（実測 $\ge 0.100\text{ mm}$）。
  4. **PTH / NPTH ドリル径**: PTH ドリル径 $0.20 \sim 6.30\text{ mm}$（実測最小：$0.60\text{ mm}$）、NPTH ドリル径 $\ge 0.50\text{ mm}$（実測最小：$1.90\text{ mm}$）。
  5. **Gerber ZIP 構成 & BOM / CPL 完全性**: 全9レイヤーの Gerber ファイル＋PTH/NPTH ドリルファイルの存在確認、BOM と CPL の Designator 集合 100% 一致、全実装部品の有効な LCSC 部品番号（`Cxxxxxx`）付与、および `DNP` / 手ハンダ部品（`R4`, `C5`, `J4`, `rJ4`, `U1(PMW3360)`, `JP1`, ワイヤパッド等）の BOM/CPL 除外を自動検証します。

### 8.3 KiCad 10.0 `pcbnew` Python スクリプト操作時の注意事項
* KiCad 10.0 (Windows版) の `pcbnew` Python API では、`PCB_VIA` オブジェクトに対してレイヤー引数なしで `t.GetWidth()` を呼び出したり、`t.GetEnd()` を呼び出すと、C++ 内部アサーションダイアログ（`assert "false" failed in GetWidth(): Warning: PCB_VIA::GetWidth called without a layer argument`）が発生してプロセスが停止します。
* スクリプトで `board.GetTracks()` を走査する際は、必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を先に分岐させ、ビアの幅取得には `t.GetWidth(pcbnew.F_Cu)`、座標取得には `t.GetPosition()` を使用してください。
* また、`pcbnew.LoadBoard()` / `pcbnew.SaveBoard()` を単体で呼び出すとフットプリントの `(path "/<symbol-uuid>")` が消去される場合があるため、保存時は回路図シンボル UUID とのリンク（`(path ...)`）が維持されていることを確認してください。

---

## 9. リポジトリのフォルダ構成・生成スクリプト格納ルール (Directory & Script Rules)

リポジトリ内の一時ファイル散乱や仕様不整合を防ぐため、ディレクトリ役割と生成スクリプトの格納ルールを以下の通り定めます。

| ディレクトリ | 格納対象・役割 | 運用ルール |
| :--- | :--- | :--- |
| **[`docs/`](../docs)** | 設計仕様書（`case_spec.md`, `pcb_spec.md`, `passive_inertia_wheel_spec.md`）、ビルドガイド（`buildguide_jp.md`, `inertia_wheel_eval_buildguide_jp.md`）、および図版・3Dレンダリング資産（`assets/`） | すべての仕様書・画像アセットをこの配下に一元管理する（3Dプレビューギャラリーはルート [`README.md`](../README.md) に統合） |
| **[`pcbs/`](../pcbs)** | 左右メイン基板・センサーサブ基板・ホイール評価基板の KiCad プロジェクト（`left/`, `right/`, `pmw3360/`, `inertia-wheel-sensor/`, `inertia-wheel-eval/`）および JLCPCB 発注データ（`*/jlcpcb/production_files/`） | `.rpt`, `.net`, `.bak`, `.kicad_prl` 等の一時ファイルを残さない |
| **[`plates/`](../plates)** | FR-4 トッププレート基板（`pcb/plate-top-{left,right}.kicad_pcb`）、JLCPCB Gerber（`pcb/jlcpcb/production_files/`）、レーザーカット用 SVG（`svg/`） | ボトムプレートはトレイ型ケースに統合済みのため作成・保持しない |
| **[`cases/`](../cases)** | 直下にケース・カップ実部品（`left.step/.stl`, `left-desk.step/.stl`, `right.step/.stl`, `right-desk.step/.stl`, `trackball-cup.step/.stl`）、[`cases/inertia_wheel/`](../cases/inertia_wheel) にパッシブ磁気慣性ホイール実部品（7種）、[`cases/assemblies/`](../cases/assemblies) に9種の3D検証アセンブリモデル | すべて [`scripts/`](../scripts) 配下のジェネレータから再現可能に生成する |
| **[`scripts/`](../scripts)** | 恒久的に使用する公式生成・出力スクリプト群（計10本、下記一覧参照） | 1回限りのデバッグ用・調査用スクリプトや一時レポート（`scratch/`, `tmp/`）は作業完了後に削除し、リポジトリに残さない |

### `scripts/` 配下の公式スクリプト一覧（計10本）
1. **[`scripts/generate_cases.py`](../scripts/generate_cases.py)**: 左右 3D プリントボトムケース（トッププレート水平基準 `left.step/.stl`, `right.step/.stl` およびデスク水平基準 `left-desk.step/.stl`, `right-desk.step/.stl`）を生成
2. **[`scripts/generate_trackball_cup.py`](../scripts/generate_trackball_cup.py)**: トラックボールカップ（`trackball-cup.step/.stl`）および `trackball-cup-with-ball.step/.stl`（光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
3. **[`scripts/generate_sensor_assemblies.py`](../scripts/generate_sensor_assemblies.py)**: 光学センサー検証アセンブリ（`pmw3360-lens-pcb-assembly.step`, `trackball-sensor-assembly.step`、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
4. **[`scripts/generate_inertia_wheel.py`](../scripts/generate_inertia_wheel.py)**: パッシブ磁気慣性ホイールの全製造パーツ（[`cases/inertia_wheel/`](../cases/inertia_wheel) 配下 7種）およびホイール検証アセンブリ 4種を生成・DfAM検証
5. **[`scripts/generate_full_assembly.py`](../scripts/generate_full_assembly.py)**: フルアセンブリ（`assembly-full.step`, `assembly-full-desk.step`、全140パーツ、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成し、全パーツ間の干渉ゼロ（`0.00000000 mm³`）を検証
6. **[`scripts/generate_plates.py`](../scripts/generate_plates.py)**: 左右トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成・DRC検証
7. **[`scripts/export_jlcpcb.py`](../scripts/export_jlcpcb.py)**: 全5基板（`left`, `right`, `pmw3360`, `inertia-wheel-sensor`, `inertia-wheel-eval`）および左右トッププレートの JLCPCB 発注用データ（`GERBER-*.zip`, `BOM-*.csv`, `CPL-*.csv`）を一括出力・プリフライト検証
8. **[`scripts/generate_spec_diagrams.py`](../scripts/generate_spec_diagrams.py)**: `docs/assets/` 内のケース・光学設計図解 PNG を生成
9. **[`scripts/generate_inertia_wheel_diagram.py`](../scripts/generate_inertia_wheel_diagram.py)**: パッシブ磁気慣性ホイールの断面設計図・部品呼称マップ・レンダリング PNG を生成
10. **[`scripts/render_previews.py`](../scripts/render_previews.py)**: `docs/assets/render_*.png` の 3D プレビュー画像を一括レンダリング

