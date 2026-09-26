from datetime import datetime, timezone
import httpx
from .config import settings

DEMO_WEATHER = {
    "temperature_c": 34.0,
    "humidity_pct": 82.0,
    "wind_kmh": 18.0,
    "rain_probability_pct": 70.0,
    "source": "demo",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}


async def _geocode_area(area: str) -> tuple[float, float]:
    area = (area or "").strip()
    if not area:
        raise ValueError("An area name or latitude/longitude is required for live weather.")

    # The UI displays locations as "State - District", while the geocoder
    # resolves the district name more reliably on its own.
    if " - " in area:
        area = area.rsplit(" - ", 1)[-1].strip()

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": area, "count": 1, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    results = payload.get("results") or []
    if not results:
        raise ValueError(f"No location match found for area: {area}")

    first = results[0]
    return float(first["latitude"]), float(first["longitude"])


def _parse_time_minutes(value: str | None) -> int:
    if not value:
        return 0
    try:
        hour, minute = value.split(":", 1)
        return int(hour) * 60 + int(minute)
    except ValueError:
        return 0


def _pick_hourly_forecast(hourly: dict, target_date: str | None, target_time: str | None) -> tuple[int, str]:
    timestamps = hourly.get("time") or []
    if not timestamps:
        return 0, ""

    if target_date:
        candidate_times = [t for t in timestamps if t.startswith(target_date)]
        if candidate_times:
            timestamps = candidate_times

    if not target_time:
        return 0, timestamps[0]

    target_minutes = _parse_time_minutes(target_time)
    best_idx = min(range(len(timestamps)), key=lambda i: abs(_parse_time_minutes(timestamps[i][11:16]) - target_minutes))
    return best_idx, timestamps[best_idx]


async def get_weather(
    latitude: float | None,
    longitude: float | None,
    demo_mode: bool = False,
    *,
    target_date: str | None = None,
    target_time: str | None = None,
    area: str | None = None,
) -> dict:
    try:
        if area:
            latitude, longitude = await _geocode_area(area)
        elif latitude is None or longitude is None:
            if demo_mode and settings.demo_weather_enabled:
                return {**DEMO_WEATHER, "warning": "Demo weather. Enter an area or coordinates for live weather."}
            raise ValueError("Latitude and longitude are required for live weather.")

        target_date = target_date or datetime.now(timezone.utc).date().isoformat()
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability",
            "start_date": target_date,
            "end_date": target_date,
            "timezone": "auto",
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        hourly = payload.get("hourly", {})
        index, selected_time = _pick_hourly_forecast(hourly, target_date, target_time)
        temperature = (hourly.get("temperature_2m") or [0])[index]
        humidity = (hourly.get("relative_humidity_2m") or [0])[index]
        wind = (hourly.get("wind_speed_10m") or [0])[index]
        rain = (hourly.get("precipitation_probability") or [0])[index]

        return {
            "temperature_c": float(temperature or 0),
            "humidity_pct": float(humidity or 0),
            "wind_kmh": float(wind or 0),
            "rain_probability_pct": float(rain or 0),
            "source": "Open-Meteo",
            "timestamp": selected_time or datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        if demo_mode and settings.demo_weather_enabled:
            return {**DEMO_WEATHER, "warning": f"Live weather unavailable; demo weather used: {type(exc).__name__}"}
        raise RuntimeError("Live weather service is unavailable. Reassess when weather data is available.") from exc
