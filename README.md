# curcur40

**curcur40** は、[Corne Keyboard (crkbd v4)](https://github.com/foostan/crkbd) をベースに、Kailh Choc V1/V2 ロープロファイルスイッチ専用の **40キー左右分割レイアウト**、右手親指内側の **$\varnothing 25\,\text{mm}$ 光学式トラックボール（PMW3360DM-T2QU シングルボード統合）**、および右手人差し指内側の **水平ローラーエンコーダ（CKW12）** を融合したカスタム分割エルゴノミクスキーボードです。

![Full Assembly Isometric](./docs/assets/render_full_assembly_iso.png)

---

## 主な特徴 (Key Features)

- **40キー + 25mm トラックボール + 水平ローラーエンコーダ**:
  - **左手 (21キー)**: メイン $3\times 5$ (15キー) ＋ 内側縦2キー (`EXSW1`, `EXSW2`) ＋ 親指4キー (`SW1`, `SW8`, `SW9`, `EXSW3`)
  - **右手 (19キー + 2デバイス)**: メイン $3\times 5$ (15キー) ＋ 内側下段1キー (`rEXSW2`) ＋ 親指外側3キー (`rSW1`, `rSW8`, `rSW9`) ＋ **水平ローラーエンコーダ (`CKW12`)** ＋ **$\varnothing 25\,\text{mm}$ トラックボール (`PMW3360DM-T2QU` + `LM19-LSI`)**
- **PMW3360 光学センサーの右手メイン基板へのシングルボード統合**:
  - センサー子基板やピンヘッダーを使わず、右手メイン基板（`curcur40-right`）へ `PMW3360DM-T2QU` および `1.8V` LDO（`TLV74318PDBVR`）を直接統合。
  - 基板の矩形開口（$8.70 \times 16.90\,\text{mm}$）に表面から `LM19-LSI` レンズをスナップイン装着し、裏面からセンサーICを差し込んで表面スルーホールでハンダ付けする高剛性・省スペース構造により、ケース外底面高さ **$Z = -12.30\,\text{mm}$** の薄型トレイ設計を実現。
- **13箇所 M2 5.50mm スペーサーによる統一締結アーキテクチャ**:
  - 左手外周 5箇所（`L1`〜`L5`、うち `L5` は右手トラックボール南東穴 `TB4` と左右対称配置）＋ 右手外周 4箇所（`R1`〜`R4`）＋ トラックボールカップ固定耳 4箇所（`TB1`〜`TB4`）＝ **計 13箇所**すべてを **M2 5.50mm メス-メス スペーサー（外径 $\varnothing 3.0\,\text{mm}$）** と上下の **M2 × 4.0mm ネジ（計 26本）** で締結。
  - ケース内底面（$Z = -9.10\,\text{mm}$）から立ち上がるスペーサーがメイン基板の $\varnothing 3.60\,\text{mm}$ 貫通穴を通って基板表面（$Z = -3.60\,\text{mm}$）と完全にツライチとなり、底面外側の **$\varnothing 4.60 \times 0.90\,\text{mm}$ ザグリ穴**によってネジ頭が底面から一切突出しないフラット構造。
- **3爪スリムアーチ保持・3点セラミック球支持トラックボールカップ**:
  - $\varnothing 2.0\,\text{mm}$ G5 窒化ケイ素（$\text{Si}_3\text{N}_4$）セラミックベアリング球 3個で $\varnothing 25.0\,\text{mm}$ ボールを低摩擦支持し、上部のスリムアーチ3爪（スロート径 $\varnothing 24.59\,\text{mm}$、食い込み量 $0.205\,\text{mm}$）で逆さにしても落下しないスナップイン保持と全方位の指クリアランスを両立。
- **RP2040 オンボード & QMK / Vial 完全対応**:
  - 左右とも `RP2040` + `16MB` QSPI Flash (`W25Q128JVSIQ`) をオンボード実装し、ダイオードレスのダイレクトピン接続を採用。Vial GUI からキーマップ・ロータリーエンコーダ・トラックボール設定をリアルタイム変更可能。

---

## ドキュメント・設計仕様書 (Documentation)

| ドキュメント | 内容 |
| :--- | :--- |
| **[ビルドガイド (`docs/buildguide_jp.md`)](./docs/buildguide_jp.md)** | 必要パーツ一覧（BOM）、JLCPCB PCBA 発注手順、PMW3360/CKW12 の手ハンダ手順、ケース・トラックボールカップ組み立て手順、ファームウェア書き込み手順 |
| **[ケース・機構設計仕様書 (`docs/case_spec.md`)](./docs/case_spec.md)** | Z軸スタックアップ定義、13箇所 M2 5.50mm スペーサー締結仕様、外周ポート開口（USB-C / TRRS）、トラックボールカップ＆光学距離（$2.40\,\text{mm}$）仕様 |
| **[PCB・回路図設計仕様書 (`docs/pcb_spec.md`)](./docs/pcb_spec.md)** | 左右メイン基板の回路構成、RP2040 GPIO ピンアサイン表、PMW3360 シングルボード統合仕様、カスタムライブラリ一覧、DRC/ERC 検証基準 |
| **[生成スクリプト一覧 (`scripts/README.md`)](./scripts/README.md)** | 3Dモデル（ケース・カップ・フルアセンブリ）、トッププレート、JLCPCB 発注データ、プレビュー画像の再現生成スクリプト（全8本）の説明 |

---

## 3D プレビュー・完成イメージギャラリー (3D Preview Gallery)

KiCad 10.0 Raytracing（`kicad-cli pcb render`）および `cadgen` 3D CAD レンダラーで出力した完成イメージ一覧です。

### 1. フルアセンブリ（3Dプリントケース + メイン基板 + トッププレート + 25mmトラックボール + CKW12エンコーダ）

#### 斜視図（アイソメトリックビュー）
![Full Assembly Isometric](./docs/assets/render_full_assembly_iso.png)

#### 上面図（トップビュー）
![Full Assembly Top](./docs/assets/render_full_assembly_top.png)

#### 底面図（ボトムビュー：13箇所 Ø4.6mm×0.9mm ザグリ穴、L5–TB4 左右対称配置）
![Full Assembly Bottom](./docs/assets/render_full_assembly_bottom.png)

---

### 2. 左手メイン基板 (`curcur40-left`)
- **構成**: 21キー（メイン $3\times 5$ + 内側 1u×2 + 親指 1u×4）
- **制御回路**: `RP2040`（QFN-56）+ `W25Q128JVSIQ`（16MB QSPI Flash）+ USB Type-C（ESD保護 `TPD4E05U06DQAR`・VBUS逆流防止ダイオード搭載）+ TRRS/TRS 4極ジャック
- **外周固定穴**: 5箇所（$\varnothing 3.60\,\text{mm}$ 貫通穴、M2 5.50mm スペーサー挿通用。親指下穴 `L5` $(-21.5250, 63.6875)$ は右手トラックボール南東穴 `TB4` $(21.5250, 63.6875)$ と完全左右対称）

#### 表面（スイッチ差し込み面 / `F.Cu`）
![Left PCB Top](./docs/assets/render_left_top.png)

#### 斜視図（アイソメトリックビュー）
![Left PCB Isometric](./docs/assets/render_left_iso.png)

#### 裏面（部品実装面 / `B.Cu`）
![Left PCB Bottom](./docs/assets/render_left_bottom.png)

---

### 3. 右手メイン基板 (`curcur40-right`：PMW3360 シングルボード統合設計)
- **構成**: 19キー（メイン $3\times 5$ + 内側下段 1u×1 + 親指外側 1u×3）+ 水平ローラーエンコーダ **CKW12**（`rEXSW1`: $(14.2875, 0.0000)\,\text{mm}$）+ **25mm トラックボール光学センサー統合部**（中心 $(9.5250, 52.3875)\,\text{mm}$）
- **シングルボード統合アーキテクチャ**:
  - 右手メイン基板に `PMW3360DM-T2QU`（`U1`）および `1.8V` LDO（`U2`: `TLV74318PDBVR`）回路を直接統合。
  - 裏面（`B.Cu`）の電圧選択ジャンパ `JP1` は、**Pad 1（`+3V3R`）– Pad 2（`/V_{IO}`）間が基板の銅箔パターンで最初から直結（`SolderJumper_3_Bridged12`）** されており、手作業でのブリッジは不要。
  - `R4`（28kΩ）、`C5`（22nF）、およびデバッグ端子 `J4` / `rJ4` は **DNP（未実装）** 指定。
- **固定穴・光学開口**:
  - 外周スペーサー貫通穴 4箇所（$\varnothing 3.60\,\text{mm}$）+ トラックボールカップ固定用スペーサー貫通穴 4箇所（$\varnothing 3.60\,\text{mm}$：中心 $(9.5250, 52.3875)\,\text{mm}$ から $X \pm 12.00\,\text{mm}, Y \pm 11.30\,\text{mm}$）＝ 計 8箇所
  - PMW3360 光学窓＆LM19-LSI レンズ脚部用の矩形開口（$8.70 \times 16.90\,\text{mm}$）

#### 表面（スイッチ・トラックボールカップ搭載面 / `F.Cu`）
![Right PCB Top](./docs/assets/render_right_top.png)

#### 斜視図（アイソメトリックビュー）
![Right PCB Isometric](./docs/assets/render_right_iso.png)

#### 裏面（SMD部品・PMW3360センサー実装面 / `B.Cu`）
![Right PCB Bottom](./docs/assets/render_right_bottom.png)

---

### 4. FR-4 トッププレート (`plate-top-left` / `plate-top-right`)
- **材質・板厚**: FR-4（ガラスエポキシ基板材）、板厚 $1.60\,\text{mm}$（$Z = -1.60 \sim 0.00\,\text{mm}$）
- **ネジ穴仕様**: すべて **$\varnothing 2.40\,\text{mm}$ ストレート貫通穴（ザグリなし）**（左手 5箇所、右手 4箇所）。上から M2 × 4.0mm ネジを通してメイン基板表面とツライチの M2 5.50mm スペーサー上端へ締結。
- **右手プレート形状**: CKW12 水平ローラーエンコーダ用の開口（$18.20 \times 18.20\,\text{mm}$）および親指内側のトラックボールカップ領域を切り欠いた L字ノッチ形状。

#### 左手トッププレート (`plate-top-left`)
![Left Top Plate](./docs/assets/render_plate_left.png)

#### 右手トッププレート (`plate-top-right`)
![Right Top Plate](./docs/assets/render_plate_right.png)

---

### 5. トラックボールカップ・光学スタックアップ検証モデル
[`cases/`](./cases/) 配下の3Dプリント用モデルおよび4つの光学検証アセンブリモデルです。4つの検証アセンブリ STEP には、GUI（CAD Viewer等）の計測ツールで直接選択してボール底面（$Z_{\text{rel}} = +5.80\,\text{mm}$）との距離（設計値 **$2.40\,\text{mm}$**）を計測できるよう、レンズ側光学距離基準点（**`Lens_Optical_Ref_Point`**, $Z_{\text{rel}} = +3.40\,\text{mm}$ / グローバル $Z = -0.20\,\text{mm}$）が独立オブジェクトとしてプロットされています。

| トラックボールカップ単体 (`trackball-cup.step`) | 25mmボール・レンズ組込 (`trackball-cup-with-ball.step`) |
| :---: | :---: |
| ![Trackball Cup](./docs/assets/trackball_cup_render.png) | ![Trackball Cup with Ball](./docs/assets/trackball_cup_with_ball_render.png) |

---

## リポジトリ構成と発注用データ (Repository Structure & Production Files)

```text
curcur40/
├── cases/                        # 3Dプリント用ケース・トラックボールカップ・検証用フルアセンブリ (STEP / STL)
│   ├── left.step / left.stl      # 左手トレイ型ボトムケース
│   ├── right.step / right.stl    # 右手トレイ型ボトムケース
│   ├── trackball-cup.step / .stl # 25mmトラックボール用スナップインカップ
│   └── assembly-full.step        # 全95パーツ統合・干渉ゼロ検証済みフルアセンブリ
├── pcbs/                         # KiCad 10.0 左右メイン基板プロジェクト & JLCPCB PCBA 発注データ
│   ├── left/                     # 左手メイン基板 (curcur40-left)
│   │   └── jlcpcb/production_files/  # GERBER-curcur40-left.zip, BOM-curcur40-left.csv, CPL-curcur40-left.csv
│   ├── right/                    # 右手メイン基板 (curcur40-right: PMW3360統合)
│   │   └── jlcpcb/production_files/  # GERBER-curcur40-right.zip, BOM-curcur40-right.csv, CPL-curcur40-right.csv
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

- **基板・回路・ケース・ドキュメント (`pcbs/`, `plates/`, `cases/`, `docs/`, `scripts/`)**:
  - [MIT License](./LICENSE_MIT) および [CC BY 4.0](./LICENSE_CC) のデュアルライセンスで公開しています（原著作者: Kosuke Adachi / `foostan` 氏の [crkbd](https://github.com/foostan/crkbd) および [kbd](https://github.com/foostan/kbd) をフォーク・改変）。
- **PMW3360 センサー回路・ライブラリ (`pcbs/common/kbd/kicad-symbols/pmw3360_pcb.kicad_sym` 等)**:
  - [SideraKB/PMW3360_PCB](https://github.com/SideraKB/PMW3360_PCB)（[CERN-OHL-P v2](https://ohwr.org/project/cernohl/wikis/Documents/CERN-OHL-version-2) — Permissive）および [monkeypad/pmw3360-breakout](https://github.com/monkeypad/pmw3360-breakout)（MIT License）をベースにシングルボード統合・改変しています。
- **CKW12 水平ローラーエンコーダ 3Dモデル (`pcbs/common/kbd/3dmodels/ckw12_*.stp`)**:
  - [kumamuk-git/CKW12](https://github.com/kumamuk-git/CKW12) / [kumakey/roBa](https://github.com/kumakey/roBa) にて公開されているモデルを使用しています。
- **ファームウェア (`kbd_firmware/keyboards/curcur40/`)**:
  - [QMK Firmware](https://github.com/qmk/qmk_firmware) / [Vial-QMK](https://github.com/vial-kb/vial-qmk) に準拠し、**GPL-2.0-or-later** ライセンスの下で提供されます。
