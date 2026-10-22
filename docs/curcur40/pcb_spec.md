# curcur40 PCB・回路設計仕様書 (PCB & Schematic Specification)

本書は、エルゴノミクス分割キーボード **curcur40**（トラックボール・CKW12ホイール一体型、Choc v2 ロープロファイル）の左右メイン基板（PCB）および回路図の設計基準書です。
ケース設計仕様書（[case_spec.md](../../docs/curcur40/case_spec.md)）と対をなし、基板構成・回路仕様・ピンアサイン・ライブラリ管理・DRC/ERC検証基準を定義します。

> **【運用ルール】**
> 1. **対象バージョン**: KiCad **10.0**（10.0.7以降）を基準環境とします。
> 2. **標準ライブラリ準拠（シャドウ定義の禁止）**:
>    - KiCad公式標準ライブラリ（`MCU_RaspberryPi`, `Device`, `Diode`, `Connector`, `Capacitor_SMD`, `Resistor_SMD`, `Package_DFN_QFN`, `Package_SO` 等）をプロジェクトローカルのテーブルで上書き（シャドウイング）してはなりません。
>    - プロジェクト固有ライブラリは [pcbs/common/kbd/](../../pcbs/common/kbd) 配下の `kbd` および `PMW3360_PCB` のみとします。
> 3. **設計変更の手順**:
>    - 回路・ピン配置・基板寸法を変更する場合、まず本書（[docs/curcur40/pcb_spec.md](../../docs/curcur40/pcb_spec.md)）の該当箇所を更新し、レビュー合意後に回路図（`.kicad_sch`）および基板（`.kicad_pcb`）へ反映します。
>    - 変更後は必ず `kicad-cli` による ERC および DRC（`--schematic-parity` 含む）を実行し、本書の第6節に定める品質基準を満たすことを検証します。

---

## 1. ファイル・ライブラリ構成 (Project & Library Structure)

### 1.1 プロジェクトファイル一覧

| 区分 | 左手用 (Left) | 右手用 (Right) | 役割 |
| :--- | :--- | :--- | :--- |
| **プロジェクト設定** | [curcur40-left.kicad_pro](../../pcbs/curcur40/left/curcur40-left.kicad_pro) | [curcur40-right.kicad_pro](../../pcbs/curcur40/right/curcur40-right.kicad_pro) | デザインルール・DRC/ERC設定 |
| **回路図 (Schematic)** | [curcur40-left.kicad_sch](../../pcbs/curcur40/left/curcur40-left.kicad_sch) | [curcur40-right.kicad_sch](../../pcbs/curcur40/right/curcur40-right.kicad_sch) | 回路論理・シンボル定義 |
| **基板レイアウト (PCB)** | [curcur40-left.kicad_pcb](../../pcbs/curcur40/left/curcur40-left.kicad_pcb) | [curcur40-right.kicad_pcb](../../pcbs/curcur40/right/curcur40-right.kicad_pcb) | パターン配線・外形・シルク |
| **シンボルテーブル** | [left/sym-lib-table](../../pcbs/curcur40/left/sym-lib-table) | [right/sym-lib-table](../../pcbs/curcur40/right/sym-lib-table) | カスタムシンボル登録 |
| **フットプリントテーブル** | [left/fp-lib-table](../../pcbs/curcur40/left/fp-lib-table) | [right/fp-lib-table](../../pcbs/curcur40/right/fp-lib-table) | カスタムフットプリント登録 |

### 1.2 ライブラリ管理ポリシー

`sym-lib-table` および `fp-lib-table` には、以下の**プロジェクト固有カスタムライブラリのみ**を登録します。汎用部品はすべて KiCad 10.0 標準ライブラリ（`${KICAD10_SYMBOL_DIR}` / `${KICAD10_FOOTPRINT_DIR}`）を直接参照します（同ディレクトリ内に存在する `corne-cherry` / `corne-chocolate` 専用のファイル群は `curcur40` では使用しません）。

| ライブラリ名 | 種別 | パス | `curcur40` で使用している固有定義 |
| :--- | :--- | :--- | :--- |
| **`kbd`** | シンボル | [pcbs/common/kbd/kicad-symbols/kbd.kicad_sym](../../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | 右手用電源シンボル（`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`）、逆付けRGB LED（`YS-SK6812MINI-E`） |
| **`PMW3360_PCB`** | シンボル | [pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym](../../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | 光学センサー（`PMW3360DM-T2QU`）、1.8V LDO（`TLV74318PDBVR`） |
| **`kbd`** | フットプリント | [pcbs/common/kbd/kicad-footprints/kbd.pretty](../../pcbs/common/kbd/kicad-footprints/kbd.pretty) | 下記 **1.3節** の計7種類のカスタムフットプリントのみ使用 |

### 1.3 `curcur40` で使用するプロジェクト固有ライブラリデータの入手元と改変履歴

`pcbs/common/kbd/` 配下のうち、`curcur40` で実際に使用している**回路図シンボル（2ファイル）**および**フットプリント（7ファイル）**のデータ入手元（公開リポジトリ）と、KiCad 10.0 対応時のローカル調整内容は以下の通りです。

#### ① 回路図シンボルライブラリ（`.kicad_sym`）

| ライブラリ / シンボル名 | ファイルパス | データ入手元（公開リポジトリ） | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **`kbd`**<br>(`+1V1R`, `+3V3R`, `+5VR`, `GNDR`, `VBUSR`, `YS-SK6812MINI-E`) | [kbd.kicad_sym](../../pcbs/common/kbd/kicad-symbols/kbd.kicad_sym) | **foostan/kbd**<br>(`https://github.com/foostan/kbd` — Corne v4 公式 KiCad ライブラリ、MIT License。`git subtree` で取得) | `YS-SK6812MINI-E` の Pin 3 (`DOUT`) が元データで `power_in` になっていたため、KiCad 10.0 ERC 対応としてデータシート通り `output` にローカル修正 |
| **`PMW3360_PCB`**<br>(`PMW3360DM-T2QU`, `TLV74318PDBVR`) | [pmw3360_pcb.kicad_sym](../../pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym) | **SideraKB/PMW3360_PCB**<br>(`https://github.com/SideraKB/PMW3360_PCB` — PMW3360 ブレイクアウト基板 OSS、CERN-OHL-P v2) | `PMW3360DM-T2QU` の Pin 3 (`VDDPIX`) が元データで `power_in` になっていたため、内部レギュレータ出力仕様に合わせて `power_out` にローカル修正 |

#### ② フットプリントライブラリ（`kbd.pretty/*.kicad_mod`）および 3Dモデル

| フットプリント名 (`kbd:`) | 対象部品 / 回路図シンボル | データ入手元（公開リポジトリ） | ローカルでの生成・改変内容 |
| :--- | :--- | :--- | :--- |
| **[`keyswitch_choc12_hotswap_1u.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/keyswitch_choc12_hotswap_1u.kicad_mod)** | Kailh Choc ソケット (`CPG135001S30`)<br>`Switch:SW_Push` | **foostan/kbd**<br>(`keyswitch_choc12_hotswap_1u.kicad_mod` ＋ `kailh_choc_socket.step`) | NPTH 穴の `solder_mask_margin`（`-0.2 mm`）統一、および 3D モデル参照パスを環境非依存の `${KIPRJMOD}/../../common/kbd/...` に修正 |
| **[`YS-SK6812MINI-E.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/YS-SK6812MINI-E.kicad_mod)** | 逆付け RGB LED (`YS-SK6812MINI-E`)<br>`kbd:YS-SK6812MINI-E` | **foostan/kbd**<br>(`YS-SK6812MINI-E.kicad_mod` ＋ `YS-SK6812MINI-E.step`) | パッド上のシルク重なり回避微調整、および 3D モデル参照パス（元データの `/Users/foostan/...`）を `${KIPRJMOD}/../../common/kbd/...` に修正 |
| **[`TS-1088R-02026.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/TS-1088R-02026.kicad_mod)** | SMD タクトSW (`TS-1088R-02026`)<br>`Switch:SW_Push` | **foostan/kbd**<br>(`TS-1088R-02026.kicad_mod` ＋ `TS-1088R-02026.step`) | 形状変更なし。3D モデル参照パスを環境非依存の `${KIPRJMOD}/../../common/kbd/...` に修正 |
| **[`USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/USB_C_Receptacle_TYPE-C-31-M-13C.kicad_mod)** | USB-C 16ピン (`TYPE-C-31-M-13C`)<br>`Connector:USB_C_Receptacle_USB2.0_16P` | **foostan/kbd** の [`TYPE-C-31-M-13C.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/TYPE-C-31-M-13C.kicad_mod)（＋ `TYPE-C-31-M-13C.step`）が元データ | 標準シンボル `USB_C_Receptacle_USB2.0_16P` のフィルタ（`USB*C*Receptacle*`）に適合するよう**ローカルでリネーム複製**し、シールド脚 `SH` のピン名整合・3D モデルパス修正を実施 |
| **[`Jack_PJ-398A-5A_PJ-399B-6A.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/Jack_PJ-398A-5A_PJ-399B-6A.kicad_mod)** | 3.5mm ジャック (`PJ-398A-5A`)<br>`Connector_Audio:AudioJack3` | **foostan/kbd** の [`PJ-398A-5A_PJ-399B-6A.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/PJ-398A-5A_PJ-399B-6A.kicad_mod)（＋ `PJ-398A-5A.step`）が元データ | 標準シンボル `AudioJack3` のフィルタ（`Jack*`）に適合するよう**ローカルでリネーム複製**し、パッド番号を `1/2/3` から `T/R/S` に変更・3D モデルパス修正を実施 |
| **[`RotaryEncoder_Switch_CKW12.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/RotaryEncoder_Switch_CKW12.kicad_mod)** | ホイールエンコーダ (`CKW12`)<br>`Device:RotaryEncoder_Switch` | **kumakey/roBa**<br>(`https://github.com/kumakey/roBa` の `roBa:SW_MX_EC12` フットプリントとして [`CKW12.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/CKW12.kicad_mod) に取得 ＋ `3dmodels/ckw12_*.stp`) | 標準シンボル `RotaryEncoder_Switch` のフィルタ（`RotaryEncoder*Switch*`）に適合するよう `CKW12.kicad_mod` から**ローカルでリネーム複製** |
| **[`PMW3360DM-T2QU_16Pin.kicad_mod`](../../pcbs/common/kbd/kicad-footprints/kbd.pretty/PMW3360DM-T2QU_16Pin.kicad_mod)** | 光学センサー (`PMW3360DM-T2QU`)<br>`PMW3360_PCB:PMW3360DM-T2QU` | **SideraKB/PMW3360_PCB**<br>(`https://github.com/SideraKB/PMW3360_PCB` の `PMW3360DM-T2QU_16Pin.kicad_mod`) | 元データをベースに、KiCad 10.0 でスルーホールパッドの銅箔定義欠落エラーを防ぐため `(layers "*.Cu" "*.Mask")` をローカル補完 |

> **【補足：`SW1` / `rSW1` のソケットフットプリント統一について】**
> 派生元の Corne Chocolate では内側親指キー（`SW1` / `rSW1`）に 1.5u キーキャップ用のガイド枠を持つ `keyswitch_choc12_hotswap_1.5u` が割り当てられていましたが、物理的なホットスワップソケット部品および銅箔パッド・穴径は `1u` と完全に同一であり、かつ `curcur40` では全キーが **1u キーキャップ構成** であるため、回路図・PCBともに全キーを `kbd:keyswitch_choc12_hotswap_1u` に統一しています。

---

## 2. 基板物理仕様・デザインルール (Board Physical Specs & Design Rules)

### 2.1 基板外形・層構成

| 項目 | 左手 PCB (`curcur40-left`) | 右手 PCB (`curcur40-right`) | 備考 |
| :--- | :---: | :---: | :--- |
| **基材・層数** | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | FR-4 / 両面 2層 (`F.Cu`, `B.Cu`) | 銅箔厚 1 oz (35 µm) 標準 |
| **基板板厚** | **1.60 mm** | **1.60 mm** | [case_spec.md](../../docs/curcur40/case_spec.md) 第1節と完全同期 |
| **外形バウンディングボックス** | 幅 **124.425 mm** × 高さ **91.9125 mm** | 幅 **124.425 mm** × 高さ **91.9125 mm** | 左右対称外形 |
| **PCB座標範囲 ($X$)** | $-119.1125 \sim +5.3125 \, \text{mm}$ | $-5.3125 \sim +119.1125 \, \text{mm}$ | |
| **PCB座標範囲 ($Y$)** | $-24.3625 \sim +67.5500 \, \text{mm}$ | $-24.3625 \sim +67.5500 \, \text{mm}$ | |
| **内部切り欠き穴** | なし | **$16.90 \times 8.70 \, \text{mm}$ 角穴** | 右手親指部：PMW3360/LM19 光学レンズ穴（中心 $(9.525, 52.3875)$） |
| **総フットプリント数** | 79 点 | 88 点 | |
| **総ネット数** | 78 ネット | 88 ネット | |

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
| **トラックボールセンサー** | なし（親指4キー構成） | **PMW3360DM-T2QU** (`U1`) ＋ **1.8V LDO** (`U2`) | 右手親指部に配置（SPI接続） |
| **SWD デバッグ端子** | `J4` (`1x03` 2.54mm スルーホール) | `rJ4` (`1x03` 2.54mm スルーホール) | `/SWCLK`, `GND`, `/SWD`。**未実装 (`DNP`)**・BOM/Pos/3Dモデル非表示 |
| **左右判定ピン (`GPIO21`)** | **`+3V3` (HIGH) に直結** | **`GNDR` (LOW) に直結** | QMK `split.handedness.pin = GP21` による自動左右認識 |
| **M2 スペーサー貫通穴** | **5 箇所**（外周5） | **8 箇所**（外周4 ＋ トラックボール周囲4） | すべて $\varnothing 3.60 \, \text{mm}$ 非スルーホール（NPTH相当のEdge.Cuts円穴） |

---

## 4. 回路ブロック別詳細仕様 (Detailed Circuit Specifications)

### 4.1 電源回路と左右間電源分離
1. **USB 5V 入力と逆流防止**:
   - USB Type-C コネクタ（`J1` / `rJ1`）の `VBUS` ピンからヒューズ・ショットキーバリアダイオード `D1` / `rD1` (`RB521S30T1G`) を経由して内部 5V ライン（RGB LED 電源および 3.3V LDO 入力）へ供給されます。
2. **VBUS 接続検出 (`/USB_VBUS_PIN`)**:
   - USB `VBUS` を `10kΩ` 抵抗（`R5`/`R6`、右は `rR5`/`rR6`）で分圧し、`RP2040` の Pin 16 (`GPIO13` / `/USB_VBUS_PIN`) に入力することで、どちらの基板に USB ケーブルが挿さっているか（マスター/スレーブ判定）を検出します。
3. **3.3V ロジック電源 (`+3V3` / `+3V3R`)**:
   - LDO `U2` / `rU2` (`NCP1117LPST33T3G`) により 3.3V を生成し、`RP2040` の `IOVDD` / `USB_VDD` / `ADC_AVDD`、QSPI フラッシュ、および TRRS コネクタ経由の対向基板へ供給します。

### 4.2 左右判定ピン (`RP2040` Pin 32 `GPIO21`) の設計と ERC 警告の扱い
* **設計意図**:
  * [kbd_firmware/keyboards/curcur40/qmk/qmk_firmware/rev1/keyboard.json](../../kbd_firmware/keyboards/curcur40/qmk/qmk_firmware/rev1/keyboard.json#L50-L52) において `"handedness": { "pin": "GP21" }` が設定されています。
  * 左右の基板に同一のファームウェアバイナリを書き込んでも起動時に自動で左右を判別できるよう、ハードウェア上で以下の通り固定結線しています：
    * **左手 (`U1` Pin 32 `GPIO21`)**: **`+3V3`**（HIGH）に直結
    * **右手 (`rU1` Pin 32 `GPIO21`)**: **`GNDR`**（LOW）に直結
* **KiCad ERC 警告の扱い（意図的な保持）**:
  * KiCad 10.0 純正の `MCU_RaspberryPi:RP2040` シンボルでは Pin 32 (`GPIO21`) が `Bidirectional` 属性であり、電源出力（`Power output`）である `+3V3` / `GNDR`（`PWR_FLAG` 付）と直結されるため、ERC 実行時に `[pin_to_pin]: ピンのタイプ Bidirectional と Power output が接続されています` という警告が左右それぞれ **1件のみ** 出力されます。
  * この警告を消すために標準シンボルを改変したり ERC の `pin_to_pin` チェック自体を無効化すると、他のピンでの意図しない電源ショートを見落とすリスクが生じるため、**標準シンボルを維持したままこの正当な警告 1件のみを残す** のを curcur40 の正式仕様とします。

### 4.3 右手専用：光学トラックボールセンサー回路 (`PMW3360DM-T2QU`)

右手親指部に配置される光学センサー `U1` (`PMW3360DM-T2QU`) とその周辺回路は、PixArt 社データシートのリファレンス回路に厳密に準拠しています。

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
* 遊舎工房 CKW12（薄型ホイールエンコーダ＋プッシュスイッチ）を右手内側上部 `(14.2875, 0.0)` の表面（`F.Cu`）に配置。
* **ピン接続**:
  * **Pad A**: `/RE0A` → `rU1` Pin 36 (`GPIO24`)
  * **Pad B**: `/REB` → `rU1` Pin 9 (`GPIO7`)
  * **Pad C**: `GNDR`
  * **Pad S1**: `GNDR`
  * **Pad S2**: `/KEYEX1` → `rU1` Pin 37 (`GPIO25`、マトリクス座標 `[4, 6]` のプッシュスイッチとして動作)

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

ケース設計仕様書（[case_spec.md](../../docs/curcur40/case_spec.md) 第2.3節）と完全一致する、M2 5.50mm メスメススペーサー貫通用の円穴（`Edge.Cuts` レイヤー、直径 **$\varnothing 3.60 \, \text{mm}$**）の配置定義です。

### 6.1 左手 PCB (`curcur40-left.kicad_pcb`) — 計5箇所

| 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 穴径 (`Edge.Cuts`) | 備考 |
| :---: | :--- | :---: | :---: | :--- |
| **L1** | 内側上（USB-C横） | $(0.0000, -15.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L2** | 内側下（TRRS上） | $(0.0000, 25.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L3** | 小指側上 | $(-109.5375, -20.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L4** | 小指側下 | $(-98.0000, 38.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **L5** | 親指側下 | $(-23.8125, 64.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |

### 6.2 右手 PCB (`curcur40-right.kicad_pcb`) — 計8箇所

右手親指側はトラックボールカップ周囲の4本（`TB1`〜`TB4`）で強固に締結されるため、`L5` 相当の親指外周穴は設けません。

| 穴番号 | 配置箇所 | PCB座標 $(x_{\text{pcb}}, y_{\text{pcb}})$ | 穴径 (`Edge.Cuts`) | 備考 |
| :---: | :--- | :---: | :---: | :--- |
| **R1** | 外周・内側上（USB-C横） | $(0.0000, -15.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **R2** | 外周・内側下（TRRS上） | $(0.0000, 25.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **R3** | 外周・小指側上 | $(109.5375, -20.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **R4** | 外周・小指側下 | $(98.0000, 38.0000)$ | $\varnothing 3.60 \, \text{mm}$ | 外周スペーサー貫通穴 |
| **TB1** | トラックボール北西 (NW) | $(-2.4750, 41.0875)$ | $\varnothing 3.60 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(-12.0, -11.3)$ |
| **TB2** | トラックボール北東 (NE) | $(21.5250, 41.0875)$ | $\varnothing 3.60 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(+12.0, -11.3)$ |
| **TB3** | トラックボール南西 (SW) | $(-2.4750, 63.6875)$ | $\varnothing 3.60 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(-12.0, +11.3)$ |
| **TB4** | トラックボール南東 (SE) | $(21.5250, 63.6875)$ | $\varnothing 3.60 \, \text{mm}$ | カップ中心 $(9.525, 52.3875)$ から $(+12.0, +11.3)$ |

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
| **Choc ソケット (1u)** | `SW1`〜`18`, `EXSW1`〜`3` | `rSW1`〜`18`, `rEXSW2` | `CPG135001S30` | `kbd:keyswitch_choc12_hotswap_1u` | `B.Cu` | 21 | 19 |
| **ホイールエンコーダ** | ― | `rEXSW1` (手ハンダ) | `CKW12` | `kbd:RotaryEncoder_Switch_CKW12` | `F.Cu` | 0 | 1 |
| **光学センサー** | ― | `U1` (手ハンダ) | `PMW3360DM-T2QU` | `kbd:PMW3360DM-T2QU_16Pin` | `B.Cu` | 0 | 1 |
| **1.8V LDO** | ― | `U2` | `TLV74318PDBVR` | `Package_TO_SOT_SMD:SOT-23-5` | `B.Cu` | 0 | 1 |
| **コンデンサ (0603)** | ― | `C1`〜`C4` (`C5` は `DNP`) | `4.7uF`(1), `1uF`(2), `100nF`(1) | `Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder` | `B.Cu` | 0 | 4 (実装) + 1 (`DNP`) |
| **抵抗 (0603)** | ― | `R1`〜`R3` (`R4` は `DNP`) | `10k`(2), `39R`(1) | `Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder` | `B.Cu` | 0 | 3 (実装) + 1 (`DNP`) |
| **電圧選択ジャンパ** | ― | `JP1` (Pad 1–2 基板直結) | `SolderJumper_3_Bridged12` | `Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels` | `B.Cu` | 0 | 0 (銅箔パターン) |
| **SWD デバッグ端子** | `J4` (`DNP`) | `rJ4` (`DNP`) | `Conn_01x03` | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | `B.Cu` | 0 (`DNP`) | 0 (`DNP`) |

---

## 8. 品質検証基準 (DRC / ERC Verification Criteria)

回路図またはPCBを編集した際は、以下のコマンドで検証を行い、すべての基準を満たしていることを確認します。

### 8.1 検証コマンド
```powershell
# 左手 ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/curcur40/left/curcur40-left.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/curcur40/left/curcur40-left.kicad_pcb

# 右手 ERC / DRC
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" sch erc pcbs/curcur40/right/curcur40-right.kicad_sch
& "$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe" pcb drc --schematic-parity pcbs/curcur40/right/curcur40-right.kicad_pcb
```

### 8.2 合格基準（現在の達成状態）

| チェック対象 | エラー数 | 警告数 | 未配線 / 回路図不一致 | 無視設定 (Ignored Checks) | 許容される唯一の警告内容 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **左手 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **右手 PCB DRC** | **0 件** | **0 件** | **0 件 / 0 件** | **なし (0 件)** | なし（完全ゼロ） |
| **左手 回路図 ERC** | **0 件** | **1 件** | ― | グリッド・4点接続のみ | `[pin_to_pin]` `U1` Pin 32 (`GPIO21`) と `+3V3` の直結（左右判定ピン） |
| **右手 回路図 ERC** | **0 件** | **1 件** | ― | グリッド・4点接続のみ | `[pin_to_pin]` `rU1` Pin 32 (`GPIO21`) と `GNDR` の直結（左右判定ピン） |

### 8.3 KiCad 10.0 `pcbnew` Python スクリプト操作時の注意事項
* KiCad 10.0 (Windows版) の `pcbnew` Python API では、`PCB_VIA` オブジェクトに対してレイヤー引数なしで `t.GetWidth()` を呼び出したり、`t.GetEnd()` を呼び出すと、C++ 内部アサーションダイアログ（`assert "false" failed in GetWidth(): Warning: PCB_VIA::GetWidth called without a layer argument`）が発生してプロセスが停止します。
* スクリプトで `board.GetTracks()` を走査する際は、必ず `if t.GetClass() == "PCB_TRACK":` と `elif t.GetClass() == "PCB_VIA":` を先に分岐させ、ビアの幅取得には `t.GetWidth(pcbnew.F_Cu)`、座標取得には `t.GetPosition()` を使用してください。

---

## 9. リポジトリのフォルダ構成・生成スクリプト格納ルール (Directory & Script Rules)

リポジトリ内の一時ファイル散乱や仕様不整合を防ぐため、ディレクトリ役割と生成スクリプトの格納ルールを以下の通り定めます。

| ディレクトリ | 格納対象・役割 | 運用ルール |
| :--- | :--- | :--- |
| **[`docs/curcur40/`](../../docs/curcur40)** | 設計仕様書（`case_spec.md`, `pcb_spec.md`）、ビルドガイド（`buildguide_jp.md`）、3Dプレビューギャラリー（`preview.md`）、および図版資産（`assets/`） | すべてのドキュメント・画像アセットをこの配下に一元管理する（ルート直下に `preview/` 等を作らない） |
| **[`pcbs/curcur40/`](../../pcbs/curcur40)** | 左右メイン基板の KiCad プロジェクト（`left/`, `right/`）および JLCPCB 発注データ（`*/jlcpcb/production_files/`） | `.rpt`, `.net`, `.bak`, `.kicad_prl` 等の一時ファイルや廃止された旧子基板ディレクトリを残さない |
| **[`plates/curcur40/`](../../plates/curcur40)** | FR-4 トッププレート基板（`pcb/plate-top-{left,right}.kicad_pcb`）、JLCPCB Gerber（`pcb/jlcpcb/production_files/`）、レーザーカット用 SVG（`svg/`） | ボトムプレートはトレイ型ケースに統合済みのため作成・保持しない |
| **[`cases/curcur40/`](../../cases/curcur40)** | 左右ボトムケース（`left.step/.stl`, `right.step/.stl`）、トラックボールカップ（`trackball-cup.step/.stl`）、および4種の3D検証アセンブリ STEP | すべて [`scripts/`](../../scripts) 配下のジェネレータから再現可能に生成する |
| **[`scripts/`](../../scripts)** | 恒久的に使用する公式生成・出力スクリプト群（下記一覧参照） | 1回限りのデバッグ用・調査用スクリプトや一時レポート（`scratch/`, `tmp/`）は作業完了後に削除し、リポジトリに残さない |

### `scripts/` 配下の公式スクリプト一覧
1. **[`scripts/generate_cases.py`](../../scripts/generate_cases.py)**: 左右 3D プリントボトムケース（`left.step/.stl`, `right.step/.stl`）を生成
2. **[`scripts/generate_trackball_cup.py`](../../scripts/generate_trackball_cup.py)**: トラックボールカップ（`trackball-cup.step/.stl`）および `trackball-cup-with-ball.step/.stl`（光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
3. **[`scripts/generate_sensor_assemblies.py`](../../scripts/generate_sensor_assemblies.py)**: 光学センサー検証アセンブリ（`pmw3360-lens-pcb-assembly.step`, `trackball-sensor-assembly.step`、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成
4. **[`scripts/generate_full_assembly.py`](../../scripts/generate_full_assembly.py)**: フルアセンブリ（`assembly-full.step`、光学基準点 `Lens_Optical_Ref_Point` 含む）を生成し、全パーツ間の干渉ゼロ（`0.00000000 mm³`）を検証
5. **[`scripts/generate_plates.py`](../../scripts/generate_plates.py)**: 左右トッププレート（`plate-top-left.kicad_pcb`, `plate-top-right.kicad_pcb`）およびレーザーカット用 SVG（`plate-curcur40.svg`, `foam-curcur40.svg`）を生成・DRC検証
6. **[`scripts/export_jlcpcb.py`](../../scripts/export_jlcpcb.py)**: 左右メイン基板および左右トッププレートの JLCPCB 発注用データ（`GERBER-*.zip`, `BOM-*.csv`, `CPL-*.csv`）を一括出力
7. **[`scripts/generate_spec_diagrams.py`](../../scripts/generate_spec_diagrams.py)**: `docs/curcur40/assets/` 内の設計図解 PNG を生成
8. **[`scripts/render_previews.py`](../../scripts/render_previews.py)**: `docs/curcur40/assets/render_*.png` の 3D プレビュー画像を一括レンダリング

