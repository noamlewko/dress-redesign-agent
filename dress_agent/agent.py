"""
Root agent: an 8-step SequentialAgent pipeline that takes a dress photo + user
preferences and produces a validated redesign sketch and seamstress construction guide.

Pipeline order:
    TrendResearchAgent → DressAnalyzerAgent → DesignCreatorAgent
    → DesignValidatorAgent → ImageGeneratorAgent → SketchValidatorAgent
    → SeamstressGuideAgent → SeamstressValidatorAgent
"""
from google.adk.agents import SequentialAgent
from .sub_agents import (
    trend_researcher,
    dress_analyzer,
    design_creator,
    design_validator,
    image_generator,
    sketch_validator,
    seamstress_guide,
    seamstress_validator,
)

root_agent = SequentialAgent(
    name="DressRedesignPipeline",
    description=(
        "A complete dress redesign pipeline: researches current trends, "
        "analyzes your dress, creates a new design concept, validates and corrects it, "
        "generates a visual sketch, validates the sketch visually, "
        "writes seamstress instructions, and validates them against the design."
    ),
    sub_agents=[
        trend_researcher,
        dress_analyzer,
        design_creator,
        design_validator,
        image_generator,
        sketch_validator,
        seamstress_guide,
        seamstress_validator,
    ],
)
