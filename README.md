# 台灣一週氣溫預報系統 (CWA Weather Forecast)

這是一個基於中央氣象署 (CWA) 開放資料 API 所實作的台灣一週天氣預報統整與視覺化專案。專案包含了從資料擷取、處理、資料庫儲存，到前端 Web App 視覺化展示的完整流程。

## 專案功能與架構 (作業說明)

本專案分為四個主要部分：

### 1. 獲取天氣預報資料 (`cwa_weather_forecast.py`)
- **功能**: 使用 `requests` 調用 CWA API (資料集: `F-D0047-091`) 獲取台灣各鄉鎮的一週預報。
- **處理**: 依據行政區畫分，將全台 22 縣市歸納為「北部、中部、南部、東北部、東部、東南部」六大區域。
- **輸出**: 將原始的預報資料存為 `weather_raw.json` 及依地區分類的 `weather_by_region.json` 以供後續觀察與運用。

### 2. 分析並提取最高與最低氣溫 (`extract_temperature.py`)
- **功能**: 深度分析 CWA API 回傳的 JSON 階層結構，定位出目標資料 (WeatherElement 中的「最高溫度」與「最低溫度」)。
- **處理**: 提取各縣市每日/每時段的最高溫與最低溫數值。
- **輸出**: 在終端機彙整出各區的極端溫度表格，並將此重點溫度資料匯出為 `temperature_data.json`。

### 3. SQLite3 資料庫儲存與查詢 (`save_to_database.py`)
- **功能**: 建立輕量化關聯式資料庫系統。
- **處理**: 創建名為 `data.db` 的 SQLite 資料庫，建立 `TemperatureForecasts` 資料表。
- **資料表結構**:
  - `id` (主鍵)
  - `regionName` (地區名稱)
  - `dataDate` (時間)
  - `mint` (最低氣溫)
  - `maxt` (最高氣溫)
- **驗證**: 寫入約 280 筆資料後，並內建 SQL 腳本來驗證是否能正常查詢各區的地名及「中部」的所有氣溫資料。

### 4. 氣溫預報 Web App 視覺化 (`weather_app.py`)
- **功能**: 使用 **Streamlit** 框架建立互動式介面，直拉讀取 `data.db` 的資料。
- **互動地圖**: 採用 `folium` 生成類似「口罩地圖」的氣象圖，地圖上標有各區域，並依氣溫高低顯示不同熱力顏色；可以直接在地圖上觀看最高、最低溫與平均溫。
- **動態圖表**: 內建側邊欄下拉選單，選擇區域後會即時繪製最高溫/最低溫的「折線趨勢圖」。
- **檢視表格**: 將一週各時段詳細預報轉化為易讀的清單表格。

---

## 執行環境設定

1. **安裝依賴套件**:
   請確認您已經安裝以下 Python 套件：
   ```bash
   pip install requests pandas sqlite3 streamlit folium streamlit-folium
   ```

2. **執行 Web App**:
   透過 terminal 輸入以下指令啟動系統：
   ```bash
   python -m streamlit run weather_app.py
   ```
   系統將在瀏覽器 `http://localhost:8501` 自動開啟。

## 授權與資料來源

- 本專案使用的天氣資料由 [交通部中央氣象署氣象資料開放平臺](https://opendata.cwa.gov.tw/) 提供。
- 呼叫資料庫需使用個人的 Authorization Key。
