import os
from google import genai
from google.genai import types
from google.adk.tools import ToolContext


def generate_dress_sketch(design_description: str, tool_context: ToolContext) -> str:
    """Generate a dress design sketch from a description using Imagen 3.

    Args:
        design_description: Detailed visual description of the redesigned dress,
            including style, colors, fabrics, silhouette, and key design elements.
        tool_context: Automatically injected by ADK — do not pass manually.

    Returns:
        Path to the saved sketch image file.
    """
    client = genai.Client()

    prompt = (
        f"Two fashion design sketches of the same dress side by side on a plain white background. "
        f"Left sketch: front view. Right sketch: back view. "
        f"Style: professional fashion illustration with fabric areas filled in their actual colors — dark fabrics drawn as solid dark shapes, not as outlines only. "
        f"Clean sketch lines, minimal shading, flat color fills. "
        f"Absolutely no text, no letters, no numbers, no words, no labels, no annotations anywhere in the image. "
        f"No logos, no watermarks, no brand names, no callouts, no dimension lines. "
        f"Dress description: {design_description}"
    )

    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1),
    )

    os.makedirs("output", exist_ok=True)
    image_bytes = response.generated_images[0].image.image_bytes
    path = "output/new_design.png"

    with open(path, "wb") as f:
        f.write(image_bytes)

    tool_context.state["sketch_path"] = path
    return f"Sketch saved to {path}"
