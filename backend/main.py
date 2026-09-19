from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.assistant import get_assistant_reply, start_new_conversation

api = FastAPI(
    title="Singapore Travel Agent \u2014 Singapore Travel Companion API"
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Holds each browser session's running conversation.
session_store = {}


def empty_reply(reply_text):
    return {
        "reply": reply_text,
        "tools_invoked": [],
        "citations": [],
        "used_live_data": False,
    }


@api.get("/")
def get_service_status():
    return {
        "message": "Singapore Travel Agent Travel Companion API is running"
    }


@api.post("/api/chat")
def handle_chat_message(payload: dict):
    user_message = payload.get("message", "")
    session_id = payload.get("session_id", "")

    if not user_message.strip():
        return empty_reply("Please enter a question.")

    if not session_id:
        return empty_reply("Session ID is required.")

    if session_id not in session_store:
        session_store[session_id] = start_new_conversation()

    message_history = session_store[session_id]

    return get_assistant_reply(user_message, message_history)
