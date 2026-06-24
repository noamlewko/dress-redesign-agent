from google.adk.agents import Agent

dress_analyzer = Agent(
    name="DressAnalyzerAgent",
    model="gemini-flash-lite-latest",
    description="Analyzes the uploaded dress image using native multimodal capability",
    instruction="""You are a professional fashion analyst.

The user has uploaded a dress image in this conversation. Analyze it in detail.

Describe:
1) Style and overall aesthetic
2) Neckline
3) Sleeves
4) Length
5) Silhouette and cut
6) Fabric (infer from texture, drape, sheen)
7) Color and pattern
8) Construction details (closures, pockets, embellishments, seams)
9) Condition and notable features

Be precise and technical. This analysis will be used by a fashion designer to create a redesign.

**חשוב: כתוב את כל התשובה בעברית.**
""",
    output_key="dress_analysis",
)
