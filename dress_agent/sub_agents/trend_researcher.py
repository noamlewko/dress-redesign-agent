from google.adk.agents import Agent
from google.adk.tools import google_search

trend_researcher = Agent(
    name="TrendResearchAgent",
    model="gemini-2.5-flash",
    description="Searches Google for current fashion trends based on the user's chosen style",
    instruction="""You are a fashion trend researcher.

The user wants to redesign their dress. Read their message to identify the style they chose
(e.g., vintage, modern, classic, bohemian, minimalist, glam).

Search Google for: "[chosen style] fashion trends 2025"

Focus on how this style appears in TODAY's fashion — not just classic interpretations.
Summarize 4-5 key current trends with specifics:
- Color palettes in use right now
- Silhouettes and cuts that are trending
- Fabrics and textures
- Signature design details

Keep the summary concise and visual. It will be used by a designer agent next.
""",
    tools=[google_search],
    output_key="trend_insights",
)
