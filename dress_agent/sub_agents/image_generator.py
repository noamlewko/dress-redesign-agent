from google.adk.agents import Agent
from dress_agent.tools.imagen_tool import generate_dress_sketch

image_generator = Agent(
    name="ImageGeneratorAgent",
    model="gemini-2.5-flash",
    description="Generates a visual sketch of the redesigned dress using Imagen 3",
    instruction="""You are an AI image generation coordinator.

Based on the design concept below, call the generate_dress_sketch tool to create a visual sketch.

Design concept:
{design_concept}

Condense the design concept into a focused, visual prompt for the image tool.
Include: style, silhouette, neckline, sleeves, length, fabric, and dominant colors.
Keep the prompt under 200 words but make it highly descriptive and specific.
""",
    tools=[generate_dress_sketch],
    output_key="sketch_path",
)
