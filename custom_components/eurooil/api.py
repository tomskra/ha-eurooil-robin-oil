"""Small async client for the public EuroOil station and price API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import PRICES_URL, STATIONS_URL


class EuroOilApiError(Exception):
    """Raised when the EuroOil API returns invalid or unavailable data."""


async def _get_data(session: aiohttp.ClientSession, url: str) -> list[dict[str, Any]]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
        raise EuroOilApiError(f"Unable to retrieve EuroOil data from {url}") from err

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise EuroOilApiError("EuroOil API returned an unexpected response")
    return payload["data"]


async def async_get_stations(session: aiohttp.ClientSession) -> list[dict[str, Any]]:
    """Return the public station list."""
    return await _get_data(session, STATIONS_URL)


async def async_get_station_prices(
    session: aiohttp.ClientSession, station_id: int
) -> dict[str, dict[str, Any]]:
    """Return current price records indexed by product EAN for one station."""
    rows = await _get_data(session, PRICES_URL)
    return {
        str(row["ean"]): row
        for row in rows
        if row.get("cerpaciStaniceIID") == station_id and row.get("ean") is not None
    }
