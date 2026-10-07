from typing import Final

DOMAIN: Final = "eurooil"
CONF_STATION_ID: Final = "station_id"
CONF_STATION_NAME: Final = "station_name"
CONF_PRODUCTS: Final = "products"

API_BASE_URL: Final = "https://srdcovka.eurooil.cz/api/verejne"
STATIONS_URL: Final = f"{API_BASE_URL}/cerpaci-stanice"
PRICES_URL: Final = f"{API_BASE_URL}/ceniky"

UPDATE_INTERVAL_MINUTES: Final = 30

# Public API EANs observed in the EuroOil app/API for these products.
PRODUCTS: Final = {
    "1": ("Diesel", "mdi:gas-station"),
    "3": ("Diesel Plus", "mdi:gas-station"),
    "4": ("Natural 95", "mdi:gas-station"),
    "5": ("BA 98 Super+", "mdi:gas-station"),
    "6": ("BA 91 Special", "mdi:gas-station"),
    "8": ("LPG PB", "mdi:gas-cylinder"),
    "9": ("Diesel Plus", "mdi:gas-station"),
    "11": ("Optimal BA95", "mdi:gas-station"),
    "15": ("CNG", "mdi:gas-cylinder"),
    "16": ("AdBlue", "mdi:water"),
    "204": ("HVO (XTL)", "mdi:gas-station"),
}
