from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import news


@pytest.mark.asyncio
async def test_search_news_response_related_to_country():
    """Verify the returned results contain country-related content."""
    mock_response = MagicMock()
    mock_response.text = "20260204183000,eng,https://example.com/argentina-inflation-article\n"

    with patch("news.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )
        results = await news._search_news_by_countries("inflation", ["Argentina"])

    assert len(results) == 1
    combined = f"{results[0]['title']} {results[0]['link']}".lower()
    assert "argentina" in combined


@pytest.mark.asyncio
async def test_search_news_with_timeline_filter():
    """Verify timeline_filter adds lastminutes to GDELT query."""
    mock_response = MagicMock()
    mock_response.text = "20260204183000,eng,https://example.com/article\n"

    mock_get = AsyncMock(return_value=mock_response)

    with patch("news.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await news._search_news_by_countries("inflation", ["Argentina"], "last month")

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    params = call_kwargs.get("params", {})
    assert "lastminutes:43200" in params["query"]  # 30 * 24 * 60


@pytest.mark.asyncio
async def test_search_news_without_timeline_filter():
    """Verify query has no lastminutes when timeline_filter is empty."""
    mock_response = MagicMock()
    mock_response.text = "20260204183000,eng,https://example.com/article\n"

    mock_get = AsyncMock(return_value=mock_response)

    with patch("news.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await news._search_news_by_countries("inflation", ["Argentina"])

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    params = call_kwargs.get("params", {})
    assert "lastminutes" not in params["query"]


@pytest.mark.asyncio
async def test_search_news_timeline_in_2024_ignored():
    """GDELT doesn't support 'in 2024' - lastminutes should not be added."""
    mock_response = MagicMock()
    mock_response.text = "20260204183000,eng,https://example.com/article\n"

    mock_get = AsyncMock(return_value=mock_response)

    with patch("news.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await news._search_news_by_countries("inflation", ["Argentina"], "in 2024")

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    params = call_kwargs.get("params", {})
    assert "lastminutes" not in params["query"]


@pytest.mark.asyncio
async def test_search_news_ireland_query():
    """Verify Ireland is used in the GDELT query."""
    mock_response = MagicMock()
    mock_response.text = "20260204183000,eng,https://example.com/ireland-economy\n"

    mock_get = AsyncMock(return_value=mock_response)

    with patch("news.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await news._search_news_by_countries("inflation", ["Ireland"])

    mock_get.assert_called_once()
    params = mock_get.call_args.kwargs.get("params", {})
    assert "Ireland inflation" in params["query"]
