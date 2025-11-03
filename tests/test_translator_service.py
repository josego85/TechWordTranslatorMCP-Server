"""Tests for TranslatorService."""

import pytest
from unittest.mock import AsyncMock

from techword_translator.services.translator import TranslatorService
from techword_translator.models.word import Word, Translation


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
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="es")

        assert result == "computadora"
        mock_search_service.find_exact_match.assert_called_once_with("computer", "en")

    @pytest.mark.asyncio
    async def test_translate_english_to_german(self, mock_search_service):
        """Test translating from English to German."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="de")

        assert result == "Computer"

    @pytest.mark.asyncio
    async def test_translate_spanish_to_english(self, mock_search_service):
        """Test translating from Spanish to English."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computadora", from_locale="es", to_locale="en")

        assert result == "computer"
        mock_search_service.find_exact_match.assert_called_once_with("computadora", "es")

    @pytest.mark.asyncio
    async def test_translate_spanish_to_german(self, mock_search_service):
        """Test translating from Spanish to German."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computadora", from_locale="es", to_locale="de")

        assert result == "Computer"

    @pytest.mark.asyncio
    async def test_translate_german_to_english(self, mock_search_service):
        """Test translating from German to English."""
        word = Word(
            id=2,
            english_word="keyboard",
            translation=Translation(
                id=2, word_id=2, spanish_word="teclado", german_word="Tastatur"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("Tastatur", from_locale="de", to_locale="en")

        assert result == "keyboard"
        mock_search_service.find_exact_match.assert_called_once_with("Tastatur", "de")

    @pytest.mark.asyncio
    async def test_translate_german_to_spanish(self, mock_search_service):
        """Test translating from German to Spanish."""
        word = Word(
            id=2,
            english_word="keyboard",
            translation=Translation(
                id=2, word_id=2, spanish_word="teclado", german_word="Tastatur"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("Tastatur", from_locale="de", to_locale="es")

        assert result == "teclado"

    @pytest.mark.asyncio
    async def test_translate_same_language(self, mock_search_service):
        """Test translating to the same language (should return same word)."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
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
        mock_search_service.find_exact_match.assert_called_once_with("nonexistent", "en")

    @pytest.mark.asyncio
    async def test_translate_word_without_translation(self, mock_search_service):
        """Test translate when word has no translation data."""
        word = Word(id=1, english_word="computer", translation=None)
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)

        # English to English should work
        result = await service.translate("computer", from_locale="en", to_locale="en")
        assert result == "computer"

        # English to Spanish should return None
        result = await service.translate("computer", from_locale="en", to_locale="es")
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_invalid_target_locale(self, mock_search_service):
        """Test translate with invalid target locale."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("computer", from_locale="en", to_locale="fr")

        assert result is None

    @pytest.mark.asyncio
    async def test_translate_multiple_calls(self, mock_search_service):
        """Test making multiple translation calls."""
        word1 = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        word2 = Word(
            id=2,
            english_word="keyboard",
            translation=Translation(
                id=2, word_id=2, spanish_word="teclado", german_word="Tastatur"
            ),
        )

        mock_search_service.find_exact_match = AsyncMock(side_effect=[word1, word2])

        service = TranslatorService(mock_search_service)

        result1 = await service.translate("computer", from_locale="en", to_locale="es")
        result2 = await service.translate("keyboard", from_locale="en", to_locale="es")

        assert result1 == "computadora"
        assert result2 == "teclado"
        assert mock_search_service.find_exact_match.call_count == 2

    @pytest.mark.asyncio
    async def test_translate_case_sensitivity(self, mock_search_service):
        """Test that translate passes exact term to search."""
        word = Word(
            id=1,
            english_word="Computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        await service.translate("Computer", from_locale="en", to_locale="es")

        # Verify exact term was passed
        mock_search_service.find_exact_match.assert_called_once_with("Computer", "en")

    @pytest.mark.asyncio
    async def test_translate_all_language_combinations(self, mock_search_service):
        """Test all possible language combination translations."""
        word = Word(
            id=1,
            english_word="test",
            translation=Translation(
                id=1, word_id=1, spanish_word="prueba", german_word="Test"
            ),
        )

        service = TranslatorService(mock_search_service)

        # Test all 9 combinations
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
        mock_search_service.find_exact_match.assert_called_once_with("", "en")

    @pytest.mark.asyncio
    async def test_translate_whitespace_term(self, mock_search_service):
        """Test translate with whitespace term."""
        mock_search_service.find_exact_match = AsyncMock(return_value=None)

        service = TranslatorService(mock_search_service)
        result = await service.translate("   ", from_locale="en", to_locale="es")

        assert result is None

    @pytest.mark.asyncio
    async def test_translate_special_characters(self, mock_search_service):
        """Test translate with special characters in term."""
        word = Word(
            id=1,
            english_word="C++",
            translation=Translation(id=1, word_id=1, spanish_word="C++", german_word="C++"),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("C++", from_locale="en", to_locale="es")

        assert result == "C++"

    @pytest.mark.asyncio
    async def test_translate_unicode_characters(self, mock_search_service):
        """Test translate with unicode characters."""
        word = Word(
            id=1,
            english_word="mouse",
            translation=Translation(id=1, word_id=1, spanish_word="ratón", german_word="Maus"),
        )
        mock_search_service.find_exact_match = AsyncMock(return_value=word)

        service = TranslatorService(mock_search_service)
        result = await service.translate("ratón", from_locale="es", to_locale="en")

        assert result == "mouse"
