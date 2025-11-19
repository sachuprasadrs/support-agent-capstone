import json
import uuid
from .llm_client import llm_generate
from .tools import get_order, get_product, create_ticket, send_email
from .memory import init_db, append_session_event, add_memory, retrieve_memories
from .logger import log_event

init_db()

TOOLS = {
    "get_order": {"fn": get_order, "desc": "Fetch an order by ID"},
    "get_product": {"fn": get_product, "desc": "Fetch a product by ID"},
    "create_ticket": {"fn": create_ticket, "desc": "Create a support ticket"},
    "send_email": {"fn": send_email, "desc": "Send an email"}
}

SYSTEM_PROMPT = (
    "You are SupportGPT. You solve customer issues using tools when needed. "
    "If tool needed, respond ONLY with JSON: {\"tool\": \"tool_name\", \"args\": {...}}"
)


def handle_user_message(session_id: str, user_id: str, user_msg: str):
    trace_id = str(uuid.uuid4())

    memories = retrieve_memories(user_id)
    memory_text = "\n".join([m["content"] for m in memories])

    context = [
        {"role": "system", "text": SYSTEM_PROMPT},
        {"role": "system", "text": f"User memory:\n{memory_text}"},
        {"role": "user", "text": user_msg}
    ]

    log_event({"trace_id": trace_id, "event": "user_message", "text": user_msg})
    append_session_event(session_id, user_id, {"role": "user", "text": user_msg})

    for step in range(5):
        decision = llm_generate(
            context,
            tools=[{"name": k, "desc": TOOLS[k]["desc"]} for k in TOOLS]
        )

        log_event({"trace_id": trace_id, "event": "llm_decision", "decision": decision})

        if decision["type"] == "reply":
            reply = decision["text"]
            append_session_event(session_id, user_id, {"role": "assistant", "text": reply})
            log_event({"trace_id": trace_id, "event": "assistant_reply", "reply": reply})
            return {"trace_id": trace_id, "reply": reply}

        if decision["type"] == "tool_call":
            tool_name = decision["tool_name"]
            args = decision.get("args", {})

            tool = TOOLS.get(tool_name)
            if not tool:
                err = f"Unknown tool: {tool_name}"
                append_session_event(session_id, user_id, {"role": "assistant", "text": err})
                return {"trace_id": trace_id, "reply": err}

            # Auto-fill missing user_id for tools that need it
            if tool_name == "create_ticket":
                if "user_id" not in args:
                    args["user_id"] = user_id  # <-- FIX

            result = tool["fn"](**args)

            append_session_event(
                session_id,
                user_id,
                {"role": "tool", "tool": tool_name, "args": args, "result": result}
            )

            log_event({"trace_id": trace_id, "event": "tool_result", "tool": tool_name, "result": result})

            context.append({
                "role": "tool",
                "text": json.dumps({"tool": tool_name, "result": result})
            })

    fallback = "I couldn't resolve this automatically. I have created a ticket."
    ticket = create_ticket(user_id, user_msg)
    add_memory(user_id, "ticket", json.dumps(ticket))

    log_event({"trace_id": trace_id, "event": "fallback_ticket", "ticket": ticket})

    return {"trace_id": trace_id, "reply": f"{fallback} Ticket ID: {ticket['ticket_id']}"}
