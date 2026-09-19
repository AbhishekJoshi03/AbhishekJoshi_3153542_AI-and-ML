from langchain_core.tools import tool

from backend.services.mcp_gateway import invoke_mcp_tool_sync


@tool
def get_current_weather(
    start_date: str = "",
    end_date: str = ""
) -> dict:
    """
    Get current or forecast weather for Singapore.

    Use this tool when the user asks about:
    - current weather
    - upcoming weather
    - rain
    - temperature
    - forecast
    - weather for specific travel dates

    Dates must use YYYY-MM-DD format.

    Do not use the static knowledge base for current weather.
    """

    return invoke_mcp_tool_sync(
        "fetch_singapore_weather",
        {
            "city": "Singapore",
            "start_date": start_date,
            "end_date": end_date
        }
    )


@tool
def convert_indian_rupees_to_sgd(amount: float) -> dict:
    """
    Convert Indian Rupees (INR) to Singapore Dollars (SGD)
    using the current exchange rate.

    MUST be used when the user asks for:
    - INR to SGD conversion
    - Indian Rupees to Singapore Dollars
    - Singapore budget conversion from INR
    """

    return invoke_mcp_tool_sync(
        "fetch_currency_conversion",
        {
            "amount": amount,
            "from_currency": "INR",
            "to_currency": "SGD"
        }
    )
