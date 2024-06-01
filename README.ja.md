# ailingo: 生成AI(LLM)を使った、ローカルファイル翻訳のためのCLIツール

**ailingo** は、生成AIを利用してローカルファイルを様々な言語に翻訳するコマンドラインインターフェース(CLI)ツールです。

<p align="center">
    <a href="https://github.com/yamitzky/ailingo/releases" target="_blank">
        <img alt="Releases" src="https://img.shields.io/github/v/release/yamitzky/ailingo"></a>
    <a href="https://github.com/yamitzky/ailingo/actions/workflows/check_diffs.yml" target="_blank">
        <img alt="CI" src="https://github.com/yamitzky/ailingo/actions/workflows/lint.yml/badge.svg"></a>
    <a href="https://opensource.org/licenses/MIT" target="_blank">
        <img alt="MIT License" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README.ja.md">日本語</a> |
  <a href="./README.zh-CN.md">简体中文</a> |
  <a href="./README.zh-TW.md">繁体中文</a> |
  <a href="./README.es.md">Español</a>
</p>

## 概要

開発者、翻訳者、コンテンツ制作者がファイルを効率的に多言語化できるように設計されています。

**主な機能:**

- **柔軟なファイル処理:** 複数のファイルを一度に翻訳できます。
- **幅広い言語サポート:** 翻訳元と翻訳先の言語を自由に指定できます。
- **生成AIモデルの選択:** ChatGPT、Gemini、Anthropicなど、litellmで利用可能な様々な生成AIモデルから選択できます。
- **カスタマイズ可能な出力:** 翻訳されたファイルの名前と保存場所を制御できます。
- **翻訳リクエストの追加**: カジュアルな口調など、翻訳のニュアンスのリクエストを追加できます。
- **書き換えモード**: スペル/文法修正を行って同じ言語でテキストを書き直したり、リクエストに応じて文体を調整したりできます。
- **エディターモード**: エディターでテキストを直接翻訳できます。
- **URLモード**: ウェブページをダウンロードして翻訳できます。

## インストール

### 前提条件:

- Python 3.11

## Quick Start:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
pip install ailingo
ailingo my_document.txt --target ja
```

### 詳細なセットアップ手順:

#### 1. litellmのセットアップ:

このプログラムは、生成AIにアクセスするためにLiteLLMを使用しています。LiteLLMは、様々なプロバイダーと連携するように設計されています。使用する生成AIモデルのプロバイダーでアカウントを作成し、APIキーを取得してください。

詳しいセットアップは、[LiteLLM](https://docs.litellm.ai/docs/providers)のドキュメントを参考にしてください。以下に、代表的なAPIキーの設定例を示します。

```bash
# デフォルト: OpenAI (gpt-4oなど)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (Geminiなど)
# gcloud auth application-default login を実行するか、GOOGLE_APPLICATION_CREDENTIALSを設定する
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (haiku, opus, sonnetなど)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

#### 2. ailingoのインストール:

```bash
pip install ailingo
# VertexAI(Geminiなど)を使う場合
pip install 'ailingo[google]'
# AWS(Bedrock)を使う場合
pip install 'ailingo[aws]'
# または、全ての依存をインストール
pip install 'ailingo[all]'
```

## 使い方

### 基本的な翻訳:

```bash
ailingo <ファイルパス> --target <翻訳先言語>
```

### 例:

```bash
ailingo my_document.txt --target ja
```

これは `my_document.txt` を日本語に翻訳し、`my_document.ja.txt` として保存します。デフォルトでは、同じフォルダ内に`{stem}.{target}{suffix}` 形式で保存されます。

### 翻訳元言語指定によるファイル名推定:

```bash
ailingo /path/to/en/my_document.txt --source en --target ja
```

これは `my_document.txt` を日本語に翻訳し、 `/path/to/ja/my_document.txt` として保存します。この機能は、ファイル名やディレクトリ名に翻訳元言語コードが含まれている場合、それを翻訳先言語コードに置き換えます。

- 例: `document.en.txt` → `document.ja.txt`
- 例: `locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

注意: `--output` オプションで出力先ファイル名のパターンを指定した場合、この自動推定は適用されません。

### 複数のファイルと翻訳先言語:

```bash
ailingo file1.txt file2.html --target ja,es,fr
```

これは `file1.txt` と `file2.html` を日本語、スペイン語、フランス語に翻訳します。

### 追加の翻訳リクエストの指定:

```bash
ailingo my_document.txt --target de --request "間にジョークを交えながら、なるべく砕けた表現にしてください"
```

これは `my_document.txt` をドイツ語に翻訳する際に、ジョークを交えた砕けた表現にするようにリクエストします。

### リライトモード: 同じ言語で文体を修正

```bash
ailingo my_document.txt
```

翻訳先言語を指定しない場合、既存の `my_document.txt` を同じ言語でリライトします。他のオプションは、翻訳時と同様に指定できます。

デフォルトでは、スペルミスや文法ミスを修正しますが、 `--request` オプションを使用して、より具体的なリクエストを追加することも可能です。

### エディターモード: ファイルを指定せずに翻訳

```bash
ailingo -e
```

エディターモードでは、一時ファイルをエディタ（デフォルトはvi）で開き、手動で編集してから翻訳を実行できます。編集後、保存された内容が翻訳に使用されます。

その他のオプションも組み合わせて使用できます。

- `--target` で翻訳先の言語を指定できます。
- `--request` で文体の修正リクエストを追加できます。
- デフォルトでは翻訳結果は標準出力に表示されますが、 `--output` で出力先ファイルを指定できます。

 
### URL モード: Webページを翻訳

```bash
ailingo -u <URL> --target <翻訳先言語>
```

URL モードでは、指定したURLのWebページのテキストコンテンツを抽出、翻訳し、Markdown形式で出力します。

その他のオプションも組み合わせて使用できます。

### 生成AIモデルの指定:

```bash
ailingo my_document.txt --target de --model gemini-1.5-pro
```

これは `my_document.txt` をGoogle Gemini Proを使用してドイツ語に翻訳します。

### 出力ファイル名のカスタマイズ:

```bash
ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

これは `my_document.txt` をスペイン語に翻訳し、`my_document_translated.es.txt` として保存します。

```bash
ailingo /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

これは `path/to/en/my_document.txt` を日本語に翻訳し、`path/to/ja/my_document.txt` として保存します。

`--output` に指定した文字列は[format関数](https://docs.python.org/3.11/tutorial/inputoutput.html)で解釈されます。以下の変数が利用できます。

| 変数名     | 値                                                     | 型           | 例                        |
|------------|-------------------------------------------------------|--------------|-----------------------------|
| `{stem}`    | 入力ファイルの拡張子を除いた部分                         | str       | `my_document`               |
| `{suffix}`  | 入力ファイルの拡張子(ドットを含む)                      | str         | `.txt`                      |
| `{suffixes}`  | 入力ファイルの拡張子のリスト(ドットを含む)             | list[str]  | `['.ja', '.txt']`           |
| `{name}`    | 入力ファイルの拡張子を含むファイル名                     | str         | `my_document.txt`           |
| `{parent}`  | 入力ファイルの親ディレクトリ                           | str         | `/path/to`                 |
| `{parents}` | 入力ファイルの親ディレクトリのリスト                  | list[str]  | `['/path/to', '/path']`      |
| `{target}` | 翻訳先の言語                                           | str         | `ja`                        |
| `{source}` | 翻訳元の言語(指定した場合のみ)                      | Optional[str] | `en`                        |

その他の変数については[Pathlib](https://docs.python.org/3/library/pathlib.html#methods-and-properties)のドキュメントを参照してください。

### 詳細なオプション:

より高度な使用方法については、ヘルプコマンドを使用してください。

```bash
ailingo --help
```

## ライセンス

このプロジェクトは、MITライセンスの下で配布されています。

## 免責事項

このツールは生成AIを利用していますが、翻訳の品質は選択したAIモデルや入力テキストによって異なります。 翻訳結果をレビューし、必要に応じて修正することをお勧めします。
