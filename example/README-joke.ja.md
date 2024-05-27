おいおい、ファイル翻訳してくれるってマジ？ 🎉  ファイル投げるから、頑張って翻訳してくれよな！😤

**transpa** は、AIの力を借りて、ローカルのファイルを色んな言語に翻訳してくれるコマンドラインツールだぜ。

### なにがすごいの？

開発者、翻訳者、コンテンツクリエイターが、ファイルを複数の言語に簡単にローカライズできるように作られたんだ。

**主な機能:**

- **ファイル対応力抜群:** 一度に複数のファイルを翻訳できる。
- **言語サポートも充実:** 翻訳元の言語と翻訳先の言語を自由に指定できる。
- **AIモデルも選び放題:** ChatGPT、Gemini、Anthropicなど、litellmで使える様々な生成AIモデルから選択可能。
- **出力も自由自在:** 翻訳後のファイルの名前や保存場所を自由に設定できる。
- **翻訳のリクエストもOK:** カジュアルなトーンにしたいとか、細かい翻訳のニュアンスも指定できる。
- **リライトモード搭載:** スペルや文法を修正したり、リクエストに応じて文体を調整したり、同じ言語でテキストを書き直すこともできる。

### インストール

**必要なもの:**

- Python 3.11

**手順:**

1. **litellmの設定:**

このプログラムは、LiteLLMを使って生成AIにアクセスするんだ。 LiteLLMは様々なプロバイダーで動作するように設計されてる。 使いたい生成AIモデルのプロバイダーのアカウントを作成して、APIキーを取得してくれ。

詳しい設定手順は、[LiteLLMのドキュメント](https://docs.litellm.ai/docs/providers)を参照してくれ。 よくあるAPIキーの設定は次のとおりだ。

```bash
# デフォルト: OpenAI (例: gpt-4)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (例: Gemini)
# "gcloud auth application-default login"を実行するか、GOOGLE_APPLICATION_CREDENTIALSを設定する
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (例: haiku, opus, sonnet)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

2. **transpaのインストール:**

```bash
pip install transpa
# VertexAI (例: Gemini)を使う場合
pip install 'transpa[google]'
# AWS (Bedrock)を使う場合
pip install 'transpa[aws]'
# すべての依存関係をインストールする場合
pip install 'transpa[all]'
```

### 使い方

**基本的な翻訳:**

```bash
transpa <file_path> --target <target_language>
```

**例:**

```bash
transpa my_document.txt --target ja
```

これは`my_document.txt`を日本語に翻訳し、`my_document.ja.txt`というファイル名で保存する。 デフォルトでは、翻訳後のファイルは同じフォルダに`{stem}.{target}{suffix}`という形式のファイル名で保存される。

**ソース言語を指定してファイル名を推測:**

```bash
transpa /path/to/en/my_document.txt --source en --target ja
```

これは`my_document.txt`を日本語に翻訳し、`/path/to/ja/my_document.txt`というファイル名で保存する。 この機能は、ファイル名またはディレクトリ名にソース言語コードが含まれている場合、ソース言語コードをターゲット言語コードに置き換えるんだ。

- 例: `document.en.txt` → `document.ja.txt`
- 例: `locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

注意: `--output`オプションで出力ファイル名のパターンを指定した場合は、この自動推測は適用されないから気をつけろよ。

**複数のファイルとターゲット言語:**

```bash
transpa file1.txt file2.html --target ja,es,fr
```

これは`file1.txt`と`file2.html`を日本語、スペイン語、フランス語に翻訳する。

**翻訳のリクエストを追加:**

```bash
transpa my_document.txt --target de --request "冗談を交えてカジュアルな口調で翻訳してください。"
```

これは`my_document.txt`をドイツ語に翻訳するんだけど、冗談を交えつつ、カジュアルな口調で翻訳してくれる。

**リライトモード: スペル/文法の修正または文体の調整**

```bash
transpa my_document.txt 
```

ターゲット言語を指定しないと、既存の`my_document.txt`を同じ言語で書き直してくれる。 翻訳の場合と同じように、他のオプションも指定できる。

デフォルトでは、スペルや文法の間違いを修正してくれるけど、`--request`オプションを使えば、もっと具体的なリクエストを追加することもできる。

**生成AIモデルの指定:**

```bash
transpa my_document.txt --target de --model gemini-1.5-pro
```

これはGoogle Gemini Proを使って`my_document.txt`をドイツ語に翻訳する。

**出力ファイル名のカスタマイズ:**

```bash
transpa my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

これは`my_document.txt`をスペイン語に翻訳し、`my_document_translated.es.txt`というファイル名で保存する。

```bash
transpa /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

これは`path/to/en/my_document.txt`を日本語に翻訳し、`path/to/ja/my_document.txt`というファイル名で保存する。

文字列は[format関数](https://docs.python.org/3.11/tutorial/inputoutput.html)で解釈される。 次のような変数が使えるぞ。

| 変数名       | 値                                                          | タイプ        | 例                      |
|--------------|----------------------------------------------------------------|-------------|------------------------------|
| `{stem}`     | 拡張子を除いた入力ファイル名の一部                         | str        | `my_document`                |
| `{suffix}`   | 入力ファイルの拡張子（ドットを含む）                      | str        | `.txt`                       |
| `{suffixes}` | 入力ファイルの拡張子のリスト（ドットを含む）                 | list[str] | `[ '.ja', '.txt' ]`      |
| `{name}`     | 拡張子を含む入力ファイルのファイル名                        | str        | `my_document.txt`            |
| `{parent}`   | 入力ファイルの親ディレクトリ                             | str        | `/path/to/en`                  |
| `{parents}`  | 入力ファイルの親ディレクトリのリスト                        | list[str] | `['/path/to', '/path']`      |
| `{target}`   | ターゲット言語                                              | str        | `ja`                         |
| `{source}`   | ソース言語（指定されている場合のみ）                        | Optional[str] | `en`                         |

その他のプロパティについては、[Pathlibのドキュメント](https://docs.python.org/3/library/pathlib.html#methods-and-properties)を参照してくれ。

**詳細なオプション:**

もっと使いこなしたい場合は、ヘルプコマンドを使ってみてくれ。

```bash
transpa --help
```

### ライセンス

このプロジェクトはMITライセンスで配布されているぜ。

### 免責事項

このツールは生成AIの力を借りているけど、翻訳の品質は選択したAIモデルや入力テキストによって異なる場合がある。 翻訳結果については、必要に応じて確認と修正を行うことをお勧めするぜ。
