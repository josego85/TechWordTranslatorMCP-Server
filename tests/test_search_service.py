"""Tests for SearchService."""

import pytest
from unittest.mock import AsyncMock

from techword_translator.services.search import SearchService
from techword_translator.models.word import Word, TranslationItem
from techword_translator.models.api import WordsResponse, PaginationMeta


def make_word(id: int, en: str, es: str = "", de: str = "") -> Word:
    """Helper to build a Word with translations."""
    translations = [TranslationItem(language="en", translation=en)]
    if es:
        translations.append(TranslationItem(language="es", translation=es))
    if de:
        translations.append(TranslationItem(language="de", translation=de))
    return Word(id=id, word=en, translations=translations)


def make_response(words: list, next_cursor: str = None) -> WordsResponse:
    """Helper to build a WordsResponse."""
    return WordsResponse(
        data=words,
        links={"next": next_cursor, "prev": None},
        meta=PaginationMeta(
            path="/api/v1/words", per_page=50,
            next_cursor=next_cursor, prev_cursor=None
        ),
    )


class TestSearchServiceInitialization:
    """Tests for SearchService initialization."""

    def test_search_service_creation(self, mock_api_client):
        """Test creating a SearchService instance."""
        service = SearchService(mock_api_client)
        assert service.api == mock_api_client


class TestSearchServiceMatchesSearch:
    """Tests for _matches_search internal method."""

    def test_matches_english_exact(self, search_service):
        """Test exact match in English."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "computer", None)

    def test_matches_english_partial(self, search_service):
        """Test partial match in English."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert search_service._matches_search(word, "comp", "en")
        assert search_service._matches_search(word, "puter", "en")
        assert search_service._matches_search(word, "put", None)

    def test_matches_english_case_insensitive(self, search_service):
        """Test case-insensitive match (term_lower already lowercased)."""
        word = make_word(1, "Computer", "computadora", "Computer")
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "computer", None)

    def test_matches_spanish_exact(self, search_service):
        """Test exact match in Spanish."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert search_service._matches_search(word, "computadora", "es")
        assert search_service._matches_search(word, "computadora", None)

    def test_matches_spanish_partial(self, search_service):
        """Test partial match in Spanish."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert search_service._matches_search(word, "comput", "es")
        assert search_service._matches_search(word, "dora", "es")

    def test_matches_german_exact(self, search_service):
        """Test exact match in German."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert search_service._matches_search(word, "computer", "de")

    def test_matches_german_partial(self, search_service):
        """Test partial match in German."""
        word = make_word(2, "keyboard", "teclado", "Tastatur")
        assert search_service._matches_search(word, "tast", "de")
        assert search_service._matches_search(word, "atur", "de")

    def test_no_match(self, search_service):
        """Test when word doesn't match search."""
        word = make_word(1, "computer", "computadora", "Computer")
        assert not search_service._matches_search(word, "mouse", "en")
        assert not search_service._matches_search(word, "ratón", "es")
        assert not search_service._matches_search(word, "xyz", None)

    def test_matches_english_only_word(self, search_service):
        """Test matching word that only has English translation."""
        word = make_word(1, "computer")
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "comp", None)
        assert not search_service._matches_search(word, "computadora", "es")
        assert not search_service._matches_search(word, "computer", "de")

    def test_locale_filter_isolates_language(self, search_service):
        """Test locale filter searches only that language."""
        word = make_word(1, "computer", "computadora", "Computer")
        # "computer" exists in en and de, but not es
        assert not search_service._matches_search(word, "computer", "es")
        # "computadora" exists in es, but not de
        assert not search_service._matches_search(word, "computadora", "de")


class TestSearchServiceSearchByTerm:
    """Tests for search_by_term method."""

    @pytest.mark.asyncio
    async def test_single_result(self, mock_api_client):
        """Test searching and finding a single result."""
        words = [
            make_word(1, "computer", "computadora", "Computer"),
            make_word(2, "keyboard", "teclado", "Tastatur"),
        ]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        results = await service.search_by_term("computer", locale="en")

        assert len(results) == 1
        assert results[0].word == "computer"

    @pytest.mark.asyncio
    async def test_multiple_results(self, mock_api_client):
        """Test searching and finding multiple results."""
        words = [
            make_word(1, "computer", "computadora", "Computer"),
            make_word(2, "compute", "calcular", "berechnen"),
            make_word(3, "computational", "computacional", "rechnerisch"),
        ]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        results = await service.search_by_term("comput", locale="en")

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_respects_limit(self, mock_api_client):
        """Test search respects limit parameter."""
        words = [make_word(i, f"compute{i}", f"test{i}", f"test{i}") for i in range(1, 6)]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        results = await service.search_by_term("compute", locale="en", limit=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_no_results(self, mock_api_client):
        """Test search with no matching results."""
        words = [make_word(1, "computer", "computadora", "Computer")]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        results = await service.search_by_term("mouse", locale="en")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_locale_filtering(self, mock_api_client):
        """Test search filters by locale correctly."""
        words = [make_word(1, "computer", "computadora", "Computer")]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)

        assert len(await service.search_by_term("computadora", locale="es")) == 1
        assert len(await service.search_by_term("Computer", locale="de")) == 1
        assert len(await service.search_by_term("computer", locale="es")) == 0

    @pytest.mark.asyncio
    async def test_no_locale_searches_all(self, mock_api_client):
        """Test search without locale searches all languages."""
        words = [make_word(1, "computer", "computadora", "Computer")]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)

        assert len(await service.search_by_term("computer", locale=None)) == 1
        assert len(await service.search_by_term("computadora", locale=None)) == 1

    @pytest.mark.asyncio
    async def test_pagination(self, mock_api_client):
        """Test search handles pagination correctly."""
        page1 = make_response([make_word(1, "test1", "prueba1", "Test1")], next_cursor="cursor123")
        page2 = make_response([make_word(2, "test2", "prueba2", "Test2")])

        mock_api_client.fetch_words = AsyncMock(side_effect=[page1, page2])

        service = SearchService(mock_api_client)
        results = await service.search_by_term("test", locale="en", limit=10)

        assert len(results) == 2
        assert mock_api_client.fetch_words.call_count == 2

    @pytest.mark.asyncio
    async def test_max_pages_limit(self, mock_api_client):
        """Test search stops at max pages limit."""
        response = make_response(
            [make_word(1, "other", "otro", "andere")],
            next_cursor="cursor"
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)

        service = SearchService(mock_api_client)
        await service.search_by_term("test", locale="en", limit=100)

        assert mock_api_client.fetch_words.call_count == 10


class TestSearchServiceFindExactMatch:
    """Tests for find_exact_match method."""

    @pytest.mark.asyncio
    async def test_finds_match(self, mock_api_client):
        """Test finding an exact match."""
        words = [make_word(1, "computer", "computadora", "Computer")]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("computer", "en")

        assert result is not None
        assert result.word == "computer"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, mock_api_client):
        """Test when exact match is not found."""
        words = [make_word(1, "computer", "computadora", "Computer")]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("mouse", "en")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_first_match(self, mock_api_client):
        """Test that find_exact_match returns only the first result."""
        words = [
            make_word(1, "computer", "computadora", "Computer"),
            make_word(2, "compute", "calcular", "berechnen"),
        ]
        mock_api_client.fetch_words = AsyncMock(return_value=make_response(words))

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("comput", "en")

        assert result is not None
        assert result.id == 1
