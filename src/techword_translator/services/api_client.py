"""API client module - Single Responsibility: Make HTTP requests to the API."""

import os
from typing import Optional
import httpx
from dotenv import load_dotenv

from ..models import Word, WordsResponse, Translation

load_dotenv()


class APIClient:
    """Simple HTTP client for TechWordTranslator API.

    Responsibility: Make HTTP requests and return parsed responses.
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client.

        Args:
            base_url: Base URL for the API (defaults to env TECHWORD_TRANSLATOR_API_URL)
        """
        self.base_url = (base_url or os.getenv("TECHWORD_TRANSLATOR_API_URL", "")).rstrip("/")

        if not self.base_url:
            raise ValueError("TECHWORD_TRANSLATOR_API_URL must be set")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def fetch_words(
        self, per_page: int = 15, cursor: Optional[str] = None
    ) -> WordsResponse:
        """Fetch words from API.

        Args:
            per_page: Number of words per page
            cursor: Pagination cursor

        Returns:
            WordsResponse with data and metadata
        """
        params = {"per_page": per_page}
        if cursor:
            params["cursor"] = cursor

        response = await self.client.get("/api/v1/words", params=params)
        response.raise_for_status()

        data = response.json()
        words = [Word(**word_data) for word_data in data["data"]]

        return WordsResponse(
            data=words,
            links=data.get("links", {}),
            meta=data["meta"]
        )

    async def fetch_word(self, word_id: int) -> Word:
        """Fetch a single word by ID.

        Args:
            word_id: ID of the word

        Returns:
            Word object
        """
        response = await self.client.get(f"/api/v1/words/{word_id}")
        response.raise_for_status()

        return Word(**response.json())

    async def fetch_translation(self, word_id: int) -> Optional[Translation]:
        """Fetch translation for a word.

        Args:
            word_id: ID of the word

        Returns:
            Translation object or None if not found
        """
        try:
            response = await self.client.get(f"/api/v1/translations/{word_id}")
            response.raise_for_status()
            return Translation(**response.json())
        except httpx.HTTPError:
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
