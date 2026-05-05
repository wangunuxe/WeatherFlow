import requests
import json
from datetime import datetime, timezone

CITIES = {
    # 特大城市
    "Paris":        {"lat": 48.8566, "lon": 2.3522},
    "Marseille":    {"lat": 43.2965, "lon": 5.3698},
    "Lyon":         {"lat": 45.7640, "lon": 4.8357},
    "Toulouse":     {"lat": 43.6047, "lon": 1.4442},
    "Nice":         {"lat": 43.7102, "lon": 7.2620},
    "Nantes":       {"lat": 47.2184, "lon": -1.5536},
    "Strasbourg":   {"lat": 48.5734, "lon": 7.7521},
    "Montpellier":  {"lat": 43.6119, "lon": 3.8772},
    "Bordeaux":     {"lat": 44.8378, "lon": -0.5792},
    "Lille":        {"lat": 50.6292, "lon": 3.0573},

    # 大城市
    "Rennes":       {"lat": 48.1173, "lon": -1.6778},
    "Reims":        {"lat": 49.2583, "lon": 4.0317},
    "Le Havre":     {"lat": 49.4944, "lon": 0.1079},
    "Saint-Etienne":{"lat": 45.4397, "lon": 4.3872},
    "Toulon":       {"lat": 43.1242, "lon": 5.9280},
    "Grenoble":     {"lat": 45.1885, "lon": 5.7245},
    "Dijon":        {"lat": 47.3220, "lon": 5.0415},
    "Angers":       {"lat": 47.4784, "lon": -0.5632},
    "Nîmes":        {"lat": 43.8367, "lon": 4.3601},
    "Villeurbanne": {"lat": 45.7676, "lon": 4.8800},

    # 中等城市
    "Le Mans":      {"lat": 48.0061, "lon": 0.1996},
    "Aix-en-Provence": {"lat": 43.5297, "lon": 5.4474},
    "Clermont-Ferrand": {"lat": 45.7772, "lon": 3.0870},
    "Brest":        {"lat": 48.3904, "lon": -4.4861},
    "Tours":        {"lat": 47.3941, "lon": 0.6848},
    "Amiens":       {"lat": 49.8941, "lon": 2.2958},
    "Limoges":      {"lat": 45.8336, "lon": 1.2611},
    "Annecy":       {"lat": 45.8992, "lon": 6.1294},
    "Perpignan":    {"lat": 42.6986, "lon": 2.8956},
    "Boulogne-Billancourt": {"lat": 48.8350, "lon": 2.2400},

    # 其他重要城市
    "Metz":         {"lat": 49.1193, "lon": 6.1757},
    "Besançon":     {"lat": 47.2380, "lon": 6.0243},
    "Orléans":      {"lat": 47.9029, "lon": 1.9039},
    "Rouen":        {"lat": 49.4432, "lon": 1.0993},
    "Mulhouse":     {"lat": 47.7508, "lon": 7.3359},
    "Caen":         {"lat": 49.1829, "lon": -0.3707},
    "Nancy":        {"lat": 48.6921, "lon": 6.1844},
    "Argenteuil":   {"lat": 48.9472, "lon": 2.2467},
    "Montreuil":    {"lat": 48.8638, "lon": 2.4483},
    "Pau":          {"lat": 43.2951, "lon": -0.3708},
}

def fetch_weather(city_name: str, lat: float, lon: float) -> dict:
    """
    Call the Open-Meteo API to fetch the last 90 days of daily weather data.
    Completely free — no account or API key required.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
        ],
        "timezone":   "Europe/Paris",
        "past_days":  90,
        "forecast_days": 1,
    }
    # The Response class
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # If the status code is not 200, raise a execption immdiately and Airflow will catch it and retry
    return response.json() # Converts the raw response (just a string in format JSON) text into a python dictionary


def extract_all_cities() -> list[dict]:
    """
    extract_all_cities() loops through all three cities and calls fetch_weather() for each one, which returns a dictionary containing the raw API response. -> "raw" is the full dictionary, which contains several keys

    raw["daily"] picks out the value associated with the key "daily" — which is the nested dictionary containing all the weather data. -> "daily = raw["daily"] " is also a dictionary

    The API response is column-oriented — meaning all the dates are stored in one list, all the max temperatures in another list, and so on. However, a database expects row-oriented data — one complete record per day. So the function uses enumerate() to loop through the dates by index, and uses that index i to pick the matching value from each of the other lists, building one dictionary per day.

    Each dictionary is then appended to the records list. After all three cities are processed, records contains 24 dictionaries in total (8 days * 3 cities), each representing one city's weather on one specific day
    """
    records = []
    for city_name, coords in CITIES.items():
        raw = fetch_weather(city_name, coords["lat"], coords["lon"])
        daily = raw["daily"]

        for i, date_str in enumerate(daily["time"]):
            records.append({
                "city":        city_name,
                "date":        date_str,
                "temp_max":    daily["temperature_2m_max"][i],
                "temp_min":    daily["temperature_2m_min"][i],
                "precip_mm":   daily["precipitation_sum"][i],
                "wind_max":    daily["windspeed_10m_max"][i],
                "fetched_at":  datetime.now(timezone.utc).isoformat(),  # Record fetch time to help identify duplicates
            })

    print(f"✅ Extraction complete — {len(records)} records fetched.")
    return records


if __name__ == "__main__":
    data = extract_all_cities()
    #json.dumps() converts the Python dictionary into JSON string
    print(json.dumps(data[:2], indent=2, ensure_ascii=False))