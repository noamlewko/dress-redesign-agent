"""
Step 8 of 8 — validates the seamstress guide against the design concept,
fixing contradictions or missing elements in a loop until approved.
"""
from google.adk.agents import Agent
from dress_agent.tools.validate_seamstress_tool import validate_seamstress_guide

seamstress_validator = Agent(
    name="SeamstressValidatorAgent",
    model="gemini-flash-lite-latest",
    description="Validates the seamstress guide for design consistency and professional construction quality, fixing issues in a loop",
    instruction="""You are a master couturier validating a seamstress guide.

Call validate_seamstress_guide. The tool will:
1. Check that the guide matches the design concept and user preferences
2. Check that all instructions are professionally correct — proper terminology, achievable techniques, correct construction sequence
3. Rewrite and fix the guide automatically if problems are found
4. Loop until the guide passes both checks or 3 attempts are reached

After the tool completes, report what happened: either approval or what issues remain.
""",
    tools=[validate_seamstress_guide],
    output_key="seamstress_validation",
    include_contents="none",
)
