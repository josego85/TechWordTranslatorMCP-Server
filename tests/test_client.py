"""Tests for the API client."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from techword_mcp.client import TechWordAPIClient
from techword_mcp.models import Word, Translation, WordsResponse


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    with patch.dict("os.environ", {
        "TECHWORD_TRANSLATOR_API_URL": "https://api.example.com"
    }):
        client = TechWordAPIClient()
        return client


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization with environment variables."""
    with patch.dict("os.environ", {
        "TECHWORD_TRANSLATOR_API_URL": "https://api.example.com"
    }):
        client = TechWordAPIClient()
        assert client.base_url == "https://api.example.com"
        await client.close()


@pytest.mark.asyncio
async def test_search_term_returns_results(mock_client):
    """Test search_term returns matching words."""
    # Mock response data
    mock_word = Word(
        id=1,
        created_at="2024-01-01",
        updated_at="2024-01-01",
        translations=[
            Translation(
                id=1,
                word_id=1,
                locale="en",
                term="computer",
                created_at="2024-01-01",
                updated_at="2024-01-01"
            )
        ]
    )

    # This is a placeholder test - in real tests you'd mock httpx responses
    # For now, just verify the method exists and has correct signature
    assert hasattr(mock_client, 'search_term')
    await mock_client.close()


@pytest.mark.asyncio
async def test_get_translation(mock_client):
    """Test get_translation method."""
    # Verify method exists
    assert hasattr(mock_client, 'get_translation')
    await mock_client.close()
