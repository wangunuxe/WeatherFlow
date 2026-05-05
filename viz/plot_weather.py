import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB_CONFIG = {
    "host": "localhost", "port": 5433,
    "dbname": "weather", "user": "weather", "password": "weather123",
}

#pd.DataFram是 pandas 库提供的一种二维表格数据结构，就像一张 Excel 表
def load_data() -> pd.DataFrame:
    """
    Reads all data from the clean_weather table
    pd.read_sql() directly converts the query result into a DataFrame
    parse_dates=["date"] automatically converts the date column into a Python date type
    """
    sql = """
        SELECT city, date, temp_max_c, temp_min_c, precip_mm, weather_category
        FROM clean_weather
        ORDER BY date, city
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql(sql, conn, parse_dates=["date"])
    # parse_dates=["date"] 将日期（字符串类型）那一列转化为日期类型
def plot_temperature(df: pd.DataFrame):
    """
    Takes a DataFrame containing weather data for multiple cities
    and generates a two-panel chart:
    - Top panel: temperature trends (max/min) per city over time
    - Bottom panel: daily rainfall bar chart per city
    Saves the result as 'weather_trend.png' and displays it on screen.
    """
    # 创建一个画布和子图;给画布一个总标题
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("Weather Trends for 40 French Cities", fontsize=14, fontweight="bold")

    colors = {
    # 特大城市
        "Paris":         "#2196F3",
        "Marseille":     "#FF5722",
        "Lyon":          "#4CAF50",
        "Toulouse":      "#9C27B0",
        "Nice":          "#00BCD4",
        "Nantes":        "#FF9800",
        "Strasbourg":    "#E91E63",
        "Montpellier":   "#795548",
        "Bordeaux":      "#607D8B",
        "Lille":         "#FFEB3B",

        # 大城市
        "Rennes":        "#3F51B5",
        "Reims":         "#009688",
        "Le Havre":      "#FF5252",
        "Saint-Etienne": "#69F0AE",
        "Toulon":        "#40C4FF",
        "Grenoble":      "#FF6D00",
        "Dijon":         "#D500F9",
        "Angers":        "#00E676",
        "Nîmes":         "#F06292",
        "Villeurbanne":  "#4DB6AC",

        # 中等城市
        "Le Mans":       "#FFD740",
        "Aix-en-Provence": "#78909C",
        "Clermont-Ferrand": "#AED581",
        "Brest":         "#4FC3F7",
        "Tours":         "#CE93D8",
        "Amiens":        "#FFAB40",
        "Limoges":       "#80CBC4",
        "Annecy":        "#EF9A9A",
        "Perpignan":     "#A5D6A7",
        "Boulogne-Billancourt": "#90CAF9", 

        # 其他重要城市
        "Metz":          "#BCAAA4",
        "Besançon":      "#B39DDB",
        "Orléans":       "#80DEEA",
        "Rouen":         "#FFCC02",
        "Mulhouse":      "#FF8A65",
        "Caen":          "#A1887F",
        "Nancy":         "#DCE775",
        "Argenteuil":    "#4DD0E1", 
        "Montreuil":     "#F48FB1",
        "Pau":           "#81C784",
    }

    # 上图：温度趋势
    for city, color in colors.items(): #遍历 colors 字典，每次取出一个城市名和对应的颜色
        city_df = df[df["city"] == city] #  过滤该城市的数据
        ax1.fill_between(city_df["date"], city_df["temp_min_c"], city_df["temp_max_c"], alpha=0.15, color=color) # 在最低温和最高温之间填充半透明阴影，表示每天的温度范围
        ax1.plot(city_df["date"], city_df["temp_max_c"], color=color,
                 linewidth=2, label=f"{city} (MAX)") # 画最高温折线
        ax1.plot(city_df["date"], city_df["temp_min_c"], color=color,
                 linewidth=1, linestyle="--", alpha=0.7) #  画最低温折线

    ax1.set_ylabel("temperature (°C)") # Y轴标签
    ax1.legend(loc="upper left")  # 图例显示在左上角
    # 或者移到图表外面
    ax1.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=6)
    ax1.grid(alpha=0.3) # 显示淡淡的网格线

    # 下图：降雨量柱状图
    cities = df["city"].unique()  # get all unique city names
    width = 0.25 # width spacing between bars
    dates = df["date"].unique()

        # 遍历每个城市
    top_cities = list(colors.keys())[:5]
    for i, city in enumerate(cities):
        city_df = df[df["city"] == city].set_index("date")
        offsets = [d + pd.Timedelta(days=i * width - width) for d in dates]
        ax2.bar(offsets, [city_df.loc[d, "precip_mm"] if d in city_df.index else 0
                          for d in dates],
                width=0.2, label=city, color=list(colors.values())[i], alpha=0.8)

    ax2.set_ylabel("Rainfall (mm)")
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3, axis="y")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

    plt.tight_layout()
    plt.savefig("weather_trend.png", dpi=150, bbox_inches="tight")
    print("✅ Chart saved to weather_trend.png")
    plt.show()

if __name__ == "__main__":
    df = load_data()
    print(f"Rainfall：{len(df)} records，data limite：{df['date'].min()} ~ {df['date'].max()}")
    plot_temperature(df)