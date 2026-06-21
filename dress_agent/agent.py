from google.adk.agents import SequentialAgent
from .sub_agents import (
    trend_researcher,
    dress_analyzer,
    design_creator,
    image_generator,
    seamstress_guide,
)

root_agent = SequentialAgent(
    name="DressRedesignPipeline",
    description=(
        "A complete dress redesign pipeline: researches current trends, "
        "analyzes your dress, creates a new design concept, generates a visual sketch, "
        "and provides detailed seamstress instructions."
    ),
    sub_agents=[
        trend_researcher,
        dress_analyzer,
        design_creator,
        image_generator,
        seamstress_guide,
    ],
)
