# Telegram → MT5 Signal System

מערכת לקבלת סיגנלים מ-Telegram, פתיחת עסקאות ב-MT5, ניהול מחזור חיים, Recovery ודוחות.

> **MT5 הוא מקור האמת.**

- [SYSTEM_PHILOSOPHY.md](SYSTEM_PHILOSOPHY.md) — פילוסופיה לכל צ'אט חדש
- [docs/FAST_PATH.md](docs/FAST_PATH.md) — הפעלת Fast Path

## מבנה

```
fast_path/          ← ⚡ Listener → Parser → Builder → Order Engine → MT5
smart_path/         ← 🧠 אחרי שליחה (בפיתוח)
recovery/           ← 🔄 שחזור מ-MT5 (בפיתוח)
config/groups.json  ← 9 קבוצות Telegram + strategy mapping
main.py             ← נקודת כניסה
```

## התקנה מהירה (Python)

```bash
git clone https://github.com/ARYoz/TelegramMT5System.git
cd TelegramMT5System
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # מלא API ID / Hash
```

**דרישות:** MT5 פתוח על אותו VPS + AutoTrading מופעל.

```bash
python main.py
```

## הגדרת קבוצה

ב-`config/groups.json` לכל קבוצה:

```json
{
  "chat_id": -1001784375097,
  "provider": "gold_signals",
  "strategy": "example",
  "strategy_version": "1.0",
  "enabled": true
}
```

`strategy` חייב להתאים ל-parser רשום (כרגע: `example`).

## סטטוס

| רכיב | סטטוס |
|------|--------|
| פילוסופיה + ארכיטקטורה | ✅ |
| Fast Path (Python) | ✅ scaffold |
| Smart Path | 🔲 hook בלבד |
| Recovery | 🔲 |

## Repo נפרד

נפרד מ-[VolatilityGridBot](https://github.com/ARYoz/VolatilityGridBot).
