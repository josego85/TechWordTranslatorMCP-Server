"""Integration tests for MCP Server tools."""

import pytest
import respx
import httpx
from unittest.mock import AsyncMock, patch

from techword_translator.server import (
    translate_term,
    search_tech_terms,
    get_all_translations,
    get_term_details,
    list_tech_terms,
)


class TestTranslateTermTool:
    """Integration tests for translate_term tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_term_success(self, mock_env_vars):
        """Test successful translation."""
        # Mock API responses
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "computadora",
                        "german_word": "Computer",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )

        result = await translate_term("computer", "en", "es")

        assert "computer (en) → computadora (es)" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_term_not_found(self, mock_env_vars):
        """Test translation when term not found."""
        empty_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=empty_response)
        )

        result = await translate_term("nonexistent", "en", "es")

        assert "Translation not found" in result
        assert "nonexistent" in result

    @pytest.mark.asyncio
    async def test_translate_term_invalid_source_locale(self, mock_env_vars):
        """Test translation with invalid source locale."""
        result = await translate_term("test", "fr", "es")

        assert "Error: Invalid source locale 'fr'" in result

    @pytest.mark.asyncio
    async def test_translate_term_invalid_target_locale(self, mock_env_vars):
        """Test translation with invalid target locale."""
        result = await translate_term("test", "en", "fr")

        assert "Error: Invalid target locale 'fr'" in result

    @pytest.mark.asyncio
    async def test_translate_term_same_locale(self, mock_env_vars):
        """Test translation when source and target are the same."""
        result = await translate_term("computer", "en", "en")

        assert "Source and target locales are the same" in result
        assert "computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_translate_term_all_directions(self, mock_env_vars):
        """Test translation in different directions."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "computadora",
                        "german_word": "Computer",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )

        # English to German
        result = await translate_term("computer", "en", "de")
        assert "computer (en) → Computer (de)" in result


class TestSearchTechTermsTool:
    """Integration tests for search_tech_terms tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_tech_terms_success(self, mock_env_vars):
        """Test successful search."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "computadora",
                        "german_word": "Computer",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )

        result = await search_tech_terms("computer")

        assert "Found 1 result(s)" in result
        assert "computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_tech_terms_no_results(self, mock_env_vars):
        """Test search with no results."""
        empty_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=empty_response)
        )

        result = await search_tech_terms("nonexistent")

        assert "No results found" in result
        assert "nonexistent" in result

    @pytest.mark.asyncio
    async def test_search_tech_terms_invalid_locale(self, mock_env_vars):
        """Test search with invalid locale."""
        result = await search_tech_terms("test", locale="fr")

        assert "Error: Invalid locale 'fr'" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_tech_terms_with_locale(self, mock_env_vars):
        """Test search with specific locale."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "computadora",
                        "german_word": "Computer",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )

        result = await search_tech_terms("computadora", locale="es")

        assert "Found 1 result(s)" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_tech_terms_limit_validation(self, mock_env_vars):
        """Test search with limit validation."""
        words_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )

        # Test with limit too high (should cap at 50)
        result = await search_tech_terms("test", limit=1000)
        assert "No results found" in result

        # Test with limit too low (should use 1)
        result = await search_tech_terms("test", limit=-5)
        assert "No results found" in result


class TestGetAllTranslationsTool:
    """Integration tests for get_all_translations tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_all_translations_success(self, mock_env_vars):
        """Test getting all translations."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "computadora",
                        "german_word": "Computer",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
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
        empty_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=empty_response)
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
        """Test getting term details."""
        word_response = {
            "id": 1,
            "english_word": "computer",
            "translation": {
                "id": 1,
                "word_id": 1,
                "spanish_word": "computadora",
                "german_word": "Computer",
            },
        }

        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(200, json=word_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )

        result = await get_term_details(1)

        assert "Word ID: 1" in result
        assert "Translations:" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_term_details_not_found(self, mock_env_vars):
        """Test getting term details when not found."""
        respx.get("https://api.test.com/api/v1/words/999").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        result = await get_term_details(999)

        assert "Error retrieving word 999" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_term_details_with_missing_translation(self, mock_env_vars):
        """Test getting term details when translation is missing."""
        word_response = {
            "id": 2,
            "english_word": "keyboard",
            "translation": None,
        }

        respx.get("https://api.test.com/api/v1/words/2").mock(
            return_value=httpx.Response(200, json=word_response)
        )
        respx.get("https://api.test.com/api/v1/translations/2").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        result = await get_term_details(2)

        assert "Word ID: 2" in result
        assert "English: keyboard" in result


class TestListTechTermsTool:
    """Integration tests for list_tech_terms tool."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_tech_terms_success(self, mock_env_vars):
        """Test listing tech terms."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "computer",
                    "translation": None,
                },
                {
                    "id": 2,
                    "english_word": "keyboard",
                    "translation": None,
                },
            ],
            "links": {"next": "cursor123", "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 15,
                "next_cursor": "cursor123",
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "computadora",
                    "german_word": "Computer",
                },
            )
        )
        respx.get("https://api.test.com/api/v1/translations/2").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 2,
                    "word_id": 2,
                    "spanish_word": "teclado",
                    "german_word": "Tastatur",
                },
            )
        )

        result = await list_tech_terms()

        assert "Showing 2 terms:" in result
        assert "[ID: 1]" in result
        assert "[ID: 2]" in result
        assert "computer" in result
        assert "keyboard" in result
        assert "Next cursor: cursor123" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_tech_terms_empty(self, mock_env_vars):
        """Test listing when no terms available."""
        empty_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 15,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=empty_response)
        )

        result = await list_tech_terms()

        assert "No terms found" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_tech_terms_with_cursor(self, mock_env_vars):
        """Test listing with pagination cursor."""
        words_response = {
            "data": [
                {
                    "id": 3,
                    "english_word": "mouse",
                    "translation": None,
                }
            ],
            "links": {"next": None, "prev": "cursor123"},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 15,
                "next_cursor": None,
                "prev_cursor": "cursor123",
            },
        }

        respx.get("https://api.test.com/api/v1/words", params={"per_page": 15, "cursor": "abc"}).mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/3").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 3,
                    "word_id": 3,
                    "spanish_word": "ratón",
                    "german_word": "Maus",
                },
            )
        )

        result = await list_tech_terms(cursor="abc")

        assert "Showing 1 terms:" in result
        assert "Previous cursor: cursor123" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_tech_terms_page_size_validation(self, mock_env_vars):
        """Test list with page size validation."""
        empty_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 100,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=empty_response)
        )

        # Test with page size too high (should cap at 100)
        result = await list_tech_terms(page_size=1000)
        assert "No terms found" in result

        # Test with page size too low (should use 1)
        result = await list_tech_terms(page_size=-5)
        assert "No terms found" in result


class TestServerIntegrationEdgeCases:
    """Integration tests for edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_service_reuse(self, mock_env_vars):
        """Test that services are reused across calls."""
        words_response = {
            "data": [],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )

        # Make multiple calls
        await search_tech_terms("test1")
        await search_tech_terms("test2")

        # Services should be reused (not creating new instances each time)
        # This is tested implicitly by not getting initialization errors

    @pytest.mark.asyncio
    @respx.mock
    async def test_unicode_handling(self, mock_env_vars):
        """Test handling of unicode characters."""
        words_response = {
            "data": [
                {
                    "id": 1,
                    "english_word": "mouse",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "ratón",
                        "german_word": "Maus",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 50,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }

        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=words_response)
        )
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "word_id": 1,
                    "spanish_word": "ratón",
                    "german_word": "Maus",
                },
            )
        )

        result = await search_tech_terms("ratón")

        assert "ratón" in result
