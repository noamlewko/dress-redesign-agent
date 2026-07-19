import asyncio
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

# Load .env before importing ADK
def _load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

_load_env()

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from dress_agent.agent import root_agent

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="עיצוב שמלה מחדש", page_icon="👗", layout="centered")

st.markdown("""
<style>
    html, body, [class*="st-"] { direction: rtl; text-align: right; }
    .stButton button { width: 100%; font-size: 1.1rem; padding: 0.6rem; }
</style>
""", unsafe_allow_html=True)

# ── Agent labels for progress display ───────────────────────────────────────
AGENT_STEPS = [
    ("TrendResearchAgent",   "🔍 מחפש טרנדי אופנה עדכניים..."),
    ("DressAnalyzerAgent",   "🔬 מנתח את השמלה..."),
    ("DesignCreatorAgent",   "✏️  יוצר קונספט עיצוב חדש..."),
    ("DesignValidatorAgent", "🔎 בודק ומתקן את העיצוב..."),
    ("ImageGeneratorAgent",  "🎨 מייצר סקיצה..."),
    ("SketchValidatorAgent", "🔍 בודק שהסקיצה מתאימה לעיצוב..."),
    ("SeamstressGuideAgent",    "🧵 כותב מדריך לתופרת..."),
    ("SeamstressValidatorAgent", "✅ מוודא שהמדריך מתאים לעיצוב..."),
]
# ── Hebrew → English translation maps for agent prompts ─────────────────────
STYLE_MAP = {
    "וינטג׳": "vintage", "מודרני": "modern", "קלאסי": "classic",
    "בוהמי": "boho", "מינימליסטי": "minimalist", "גלאם": "glam",
}
OCCASION_MAP = {
    "יומיומי": "casual", "עבודה": "work", "ערב": "evening", "חתונה": "wedding",
}
LENGTH_MAP = {
    "מידי": "midi", "מיני": "mini", "ברך": "knee-length", "מקסי": "maxi",
}
EXPOSURE_MAP = {
    "מינימלי — מכוסה ואלגנטי": "minimal — covered and elegant",
    "בינוני — קצת חשיפה": "moderate — some skin",
    "נועז — אני אוהבת חשוף": "bold — I love skin exposure",
}
ZIPPER_MAP = {
    "לא יודעת": "unknown",
    "גב — מלמעלה למטה": "back — top to bottom",
    "צד שמאל / ימין": "side — left or right",
    "אין רוכסן": "no zipper",
}
CHANGE_MAP = {"קל": "light", "בינוני": "moderate", "קיצוני": "radical"}

# ── UI ───────────────────────────────────────────────────────────────────────
st.title("👗 עיצוב שמלה מחדש")
st.markdown("העלי תמונה של השמלה, מלאי את הטופס — ה-AI יעצב עבורך שמלה חדשה")
st.divider()

# Image upload
uploaded_file = st.file_uploader(
    "📸 תמונה של השמלה",
    type=["jpg", "jpeg", "png", "webp"],
    help="תמונה שלך לובשת את השמלה, מישהי אחרת לובשת אותה, או השמלה מונחת",
)
if uploaded_file:
    st.image(uploaded_file, width=280)

st.divider()
st.subheader("הטופס")

col1, col2 = st.columns(2)

with col1:
    style = st.selectbox("סגנון", ["וינטג׳", "מודרני", "קלאסי", "בוהמי", "מינימליסטי", "גלאם"])
    occasion = st.selectbox("אירוע", ["יומיומי", "עבודה", "ערב", "חתונה"])
    length = st.selectbox("אורך רצוי", ["מידי", "מיני", "ברך", "מקסי"])

with col2:
    age = st.number_input("גיל", min_value=16, max_value=80, value=28, step=1)
    change_level = st.radio(
        "רמת שינוי",
        ["קל — שמרי על הבסיס", "בינוני", "קיצוני — השראה בלבד"],
    )

exposure = st.radio(
    "חשיפת עור",
    ["מינימלי — מכוסה ואלגנטי", "בינוני — קצת חשיפה", "נועז — אני אוהבת חשוף"],
    horizontal=True,
)

zipper_location = st.selectbox(
    "מיקום רוכסן",
    ["לא יודעת", "גב — מלמעלה למטה", "צד שמאל / ימין", "אין רוכסן"],
)

color_choice = st.radio("צבע", ["שמרי את הצבע המקורי", "שני את הצבע"])
color_input = ""
if color_choice == "שני את הצבע":
    color_input = st.text_input("לאיזה צבע?", placeholder="לבן, אדום בורדו, שחור...")

st.divider()

ready = bool(uploaded_file)
run_btn = st.button("✨ עצבי מחדש", type="primary", disabled=not ready)

if not ready:
    st.caption("העלי תמונה כדי להפעיל")

# ── Pipeline ─────────────────────────────────────────────────────────────────
if run_btn and uploaded_file:
    change_label = change_level.split(" — ")[0]

    color_line = "keep original color" if color_choice == "שמרי את הצבע המקורי" else f"change color to: {color_input or 'not specified'}"

    form_text = (
        f"Style: {STYLE_MAP.get(style, style)}\n"
        f"Change level: {CHANGE_MAP.get(change_label, change_label)}\n"
        f"Age: {age}\n"
        f"Length: {LENGTH_MAP.get(length, length)}\n"
        f"Occasion: {OCCASION_MAP.get(occasion, occasion)}\n"
        f"Skin exposure preference: {EXPOSURE_MAP.get(exposure, exposure)}\n"
        f"Zipper location: {ZIPPER_MAP.get(zipper_location, zipper_location)}\n"
        f"Color: {color_line}"
    )

    image_bytes = uploaded_file.read()
    mime_type = uploaded_file.type or "image/jpeg"

    # Pass image directly in new_message so DressAnalyzerAgent sees it natively
    new_message = types.Content(
        role="user",
        parts=[
            types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)),
            types.Part(text=form_text),
        ],
    )

    run_id = str(uuid.uuid4())
    sketch_filename = f"output/sketch_{run_id}.png"

    session_service = InMemorySessionService()
    session = asyncio.run(session_service.create_session(
        app_name="dress_agent",
        user_id="user",
        session_id=run_id,
    ))
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="dress_agent",
    )

    # Progress display — all start as ⏳ (running)
    st.divider()
    st.subheader("מעבד...")

    progress_slots = {}
    for name, label in AGENT_STEPS:
        progress_slots[name] = st.empty()
        progress_slots[name].markdown(f"⏳ {label}")

    status_text = st.empty()

    state_delta = {
        "user_preferences": form_text,
        "dress_analysis": "",
        "trend_insights": "",
        "design_concept": "",
        "final_design_concept": "",
        "sketch_path": sketch_filename,
        "seamstress_guide": "",
        "current_date": datetime.now().strftime("%B %Y"),
        "current_year": str(datetime.now().year),
    }

    pipeline_ok = False
    last_error = ""
    for attempt in range(3):
        if attempt > 0:
            status_text.markdown(f"**השרת עמוס, מנסה שוב ({attempt + 1}/3)...**")
            time.sleep(15)
            # Fresh session for each retry so pipeline starts clean
            session = asyncio.run(session_service.create_session(
                app_name="dress_agent",
                user_id="user",
                session_id=str(uuid.uuid4()),  # fresh session_id per retry
            ))

        try:
            agent_error = None
            completed = set()
            for event in runner.run(
                user_id="user",
                session_id=session.id,
                new_message=new_message,
                state_delta=state_delta,
            ):
                if getattr(event, "error_message", None):
                    agent_error = f"{event.author}: {event.error_message}"
                    break

                author = event.author or ""

                if getattr(event, "turn_complete", False) and author in progress_slots:
                    if author not in completed:
                        completed.add(author)
                        _, label = next((x for x in AGENT_STEPS if x[0] == author), (None, ""))
                        progress_slots[author].markdown(f"✅ {label.split('...')[0]}")

                        names = [n for n, _ in AGENT_STEPS]
                        idx = names.index(author) if author in names else -1
                        if idx >= 0 and idx + 1 < len(names):
                            _, next_label = AGENT_STEPS[idx + 1]
                            status_text.markdown(f"**עכשיו:** {next_label}")

            if agent_error:
                last_error = agent_error
                if "503" in last_error or "UNAVAILABLE" in last_error:
                    continue  # retryable — temporary API error
                break  # non-retryable — agent returned an error

            pipeline_ok = True
            break

        except Exception as e:
            last_error = str(e)
            if "503" not in last_error and "UNAVAILABLE" not in last_error:
                break  # non-retryable error

    if not pipeline_ok:
        if "503" in last_error or "UNAVAILABLE" in last_error:
            st.error("השרת של Gemini עמוס כרגע. נסי שוב בעוד כמה דקות.")
        else:
            st.error(f"שגיאה: {last_error}")
        st.stop()

    # Read results from session state
    final_session = asyncio.run(session_service.get_session(
        app_name="dress_agent", user_id="user", session_id=session.id
    ))
    state = getattr(final_session, "state", {}) if final_session else {}

    # Check which stages failed and update progress indicators
    _STAGE_STATUS_KEYS = {
        "ImageGeneratorAgent": "image_generation_status",
        "SketchValidatorAgent": "sketch_validation_status",
        "SeamstressValidatorAgent": "seamstress_validation_status",
    }
    failed_agents = {
        name for name, key in _STAGE_STATUS_KEYS.items()
        if state.get(key) == "failed"
    }
    for name, label in AGENT_STEPS:
        if name in failed_agents:
            progress_slots[name].markdown(f"⚠️ {label.split('...')[0]}")
        else:
            progress_slots[name].markdown(f"✅ {label.split('...')[0]}")
    status_text.empty()

    if failed_agents:
        st.warning("הצנרת הושלמה, אך שלב אחד או יותר לא עבר אימות. הסקיצה או המדריך עלולים להיות לא מושלמים.")

    # ── Results ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("התוצאות")

    sketch_path = Path(state.get("sketch_path", sketch_filename))
    if sketch_path.exists():
        st.image(str(sketch_path), caption="הסקיצה החדשה שלך", width=400)
        with open(sketch_path, "rb") as f:
            st.download_button("📥 הורידי את הסקיצה", f, file_name="new_design.png", mime="image/png")
        st.divider()

    tabs = st.tabs(["🔍 טרנדים", "🔬 ניתוח השמלה", "✏️ קונספט עיצוב", "🧵 מדריך לתופרת"])

    with tabs[0]:
        st.markdown(state.get("trend_insights", "—"))
    with tabs[1]:
        st.markdown(state.get("dress_analysis", "—"))
    with tabs[2]:
        st.markdown(state.get("final_design_concept", state.get("design_concept", "—")))
    with tabs[3]:
        st.markdown(state.get("seamstress_guide", "—"))
