# 台灣天氣預報作業 — Prompt 互動紀錄

> **Repository:** https://github.com/Hellowar12345/weather  
> **建立日期:** 2026-04-28  
> **作業說明:** 使用 CWA API 獲取台灣六大區域一週天氣預報，分析氣溫資料，儲存至 SQLite3，並以 Streamlit 建立互動式 Web App

---

## 作業架構總覽

| 作業 | 檔案 | 功能 | 配分 |
|------|------|------|------|
| HW2-1 | `cwa_weather_forecast.py` | 獲取 CWA API 天氣預報資料 | 20% |
| HW2-2 | `extract_temperature.py` | 分析並提取最高/最低氣溫 | 20% |
| HW2-3 | `save_to_database.py` | 儲存氣溫資料至 SQLite3 | 20% |
| HW2-4 | `weather_app.py` | Streamlit 氣溫預報 Web App | 40% |

---

## Step 1 — HW2-1：獲取天氣預報資料

### Prompt

```
i want to 獲取天氣預報資料
使用 CWA API 獲取台灣北部、中部、南部、東北部、東部及東南部地區一週的天氣預報資料（必須是 JSON 格式）。

方法：
使用 Requests 套件調用 CWA API，獲取天氣預報資料。
使用 json.dumps 觀察獲得的資料

評分比重：
調用 CWA API 獲取天氣預報資料（10%）
觀察獲得的資料（5%）
程式碼結構與可讀性（5%）
```

### 完成內容

產生 `cwa_weather_forecast.py`，完成以下功能：

- **API 設定**
  - 使用 `F-D0047-091` 資料集（鄉鎮天氣預報 — 臺灣未來 1 週天氣預報）
  - `verify=False` 搭配 `urllib3.disable_warnings()` 繞過 SSL 憑證問題
  - Authorization Key 以常數 `API_KEY` 管理

- **六大區域對應表** (`REGION_MAPPING`)
  - 北部：基隆市、臺北市、新北市、桃園市、新竹市、新竹縣
  - 中部：苗栗縣、臺中市、彰化縣、南投縣、雲林縣
  - 南部：嘉義市、嘉義縣、臺南市、高雄市、屏東縣、澎湖縣
  - 東北部：宜蘭縣
  - 東部：花蓮縣
  - 東南部：臺東縣

- **主要函式**
  - `fetch_weekly_forecast()` — 調用 CWA API，回傳 JSON dict
  - `display_raw_json()` — 用 `json.dumps` 輸出前 2000 字元觀察原始結構
  - `organize_by_region()` — 解析 `records.Locations[0].Location[]`，依區域分類
  - `display_regional_forecast()` — 列印各縣市天氣現象、最高/最低溫摘要
  - `display_region_json()` — 用 `json.dumps` 輸出各區域 JSON
  - `save_json_file()` — 將資料儲存為 JSON 檔案

- **輸出檔案**
  - `weather_raw.json` — 原始 API 回傳資料
  - `weather_by_region.json` — 依區域分類後的資料

---

## Step 2 — HW2-2：分析資料，提取最高與最低氣溫

### Prompt

```
[Provide the Python code snippet for weather.py, as in the conversation.]
```

*(此步驟為提供基礎程式碼後，進一步分析 JSON 階層結構並提取氣溫資料)*

### 完成內容

產生 `extract_temperature.py`，完成以下功能：

- **JSON 結構分析** (`analyze_json_structure()`)
  - 印出 `WeatherElement` 列表中各項目名稱，標記「最高溫度」與「最低溫度」位置
  - 完整路徑：  
    `data["records"]["Locations"][0]["Location"][i]["WeatherElement"][?]["Time"][t]["ElementValue"][0]["MaxTemperature"]`
  - 顯示第一個縣市第一個時段的實際範例值

- **氣溫提取** (`extract_temperature_data()`)
  - 遍歷所有縣市，依 `REGION_MAPPING` 歸類
  - 對每個縣市提取所有時段的最高溫/最低溫（含 `StartTime`、`EndTime`、`溫度`）
  - 回傳按區域分類的字典

- **資料觀察**
  - `display_temperature_json()` — 用 `json.dumps` 顯示各區第一個縣市完整資料，及前 3000 字元
  - `display_temperature_summary()` — 彙整各縣市整週最高/最低溫表格

- **輸出檔案**
  - `temperature_data.json` — 提取後的氣溫資料

---

## Step 3 — 儲存至指定 CSV

### Prompt

```
save the output the weather_data.csv
```

*(此步驟在原始對話中用於確認輸出檔案名稱，最終版本改為儲存 JSON 與 SQLite3，CSV 需求於此確認)*

---

## Step 4 — HW2-3：將氣溫資料儲存到 SQLite3 資料庫

### Prompt

*(承接 HW2-2 產出的氣溫資料，建立資料庫儲存流程)*

### 完成內容

產生 `save_to_database.py`，完成以下功能：

- **資料庫設定**
  - 資料庫名稱：`data.db`
  - 資料表名稱：`TemperatureForecasts`

- **資料表結構**

  | 欄位 | 型別 | 說明 |
  |------|------|------|
  | `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 主鍵 |
  | `regionName` | TEXT NOT NULL | 地區名稱（北部/中部/南部等） |
  | `dataDate` | TEXT NOT NULL | 預報開始時間 |
  | `mint` | INTEGER NOT NULL | 最低氣溫 (°C) |
  | `maxt` | INTEGER NOT NULL | 最高氣溫 (°C) |

- **主要函式**
  - `extract_temperature_records()` — 從 API JSON 提取結構化氣溫記錄（含反向對應 `CITY_TO_REGION`），跳過金門、連江等不在六大區域的縣市
  - `create_database()` — 建立 `data.db`，`DROP TABLE IF EXISTS` 確保資料最新
  - `insert_records()` — `executemany` 批次寫入，共約 **280 筆**
  - `verify_data()` — 兩項驗證查詢：
    1. `SELECT DISTINCT regionName` — 列出所有地區
    2. `WHERE regionName = '中部'` — 列出中部所有氣溫資料

- **執行流程**
  1. 調用 CWA API → 2. 提取氣溫記錄 → 3. 建立資料庫 → 4. 寫入資料 → 5. 驗證查詢

---

## Step 5 — HW2-4：建立 Streamlit Web App（含互動地圖）

### Prompt

```
i want to display these data on streamlit, but i need a dynamic web with taiwan map such as 
https://www.cwa.gov.tw/V8/C/W/OBS_Temp.html, please suggest me how to do it
```

### 完成內容（初版）

產生 `weather_app.py`（Streamlit + Folium），功能：

- **頁面設定**：`st.set_page_config(layout="wide")`，標題「台灣氣溫預報」
- **地圖互動**：使用 Folium，以台灣為中心（`[23.65, 120.95]`，zoom=8）
  - CartoDB positron 底圖 + OpenStreetMap 圖層切換
  - 每個區域：半透明彩色圓圈（溫度覆蓋範圍）+ HTML 標籤標記（含 ▲最高/▼最低）+ 可點擊 CircleMarker（Popup 資訊卡）
  - 顏色梯度：`#2c3e50` (< 22°C) → `#3498db` → `#2ecc71` → `#f1c40f` → `#f39c12` → `#e67e22` → `#e74c3c` (>= 33°C)
  - 溫度圖例固定在地圖左下角

- **資料庫查詢**（`@st.cache_data(ttl=300)`）
  - `get_all_regions()` — 查詢所有地區名稱
  - `get_region_data(region_name)` — 查詢指定地區氣溫
  - `get_all_data()` — 查詢全部資料
  - `get_region_summary()` — 計算各區域統計摘要（平均/最高/最低）

---

## Step 6 — 調整為左右版面配置

### Prompt

```
i want left-right layout
```

### 完成內容（最終版）

`weather_app.py` 最終版面架構：

```
+-----------------------------------------------------------------------+
|  台灣氣溫預報 Web App                                                  |
|  資料來源：中央氣象署 CWA｜一週天氣預報                                |
+------------+----------------------------------------------------------+
| Sidebar    |  地圖總覽（Folium 互動地圖）                              |
|            +----------------------------------------------------------+
| 地區選擇   |  {地區} 一週氣溫預報                                      |
| (selectbox)|  [最高溫] [最低溫] [平均高] [平均低]  (4欄 metric card)   |
|            +----------------------------------------------------------+
| 地區列表   |  氣溫趨勢折線圖                                            |
|            |  (最高氣溫 紅線 / 最低氣溫 藍線)                          |
|            +----------------------------------------------------------+
|            |  詳細資料表格                                             |
|            |  [ID | 地區 | 時間 | 最低(°C) | 最高(°C)]                |
+------------+----------------------------------------------------------+
```

- **側邊欄**：`st.selectbox` 下拉選單選擇地區，顯示目前選中區域
- **指標卡片**：4 欄 `st.columns`，漸層背景，紅/藍/橙/青配色
- **折線圖**：`st.line_chart`，按時間分組取平均，紅色最高溫 + 藍色最低溫
- **資料表格**：`st.dataframe`，格式化時間欄（`%m/%d %H:%M`），`NumberColumn` 加 `°C` 後綴
- **自訂 CSS**：`@import` Noto Sans TC 字型，漸層標題、metric-card 樣式

---

## 執行環境

```bash
# 安裝依賴
pip install requests pandas streamlit folium streamlit-folium

# 依序執行
python cwa_weather_forecast.py   # 獲取並儲存 API 資料
python extract_temperature.py    # 分析並提取氣溫資料
python save_to_database.py       # 建立 data.db 並寫入資料

# 啟動 Web App
python -m streamlit run weather_app.py
# 開啟瀏覽器 http://localhost:8501
```

---

## 專案檔案結構

```
weather/
├── cwa_weather_forecast.py   # HW2-1：獲取天氣預報資料
├── extract_temperature.py    # HW2-2：提取最高/最低氣溫
├── save_to_database.py       # HW2-3：儲存至 SQLite3
├── weather_app.py            # HW2-4：Streamlit Web App
├── data.db                   # SQLite3 資料庫（約 280 筆）
├── weather_raw.json          # 原始 CWA API 回傳資料
├── weather_by_region.json    # 依區域分類的天氣資料
├── temperature_data.json     # 提取後的氣溫資料
├── .gitignore
└── README.md
```

---

## All-in-One Prompt（最終完整版）

> 以下為可一次性生成完整專案的 prompt：

```
Create a complete Python project to fetch 7-day weather forecast data for Taiwan's northern, 
central, southern, northeastern, eastern, and southeastern regions using the CWA API 
(specifically the F-D0047-091 endpoint for agricultural weather forecasts), parse the JSON 
response to extract temperature data (min and max), save it to a CSV file named 
"weather_data.csv", and build an interactive Streamlit web app with a left-right layout 
featuring a Folium-based Taiwan map where regions are marked with colored circles based on 
average temperature (blue <20°C, green 20-25°C, yellow 25-30°C, red >30°C), a date selector 
dropdown to filter data dynamically, and a data table on the right side showing the selected 
date's temperatures; ensure the app handles SSL verification issues, uses approximate region 
coordinates for markers, and includes popups with region details; set up the Python virtual 
environment, install necessary packages (requests, pandas, streamlit, folium), validate the 
code by running it to fetch and display data, and make the app runnable via Streamlit.
```

---

## 技術要點記錄

| 問題 | 解決方式 |
|------|---------|
| CWA SSL 憑證錯誤 | `requests.get(..., verify=False)` + `urllib3.disable_warnings()` |
| JSON 中文輸出亂碼 | `json.dumps(..., ensure_ascii=False)` |
| Windows 終端機中文 | `sys.stdout.reconfigure(encoding="utf-8")` |
| 資料庫資料重複 | `DROP TABLE IF EXISTS` 每次執行前清除 |
| Streamlit 快取 | `@st.cache_data(ttl=300)` 避免每次互動重新查詢 |
| 地圖底圖選擇 | CartoDB positron（簡潔）+ OpenStreetMap（備用切換） |

---

*此 log 由 Antigravity 根據 GitHub repo `Hellowar12345/weather` 原始碼及作業說明重建*
