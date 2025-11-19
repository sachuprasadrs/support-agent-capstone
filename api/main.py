from fastapi import FastAPI
from pydantic import BaseModel
from agent.orchestrator import handle_user_message
from agent.memory import save_user
import uvicorn

app = FastAPI()


class MessageInput(BaseModel):
    session_id: str
    user_id: str
    user_name: str = "User"
    user_email: str = "user@example.com"
    message: str


@app.post("/send")
def send_message(payload: MessageInput):
    """
    Endpoint for sending a user message to the Support Agent.
    """

    # Make sure user exists in DB
    save_user(
        payload.user_id,
        payload.user_name,
        payload.user_email,
        {"notes": "auto-created"}
    )

    output = handle_user_message(
        session_id=payload.session_id,
        user_id=payload.user_id,
        user_msg=payload.message
    )

    return {
        "reply": output["reply"],
        "trace_id": output["trace_id"]
    }


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
