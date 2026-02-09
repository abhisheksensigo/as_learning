"""Entry point for country_research_news MCP server."""

from server_news import mcp


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
