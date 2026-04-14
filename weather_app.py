"""
HW2-4: 氣溫預報 Web App
使用 Streamlit 建立氣溫預報 Web App，視覺化氣溫資料。
功能：下拉選單選擇地區、折線圖與表格、互動式地圖、從 SQLite3 資料庫查詢資料。
"""

import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="台灣氣溫預報",
    page_icon="🌡️",
    layout="wide",
)

# ============================================================
# 常數設定
# ============================================================
DB_NAME = "data.db"
TABLE_NAME = "TemperatureForecasts"

# 各區域的代表經緯度（用於地圖標記）
REGION_COORDINATES = {
    "北部": {"lat": 25.0330, "lon": 121.5654, "cities": "基隆、臺北、新北、桃園、新竹"},
    "中部": {"lat": 24.1477, "lon": 120.6736, "cities": "苗栗、臺中、彰化、南投、雲林"},
    "南部": {"lat": 22.6273, "lon": 120.3014, "cities": "嘉義、臺南、高雄、屏東、澎湖"},
    "東北部": {"lat": 24.7570, "lon": 121.7530, "cities": "宜蘭"},
    "東部": {"lat": 23.9910, "lon": 121.6016, "cities": "花蓮"},
    "東南部": {"lat": 22.7583, "lon": 121.1444, "cities": "臺東"},
}

# 溫度顏色對照
def get_temp_color(temp):
    """根據溫度回傳對應的標記顏色。"""
    if temp >= 33:
        return "red"
    elif temp >= 30:
        return "orange"
    elif temp >= 27:
        return "beige"
    elif temp >= 24:
        return "green"
    elif temp >= 20:
        return "blue"
    else:
        return "darkblue"


# ============================================================
# 資料庫查詢函式
# ============================================================
@st.cache_data(ttl=300)
def get_all_regions():
    """從 SQLite 資料庫查詢所有地區名稱。"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        f"SELECT DISTINCT regionName FROM {TABLE_NAME}",
        conn
    )
    conn.close()
    return df["regionName"].tolist()


@st.cache_data(ttl=300)
def get_region_data(region_name):
    """從 SQLite 資料庫查詢指定地區的氣溫資料。"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        f"SELECT id, regionName, dataDate, mint, maxt FROM {TABLE_NAME} WHERE regionName = ?",
        conn,
        params=(region_name,)
    )
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_all_data():
    """從 SQLite 資料庫查詢所有地區的氣溫資料。"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        f"SELECT id, regionName, dataDate, mint, maxt FROM {TABLE_NAME}",
        conn
    )
    conn.close()
    return df


def get_region_summary():
    """取得各區域的氣溫統計摘要（用於地圖）。"""
    all_data = get_all_data()
    summary = {}
    for region in all_data["regionName"].unique():
        region_df = all_data[all_data["regionName"] == region]
        summary[region] = {
            "avg_max": round(region_df["maxt"].mean(), 1),
            "avg_min": round(region_df["mint"].mean(), 1),
            "max": region_df["maxt"].max(),
            "min": region_df["mint"].min(),
            "records": len(region_df),
        }
    return summary


# ============================================================
# 自訂 CSS 樣式
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    .stApp {
        font-family: 'Noto Sans TC', sans-serif;
    }

    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
    }

    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    .metric-card h3 {
        margin: 0;
        font-size: 0.9rem;
        color: #666;
    }

    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }

    .high-temp { color: #e74c3c; }
    .low-temp { color: #3498db; }
    .avg-temp { color: #f39c12; }

    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        border-left: 4px solid #667eea;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 主頁面
# ============================================================
st.markdown('<div class="main-title">🌡️ 台灣氣溫預報 Web App</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">資料來源：中央氣象署 CWA｜一週天氣預報</div>', unsafe_allow_html=True)

# --- 側邊欄：地區選擇 ---
with st.sidebar:
    st.markdown("## 🗺️ 地區選擇")
    regions = get_all_regions()
    selected_region = st.selectbox(
        "請選擇地區",
        options=regions,
        index=0,
        help="從下拉選單選擇要查看的地區"
    )
    st.markdown("---")
    st.markdown("### 📋 地區列表")
    for r in regions:
        icon = "📍" if r == selected_region else "  "
        st.markdown(f"{icon} {r}")

    st.markdown("---")
    st.markdown(
        "<small>資料庫：data.db<br>資料表：TemperatureForecasts</small>",
        unsafe_allow_html=True
    )


# ============================================================
# 上方：互動式地圖
# ============================================================
st.markdown('<div class="section-header">🗺️ 氣溫地圖總覽</div>', unsafe_allow_html=True)
st.caption("點擊標記查看詳細資訊，圓圈顏色代表平均最高溫度")

summary = get_region_summary()

# 各區域覆蓋半徑（公里，用於視覺化範圍）
REGION_RADIUS = {
    "北部": 35000,
    "中部": 35000,
    "南部": 40000,
    "東北部": 25000,
    "東部": 30000,
    "東南部": 30000,
}

def get_temp_hex_color(temp):
    """根據溫度回傳漸層 HEX 色碼（藍→綠→黃→橘→紅）。"""
    if temp >= 33:
        return "#e74c3c"
    elif temp >= 31:
        return "#e67e22"
    elif temp >= 29:
        return "#f39c12"
    elif temp >= 27:
        return "#f1c40f"
    elif temp >= 25:
        return "#2ecc71"
    elif temp >= 22:
        return "#3498db"
    else:
        return "#2c3e50"

# 建立 Folium 地圖（以台灣為中心，較深的底圖）
m = folium.Map(
    location=[23.65, 120.95],
    zoom_start=8,
    tiles="CartoDB positron",
    min_zoom=7,
    max_zoom=12,
)

# 加入備用圖層切換
folium.TileLayer("OpenStreetMap", name="街道地圖").add_to(m)
folium.LayerControl(position="topright").add_to(m)

for region, coords in REGION_COORDINATES.items():
    if region in summary:
        s = summary[region]
        hex_color = get_temp_hex_color(s["avg_max"])
        radius = REGION_RADIUS.get(region, 30000)
        is_selected = (region == selected_region)

        # --- 1. 半透明彩色圓圈（溫度覆蓋區域）---
        folium.Circle(
            location=[coords["lat"], coords["lon"]],
            radius=radius,
            color=hex_color,
            fill=True,
            fill_color=hex_color,
            fill_opacity=0.20 if not is_selected else 0.35,
            weight=2 if not is_selected else 4,
            dash_array="5" if not is_selected else None,
        ).add_to(m)

        # --- 2. 溫度標籤（直接顯示在地圖上）---
        label_html = f"""
        <div style="
            background: {'linear-gradient(135deg, #667eea, #764ba2)' if is_selected else 'rgba(255,255,255,0.92)'};
            color: {'#fff' if is_selected else '#2c3e50'};
            border: 2px solid {hex_color};
            border-radius: 10px;
            padding: 4px 8px;
            font-family: 'Noto Sans TC', Arial, sans-serif;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            backdrop-filter: blur(4px);
        ">
            <div style="font-size: 13px; margin-bottom: 2px;">{'📍 ' if is_selected else ''}{region}</div>
            <div>
                <span style="color: {'#ffd5d5' if is_selected else '#e74c3c'};">▲{s['max']}°</span>
                <span style="color: {'#d5e8ff' if is_selected else '#3498db'};">▼{s['min']}°</span>
            </div>
        </div>
        """
        folium.Marker(
            location=[coords["lat"], coords["lon"]],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(100, 50),
                icon_anchor=(50, 25),
            ),
        ).add_to(m)

        # --- 3. 隱藏的可點擊標記（帶 popup 資訊卡片）---
        popup_html = f"""
        <div style="font-family: 'Noto Sans TC', Arial, sans-serif; width: 220px;">
            <h4 style="margin:0; color:#fff; background: linear-gradient(135deg, {hex_color}, #2c3e50);
                       padding: 8px 12px; border-radius: 8px 8px 0 0; font-size: 16px;">
                🌡️ {region}
            </h4>
            <div style="padding: 10px 12px; background: #fafafa; border-radius: 0 0 8px 8px; border: 1px solid #eee;">
                <p style="margin: 4px 0; color: #888; font-size: 12px;">📍 {coords['cities']}</p>
                <hr style="margin: 6px 0; border: none; border-top: 1px solid #eee;">
                <table style="width:100%; font-size: 14px;">
                    <tr>
                        <td style="padding: 3px 0;">🔺 一週最高溫</td>
                        <td style="text-align:right; font-weight:bold; color:#e74c3c; font-size:16px;">{s['max']}°C</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px 0;">🔻 一週最低溫</td>
                        <td style="text-align:right; font-weight:bold; color:#3498db; font-size:16px;">{s['min']}°C</td>
                    </tr>
                    <tr><td colspan="2"><hr style="margin:4px 0; border:none; border-top:1px dashed #ddd;"></td></tr>
                    <tr>
                        <td style="padding: 3px 0; color:#666;">📊 平均高溫</td>
                        <td style="text-align:right; color:#e67e22;">{s['avg_max']}°C</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px 0; color:#666;">📊 平均低溫</td>
                        <td style="text-align:right; color:#2980b9;">{s['avg_min']}°C</td>
                    </tr>
                </table>
                <p style="margin: 6px 0 0 0; font-size: 11px; color: #bbb; text-align: right;">
                    共 {s['records']} 筆預報資料
                </p>
            </div>
        </div>
        """

        # 透明圓形標記（較大點擊區域）
        folium.CircleMarker(
            location=[coords["lat"], coords["lon"]],
            radius=18,
            color="transparent",
            fill=True,
            fill_color="transparent",
            fill_opacity=0,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"點擊查看 {region} 詳細氣溫",
        ).add_to(m)

# --- 4. 自訂溫度圖例 ---
legend_html = """
<div style="
    position: fixed;
    bottom: 30px; left: 30px;
    background: rgba(255,255,255,0.92);
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 10px 14px;
    font-family: 'Noto Sans TC', Arial, sans-serif;
    font-size: 12px;
    z-index: 9999;
    box-shadow: 0 2px 10px rgba(0,0,0,0.12);
    backdrop-filter: blur(4px);
">
    <div style="font-weight:700; margin-bottom:6px; font-size:13px;">🌡️ 溫度圖例</div>
    <div><span style="background:#e74c3c;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> ≥ 33°C 極熱</div>
    <div><span style="background:#e67e22;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> 31-32°C 炎熱</div>
    <div><span style="background:#f39c12;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> 29-30°C 溫暖</div>
    <div><span style="background:#f1c40f;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> 27-28°C 舒適</div>
    <div><span style="background:#2ecc71;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> 25-26°C 涼爽</div>
    <div><span style="background:#3498db;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> 22-24°C 偏涼</div>
    <div><span style="background:#2c3e50;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:5px;vertical-align:middle;"></span> &lt; 22°C 寒冷</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width="stretch", height=480)


# ============================================================
# 中間：指標卡片
# ============================================================
st.markdown(f'<div class="section-header">📊 {selected_region}地區 — 一週氣溫預報</div>', unsafe_allow_html=True)

region_df = get_region_data(selected_region)

if not region_df.empty:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 一週最高溫</h3>
            <div class="value high-temp">{region_df['maxt'].max()}°C</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔵 一週最低溫</h3>
            <div class="value low-temp">{region_df['mint'].min()}°C</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 平均最高溫</h3>
            <div class="value avg-temp">{round(region_df['maxt'].mean(), 1)}°C</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📉 平均最低溫</h3>
            <div class="value" style="color: #1abc9c;">{round(region_df['mint'].mean(), 1)}°C</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ============================================================
    # 折線圖
    # ============================================================
    st.markdown('<div class="section-header">📈 氣溫趨勢折線圖</div>', unsafe_allow_html=True)

    # 處理日期時間
    chart_df = region_df.copy()
    chart_df["dataDate"] = pd.to_datetime(chart_df["dataDate"])

    # 按時間分組取平均（同區域可能有多個縣市資料）
    chart_grouped = chart_df.groupby("dataDate").agg(
        最高氣溫=("maxt", "mean"),
        最低氣溫=("mint", "mean"),
    ).reset_index()
    chart_grouped = chart_grouped.sort_values("dataDate")

    # 使用 Streamlit 內建折線圖
    st.line_chart(
        chart_grouped.set_index("dataDate")[["最高氣溫", "最低氣溫"]],
        color=["#e74c3c", "#3498db"],
        width="stretch",
    )

    # ============================================================
    # 資料表格
    # ============================================================
    st.markdown('<div class="section-header">📋 詳細資料表格</div>', unsafe_allow_html=True)

    display_df = region_df.copy()
    display_df.columns = ["ID", "地區", "時間", "最低氣溫(°C)", "最高氣溫(°C)"]
    display_df["時間"] = pd.to_datetime(display_df["時間"]).dt.strftime("%m/%d %H:%M")

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "地區": st.column_config.TextColumn("地區", width="small"),
            "時間": st.column_config.TextColumn("時間", width="medium"),
            "最低氣溫(°C)": st.column_config.NumberColumn(
                "最低氣溫(°C)",
                format="%d°C",
            ),
            "最高氣溫(°C)": st.column_config.NumberColumn(
                "最高氣溫(°C)",
                format="%d°C",
            ),
        }
    )

    st.caption(f"共 {len(display_df)} 筆資料，來源：SQLite3 資料庫 (data.db)")

else:
    st.warning(f"找不到 {selected_region} 的資料，請先執行 save_to_database.py 建立資料庫。")
