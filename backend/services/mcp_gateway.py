import asyncio
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
        command="python",
        args=[str(MCP_SERVER_SCRIPT)],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            return result


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
