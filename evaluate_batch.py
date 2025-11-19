import json
from agent.evaluator import hybrid_score
from api.main import send_message, MessageInput

"""
This script:
- Runs a batch of simulated messages through the agent
- Collects agent replies
- Evaluates each interaction
- Saves a metrics report
"""

def run_batch():
    tests = [
        {"user_id": "u010", "msg": "Where is my order A123?"},
        {"user_id": "u020", "msg": "I want a refund for my damaged item"},
        {"user_id": "u030", "msg": "Package never arrived"},
        {"user_id": "u040", "msg": "Wrong item delivered"},
        {"user_id": "u050", "msg": "Help me track my shipment"}
    ]

    results = []

    for i, t in enumerate(tests):
        session_id = f"batch{i}"

        payload = MessageInput(
            session_id=session_id,
            user_id=t["user_id"],
            user_name="TestUser",
            user_email="test@example.com",
            message=t["msg"]
        )

        res = send_message(payload)

        score = hybrid_score(t["msg"], res["reply"])

        results.append({
            "case": t["msg"],
            "reply": res["reply"],
            "scores": score
        })

    # Save report
    with open("evaluation_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Evaluation complete → evaluation_report.json")


if __name__ == "__main__":
    run_batch()
