"""MCP tool implementations — one async function per tool."""

from typing import Optional

from .container import get_services
from .formatters import ResponseFormatter

VALID_LOCALES = ["en", "es", "de"]
_LOCALES_STR = ", ".join(VALID_LOCALES)


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
    if from_locale not in VALID_LOCALES:
        return f"Error: Invalid source locale '{from_locale}'. Must be one of: {_LOCALES_STR}"
    if to_locale not in VALID_LOCALES:
        return f"Error: Invalid target locale '{to_locale}'. Must be one of: {_LOCALES_STR}"
    if from_locale == to_locale:
        return f"Source and target locales are the same: {term}"

    async with get_services() as (_, _, translator):
        translated = await translator.translate(term, from_locale, to_locale)
        if translated:
            return ResponseFormatter.format_translation(term, from_locale, translated, to_locale)
        return ResponseFormatter.format_translation_not_found(term, from_locale, to_locale)


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
    if locale and locale not in VALID_LOCALES:
        return f"Error: Invalid locale '{locale}'. Must be one of: {_LOCALES_STR}"

    limit = min(max(1, limit), 50)

    async with get_services() as (_, search, _):
        words = await search.search_by_term(term, locale=locale, limit=limit)
        return ResponseFormatter.format_search_results(words, term, locale)


async def get_all_translations(term: str, source_locale: str) -> str:
    """Get all available translations for a term from a specific source language.

    Args:
        term: The technical term to translate
        source_locale: Source language code (en, es, or de)

    Returns:
        All available translations of the term
    """
    if source_locale not in VALID_LOCALES:
        return f"Error: Invalid locale '{source_locale}'. Must be one of: {_LOCALES_STR}"

    async with get_services() as (_, search, _):
        word = await search.find_exact_match(term, source_locale)
        if not word:
            return f"Term '{term}' not found in {source_locale}"
        return ResponseFormatter.format_all_translations(word, source_locale)


async def get_term_details(word_id: int) -> str:
    """Get detailed information about a specific technical term by its ID.

    Args:
        word_id: The ID of the word to retrieve

    Returns:
        Detailed information including all translations
    """
    async with get_services() as (api, _, _):
        try:
            word = await api.fetch_word(word_id)
            return ResponseFormatter.format_word_details(word)
        except Exception as e:
            return f"Error retrieving word {word_id}: {str(e)}"


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
    page_size = min(max(1, page_size), 100)

    async with get_services() as (api, _, _):
        response = await api.fetch_words(per_page=page_size, cursor=cursor)
        return ResponseFormatter.format_word_list(response)
