# ailingo: Una herramienta CLI para traducir archivos locales usando AI generativa (LLM)

**ailingo** es una herramienta de línea de comandos (CLI) que utiliza inteligencia artificial generativa para traducir archivos locales a varios idiomas.

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

NOTICE: Este documento fue generado automáticamente usando ailingo.

## Resumen

Está diseñada para que desarrolladores, traductores y creadores de contenido puedan localizar sus archivos de manera eficiente.

**Características Clave:**

- **Manejo flexible de archivos:** Traduce múltiples archivos a la vez.
- **Amplia compatibilidad de idiomas:** Especifica libremente los idiomas fuente y objetivo.
- **Selección de modelo de AI generativa:** Elige entre varios modelos de AI generativa disponibles a través de litellm, como ChatGPT, Gemini y Anthropic.
- **Salida personalizable:** Controla los nombres y ubicaciones de guardado de los archivos traducidos.
- **Añadir solicitudes de traducción:** Añade solicitudes para matices en la traducción, como un tono casual.
- **Modo de reescritura:** Reescribe el texto en el mismo idioma con corrección ortográfica/gramatical o ajusta el estilo de escritura según lo solicitado.
- **Modo Editor:** Traduce texto directamente en un editor.

## Instalación

### Requisitos Previos:

- Python 3.11

## Inicio Rápido:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
pip install ailingo
ailingo my_document.txt --target ja
```

### Procedimiento detallado de configuración:

#### 1. Configuración de litellm:

Este programa utiliza LiteLLM para acceder a AI generativa. LiteLLM está diseñado para funcionar con una variedad de proveedores. Por favor, crea una cuenta con el proveedor del modelo de AI generativa que deseas usar y obtén una clave API.

Por favor, consulta la [documentación de LiteLLM](https://docs.litellm.ai/docs/providers) para instrucciones detalladas de configuración. Aquí hay algunos ejemplos de cómo configurar claves API típicas:

```bash
# Predeterminado: OpenAI (gpt-4o, etc.)
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# VertexAI (Gemini, etc.)
# Ejecuta `gcloud auth application-default login` o establece `GOOGLE_APPLICATION_CREDENTIALS`
export VERTEXAI_PROJECT="your-google-project-id"
export VERTEXAI_LOCATION="us-central1"

# Anthropic (haiku, opus, sonnet, etc.)
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

#### 2. Instalación de ailingo:

```bash
pip install ailingo
# Si deseas usar VertexAI (Gemini etc.)
pip install 'ailingo[google]'
# Si deseas usar AWS (Bedrock)
pip install 'ailingo[aws]'
# O instala todas las dependencias
pip install 'ailingo[all]'
```

## Uso

### Traducción básica:

```bash
ailingo <ruta del archivo> --target <idioma objetivo>
```

### Ejemplo:

```bash
ailingo my_document.txt --target ja
```

Esto traducirá `my_document.txt` al japonés y lo guardará como `my_document.ja.txt`. Por defecto, se guardará en la misma carpeta en el formato `{stem}.{target}{suffix}`.

### Estimación del nombre del archivo especificando el idioma fuente:

```bash
ailingo /path/to/en/my_document.txt --source en --target ja
```

Esto traducirá `my_document.txt` al japonés y lo guardará como `/path/to/ja/my_document.txt`. Esta característica reemplaza el código del idioma fuente con el código del idioma objetivo si el nombre del archivo o el nombre del directorio contiene el código del idioma fuente.

- Ejemplo: `document.en.txt` → `document.ja.txt`
- Ejemplo: `locales/en/LC_MESSAGES/message.po` → `locales/ja/LC_MESSAGES/message.po`

Nota: Esta estimación automática no se aplica si especificas un patrón de nombre de archivo de salida con la opción `--output`.

### Múltiples archivos e idiomas objetivo:

```bash
ailingo file1.txt file2.html --target ja,es,fr
```

Esto traducirá `file1.txt` y `file2.html` al japonés, español y francés.

### Especificar solicitudes adicionales de traducción:

```bash
ailingo my_document.txt --target de --request "Hazlo lo más casual posible, con algunas bromas intercaladas."
```

Esto solicitará hacer la traducción de `my_document.txt` al alemán lo más casual posible, con algunas bromas añadidas.

### Modo de reescritura: Modificando el estilo del texto en el mismo idioma

```bash
ailingo my_document.txt
```

Si no especificas un idioma objetivo, el existente `my_document.txt` se reescribirá en el mismo idioma. Otras opciones pueden especificarse de la misma manera que para la traducción.

Por defecto, corregirá errores ortográficos y gramaticales, pero también puedes usar la opción `--request` para añadir solicitudes más específicas.

### Modo Editor: Traduce sin especificar un archivo

```bash
ailingo -e
```

En el modo editor, se abre un archivo temporal en un editor (vi por defecto) para la edición manual antes de la traducción. Después de la edición, se usa el contenido guardado para la traducción.

Otras opciones pueden usarse en combinación:

- El idioma objetivo puede especificarse con `--target`.
- Solicitudes de modificación de estilo pueden añadirse con `--request`.
- El resultado de la traducción se muestra en la salida estándar por defecto, pero puede especificarse un archivo de salida con `--output`.

### Especificar el Modelo de AI Generativa:

```bash
ailingo my_document.txt --target de --model gemini-1.5-pro
```

Esto traducirá `my_document.txt` al alemán usando Google Gemini Pro.

### Personalizando el nombre del archivo de salida:

```bash
ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
```

Esto traducirá `my_document.txt` al español y lo guardará como `my_document_translated.es.txt`.

```bash
ailingo /path/to/en/my_document.txt --target ja --output "{parents[1]}/{target}/{name}"
```

Esto traducirá `path/to/en/my_document.txt` al japonés y lo guardará como `path/to/ja/my_document.txt`.

La cadena especificada para `--output` es interpretada por la [función format](https://docs.python.org/3.11/tutorial/inputoutput.html). Las siguientes variables están disponibles:

| Nombre de la Variable | Valor | Tipo | Ejemplo |
|:-----------------|:----------------------------------------------------------|:--------------|:------------------------------|
| `{stem}` | Parte del archivo de entrada excluyendo la extensión | `str` | `my_document` |
| `{suffix}` | Extensión del archivo de entrada (incluyendo el punto) | `str` | `.txt` |
| `{suffixes}` | Lista de extensiones del archivo de entrada (incluyendo el punto) | `list[str]` | `['.ja', '.txt']` |
| `{name}` | Nombre del archivo de entrada incluyendo la extensión | `str` | `my_document.txt` |
| `{parent}` | Directorio principal del archivo de entrada | `str` | `/path/to/en` |
| `{parents}` | Lista de directorios principales del archivo de entrada | `list[str]` | `['/path/to', '/path']` |
| `{target}` | Idioma objetivo | `str` | `ja` |
| `{source}` | Idioma fuente (solo si se especifica) | `Optional[str]` | `en` |

Para otras variables, por favor consulta la [documentación de Pathlib](https://docs.python.org/3/library/pathlib.html#methods-and-properties).

### Opciones detalladas:

Para un uso más avanzado, por favor usa el comando de ayuda:

```bash
ailingo --help
```

## Licencia

Este proyecto se distribuye bajo la Licencia MIT.

## Descargo de responsabilidad

Esta herramienta utiliza AI generativa, pero la calidad de la traducción depende del modelo de AI seleccionado y del texto de entrada. Se recomienda revisar los resultados de la traducción y hacer las correcciones necesarias.
