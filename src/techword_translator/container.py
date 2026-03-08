"""Service container — manages singleton service instances."""

from contextlib import asynccontextmanager
from typing import Optional

from .services import APIClient, SearchService, TranslatorService

_api_client: Optional[APIClient] = None
_search_service: Optional[SearchService] = None
_translator_service: Optional[TranslatorService] = None


@asynccontextmanager
async def get_services():
    """Yield (api_client, search_service, translator_service), creating them once."""
    global _api_client, _search_service, _translator_service

    if _api_client is None:
        _api_client = APIClient()
        _search_service = SearchService(_api_client)
        _translator_service = TranslatorService(_search_service)

    yield _api_client, _search_service, _translator_service
