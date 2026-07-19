"""Image generation tool: calls Gemini to produce a front-and-back fashion sketch."""
import os
from google import genai
from google.genai import types
from google.adk.tools import ToolContext


def generate_dress_sketch(design_description: str, tool_context: ToolContext) -> str:
    """Generate a front-and-back fashion sketch using Gemini image generation.

    Args:
        design_description: Visual description of the redesigned dress including
            silhouette, fabrics, colors, and key design elements.
        tool_context: Injected automatically by ADK — do not pass manually.

    Returns:
        Confirmation string with the path to the saved sketch, or an error message.
    """
    client = genai.Client()

    prompt = (
        f"Two fashion design sketches of the same dress side by side on a plain white background. "
        f"Left sketch: front view. Right sketch: back view. "
        f"Style: professional fashion illustration with fabric areas filled in their actual colors — dark fabrics drawn as solid dark shapes, not as outlines only. "
        f"Clean sketch lines, minimal shading, flat color fills. "
        f"COLOR RULE: Every part of the dress must be the exact color stated in the description. Do NOT use default fabric colors — lace is NOT always white, chiffon is NOT always ivory, satin is NOT always cream. If the description says black lace, draw deep black lace — NOT gray, NOT dark gray, NOT charcoal. Black means black. Color from the description overrides all assumptions about typical fabric color. When lace is black on black fabric, show the lace pattern as very subtle texture variation within deep black — the overall area must read as black, not gray. "
        f"FABRIC RENDERING GUIDE — render each fabric exactly as follows: "
        f"SEQUIN MESH: dense field of small dots of light scattered across the surface, high sparkle, fabric reads as glittering. "
        f"METALLIC LAMÉ: soft draped woven cloth with a subtle all-over metallic sheen — flows and catches light as it moves. NOT rigid, NOT geometric faceted shapes, NOT armor. "
        f"HIGH-SHINE SATIN or SILK CHARMEUSE: smooth liquid surface with strong highlight on curves and deep shadow in folds. Reflective but not sparkly. "
        f"FEATHER TRIM: soft fluffy fringe along hem or cuffs — individual feather strands visible, light and airy. "
        f"GUIPURE LACE: bold raised floral or geometric motif, opaque pattern with open holes between motifs — NOT sheer overall. "
        f"CHANTILLY LACE: fine delicate floral net pattern, more transparent than guipure, ground net is visible. "
        f"BRODERIE ANGLAISE: white or cream embroidered fabric with small eyelet holes punched through — embroidered edges around each hole. "
        f"VELVET: same color as surrounding fabric but visibly deeper and richer — directional surface sheen where light hits, slightly darker in shadow. Clearly distinct from matte cotton even when same color. "
        f"BROCADE: woven pattern raised slightly above the surface — geometric or floral motif visible as texture, not as separate pieces. "
        f"SATIN TRIM: narrow ribbon or band with a high-shine reflective surface, contrasting against matte base. "
        f"CHIFFON: translucent soft layers — fabric is sheer, edges are soft and floating, multiple layers visible. NOT stiff or structured. "
        f"RAW LINEN: slightly rough matte texture, visible fabric weave, earthy and unpolished look. "
        f"MACRAMÉ or CROCHET: visible open knotted or stitched pattern — graphic geometric or floral openwork. "
        f"SILK CREPE or STRUCTURED TAFFETA: flat matte surface, holds its shape, no sheen, no texture. "
        f"TWEED or JACQUARD: visible woven pattern or fleck texture across the surface — heavier-looking than crepe. "
        f"MATTE COTTON: completely flat, no sheen, no texture — the baseline reference fabric. "
        f"LACE TRANSPARENCY RULE: 'lace appliqué over fabric' or 'lace bonded onto' = opaque, skin NOT visible, lace texture on surface only. Only draw lace as transparent when description says 'sheer lace', 'lace revealing skin', or 'transparent lace'. "
        f"SLEEVES: If the description says 'sleeveless' — draw NO sleeves, NO cap sleeves, NO lace extending over the shoulder. The armhole must be clean and open. "
        f"Absolutely no text, no letters, no numbers, no words, no labels, no annotations anywhere in the image. "
        f"No logos, no watermarks, no brand names, no callouts, no dimension lines. "
        f"Dress description: {design_description}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        ),
    )

    os.makedirs("output", exist_ok=True)
    path = "output/new_design.png"

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            with open(path, "wb") as f:
                f.write(part.inline_data.data)
            tool_context.state["sketch_path"] = path
            return f"Sketch saved to {path}"

    return "Image generation returned no image"
