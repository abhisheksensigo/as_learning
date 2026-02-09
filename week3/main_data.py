"""Entry point for country_research_data MCP server."""

from server_data import mcp


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
