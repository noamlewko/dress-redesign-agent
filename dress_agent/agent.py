from google.adk.agents import Agent

root_agent = Agent(
    name="dress_agent",
    model="gemini-2.5-flash",
    description="A fashion redesign assistant that analyzes dresses and suggests new designs",
    instruction="""
    You are a professional fashion designer assistant.

    Your job is to help users redesign their dresses.
    For now, ask the user to describe their dress and their style preferences,
    and suggest a redesign concept.
    """,
)
