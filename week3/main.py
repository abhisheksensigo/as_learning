from mcp.server.fastmcp import FastMCP

mcp = FastMCP("argentina-research")


@mcp.tool()
def hello() -> str:
    """Say hello. Use this to verify the server is connected."""
    return "Hello from Havier Millei!"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
