# curcur40 AI エージェント運用ルール (AGENTS.md)

本ファイルは、ワークスペース `curcur40` において AI エージェントが常時遵守すべき最上位の運用ルール・表記規則・仕様書ルーティングを定義します。

---

## 1. 基本行動原則・Git 運用・ドキュメント記述ルール

1. **作業着手前の方針確認**:
   - ファイルの変更や再生成が必要と判断した場合は、**いきなりコード変更やデータ生成に入らず、まずユーザーへ対応方針を提案・確認してから作業を行うこと**。
   - ただし、**ユーザーから明示的に作成・変更・生成の依頼があった場合は、事前確認なしで直ちに実行してよい**。
2. **タスク／フェーズ単位での Git コミット**:
   - タスクやフェーズが完了した際は、タスクごとに Git コミットを作成し、履歴から差分が明確に追えるようにすること（コミットしない方がよい理由がある場合は事前に確認すること）。
3. **仕様書ファースト（Single Source of Truth とルーティング）**:
   - 対象領域の作業を行う前に、必ず対応する以下の正本ドキュメントを読み込むこと。また、**同じ数値表や BOM を複数ファイルに重複記載してはならない**：
     - 全体 Zスタックアップ・19箇所ネジ座標・ケース・トッププレート仕様: [`docs/case_spec.md`](docs/case_spec.md)
     - 全3基板・3-in-1パネル・回路設計根拠・ピンアサイン・SMD部品表: [`docs/pcb_spec.md`](docs/pcb_spec.md)
     - トラックボールカップ・光学距離・2D慣性スクロール FW 仕様: [`docs/trackball_spec.md`](docs/trackball_spec.md)
     - アンダープレート慣性ホイール機械設計・3Dホール角度復調 FW 仕様: [`docs/wheel_spec.md`](docs/wheel_spec.md)
     - 持ち運び用キャリングボックス・浅角カムスナップフタ仕様: [`docs/carrying_box_spec.md`](docs/carrying_box_spec.md)
     - 購入部材（BOM・URL）・JLC 3社発注手順＆ノウハウ・組立手順: [`docs/buildguide_jp.md`](docs/buildguide_jp.md)
     - 生成スクリプト一覧（全12本）・DFM / 6-DOF / 干渉ゼロ自動検証基準: [`scripts/README.md`](scripts/README.md)
     - 外部仕様（ギャラリー・ハード仕様・ソフト仕様・キーマップ）: [`README.md`](README.md)
   - エラーや警告を回避するためだけに不要な配線を追加したり、DRC / ERC / DFM ルールを無効化する対症療法は絶対に行わないこと。
4. **Markdown 記述ルール（LaTeX 単位・記号表記の禁止）**:
   - GitHub 上でのレンダリング崩れを防ぐため、**Markdown ドキュメント内で `$...$` や `\varnothing`, `\text{mm}`, `^\circ` 等の LaTeX 数式記法を用いて寸法・単位・記号を記述してはならない**。必ずプレーンテキスト／Unicode／バッククォート（例: `2.85 mm`, `⌀2.85 mm`, `11.80°`, `±0.02 mm`, `774 g·mm²`）を使用すること（金額表記も数式誤認を防ぐため `USD` 等を用いること）。
   - ドキュメントには現在の確定仕様と設計根拠のみを簡潔に記述し、過去ボツ案との比較や変動しやすい総ソリッド数カウントを書き残さないこと。
5. **長時間処理・ハング防止ルール**:
   - 自動配線・3D ブーリアン演算・距離検査スクリプトを実行する際は、実行前に予想時間を見積もり、フェーズごとの経過秒数ログ（`flush=True`）と `time.monotonic()` によるハードタイムアウト上限（`MAX_RUNTIME_SEC`）を必ず設けること（純 Python 二重ループによる大規模グリッド走査は避け、ベクトル化やバウンディングボックス枝刈りを行うこと）。
   - バックグラウンド化したコマンドが予想時間の 2倍（または無出力 120秒）を超過した場合は、放置せず直ちに `kill` して計算量を見直すこと。

---

## 2. ディレクトリ構成とファイル管理ルール

1. **一時ファイル・使い捨てスクリプトの残置禁止**:
   - `scratch/` や `tmp/`、`.json` / `.rpt` / `.net` / `.bak` / `.kicad_prl` 等を作業後に残さないこと（一時出力には `tempfile.TemporaryDirectory` を使用）。
2. **公式スクリプトの一元管理 (`scripts/`)**:
   - 生成・検証処理は [`scripts/`](scripts/) 配下の 12本の公式スクリプトに集約し、パス参照は必ず `WORKSPACE = Path(__file__).resolve().parent.parent` からの相対解決で記述すること。
3. **STEP 一本化（`.stl`・ボトムプレート作成禁止）と `cases/` 構成**:
   - 重複する `.stl` ファイルおよび廃止済みのボトムプレートは生成・出力しないこと。
   - `cases/` 直下にはケース・カップ・キャリングボックスの `.step`、`cases/inertia_wheel/` 配下には慣性ホイール 4部品の `.step` と同名 2D 公差図面 `steel-flywheel.pdf`、`cases/assemblies/` 配下には検証・レンダリング用アセンブリ `.step`（8種）を分離して管理すること。
4. **ドキュメント・画像アセットの一元管理 (`docs/`)**:
   - 仕様書・体験型 HTML・プレビュー画像はすべて `docs/` および `docs/assets/` 配下に格納すること。

---

## 3. PCB・回路図（KiCad 10.0）のルール

1. **実行環境**:
   - KiCad CLI: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\kicad-cli.exe`
   - KiCad Python: `$env:LOCALAPPDATA\Programs\KiCad\10.0\bin\python.exe`
2. **ライブラリ参照ポリシー（シャドウイング禁止）**:
   - KiCad 公式標準ライブラリをローカルの `sym-lib-table` / `fp-lib-table` で上書きしてはならない。ローカル登録は `pcbs/common/kbd/` 配下の `kbd` および `PMW3360_PCB` のみとする。
3. **`pcbnew` Python API の注意事項**:
   - KiCad 10.0 では `PCB_VIA` に対してレイヤー引数なしで `GetWidth()` や `GetEnd()` を呼ぶと C++ アサーション停止する。`board.GetTracks()` 走査時は必ず `PCB_TRACK` と `PCB_VIA` を分岐させ、ビアには `t.GetWidth(pcbnew.F_Cu)` および `t.GetPosition()` を使用すること。
4. **回路・基板の不変仕様（詳細は [`docs/pcb_spec.md`](docs/pcb_spec.md) 参照）**:
   - `PMW3360`（`U1`）Pin 3（`VDDPIX`）は内部レギュレータ出力のため外部 `1.8 V` とショートさせず独立ネットに保つこと。`JP1` は銅箔ブリッジ維持、`R4` / `C5` / `J4` / `rJ4` は `DNP` 維持、右メイン `rU6`（`TMAG5273`）Pin 5 は `rR13`（`0 Ω`）経由 `GNDR` 接続による `TLV493D-A1B6` 互換設計を維持すること。
5. **DRC / ERC / プリフライト合格基準（詳細は [`scripts/README.md`](scripts/README.md) 参照）**:
   - 全基板・パネル・トッププレートで DRC 違反 0件・未接続 0件・回路図不一致 0件、ERC エラー 0件（左右メインの `GPIO21` 左右判定ピン直結による `pin_to_pin` 警告 1件のみ許容）を満たすこと。
6. **PCB・プレート変更時の 3D アセンブリ干渉検証必須化と 3D モデル未設定 NG 時の厳格運用**:
   - 基板外形・穴（`Edge.Cuts`）、部品配置、フットプリント、3D モデル、またはトッププレートを変更した際は、`scripts/export_jlcpcb.py` だけで完了とせず、**必ず [`scripts/generate_full_assembly.py`](scripts/generate_full_assembly.py) も実行して 3D 干渉体積 `0.00000000 mm³`・クリアランス・6-DOF 拘束を検証し `cases/assemblies/*.step` を同期すること**。
   - **【重要】3D モデル未設定・リンク切れ（NG）検知時の勝手にパスさせる行為の禁止**: 有効な `.step`/`.stp` 3D モデル未設定エラーが発生した場合、独断でダミー・推測形状を自作したり除外リストへ追加して素通りさせてはならない（確定除外は `JP1` と光学側配置 `PMW3360 U1` の 2点のみ）。NG のまま停止して対象部品をユーザーへ報告し、対応方針を合意してから進めること。

---

## 4. 3D CAD (`cadgen` / `build123d`) のルール

1. **実行環境**:
   - `& "$env:USERPROFILE\.local\bin\uvx.exe" --no-config --managed-python --python 3.13 --from "cadgen==0.7.26" python`
2. **光学距離基準面 (`Lens_Optical_Ref_Point`) の維持**:
   - 4つの検証アセンブリ STEP（`pmw3360-lens-pcb-assembly.step`, `trackball-cup-with-ball.step`, `assembly-full.step`, `assembly-full-desk.step`）には、25 mm ボール最下面との規定光学距離（`2.4000 mm`）を CAD ビューアで直接計測できるよう、名前付きオブジェクト **`Lens_Optical_Ref_Point`** を必ず含めること（詳細は [`docs/trackball_spec.md`](docs/trackball_spec.md) 参照）。
3. **JLC3DP / JLCCNC 準拠・干渉ゼロ・6-DOF 自動検証**:
   - 3D モデル更新時は対応する生成スクリプトおよび `scripts/generate_full_assembly.py` を実行し、[`scripts/README.md`](scripts/README.md) 第3節に定める全基準（造形サイズ・底面接地・穴径 `≥ ⌀1.50 mm`・穴深さ比 `h/Φ ≤ 3.0`・薄肉検証・静止＆クリック押下＆ボックス収納時の干渉体積 `0.00000000 mm³`・6-DOF 拘束）で違反 0件を確認すること。

---

## 5. 確定設計根拠の確認（誤指摘・勝手な仕様変更の防止）

以下の設計は実部品データシート・公差計算・実機検証に基づく確定仕様である。変更やレビューを行う際は誤認による改変を行わず、必ず各仕様書の設計根拠を確認すること：
- 短胴 USB-C `TYPE-C-31-M-13C` におけるプラグ金属シェル露出と最小ケース開口（`10.20 × 4.40 mm`）、スイッチ嵌合プレート保持、キー谷間 `⌀5.20 mm` フラットボス＋USB-C 内壁受け棚: [`docs/case_spec.md`](docs/case_spec.md)
- `PMW3360` / `LM19-LSI` の非対称丸ガイドポスト座標と `55.0°` セラミック支持球配置: [`docs/trackball_spec.md`](docs/trackball_spec.md)
- 1ピース一体軸 `45# Steel + Blackening` ホイール（軸公差 `⌀1.97 ±0.02 mm` 同名 PDF 図面指定）、接着剤ゼロ保持、スリット分離型 Cクリップヒンジ、オンボード `TMAG5273` `XZX` 復調: [`docs/wheel_spec.md`](docs/wheel_spec.md)
