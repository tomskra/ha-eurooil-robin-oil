"""Config flow for EuroOil."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EuroOilApiError, async_get_stations
from .const import CONF_PRODUCTS, CONF_STATION_ID, CONF_STATION_NAME, DOMAIN, PRODUCTS

_LOGGER = logging.getLogger(__name__)


class EuroOilConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up EuroOil for a selected fuel station."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Select a station from the public EuroOil station list."""
        try:
            stations = await async_get_stations(async_get_clientsession(self.hass))
        except EuroOilApiError:
            _LOGGER.exception("Could not fetch the EuroOil station list")
            return self.async_abort(reason="cannot_connect")

        self._stations = {
            int(station["cerpaciStaniceIID"]): station
            for station in stations
            if station.get("cerpaciStaniceIID") is not None
            and station.get("nazev")
            and not station.get("neaktivni")
        }
        if not self._stations:
            return self.async_abort(reason="no_stations")

        if user_input is not None:
            self._station_id = int(user_input[CONF_STATION_ID])
            self._station_name = self._stations[self._station_id]["nazev"]
            return await self.async_step_products()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION_ID): vol.In(
                        {
                            station_id: f"{station['nazev']} (ID {station_id})"
                            for station_id, station in self._stations.items()
                        }
                    )
                }
            ),
        )

    async def async_step_products(self, user_input: dict | None = None):
        """Select the fuel products available at the chosen station."""
        station = self._stations[self._station_id]
        available = {
            str(product["ean"]): PRODUCTS[str(product["ean"])]
            for product in station.get("produkty", [])
            if str(product.get("ean")) in PRODUCTS
        }
        if not available:
            return self.async_abort(reason="no_supported_products")

        if user_input is not None:
            selected_products = [
                code for code in user_input.get(CONF_PRODUCTS, []) if code in available
            ]
            if not selected_products:
                return self.async_show_form(
                    step_id="products",
                    data_schema=self._products_schema(available),
                    errors={"base": "select_product"},
                )
            await self.async_set_unique_id(f"station_{self._station_id}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Eurooil and Robin Oil prices - {self._station_name}",
                data={
                    CONF_STATION_ID: self._station_id,
                    CONF_STATION_NAME: self._station_name,
                    CONF_PRODUCTS: selected_products,
                },
            )

        return self.async_show_form(
            step_id="products",
            data_schema=self._products_schema(available),
        )

    @staticmethod
    def _products_schema(available: dict[str, tuple[str, str]]) -> vol.Schema:
        """Build a multi-select control with all supported station products selected."""
        return vol.Schema(
            {
                vol.Required(CONF_PRODUCTS, default=list(available)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": code, "label": product[0]}
                            for code, product in available.items()
                        ],
                        multiple=True,
                    )
                )
            }
        )
