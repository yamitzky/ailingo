## transpa: A CLI Tool for Local File Translation Using Generative AI

**transpa** is a command-line interface (CLI) tool that utilizes the power of generative AI to translate local files into various languages.

### Overview

This tool is designed to help developers, translators, and content creators efficiently localize their files into multiple languages. 

**Key Features:**

- **Flexible file handling:** Translate multiple files at once.
- **Wide language support:** Freely specify the source and target languages for translation.
- **Generative AI model selection:** Choose from various generative AI models available through litellm, such as ChatGPT, Gemini, and Anthropic.
- **Customizable output:** Control the name and location of the translated files.
- **Additional translation requests**: You can add requests for nuances in translation, such as a casual tone.
- **Rewrite mode**: You can rewrite the text in the same language with spell/grammar correction or adjust the writing style with a request.
- **Editor mode**: You can translate text directly in an editor.

### Installation

**Prerequisites:**

- Python 3.11

**Steps:**

1. **Setting up litellm:**

This program utilizes LiteLLM to access generative AI. LiteLLM is designed to work with various providers. Create an account with your preferred generative AI model provider and obtain an API key. 

For detailed setup instructions, please refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/providers). Below are some common API key settings:

```bash
# Default: OpenAI (e.g., gpt-4)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (e.g., Gemini)
# Run "gcloud auth application-default login" or set GOOGLE_APPLICATION_CREDENTIALS
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (e.g., haiku, opus, sonnet)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

2. **Installing transpa:**

```bash
pip install transpa
# To use VertexAI (e.g., Gemini)
pip install 'transpa[google]'
# To use AWS (Bedrock)
pip install 'transpa[aws]'
# Or install all dependencies
pip install 'transpa[all]'
```

### Usage

**Basic translation:**

```bash
transpa <file_path> --target <target_language>
```

**Example:**

```bash
transpa my_document.txt --target ja
```

This translates `my_document.txt` into Japanese and saves it as `my_document.ja.txt`. By default, it saves the translated file in the same folder in the format `{stem}.{target}{suffix}`.

**Filename estimation by specifying the source language:**

```bash
transpa /path/to/en/my_document.txt --source en --target ja
```

This translates `my_document.txt` into Japanese and saves it as `/path/to/ja/my_document.txt`. This feature replaces the source language code with the target language code when the file name or directory name contains the source language code.

- Example: `document.en.txt` → `document.ja.txt`
- Example: `locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

Note: If you specify the output file name pattern with the `--output` option, this automatic estimation will not be applied.

**Multiple files and target languages:**

```bash
transpa file1.txt file2.html --target ja,es,fr
```

This translates `file1.txt` and `file2.html` into Japanese, Spanish, and French.

**Adding a translation request:**

```bash
transpa my_document.txt --target de --request "Please translate with a casual tone, including jokes."
```

This translates `my_document.txt` into German with a casual tone, including jokes.

**Rewrite mode: Correcting spelling/grammar or adjusting writing style**

```bash
transpa my_document.txt 
```

If you don't specify the target language, it will rewrite the existing `my_document.txt` in the same language. You can specify other options in the same way as for translation.

By default, it will correct spelling and grammar errors, but you can add more specific requests using the `--request` option.

**Editor mode: Translate without specifying a file**

```bash
transpa -e
```

In editor mode, a temporary file is opened in an editor (default: vi), allowing you to manually edit the text before translation. After saving, the content will be translated.

You can combine other options with editor mode.

- Specify the target language with `--target`.
- Add a request for adjusting writing style with `--request`.
- By default, the translation result is printed to standard output, but you can specify an output file with `--output`.

**Specifying the generative AI model:**

```bash
transpa my_document.txt --target de --model gemini-1.5-pro
```

This translates `my_document.txt` into German using Google Gemini Pro.

**Customizing the output file name:**

```bash
transpa my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

This translates `my_document.txt` into Spanish and saves it as `my_document_translated.es.txt`.

```bash
transpa /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

This translates `path/to/en/my_document.txt` into Japanese and saves it as `path/to/ja/my_document.txt`.

The string is interpreted by the [format function](https://docs.python.org/3.11/tutorial/inputoutput.html). The following variables are available:

| Variable name | Value                                                        | Type        | Example                      |
|--------------|--------------------------------------------------------------|-------------|------------------------------|
| `{stem}`     | Part of the input file name excluding the extension          | str        | `my_document`                |
| `{suffix}`   | Extension of the input file (including the dot)              | str        | `.txt`                       |
| `{suffixes}` | List of extensions of the input file (including the dot)    | list[str] | `[ '.ja', '.txt' ]`      |
| `{name}`     | File name of the input file including the extension         | str        | `my_document.txt`            |
| `{parent}`   | Parent directory of the input file                            | str        | `/path/to/en`                  |
| `{parents}`  | List of parent directories of the input file                 | list[str] | `['/path/to', '/path']`      |
| `{target}`   | Target language                                               | str        | `ja`                         |
| `{source}`   | Source language (only if specified)                         | Optional[str] | `en`                         |

For other properties, please refer to the [Pathlib documentation](https://docs.python.org/3/library/pathlib.html#methods-and-properties).

**Detailed options:**

For more advanced usage, please use the help command:

```bash
transpa --help
```

### License

This project is distributed under the MIT License.

### Disclaimer

This tool leverages the power of generative AI, but the quality of the translation may vary depending on the selected AI model and the input text. It is recommended to review and revise the translation results as needed. 
