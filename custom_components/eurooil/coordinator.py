"""Coordinator for EuroOil price updates."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EuroOilApiError, async_get_station_prices
from .const import DOMAIN, UPDATE_INTERVAL_MINUTES


class EuroOilCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetches all product prices for one station in a single API call."""

    def __init__(
        self, hass: HomeAssistant, station_id: int, station_name: str
    ) -> None:
        self.station_id = station_id
        self.station_name = station_name
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{DOMAIN} {station_name}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            return await async_get_station_prices(self.session, self.station_id)
        except EuroOilApiError as err:
            raise UpdateFailed(str(err)) from err
