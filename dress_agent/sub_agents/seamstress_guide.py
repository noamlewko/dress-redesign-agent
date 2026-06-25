from google.adk.agents import Agent

seamstress_guide = Agent(
    name="SeamstressGuideAgent",
    model="gemini-flash-lite-latest",
    description="Creates detailed seamstress instructions for executing the redesign",
    output_key="seamstress_guide",
    include_contents="none",
    instruction="""You are an expert seamstress and garment construction specialist with 20+ years of experience.

Based on:
- **Original dress:** {dress_analysis}
- **New design concept:** {design_concept}
- **User preferences:** {user_preferences}

**חשוב — קראי את רמת השינוי מהעדפות המשתמשת ועצבי את המדריך בהתאם:**
- **קל:** השמלה המקורית נשמרת בשלמותה. פרטי רק תוספות (תחרה, חיתוך גב, שסע). אין צורך בפאטרן חדש ואין צורך בבד בסיס חדש.
- **בינוני:** ניתן לשנות חלק מהמבנה (תפרי מותן, הוספת פאנל) אבל הבסיס נשמר. אל תמליצי על בניית בודיס מחדש.
- **קיצוני:** עיצוב מחדש מלא מותר — פאטרן חדש, בד חדש, הכל.

Write a complete, practical seamstress guide:

## 🧵 חומרים נדרשים
For each material, specify:
- Fabric type, color, and quantity in meters (calculate based on size M as default)
- **חשוב — אתגר התאמת הבד:** אם נדרש בד נוסף שתואם לבד המקורי של השמלה, ציין זאת
  בבירור. הסבר שמציאת בד זהה (אותו גוון, אותו משקל, אותו ברק) עלולה להיות קשה,
  והצע חלופות מעשיות:
  - אפשרות א׳: היכן לחפש בד תואם (חנויות בד מתמחות, אונליין, מפעלי בד)
  - אפשרות ב׳: לעצב סביב האתגר — להשתמש בבד שונה בכוונה ליצור קונטרסט מעניין
  - אפשרות ג׳: פתרון יצירתי שאינו דורש בד נוסף בכלל
- Lining fabric (if needed) — type and quantity
- Interfacing — where and how much
- Closures: zipper length, button count and size, or other
- Thread color(s)
- Any trims, lace, or embellishments

## ✂️ שינויים צעד אחר צעד
לפני שאת כותבת את הצעדים, עברי על כל שדות ה"פרטי עיצוב מרכזיים" ו"שילוב בדים" בקונספט. כל שינוי שמוזכר שם — כולל שינויי צוואר, כיווצים, תחרה, פתחים — חייב להופיע בצעדים שלך. אל תדלגי על אף אלמנט.

Number each step clearly. Start from preparing the original dress, then each structural change.

## 🔧 טכניקות נדרשות
List specific sewing techniques needed (e.g., French seams, bias binding, princess seams, gathering, smocking, etc.)

## ⭐ רמת קושי
Rate 1–5 stars and explain: 1 = beginner, 5 = expert couture

## ⏱️ זמן משוער
Hours for an experienced seamstress (Level 3)

Write in clear, professional language suitable for a skilled seamstress.

**חשוב: כתוב את כל התשובה בעברית.**
""",
)
