import json
from typing import List, Dict, Any
from .llm_client import llm_generate

"""
EVALUATION SYSTEM OVERVIEW:

This evaluator uses TWO judging layers:

1. Heuristic Judge (fast, offline)
2. LLM-as-Judge (accurate, qualitative scoring)

Then combines both to produce:
- Resolution score (0–1)
- Helpfulness score (0–1)
- Final weighted score
"""

# ---------------------------------------------------------
# 1. HEURISTIC JUDGE (local)
# ---------------------------------------------------------

def heuristic_judge(user_msg: str, agent_reply: str) -> float:
    """
    Simple offline judge:
    Looks for keyword alignment between the user's issue and the agent's response.
    """

    user_low = user_msg.lower()
    reply_low = agent_reply.lower()

    score = 0.0

    # If it's about order/delivery
    if "order" in user_low:
        if "order" in reply_low or "delivery" in reply_low or "tracking" in reply_low:
            score += 0.5

    # If it's about refund
    if "refund" in user_low:
        if "refund" in reply_low or "ticket" in reply_low:
            score += 0.5

    # Ticket fallback cover
    if "ticket" in reply_low:
        score += 0.4

    return min(score, 1.0)


# ---------------------------------------------------------
# 2. LLM-AS-JUDGE (slow, accurate)
# ---------------------------------------------------------

def llm_judge(user_msg: str, agent_reply: str) -> Dict[str, float]:
    """
    Uses the main LLM (or mock) to give:
    - resolution_score (0–1)
    - helpfulness_score (0–1)
    """

    prompt = f"""
You are a strict evaluator AI.

User message:
"{user_msg}"

Agent reply:
"{agent_reply}"

Evaluate the agent on two metrics:

1. RESOLUTION SCORE (0 to 1):
- 1.0 if the agent fully resolves or meaningfully progresses the issue
- 0.5 if partially correct or incomplete
- 0.0 if irrelevant, hallucinated, or incorrect

2. HELPFULNESS SCORE (0 to 1):
- 1.0 if the tone is polite, clear, and informative
- 0.5 if average
- 0.0 if unhelpful

Respond ONLY in JSON:
{{
  "resolution": 0.0,
  "helpfulness": 0.0
}}
""" 


    decision = llm_generate(
        context=[
            {"role": "system", "text": "You are an evaluation model."},
            {"role": "user", "text": prompt}
        ],
        tools=[]
    )

    # Mock LLM case
    if "text" in decision:
        try:
            result = json.loads(decision["text"])
            return {
                "resolution": float(result.get("resolution", 0)),
                "helpfulness": float(result.get("helpfulness", 0))
            }
        except:
            pass

    # If mock LLM cannot generate JSON:
    return {"resolution": 0.5, "helpfulness": 0.5}


# ---------------------------------------------------------
# 3. HYBRID JUDGE — combine both systems
# ---------------------------------------------------------

def hybrid_score(user_msg: str, agent_reply: str) -> Dict[str, float]:
    h_score = heuristic_judge(user_msg, agent_reply)
    llm_scores = llm_judge(user_msg, agent_reply)

    # Weighted final score
    final_score = 0.3 * h_score + 0.7 * (
        0.7 * llm_scores["resolution"] + 0.3 * llm_scores["helpfulness"]
    )

    return {
        "heuristic": h_score,
        "llm_resolution": llm_scores["resolution"],
        "llm_helpfulness": llm_scores["helpfulness"],
        "final_score": final_score
    }
