import os
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone

#调用路径？？？
# A dictionary containing all the information needed to connect to the database. Each value is read from an environment variable — if the variable is not set, it falls back to the default value on the right. The real values come from .env via docker-compose.yml.
DB_CONFIG = {
    "host":     os.getenv("WEATHER_DB_HOST", "weather-db"),
    "port":     int(os.getenv("WEATHER_DB_PORT", 5432)),
    "dbname":   os.getenv("WEATHER_DB_NAME", "weather"),
    "user":     os.getenv("WEATHER_DB_USER", "weather"),
    "password": os.getenv("WEATHER_DB_PASSWORD", "weather123"),
}


def get_conn():
    """
    Helper function that opens and returns a database connection
    """
    return psycopg2.connect(**DB_CONFIG)


def load_raw(records: list[dict]):
    """
    writing to the raw layer: load_raw() takes the cleaned records from extract.py;  no deduplication, as the raw layer's responsibility is to faithfully record the original data.
    """
    # If the exact same record already exists, skip it silently instead of raising an error. This makes it safe to re-run without creating duplicates, while still perserving the original data faithfully
    sql = """
        INSERT INTO raw_weather (city, date, temp_max, temp_min, precip_mm, wind_max, fetched_at)
        VALUES %s
        ON CONFLICT (city, date, fetched_at) DO NOTHING
    """
    # list of dict -> list of tuple
    rows = [(r["city"], r["date"], r["temp_max"], r["temp_min"],
             r["precip_mm"], r["wind_max"], r["fetched_at"]) for r in records]
    
    # rows = []
    # for r in records:
    #     row = (r["city"], r["date"], r["temp_max"], r["temp_min"],
    #         r["precip_mm"], r["wind_max"], r["fetched_at"])
    #     rows.append(row)

    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, rows)
    print(f"✅ raw layer: {len(rows)} records written")


def load_clean(records: list[dict]):
    """
    writing to the cleaned layer: load_clean() takes the cleaned records from transform.py and writes them to the clean_weather table using UPSERT; This makes the function idempotent — you can run it multiple times for the same day without creating duplicates or errors. It always guarantees that clean_weather contains the most up-to-date version of the data, ready for analysis or dashboards.
    """
    sql = """
        INSERT INTO clean_weather
            (city, date, temp_max_c, temp_min_c, temp_range_c,
             precip_mm, wind_max_kmh, weather_category, updated_at)
        VALUES %s
        ON CONFLICT (city, date) DO UPDATE SET
            temp_max_c       = EXCLUDED.temp_max_c,
            temp_min_c       = EXCLUDED.temp_min_c,
            temp_range_c     = EXCLUDED.temp_range_c,
            precip_mm        = EXCLUDED.precip_mm,
            wind_max_kmh     = EXCLUDED.wind_max_kmh,
            weather_category = EXCLUDED.weather_category,
            updated_at       = NOW()
    """
    rows = [(r["city"], r["date"], r["temp_max_c"], r["temp_min_c"], r["temp_range_c"],
             r["precip_mm"], r["wind_max_kmh"], r["weather_category"],
             datetime.now(timezone.utc).isoformat()) for r in records]

    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, rows)
    print(f"✅clean layer: {len(rows)} records upserted")