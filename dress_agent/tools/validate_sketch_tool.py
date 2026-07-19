"""Sketch validation tool: compares the generated sketch against the design concept using Gemini Vision."""
import re
from pathlib import Path

from google import genai
from google.genai import types
from google.adk.tools import ToolContext

from dress_agent.tools.imagen_tool import generate_dress_sketch

MAX_ATTEMPTS = 3


def validate_sketch(tool_context: ToolContext) -> str:
    """Compare the generated sketch against IMAGE_PROMPT using Gemini Vision.

    Reads the sketch, checks it against the design description, and loops —
    regenerating with explicit corrections each time — until the sketch matches
    or MAX_ATTEMPTS is reached.

    Args:
        tool_context: Injected automatically by ADK — do not pass manually.

    Returns:
        Validation result: approval message, or what issues remain after max attempts.
    """
    sketch_path = tool_context.state.get("sketch_path")
    if not sketch_path or not Path(sketch_path).exists():
        tool_context.state["sketch_validation_status"] = "failed"
        return "No sketch found to validate."

    design_concept = tool_context.state.get("final_design_concept", "")

    if not design_concept:
        tool_context.state["sketch_validation_status"] = "failed"
        tool_context.state["sketch_validation"] = "Validation failed because no design concept was found."
        return "No design concept found to validate against."

    # Extract IMAGE_PROMPT section from the design concept
    match = re.search(r"IMAGE_PROMPT[:\s]+(.*?)(?=\n[A-Z][A-Z]|\Z)", design_concept, re.DOTALL | re.IGNORECASE)
    image_prompt = match.group(1).strip() if match else design_concept

    client = genai.Client()
    last_issues = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        with open(sketch_path, "rb") as f:
            sketch_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(inline_data=types.Blob(mime_type="image/png", data=sketch_bytes)),
                        types.Part(text=(
                            f"You are a fashion sketch quality checker.\n\n"
                            f"DESIGN DESCRIPTION:\n{image_prompt}\n\n"
                            f"Examine this sketch carefully. List ONLY elements from the description "
                            f"that are clearly missing or visually wrong in the sketch. "
                            f"Be specific: name each missing element and what it should look like.\n"
                            f"Focus on: fabric types, colors, neckline, silhouette, length, key details.\n"
                            f"Ignore minor artistic style differences — only flag real omissions.\n"
                            f"If the sketch matches the description well, respond with exactly: APPROVED"
                        )),
                    ],
                )
            ],
        )

        result = response.text.strip()

        if result.upper() == "APPROVED":
            tool_context.state["sketch_validation"] = "Sketch matches design."
            tool_context.state["sketch_validation_status"] = "passed"
            return f"Sketch approved after {attempt} attempt(s)."

        last_issues = result

        if attempt < MAX_ATTEMPTS:
            enhanced_prompt = (
                f"{image_prompt}\n\n"
                f"CRITICAL — the following elements were missing in the previous attempt. "
                f"Each one MUST be clearly visible in this new sketch:\n{last_issues}"
            )
            regen_result = generate_dress_sketch(enhanced_prompt, tool_context)
            if "Sketch saved to" not in regen_result:
                tool_context.state["sketch_validation_status"] = "failed"
                return f"Sketch regeneration failed: {regen_result}"
            sketch_path = tool_context.state.get("sketch_path", sketch_path)

    tool_context.state["sketch_validation_status"] = "failed"
    tool_context.state["sketch_validation"] = f"Validation failed. Remaining issues: {last_issues}"
    return f"Sketch validation failed after {MAX_ATTEMPTS} attempts. Remaining issues:\n{last_issues}"
