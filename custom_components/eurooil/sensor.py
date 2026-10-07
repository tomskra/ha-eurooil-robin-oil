"""EuroOil price sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PRODUCTS, CONF_STATION_ID, DOMAIN, PRODUCTS
from .coordinator import EuroOilCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up price entities for the configured station."""
    coordinator: EuroOilCoordinator = entry.runtime_data
    async_add_entities(
        EuroOilPriceSensor(coordinator, entry.data[CONF_STATION_ID], ean)
        for ean in entry.data.get(CONF_PRODUCTS, ("1", "3", "9"))
        if ean in PRODUCTS
    )


class EuroOilPriceSensor(CoordinatorEntity[EuroOilCoordinator], SensorEntity):
    """A single fuel price at a EuroOil station."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "Kč/l"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: EuroOilCoordinator,
        station_id: int,
        ean: str,
    ) -> None:
        super().__init__(coordinator)
        product_name, icon = PRODUCTS[ean]
        self._ean = ean
        self._attr_name = product_name
        self._attr_icon = icon
        self._attr_unique_id = f"{station_id}_{ean}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(station_id))},
            "name": f"EuroOil {coordinator.station_name}",
            "manufacturer": "EuroOil / ČEPRO",
        }

    @property
    def native_value(self) -> float | None:
        """Return current price in CZK per litre."""
        record = self.coordinator.data.get(self._ean)
        if record is None:
            return None
        price: Any = record.get("prodejniCena")
        return float(price) if price is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose API timestamps for freshness and validity."""
        record = self.coordinator.data.get(self._ean)
        if record is None:
            return {}
        return {
            "updated_at": record.get("aktualizovano"),
            "valid_from": record.get("platnostOd"),
            "valid_until": record.get("platnostDo"),
            "station_id": self.coordinator.station_id,
            "product_ean": self._ean,
        }
