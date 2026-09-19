from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
    SystemMessage,
)

from backend.services.knowledge_base import search_travel_knowledge_base
from backend.services.travel_tools import (
    get_current_weather,
    convert_indian_rupees_to_sgd,
)

load_dotenv()

CHAT_MODEL_NAME = "gemini-3.6-flash"

LIVE_DATA_TOOL_NAMES = {
    "get_current_weather",
    "convert_indian_rupees_to_sgd",
}

ASSISTANT_SYSTEM_PROMPT = """
You are Singapore Travel Agent, a context-aware Singapore travel planning assistant.

You have access to three tools.

1. search_travel_knowledge_base

Use this for relatively stable Singapore travel information:

- attractions
- neighbourhoods
- transportation
- food
- cultural information
- indoor activities
- outdoor activities
- sample itineraries

2. get_current_weather

Use this for:

- current weather
- upcoming weather
- rain
- temperature
- weather forecast
- weather for specific travel dates

This information comes from a live MCP weather service.

3. convert_indian_rupees_to_sgd

Use this for:

- INR to SGD conversion
- Indian Rupees to Singapore Dollars
- Singapore budget conversion from INR

This information comes from a live MCP currency service.

IMPORTANT RULES:

- Never invent facts.
- Use the knowledge base for relatively stable destination information.
- Use MCP for current weather.
- Use MCP for current currency conversion.
- Do not use the knowledge base for current weather.
- If the knowledge base does not contain enough information, say so clearly.
- Distinguish facts from recommendations.
- Preserve context from previous user messages.
- If the user refers to "this trip", "day 2", "that itinerary", etc.,
  use previous conversation context.
- When using knowledge base information, mention the relevant source.
- When using MCP information, identify it as live MCP information.
"""

chat_model = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)

assistant_tools = [
    search_travel_knowledge_base,
    get_current_weather,
    convert_indian_rupees_to_sgd,
]

tool_registry = {
    tool.name: tool
    for tool in assistant_tools
}

chat_model_with_tools = chat_model.bind_tools(assistant_tools)


def start_new_conversation():
    return [
        SystemMessage(content=ASSISTANT_SYSTEM_PROMPT)
    ]


def extract_knowledge_sources(tool_result, known_sources):
    result_text = str(tool_result)
    discovered_sources = []

    for block in result_text.split("SOURCE TITLE:")[1:]:
        lines = block.strip().splitlines()

        if len(lines) < 2:
            continue

        title = lines[0].strip()
        url = ""

        for line in lines:
            line = line.strip()
            if line.startswith("SOURCE URL:"):
                url = line.replace("SOURCE URL:", "").strip()

        already_known = any(
            source["title"] == title
            for source in known_sources
        )

        if title and not already_known:
            discovered_sources.append({"title": title, "url": url})

    return discovered_sources


def run_tool_call(tool_call, citations):
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    tool = tool_registry.get(tool_name)

    if tool is None:
        return {"error": f"Tool '{tool_name}' is unavailable."}

    try:
        result = tool.invoke(tool_args)

        if tool_name == "search_travel_knowledge_base":
            citations.extend(
                extract_knowledge_sources(result, citations)
            )

        return result

    except Exception as error:
        return {"error": f"Tool execution failed: {str(error)}"}


def get_assistant_reply(user_message, message_history):
    message_history.append(
        HumanMessage(content=user_message)
    )

    tools_invoked = []
    citations = []
    used_live_data = False

    while True:
        response = chat_model_with_tools.invoke(message_history)
        message_history.append(response)

        if not response.tool_calls:
            return {
                "reply": response.content,
                "tools_invoked": list(dict.fromkeys(tools_invoked)),
                "citations": citations,
                "used_live_data": used_live_data,
            }

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tools_invoked.append(tool_name)

            if tool_name in LIVE_DATA_TOOL_NAMES:
                used_live_data = True

            result = run_tool_call(tool_call, citations)

            message_history.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )
