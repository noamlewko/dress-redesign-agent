"""Seamstress guide validation tool: checks that instructions match the design concept exactly."""
from google import genai
from google.adk.tools import ToolContext

MAX_ATTEMPTS = 3

CHECK_PROMPT = """You are a master couturier with 20+ years of atelier experience. You are checking a seamstress guide for two things:

1. DESIGN CONSISTENCY — does the guide match the design concept and user preferences?
2. PROFESSIONAL QUALITY — are the instructions technically correct and written in proper seamstress language?

DESIGN CONCEPT:
{design_concept}

USER PREFERENCES:
{user_preferences}

SEAMSTRESS GUIDE:
{guide}

Check BOTH of the following:

**DESIGN CONSISTENCY — flag if:**
- An instruction contradicts the design (e.g. guide says remove zipper but design keeps it)
- A named design element is completely missing from the guide
- An instruction conflicts with user preferences (color, length, change level)

**PROFESSIONAL QUALITY — flag if:**
- A technique is named incorrectly or used in the wrong context (e.g. French seam on velvet, serger on lamé, fusible interfacing on velvet or lamé)
- An instruction is physically impossible or structurally unsound
- Construction steps are in the wrong order — the correct order is: pre-shrink → interface → stay-stitch → darts → pockets → ZIPPER (before side seams, while garment is flat) → shoulder seams → neckline/facings → side seams → waist → sleeves → hem
- Ruffles described as cut on bias — ruffles use crosswise grain, not true bias (bias is for cowl necklines and spiral flounces only)
- Wrong thread specified for fabric — polyester 40-weight on silk risks cutting fibers (should be fine 60-weight polyester or cotton)
- Wrong needle type for fabric — silk/lamé/satin require Microtex; velvet requires walking foot
- Seam allowance wrong for fabric or situation
- Grain direction missing or wrong for a new fabric piece
- Facing sewn without understitching instruction
- Curves not clipped (concave) or notched (convex)
- An irreversible step is not marked with ⚠️
- On silk/satin/lamé: guide says to let out (widen) an existing seam — old needle holes will be exposed on high-sheen surfaces

Do NOT flag: minor wording differences, style preferences, or valid alternative techniques.

If the guide is both consistent with the design AND professionally correct, respond with exactly: APPROVED"""

FIX_PROMPT = """You are a master couturier with 20+ years of atelier experience. Rewrite the seamstress guide below to fix these specific issues:

ISSUES TO FIX:
{issues}

DESIGN CONCEPT (source of truth):
{design_concept}

USER PREFERENCES:
{user_preferences}

ORIGINAL GUIDE:
{guide}

Rules:
- Fix only the listed issues. Do not change anything else.
- Keep the same Hebrew sections and structure.
- Write the entire corrected guide in Hebrew.
- Do not add a preamble — output the guide directly."""


def validate_seamstress_guide(tool_context: ToolContext) -> str:
    """Validate the seamstress guide against the design concept and fix issues in a loop.

    Reads seamstress_guide and final_design_concept from state, checks for
    contradictions or missing elements, and rewrites problematic sections
    until the guide matches or MAX_ATTEMPTS is reached.

    Args:
        tool_context: Injected automatically by ADK — do not pass manually.

    Returns:
        Validation result: approval message or description of remaining issues.
    """
    guide = tool_context.state.get("seamstress_guide", "")
    design_concept = tool_context.state.get("final_design_concept", "")
    user_preferences = tool_context.state.get("user_preferences", "")

    if not guide or not design_concept:
        return "Missing guide or design concept — cannot validate."

    client = genai.Client()
    last_issues = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        check_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=CHECK_PROMPT.format(
                design_concept=design_concept,
                user_preferences=user_preferences,
                guide=guide,
            ),
        )

        result = check_response.text.strip()

        if result.upper() == "APPROVED":
            tool_context.state["seamstress_validation"] = "Guide matches design."
            tool_context.state["seamstress_validation_status"] = "passed"
            return f"Seamstress guide approved after {attempt} attempt(s)."

        last_issues = result

        if attempt < MAX_ATTEMPTS:
            fix_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=FIX_PROMPT.format(
                    issues=last_issues,
                    design_concept=design_concept,
                    user_preferences=user_preferences,
                    guide=guide,
                ),
            )
            guide = fix_response.text.strip()
            tool_context.state["seamstress_guide"] = guide

    tool_context.state["seamstress_validation_status"] = "failed"
    tool_context.state["seamstress_validation"] = f"Validation failed. Remaining issues: {last_issues}"
    return f"Seamstress guide validation failed after {MAX_ATTEMPTS} attempts. Remaining issues:\n{last_issues}"
