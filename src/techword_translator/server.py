"""FastMCP Server for TechWordTranslator API.

Refactored following SOLID principles:
- Single Responsibility: Each module has one job
- Open/Closed: Easy to extend without modifying
- Liskov Substitution: Services can be swapped
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions
"""

import os
from typing import Optional
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .services import APIClient, SearchService, TranslatorService
from .formatters import ResponseFormatter

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(name=os.getenv("MCP_SERVER_NAME", "TechWord Translator"))

# Global service instances
_api_client: Optional[APIClient] = None
_search_service: Optional[SearchService] = None
_translator_service: Optional[TranslatorService] = None


@asynccontextmanager
async def get_services():
    """Get or create service instances.

    Yields:
        Tuple of (api_client, search_service, translator_service)
    """
    global _api_client, _search_service, _translator_service

    if _api_client is None:
        _api_client = APIClient()
        _search_service = SearchService(_api_client)
        _translator_service = TranslatorService(_search_service)

    try:
        yield _api_client, _search_service, _translator_service
    finally:
        pass  # Keep services alive for reuse


# ============================================================================
# MCP Tools - Each tool has ONE responsibility
# ============================================================================


@mcp.tool()
async def translate_term(term: str, from_locale: str, to_locale: str) -> str:
    """Translate a technical term from one language to another.

    Supported languages:
    - en: English
    - es: Spanish (Español)
    - de: German (Deutsch)

    Args:
        term: The technical term to translate
        from_locale: Source language code (en, es, or de)
        to_locale: Target language code (en, es, or de)

    Returns:
        The translated term or error message
    """
    # Validate inputs
    valid_locales = ["en", "es", "de"]
    if from_locale not in valid_locales:
        return f"Error: Invalid source locale '{from_locale}'. Must be one of: {', '.join(valid_locales)}"
    if to_locale not in valid_locales:
        return f"Error: Invalid target locale '{to_locale}'. Must be one of: {', '.join(valid_locales)}"
    if from_locale == to_locale:
        return f"Source and target locales are the same: {term}"

    # Translate
    async with get_services() as (api, search, translator):
        translated = await translator.translate(term, from_locale, to_locale)

        if translated:
            return ResponseFormatter.format_translation(term, from_locale, translated, to_locale)
        else:
            return ResponseFormatter.format_translation_not_found(term, from_locale, to_locale)


@mcp.tool()
async def search_tech_terms(
    term: str,
    locale: Optional[str] = None,
    limit: int = 10,
) -> str:
    """Search for technical terms in the database.

    Args:
        term: The term to search for (case-insensitive partial match)
        locale: Optional language to search in (en, es, or de)
        limit: Maximum number of results (default: 10, max: 50)

    Returns:
        Formatted list of matching terms with all their translations
    """
    # Validate inputs
    if locale:
        valid_locales = ["en", "es", "de"]
        if locale not in valid_locales:
            return f"Error: Invalid locale '{locale}'. Must be one of: {', '.join(valid_locales)}"

    limit = min(max(1, limit), 50)

    # Search
    async with get_services() as (api, search, translator):
        words = await search.search_by_term(term, locale=locale, limit=limit)
        return ResponseFormatter.format_search_results(words, term, locale)


@mcp.tool()
async def get_all_translations(term: str, source_locale: str) -> str:
    """Get all available translations for a term from a specific source language.

    Args:
        term: The technical term to translate
        source_locale: Source language code (en, es, or de)

    Returns:
        All available translations of the term
    """
    # Validate input
    valid_locales = ["en", "es", "de"]
    if source_locale not in valid_locales:
        return f"Error: Invalid locale '{source_locale}'. Must be one of: {', '.join(valid_locales)}"

    # Find word
    async with get_services() as (api, search, translator):
        word = await search.find_exact_match(term, source_locale)

        if not word:
            return f"Term '{term}' not found in {source_locale}"

        return ResponseFormatter.format_all_translations(word, source_locale)


@mcp.tool()
async def get_term_details(word_id: int) -> str:
    """Get detailed information about a specific technical term by its ID.

    Args:
        word_id: The ID of the word to retrieve

    Returns:
        Detailed information including all translations
    """
    async with get_services() as (api, search, translator):
        try:
            word = await api.fetch_word(word_id)
            word.translation = await api.fetch_translation(word_id)
            return ResponseFormatter.format_word_details(word)
        except Exception as e:
            return f"Error retrieving word {word_id}: {str(e)}"


@mcp.tool()
async def list_tech_terms(
    page_size: int = 15,
    cursor: Optional[str] = None,
) -> str:
    """List technical terms with pagination.

    Args:
        page_size: Number of terms per page (default: 15, max: 100)
        cursor: Pagination cursor for next/previous page

    Returns:
        Formatted list of terms with pagination information
    """
    # Validate input
    page_size = min(max(1, page_size), 100)

    # Fetch and format
    async with get_services() as (api, search, translator):
        response = await api.fetch_words(per_page=page_size, cursor=cursor)

        # Load translations for all words
        for word in response.data:
            word.translation = await api.fetch_translation(word.id)

        return ResponseFormatter.format_word_list(response)


if __name__ == "__main__":
    mcp.run()
