"""Pytest configuration and fixtures for testing."""

import os
import pytest
from unittest.mock import AsyncMock
from techword_translator.models.word import Word, Translation
from techword_translator.models.api import WordsResponse, PaginationMeta


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("TECHWORD_TRANSLATOR_API_URL", "https://api.test.com")
    monkeypatch.setenv("MCP_SERVER_NAME", "Test Server")
    monkeypatch.setenv("MCP_SERVER_VERSION", "1.0.0-test")


@pytest.fixture
def sample_translation():
    """Create a sample translation with all languages."""
    return Translation(
        id=1,
        word_id=1,
        spanish_word="computadora",
        german_word="Computer",
    )


@pytest.fixture
def sample_translation_keyboard():
    """Create a sample translation for keyboard."""
    return Translation(
        id=2,
        word_id=2,
        spanish_word="teclado",
        german_word="Tastatur",
    )


@pytest.fixture
def sample_translation_mouse():
    """Create a sample translation for mouse."""
    return Translation(
        id=3,
        word_id=3,
        spanish_word="ratón",
        german_word="Maus",
    )


@pytest.fixture
def sample_word_with_translation():
    """Create a sample Word with translation."""
    return Word(
        id=1,
        english_word="computer",
        translation=Translation(
            id=1,
            word_id=1,
            spanish_word="computadora",
            german_word="Computer",
        ),
    )


@pytest.fixture
def sample_word_without_translation():
    """Create a sample Word without translation."""
    return Word(
        id=2,
        english_word="keyboard",
        translation=None,
    )


@pytest.fixture
def sample_words_list():
    """Create a list of sample words."""
    return [
        Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        ),
        Word(
            id=2,
            english_word="keyboard",
            translation=Translation(
                id=2, word_id=2, spanish_word="teclado", german_word="Tastatur"
            ),
        ),
        Word(
            id=3,
            english_word="mouse",
            translation=Translation(id=3, word_id=3, spanish_word="ratón", german_word="Maus"),
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
        next_page_url="https://api.test.com/api/v1/words?cursor=cursor123",
        prev_page_url=None,
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
def mock_search_service(mock_api_client):
    """Create a mock SearchService."""
    from techword_translator.services.search import SearchService

    service = AsyncMock(spec=SearchService)
    service.api_client = mock_api_client
    return service


@pytest.fixture
def search_service(api_client):
    """Create a real SearchService for testing."""
    from techword_translator.services.search import SearchService

    return SearchService(api_client)


@pytest.fixture
def mock_translator_service(mock_search_service):
    """Create a mock TranslatorService."""
    from techword_translator.services.translator import TranslatorService

    service = AsyncMock(spec=TranslatorService)
    service.search_service = mock_search_service
    return service


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


# API Response Mocks
@pytest.fixture
def mock_api_words_response():
    """Mock API response for /api/v1/words endpoint."""
    return {
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
            },
            {
                "id": 2,
                "english_word": "keyboard",
                "translation": {
                    "id": 2,
                    "word_id": 2,
                    "spanish_word": "teclado",
                    "german_word": "Tastatur",
                },
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
            "next_url": "https://api.test.com/api/v1/words?cursor=cursor123",
            "prev_url": None,
        },
    }


@pytest.fixture
def mock_api_word_response():
    """Mock API response for /api/v1/words/{id} endpoint."""
    return {
        "id": 1,
        "english_word": "computer",
        "translation": {
            "id": 1,
            "word_id": 1,
            "spanish_word": "computadora",
            "german_word": "Computer",
        },
    }


@pytest.fixture
def mock_api_translation_response():
    """Mock API response for /api/v1/words/{id}/translation endpoint."""
    return {
        "id": 1,
        "word_id": 1,
        "spanish_word": "computadora",
        "german_word": "Computer",
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
            "next_url": None,
            "prev_url": None,
        },
    }
