import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import numpy as np

DB_CONFIG = {
    "host": "localhost", "port": 5433,
    "dbname": "weather", "user": "weather", "password": "weather123",
}

# pd.DataFrame is a 2D table data structure provided by the pandas library, like an Excel sheet
def load_data() -> pd.DataFrame:
    """
    Reads all data from the clean_weather table.
    pd.read_sql() directly converts the query result into a DataFrame.
    parse_dates=["date"] automatically converts the date column into a Python date type.
    """
    sql = """
        SELECT city, date, temp_max_c, temp_min_c, precip_mm, weather_category
        FROM clean_weather
        ORDER BY date, city
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql(sql, conn, parse_dates=["date"])


def plot_temperature(df: pd.DataFrame):
    """
    Takes a DataFrame containing weather data for multiple cities
    and generates a two-panel chart:
    - Top panel: average temperature band across all cities + individual city lines (thin)
    - Bottom panel: top 10 cities by total rainfall (grouped bar chart)
    Saves the result as 'weather_trend.png' and displays it on screen.
    """

    colors = {
        "Paris":                  "#2196F3",
        "Marseille":              "#FF5722",
        "Lyon":                   "#4CAF50",
        "Toulouse":               "#9C27B0",
        "Nice":                   "#00BCD4",
        "Nantes":                 "#FF9800",
        "Strasbourg":             "#E91E63",
        "Montpellier":            "#795548",
        "Bordeaux":               "#607D8B",
        "Lille":                  "#F9A825",
        "Rennes":                 "#3F51B5",
        "Reims":                  "#009688",
        "Le Havre":               "#FF5252",
        "Saint-Etienne":          "#69F0AE",
        "Toulon":                 "#40C4FF",
        "Grenoble":               "#FF6D00",
        "Dijon":                  "#D500F9",
        "Angers":                 "#00E676",
        "Nîmes":                  "#F06292",
        "Villeurbanne":           "#4DB6AC",
        "Le Mans":                "#FFD740",
        "Aix-en-Provence":        "#78909C",
        "Clermont-Ferrand":       "#AED581",
        "Brest":                  "#4FC3F7",
        "Tours":                  "#CE93D8",
        "Amiens":                 "#FFAB40",
        "Limoges":                "#80CBC4",
        "Annecy":                 "#EF9A9A",
        "Perpignan":              "#A5D6A7",
        "Boulogne-Billancourt":   "#90CAF9",
        "Metz":                   "#BCAAA4",
        "Besançon":               "#B39DDB",
        "Orléans":                "#80DEEA",
        "Rouen":                  "#FFCC02",
        "Mulhouse":               "#FF8A65",
        "Caen":                   "#A1887F",
        "Nancy":                  "#DCE775",
        "Argenteuil":             "#4DD0E1",
        "Montreuil":              "#F48FB1",
        "Pau":                    "#81C784",
    }

    # ── Style ────────────────────────────────────────────────
    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor("#F8F9FA")

    gs = gridspec.GridSpec(
        2, 1,
        figure=fig,
        height_ratios=[1.4, 1],
        hspace=0.35
    )
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    for ax in [ax1, ax2]:
        ax.set_facecolor("#FFFFFF")
        for spine in ax.spines.values():
            spine.set_edgecolor("#DDDDDD")

    fig.suptitle(
        "Weather Trends for 40 French Cities",
        fontsize=18, fontweight="bold",
        color="#1A1A2E", y=0.98
    )

    # ── TOP PANEL: Temperature ───────────────────────────────
    # Draw all city lines very thin and semi-transparent
    for city, color in colors.items():
        city_df = df[df["city"] == city]
        if city_df.empty:
            continue
        ax1.plot(
            city_df["date"], city_df["temp_max_c"],
            color=color, linewidth=0.8, alpha=0.4
        )
        ax1.plot(
            city_df["date"], city_df["temp_min_c"],
            color=color, linewidth=0.5, alpha=0.25, linestyle="--"
        )

    # Draw bold lines for the 5 most representative cities
    highlight_cities = ["Paris", "Marseille", "Lyon", "Lille", "Nice"]
    legend_elements = []
    for city in highlight_cities:
        city_df = df[df["city"] == city]
        if city_df.empty:
            continue
        color = colors[city]
        ax1.plot(
            city_df["date"], city_df["temp_max_c"],
            color=color, linewidth=2.5, alpha=1.0, label=city, zorder=5
        )
        ax1.plot(
            city_df["date"], city_df["temp_min_c"],
            color=color, linewidth=1.5, alpha=0.7, linestyle="--", zorder=5
        )
        legend_elements.append(
            Line2D([0], [0], color=color, linewidth=2.5, label=city)
        )

    # Draw the overall average temperature band
    avg_max = df.groupby("date")["temp_max_c"].mean()
    avg_min = df.groupby("date")["temp_min_c"].mean()
    ax1.fill_between(avg_max.index, avg_min, avg_max, alpha=0.08, color="#1A1A2E", label="_nolegend_")
    ax1.plot(avg_max.index, avg_max, color="#1A1A2E", linewidth=1.5,
             linestyle=":", alpha=0.5, label="National avg (MAX)")
    ax1.plot(avg_min.index, avg_min, color="#1A1A2E", linewidth=1,
             linestyle=":", alpha=0.35, label="National avg (MIN)")

    legend_elements += [
        Line2D([0], [0], color="#1A1A2E", linewidth=1.5, linestyle=":", label="National avg (MAX)"),
        Line2D([0], [0], color="#1A1A2E", linewidth=1, linestyle=":", alpha=0.5, label="National avg (MIN)"),
        Line2D([0], [0], color="gray", linewidth=0.8, alpha=0.4, label="Other cities (MAX)"),
    ]

    ax1.legend(
        handles=legend_elements,
        loc="upper left",
        fontsize=9,
        framealpha=0.9,
        edgecolor="#DDDDDD",
        ncol=2
    )
    ax1.set_ylabel("Temperature (°C)", fontsize=11, color="#444444")
    ax1.tick_params(colors="#666666")
    ax1.grid(alpha=0.3, linestyle="--")
    ax1.set_title(
        "Daily Max/Min Temperature — highlighted cities + national average",
        fontsize=10, color="#666666", pad=8
    )

    # ── BOTTOM PANEL: Rainfall ───────────────────────────────
    # Only show top 10 cities by total rainfall for readability
    total_precip = df.groupby("city")["precip_mm"].sum().sort_values(ascending=False)
    top10_cities = total_precip.head(10).index.tolist()

    dates = df["date"].unique()
    n = len(top10_cities)
    bar_width = 0.7 / n  # divide space among cities

    for i, city in enumerate(top10_cities):
        color = colors.get(city, "#AAAAAA")
        city_df = df[df["city"] == city].set_index("date")
        values = [city_df.loc[d, "precip_mm"] if d in city_df.index else 0 for d in dates]
        offsets = [d + pd.Timedelta(days=(i - n / 2) * bar_width) for d in dates]
        ax2.bar(offsets, values, width=bar_width * 0.85,
                label=city, color=color, alpha=0.85)

    ax2.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=5,
        fontsize=9,
        framealpha=0.9,
        edgecolor="#DDDDDD",
        title="Top 10 cities by total rainfall",
        title_fontsize=9
    )
    ax2.set_ylabel("Rainfall (mm)", fontsize=11, color="#444444")
    ax2.tick_params(colors="#666666")
    ax2.grid(alpha=0.3, linestyle="--", axis="y")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax2.set_title(
        "Daily Rainfall — Top 10 cities by total precipitation",
        fontsize=10, color="#666666", pad=8
    )

    # ── Shared X-axis formatting ─────────────────────────────
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    plt.subplots_adjust(bottom=0.15)
    plt.savefig("weather_trend.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print("✅ Chart saved to weather_trend.png")
    plt.show()


if __name__ == "__main__":
    df = load_data()
    print(f"Records: {len(df)}, Date range: {df['date'].min()} ~ {df['date'].max()}")
    plot_temperature(df)