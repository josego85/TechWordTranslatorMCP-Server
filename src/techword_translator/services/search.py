"""Search service - Single Responsibility: Search and filter words."""

from typing import List, Optional

from ..models import Word
from .api_client import APIClient


class SearchService:
    """Service for searching words.

    Responsibility: Implement search logic across paginated results.
    """

    def __init__(self, api_client: APIClient):
        """Initialize search service.

        Args:
            api_client: API client to use for fetching data
        """
        self.api = api_client

    async def search_by_term(
        self, term: str, locale: Optional[str] = None, limit: int = 10
    ) -> List[Word]:
        """Search for words containing the given term.

        Args:
            term: Term to search for (case-insensitive)
            locale: Language to search in (en, es, de) or None for all
            limit: Maximum results to return

        Returns:
            List of matching Word objects
        """
        results: List[Word] = []
        cursor = None
        pages_checked = 0
        max_pages = 10

        term_lower = term.lower()

        while len(results) < limit and pages_checked < max_pages:
            response = await self.api.fetch_words(per_page=50, cursor=cursor)

            for word in response.data:
                if len(results) >= limit:
                    break

                # Load translation if needed
                if not word.translation:
                    word.translation = await self.api.fetch_translation(word.id)

                # Check if matches
                if self._matches_search(word, term_lower, locale):
                    results.append(word)

            if not response.meta.next_cursor:
                break

            cursor = response.meta.next_cursor
            pages_checked += 1

        return results[:limit]

    def _matches_search(self, word: Word, term_lower: str, locale: Optional[str]) -> bool:
        """Check if word matches search criteria.

        Args:
            word: Word to check
            term_lower: Lowercase search term
            locale: Language filter or None

        Returns:
            True if word matches
        """
        # Search in English
        if (locale is None or locale == "en") and term_lower in word.english_word.lower():
            return True

        # Search in other languages
        if word.translation:
            if (locale is None or locale == "es") and term_lower in word.translation.spanish_word.lower():
                return True

            if (locale is None or locale == "de") and term_lower in word.translation.german_word.lower():
                return True

        return False

    async def find_exact_match(
        self, term: str, locale: str
    ) -> Optional[Word]:
        """Find exact match for a term in a specific language.

        Args:
            term: Term to find
            locale: Language (en, es, de)

        Returns:
            Word if found, None otherwise
        """
        matches = await self.search_by_term(term, locale=locale, limit=1)
        return matches[0] if matches else None
