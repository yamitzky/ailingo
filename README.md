# ailingo: A CLI tool for translating local files using generative AI (LLM)

**ailingo** is a command-line interface (CLI) tool that uses generative AI to translate local files into various languages.

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

<p align="center">
    <img alt="example" src="https://github.com/yamitzky/ailingo/assets/623449/faae1265-9ab6-4df5-a787-23e73fff9778">
</p>

NOTICE: This document was automatically generated using ailingo.

## Overview

It is designed to enable developers, translators, and content creators to efficiently localize their files.

**Key Features:**

- **Flexible file handling:** Translate multiple files at once.
- **Wide language support:** Freely specify the source and target languages.
- **Generative AI model selection:** Choose from various generative AI models available through litellm, including ChatGPT, Gemini, and Anthropic.
- **Customizable output:** Control the names and save locations of translated files.
- **Adding translation requests**: Add requests for nuances in translation, such as casual tone.
- **Rewrite mode**: Rewrite text in the same language with spelling/grammar correction or adjust the writing style as requested.
- **Editor mode**: Translate text directly in an editor.

## Installation

### Prerequisites:

- Python 3.11

## Quick Start:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
pip install ailingo
ailingo my_document.txt --target ja
```

### Detailed setup procedure:

#### 1. Setting up litellm:

This program uses LiteLLM to access generative AI. LiteLLM is designed to work with a variety of providers. Please create an account with the provider of the generative AI model you wish to use, and obtain an API key.

Please refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/providers) for detailed setup instructions. Here are some examples of setting up typical API keys:

```bash
# Default: OpenAI (gpt-4o, etc.)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (Gemini, etc.)
# Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (haiku, opus, sonnet, etc.)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

#### 2. Installing ailingo:

```bash
pip install ailingo
# If you want to use VertexAI (Gemini etc.)
pip install 'ailingo[google]'
# If you want to use AWS (Bedrock)
pip install 'ailingo[aws]'
# Or install all dependencies
pip install 'ailingo[all]'
```

## Usage

### Basic translation:

```bash
ailingo <file path> --target <target language>
```

### Example:

```bash
ailingo my_document.txt --target ja
```

This will translate `my_document.txt` into Japanese and save it as `my_document.ja.txt`. By default, it will be saved in the same folder in the format `{stem}.{target}{suffix}`.

### File name estimation by specifying the source language:

```bash
ailingo /path/to/en/my_document.txt --source en --target ja
```

This will translate `my_document.txt` into Japanese and save it as `/path/to/ja/my_document.txt`. This feature replaces the source language code with the target language code if the file name or directory name contains the source language code.

- Example: `document.en.txt` → `document.ja.txt`
- Example: `locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

Note: This automatic estimation does not apply if you specify an output file name pattern with the `--output` option.

### Multiple files and target languages:

```bash
ailingo file1.txt file2.html --target ja,es,fr
```

This will translate `file1.txt` and `file2.html` into Japanese, Spanish, and French.

### Specifying additional translation requests:

```bash
ailingo my_document.txt --target de --request "Please make it as casual as possible, with some jokes in between."
```

This will request to make the translation of `my_document.txt` into German as casual as possible, with some jokes added.

### Rewrite mode: Modifying the style of the text in the same language

```bash
ailingo my_document.txt
```

If you do not specify a target language, the existing `my_document.txt` will be rewritten in the same language. Other options can be specified in the same way as for translation.

By default, it will correct spelling and grammatical errors, but you can also use the `--request` option to add more specific requests.

### Editor mode: Translate without specifying a file

```bash
ailingo -e
```

In editor mode, a temporary file is opened in an editor (vi by default) for manual editing before translation. After editing, the saved content is used for translation.

Other options can be used in combination:

- The target language can be specified with `--target`.
- Style modification requests can be added with `--request`.
- The translation result is displayed on standard output by default, but an output file can be specified with `--output`.

### Specifying the Generative AI Model:

```bash
ailingo my_document.txt --target de --model gemini-1.5-pro
```

This will translate `my_document.txt` into German using Google Gemini Pro.

### Customizing the output file name:

```bash
ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

This will translate `my_document.txt` into Spanish and save it as `my_document_translated.es.txt`.

```bash
ailingo /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

This will translate `path/to/en/my_document.txt` into Japanese and save it as `path/to/ja/my_document.txt`.

The string specified for `--output` is interpreted by the [format function](https://docs.python.org/3.11/tutorial/inputoutput.html). The following variables are available:

| Variable Name | Value | Type | Example |
|:------------|:----------------------------------------------------------|:--------------|:------------------------------|
| `{stem}` | Part of the input file excluding the extension | `str` | `my_document` |
| `{suffix}` | Extension of the input file (including the dot) | `str` | `.txt` |
| `{suffixes}` | List of extensions of the input file (including the dot) | `list[str]` | `['.ja', '.txt']` |
| `{name}` | File name of the input file including the extension | `str` | `my_document.txt` |
| `{parent}` | Parent directory of the input file | `str` | `/path/to/en` |
| `{parents}` | List of parent directories of the input file | `list[str]` | `['/path/to', '/path']` |
| `{target}` | Target language | `str` | `ja` |
| `{source}` | Source language (only if specified) | `Optional[str]` | `en` |

For other variables, please refer to the [Pathlib documentation](https://docs.python.org/3/library/pathlib.html#methods-and-properties).

### Detailed options:

For more advanced usage, please use the help command:

```bash
ailingo --help
```

## License

This project is distributed under the MIT License.

## Disclaimer

This tool utilizes generative AI, but the quality of the translation depends on the selected AI model and input text. It is recommended to review the translation results and make corrections as needed.
