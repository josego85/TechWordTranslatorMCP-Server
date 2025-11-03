"""Output formatters - Single Responsibility: Format data for display."""

from typing import List, Optional

from .models import Word, WordsResponse


class ResponseFormatter:
    """Formats API responses into user-friendly strings.

    Responsibility: Convert data models into readable text.
    """

    @staticmethod
    def format_translation(term: str, from_locale: str, translated: str, to_locale: str) -> str:
        """Format a translation result.

        Args:
            term: Original term
            from_locale: Source language
            translated: Translated term
            to_locale: Target language

        Returns:
            Formatted string
        """
        return f"{term} ({from_locale}) → {translated} ({to_locale})"

    @staticmethod
    def format_translation_not_found(term: str, from_locale: str, to_locale: str) -> str:
        """Format 'not found' message.

        Args:
            term: Original term
            from_locale: Source language
            to_locale: Target language

        Returns:
            Error message
        """
        return f"Translation not found for '{term}' from {from_locale} to {to_locale}"

    @staticmethod
    def format_word_with_translations(word: Word) -> str:
        """Format a word with all its translations.

        Args:
            word: Word to format

        Returns:
            Formatted string with all translations
        """
        translations = word.get_all_translations()
        trans_list = [f"{lang}: {term}" for lang, term in sorted(translations.items())]
        return " | ".join(trans_list)

    @staticmethod
    def format_search_results(words: List[Word], search_term: str, locale: Optional[str] = None) -> str:
        """Format search results.

        Args:
            words: List of matching words
            search_term: Search term used
            locale: Language filter used (if any)

        Returns:
            Formatted results string
        """
        if not words:
            locale_msg = f" in {locale}" if locale else ""
            return f"No results found for '{search_term}'{locale_msg}"

        lines = [f"Found {len(words)} result(s) for '{search_term}':\n"]

        for idx, word in enumerate(words, 1):
            formatted = ResponseFormatter.format_word_with_translations(word)
            lines.append(f"{idx}. {formatted}")

        return "\n".join(lines)

    @staticmethod
    def format_word_details(word: Word) -> str:
        """Format detailed word information.

        Args:
            word: Word to format

        Returns:
            Detailed string representation
        """
        lines = [f"Word ID: {word.id}"]
        lines.append("\nTranslations:")

        translations = word.get_all_translations()
        lang_names = {"en": "English", "es": "Spanish", "de": "German"}

        for locale, term in sorted(translations.items()):
            lang_name = lang_names.get(locale, locale)
            lines.append(f"  [{locale}] {lang_name}: {term}")

        return "\n".join(lines)

    @staticmethod
    def format_word_list(response: WordsResponse) -> str:
        """Format paginated word list.

        Args:
            response: API response with words

        Returns:
            Formatted list with pagination info
        """
        if not response.data:
            return "No terms found"

        lines = [f"Showing {len(response.data)} terms:\n"]

        for idx, word in enumerate(response.data, 1):
            formatted = ResponseFormatter.format_word_with_translations(word)
            lines.append(f"{idx}. [ID: {word.id}] {formatted}")

        lines.append("\n--- Pagination ---")
        if response.meta.next_cursor:
            lines.append(f"Next cursor: {response.meta.next_cursor}")
        if response.meta.prev_cursor:
            lines.append(f"Previous cursor: {response.meta.prev_cursor}")
        if not response.meta.next_cursor and not response.meta.prev_cursor:
            lines.append("No more pages available")

        return "\n".join(lines)

    @staticmethod
    def format_all_translations(word: Word, source_locale: str) -> str:
        """Format all translations for a term.

        Args:
            word: Word with translations
            source_locale: Source language

        Returns:
            Formatted translations string
        """
        source_term = word.get_translation(source_locale)
        lines = [f"Translations for '{source_term}':"]

        translations = word.get_all_translations()
        lang_names = {"en": "English", "es": "Spanish", "de": "German"}

        for locale, term in sorted(translations.items()):
            lang_name = lang_names.get(locale, locale)
            lines.append(f"  {lang_name}: {term}")

        lines.append(f"\nWord ID: {word.id}")
        return "\n".join(lines)
