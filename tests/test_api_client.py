"""Tests for API client."""

import pytest
import httpx
import respx
from techword_translator.services.api_client import APIClient


class TestAPIClientInitialization:
    """Tests for APIClient initialization."""

    def test_client_init_with_env_var(self, mock_env_vars):
        """Test client initialization with environment variable."""
        client = APIClient()
        assert client.base_url == "https://api.test.com"
        assert isinstance(client.client, httpx.AsyncClient)

    def test_client_init_with_explicit_url(self):
        """Test client initialization with explicit URL."""
        client = APIClient(base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"

    def test_client_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = APIClient(base_url="https://api.test.com/")
        assert client.base_url == "https://api.test.com"

    def test_client_init_without_url(self, monkeypatch):
        """Test that initialization fails without URL."""
        monkeypatch.delenv("TECHWORD_TRANSLATOR_API_URL", raising=False)
        with pytest.raises(ValueError, match="TECHWORD_TRANSLATOR_API_URL must be set"):
            APIClient()

    def test_client_has_correct_headers(self, mock_env_vars):
        """Test that client has correct default headers."""
        client = APIClient()
        headers = client.client.headers
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_client_has_timeout(self, mock_env_vars):
        """Test that client has timeout configured."""
        client = APIClient()
        assert client.client.timeout.read == 30.0


class TestAPIClientFetchWords:
    """Tests for fetch_words method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_success(self, api_client, mock_api_words_response):
        """Test successful fetch_words request."""
        # Mock the HTTP request
        route = respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=mock_api_words_response)
        )

        result = await api_client.fetch_words()

        assert route.called
        assert len(result.data) == 2
        assert result.data[0].english_word == "computer"
        assert result.data[1].english_word == "keyboard"
        assert result.meta.per_page == 10

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_with_pagination(self, api_client, mock_api_words_response):
        """Test fetch_words with pagination parameters."""
        route = respx.get(
            "https://api.test.com/api/v1/words", params={"per_page": 20, "cursor": "abc123"}
        ).mock(return_value=httpx.Response(200, json=mock_api_words_response))

        result = await api_client.fetch_words(per_page=20, cursor="abc123")

        assert route.called
        assert len(result.data) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_empty_results(self, api_client, mock_api_empty_response):
        """Test fetch_words with empty results."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=mock_api_empty_response)
        )

        result = await api_client.fetch_words()

        assert len(result.data) == 0
        assert result.meta.next_cursor is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_http_error(self, api_client):
        """Test fetch_words with HTTP error."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.fetch_words()

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_network_error(self, api_client):
        """Test fetch_words with network error."""
        respx.get("https://api.test.com/api/v1/words").mock(side_effect=httpx.ConnectError)

        with pytest.raises(httpx.ConnectError):
            await api_client.fetch_words()

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_timeout(self, api_client):
        """Test fetch_words with timeout."""
        respx.get("https://api.test.com/api/v1/words").mock(side_effect=httpx.TimeoutException)

        with pytest.raises(httpx.TimeoutException):
            await api_client.fetch_words()

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_default_per_page(self, api_client, mock_api_words_response):
        """Test fetch_words uses default per_page value."""
        route = respx.get(
            "https://api.test.com/api/v1/words", params={"per_page": 15}
        ).mock(return_value=httpx.Response(200, json=mock_api_words_response))

        await api_client.fetch_words()

        assert route.called


class TestAPIClientFetchWord:
    """Tests for fetch_word method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_word_success(self, api_client, mock_api_word_response):
        """Test successful fetch_word request."""
        route = respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(200, json=mock_api_word_response)
        )

        result = await api_client.fetch_word(1)

        assert route.called
        assert result.id == 1
        assert result.english_word == "computer"
        assert result.translation is not None
        assert result.translation.spanish_word == "computadora"

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_word_not_found(self, api_client):
        """Test fetch_word with non-existent word."""
        respx.get("https://api.test.com/api/v1/words/999").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.fetch_word(999)

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_word_without_translation(self, api_client):
        """Test fetch_word for word without translation."""
        response_data = {
            "id": 2,
            "english_word": "keyboard",
            "translation": None,
        }
        respx.get("https://api.test.com/api/v1/words/2").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        result = await api_client.fetch_word(2)

        assert result.id == 2
        assert result.english_word == "keyboard"
        assert result.translation is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_word_http_error(self, api_client):
        """Test fetch_word with HTTP error."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.fetch_word(1)


class TestAPIClientFetchTranslation:
    """Tests for fetch_translation method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_translation_success(self, api_client, mock_api_translation_response):
        """Test successful fetch_translation request."""
        route = respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(200, json=mock_api_translation_response)
        )

        result = await api_client.fetch_translation(1)

        assert route.called
        assert result is not None
        assert result.id == 1
        assert result.word_id == 1
        assert result.spanish_word == "computadora"
        assert result.german_word == "Computer"

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_translation_not_found(self, api_client):
        """Test fetch_translation returns None when not found."""
        respx.get("https://api.test.com/api/v1/translations/999").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        result = await api_client.fetch_translation(999)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_translation_http_error(self, api_client):
        """Test fetch_translation returns None on HTTP error."""
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        result = await api_client.fetch_translation(1)

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_translation_network_error(self, api_client):
        """Test fetch_translation returns None on network error."""
        respx.get("https://api.test.com/api/v1/translations/1").mock(
            side_effect=httpx.ConnectError
        )

        result = await api_client.fetch_translation(1)

        assert result is None


class TestAPIClientContextManager:
    """Tests for async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_env_vars):
        """Test using client as async context manager."""
        async with APIClient() as client:
            assert client.base_url == "https://api.test.com"
            assert not client.client.is_closed

        # Client should be closed after context
        assert client.client.is_closed

    @pytest.mark.asyncio
    @respx.mock
    async def test_context_manager_with_request(self, mock_env_vars, mock_api_word_response):
        """Test making request within context manager."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(200, json=mock_api_word_response)
        )

        async with APIClient() as client:
            result = await client.fetch_word(1)
            assert result.english_word == "computer"

    @pytest.mark.asyncio
    async def test_manual_close(self, mock_env_vars):
        """Test manually closing client."""
        client = APIClient()
        assert not client.client.is_closed

        await client.close()
        assert client.client.is_closed

    @pytest.mark.asyncio
    @respx.mock
    async def test_context_manager_with_exception(self, mock_env_vars):
        """Test context manager closes client even with exception."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(500, json={"error": "Error"})
        )

        try:
            async with APIClient() as client:
                await client.fetch_word(1)
        except httpx.HTTPStatusError:
            pass

        assert client.client.is_closed


class TestAPIClientEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_with_missing_links(self, api_client):
        """Test fetch_words handles missing links gracefully."""
        response_data = {
            "data": [],
            # Missing "links" key
            "meta": {
                "path": "/api/v1/words",
                "per_page": 10,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        result = await api_client.fetch_words()

        assert result.links == {}
        assert len(result.data) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_large_per_page(self, api_client, mock_api_words_response):
        """Test fetch_words with large per_page value."""
        route = respx.get(
            "https://api.test.com/api/v1/words", params={"per_page": 100}
        ).mock(return_value=httpx.Response(200, json=mock_api_words_response))

        result = await api_client.fetch_words(per_page=100)

        assert route.called
        assert len(result.data) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_multiple_sequential_requests(self, api_client, mock_api_word_response):
        """Test making multiple sequential requests."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(200, json=mock_api_word_response)
        )

        # Make multiple requests
        result1 = await api_client.fetch_word(1)
        result2 = await api_client.fetch_word(1)

        assert result1.english_word == "computer"
        assert result2.english_word == "computer"
