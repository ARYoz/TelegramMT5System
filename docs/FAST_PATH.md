# Fast Path — Python

## זרימה

```
Telegram → Listener → Parser → Builder → Order Engine → MT5
                              ↓
                    Smart Path (async, אחרי שליחה)
```

## חוקים

- **אין** Analytics / Recovery / Reports בנתיב הקריטי
- כל המדידות נאספות ב-`FastPathResult.timings` — Smart Path ירחיב later
- `enqueue_after_send()` רץ ב-background task בלבד

## Parser חדש

1. צור `fast_path/parsers/my_strategy.py`
2. הירשם ב-`default_registry()` ב-`fast_path/parser.py`
3. הגדר `"strategy": "my_strategy"` ב-`config/groups.json`

## דוגמת parser (example)

הודעה:
```
BUY XAUUSD 0.01 SL 2300 TP 2350
```

## Env

| משתנה | תיאור |
|--------|--------|
| `TELEGRAM_API_ID` | מ-my.telegram.org |
| `TELEGRAM_API_HASH` | מ-my.telegram.org |
| `TELEGRAM_SESSION` | שם session file |
| `MT5_PATH` | נתיב ל-terminal64.exe (אופציונלי) |
| `MT5_MAGIC` | Magic number לפקודות |
| `GROUPS_CONFIG` | נתיב ל-groups.json |
