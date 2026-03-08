"""Tests for domain models."""

import pytest
from pydantic import ValidationError

from techword_translator.models.word import Word, TranslationItem
from techword_translator.models.api import WordsResponse, PaginationMeta


class TestTranslationItem:
    """Tests for TranslationItem model."""

    def test_translation_item_creation(self):
        """Test creating a TranslationItem with all fields."""
        item = TranslationItem(language="es", translation="computadora")
        assert item.language == "es"
        assert item.translation == "computadora"

    def test_translation_item_validation(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            TranslationItem(language="es")

    def test_translation_item_serialization(self):
        """Test serialization to dict."""
        item = TranslationItem(language="de", translation="Computer")
        data = item.model_dump()
        assert data["language"] == "de"
        assert data["translation"] == "Computer"

    def test_translation_item_from_dict(self):
        """Test creating TranslationItem from dictionary."""
        data = {"language": "en", "translation": "server"}
        item = TranslationItem(**data)
        assert item.language == "en"
        assert item.translation == "server"


class TestWord:
    """Tests for Word model."""

    def test_word_with_all_translations(self, sample_word_with_translation):
        """Test creating a word with full translations list."""
        assert sample_word_with_translation.id == 1
        assert sample_word_with_translation.word == "computer"
        assert len(sample_word_with_translation.translations) == 3

    def test_word_with_single_translation(self, sample_word_without_translation):
        """Test creating a word with a single language."""
        assert sample_word_without_translation.id == 2
        assert sample_word_without_translation.word == "keyboard"
        assert len(sample_word_without_translation.translations) == 1

    def test_word_validation_missing_word(self):
        """Test that missing word field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Word(id=1)
        assert "word" in str(exc_info.value)

    def test_word_defaults_to_empty_translations(self):
        """Test that translations defaults to empty list."""
        word = Word(id=1, word="test")
        assert word.translations == []

    def test_get_translation_english(self, sample_word_with_translation):
        """Test getting English translation."""
        assert sample_word_with_translation.get_translation("en") == "computer"

    def test_get_translation_spanish(self, sample_word_with_translation):
        """Test getting Spanish translation."""
        assert sample_word_with_translation.get_translation("es") == "computadora"

    def test_get_translation_german(self, sample_word_with_translation):
        """Test getting German translation."""
        assert sample_word_with_translation.get_translation("de") == "Computer"

    def test_get_translation_unknown_locale(self, sample_word_with_translation):
        """Test getting translation with unsupported locale returns None."""
        assert sample_word_with_translation.get_translation("fr") is None

    def test_get_translation_missing_locale(self, sample_word_without_translation):
        """Test getting a locale that is not in the translations list."""
        assert sample_word_without_translation.get_translation("es") is None
        assert sample_word_without_translation.get_translation("en") == "keyboard"

    def test_get_all_translations_full(self, sample_word_with_translation):
        """Test getting all translations as dict."""
        result = sample_word_with_translation.get_all_translations()
        assert result == {"en": "computer", "es": "computadora", "de": "Computer"}

    def test_get_all_translations_single(self, sample_word_without_translation):
        """Test get_all_translations with only one language."""
        result = sample_word_without_translation.get_all_translations()
        assert result == {"en": "keyboard"}

    def test_get_all_translations_empty(self):
        """Test get_all_translations when no translations."""
        word = Word(id=1, word="test")
        assert word.get_all_translations() == {}

    def test_word_pydantic_serialization(self, sample_word_with_translation):
        """Test serialization to dict."""
        data = sample_word_with_translation.model_dump()
        assert data["id"] == 1
        assert data["word"] == "computer"
        assert len(data["translations"]) == 3
        assert data["translations"][0]["language"] == "en"

    def test_word_from_api_dict(self):
        """Test creating Word from actual API response format."""
        data = {
            "id": 10,
            "word": "server",
            "translations": [
                {"language": "en", "translation": "server"},
                {"language": "es", "translation": "servidor"},
                {"language": "de", "translation": "Server"},
            ],
        }
        word = Word(**data)
        assert word.id == 10
        assert word.word == "server"
        assert word.get_translation("es") == "servidor"


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
        )
        assert meta.prev_cursor == "prev456"

    def test_pagination_meta_no_next(self):
        """Test pagination without next cursor (last page)."""
        meta = PaginationMeta(path="/api/v1/words", per_page=10, prev_cursor="prev123")
        assert meta.next_cursor is None
        assert meta.prev_cursor == "prev123"

    def test_pagination_meta_validation(self):
        """Test pagination validation requirements."""
        meta = PaginationMeta(path="/test", per_page=10)
        assert meta.path == "/test"
        assert meta.per_page == 10

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
        assert sample_words_response.data[0].word == "computer"
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
        assert data["data"][0]["word"] == "computer"

    def test_words_response_from_dict(self):
        """Test creating words response from API-format dictionary."""
        data = {
            "data": [
                {
                    "id": 1,
                    "word": "test",
                    "translations": [
                        {"language": "en", "translation": "test"},
                        {"language": "es", "translation": "prueba"},
                    ],
                }
            ],
            "links": {"next": None, "prev": None},
            "meta": {"path": "/api/v1/words", "per_page": 10},
        }
        response = WordsResponse(**data)
        assert len(response.data) == 1
        assert response.data[0].word == "test"
        assert response.data[0].get_translation("es") == "prueba"

    def test_words_response_navigation(self, sample_words_response):
        """Test accessing navigation links."""
        assert "next" in sample_words_response.links
        assert "prev" in sample_words_response.links
        assert sample_words_response.links["next"] is not None
        assert sample_words_response.links["prev"] is None

    def test_words_response_iteration(self, sample_words_response):
        """Test iterating over words in response."""
        words = [word.word for word in sample_words_response.data]
        assert words == ["computer", "keyboard", "mouse"]
