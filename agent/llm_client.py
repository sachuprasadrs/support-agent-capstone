import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def mock_llm_generate(context: List[Dict[str, str]], tools: List[Dict[str, Any]]):
    """
    Very simple mock model:
    - If message contains 'order', attempts a get_order tool call
    - Else replies normally
    """
    last = context[-1]['text'].lower()

    if "order" in last and ("status" in last or "late" in last or "#" in last):
        return {
            "type": "tool_call",
            "tool_name": "get_order",
            "args": {"order_id": "A123"}
        }

    if "refund" in last or "complain" in last:
        return {
            "type": "tool_call",
            "tool_name": "create_ticket",
            "args": {"summary": last}
        }

    return {"type": "reply", "text": "Sure, could you provide your order ID?"}


def openai_llm_generate(context: List[Dict[str, str]], tools: List[Dict[str, Any]]):
    import openai
    openai.api_key = OPENAI_API_KEY

    messages = [{"role": c["role"], "content": c["text"]} for c in context]

    system_inst = (
        "You are a customer support agent. If you need a tool, return JSON like "
        "{\"tool\": \"get_order\", \"args\": {\"order_id\": \"A123\"}}. "
        "Otherwise, reply normally."
    )
    messages.append({"role": "system", "content": system_inst})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    text = response.choices[0].message.content

    try:
        parsed = json.loads(text.strip())
        if "tool" in parsed:
            return {
                "type": "tool_call",
                "tool_name": parsed["tool"],
                "args": parsed.get("args", {})
            }
    except:
        pass

    return {"type": "reply", "text": text}


def llm_generate(context, tools):
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return openai_llm_generate(context, tools)
    return mock_llm_generate(context, tools)
