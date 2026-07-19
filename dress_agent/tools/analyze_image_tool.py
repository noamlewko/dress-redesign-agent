"""Standalone vision tool for analyzing a dress image via Gemini."""
import base64
from google import genai
from google.genai import types
from google.adk.tools import ToolContext


def analyze_dress_image(tool_context: ToolContext) -> str:
    """Analyze the uploaded dress image using Gemini Vision.

    Reads the image from session state (uploaded_image_bytes / uploaded_image_mime),
    calls Gemini, writes the Hebrew analysis back to state, and returns it.

    Args:
        tool_context: Injected automatically by ADK — do not pass manually.

    Returns:
        Hebrew fashion analysis string, or an error message.
    """
    image_b64 = tool_context.state.get("uploaded_image_bytes")
    mime_type = tool_context.state.get("uploaded_image_mime", "image/jpeg")
    if not image_b64:
        return "Error: no image found in session state."

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
