"""Tests for domain models."""

import pytest
from pydantic import ValidationError

from techword_translator.models.word import Word, Translation
from techword_translator.models.api import WordsResponse, PaginationMeta


class TestTranslation:
    """Tests for Translation model."""

    def test_translation_creation(self, sample_translation):
        """Test creating a translation with all fields."""
        assert sample_translation.id == 1
        assert sample_translation.word_id == 1
        assert sample_translation.spanish_word == "computadora"
        assert sample_translation.german_word == "Computer"

    def test_translation_validation(self):
        """Test translation validation requirements."""
        # Valid translation
        translation = Translation(
            id=1, word_id=1, spanish_word="hola", german_word="Hallo"
        )
        assert translation.spanish_word == "hola"
        assert translation.german_word == "Hallo"

    def test_translation_missing_fields(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Translation(id=1)
        assert "word_id" in str(exc_info.value)

    def test_translation_pydantic_serialization(self, sample_translation):
        """Test serialization to dict."""
        data = sample_translation.model_dump()
        assert data["id"] == 1
        assert data["word_id"] == 1
        assert data["spanish_word"] == "computadora"
        assert data["german_word"] == "Computer"

    def test_translation_from_dict(self):
        """Test creating translation from dictionary."""
        data = {
            "id": 5,
            "word_id": 5,
            "spanish_word": "software",
            "german_word": "Software",
        }
        translation = Translation(**data)
        assert translation.id == 5
        assert translation.spanish_word == "software"
        assert translation.german_word == "Software"


class TestWord:
    """Tests for Word model."""

    def test_word_with_translation(self, sample_word_with_translation):
        """Test creating a word with translation."""
        assert sample_word_with_translation.id == 1
        assert sample_word_with_translation.english_word == "computer"
        assert sample_word_with_translation.translation is not None
        assert sample_word_with_translation.translation.spanish_word == "computadora"

    def test_word_without_translation(self, sample_word_without_translation):
        """Test creating a word without translation."""
        assert sample_word_without_translation.id == 2
        assert sample_word_without_translation.english_word == "keyboard"
        assert sample_word_without_translation.translation is None

    def test_word_validation(self):
        """Test word validation requirements."""
        # Valid word
        word = Word(id=1, english_word="test")
        assert word.english_word == "test"

        # Missing required field
        with pytest.raises(ValidationError) as exc_info:
            Word(id=1)
        assert "english_word" in str(exc_info.value)

    def test_get_translation_english(self, sample_word_with_translation):
        """Test getting English translation."""
        result = sample_word_with_translation.get_translation("en")
        assert result == "computer"

    def test_get_translation_spanish(self, sample_word_with_translation):
        """Test getting Spanish translation."""
        result = sample_word_with_translation.get_translation("es")
        assert result == "computadora"

    def test_get_translation_german(self, sample_word_with_translation):
        """Test getting German translation."""
        result = sample_word_with_translation.get_translation("de")
        assert result == "Computer"

    def test_get_translation_invalid_locale(self, sample_word_with_translation):
        """Test getting translation with invalid locale."""
        result = sample_word_with_translation.get_translation("fr")
        assert result is None

    def test_get_translation_no_translation_data(self, sample_word_without_translation):
        """Test getting translation when translation is None."""
        result = sample_word_without_translation.get_translation("es")
        assert result is None

        # English should still work
        result = sample_word_without_translation.get_translation("en")
        assert result == "keyboard"

    def test_get_all_translations_with_data(self, sample_word_with_translation):
        """Test getting all translations when translation exists."""
        result = sample_word_with_translation.get_all_translations()
        assert result == {
            "en": "computer",
            "es": "computadora",
            "de": "Computer",
        }

    def test_get_all_translations_without_data(self, sample_word_without_translation):
        """Test getting all translations when translation is None."""
        result = sample_word_without_translation.get_all_translations()
        assert result == {"en": "keyboard"}

    def test_word_pydantic_serialization(self, sample_word_with_translation):
        """Test serialization to dict."""
        data = sample_word_with_translation.model_dump()
        assert data["id"] == 1
        assert data["english_word"] == "computer"
        assert data["translation"]["spanish_word"] == "computadora"

    def test_word_from_dict(self):
        """Test creating word from dictionary."""
        data = {
            "id": 10,
            "english_word": "server",
            "translation": {
                "id": 10,
                "word_id": 10,
                "spanish_word": "servidor",
                "german_word": "Server",
            },
        }
        word = Word(**data)
        assert word.id == 10
        assert word.english_word == "server"
        assert word.translation.spanish_word == "servidor"


class TestPaginationMeta:
    """Tests for PaginationMeta model."""

    def test_pagination_meta_creation(self, sample_pagination_meta):
        """Test creating pagination metadata."""
        assert sample_pagination_meta.path == "/api/v1/words"
        assert sample_pagination_meta.per_page == 10
        assert sample_pagination_meta.next_cursor == "cursor123"
        assert sample_pagination_meta.prev_cursor is None

    def test_pagination_meta_with_prev(self):
        """Test pagination with previous cursor."""
        meta = PaginationMeta(
            path="/api/v1/words",
            per_page=10,
            next_cursor="next123",
            prev_cursor="prev456",
            next_page_url="https://api.test.com/next",
            prev_page_url="https://api.test.com/prev",
        )
        assert meta.prev_cursor == "prev456"
        assert meta.prev_page_url == "https://api.test.com/prev"

    def test_pagination_meta_no_next(self):
        """Test pagination without next cursor (last page)."""
        meta = PaginationMeta(
            path="/api/v1/words",
            per_page=10,
            next_cursor=None,
            prev_cursor="prev123",
        )
        assert meta.next_cursor is None
        assert meta.prev_cursor == "prev123"

    def test_pagination_meta_validation(self):
        """Test pagination validation requirements."""
        # Valid pagination
        meta = PaginationMeta(path="/test", per_page=10)
        assert meta.path == "/test"
        assert meta.per_page == 10

        # Missing required fields
        with pytest.raises(ValidationError) as exc_info:
            PaginationMeta(path="/test")
        assert "per_page" in str(exc_info.value)

    def test_pagination_meta_serialization(self, sample_pagination_meta):
        """Test serialization to dict."""
        data = sample_pagination_meta.model_dump()
        assert data["path"] == "/api/v1/words"
        assert data["per_page"] == 10
        assert data["next_cursor"] == "cursor123"


class TestWordsResponse:
    """Tests for WordsResponse model."""

    def test_words_response_creation(self, sample_words_response):
        """Test creating a words response."""
        assert len(sample_words_response.data) == 3
        assert sample_words_response.data[0].english_word == "computer"
        assert sample_words_response.meta.per_page == 10

    def test_words_response_empty_data(self, sample_pagination_meta):
        """Test words response with empty data list."""
        response = WordsResponse(
            data=[],
            links={"next": None, "prev": None},
            meta=sample_pagination_meta,
        )
        assert len(response.data) == 0
        assert response.links["next"] is None

    def test_words_response_validation(self):
        """Test words response validation."""
        # Missing required field
        with pytest.raises(ValidationError) as exc_info:
            WordsResponse(data=[], links={})
        assert "meta" in str(exc_info.value)

    def test_words_response_serialization(self, sample_words_response):
        """Test serialization to dict."""
        data = sample_words_response.model_dump()
        assert "data" in data
        assert "links" in data
        assert "meta" in data
        assert len(data["data"]) == 3
        assert data["data"][0]["english_word"] == "computer"

    def test_words_response_from_dict(self):
        """Test creating words response from dictionary."""
        data = {
            "data": [
                {
                    "id": 1,
                    "english_word": "test",
                    "translation": {
                        "id": 1,
                        "word_id": 1,
                        "spanish_word": "prueba",
                        "german_word": "Test",
                    },
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {
                "path": "/api/v1/words",
                "per_page": 10,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }
        response = WordsResponse(**data)
        assert len(response.data) == 1
        assert response.data[0].english_word == "test"
        assert response.meta.per_page == 10

    def test_words_response_navigation(self, sample_words_response):
        """Test accessing navigation links."""
        assert "next" in sample_words_response.links
        assert "prev" in sample_words_response.links
        assert sample_words_response.links["next"] is not None
        assert sample_words_response.links["prev"] is None

    def test_words_response_iteration(self, sample_words_response):
        """Test iterating over words in response."""
        words = [word.english_word for word in sample_words_response.data]
        assert words == ["computer", "keyboard", "mouse"]
