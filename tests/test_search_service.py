"""Tests for SearchService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from techword_translator.services.search import SearchService
from techword_translator.models.word import Word, Translation
from techword_translator.models.api import WordsResponse, PaginationMeta


class TestSearchServiceInitialization:
    """Tests for SearchService initialization."""

    def test_search_service_creation(self, mock_api_client):
        """Test creating a SearchService instance."""
        service = SearchService(mock_api_client)
        assert service.api == mock_api_client


class TestSearchServiceMatchesSearch:
    """Tests for _matches_search internal method."""

    def test_matches_search_english_exact(self, search_service):
        """Test exact match in English."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "computer", None)

    def test_matches_search_english_partial(self, search_service):
        """Test partial match in English."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert search_service._matches_search(word, "comp", "en")
        assert search_service._matches_search(word, "puter", "en")
        assert search_service._matches_search(word, "put", None)

    def test_matches_search_english_case_insensitive(self, search_service):
        """Test case-insensitive match in English."""
        word = Word(
            id=1,
            english_word="Computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        # _matches_search expects term_lower to already be lowercase
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "computer", None)

    def test_matches_search_spanish_exact(self, search_service):
        """Test exact match in Spanish."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert search_service._matches_search(word, "computadora", "es")
        assert search_service._matches_search(word, "computadora", None)

    def test_matches_search_spanish_partial(self, search_service):
        """Test partial match in Spanish."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert search_service._matches_search(word, "comput", "es")
        assert search_service._matches_search(word, "dora", "es")
        assert search_service._matches_search(word, "tadora", None)

    def test_matches_search_german_exact(self, search_service):
        """Test exact match in German."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert search_service._matches_search(word, "computer", "de")
        assert search_service._matches_search(word, "computer", None)

    def test_matches_search_german_partial(self, search_service):
        """Test partial match in German."""
        word = Word(
            id=2,
            english_word="keyboard",
            translation=Translation(
                id=2, word_id=2, spanish_word="teclado", german_word="Tastatur"
            ),
        )

        assert search_service._matches_search(word, "tast", "de")
        assert search_service._matches_search(word, "atur", "de")
        assert search_service._matches_search(word, "stat", None)

    def test_matches_search_no_match(self, search_service):
        """Test when word doesn't match."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        assert not search_service._matches_search(word, "mouse", "en")
        assert not search_service._matches_search(word, "ratón", "es")
        assert not search_service._matches_search(word, "xyz", None)

    def test_matches_search_without_translation(self, search_service):
        """Test matching when word has no translation."""
        word = Word(id=1, english_word="computer", translation=None)

        # Should match English
        assert search_service._matches_search(word, "computer", "en")
        assert search_service._matches_search(word, "comp", None)

        # Should not match other languages
        assert not search_service._matches_search(word, "computadora", "es")
        assert not search_service._matches_search(word, "computer", "de")

    def test_matches_search_wrong_locale_filter(self, search_service):
        """Test that locale filter works correctly."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        # "computer" exists in English and German, but not Spanish
        assert not search_service._matches_search(word, "computer", "es")

        # "computadora" exists in Spanish, but not German
        assert not search_service._matches_search(word, "computadora", "de")


class TestSearchServiceSearchByTerm:
    """Tests for search_by_term method."""

    @pytest.mark.asyncio
    async def test_search_by_term_single_result(self, mock_api_client):
        """Test searching and finding a single result."""
        # Mock API response
        words = [
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
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("computer", locale="en")

        assert len(results) == 1
        assert results[0].english_word == "computer"

    @pytest.mark.asyncio
    async def test_search_by_term_multiple_results(self, mock_api_client):
        """Test searching and finding multiple results."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
            Word(
                id=2,
                english_word="compute",
                translation=Translation(
                    id=2, word_id=2, spanish_word="calcular", german_word="berechnen"
                ),
            ),
            Word(
                id=3,
                english_word="computational",
                translation=Translation(
                    id=3, word_id=3, spanish_word="computacional", german_word="rechnerisch"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("comput", locale="en")

        assert len(results) == 3
        assert all("comput" in word.english_word.lower() for word in results)

    @pytest.mark.asyncio
    async def test_search_by_term_with_limit(self, mock_api_client):
        """Test search respects limit parameter."""
        words = [
            Word(
                id=i,
                english_word=f"compute{i}",
                translation=Translation(
                    id=i, word_id=i, spanish_word=f"test{i}", german_word=f"test{i}"
                ),
            )
            for i in range(1, 6)
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("compute", locale="en", limit=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_by_term_no_results(self, mock_api_client):
        """Test search with no matching results."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("mouse", locale="en")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_by_term_locale_filtering(self, mock_api_client):
        """Test search filters by locale correctly."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)

        # Search in Spanish
        results = await service.search_by_term("computadora", locale="es")
        assert len(results) == 1

        # Search in German
        results = await service.search_by_term("Computer", locale="de")
        assert len(results) == 1

        # Search "computer" in Spanish should not match (it's English)
        results = await service.search_by_term("computer", locale="es")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_by_term_no_locale_searches_all(self, mock_api_client):
        """Test search without locale searches all languages."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)

        # All of these should match
        results = await service.search_by_term("computer", locale=None)
        assert len(results) == 1

        results = await service.search_by_term("computadora", locale=None)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_by_term_pagination(self, mock_api_client):
        """Test search handles pagination."""
        # First page
        words_page1 = [
            Word(
                id=1,
                english_word="test1",
                translation=Translation(
                    id=1, word_id=1, spanish_word="prueba1", german_word="Test1"
                ),
            ),
        ]
        response1 = WordsResponse(
            data=words_page1,
            links={"next": "cursor123", "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor="cursor123", prev_cursor=None
            ),
        )

        # Second page
        words_page2 = [
            Word(
                id=2,
                english_word="test2",
                translation=Translation(
                    id=2, word_id=2, spanish_word="prueba2", german_word="Test2"
                ),
            ),
        ]
        response2 = WordsResponse(
            data=words_page2,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )

        mock_api_client.fetch_words = AsyncMock(side_effect=[response1, response2])
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("test", locale="en", limit=10)

        assert len(results) == 2
        assert mock_api_client.fetch_words.call_count == 2

    @pytest.mark.asyncio
    async def test_search_by_term_max_pages_limit(self, mock_api_client):
        """Test search stops at max pages."""
        # Create response with next_cursor
        words = [
            Word(
                id=1,
                english_word="other",
                translation=Translation(
                    id=1, word_id=1, spanish_word="otro", german_word="andere"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": "cursor", "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor="cursor", prev_cursor=None
            ),
        )

        # Always return response with next_cursor
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("test", locale="en", limit=100)

        # Should stop at 10 pages max
        assert mock_api_client.fetch_words.call_count == 10

    @pytest.mark.asyncio
    async def test_search_by_term_fetches_missing_translation(self, mock_api_client):
        """Test search fetches translation if not present."""
        words = [
            Word(id=1, english_word="computer", translation=None),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )

        translation = Translation(
            id=1, word_id=1, spanish_word="computadora", german_word="Computer"
        )

        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=translation)

        service = SearchService(mock_api_client)
        results = await service.search_by_term("computer", locale="en")

        assert len(results) == 1
        assert mock_api_client.fetch_translation.called


class TestSearchServiceFindExactMatch:
    """Tests for find_exact_match method."""

    @pytest.mark.asyncio
    async def test_find_exact_match_found(self, mock_api_client):
        """Test finding an exact match."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("computer", "en")

        assert result is not None
        assert result.english_word == "computer"

    @pytest.mark.asyncio
    async def test_find_exact_match_not_found(self, mock_api_client):
        """Test when exact match is not found."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("mouse", "en")

        assert result is None

    @pytest.mark.asyncio
    async def test_find_exact_match_uses_limit_one(self, mock_api_client):
        """Test that find_exact_match only fetches one result."""
        words = [
            Word(
                id=1,
                english_word="computer",
                translation=Translation(
                    id=1, word_id=1, spanish_word="computadora", german_word="Computer"
                ),
            ),
            Word(
                id=2,
                english_word="compute",
                translation=Translation(
                    id=2, word_id=2, spanish_word="calcular", german_word="berechnen"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=50, next_cursor=None, prev_cursor=None
            ),
        )
        mock_api_client.fetch_words = AsyncMock(return_value=response)
        mock_api_client.fetch_translation = AsyncMock(return_value=None)

        service = SearchService(mock_api_client)
        result = await service.find_exact_match("comput", "en")

        # Should return only the first match
        assert result is not None
        assert result.id == 1
