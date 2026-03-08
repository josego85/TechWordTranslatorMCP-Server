"""Tests for ResponseFormatter."""

import pytest
from techword_translator.formatters import ResponseFormatter
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


class TestFormatTranslation:
    """Tests for format_translation method."""

    def test_english_to_spanish(self, response_formatter):
        result = response_formatter.format_translation("computer", "en", "computadora", "es")
        assert result == "computer (en) → computadora (es)"

    def test_spanish_to_german(self, response_formatter):
        result = response_formatter.format_translation("computadora", "es", "Computer", "de")
        assert result == "computadora (es) → Computer (de)"

    def test_german_to_english(self, response_formatter):
        result = response_formatter.format_translation("Computer", "de", "computer", "en")
        assert result == "Computer (de) → computer (en)"

    def test_special_chars(self, response_formatter):
        result = response_formatter.format_translation("C++", "en", "C++", "es")
        assert result == "C++ (en) → C++ (es)"

    def test_unicode(self, response_formatter):
        result = response_formatter.format_translation("mouse", "en", "ratón", "es")
        assert result == "mouse (en) → ratón (es)"


class TestFormatTranslationNotFound:
    """Tests for format_translation_not_found method."""

    def test_not_found_message(self, response_formatter):
        result = response_formatter.format_translation_not_found("nonexistent", "en", "es")
        assert result == "Translation not found for 'nonexistent' from en to es"

    def test_all_language_combinations(self, response_formatter):
        combinations = [
            ("test", "en", "es"),
            ("test", "en", "de"),
            ("prueba", "es", "en"),
            ("prueba", "es", "de"),
            ("Test", "de", "en"),
            ("Test", "de", "es"),
        ]
        for term, from_loc, to_loc in combinations:
            result = response_formatter.format_translation_not_found(term, from_loc, to_loc)
            assert f"'{term}'" in result
            assert f"from {from_loc}" in result
            assert f"to {to_loc}" in result


class TestFormatWordWithTranslations:
    """Tests for format_word_with_translations method."""

    def test_all_translations(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_word_with_translations(sample_word_with_translation)
        assert "de: Computer" in result
        assert "en: computer" in result
        assert "es: computadora" in result
        assert "|" in result

    def test_single_translation(self, response_formatter, sample_word_without_translation):
        result = response_formatter.format_word_with_translations(sample_word_without_translation)
        assert "en: keyboard" in result
        assert "es:" not in result
        assert "de:" not in result

    def test_alphabetical_order(self, response_formatter):
        word = make_word(1, "test", "prueba", "Test")
        result = response_formatter.format_word_with_translations(word)
        parts = result.split(" | ")
        assert parts[0].startswith("de:")
        assert parts[1].startswith("en:")
        assert parts[2].startswith("es:")

    def test_unicode(self, response_formatter):
        word = make_word(1, "mouse", "ratón", "Maus")
        result = response_formatter.format_word_with_translations(word)
        assert "es: ratón" in result


class TestFormatSearchResults:
    """Tests for format_search_results method."""

    def test_with_results(self, response_formatter, sample_words_list):
        result = response_formatter.format_search_results(sample_words_list, "test")
        assert "Found 3 result(s) for 'test':" in result
        assert "computer" in result
        assert "keyboard" in result
        assert "mouse" in result

    def test_no_results(self, response_formatter):
        result = response_formatter.format_search_results([], "nonexistent")
        assert result == "No results found for 'nonexistent'"

    def test_no_results_with_locale(self, response_formatter):
        result = response_formatter.format_search_results([], "test", locale="es")
        assert result == "No results found for 'test' in es"

    def test_single_result(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_search_results(
            [sample_word_with_translation], "computer"
        )
        assert "Found 1 result(s)" in result
        assert "computer" in result

    def test_numbering(self, response_formatter, sample_words_list):
        result = response_formatter.format_search_results(sample_words_list, "test")
        lines = [line for line in result.split("\n") if line.strip()]
        assert lines[1].startswith("1.")
        assert lines[2].startswith("2.")
        assert lines[3].startswith("3.")

    def test_includes_all_translations(self, response_formatter):
        word = make_word(1, "computer", "computadora", "Computer")
        result = response_formatter.format_search_results([word], "comp")
        assert "en: computer" in result
        assert "es: computadora" in result
        assert "de: Computer" in result


class TestFormatWordDetails:
    """Tests for format_word_details method."""

    def test_with_all_translations(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_word_details(sample_word_with_translation)
        assert "Word ID: 1" in result
        assert "Translations:" in result
        assert "[en] English: computer" in result
        assert "[es] Spanish: computadora" in result
        assert "[de] German: Computer" in result

    def test_single_translation(self, response_formatter, sample_word_without_translation):
        result = response_formatter.format_word_details(sample_word_without_translation)
        assert "Word ID: 2" in result
        assert "[en] English: keyboard" in result
        assert "Spanish:" not in result
        assert "German:" not in result

    def test_structure(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_word_details(sample_word_with_translation)
        lines = result.split("\n")
        assert lines[0].startswith("Word ID:")
        assert "[de]" in lines[3]
        assert "[en]" in lines[4]
        assert "[es]" in lines[5]

    def test_indentation(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_word_details(sample_word_with_translation)
        lines = result.split("\n")
        for line in lines[3:]:
            if line:
                assert line.startswith("  ")


class TestFormatWordList:
    """Tests for format_word_list method."""

    def test_with_data(self, response_formatter, sample_words_response):
        result = response_formatter.format_word_list(sample_words_response)
        assert "Showing 3 terms:" in result
        assert "1. [ID: 1]" in result
        assert "--- Pagination ---" in result
        assert "Next cursor: cursor123" in result

    def test_empty(self, response_formatter):
        response = WordsResponse(
            data=[],
            links={"next": None, "prev": None},
            meta=PaginationMeta(path="/api/v1/words", per_page=10),
        )
        assert response_formatter.format_word_list(response) == "No terms found"

    def test_no_pagination(self, response_formatter):
        response = WordsResponse(
            data=[make_word(1, "test", "prueba", "Test")],
            links={"next": None, "prev": None},
            meta=PaginationMeta(path="/api/v1/words", per_page=10),
        )
        result = response_formatter.format_word_list(response)
        assert "No more pages available" in result

    def test_with_prev_cursor(self, response_formatter):
        response = WordsResponse(
            data=[make_word(1, "test", "prueba", "Test")],
            links={"next": "next123", "prev": "prev456"},
            meta=PaginationMeta(
                path="/api/v1/words", per_page=10,
                next_cursor="next123", prev_cursor="prev456",
            ),
        )
        result = response_formatter.format_word_list(response)
        assert "Next cursor: next123" in result
        assert "Previous cursor: prev456" in result

    def test_includes_ids(self, response_formatter, sample_words_response):
        result = response_formatter.format_word_list(sample_words_response)
        assert "[ID: 1]" in result
        assert "[ID: 2]" in result
        assert "[ID: 3]" in result


class TestFormatAllTranslations:
    """Tests for format_all_translations method."""

    def test_from_english(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_all_translations(sample_word_with_translation, "en")
        assert "Translations for 'computer':" in result
        assert "English: computer" in result
        assert "Spanish: computadora" in result
        assert "German: Computer" in result
        assert "Word ID: 1" in result

    def test_from_spanish(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_all_translations(sample_word_with_translation, "es")
        assert "Translations for 'computadora':" in result

    def test_from_german(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_all_translations(sample_word_with_translation, "de")
        assert "Translations for 'Computer':" in result

    def test_sorted_alphabetically(self, response_formatter, sample_word_with_translation):
        result = response_formatter.format_all_translations(sample_word_with_translation, "en")
        lines = result.split("\n")
        assert "German:" in lines[1]
        assert "English:" in lines[2]
        assert "Spanish:" in lines[3]

    def test_with_unicode(self, response_formatter):
        word = make_word(1, "mouse", "ratón", "Maus")
        result = response_formatter.format_all_translations(word, "es")
        assert "Translations for 'ratón':" in result
        assert "Spanish: ratón" in result


class TestFormatterEdgeCases:
    """Tests for edge cases."""

    def test_empty_word_list(self, response_formatter):
        response = WordsResponse(
            data=[],
            links={},
            meta=PaginationMeta(path="/test", per_page=10),
        )
        assert response_formatter.format_word_list(response) == "No terms found"

    def test_search_empty_term(self, response_formatter):
        result = response_formatter.format_search_results([], "")
        assert "No results found for ''" in result

    def test_translation_same_language(self, response_formatter):
        result = response_formatter.format_translation("computer", "en", "computer", "en")
        assert result == "computer (en) → computer (en)"

    def test_long_translations(self, response_formatter):
        word = Word(
            id=1,
            word="very_long_technical_term_in_english",
            translations=[
                TranslationItem(language="en", translation="very_long_technical_term_in_english"),
                TranslationItem(language="es", translation="término_técnico_muy_largo_en_español"),
                TranslationItem(language="de", translation="sehr_langer_technischer_Begriff_auf_Deutsch"),
            ],
        )
        result = response_formatter.format_word_with_translations(word)
        assert "very_long_technical_term_in_english" in result
        assert "término_técnico_muy_largo_en_español" in result
        assert "sehr_langer_technischer_Begriff_auf_Deutsch" in result
