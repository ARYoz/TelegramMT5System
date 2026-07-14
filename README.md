# Telegram → MT5 Signal System

מערכת לקבלת סיגנלים מ-Telegram, פתיחת עסקאות ב-MT5, ניהול מחזור חיים, Recovery ודוחות.

> **MT5 הוא מקור האמת.**

ראה [SYSTEM_PHILOSOPHY.md](SYSTEM_PHILOSOPHY.md) — מסמך הפילוסופיה לכל צ'אט/מפתח חדש.

## מבנה (מתוכנן)

```
fast-path/      ← Listener, Parser, Builder, Order Engine
smart-path/     ← Workers, Supervisor, Analytics, Reports
recovery/       ← שחזור מ-MT5
config/         ← קבוצות Telegram + אסטרטגיות
```

## קבוצות Telegram

9 קבוצות — רשימה מלאה ב-[config/groups.json](config/groups.json).

## סטטוס

| רכיב | סטטוס |
|------|--------|
| פילוסופיה + ארכיטקטורה | ✅ מתועד |
| Fast Path | 🔲 לא מומש |
| Smart Path | 🔲 לא מומש |
| Recovery | 🔲 לא מומש |

## Repo נפרד

פרויקט זה **נפרד** מ-[VolatilityGridBot](https://github.com/ARYoz/VolatilityGridBot) (EA לגריד תנודתיות בזהב).
