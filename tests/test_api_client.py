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

    def test_client_without_token_has_empty_auth_headers(self, mock_env_vars, monkeypatch):
        """Test that _auth_headers is empty when TECHWORD_API_TOKEN is not set."""
        monkeypatch.delenv("TECHWORD_API_TOKEN", raising=False)
        client = APIClient()
        assert client._auth_headers == {}

    def test_client_with_token_sets_auth_headers(self, mock_env_vars, monkeypatch):
        """Test that _auth_headers contains Authorization when TECHWORD_API_TOKEN is set."""
        monkeypatch.setenv("TECHWORD_API_TOKEN", "1|testtoken123")
        client = APIClient()
        assert client._auth_headers == {"Authorization": "Bearer 1|testtoken123"}

    def test_public_client_headers_never_contain_authorization(self, mock_env_vars, monkeypatch):
        """Test that shared client headers never carry Authorization regardless of token."""
        monkeypatch.setenv("TECHWORD_API_TOKEN", "1|testtoken123")
        client = APIClient()
        assert "authorization" not in client.client.headers

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
        route = respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=mock_api_words_response)
        )

        result = await api_client.fetch_words()

        assert route.called
        assert len(result.data) == 2
        assert result.data[0].word == "computer"
        assert result.data[1].word == "keyboard"
        assert result.meta.per_page == 10

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_translations_embedded(self, api_client, mock_api_words_response):
        """Test that translations are embedded in each word."""
        respx.get("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(200, json=mock_api_words_response)
        )

        result = await api_client.fetch_words()

        word = result.data[0]
        assert word.get_translation("en") == "computer"
        assert word.get_translation("es") == "computadora"
        assert word.get_translation("de") == "Computer"

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
        assert result.word == "computer"
        assert result.get_translation("es") == "computadora"
        assert result.get_translation("de") == "Computer"

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
    async def test_fetch_word_no_translations(self, api_client):
        """Test fetch_word for word with no translations."""
        response_data = {
            "id": 2,
            "word": "keyboard",
            "translations": [],
        }
        respx.get("https://api.test.com/api/v1/words/2").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        result = await api_client.fetch_word(2)

        assert result.id == 2
        assert result.word == "keyboard"
        assert result.translations == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_word_http_error(self, api_client):
        """Test fetch_word with HTTP error."""
        respx.get("https://api.test.com/api/v1/words/1").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.fetch_word(1)


class TestAPIClientContextManager:
    """Tests for async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_env_vars):
        """Test using client as async context manager."""
        async with APIClient() as client:
            assert client.base_url == "https://api.test.com"
            assert not client.client.is_closed

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
            assert result.word == "computer"

    @pytest.mark.asyncio
    async def test_manual_close(self, mock_env_vars):
        """Test manually closing client."""
        client = APIClient()
        assert not client.client.is_closed

        await client.close()
        assert client.client.is_closed


class TestAPIClientEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_words_with_missing_links(self, api_client):
        """Test fetch_words handles missing links gracefully."""
        response_data = {
            "data": [],
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

        result1 = await api_client.fetch_word(1)
        result2 = await api_client.fetch_word(1)

        assert result1.word == "computer"
        assert result2.word == "computer"


class TestAPIClientCreateWord:
    """Tests for create_word method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_word_success(self, api_client):
        """Test successful word creation."""
        response_data = {"id": 10, "word": "algorithm", "translations": []}
        route = respx.post("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(201, json=response_data)
        )

        result = await api_client.create_word("algorithm")

        assert route.called
        assert result.id == 10
        assert result.word == "algorithm"
        assert result.translations == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_word_conflict(self, api_client):
        """Test create_word raises on 422 validation error."""
        respx.post("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(422, json={"errors": {"english_word": ["The english word has already been taken."]}})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.create_word("algorithm")

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_word_unauthorized(self, api_client):
        """Test create_word raises on 401 when no valid token."""
        respx.post("https://api.test.com/api/v1/words").mock(
            return_value=httpx.Response(401, json={"message": "Unauthenticated."})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.create_word("algorithm")


class TestAPIClientCreateTranslation:
    """Tests for create_translation method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_translation_success(self, api_client):
        """Test successful translation creation."""
        response_data = {"id": 20, "word_id": 10, "language": "es", "translation": "algoritmo"}
        route = respx.post("https://api.test.com/api/v1/translations").mock(
            return_value=httpx.Response(201, json=response_data)
        )

        result = await api_client.create_translation(10, "es", "algoritmo")

        assert route.called
        assert result["id"] == 20
        assert result["language"] == "es"
        assert result["translation"] == "algoritmo"

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_translation_invalid_word_id(self, api_client):
        """Test create_translation raises on 422 when word_id does not exist."""
        respx.post("https://api.test.com/api/v1/translations").mock(
            return_value=httpx.Response(422, json={"errors": {"word_id": ["The selected word id is invalid."]}})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.create_translation(9999, "es", "algoritmo")
