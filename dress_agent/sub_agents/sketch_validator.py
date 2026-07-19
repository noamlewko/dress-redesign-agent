"""
Step 6 of 8 — visually validates the generated sketch against the design concept
and regenerates it once if critical elements are missing.
"""
from google.adk.agents import Agent
from dress_agent.tools.validate_sketch_tool import validate_sketch

sketch_validator = Agent(
    name="SketchValidatorAgent",
    model="gemini-flash-lite-latest",
    description="Validates the generated sketch against the design concept and regenerates if elements are missing",
    instruction="""You are a sketch quality validator.

Call validate_sketch. The tool will:
1. Compare the generated sketch visually against the design description
2. Identify any missing or incorrect elements
3. Regenerate the sketch automatically if problems are found

After the tool completes, report what happened: either that the sketch was approved, or what was fixed.
""",
    tools=[validate_sketch],
    output_key="sketch_validation",
    include_contents="none",
)
