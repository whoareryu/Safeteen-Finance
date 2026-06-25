from mcp.server.fastmcp import FastMCP


mcp = FastMCP("piper_dunn_coo")


@mcp.tool()
async def introduce_myself() -> str:
    return "파이드 파이퍼 COO 던 입니다"
