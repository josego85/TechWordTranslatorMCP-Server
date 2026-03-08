"""Integration tests for MCP Server tools."""

import pytest
import respx
import httpx

from techword_translator.server import (
    translate_term,
    search_tech_terms,
    get_all_translations,
    get_term_details,
    list_tech_terms,
)


def _word_response(id: int, word: str, en: str, es: str, de: str) -> dict:
    """Build a word dict matching the actual API response format."""
    return {
        "id": id,
        "word": word,
        "translations": [
            {"language": "en", "translation": en},
            {"language": "es", "translation": es},
            {"language": "de", "translation": de},
        ],
    }


def _words_page(words: list, next_cursor: str = None) -> dict:
    """Build a paginated words response."""
    return {
        "data": words,
        "links": {"next": next_cursor, "prev": None},
        "meta": {
            "path": "/api/v1/words",
            "per_page": 50,
            "next_cursor": next_cursor,
            "prev_cursor": None,
        },
    }


COMPUTER = _word_response(1, "computer", "computer", "computadora", "Computer")
KEYBOARD = _word_response(2, "keyboard", "keyboard", "teclado", "Tastatur")
MOUSE = _word_response(3, "mouse", "mouse", "ratón", "Maus")


class TestTranslateTermTool:
    """Integration tests for translate_term tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_success(self, mock_env_vars):
        """Test successful translation."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([COMPUTER]))
        )

        result = await translate_term("computer", "en", "es")
        assert "computer (en) → computadora (es)" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_to_german(self, mock_env_vars):
        """Test translation to German."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([COMPUTER]))
        )

        result = await translate_term("computer", "en", "de")
        assert "computer (en) → Computer (de)" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_not_found(self, mock_env_vars):
        """Test translation when term not found."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        result = await translate_term("nonexistent", "en", "es")
        assert "Translation not found" in result
        assert "nonexistent" in result

    @pytest.mark.asyncio
    async def test_translate_invalid_source_locale(self, mock_env_vars):
        """Test translation with invalid source locale."""
        result = await translate_term("test", "fr", "es")
        assert "Error: Invalid source locale 'fr'" in result

    @pytest.mark.asyncio
    async def test_translate_invalid_target_locale(self, mock_env_vars):
        """Test translation with invalid target locale."""
        result = await translate_term("test", "en", "fr")
        assert "Error: Invalid target locale 'fr'" in result

    @pytest.mark.asyncio
    async def test_translate_same_locale(self, mock_env_vars):
        """Test translation when source and target are the same."""
        result = await translate_term("computer", "en", "en")
        assert "Source and target locales are the same" in result
        assert "computer" in result


class TestSearchTechTermsTool:
    """Integration tests for search_tech_terms tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_success(self, mock_env_vars):
        """Test successful search."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([COMPUTER]))
        )

        result = await search_tech_terms("computer")
        assert "Found 1 result(s)" in result
        assert "computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_no_results(self, mock_env_vars):
        """Test search with no results."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        result = await search_tech_terms("nonexistent")
        assert "No results found" in result

    @pytest.mark.asyncio
    async def test_search_invalid_locale(self, mock_env_vars):
        """Test search with invalid locale."""
        result = await search_tech_terms("test", locale="fr")
        assert "Error: Invalid locale 'fr'" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_by_spanish_term(self, mock_env_vars):
        """Test searching by Spanish term."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([COMPUTER]))
        )

        result = await search_tech_terms("computadora", locale="es")
        assert "Found 1 result(s)" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_limit_validation(self, mock_env_vars):
        """Test search with out-of-range limit values."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        assert "No results found" in await search_tech_terms("test", limit=1000)
        assert "No results found" in await search_tech_terms("test", limit=-5)


class TestGetAllTranslationsTool:
    """Integration tests for get_all_translations tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_all_translations_success(self, mock_env_vars):
        """Test getting all translations."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([COMPUTER]))
        )

        result = await get_all_translations("computer", "en")
        assert "Translations for 'computer':" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_all_translations_not_found(self, mock_env_vars):
        """Test get all translations when term not found."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        result = await get_all_translations("nonexistent", "en")
        assert "Term 'nonexistent' not found in en" in result

    @pytest.mark.asyncio
    async def test_get_all_translations_invalid_locale(self, mock_env_vars):
        """Test get all translations with invalid locale."""
        result = await get_all_translations("test", "fr")
        assert "Error: Invalid locale 'fr'" in result


class TestGetTermDetailsTool:
    """Integration tests for get_term_details tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_term_details_success(self, mock_env_vars):
        """Test getting term details by ID."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(200, json=COMPUTER)
        )

        result = await get_term_details(1)
        assert "Word ID: 1" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_term_details_not_found(self, mock_env_vars):
        """Test getting term details when ID does not exist."""
        respx.get("https://api.test.com/api/v1/words/999").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        result = await get_term_details(999)
        assert "Error retrieving word 999" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_term_details_no_translations(self, mock_env_vars):
        """Test getting term details for word with no translations."""
        word = {"id": 2, "word": "keyboard", "translations": []}
        respx.get("https://api.test.com/api/v1/words/2").mock(
            return_value=httpx.Response(200, json=word)
        )

        result = await get_term_details(2)
        assert "Word ID: 2" in result


class TestListTechTermsTool:
    """Integration tests for list_tech_terms tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_success(self, mock_env_vars):
        """Test listing tech terms."""
        response = _words_page([COMPUTER, KEYBOARD], next_cursor="cursor123")
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=response)
        )

        result = await list_tech_terms()
        assert "Showing 2 terms:" in result
        assert "[ID: 1]" in result
        assert "[ID: 2]" in result
        assert "Next cursor: cursor123" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_empty(self, mock_env_vars):
        """Test listing when no terms available."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        result = await list_tech_terms()
        assert "No terms found" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_with_cursor(self, mock_env_vars):
        """Test listing with pagination cursor."""
        response = {
            "data": [MOUSE],
            "links": {"next": None, "prev": "cursor123"},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 15,
                "next_cursor": None,
                "prev_cursor": "cursor123",
            },
        }
        respx.get(
            "https://api.test.com/api/v1/words", params={"per_page": 15, "cursor": "abc"}
        ).mock(return_value=httpx.Response(200, json=response))

        result = await list_tech_terms(cursor="abc")
        assert "Showing 1 terms:" in result
        assert "Previous cursor: cursor123" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_page_size_validation(self, mock_env_vars):
        """Test list with page size clamping."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        assert "No terms found" in await list_tech_terms(page_size=1000)
        assert "No terms found" in await list_tech_terms(page_size=-5)


class TestServerIntegrationEdgeCases:
    """Integration tests for edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_service_reuse(self, mock_env_vars):
        """Test that services are reused across calls without errors."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([]))
        )

        await search_tech_terms("test1")
        await search_tech_terms("test2")

    @pytest.mark.asyncio
    @respx.mock
    async def test_unicode_handling(self, mock_env_vars):
        """Test handling of unicode characters."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=_words_page([MOUSE]))
        )

        result = await search_tech_terms("ratón")
        assert "ratón" in result
