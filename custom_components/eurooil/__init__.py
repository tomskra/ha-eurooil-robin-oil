"""EuroOil Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_STATION_ID, CONF_STATION_NAME
from .coordinator import EuroOilCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a EuroOil station config entry."""
    coordinator = EuroOilCoordinator(
        hass,
        entry.data[CONF_STATION_ID],
        entry.data[CONF_STATION_NAME],
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a EuroOil station config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
