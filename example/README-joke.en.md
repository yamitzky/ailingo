This fancy CLI tool uses AI magic to translate your files into a bunch of languages.  It's like having a personal translator on your computer but without the annoying small talk.

**Here's the deal:**

* **Handles files like a boss:**  Translate one or a gazillion files at once. You do you. 
* **Speaks your language (well, almost):**  Tons of languages to choose from. No, seriously, a ton. 
* **AI brainpower:** Pick your favorite AI model from ChatGPT, Gemini, Anthropic, or others. It's like choosing your champion in a fighting game. 
* **Output your way:** You're the boss - decide where those translated files go and what they're called. 
* **Get specific:** Want your translation to sound casual? Throw in some jokes? Just ask!
* **Rewrite like a pro:** Fix those embarrassing typos and grammar mistakes or give your writing style a makeover. 

**Wanna install this bad boy? Here's how:**

* **Step 1: Get your AI game on with LiteLLM:**  
    - This program uses LiteLLM to connect with AI models. Grab an API key from your favorite AI provider. It's like getting a backstage pass to the AI party!
    - Need help setting up LiteLLM? Check out their [documentation](https://docs.litellm.ai/docs/providers). Don't worry, it's not as scary as it sounds. 

* **Step 2: Time to install ailingo:**
    - Open your terminal and type this magic spell:

        ```bash
        pip install ailingo
        ```
    - Want to use Google Gemini? Type this instead:

        ```bash
        pip install 'ailingo[google]'
        ```
    - Feeling adventurous with AWS (Bedrock)? Use this one:

        ```bash
        pip install 'ailingo[aws]'
        ```
    - Can't decide and want it all? We got you:

        ```bash
        pip install 'ailingo[all]'
        ```

**Now for the fun part - using this thing!**

* **Basic translation - keep it simple:**

    ```bash
    ailingo <file_path> --target <target_language>
    ```
    **Example:**
    ```bash
    ailingo my_document.txt --target ja
    ```
    This will magically translate your "my_document.txt" file into Japanese and save it as "my_document.ja.txt".  Easy peasy! 

* **Translate multiple files and languages like a pro:**

    ```bash
    ailingo file1.txt file2.html --target ja,es,fr
    ```
    This translates "file1.txt" and "file2.html" into Japanese, Spanish, and French. Show off those language skills!

* **Want your translation to sound like you? No problem!**

    ```bash
    ailingo my_document.txt --target de --request "Please translate with a casual tone, including jokes."
    ```
   This translates "my_document.txt" into German, but with a casual vibe and maybe even a dad joke or two.  

* **Fix those typos and spice up your writing:**
    ```bash
    ailingo my_document.txt 
    ```
    This will magically fix any grammar errors and make your writing shine. It's like having a personal editor, but without the judgmental stares. 

* **Feeling powerful? Customize those output file names:**

    ```bash
    ailingo my_document.txt --target es --output "{parent}/{stem}_translated.{target}{suffix}"
    ```
    This translates "my_document.txt" into Spanish and saves it as "my_document_translated.es.txt" because you're all about that organization.

**Need more options? We got you:**

Type this in your terminal and unleash the full potential of this tool:

    ```bash
    ailingo --help
    ```

**Important Stuff:**

This tool uses AI, which is cool and all, but it's not perfect (like that one friend who always forgets your birthday 🙄).  Double-check the translations just in case.  

**Oh, and one more thing:**

Why don't scientists trust atoms? Because they make up everything! 😂 Okay, back to business. This project is licensed under the MIT License, which means you can pretty much do whatever you want with it. Just don't blame us if your computer starts speaking Klingon. 
