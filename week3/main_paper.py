"""Entry point for country_research_paper MCP server."""

from server_paper import mcp


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
