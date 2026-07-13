from mcp.server.fastmcp import FastMCP


mcp = FastMCP("piper_dinesh_dash")


@mcp.tool()
async def introduce_myself() -> str:
    return "파이드 파이퍼 대시보드 담당자 디네시 입니다"
