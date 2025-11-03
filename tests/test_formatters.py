"""Tests for ResponseFormatter."""

import pytest
from techword_translator.formatters import ResponseFormatter
from techword_translator.models.word import Word, Translation
from techword_translator.models.api import WordsResponse, PaginationMeta


class TestFormatTranslation:
    """Tests for format_translation method."""

    def test_format_translation_english_to_spanish(self, response_formatter):
        """Test formatting English to Spanish translation."""
        result = response_formatter.format_translation(
            "computer", "en", "computadora", "es"
        )
        assert result == "computer (en) → computadora (es)"

    def test_format_translation_spanish_to_german(self, response_formatter):
        """Test formatting Spanish to German translation."""
        result = response_formatter.format_translation(
            "computadora", "es", "Computer", "de"
        )
        assert result == "computadora (es) → Computer (de)"

    def test_format_translation_german_to_english(self, response_formatter):
        """Test formatting German to English translation."""
        result = response_formatter.format_translation(
            "Computer", "de", "computer", "en"
        )
        assert result == "Computer (de) → computer (en)"

    def test_format_translation_with_special_chars(self, response_formatter):
        """Test formatting with special characters."""
        result = response_formatter.format_translation(
            "C++", "en", "C++", "es"
        )
        assert result == "C++ (en) → C++ (es)"

    def test_format_translation_with_unicode(self, response_formatter):
        """Test formatting with unicode characters."""
        result = response_formatter.format_translation(
            "mouse", "en", "ratón", "es"
        )
        assert result == "mouse (en) → ratón (es)"


class TestFormatTranslationNotFound:
    """Tests for format_translation_not_found method."""

    def test_format_translation_not_found(self, response_formatter):
        """Test formatting not found message."""
        result = response_formatter.format_translation_not_found(
            "nonexistent", "en", "es"
        )
        assert result == "Translation not found for 'nonexistent' from en to es"

    def test_format_translation_not_found_all_languages(self, response_formatter):
        """Test not found message for all language combinations."""
        combinations = [
            ("test", "en", "es"),
            ("test", "en", "de"),
            ("prueba", "es", "en"),
            ("prueba", "es", "de"),
            ("Test", "de", "en"),
            ("Test", "de", "es"),
        ]

        for term, from_loc, to_loc in combinations:
            result = response_formatter.format_translation_not_found(
                term, from_loc, to_loc
            )
            assert f"'{term}'" in result
            assert f"from {from_loc}" in result
            assert f"to {to_loc}" in result


class TestFormatWordWithTranslations:
    """Tests for format_word_with_translations method."""

    def test_format_word_with_all_translations(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting word with all translations."""
        result = response_formatter.format_word_with_translations(
            sample_word_with_translation
        )
        assert "de: Computer" in result
        assert "en: computer" in result
        assert "es: computadora" in result
        assert "|" in result

    def test_format_word_without_translation(
        self, response_formatter, sample_word_without_translation
    ):
        """Test formatting word without translation data."""
        result = response_formatter.format_word_with_translations(
            sample_word_without_translation
        )
        # Should only have English
        assert "en: keyboard" in result
        assert "es:" not in result
        assert "de:" not in result

    def test_format_word_alphabetical_order(self, response_formatter):
        """Test that languages are sorted alphabetically."""
        word = Word(
            id=1,
            english_word="test",
            translation=Translation(
                id=1, word_id=1, spanish_word="prueba", german_word="Test"
            ),
        )

        result = response_formatter.format_word_with_translations(word)
        # Should be de, en, es (alphabetical)
        parts = result.split(" | ")
        assert parts[0].startswith("de:")
        assert parts[1].startswith("en:")
        assert parts[2].startswith("es:")

    def test_format_word_with_unicode(self, response_formatter):
        """Test formatting with unicode characters."""
        word = Word(
            id=1,
            english_word="mouse",
            translation=Translation(
                id=1, word_id=1, spanish_word="ratón", german_word="Maus"
            ),
        )

        result = response_formatter.format_word_with_translations(word)
        assert "es: ratón" in result


class TestFormatSearchResults:
    """Tests for format_search_results method."""

    def test_format_search_results_with_results(
        self, response_formatter, sample_words_list
    ):
        """Test formatting search results with matches."""
        result = response_formatter.format_search_results(
            sample_words_list, "test"
        )

        assert "Found 3 result(s) for 'test':" in result
        assert "1." in result
        assert "2." in result
        assert "3." in result
        assert "computer" in result
        assert "keyboard" in result
        assert "mouse" in result

    def test_format_search_results_no_results(self, response_formatter):
        """Test formatting search results with no matches."""
        result = response_formatter.format_search_results([], "nonexistent")
        assert result == "No results found for 'nonexistent'"

    def test_format_search_results_no_results_with_locale(self, response_formatter):
        """Test formatting no results with locale filter."""
        result = response_formatter.format_search_results(
            [], "test", locale="es"
        )
        assert result == "No results found for 'test' in es"

    def test_format_search_results_single_result(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting search results with single match."""
        result = response_formatter.format_search_results(
            [sample_word_with_translation], "computer"
        )

        assert "Found 1 result(s)" in result
        assert "1." in result
        assert "computer" in result

    def test_format_search_results_numbering(
        self, response_formatter, sample_words_list
    ):
        """Test that results are numbered correctly."""
        result = response_formatter.format_search_results(
            sample_words_list, "test"
        )

        lines = [line for line in result.split("\n") if line.strip()]
        # First line is header "Found X result(s)...", then numbered items
        assert lines[1].startswith("1.")
        assert lines[2].startswith("2.")
        assert lines[3].startswith("3.")

    def test_format_search_results_includes_all_translations(
        self, response_formatter
    ):
        """Test that all translations are included in results."""
        word = Word(
            id=1,
            english_word="computer",
            translation=Translation(
                id=1, word_id=1, spanish_word="computadora", german_word="Computer"
            ),
        )

        result = response_formatter.format_search_results([word], "comp")

        assert "en: computer" in result
        assert "es: computadora" in result
        assert "de: Computer" in result


class TestFormatWordDetails:
    """Tests for format_word_details method."""

    def test_format_word_details_with_translations(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting detailed word information."""
        result = response_formatter.format_word_details(
            sample_word_with_translation
        )

        assert "Word ID: 1" in result
        assert "Translations:" in result
        assert "[en] English: computer" in result
        assert "[es] Spanish: computadora" in result
        assert "[de] German: Computer" in result

    def test_format_word_details_without_translation(
        self, response_formatter, sample_word_without_translation
    ):
        """Test formatting word details without translation."""
        result = response_formatter.format_word_details(
            sample_word_without_translation
        )

        assert "Word ID: 2" in result
        assert "Translations:" in result
        assert "[en] English: keyboard" in result
        # Should not have Spanish or German
        assert "Spanish:" not in result
        assert "German:" not in result

    def test_format_word_details_structure(
        self, response_formatter, sample_word_with_translation
    ):
        """Test the structure of formatted word details."""
        result = response_formatter.format_word_details(
            sample_word_with_translation
        )

        lines = result.split("\n")
        assert lines[0].startswith("Word ID:")
        assert lines[1] == ""
        assert lines[2] == "Translations:"
        # Languages should be sorted
        assert "[de]" in lines[3]
        assert "[en]" in lines[4]
        assert "[es]" in lines[5]

    def test_format_word_details_indentation(
        self, response_formatter, sample_word_with_translation
    ):
        """Test that translations are properly indented."""
        result = response_formatter.format_word_details(
            sample_word_with_translation
        )

        lines = result.split("\n")
        # Translation lines should start with two spaces
        for line in lines[3:]:  # Skip header lines
            if line:
                assert line.startswith("  ")


class TestFormatWordList:
    """Tests for format_word_list method."""

    def test_format_word_list_with_data(
        self, response_formatter, sample_words_response
    ):
        """Test formatting paginated word list."""
        result = response_formatter.format_word_list(sample_words_response)

        assert "Showing 3 terms:" in result
        assert "1. [ID: 1]" in result
        assert "2. [ID: 2]" in result
        assert "3. [ID: 3]" in result
        assert "--- Pagination ---" in result
        assert "Next cursor: cursor123" in result

    def test_format_word_list_empty(self, response_formatter):
        """Test formatting empty word list."""
        response = WordsResponse(
            data=[],
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words",
                per_page=10,
                next_cursor=None,
                prev_cursor=None,
            ),
        )

        result = response_formatter.format_word_list(response)
        assert result == "No terms found"

    def test_format_word_list_no_pagination(self, response_formatter):
        """Test formatting word list without pagination cursors."""
        words = [
            Word(
                id=1,
                english_word="test",
                translation=Translation(
                    id=1, word_id=1, spanish_word="prueba", german_word="Test"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": None, "prev": None},
            meta=PaginationMeta(
                path="/api/v1/words",
                per_page=10,
                next_cursor=None,
                prev_cursor=None,
            ),
        )

        result = response_formatter.format_word_list(response)

        assert "--- Pagination ---" in result
        assert "No more pages available" in result

    def test_format_word_list_with_prev_cursor(self, response_formatter):
        """Test formatting word list with previous cursor."""
        words = [
            Word(
                id=1,
                english_word="test",
                translation=Translation(
                    id=1, word_id=1, spanish_word="prueba", german_word="Test"
                ),
            ),
        ]
        response = WordsResponse(
            data=words,
            links={"next": "next123", "prev": "prev456"},
            meta=PaginationMeta(
                path="/api/v1/words",
                per_page=10,
                next_cursor="next123",
                prev_cursor="prev456",
            ),
        )

        result = response_formatter.format_word_list(response)

        assert "Next cursor: next123" in result
        assert "Previous cursor: prev456" in result

    def test_format_word_list_includes_ids(
        self, response_formatter, sample_words_response
    ):
        """Test that word list includes word IDs."""
        result = response_formatter.format_word_list(sample_words_response)

        assert "[ID: 1]" in result
        assert "[ID: 2]" in result
        assert "[ID: 3]" in result


class TestFormatAllTranslations:
    """Tests for format_all_translations method."""

    def test_format_all_translations_from_english(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting all translations from English."""
        result = response_formatter.format_all_translations(
            sample_word_with_translation, "en"
        )

        assert "Translations for 'computer':" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result
        assert "Word ID: 1" in result

    def test_format_all_translations_from_spanish(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting all translations from Spanish."""
        result = response_formatter.format_all_translations(
            sample_word_with_translation, "es"
        )

        assert "Translations for 'computadora':" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result

    def test_format_all_translations_from_german(
        self, response_formatter, sample_word_with_translation
    ):
        """Test formatting all translations from German."""
        result = response_formatter.format_all_translations(
            sample_word_with_translation, "de"
        )

        assert "Translations for 'Computer':" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result

    def test_format_all_translations_structure(
        self, response_formatter, sample_word_with_translation
    ):
        """Test the structure of formatted translations."""
        result = response_formatter.format_all_translations(
            sample_word_with_translation, "en"
        )

        lines = result.split("\n")
        assert lines[0].startswith("Translations for")
        # Languages should be indented
        assert lines[1].startswith("  ")
        assert lines[2].startswith("  ")
        assert lines[3].startswith("  ")
        # Last two lines should be empty line and word ID
        assert lines[-2] == ""
        assert lines[-1].startswith("Word ID:")

    def test_format_all_translations_sorted(
        self, response_formatter, sample_word_with_translation
    ):
        """Test that translations are sorted alphabetically."""
        result = response_formatter.format_all_translations(
            sample_word_with_translation, "en"
        )

        lines = result.split("\n")
        # Skip header, check language order
        assert "German:" in lines[1]
        assert "English:" in lines[2]
        assert "Spanish:" in lines[3]

    def test_format_all_translations_without_translation(
        self, response_formatter, sample_word_without_translation
    ):
        """Test formatting all translations for word without translation data."""
        result = response_formatter.format_all_translations(
            sample_word_without_translation, "en"
        )

        assert "Translations for 'keyboard':" in result
        assert "English: keyboard" in result
        # Should not have other languages
        assert "Spanish:" not in result
        assert "German:" not in result

    def test_format_all_translations_with_unicode(self, response_formatter):
        """Test formatting with unicode characters."""
        word = Word(
            id=1,
            english_word="mouse",
            translation=Translation(
                id=1, word_id=1, spanish_word="ratón", german_word="Maus"
            ),
        )

        result = response_formatter.format_all_translations(word, "es")

        assert "Translations for 'ratón':" in result
        assert "Spanish: ratón" in result


class TestFormatterEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_format_empty_word_list(self, response_formatter):
        """Test formatting completely empty response."""
        response = WordsResponse(
            data=[],
            links={},
            meta=PaginationMeta(
                path="/test", per_page=10, next_cursor=None, prev_cursor=None
            ),
        )

        result = response_formatter.format_word_list(response)
        assert result == "No terms found"

    def test_format_search_empty_term(self, response_formatter):
        """Test formatting search with empty term."""
        result = response_formatter.format_search_results([], "")
        assert "No results found for ''" in result

    def test_format_translation_same_language(self, response_formatter):
        """Test formatting translation to same language."""
        result = response_formatter.format_translation(
            "computer", "en", "computer", "en"
        )
        assert result == "computer (en) → computer (en)"

    def test_format_word_with_long_translations(self, response_formatter):
        """Test formatting word with long translation strings."""
        word = Word(
            id=1,
            english_word="very_long_technical_term_in_english",
            translation=Translation(
                id=1,
                word_id=1,
                spanish_word="término_técnico_muy_largo_en_español",
                german_word="sehr_langer_technischer_Begriff_auf_Deutsch",
            ),
        )

        result = response_formatter.format_word_with_translations(word)
        assert "very_long_technical_term_in_english" in result
        assert "término_técnico_muy_largo_en_español" in result
        assert "sehr_langer_technischer_Begriff_auf_Deutsch" in result
