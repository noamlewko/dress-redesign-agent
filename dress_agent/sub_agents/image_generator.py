"""
Step 5 of 8 — extracts the IMAGE_PROMPT from the validated design concept and
calls generate_dress_sketch to produce a front-and-back fashion sketch.
"""
from google.adk.agents import Agent
from dress_agent.tools.imagen_tool import generate_dress_sketch

image_generator = Agent(
    name="ImageGeneratorAgent",
    model="gemini-flash-lite-latest",
    description="Generates a front-and-back fashion sketch of the redesigned dress using Gemini image generation",
    instruction="""You are an AI image generation coordinator.

The design concept below contains a field called IMAGE_PROMPT. Extract it exactly and pass it to generate_dress_sketch — do not paraphrase, do not summarize, do not add or remove anything from it.

Design concept:
{final_design_concept}

If IMAGE_PROMPT is present in the concept above, use it verbatim as the design_description argument.
If IMAGE_PROMPT is not present, write one yourself following these rules:
- State the EXACT neckline: "one-shoulder", "strapless", "deep V", "square neck", "cowl neck", etc. Never leave it ambiguous.
- State the EXACT sleeve type: "sleeveless", "short sleeves", "3/4 sleeves", or "long sleeves"
- State the EXACT skirt silhouette: "A-line flared skirt", "pencil skirt", "full circle skirt", "column straight skirt" — this is critical. If the concept says Fit-and-Flare, write "A-line flared skirt, wide at hem"
- State the EXACT length: "midi length", "maxi length", "mini length", "knee-length"
- VINTAGE SEAM DETAILS: if the concept mentions a specific seam or construction line (Basque waist, princess seams, corset boning lines, ruching), describe it explicitly in visual terms — e.g. "visible V-shaped seam at the waist creating a pointed basque effect", "vertical topstitched seam lines on bodice resembling corset boning"
- For waist details: match exactly what the concept says — flat band stays flat, peplum stays peplum
- Describe cutouts with exact placement: "two small triangular cutouts at the sides of the waist, exactly where the bodice meets the skirt"
- CRITICAL: No text, no letters, no words, no labels, no annotations, no callouts anywhere in the image — not even partial words or designer notes
- For skirt silhouette: never use "voluminous" or "stiff" — write exactly how the hem opens: "A-line skirt that flares outward to a wide open hem", "gathered skirt falling straight to a flat hem". Only use "bubble" or "tulip" if the design specifically calls for a closed tapering hem
""",
    tools=[generate_dress_sketch],
    include_contents="none",
)
