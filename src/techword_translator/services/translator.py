"""Translation service - Single Responsibility: Translate terms between languages."""

from typing import Optional

from .search import SearchService


class TranslatorService:
    """Service for translating terms.

    Responsibility: Coordinate translation between languages.
    """

    def __init__(self, search_service: SearchService):
        """Initialize translator service.

        Args:
            search_service: Search service to find words
        """
        self.search = search_service

    async def translate(
        self, term: str, from_locale: str, to_locale: str
    ) -> Optional[str]:
        """Translate a term from one language to another.

        Args:
            term: Term to translate
            from_locale: Source language (en, es, de)
            to_locale: Target language (en, es, de)

        Returns:
            Translated term or None if not found
        """
        # Find the word in source language
        word = await self.search.find_exact_match(term, from_locale)

        if not word:
            return None

        # Return translation in target language
        return word.get_translation(to_locale)
