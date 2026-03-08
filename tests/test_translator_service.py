"""Tests for TranslatorService."""

import pytest
from unittest.mock import AsyncMock

from techword_translator.services.translator import TranslatorService
from techword_translator.models.word import Word, TranslationItem


def make_word(id: int, en: str, es: str = "", de: str = "") -> Word:
    """Helper to build a Word with translations."""
    translations = [TranslationItem(language="en", translation=en)]
    if es:
        translations.append(TranslationItem(language="es", translation=es))
    if de:
        translations.append(TranslationItem(language="de", translation=de))
    return Word(id=id, word=en, translations=translations)


class TestTranslatorServiceInitialization:
    """Tests for TranslatorService initialization."""

    def test_translator_service_creation(self, mock_search_service):
        """Test creating a TranslatorService instance."""
        service = TranslatorService(mock_search_service)
        assert service.search == mock_search_service


class TestTranslatorServiceTranslate:
    """Tests for translate method."""

    @pytest.mark.asyncio
    async def test_translate_english_to_spanish(self, mock_search_service):
        """Test translating from English to Spanish."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="es")

        assert result == "computadora"
        mock_search_service.find_exact_match.assert_called_once_with("computer", "en")

    @pytest.mark.asyncio
    async def test_translate_english_to_german(self, mock_search_service):
        """Test translating from English to German."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="de")

        assert result == "Computer"

    @pytest.mark.asyncio
    async def test_translate_spanish_to_english(self, mock_search_service):
        """Test translating from Spanish to English."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computadora", from_locale="es", to_locale="en")

        assert result == "computer"
        mock_search_service.find_exact_match.assert_called_once_with("computadora", "es")

    @pytest.mark.asyncio
    async def test_translate_spanish_to_german(self, mock_search_service):
        """Test translating from Spanish to German."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computadora", from_locale="es", to_locale="de")

        assert result == "Computer"

    @pytest.mark.asyncio
    async def test_translate_german_to_english(self, mock_search_service):
        """Test translating from German to English."""
        word = make_word(2, "keyboard", "teclado", "Tastatur")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("Tastatur", from_locale="de", to_locale="en")

        assert result == "keyboard"

    @pytest.mark.asyncio
    async def test_translate_german_to_spanish(self, mock_search_service):
        """Test translating from German to Spanish."""
        word = make_word(2, "keyboard", "teclado", "Tastatur")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("Tastatur", from_locale="de", to_locale="es")

        assert result == "teclado"

    @pytest.mark.asyncio
    async def test_translate_same_language(self, mock_search_service):
        """Test translating to the same language returns same word."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="en")

        assert result == "computer"

    @pytest.mark.asyncio
    async def test_translate_word_not_found(self, mock_search_service):
        """Test translate when word is not found."""
        mock_search_service.find_exact_match = AsyncMock(return_value=None)

        service = TranslatorService(mock_search_service)
        result = await service.translate("nonexistent", from_locale="en", to_locale="es")

        assert result is None

    @pytest.mark.asyncio
    async def test_translate_missing_target_locale(self, mock_search_service):
        """Test translate when target locale is not in translations."""
        word = make_word(1, "computer")  # English only
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)

        assert await service.translate("computer", from_locale="en", to_locale="en") == "computer"
        assert await service.translate("computer", from_locale="en", to_locale="es") is None

    @pytest.mark.asyncio
    async def test_translate_unsupported_locale(self, mock_search_service):
        """Test translate with unsupported target locale returns None."""
        word = make_word(1, "computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="fr")

        assert result is None

    @pytest.mark.asyncio
    async def test_translate_multiple_calls(self, mock_search_service):
        """Test making multiple translation calls."""
        word1 = make_word(1, "computer", "computadora", "Computer")
        word2 = make_word(2, "keyboard", "teclado", "Tastatur")
        mock_search_service.find_exact_match = AsyncMock(side_effect=[word1, word2])

        service = TranslatorService(mock_search_service)
        assert await service.translate("computer", from_locale="en", to_locale="es") == "computadora"
        assert await service.translate("keyboard", from_locale="en", to_locale="es") == "teclado"
        assert mock_search_service.find_exact_match.call_count == 2

    @pytest.mark.asyncio
    async def test_translate_preserves_case(self, mock_search_service):
        """Test that translate passes the exact term to search."""
        word = make_word(1, "Computer", "computadora", "Computer")
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        await service.translate("Computer", from_locale="en", to_locale="es")

        mock_search_service.find_exact_match.assert_called_once_with("Computer", "en")

    @pytest.mark.asyncio
    async def test_translate_all_language_combinations(self, mock_search_service):
        """Test all 9 language combination translations."""
        word = make_word(1, "test", "prueba", "Test")
        service = TranslatorService(mock_search_service)

        combinations = [
            ("test", "en", "en", "test"),
            ("test", "en", "es", "prueba"),
            ("test", "en", "de", "Test"),
            ("prueba", "es", "en", "test"),
            ("prueba", "es", "es", "prueba"),
            ("prueba", "es", "de", "Test"),
            ("Test", "de", "en", "test"),
            ("Test", "de", "es", "prueba"),
            ("Test", "de", "de", "Test"),
        ]

        for term, from_loc, to_loc, expected in combinations:
            mock_search_service.find_exact_match = AsyncMock(return_value=word)
            result = await service.translate(term, from_locale=from_loc, to_locale=to_loc)
            assert result == expected, f"Failed for {from_loc}->{to_loc}"


class TestTranslatorServiceEdgeCases:
    """Tests for edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_translate_empty_term(self, mock_search_service):
        """Test translate with empty term."""
        mock_search_service.find_exact_match = AsyncMock(return_value=None)

        service = TranslatorService(mock_search_service)
        result = await service.translate("", from_locale="en", to_locale="es")

        assert result is None

    @pytest.mark.asyncio
    async def test_translate_special_characters(self, mock_search_service):
        """Test translate with special characters in term."""
        word = Word(
            id=1,
            word="C++",
            translations=[
                TranslationItem(language="en", translation="C++"),
                TranslationItem(language="es", translation="C++"),
            ],
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        assert await service.translate("C++", from_locale="en", to_locale="es") == "C++"

    @pytest.mark.asyncio
    async def test_translate_unicode_characters(self, mock_search_service):
        """Test translate with unicode characters."""
        word = Word(
            id=1,
            word="mouse",
            translations=[
                TranslationItem(language="en", translation="mouse"),
                TranslationItem(language="es", translation="ratón"),
            ],
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        assert await service.translate("ratón", from_locale="es", to_locale="en") == "mouse"
