rm ./example/README-joke.*.md
ailingo README.md -m gemini-1.5-pro -t en,ja -o '{parent}/example/{stem}-joke.{target}{suffix}' -y -r "Please use as casual language as possible. Please use rude language and emojis. Throw in an unrelated joke from time to time. Familiarity is important, so it doesn't necessarily have to be an accurate translation."

rm ./example/i18n.*.yaml
ailingo ./example/i18n.yaml -m gemini-1.5-pro -t es,ja -o '{parent}/{stem}.{target}{suffix}' -y

rm ./example/i18n.*.toml
ailingo ./example/i18n.yaml -m gemini-1.5-pro -t en,ja -o '{parent}/{stem}.{target}.toml' -y -r "Translate and convert to TOML format. Here is an example of the output format:
[ja.login]
title = "ログイン"
username = "ユーザー名"
password = "パスワード"
button = "ログイン"
forgot_password = "パスワードを忘れましたか？"
"

rm ./example/bad-text.*-correct.md
ailingo ./example/bad-text.ja.md ./example/bad-text.en.md -m gemini-1.5-pro -o '{parent}/{stem}-correct{suffix}' -s ja -y -r "なるべく丁寧かつ客観的に"
