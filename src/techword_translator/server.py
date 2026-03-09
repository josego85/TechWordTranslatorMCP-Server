"""FastMCP server — entry point, registers tools and runs the server."""

import os

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .tools import (
    translate_term,
    search_tech_terms,
    get_all_translations,
    get_term_details,
    list_tech_terms,
    create_tech_word,
)

load_dotenv()

mcp = FastMCP(name=os.getenv("MCP_SERVER_NAME", "TechWord Translator"))

for _tool in [translate_term, search_tech_terms, get_all_translations, get_term_details, list_tech_terms, create_tech_word]:
    mcp.tool()(_tool)

if __name__ == "__main__":
    mcp.run()
