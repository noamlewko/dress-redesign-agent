import base64
from google import genai
from google.genai import types
from google.adk.tools import ToolContext

# Module-level store — set by app.py before running the pipeline
_image_bytes: bytes | None = None
_image_mime: str = "image/jpeg"


def set_current_image(image_bytes: bytes, mime_type: str) -> None:
    global _image_bytes, _image_mime
    _image_bytes = image_bytes
    _image_mime = mime_type


def analyze_dress_image(tool_context: ToolContext) -> str:
    """Analyze the uploaded dress image using Gemini Vision."""
    global _image_bytes, _image_mime

    # Prefer module-level store; fall back to state
    if _image_bytes:
        image_bytes = _image_bytes
        mime_type = _image_mime
    else:
        image_b64 = tool_context.state.get("uploaded_image_bytes")
        mime_type = tool_context.state.get("uploaded_image_mime", "image/jpeg")
        if not image_b64:
            return "שגיאה: לא נמצאה תמונה."
        image_bytes = base64.b64decode(image_b64)

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
                    ),
                    types.Part(text=(
                        "You are a professional fashion analyst. "
                        "Analyze this dress image in detail. The image may show: "
                        "a person wearing the dress, someone else wearing it, or the dress laid flat. "
                        "Focus only on the dress. Describe: "
                        "1) Style, 2) Neckline, 3) Sleeves, 4) Length, 5) Silhouette, "
                        "6) Fabric (infer from texture/drape), 7) Color & Pattern, "
                        "8) Construction details (closures, pockets, embellishments). "
                        "Be precise and technical. Write the entire response in Hebrew."
                    )),
                ],
            )
        ],
    )

    analysis = response.text
    tool_context.state["dress_analysis"] = analysis
    return analysis
