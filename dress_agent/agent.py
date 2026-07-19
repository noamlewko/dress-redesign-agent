"""
Root agent: a 6-step SequentialAgent pipeline that takes a dress photo + user
preferences and produces a redesign sketch and seamstress construction guide.

Pipeline order:
    TrendResearchAgent → DressAnalyzerAgent → DesignCreatorAgent
    → DesignValidatorAgent → ImageGeneratorAgent → SeamstressGuideAgent
"""
from google.adk.agents import SequentialAgent
from .sub_agents import (
    trend_researcher,
    dress_analyzer,
    design_creator,
    design_validator,
    image_generator,
    seamstress_guide,
)

root_agent = SequentialAgent(
    name="DressRedesignPipeline",
    description=(
        "A complete dress redesign pipeline: researches current trends, "
        "analyzes your dress, creates a new design concept, validates and corrects it, "
        "generates a visual sketch, and provides detailed seamstress instructions."
    ),
    sub_agents=[
        trend_researcher,
        dress_analyzer,
        design_creator,
        design_validator,
        image_generator,
        seamstress_guide,
    ],
)
