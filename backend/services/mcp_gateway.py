import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_SCRIPT = PROJECT_ROOT / "mcp_server" / "server.py"


async def invoke_mcp_tool(tool_name: str, arguments: dict):
    """
    Start the MCP server, connect to it, and call a tool.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(MCP_SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            if getattr(result, "isError", False):
                return {
                    "error": f"MCP tool '{tool_name}' returned an error.",
                    "details": _extract_text_content(result.content),
                }

            structured_content = getattr(result, "structuredContent", None)

            if structured_content:
                return structured_content

            text_content = _extract_text_content(result.content)

            if len(text_content) == 1:
                try:
                    return json.loads(text_content[0])
                except json.JSONDecodeError:
                    pass

            return {"content": text_content}


def _extract_text_content(content):
    return [
        item.text
        for item in content
        if getattr(item, "type", None) == "text"
    ]


def invoke_mcp_tool_sync(tool_name: str, arguments: dict):
    """
    Synchronous wrapper around the async MCP client.
    """

    return asyncio.run(
        invoke_mcp_tool(
            tool_name,
            arguments
        )
    )
