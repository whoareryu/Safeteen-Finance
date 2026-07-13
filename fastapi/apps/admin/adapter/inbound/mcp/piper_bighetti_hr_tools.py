from mcp.server.fastmcp import FastMCP


mcp = FastMCP("piper_bighetti_hr")


@mcp.tool()
async def introduce_myself() -> str:
    return "파이드 파이퍼 HR 담당자 빅헤드 입니다"
