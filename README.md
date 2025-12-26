# jupyterlab-paperspace-model-cockpit

`jupyterlab-paperspace-model-cockpit` は、  
**Paperspace 上の JupyterLab + ComfyUI 環境向けに設計された、宣言的モデル管理用の JupyterLab 拡張機能**です。

Paperspace の「環境が定期的に消える」という前提を正面から受け止め、  
**状態を持たず、再現性を最優先**にしたモデル管理を提供します。

---

## 背景と目的

Paperspace 環境では、次のような運用が一般的です。

- 環境は一定時間で破棄される
- モデルファイル（checkpoint / LoRA / VAE など）は毎回入れ直しになる
- どのモデルを使うかは、ほぼ毎回決まっている

このとき問題になるのが、

- 何を入れるかを毎回手動で思い出す必要がある
- 中途半端なダウンロードや状態管理が混乱を生む
- UI を開かないと環境が整わない

この拡張は、それらを次の考え方で解決します。

- **モデル構成は JSON で宣言する**
- **インストール状態はファイルの有無だけで判断する**
- **必要なものだけを自動でダウンロードする**
- **UI を開かなくても環境が完成する**

---

## 特徴

### 宣言的モデル管理
- `models.json` に「どのモデルを使うか」を定義
- checkpoint / LoRA / VAE などをまとめて扱える
- 状態DB（SQLiteなど）は使用しない

### バンドルによる一括管理
- 複数モデルを **bundle** として定義
- よく使う構成をワンクリック、または自動でインストール

### 起動時の自動インストール
- bundle に `auto_install` を指定可能
- JupyterLab 起動時に、必要なモデルが自動で揃う
- UI を開く必要はない

### 安全で単純なダウンロード設計
- ダウンロードは **常に直列**
- 失敗・キャンセル時はファイルを削除
- 中途半端な状態を残さない

---

## しないこと

この拡張は、あえて次のことをしません。

- 並列ダウンロード
- インストール状態の永続管理
- 複雑な履歴・ログ管理
- 自動更新や差分アップデート
- モデルの意味的な互換性チェック

Paperspace 環境では「壊れないこと」「再構築できること」を最優先します。

---

## 想定ユースケース

- Paperspace + JupyterLab + ComfyUI を日常的に使う
- 毎回ほぼ同じモデルセットを使う
- 環境起動後、何も考えずに作業を始めたい
- モデル管理に余計な状態やDBを持ち込みたくない

---

## 基本コンセプト

- **models.json = 宣言**
- **ファイルの存在 = 状態**
- **bundle = モデルの集合**
- **失敗したら消してやり直す**

この拡張は「正しく忘れる」ことを前提に作られています。

---

## アーキテクチャ概要

- JupyterLab 拡張として動作
- フロントエンドとサーバーサイドを分離
- モデルのダウンロード・管理はサーバー側で実行
- UI はあくまで操作用の補助

ディレクトリ構成や技術スタックは、  
一般的な JupyterLab 拡張の構成に従います。

---

## 技術スタック

本拡張機能のフロントエンド UI は、以下の技術スタックを前提としています。

- React 18
- MUI (Material UI v5)
- Emotion (MUI styling engine)
- JupyterLab 4.x Extension API
- Lumino Widget + React integration

UI 実装では、JupyterLab 標準の UI コンポーネントと併用しつつ、
基本的なレイアウト・操作部品には MUI を使用します。

## ファイル配置

models.json は Jupyter サーバーのルートディレクトリに配置されることが想定されています。

---

## ステータス

このプロジェクトは現在開発中です。  
設計は Paperspace 環境での実運用を前提に固められています。

---

## Installation

```bash
pip install -e .
```

## Development

### セットアップ

1. venv環境を作成して有効化：
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# または
venv\Scripts\activate.bat     # Windows CMD
```

2. パッケージをインストール：
```bash
pip install -e .
```

3. Node.jsの依存関係をインストール：
```bash
jlpm install
```

### 開発コマンド

#### ビルド

```bash
# 開発モードでビルド（推奨）
jlpm run build

# 本番モードでビルド
jlpm run build:prod

# TypeScriptのみコンパイル
jlpm run build:lib

# JupyterLab拡張のみビルド（開発モード）
jlpm run build:labextension:dev

# JupyterLab拡張のみビルド（本番モード）
jlpm run build:labextension
```

#### ウォッチモード（自動再ビルド）

```bash
# ファイル変更を監視して自動再ビルド
jlpm run watch

# TypeScriptのみ監視
jlpm run watch:src

# JupyterLab拡張のみ監視
jlpm run watch:labextension
```

#### クリーンアップ

```bash
# ビルド成果物を削除
jlpm run clean:all

# TypeScriptのビルド成果物のみ削除
jlpm run clean:lib

# JupyterLab拡張のビルド成果物のみ削除
jlpm run clean:labextension
```

#### リント

```bash
# ESLintでコードをチェック・修正
jlpm run eslint

# リント（prettier + eslint）
jlpm run lint
```

### JupyterLabの起動

```bash
jupyter lab
```

### 動作確認

1. ブラウザのコンソール（F12）で `JupyterLab extension comfyui-cockpit is activated!` が表示されることを確認
2. ランチャーに「ComfyUI Cockpit」が表示されることを確認
3. コマンドパレット（Ctrl+Shift+C）で「ComfyUI」を検索してコマンドが表示されることを確認

### 拡張機能の状態確認

```bash
# インストールされている拡張機能の一覧を表示
jupyter labextension list
```

## 本番ビルドとインストール

既存の JupyterLab 環境に本番用としてインストールする手順です。

### 1. パッケージのビルド

配布用のパッケージ（Wheelファイル）を作成します。
このプロセスでフロントエンドコードも自動的に本番モード（`build:prod`）でビルドされ、パッケージに含まれます。

```bash
# ビルドツールのインストール
pip install build

# パッケージのビルド
python -m build
```

実行後、`dist/` ディレクトリに `.whl` ファイル（例：`jupyterlab_paperspace_model_cockpit-0.1.0-py3-none-any.whl`）が生成されます。

### 2. インストール

#### カレントディレクトリからインストールする場合

```bash
# -e オプションなしでインストール
pip install .
```

#### 生成したWheelファイルからインストールする場合（推奨）

Paperspace上の環境など、別の環境にデプロイする場合は、生成された `.whl` ファイルをJupyterLabのファイルブラウザ経由でアップロード（例：`/notebooks` ディレクトリなど、任意の場所）してインストールします。

```bash
# ファイル名は生成されたバージョンに合わせてください（/notebooks にアップロードした場合）
pip install /notebooks/jupyterlab_paperspace_model_cockpit-0.1.0-py3-none-any.whl
```

### 3. 適用確認

JupyterLabを再起動した後、拡張機能が正しく読み込まれているか確認します。

```bash
jupyter labextension list
```

`jupyterlab-comfyui-cockpit vX.X.X enabled OK` と表示されていればインストール完了です。
