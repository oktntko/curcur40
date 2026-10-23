# curcur40

**curcur40** は、[Corne Keyboard (crkbd v4)](https://github.com/foostan/crkbd) をベースに、Kailh Choc V1/V2 ロープロファイルスイッチ専用の **40キー左右分割レイアウト**、右手親指内側の **$\varnothing 25\,\text{mm}$ 光学式トラックボール（PMW3360DM-T2QU 低プロファイル分離センサーサブ基板）**、および右手人差し指内側の **水平ローラーエンコーダ（CKW12）** を融合したカスタム分割エルゴノミクスキーボードです。

![Full Assembly Isometric](./docs/assets/render_full_assembly_iso.png)

---

## 主な特徴 (Key Features)

- **40キー + 25mm トラックボール + 水平ローラーエンコーダ**:
  - **左手 (21キー)**: メイン $3\times 5$ (15キー) ＋ 内側縦2キー (`EXSW1`, `EXSW2`) ＋ 親指4キー (`SW1`, `SW8`, `SW9`, `EXSW3`)
  - **右手 (19キー + 2デバイス)**: メイン $3\times 5$ (15キー) ＋ 内側下段1キー (`rEXSW2`) ＋ 親指外側3キー (`rSW1`, `rSW8`, `rSW9`) ＋ **水平ローラーエンコーダ (`CKW12`)** ＋ **$\varnothing 25\,\text{mm}$ トラックボール (`PMW3360DM-T2QU` + `LM19-LSI`)**
- **低プロファイル沈み込みトラックボール & ビルトインテンティングケース**:
  - トラックボールカップの円形リム天面（$Z_{\text{rel}} = +14.00\,\text{mm}$）をトッププレート表面（$Z = -2.00\,\text{mm}$）と同一平面に揃えて **$-11.80\,\text{mm}$ 低プロファイル化**（キーキャップ頂点 $Z = +3.60\,\text{mm}$ から 25mm ボール頂点 $Z = +14.80\,\text{mm}$ までの突出量を **$+11.20\,\text{mm}$** に短縮）。
  - PMW3360 光学センサー回路を独立サブ基板（[`curcur40-pmw3360`](./pcbs/pmw3360/curcur40-pmw3360.kicad_pcb), $Z = -16.00\,\text{mm}$）に分離し、右手メイン基板（[`curcur40-right`](./pcbs/right/curcur40-right.kicad_pcb), $Z = -4.20\,\text{mm}$）の `rJ3`（西向き）とセンサー基板の `J1`（東向き）を正対配置した **JST SH 1.0mm ピッチ 6ピンコネクタ（`SM06B-SRSS-TB`）＆ハーネス** でワンタッチ接続。
  - 左右ボトムケースは外底面と平行な**均一肉厚 $2.40\,\text{mm}$ の傾斜内底面＋円筒ネジ座面ボス（$\varnothing 6.80\,\text{mm}$）構造**を採用。小指側外端を全高 $10.00\,\text{mm}$（$Z = -10.00\,\text{mm}$、内底面 $Z = -8.00\,\text{mm}$）、親指側内端を全高 $26.90\,\text{mm}$（$Z = -26.90\,\text{mm}$、**ビルトインテンティング角 $\theta_{\text{tent}} = 7.47^\circ$**）とすることで、テーブルからキーキャップまでの高さを抑えつつ自然な手首角度とセンサー収納空間を両立。
- **全14箇所 M2 5.50mm スペーサー統一による高剛性締結アーキテクチャ**:
  - 左手外周 5箇所（`L1`〜`L5`）＋ 右手外周 5箇所（`R1`〜`R5`、`L5` と `R5` は $(\pm 62.0000, 64.6000)$ で完全左右対称）＋ トラックボールカップ固定耳 4箇所（`TB1`〜`TB4`）の **全 14箇所すべてに共通の M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\,\text{mm}$、計 14個）** を配置し、上下の **M2 × 4.0mm ネジ（計 28本）** で締結。
  - ケースの傾斜内底面から立ち上がる円筒ボス（外周10箇所は上面 $Z = -9.10\,\text{mm}$、トラックボール4箇所は上面 $Z = -17.60\,\text{mm}$）に 5.50mm スペーサーが着座し、各基板の **$\varnothing 3.30\,\text{mm}$ 貫通穴**を通って外周 10箇所ではトッププレート下面（$Z = -3.60\,\text{mm}$）を直接支持、トラックボール部 4箇所ではセンサー基板をサンドイッチしつつカップ固定耳（高さ $5.50\,\text{mm}$、下部 $3.90\,\text{mm}$ は $\varnothing 3.30\,\text{mm}$ スペーサー穴、上部 $1.60\,\text{mm}$ は $\varnothing 2.40\,\text{mm}$ ネジ穴）へ進入して締結。全 14箇所ともケース側のネジ締結肉厚 **$2.40\,\text{mm}$**・上部締結肉厚 **$1.60\,\text{mm}$**・スペーサー内ネジ間隙間 **$1.50\,\text{mm}$** に完全統一され、ケース底面外側の **$\varnothing 4.60\,\text{mm}$ ディープザグリ穴**によってネジ頭が底面から一切突出しない構造。
- **3爪スリムアーチ保持・3点セラミック球支持トラックボールカップ**:
  - $\varnothing 2.0\,\text{mm}$ G5 窒化ケイ素（$\text{Si}_3\text{N}_4$）セラミックベアリング球 3個（入口スロート径 $\varnothing 1.95\,\text{mm}$ のスナップイン球面座）で $\varnothing 25.0\,\text{mm}$ ボールを低摩擦支持し、上部のスリムアーチ3爪（スロート径 $\varnothing 24.59\,\text{mm}$、食い込み量 $0.205\,\text{mm}$）で逆さにしても落下しないスナップイン保持と全方位の指クリアランスを両立。
- **RP2040 オンボード & QMK / Vial 完全対応**:
  - 左右とも `RP2040` + `16MB` QSPI Flash (`W25Q128JVSIQ`) をオンボード実装し、ダイオードレスのダイレクトピン接続を採用。Vial GUI からキーマップ・ロータリーエンコーダ・トラックボール設定をリアルタイム変更可能。

---

## ドキュメント・設計仕様書 (Documentation)

| ドキュメント | 内容 |
| :--- | :--- |
| **[ビルドガイド (`docs/buildguide_jp.md`)](./docs/buildguide_jp.md)** | 必要パーツ一覧（BOM）、JLCPCB PCBA 発注手順、PMW3360/CKW12 の手ハンダ手順、ケース・トラックボールカップ組み立て手順、ファームウェア書き込み手順 |
| **[ケース・機構設計仕様書 (`docs/case_spec.md`)](./docs/case_spec.md)** | Z軸スタックアップ定義、14箇所 M2 5.50mm スペーサー締結仕様、外周ポート開口（USB-C / TRRS）、トラックボールカップ＆光学距離（$2.40\,\text{mm}$）仕様 |
| **[PCB・回路図設計仕様書 (`docs/pcb_spec.md`)](./docs/pcb_spec.md)** | 左右メイン基板＆センサーサブ基板の回路構成、RP2040 GPIO ピンアサイン表、PMW3360 サブ基板分離＆正対コネクタ仕様、カスタムライブラリ一覧、DRC/ERC 検証基準 |
| **[生成スクリプト一覧 (`scripts/README.md`)](./scripts/README.md)** | 3Dモデル（ケース・カップ・フルアセンブリ）、トッププレート、JLCPCB 発注データ、プレビュー画像の再現生成スクリプト（全8本）の説明 |

---

## 3D プレビュー・完成イメージギャラリー (3D Preview Gallery)

KiCad 10.0 Raytracing（`kicad-cli pcb render`）および `cadgen` 3D CAD レンダラーで出力した完成イメージ一覧です。

### 1. フルアセンブリ（3Dプリントケース + メイン基板 + トッププレート + 25mmトラックボール + CKW12エンコーダ）

#### 斜視図（アイソメトリックビュー）
![Full Assembly Isometric](./docs/assets/render_full_assembly_iso.png)

#### 上面図（トップビュー）
![Full Assembly Top](./docs/assets/render_full_assembly_top.png)

#### 底面図（ボトムビュー：14箇所 Ø4.6mm ザグリ穴、L1〜L5 ＆ R1〜R5 左右対称配置）
![Full Assembly Bottom](./docs/assets/render_full_assembly_bottom.png)

---

### 2. 左手メイン基板 (`curcur40-left`)
- **構成**: 21キー（メイン $3\times 5$ + 内側 1u×2 + 親指 1u×4）
- **制御回路**: `RP2040`（QFN-56）+ `W25Q128JVSIQ`（16MB QSPI Flash）+ USB Type-C（ESD保護 `TPD4E05U06DQAR`・VBUS逆流防止ダイオード `ZD1` 搭載）+ TRRS/TRS 3.5mmジャック
- **外周固定穴**: 5箇所（$\varnothing 3.30\,\text{mm}$ 貫通穴、M2 5.50mm スペーサー挿通用。右手外周 5箇所 `R1`〜`R5` と完全左右対称）

#### 表面（スイッチ差し込み面 / `F.Cu`）
![Left PCB Top](./docs/assets/render_left_top.png)

#### 斜視図（アイソメトリックビュー）
![Left PCB Isometric](./docs/assets/render_left_iso.png)

#### 裏面（部品実装面 / `B.Cu`）
![Left PCB Bottom](./docs/assets/render_left_bottom.png)

---

### 3. 右手メイン基板 (`curcur40-right`) ＆ トラックボールセンサーサブ基板 (`curcur40-pmw3360`)
- **構成**: 19キー（メイン $3\times 5$ + 内側下段 1u×1 + 親指外側 1u×3）+ 水平ローラーエンコーダ **CKW12**（`rEXSW1`: $(14.2875, 0.0000)\,\text{mm}$）+ **25mm トラックボール光学センサーサブ基板**（中心 $(9.5250, 52.3875)\,\text{mm}$）
- **サブ基板分離・正対コネクタ接続アーキテクチャ**:
  - トラックボールを $-11.80\,\text{mm}$ 低プロファイル化するため、`PMW3360DM-T2QU`（`U1`）および `1.8V` LDO（`U2`: `TLV74318PDBVR`）回路を独立サブ基板 [`curcur40-pmw3360`](./pcbs/pmw3360/curcur40-pmw3360.kicad_pcb)（$Z = -17.60 \sim -16.00\,\text{mm}$）に分離。
  - 右メイン基板裏面（`B.Cu`）の `rJ3`（$(46.5000, 63.0000)$, 西向き開口）とセンサーサブ基板裏面（`B.Cu`）の `J1`（$(19.2000, 52.3875)$, 東向き開口）に **JST SH 1.0mm ピッチ 6ピン SMD コネクタ（`SM06B-SRSS-TB`）** を正対配置し、北〜南の信号順（北端 `+3V3R` 〜 南端 `/NCS`）を両基板で完全一致させているため、6ピン両端同方向フラットケーブルをひねらず真っ直ぐ伸ばしてワンタッチ接続可能。
  - センサー基板裏面（`B.Cu`）の電圧選択ジャンパ `JP1` は、**Pad 1（`+3V3R`）– Pad 2（`/V_{IO}`）間が基板の銅箔パターンで最初から直結（`SolderJumper_3_Bridged12`）** されており、手作業でのブリッジは不要。
  - `R4`（28kΩ）、`C5`（22nF）、およびデバッグ端子 `J4` / `rJ4` は **DNP（未実装）** 指定。
- **固定穴・光学開口**:
  - 右メイン基板外周スペーサー貫通穴 5箇所（`R1`〜`R5`、$\varnothing 3.30\,\text{mm}$）+ センサーサブ基板スペーサー貫通穴 4箇所（`TB1`〜`TB4`、$\varnothing 3.30\,\text{mm}$：中心 $(9.5250, 52.3875)\,\text{mm}$ から $X \pm 12.00\,\text{mm}, Y \pm 11.30\,\text{mm}$）＝ 計 9箇所
  - センサーサブ基板中央に PMW3360 光学窓＆LM19-LSI レンズ脚部用の矩形開口（$8.70 \times 16.90\,\text{mm}$）

#### 表面（スイッチ搭載面 / `F.Cu`）
![Right PCB Top](./docs/assets/render_right_top.png)

#### 斜視図（アイソメトリックビュー）
![Right PCB Isometric](./docs/assets/render_right_iso.png)

#### 右メイン基板 裏面（SMD部品・JST SH コネクタ `rJ3` 実装面 / `B.Cu`）
![Right PCB Bottom](./docs/assets/render_right_bottom.png)

#### トラックボールセンサーサブ基板 (`curcur40-pmw3360`) 表裏プレビュー
| 表面（レンズ着座面 / `F.Cu`） | 裏面（PMW3360・1.8V LDO・JST SH コネクタ `J1` 実装面 / `B.Cu`） |
| :---: | :---: |
| ![PMW3360 Sub-PCB Top](./docs/assets/render_pmw3360_top.png) | ![PMW3360 Sub-PCB Bottom](./docs/assets/render_pmw3360_bottom.png) |

---

### 4. FR-4 トッププレート (`plate-top-left` / `plate-top-right`)
- **材質・板厚**: FR-4（ガラスエポキシ基板材）、板厚 $1.60\,\text{mm}$（$Z = -3.60 \sim -2.00\,\text{mm}$）
- **ネジ穴仕様**: すべて **$\varnothing 2.40\,\text{mm}$ ストレート貫通穴（ザグリなし）**（左手 5箇所 `L1`〜`L5`、右手 5箇所 `R1`〜`R5`、完全左右対称）。上から M2 × 4.0mm ネジを通してプレート下面（$Z = -3.60\,\text{mm}$）を直接支持する M2 5.50mm スペーサー上端へ締結（噛み合い深さ $2.40\,\text{mm}$）。
- **右手プレート形状**: CKW12 水平ローラーエンコーダ用の開口（$18.20 \times 18.20\,\text{mm}$）および親指内側のトラックボールカップ領域を切り欠いた L字ノッチ形状（ケース内壁クリアランス $0.30\,\text{mm}$、カップ耳クリアランス $0.3125\,\text{mm}$）。

#### 左手トッププレート (`plate-top-left`)
![Left Top Plate](./docs/assets/render_plate_left.png)

#### 右手トッププレート (`plate-top-right`)
![Right Top Plate](./docs/assets/render_plate_right.png)

---

### 5. トラックボールカップ・光学スタックアップ検証モデル
[`cases/`](./cases/) 配下の3Dプリント用モデルおよび4つの光学検証アセンブリモデルです。4つの検証アセンブリ STEP には、GUI（CAD Viewer等）の計測ツールで直接選択してボール底面（$Z_{\text{rel}} = +5.80\,\text{mm}$ / グローバル $Z = -10.2000\,\text{mm}$）との距離（設計値 **$2.40\,\text{mm}$**）を計測できるよう、レンズ側光学距離基準点（**`Lens_Optical_Ref_Point`**, $Z_{\text{rel}} = +3.40\,\text{mm}$ / グローバル $Z = -12.6000\,\text{mm}$）が独立オブジェクトとしてプロットされています。

| トラックボールカップ単体 (`trackball-cup.step`) | 25mmボール・レンズ組込 (`trackball-cup-with-ball.step`) |
| :---: | :---: |
| ![Trackball Cup](./docs/assets/trackball_cup_render.png) | ![Trackball Cup with Ball](./docs/assets/trackball_cup_with_ball_render.png) |

---

## リポジトリ構成と発注用データ (Repository Structure & Production Files)

```text
curcur40/
├── cases/                        # 3Dプリント用ケース・トラックボールカップ・検証用フルアセンブリ (STEP / STL)
│   ├── left.step / left.stl      # 左手トレイ型ボトムケース（トッププレート水平基準）
│   ├── left-desk.step / .stl     # 左手トレイ型ボトムケース（ケース外底面＝デスク水平基準）
│   ├── right.step / right.stl    # 右手トレイ型ボトムケース（トッププレート水平基準）
│   ├── right-desk.step / .stl    # 右手トレイ型ボトムケース（ケース外底面＝デスク水平基準）
│   ├── trackball-cup.step / .stl # 25mmトラックボール用スナップインカップ
│   ├── assembly-full.step        # 全105パーツ統合フルアセンブリ（トッププレート水平基準）
│   └── assembly-full-desk.step   # 全105パーツ統合フルアセンブリ（ケース底面＝デスク面 Z=0 水平基準）
├── pcbs/                         # KiCad 10.0 左右メイン基板・センサーサブ基板 & JLCPCB PCBA 発注データ
│   ├── left/                     # 左手メイン基板 (curcur40-left)
│   │   └── jlcpcb/production_files/  # GERBER-curcur40-left.zip, BOM-curcur40-left.csv, CPL-curcur40-left.csv
│   ├── right/                    # 右手メイン基板 (curcur40-right)
│   │   └── jlcpcb/production_files/  # GERBER-curcur40-right.zip, BOM-curcur40-right.csv, CPL-curcur40-right.csv
│   ├── pmw3360/                  # トラックボールセンサーサブ基板 (curcur40-pmw3360)
│   │   └── jlcpcb/production_files/  # GERBER-curcur40-pmw3360.zip, BOM-curcur40-pmw3360.csv, CPL-curcur40-pmw3360.csv
│   └── common/kbd/               # プロジェクト固有 KiCad シンボル・フットプリント・3Dモデルライブラリ
├── plates/                       # FR-4 トッププレート KiCad PCB / Gerber & レーザーカット用 SVG
│   ├── pcb/                      # plate-top-left.kicad_pcb, plate-top-right.kicad_pcb
│   │   └── jlcpcb/production_files/  # GERBER-plate-top-left.zip, GERBER-plate-top-right.zip
│   └── svg/                      # plate-curcur40.svg, foam-curcur40.svg
├── kbd_firmware/                 # QMK / Vial ファームウェアソース (keyboards/curcur40)
├── docs/                         # ビルドガイド・設計仕様書・図版アセット
│   ├── buildguide_jp.md
│   ├── case_spec.md
│   ├── pcb_spec.md
│   └── assets/
└── scripts/                      # 3Dモデル・プレート・JLCPCBデータ・プレビュー画像の自動生成スクリプト群
```

---

## ライセンス・謝辞 (License & Credits)

本プロジェクトは、以下のオープンソースハードウェア／ソフトウェアプロジェクトの成果をベースに派生・統合して作成されています。各オリジナル作者の皆様に深く感謝いたします。

| 対象領域 / ファイル | 派生元リポジトリ・原著作者 | 適用ライセンス | 改変履歴・表示事項（CC BY 4.0 Sec. 3(a) / CERN-OHL-P v2 Sec. 3.3 準拠） |
| :--- | :--- | :--- | :--- |
| **基板・プレート・ケース・ドキュメント・スクリプト**<br>(`pcbs/left/`, `pcbs/right/`, `pcbs/pmw3360/`, `plates/`, `cases/`, `docs/`, `scripts/`) | **[foostan/crkbd](https://github.com/foostan/crkbd)**<br>(Original Author: `foostan` / Kosuke Adachi) | **[MIT License](./LICENSE_MIT)** ＆<br>**[CC BY 4.0](./LICENSE_CC)** | Corne v4 (`corne-chocolate`) をベースに、40キー配列化・親指クラスタ再配置・右手 PMW3360 トラックボール（低プロファイルサブ基板分離）＆CKW12 エンコーダ統合・KiCad 10.0 対応・3Dプリントケース＆トラックボールカップ新規設計を実施（`2026-10`） |
| **プロジェクト固有 KiCad ライブラリ（Corne 由来）**<br>(`pcbs/common/kbd/kicad-symbols/kbd.kicad_sym`, `kbd.pretty/`, `kicad-packages3D/kbd.3dshapes/`) | **[foostan/kbd](https://github.com/foostan/kbd)**<br>(Original Author: `foostan`) | **[MIT License](./pcbs/common/kbd/LICENSE)** | `2026-10-22`: 未使用シンボル・フットプリント・3Dモデルを整理し、KiCad 10.0 標準シンボルとのピン名・フィルタ整合、`YS-SK6812MINI-E` Pin 2 (`DOUT`) 電気タイプ修正、`keyswitch_choc12_hotswap_1u` の旧 Corne V3 由来 $\varnothing 0.40\,\text{mm}$ NPTH 穴削除、環境非依存の3Dモデル相対パス化を実施 |
| **PMW3360 回路図シンボル・フットプリント**<br>(`pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym`, `PMW3360DM-T2QU_16Pin.kicad_mod`) | **[siderakb/pmw3360-pcb](https://github.com/siderakb/pmw3360-pcb)**<br>(Original Author: `siderakb` / `ziteh`) | **[CERN-OHL-P v2](./LICENSE_CERN_OHL_P_V2)**<br>(Permissive) | `2026-10-22`: 未使用の `TXS0108E-QPWRQ1` シンボルを削除、`PMW3360DM-T2QU` Pin 3 (`VDDPIX`) を `power_out` に変更、および `PMW3360DM-T2QU_16Pin.kicad_mod` のスルーホールパッド層定義を KiCad 10.0 向けに補完し専用センサーサブ基板 `curcur40-pmw3360` へ統合 |
| **CKW12 水平ローラーエンコーダ フットプリント・3Dモデル**<br>(`RotaryEncoder_Switch_CKW12.kicad_mod`, `pcbs/common/kbd/3dmodels/ckw12_*.stp`) | **[kumamuk-git/CKW12](https://github.com/kumamuk-git/CKW12)** ＆<br>**[kumamuk-git/roBa](https://github.com/kumamuk-git/roBa)**<br>(Original Author: `kumamuk-git`) | **GPL-3.0**<br>([kumamuk-git/roBa LICENSE](https://github.com/kumamuk-git/roBa/blob/main/LICENSE)) | `2026-10-22`: `CKW12.kicad_mod`（`roBa:SW_MX_EC12`）を KiCad 10.0 標準 `Device:RotaryEncoder_Switch` シンボルフィルタに合わせて `RotaryEncoder_Switch_CKW12.kicad_mod` へリネームし、3Dモデル参照パスおよび `CKW12_top` 厚みオフセット `(0, 0, 0.5)` を設定 |
| **ファームウェア定義 (`kbd_firmware/`)**<br>(`kbd_firmware/keyboards/curcur40/`) | **[foostan/kbd_firmware](https://github.com/foostan/kbd_firmware)**<br>**[QMK Firmware](https://github.com/qmk/qmk_firmware)** / **[Vial-QMK](https://github.com/vial-kb/vial-qmk)** | **GPL-2.0-or-later**<br>(`SPDX-License-Identifier: GPL-2.0-or-later`) | `crkbd/rev4_1/mini` の設定をベースに、40キーマトリックス、CKW12 エンコーダ、SPI1 PMW3360 トラックボール（1200 CPI・角度補正）対応ファームウェアとして改変 |
