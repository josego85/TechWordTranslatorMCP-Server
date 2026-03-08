"""Pytest configuration and fixtures for testing."""

import pytest
from unittest.mock import AsyncMock
from techword_translator.models.word import Word, TranslationItem
from techword_translator.models.api import WordsResponse, PaginationMeta


@pytest.fixture(autouse=True)
def reset_service_container():
    """Reset global service instances between tests to avoid state leakage."""
    import techword_translator.container as container
    container._api_client = None
    container._search_service = None
    container._translator_service = None
    yield
    container._api_client = None
    container._search_service = None
    container._translator_service = None


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("TECHWORD_TRANSLATOR_API_URL", "https://api.test.com")
    monkeypatch.setenv("MCP_SERVER_NAME", "Test Server")


@pytest.fixture
def sample_word_with_translation():
    """Create a sample Word with all translations."""
    return Word(
        id=1,
        word="computer",
        translations=[
            TranslationItem(language="en", translation="computer"),
            TranslationItem(language="es", translation="computadora"),
            TranslationItem(language="de", translation="Computer"),
        ],
    )


@pytest.fixture
def sample_word_without_translation():
    """Create a sample Word with English only."""
    return Word(
        id=2,
        word="keyboard",
        translations=[
            TranslationItem(language="en", translation="keyboard"),
        ],
    )


@pytest.fixture
def sample_words_list():
    """Create a list of sample words."""
    return [
        Word(
            id=1,
            word="computer",
            translations=[
                TranslationItem(language="en", translation="computer"),
                TranslationItem(language="es", translation="computadora"),
                TranslationItem(language="de", translation="Computer"),
            ],
        ),
        Word(
            id=2,
            word="keyboard",
            translations=[
                TranslationItem(language="en", translation="keyboard"),
                TranslationItem(language="es", translation="teclado"),
                TranslationItem(language="de", translation="Tastatur"),
            ],
        ),
        Word(
            id=3,
            word="mouse",
            translations=[
                TranslationItem(language="en", translation="mouse"),
                TranslationItem(language="es", translation="ratón"),
                TranslationItem(language="de", translation="Maus"),
            ],
        ),
    ]


@pytest.fixture
def sample_pagination_meta():
    """Create sample pagination metadata."""
    return PaginationMeta(
        path="/api/v1/words",
        per_page=10,
        next_cursor="cursor123",
        prev_cursor=None,
    )


@pytest.fixture
def sample_words_response(sample_words_list, sample_pagination_meta):
    """Create a sample WordsResponse."""
    return WordsResponse(
        data=sample_words_list,
        links={
            "next": "https://api.test.com/api/v1/words?cursor=cursor123",
            "prev": None,
        },
        meta=sample_pagination_meta,
    )


@pytest.fixture
def mock_api_client(mock_env_vars):
    """Create a mock API client."""
    from techword_translator.services.api_client import APIClient

    client = AsyncMock(spec=APIClient)
    client.base_url = "https://api.test.com"
    return client


@pytest.fixture
def api_client(mock_env_vars):
    """Create a real API client for testing (with mocked HTTP)."""
    from techword_translator.services.api_client import APIClient

    return APIClient()


@pytest.fixture
def mock_search_service():
    """Create a mock SearchService."""
    from techword_translator.services.search import SearchService

    return AsyncMock(spec=SearchService)


@pytest.fixture
def search_service(api_client):
    """Create a real SearchService for testing."""
    from techword_translator.services.search import SearchService

    return SearchService(api_client)


@pytest.fixture
def mock_translator_service():
    """Create a mock TranslatorService."""
    from techword_translator.services.translator import TranslatorService

    return AsyncMock(spec=TranslatorService)


@pytest.fixture
def translator_service(search_service):
    """Create a real TranslatorService for testing."""
    from techword_translator.services.translator import TranslatorService

    return TranslatorService(search_service)


@pytest.fixture
def response_formatter():
    """Create a ResponseFormatter instance."""
    from techword_translator.formatters import ResponseFormatter

    return ResponseFormatter()


# API Response Mocks — match the actual API response format
@pytest.fixture
def mock_api_words_response():
    """Mock API response for /api/v1/words endpoint."""
    return {
        "data": [
            {
                "id": 1,
                "word": "computer",
                "translations": [
                    {"language": "en", "translation": "computer"},
                    {"language": "es", "translation": "computadora"},
                    {"language": "de", "translation": "Computer"},
                ],
            },
            {
                "id": 2,
                "word": "keyboard",
                "translations": [
                    {"language": "en", "translation": "keyboard"},
                    {"language": "es", "translation": "teclado"},
                    {"language": "de", "translation": "Tastatur"},
                ],
            },
        ],
        "links": {
            "next": "https://api.test.com/api/v1/words?cursor=cursor123",
            "prev": None,
        },
        "meta": {
            "path": "/api/v1/words",
            "per_page": 10,
            "next_cursor": "cursor123",
            "prev_cursor": None,
        },
    }


@pytest.fixture
def mock_api_word_response():
    """Mock API response for /api/v1/words/{id} endpoint."""
    return {
        "id": 1,
        "word": "computer",
        "translations": [
            {"language": "en", "translation": "computer"},
            {"language": "es", "translation": "computadora"},
            {"language": "de", "translation": "Computer"},
        ],
    }


@pytest.fixture
def mock_api_empty_response():
    """Mock empty API response."""
    return {
        "data": [],
        "links": {"next": None, "prev": None},
        "meta": {
            "path": "/api/v1/words",
            "per_page": 10,
            "next_cursor": None,
            "prev_cursor": None,
        },
    }
