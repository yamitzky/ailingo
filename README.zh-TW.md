# ailingo：使用生成式 AI (LLM) 的本地檔案翻譯 CLI 工具

**ailingo** 是一款使用生成式 AI 將本地檔案翻譯成各種語言的命令列介面 (CLI) 工具。

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

NOTICE: 本文件是使用 Ailingo 自動生成的。

## 概述

專為開發人員、翻譯人員和內容創作者設計，讓他們能夠有效地將檔案翻譯成多種語言。

**主要功能：**

- **靈活的檔案處理：**可以一次翻譯多個檔案。
- **廣泛的語言支援：**可以自由指定源語言和目標語言。
- **生成式 AI 模型選擇：**可以從 ChatGPT、Gemini、Anthropic 等 litellm 支援的各種生成式 AI 模型中進行選擇。
- **可自訂輸出：**可以控制已翻譯檔案的名稱和儲存位置。
- **翻譯請求附加資訊：**可以附加翻譯的細微差別請求，例如非正式語氣。
- **重寫模式：**可以透過拼寫/語法校正以相同語言重寫文字，或根據請求調整寫作風格。
- **編輯器模式：**可以直接在編輯器中翻譯文字。
- **URL 模式：**可以下載並翻譯網頁內容。

## 安裝

### 先決條件：

- Python 3.11

## 快速入門：

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
pip install ailingo
ailingo my_document.txt --target ja
```

### 詳細設定步驟：

#### 1. 設定 litellm：

此程式使用 LiteLLM 來存取生成式 AI。LiteLLM 設計為與各種供應商合作。請在您要使用的生成式 AI 模型的供應商處建立帳戶並取得 API 金鑰。

如需詳細的設定說明，請參閱 [LiteLLM](https://docs.litellm.ai/docs/providers) 文件。以下是一些設定常見 API 金鑰的範例：

```bash
# 預設：OpenAI (gpt-4o 等)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (Gemini 等)
# 執行 gcloud auth application-default login 或設定 GOOGLE_APPLICATION_CREDENTIALS
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (haiku、opus、sonnet 等)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

#### 2. 安裝 ailingo：

```bash
pip install ailingo
# 使用 VertexAI (Gemini 等) 時
pip install 'ailingo[google]'
# 使用 AWS (Bedrock) 時
pip install 'ailingo[aws]'
# 或安裝所有相依性
pip install 'ailingo[all]'
```

## 用法

### 基本翻譯：

```bash
ailingo <檔案路徑> --target <目標語言>
```

### 範例：

```bash
ailingo my_document.txt --target ja
```

這會將 `my_document.txt` 翻譯成日文，並儲存為 `my_document.ja.txt`。預設情況下，檔案會儲存在相同的資料夾中，格式為 `{stem}.{target}{suffix}`。

### 透過指定源語言來推斷檔名：

```bash
ailingo /path/to/en/my_document.txt --source en --target ja
```

這會將 `my_document.txt` 翻譯成日文，並儲存為 `/path/to/ja/my_document.txt`。如果檔名或目錄名稱包含源語言代碼，此功能會將其替換為目標語言代碼。

- 範例：`document.en.txt` → `document.ja.txt`
- 範例：`locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

注意：如果使用 `--output` 選項指定輸出檔名模式，則不會套用此自動推斷。

### 多個檔案和目標語言：

```bash
ailingo file1.txt file2.html --target ja,es,fr
```

這會將 `file1.txt` 和 `file2.html` 翻譯成日文、西班牙文和法文。

### 指定額外的翻譯請求：

```bash
ailingo my_document.txt --target de --request "請盡可能使用輕鬆的語氣，並加入一些笑話。"
```

這會在將 `my_document.txt` 翻譯成德文時，要求使用輕鬆的語氣並加入一些笑話。

### 重寫模式：以相同語言修改寫作風格

```bash
ailingo my_document.txt
```

如果未指定目標語言，則會以相同語言重寫現有的 `my_document.txt`。其他選項可以像翻譯時一樣指定。

預設情況下，它會修正拼寫錯誤和語法錯誤，但您也可以使用 `--request` 選項新增更具體的請求。

### 編輯器模式：無需指定檔案即可進行翻譯

```bash
ailingo -e
```

在編輯器模式下，會使用編輯器（預設為 vi）開啟暫存檔案，讓您手動編輯，然後執行翻譯。儲存的內容將用於翻譯。

也可以與其他選項組合使用。

- 可以使用 `--target` 指定目標語言。
- 可以使用 `--request` 新增寫作風格修改請求。
- 預設情況下，翻譯結果會顯示在標準輸出中，但您可以使用 `--output` 指定輸出檔案。

### URL 模式：翻譯網頁

```bash
ailingo -u <網址> --target <目標語言>
```

在 URL 模式下，會提取指定網址網頁的文字內容，進行翻譯，並以 Markdown 格式輸出。

也可以與其他選項組合使用。

### 指定生成式 AI 模型：

```bash
ailingo my_document.txt --target de --model gemini-1.5-pro
```

這會使用 Google Gemini Pro 將 `my_document.txt` 翻譯成德文。

###  **--stream** 選項 (實驗性功能)

`--stream` 選項允許您以實時方式觀看翻譯的輸出。此功能仍處於實驗階段，並非所有模型都支援。

```bash
ailingo my_document.txt --target ja --stream
```


### 自訂輸出檔名：

```bash
ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

這會將 `my_document.txt` 翻譯成西班牙文，並儲存為 `my_document_translated.es.txt`。

```bash
ailingo /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

這會將 `path/to/en/my_document.txt` 翻譯成日文，並儲存為 `path/to/ja/my_document.txt`。

`--output` 中指定的字串將由 [format 函式](https://docs.python.org/3.11/tutorial/inputoutput.html) 解讀。可以使用以下變數：

| 變數名稱     | 值                                                     | 類型           | 範例                        |
|------------|-------------------------------------------------------|--------------|-----------------------------|
| `{stem}`    | 輸入檔案不含副檔名的部分                              | str       | `my_document`               |
| `{suffix}`  | 輸入檔案的副檔名（包含點）                          | str         | `.txt`                      |
| `{suffixes}`  | 輸入檔案的副檔名清單（包含點）                      | list[str]  | `['.ja', '.txt']`           |
| `{name}`    | 輸入檔案的名稱（包含副檔名）                        | str         | `my_document.txt`           |
| `{parent}`  | 輸入檔案的父目錄                                       | str         | `/path/to`                 |
| `{parents}` | 輸入檔案的父目錄清單                                 | list[str]  | `['/path/to', '/path']`      |
| `{target}` | 目標語言                                              | str         | `ja`                        |
| `{source}` | 源語言（如果已指定）                                 | Optional[str] | `en`                        |

如需其他變數，請參閱 [Pathlib](https://docs.python.org/3/library/pathlib.html#methods-and-properties) 文件。

### 詳細選項：

如需更進階的用法，請使用說明命令。

```bash
ailingo --help
```

### 授權

本專案以 MIT 授權條款發布。

## 免責聲明

此工具使用生成式 AI，但翻譯品質會因所選的 AI 模型和輸入文字而異。建議您檢閱翻譯結果，並視需要進行修正。
