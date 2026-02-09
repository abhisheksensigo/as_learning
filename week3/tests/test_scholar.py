from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scholar import (
    _uninvert_abstract,
    _search_research_by_countries,
    _countries_to_search,
    search_research,
    search_news,
    fred_data_lookup,
    UNSUPPORTED_MSG,
)


def test_uninvert_abstract_empty():
    """_uninvert_abstract returns empty string for empty/None input."""
    assert _uninvert_abstract(None) == ""
    assert _uninvert_abstract({}) == ""


def test_uninvert_abstract_simple():
    """_uninvert_abstract converts inverted index to plain text."""
    idx = {"the": [0], "quick": [1], "brown": [2], "fox": [3]}
    assert _uninvert_abstract(idx) == "the quick brown fox"


def test_uninvert_abstract_multiple_positions():
    """_uninvert_abstract handles words with multiple positions."""
    idx = {"a": [0, 2], "b": [1]}
    assert _uninvert_abstract(idx) == "a b a"


def test_countries_to_search_empty_returns_both():
    """Empty country returns both Argentina and Ireland."""
    assert _countries_to_search("") == ["Argentina", "Ireland"]
    assert _countries_to_search("   ") == ["Argentina", "Ireland"]


def test_countries_to_search_argentina():
    """Argentina returns [Argentina]."""
    assert _countries_to_search("Argentina") == ["Argentina"]
    assert _countries_to_search("argentina") == ["Argentina"]


def test_countries_to_search_ireland():
    """Ireland returns [Ireland]."""
    assert _countries_to_search("Ireland") == ["Ireland"]
    assert _countries_to_search("ireland") == ["Ireland"]


def test_countries_to_search_unsupported():
    """Unsupported country returns error message."""
    assert _countries_to_search("France") == UNSUPPORTED_MSG
    assert _countries_to_search("Brazil") == UNSUPPORTED_MSG


@pytest.mark.asyncio
async def test_search_research_empty_topic():
    """_search_research_by_countries returns [] for empty topic."""
    result = await _search_research_by_countries("", ["Argentina"])
    assert result == []

    result = await _search_research_by_countries("   ", ["Argentina"])
    assert result == []


@pytest.mark.asyncio
async def test_search_research_inflation_topic():
    """_search_research_by_countries returns results for valid topic."""
    result = await _search_research_by_countries("inflation", ["Argentina"])
    assert result != []

    result = await _search_research_by_countries("gdp growth", ["Argentina"])
    assert result != []


@pytest.mark.asyncio
async def test_search_research_response_related_to_country():
    """Verify the returned results contain country-related content."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "display_name": "Economic Policy in Argentina: Inflation and Debt",
                "publication_date": "2024-01-15",
                "doi": "10.1234/example",
                "abstract_inverted_index": {"Argentina": [0], "economy": [1]},
            }
        ]
    }

    with patch("scholar.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )
        results = await _search_research_by_countries("inflation", ["Argentina"])

    assert len(results) == 1
    combined = f"{results[0]['title']} {results[0]['summary']} {results[0]['link']}".lower()
    assert "argentina" in combined


@pytest.mark.asyncio
async def test_search_research_with_timeline_filter():
    """Verify timeline_filter adds from_publication_date and to_publication_date to OpenAlex request."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}

    mock_get = AsyncMock(return_value=mock_response)

    with patch("scholar.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await _search_research_by_countries("inflation", ["Argentina"], "in 2024")

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    params = call_kwargs.get("params", {})
    assert "filter" in params
    assert "from_publication_date:2024-01-01" in params["filter"]
    assert "to_publication_date:2024-12-31" in params["filter"]


@pytest.mark.asyncio
async def test_search_research_without_timeline_filter():
    """Verify no filter param when timeline_filter is empty."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}

    mock_get = AsyncMock(return_value=mock_response)

    with patch("scholar.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await _search_research_by_countries("inflation", ["Argentina"])

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    params = call_kwargs.get("params", {})
    assert "filter" not in params


@pytest.mark.asyncio
async def test_search_research_unsupported_country():
    """search_research returns graceful message for unsupported country."""
    result = await search_research("inflation", country="France")
    assert result == UNSUPPORTED_MSG


@pytest.mark.asyncio
async def test_search_news_unsupported_country():
    """search_news returns graceful message for unsupported country."""
    result = await search_news("inflation", country="Brazil")
    assert result == UNSUPPORTED_MSG


@pytest.mark.asyncio
async def test_search_research_both_countries_makes_two_calls():
    """When country is empty, search both Argentina and Ireland (two API calls)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}

    mock_get = AsyncMock(return_value=mock_response)

    with patch("scholar.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await _search_research_by_countries("inflation", ["Argentina", "Ireland"])

    assert mock_get.call_count == 2
    calls = mock_get.call_args_list
    params0 = calls[0].kwargs.get("params", {})
    params1 = calls[1].kwargs.get("params", {})
    searches = [params0.get("search", ""), params1.get("search", "")]
    assert "Argentina inflation" in searches
    assert "Ireland inflation" in searches


@pytest.mark.asyncio
async def test_fred_data_lookup_needs_input():
    """fred_data_lookup returns message when neither search_text nor series_id provided."""
    result = await fred_data_lookup()
    assert "search_text" in result or "series_id" in result


@pytest.mark.asyncio
async def test_fred_data_lookup_search():
    """fred_data_lookup with search_text returns series table."""
    with patch("scholar.fred.search_series", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {"id": "GDPC1", "title": "Real GDP", "frequency": "Quarterly", "units": "Bil.", "observation_start": "1947-01-01", "observation_end": "2024-01-01"}
        ]
        result = await fred_data_lookup(search_text="GDP")
        assert "GDPC1" in result
        assert "Real GDP" in result


@pytest.mark.asyncio
async def test_fred_data_lookup_observations():
    """fred_data_lookup with series_id returns observations table."""
    with patch("scholar.fred.get_observations", new_callable=AsyncMock) as mock_obs:
        mock_obs.return_value = [{"date": "2024-01-01", "value": "28.5"}]
        result = await fred_data_lookup(series_id="GDPC1")
        assert "2024-01-01" in result
        assert "28.5" in result


@pytest.mark.asyncio
async def test_search_research_ireland_query():
    """Verify Ireland is used in the search query."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}

    mock_get = AsyncMock(return_value=mock_response)

    with patch("scholar.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get
        await _search_research_by_countries("inflation", ["Ireland"])

    mock_get.assert_called_once()
    params = mock_get.call_args.kwargs.get("params", {})
    assert "Ireland inflation" in params["search"]