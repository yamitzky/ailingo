

# ailingo：使用生成式 AI (LLM) 的本地文件翻译 CLI 工具

**ailingo** 是一款使用生成式 AI 将本地文件翻译成各种语言的命令行界面 (CLI) 工具。

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
  <a href="./README.es.md">Español</a> |
</p>

NOTICE: 本文档是使用ailingo自动生成的。

## 概述

专为开发人员、翻译人员和内容创作者设计，可帮助他们高效地将文件翻译成多种语言。

**主要功能：**

- **灵活的文件处理：** 可以一次翻译多个文件。
- **广泛的语言支持：** 可以自由指定源语言和目标语言。
- **生成式 AI 模型选择：** 可以从 ChatGPT、Gemini、Anthropic 等多种可用的生成式 AI 模型中选择（通过 litellm）。
- **可自定义的输出：** 可以控制已翻译文件的文件名和保存位置。
- **翻译请求的附加：** 可以添加关于翻译细微差别的请求，例如使用非正式的语气。
- **重写模式：** 可以通过执行拼写/语法检查来重写相同语言的文本，或者根据请求调整文体。
- **编辑器模式：** 可以直接在编辑器中翻译文本。

## 安装

### 先决条件：

- Python 3.11

## 快速入门：

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
pip install ailingo
ailingo my_document.txt --target ja
```

### 详细的安装步骤：

#### 1. 设置 litellm：

此程序使用 LiteLLM 来访问生成式 AI。LiteLLM 旨在与各种提供商合作。请在您要使用的生成式 AI 模型的提供商处创建一个帐户并获取 API 密钥。

有关详细的设置，请参阅 [LiteLLM](https://docs.litellm.ai/docs/providers) 文档。以下是一些设置常见 API 密钥的示例：

```bash
# 默认：OpenAI (gpt-4o 等)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (Gemini 等)
# 运行 gcloud auth application-default login 或设置 GOOGLE_APPLICATION_CREDENTIALS
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (haiku, opus, sonnet 等)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

#### 2. 安装 ailingo：

```bash
pip install ailingo
# 如果使用 VertexAI (Gemini 等)
pip install 'ailingo[google]'
# 如果使用 AWS (Bedrock)
pip install 'ailingo[aws]'
# 或者安装所有依赖项
pip install 'ailingo[all]'
```

## 使用方法

### 基本翻译：

```bash
ailingo <文件路径> --target <目标语言>
```

### 示例：

```bash
ailingo my_document.txt --target ja
```

这会将 `my_document.txt` 翻译成日语，并将其保存为 `my_document.ja.txt`。默认情况下，文件将以 `{stem}.{target}{suffix}` 的格式保存在同一文件夹中。

### 通过指定源语言来推断文件名：

```bash
ailingo /path/to/en/my_document.txt --source en --target ja
```

这会将 `my_document.txt` 翻译成日语，并将其保存为 `/path/to/ja/my_document.txt`。如果文件名或目录名中包含源语言代码，此功能会将其替换为目标语言代码。

- 示例：`document.en.txt` → `document.ja.txt`
- 示例：`locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

注意：如果使用 `--output` 选项指定了输出文件名的模式，则不会应用此自动推断。

### 多个文件和目标语言：

```bash
ailingo file1.txt file2.html --target ja,es,fr
```

这会将 `file1.txt` 和 `file2.html` 翻译成日语、西班牙语和法语。

### 指定其他翻译请求：

```bash
ailingo my_document.txt --target de --request "请尽可能使用非正式的表达方式，并穿插一些笑话。"
```

这会在将 `my_document.txt` 翻译成德语时，请求使用非正式的表达方式并穿插一些笑话。

### 重写模式：以相同语言修改文体

```bash
ailingo my_document.txt
```

如果不指定目标语言，则会以相同语言重写现有的 `my_document.txt`。其他选项可以像翻译时一样指定。

默认情况下，此模式会修正拼写错误和语法错误，但您也可以使用 `--request` 选项添加更具体的请求。

### 编辑器模式：无需指定文件即可进行翻译

```bash
ailingo -e
```

在编辑器模式下，可以使用编辑器（默认情况下为 vi）打开一个临时文件，手动编辑后执行翻译。编辑后的内容将用于翻译。

您也可以结合使用其他选项。

- 可以使用 `--target` 指定目标语言。
- 可以使用 `--request` 添加文体修改请求。
- 默认情况下，翻译结果会显示在标准输出中，但您可以使用 `--output` 指定输出文件。

### 指定生成式 AI 模型：

```bash
ailingo my_document.txt --target de --model gemini-1.5-pro
```

这会使用 Google Gemini Pro 将 `my_document.txt` 翻译成德语。

### 自定义输出文件名：

```bash
ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

这会将 `my_document.txt` 翻译成西班牙语，并将其保存为 `my_document_translated.es.txt`。

```bash
ailingo /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

这会将 `path/to/en/my_document.txt` 翻译成日语，并将其保存为 `path/to/ja/my_document.txt`。

指定给 `--output` 的字符串将由 [format 函数](https://docs.python.org/3.11/tutorial/inputoutput.html) 解释。可以使用以下变量：

| 变量名       | 值                                                       | 类型           | 示例                        |
|------------|---------------------------------------------------------|--------------|-----------------------------|
| `{stem}`    | 输入文件不带扩展名的部分                                   | str       | `my_document`               |
| `{suffix}`  | 输入文件的扩展名（包括点号）                              | str         | `.txt`                      |
| `{suffixes}`  | 输入文件扩展名的列表（包括点号）                           | list[str]  | `['.ja', '.txt']`           |
| `{name}`    | 包含扩展名的输入文件名                                     | str         | `my_document.txt`           |
| `{parent}`  | 输入文件的父目录                                           | str         | `/path/to`                 |
| `{parents}` | 输入文件的父目录列表                                       | list[str]  | `['/path/to', '/path']`      |
| `{target}` | 目标语言                                                   | str         | `ja`                        |
| `{source}` | 源语言（如果已指定）                                     | Optional[str] | `en`                        |

有关其他变量，请参阅 [Pathlib](https://docs.python.org/3/library/pathlib.html#methods-and-properties) 文档。

### 详细选项：

有关更高级的用法，请使用帮助命令。

```bash
ailingo --help
```

## 许可证

此项目在 MIT 许可证下分发。

## 免责声明

此工具使用生成式 AI，但翻译质量取决于所选的 AI 模型和输入文本。建议您检查翻译结果并在必要时进行修改。
