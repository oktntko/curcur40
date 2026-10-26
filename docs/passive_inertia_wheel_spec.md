# パッシブ磁気慣性ホイールモジュール 設計仕様書（`curcur40-inertia-wheel`）

本書は、電磁クラッチ（ラチェット ⇔ フリースピン切替用のソレノイド・コイル・駆動回路）をあえて持たず、**「高比重ステンレス削り出しホイール × 脱脂ミニチュアベアリング × 渦電流ゼロの非接触磁気ラチェット」** のみによって **『普段は心地よいノッチ感があり、弾けば微振動を伴いながら慣性で回り続け、指で触れればピタッと止まる』** 高速スクロールホイールモジュールの確定設計・試作データ仕様書です。

> [!TIP]
> **単体デスクトップ評価ポッドの組み立て・発注手順** については、専用ビルドガイド **[`docs/inertia_wheel_eval_buildguide_jp.md`](./inertia_wheel_eval_buildguide_jp.md)** を参照してください。

> [!IMPORTANT]
> **確定した基本設計方針（シンプル・高信頼・外形不変）**
> 1. **単体試作先行 → `curcur40-right` Rev2 統合（2種類の高さバリエーション対応）**:
>    * まずは単体 USB-C デスクトップ試作機（`Waveshare RP2040-Zero` キャリア基板 ＋ ホイールモジュール ＋ 専用台座）として製作・調整します。
>    * `curcur40-right` への組み込みは、**タイプA（基板開口なし・ポン付け版：頂点 $Z=+14.50\,\text{mm}$）** と **タイプB（メインPCB内部開口・ロープロファイル沈み込み版：ホイール中心 $Z=+1.40\,\text{mm}$＝キーキャップ上下中央・頂点 $Z=+9.80\,\text{mm}$＝一般的なマウスホイール同等の浮き出し `+6.2 mm`）** の両方に対応します（**どちらもメインPCB・トッププレートの外形サイズおよび既存ケース `cases/right.step` は 100% 無変更**、ベース枠樹脂パーツ1点の差し替えのみで両対応！）。
> 2. **電磁アクチュエータ＆変換マイコン全廃**: ソレノイド・巻線コイル・Hブリッジドライバ・変換用サブマイコン・`+5V` 電源配線をすべて廃止し、クラッチ消費電流 **`0.0 mA`**・故障箇所最小の純パッシブ機構とします。
> 3. **シルバー金属外観 ＋ Oリング着脱 2way 対応（$\varnothing 16.80\,\text{mm}$ `SUS304`）**: 既存のトッププレート開口（`18.20 × 18.20 mm`）を通過する $\varnothing 16.80 \times 5.60\,\text{mm}$ 非磁性ステンレス削り出しホイール（質量 **$7.96\,\text{g}$**）とし、金属むき出しでも市販Oリング装着でも使える 2way 外周溝を設けます。
> 4. **静音ミドルクリック標準搭載（一体揺動キャリッジ）**: `Kailh Square Silent (6.2 × 6.2 × 4.3 mm)` 静音スイッチを採用し、高速回転を指で止めた際に誤クリックせず、押し込み中も磁気ギャップが一切変化しない一体揺動構造とします。

---

## 0. 市販モジュール有無・先行製品／OSS実装実績と物理的根拠

### 0.1 `CKW12` のようにそのまま買える「1U高速スクロールホイール完成キット」は既にあるか？
* **結論：`18 × 18 mm`（1Uキー枠）に収まるキーボード向け「高速慣性スクロールモジュール」の市販キットは現時点で存在しません。**
  * 自作キーボード界隈で流通している水平ホイール系モジュール（廃番の Panasonic `EVQWGD001`、kuma氏 `CKW12`、はやしたろう氏 `THQWGD001` 等）は、いずれも **機械接点ブラシ式ロータリーエンコーダ（`EC05E` 等）＋ 軽量樹脂ホイール** の構成であるため、内部接点の摺動摩擦と板バネのクリック抵抗が大きく、指で弾いても慣性で空転しません。
  * 一方、AliExpress 等で入手できる **Logitech MX Master 3 / G502 用の交換ホイール保守部品** は、横幅・全長が約 $24 \sim 32\,\text{mm}$ あり専用マウント・専用フレキ形状のため、キーボードの 1U スイッチ枠（$18 \times 18\,\text{mm}$）には物理的に収まりません。

### 0.2 本設計の物理原理は「机上の空論・研究止まり」ではないか？（量産製品・OSSでの実証実績）
本モジュールが採用している **「金属フライホイール ＋ ボールベアリング支持 ＋ `AS5600` 非接触磁気角度センサー ＋ 永久磁石による非接触磁気ラチェット」** は、研究段階の未検証技術ではなく、**市販ハイエンドマウスおよび多数のオープンソースハードウェア実機で既に実用・量産されている枯れた技術の組み合わせ**（それを 1U サイズへ高密度パッケージングしたもの）です：

| 実績カテゴリ | 代表的な製品・OSSプロジェクト | 本モジュールとの共通原理・実証されている点 |
| :--- | :--- | :--- |
| **① 市販量産マウス** | **Logitech MagSpeed 搭載機**<br>（MX Master 3 / 3S, MX Anywhere 3 等） | **削り出しステンレスホイール ＋ ミニチュアベアリング ＋ 非接触磁気センサー ＋ 永久磁石による非接触磁気デテント** を採用。ラチェットモードのまま強く弾いた際に「微振動を伴いながら慣性で回り続け、指で触れれば止まる」挙動そのものが量産実証済み。 |
| **② 市販QMKデバイス (OSHW)** | **[Ploopy Knob](https://github.com/ploopyco/knob)**<br>（カナダ Ploopy 社が製品販売中） | **`RP2040`（QMK Firmware）＋ `AS5600` 12-bit 磁気センサー ＋ ボールベアリング** という本機の評価ポッドと完全同一の回路・ファーム構成で市販・安定稼働している実績あり。 |
| **③ 自作キーボード慣性ホイール** | **[`adolto/zmk-driver-ams-as5600`](https://github.com/adolto/zmk-driver-ams-as5600)**<br>**`Spin-maru`** 等 | 自作分割キーボード等で MX Master 風のフリースピン慣性スクロールを実現するために **ベアリング支持ホイール ＋ `AS5600`** を組み込んだ実機プロジェクトが複数公開・動作実証済み。 |
| **④ ミニマル磁気ホイール実機** | **[`torvalds/ScrollWheel`](https://github.com/torvalds/ScrollWheel)**<br>（Linus Torvalds 氏製作） | `RP2350`（RP2040後継）＋ **`AS5600` 磁気角度センサー** による非接触スクロールホイール実機。機械式エンコーダのチャタリング・摩耗を根絶する構成として実証済み。 |

> [!NOTE]
> **実機製作において性能を左右する2つの勘所（失敗防止ポイント）**
> 1. **渦電流ブレーキの物理的遮断（設計で解決済み）**: 導電性の金属ホイールに直接ネオジム磁石を近づけるとレンツの法則（渦電流）で急制動がかかりますが、本設計ではホイール本体を非磁性 `SUS304` とし、ラチェット側を **非導電SLAレジンハブ ＋ 互いに絶縁された独立 $\varnothing 2.0\,\text{mm}$ 鋼球11個** に分離しているため、渦電流ブレーキは発生しません。
> 2. **ミニチュアベアリングの脱脂洗浄（組み立て時に実施）**: 新品の `DDL-520 / MR52` ベアリングには高粘度グリスが封入されているため、組み立て前にパーツクリーナーでグリスを洗い流す（脱脂する）ことで空転持続時間が 1秒未満 → **3〜7秒以上** へ本来の性能を発揮します（手順は [`inertia_wheel_eval_buildguide_jp.md`](./inertia_wheel_eval_buildguide_jp.md) に詳述）。

---

## 1. 全体構造と2種類の高さバリエーション（標準版 vs ロープロファイル沈み込み版）

![Passive Magnetic Inertia Wheel Architecture](assets/passive_inertia_wheel_spec.png)

### 1.1 マウスホイール同等の浮き出しを実現する「ロープロファイル沈み込み版（タイプB）」

![Standard vs Sunk Height Comparison](assets/inertia_wheel_height_comparison.png)

現行 `curcur40-right` のキーキャップ（$Z = -0.80 \sim +3.60\,\text{mm}$）の上下中央は **$Z = +1.40\,\text{mm}$** です。また、`rEXSW1` 直下の既存ケース（[`cases/right.step`](../cases/right.step)）内底面はテンティング傾斜により **$Z \approx -20.5\,\text{mm}$** と非常に深い空間が空いています。
そこで、**ホイール・キャリッジ・11球ハブ・センサー基板は100%共通のまま、ベース枠パーツのみを交換** することで、以下の2種類の実装高さを選択できます：

| 比較項目 | タイプA：標準ポン付け版<br>(`curcur40-right-with-inertia-wheel.step`) | タイプB：ロープロファイル沈み込み版【本命推奨】<br>(`curcur40-right-with-inertia-wheel-sunk.step`) |
| :--- | :---: | :---: |
| **ホイール回転軸高さ ($Z$)** | $Z = +6.10\,\text{mm}$ | **$Z = +1.40\,\text{mm}$（キーキャップ上下中央と完全一致！）** |
| **ホイール頂点高さ ($Z$)** | $Z = +14.50\,\text{mm}$ | **$Z = +9.80\,\text{mm}$（$-4.70\,\text{mm}$ 低背化）** |
| **キーキャップ上面からの浮き出し** | $+10.90\,\text{mm}$（やや背が高い） | **$+6.20\,\text{mm}$（一般的なマウスホイールと同等の自然な高さ！）** |
| **使用するベース枠パーツ** | [`wheel-base-frame.step`](../cases/inertia_wheel/wheel-base-frame.step) | **[`wheel-base-frame-sunk.step`](../cases/inertia_wheel/wheel-base-frame-sunk.step)**（基板裏面フランジ＋スペーサー柱一体型） |
| **メインPCB・プレート外形寸法** | **変更なし（0%）** | **変更なし（0%：外周輪郭は 100% 同一）** |
| **メインPCB・プレート内部加工** | 既存プレート開口 $18.2\times 18.2\,\text{mm}$ のみ<br>（メインPCB開口なし） | プレート＆メインPCBに $18.5\times 18.5\,\text{mm}$ 内窓 ＋ 周囲3箇所の M2 ネジ穴を追加<br>（プレート・基板外周およびキー配置への影響ゼロ） |
| **既存ケース (`cases/right.step`)** | **無改造（干渉 `0.000 mm³`）** | **無改造（干渉 `0.000 mm³`、ケース内壁・底面まで $\ge 3.65\,\text{mm}$ 余裕）** |

### 1.2 マウス風シュラウドカバー（任意オプション `#20A` / `#20B`：内部メカ完全隠蔽＆防塵）

市販の高速スクロールマウス（MX Master 3S / G502 等）と同様に、**`#02` 11球ハブ・`#03` キャリッジ・`#07` センサー基板・`#12` 脱脂ベアリングを完全に覆い隠し、上面スリット（$6.30 \times 15.70\,\text{mm}$）からシルバーの `#01` フライホイールだけを見せるシュラウドカバー（`#20A` / `#20B`）** を選択装着できます：
* **`#20B` 沈み込み用シュラウドカバー（[`wheel-shroud-cover-sunk.step`](../cases/inertia_wheel/wheel-shroud-cover-sunk.step)）**:
  * トッププレート上面（$Z = -2.00\,\text{mm}$）に直接着座し、**`#04B` 沈み込みベース枠とまったく同じ 3箇所の M2 ネジ穴で共締め固定**（追加の基板穴・プレート穴はゼロ、ネジ長のみ `M2 × 4.0mm` → `M2 × 5.0mm` × 3本に変更）。
  * フード天面は $Z = +6.15\,\text{mm}$（キーキャップ上面 $+3.60\,\text{mm}$ から $+2.55\,\text{mm}$）、`#02` 11球ハブ直上の同軸アーチ外径は $R = 7.70\,\text{mm}$（`#01` フライホイール外周 $R = 8.40\,\text{mm}$ より常時 $0.70\,\text{mm}$ 低い段差）のため、指の腹でホイールを弾いてもカバー角が一切指に当たりません。
  * **防塵メリット**: グリスを抜いたドライ状態の `#12` 脱脂ベアリングや `#17` ラチェット磁石へのホコリ・鉄粉の侵入を防ぎ、長い空転性能を維持します。
* **`#20A` ポッド用シュラウドカバー（[`wheel-shroud-cover-eval.step`](../cases/inertia_wheel/wheel-shroud-cover-eval.step)）**:
  * 単体評価ポッド用のフル4面シュラウド。北壁に **$\varnothing 2.80\,\text{mm}$ ドライバー調整穴**（`#18` 磁力調整ネジと同軸）を備え、**カバーを被せたままノッチ感・空転時間の無段階チューニングが可能**です（西壁下端には `#11` センサー4芯線の配線トンネル付き）。

### 1.3 3D CAD / KiCad PCB プレビューギャラリー

| `SUS304` ホイール単体 (`7.96 g`) | ホイールモジュール単体 (24パーツ) |
| :---: | :---: |
| ![SUS304 Flywheel](assets/render_inertia_wheel_flywheel.png) | ![Inertia Wheel Module](assets/render_inertia_wheel_module.png) |
| **タイプA：標準ポン付け版 (`Z_top = +14.5 mm`)** | **タイプB：ロープロファイル沈み込み版・露出 (`Z_top = +9.8 mm`)** |
| ![curcur40-right Standard](assets/render_curcur40_right_inertia_wheel.png) | ![curcur40-right Sunk](assets/render_curcur40_right_inertia_wheel_sunk.png) |
| **タイプB＋`#20B` シュラウドカバー装着（マウス風外観）** | **単体評価ポッド＋`#20A` シュラウドカバー装着** |
| ![curcur40-right Sunk Covered](assets/render_curcur40_right_inertia_wheel_sunk_covered.png) | ![Eval Pod Covered](assets/render_inertia_wheel_eval_pod_covered.png) |
| **単体デスクトップ評価ポッド・露出 (`RP2040-Zero`)** | **評価キャリア基板 ＆ `AS5600` センサー小基板** |
| ![Eval Pod Assembly](assets/render_inertia_wheel_eval_pod.png) | ![Wheel Eval PCB](assets/render_pcb_wheel_eval.png) |

---

## 2. コア機構設計（慣性・渦電流対策・磁力調整・静音クリック）

### 2.1 ホイール本体：`SUS304` シルバー削り出し（2way 外周仕上げ）
* **材質**: 非磁性オーステナイト系ステンレス **`SUS304`**（比重 **$7.93\,\text{g/cm}^3$**、体積 **$1003.9\,\text{mm}^3$**、単体質量 **$7.96\,\text{g}$**）。
* **MX Master 3S 風「2way 外周プロファイル」**:
  * 外周（外径 $\varnothing 16.80 \times$ 幅 $5.60\,\text{mm}$）に **36本の横溝（フルート加工）** と、中央 **幅 $1.30\,\text{mm} \times$ 深さ $0.50\,\text{mm}$ のセンターアクセント溝** を加工。金属むき出しでも、市販Oリング（$\varnothing 15.0 \times 1.0\,\text{mm}$）を嵌めても使える 2way 仕様です。

### 2.2 「渦電流ブレーキ完全ゼロ ＆ JLC3DP 造形基準準拠」の絶縁11球・磁気ラチェット構造
* 非導電性 **SLA レジン製ラチェットハブ（外径 $\varnothing 12.40 \times$ 幅 $3.75\,\text{mm}$）** の軌道半径 $R = 5.10\,\text{mm}$ 上に **$\varnothing 2.00\,\text{mm}$ 精密鋼球（`SUJ2`）× 11個** をスナップイン保持（入口径 $\varnothing 1.94\,\text{mm} \ge \varnothing 1.50\,\text{mm}$、ポケット間肉厚 $0.814\,\text{mm} \ge 0.80\,\text{mm}$）。
* 隣り合う鋼球同士が樹脂で完全に電気絶縁されているため高速回転時の渦電流損失がゼロになり、心地よい微振動を伴いながら伸びやかに空転します。

### 2.3 分解不要の「北東 M2ネジ磁力（ノッチ感 ⇔ 空転伸び）無段階調整」
* キャリッジ北東部（$X_{\text{mod}} = +4.525\,\text{mm}, Z_{\text{mod}} = +5.65\,\text{mm}$）のラチェット磁石背面に **M2 ステンレス調整ネジ（$0.40\,\text{mm}$/回転）** を備え、ノッチ強さと空転持続時間を無段階に調整できます。

### 2.4 静音ミドルクリック機構（一体揺動キャリッジ）
* 北端ヒンジピン（$\varnothing 2.00\,\text{mm}$ `SUS304`）を支点にキャリッジ全体が一体揺動し、南東コーナーの **`Kailh Square Silent (6.2 × 6.2 × 4.3 mm)`** を押下します。押し込み中も磁気ギャップが不変で、スピン停止時に指で触れても誤クリックしません。

---

## 3. 製造・試作データ一式（全自動検証合格済み）

### 3.1 3D CAD モデル（[`cases/inertia_wheel/`](../cases/inertia_wheel/) ＆ [`cases/assemblies/`](../cases/assemblies/)）
生成・検証スクリプト：[`scripts/generate_inertia_wheel.py`](../scripts/generate_inertia_wheel.py)

| ファイル | 用途・発注プロセス | 外形寸法 [mm] | 検証結果 |
| :--- | :--- | :---: | :--- |
| [`sus304-flywheel.step`](../cases/inertia_wheel/sus304-flywheel.step) / `.stl` | JLCCNC `SUS304` 切削ホイール本体 (`7.96 g`) | $16.77 \times 16.77 \times 5.60$ | 水密単一ソリッド・最小穴径 $1.60\,\text{mm}$ **PASS** |
| [`ratchet-hub-11ball.step`](../cases/inertia_wheel/ratchet-hub-11ball.step) / `.stl` | JLC3DP SLA 絶縁11球ラチェットハブ | $12.40 \times 12.40 \times 3.75$ | 最小穴径 $1.94\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-carriage.step`](../cases/inertia_wheel/wheel-carriage.step) / `.stl` | JLC3DP SLA 一体揺動インナーキャリッジ | $13.57 \times 17.32 \times 16.70$ | 最小穴径 $1.76\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-base-frame.step`](../cases/inertia_wheel/wheel-base-frame.step) / `.stl` | JLC3DP SLA 標準ベース枠（評価ポッド／タイプA用） | $17.60 \times 17.60 \times 4.10$ | 最小穴径 $2.06\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-base-frame-sunk.step`](../cases/inertia_wheel/wheel-base-frame-sunk.step) / `.stl` | JLC3DP SLA 沈み込みベース枠（タイプB低背版用） | $23.70 \times 23.70 \times 6.49$ | 最小穴径 $1.60\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`eval-pod-stand.step`](../cases/inertia_wheel/eval-pod-stand.step) / `.stl` | JLC3DP SLA/MJF 単体評価ポッド台座 | $52.00 \times 36.00 \times 6.60$ | 最小穴径 $2.00\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-shroud-cover-eval.step`](../cases/inertia_wheel/wheel-shroud-cover-eval.step) / `.stl` | *(任意)* JLC3DP SLA/MJF ポッド用シュラウドカバー (`#20A`) | $20.20 \times 28.80 \times 18.00$ | 最小穴径 $2.40\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`wheel-shroud-cover-sunk.step`](../cases/inertia_wheel/wheel-shroud-cover-sunk.step) / `.stl` | *(任意)* JLC3DP SLA/MJF 沈み込み用シュラウドカバー (`#20B`) | $24.55 \times 24.55 \times 11.09$ | 最小穴径 $2.40\,\text{mm}$・薄肉違反 `0` **PASS** |
| [`inertia-wheel-module-assembly.step`](../cases/assemblies/inertia-wheel-module-assembly.step) | 標準モジュール検証アセンブリ (24パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`inertia-wheel-module-sunk-assembly.step`](../cases/assemblies/inertia-wheel-module-sunk-assembly.step) | 沈み込みモジュール検証アセンブリ (24パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`inertia-wheel-eval-pod-assembly.step`](../cases/assemblies/inertia-wheel-eval-pod-assembly.step) | 単体デスクトップ評価ポッド検証 (28パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`inertia-wheel-eval-pod-covered-assembly.step`](../cases/assemblies/inertia-wheel-eval-pod-covered-assembly.step) | 単体評価ポッド＋`#20A` カバー装着検証 (29パーツ) | ― | 全ペア `overlap = 0.00000000 mm³`・可動隙間 $\ge 0.35\,\text{mm}$ **PASS** |
| [`curcur40-right-with-inertia-wheel.step`](../cases/assemblies/curcur40-right-with-inertia-wheel.step) | タイプA：無改造 `curcur40-right` 搭載検証 (48パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`curcur40-right-with-inertia-wheel-sunk.step`](../cases/assemblies/curcur40-right-with-inertia-wheel-sunk.step) | タイプB：沈み込み版 `curcur40-right` 搭載検証 (51パーツ) | ― | 全ペア `overlap = 0.00000000 mm³` **PASS** |
| [`curcur40-right-with-inertia-wheel-sunk-covered.step`](../cases/assemblies/curcur40-right-with-inertia-wheel-sunk-covered.step) | タイプB＋`#20B` カバー装着 `curcur40-right` 検証 (52パーツ) | ― | 全ペア `overlap = 0.00000000 mm³`・可動隙間 $\ge 0.35\,\text{mm}$ **PASS** |

### 3.2 KiCad 10.0 回路図・基板・JLCPCB 発注ファイル
* **`AS5600` センサーサブ基板（[`pcbs/inertia-wheel-sensor/`](../pcbs/inertia-wheel-sensor/)）**：$8.80 \times 8.80 \times 0.80\,\text{mm}$、ERC `0/0`・DRC `0/0/0`。
* **単体 USB-C 評価キャリア基板（[`pcbs/inertia-wheel-eval/`](../pcbs/inertia-wheel-eval/)）**：$48.00 \times 32.00 \times 1.60\,\text{mm}$、ERC `0/0`・DRC `0/0/0`。
* **`curcur40-right` Rev2（タイプB 沈み込み版）への統合時変更点（外形サイズ不変）**：
  * `rEXSW1` 中心 $(14.2875, 0.0000)\,\text{mm}$ に **$18.50 \times 18.50\,\text{mm}$ ($R=0.50\,\text{mm}$) の内窓**（メインPCB・トッププレート共通、全周可動クリアランス $\ge 0.48\,\text{mm}$ 確保）と 3箇所の $\varnothing 3.70\,\text{mm}$ ボス貫通穴（トッププレート側は同座標に $\varnothing 2.40\,\text{mm}$ M2 ネジ穴3箇所：`dx=-12.20, dy=-1.90` / `dx=-12.20, dy=+5.80` / `dx=+2.00, dy=-12.20`）を追加し、裏面 `B.Cu` に共通 JST SH 6ピンコネクタを1個配置するだけで、**基板・プレートの外形サイズと既存ケースを1ミリも変えずに統合完了**します（現在 `rEXSW1` 直下を通過している `/D+, /D-` 等の配線は内窓の北側・東側へ容易に迂回可能です）。

### 3.3 単体評価用 QMK ファームウェア（[`kbd_firmware/keyboards/curcur40_wheel_eval/`](../kbd_firmware/keyboards/curcur40_wheel_eval/qmk/qmk_firmware/)）
* `Waveshare RP2040-Zero` 用 `1 kHz` ポーリング `AS5600` カスタムポインティングドライバ（[`wheel_eval.c`](../kbd_firmware/keyboards/curcur40_wheel_eval/qmk/qmk_firmware/rev1/wheel_eval.c)）収録・`.uf2` コンパイル検証済み。

---

## 4. 入手可能な実部品リスト（BOM ＆ 概算コスト）

| 分類 | 部品名・型番 | 仕様・寸法 | 主な入手先 / コード | 単価目安 (1台分) |
| :--- | :--- | :--- | :--- | :---: |
| **ホイール本体** | 特注ステンレスホイール (`SUS304`) | $\varnothing 16.80 \times 5.60\,\text{mm}$ ($7.96\,\text{g}$), シルバー切削 | JLCCNC (`sus304-flywheel.step`) | 約 \$6.00 (¥900) |
| **ベアリング (×2)** | ミニチュアステンレスベアリング **`DDL-520` / `MR52`** | 内径 $\varnothing 2.0 \times$ 外径 $\varnothing 5.0 \times$ 幅 $2.5\,\text{mm}$ × 2個（脱脂使用） | Amazon / MonotaRO | 約 \$2.60 (¥400 / 2個) |
| **ラチェット鋼球** | 精密ベアリング鋼球 (`SUJ2`) | **$\varnothing 2.00\,\text{mm}$** × 11個使用 | Amazon / MonotaRO (`2mm SUJ2 鋼球`) | 約 \$1.50 (¥230 / 100個) |
| **シャフト・ピン** | 非磁性ステンレス平行ピン (`SUS304`/`316`) | ホイール軸 $\varnothing 2.0 \times 15\,\text{mm}$ ×1、ヒンジ軸 $\varnothing 2.0 \times 17\,\text{mm}$ ×1 | Amazon / ミスミ / MonotaRO | 約 \$1.00 (¥150) |
| **磁力調整ネジ** | M2 ステンレス小ねじ / ホーローセット | `M2 × 4〜5 mm`（北東磁力ギャップ調整用） | ホームセンター / Amazon | 約 \$0.20 (¥30) |
| **角度センサーIC** | ams OSRAM **`AS5600-ASOT`** | `SOIC-8`, 12-bit I2C 非接触磁気角度センサー | **LCSC `C499458`** / 秋月電子 | 約 \$1.10 (¥170) |
| **センサー用磁石** | 径方向2極着磁（Diametric）NdFeB磁石 | $\varnothing 3.0 \times 1.0 \sim 1.5\,\text{mm}$ (`N35`) | AliExpress / マグネット専門店 | 約 \$0.50 (¥80) |
| **ラチェット磁石** | 軸方向着磁 小型ネオジム磁石 | $\varnothing 1.5 \sim 2.0 \times 1.5\,\text{mm}$ (`N35`) | Amazon / ハイキューパーツ | 約 \$0.30 (¥50) |
| **静音クリックSW** | **`Kailh Square Silent 6.2×6.2×4.3mm`** | 静音角形マイクロスイッチ（Red Dot, $0.74\,\text{N}$） | 遊舎工房 / Amazon / AliExpress | 約 \$0.35 (¥55) |
| **コネクタ** | JST SH 6ピン横型 **`SM06B-SRSS-TB`** | `curcur40` トラックボール基板と完全同一型番 | **LCSC `C160405`** | 約 \$0.15 (¥25) |
| **Oリング (任意)** | 極細シリコン / NBR Oリング | 内径 $\varnothing 15.0 \times$ 線径 $1.0\,\text{mm}$（2way比較用） | Amazon / MonotaRO | 約 \$0.20 (¥30) |
| **樹脂筐体パーツ** | ベース枠（標準／沈み込み）＋ キャリッジ ＋ 11球ハブ ＋ 台座 | 高精度 SLA レジン造形 | JLC3DP SLA (`8001` 等) | 約 \$3.20 (¥480) |
| **単体評価キャリア** | **`Waveshare RP2040-Zero`** ＋ 評価基板 | Stage 1 単体 USB-C テストベッド (`48 × 32 mm`) | Amazon / JLCPCB | 約 \$3.50 (¥530) |
| **合計（概算）** | ― | **ホイールモジュール単体 約 ¥2,600** ＋ 単体評価キャリア 約 ¥530 | ― | **約 ¥3,130** |
