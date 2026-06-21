import os
from google import genai
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
        f"Fashion design sketch, clean white background, professional illustration, "
        f"detailed dress design: {design_description}"
    )

    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        number_of_images=1,
    )

    os.makedirs("output", exist_ok=True)
    image_bytes = response.generated_images[0].image.image_bytes
    path = "output/new_design.png"

    with open(path, "wb") as f:
        f.write(image_bytes)

    tool_context.state["sketch_path"] = path
    return f"Sketch saved to {path}"
