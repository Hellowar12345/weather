"""
HW2-3: 將氣溫資料儲存到 SQLite3 資料庫
將氣溫資料儲存到 SQLite3 資料庫，以便後續查詢。
"""

import requests
import json
import sqlite3
import urllib3
import sys

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# 關閉 SSL 驗證警告（CWA 伺服器憑證問題）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
# 設定 CWA API 參數
# ============================================================
API_KEY = "CWA-C3D49702-79E1-4035-812F-EE485D61EEE3"
BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
DATASET_ID = "F-D0047-091"  # 鄉鎮天氣預報 - 臺灣未來1週天氣預報
DB_NAME = "data.db"
TABLE_NAME = "TemperatureForecasts"

# 定義台灣各區域對應的縣市
REGION_MAPPING = {
    "北部": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣"],
    "中部": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣", "澎湖縣"],
    "東北部": ["宜蘭縣"],
    "東部": ["花蓮縣"],
    "東南部": ["臺東縣"],
}

# 反向對應：縣市 -> 區域
CITY_TO_REGION = {}
for region, cities in REGION_MAPPING.items():
    for city in cities:
        CITY_TO_REGION[city] = region


# ============================================================
# Step 1: 調用 CWA API 獲取天氣預報資料
# ============================================================
def fetch_weekly_forecast():
    """
    調用 CWA API 獲取一週天氣預報資料。

    Returns:
        dict: API 回傳的 JSON 資料。
    """
    url = f"{BASE_URL}/{DATASET_ID}"
    params = {
        "Authorization": API_KEY,
        "format": "JSON",
    }

    print("正在調用 CWA API...")
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    print(f"HTTP 狀態碼: {response.status_code}")

    return response.json()


# ============================================================
# Step 2: 從 JSON 中提取氣溫資料
# ============================================================
def extract_temperature_records(data):
    """
    從天氣預報 JSON 資料中提取氣溫記錄。

    每筆記錄包含: regionName, dataDate, mint, maxt

    Args:
        data (dict): API 回傳的 JSON 資料。

    Returns:
        list[dict]: 氣溫記錄列表。
    """
    records = []
    all_locations = data["records"]["Locations"][0]["Location"]

    for location in all_locations:
        county = location["LocationName"]
        region = CITY_TO_REGION.get(county)
        if region is None:
            continue  # 跳過不在六大區域的縣市（如連江縣、金門縣）

        # 取得最高溫度與最低溫度的時段資料
        max_temps = {}
        min_temps = {}

        for elem in location["WeatherElement"]:
            if elem["ElementName"] == "最高溫度":
                for time_period in elem["Time"]:
                    start = time_period["StartTime"]
                    max_val = time_period["ElementValue"][0]["MaxTemperature"]
                    max_temps[start] = max_val

            elif elem["ElementName"] == "最低溫度":
                for time_period in elem["Time"]:
                    start = time_period["StartTime"]
                    min_val = time_period["ElementValue"][0]["MinTemperature"]
                    min_temps[start] = min_val

        # 合併同一時段的最高與最低溫度
        for start_time in sorted(max_temps.keys()):
            records.append({
                "regionName": region,
                "dataDate": start_time,
                "mint": int(min_temps.get(start_time, 0)),
                "maxt": int(max_temps.get(start_time, 0)),
            })

    return records


# ============================================================
# Step 3: 建立 SQLite3 資料庫與 Table
# ============================================================
def create_database():
    """
    建立 SQLite3 資料庫，並創建 TemperatureForecasts 資料表。

    Returns:
        sqlite3.Connection: 資料庫連線物件。
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 如果 Table 已存在則先刪除，確保資料是最新的
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    # 創建 TemperatureForecasts 資料表
    cursor.execute(f"""
        CREATE TABLE {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            mint INTEGER NOT NULL,
            maxt INTEGER NOT NULL
        )
    """)

    conn.commit()
    print(f"\n已建立資料庫: {DB_NAME}")
    print(f"已建立資料表: {TABLE_NAME}")

    return conn


# ============================================================
# Step 4: 將氣溫資料存入資料庫
# ============================================================
def insert_records(conn, records):
    """
    將氣溫記錄批次寫入資料庫。

    Args:
        conn (sqlite3.Connection): 資料庫連線物件。
        records (list[dict]): 氣溫記錄列表。
    """
    cursor = conn.cursor()

    cursor.executemany(
        f"INSERT INTO {TABLE_NAME} (regionName, dataDate, mint, maxt) VALUES (?, ?, ?, ?)",
        [(r["regionName"], r["dataDate"], r["mint"], r["maxt"]) for r in records]
    )

    conn.commit()
    print(f"已寫入 {len(records)} 筆氣溫資料")


# ============================================================
# Step 5: 查詢資料庫以檢查資料是否正確
# ============================================================
def verify_data(conn):
    """
    從資料庫查詢資料，驗證資料是否正確存入。

    查詢項目：
    1. 列出所有地區名稱
    2. 列出中部地區的氣溫資料

    Args:
        conn (sqlite3.Connection): 資料庫連線物件。
    """
    cursor = conn.cursor()

    # --- 查詢 1: 列出所有地區名稱 ---
    print("\n" + "=" * 60)
    print("查詢 1: 列出所有地區名稱")
    print("=" * 60)

    cursor.execute(f"SELECT DISTINCT regionName FROM {TABLE_NAME}")
    regions = cursor.fetchall()

    for row in regions:
        print(f"  - {row[0]}")

    print(f"\n共 {len(regions)} 個地區")

    # --- 查詢 2: 列出中部地區的氣溫資料 ---
    print("\n" + "=" * 60)
    print("查詢 2: 列出中部地區的氣溫資料")
    print("=" * 60)

    cursor.execute(
        f"SELECT id, regionName, dataDate, mint, maxt FROM {TABLE_NAME} WHERE regionName = ?",
        ("中部",)
    )
    rows = cursor.fetchall()

    print(f"\n  {'id':<5} {'地區':<8} {'時間':<30} {'最低溫(°C)':<12} {'最高溫(°C)':<12}")
    print(f"  {'─' * 65}")

    for row in rows:
        print(f"  {row[0]:<5} {row[1]:<8} {row[2]:<30} {row[3]:<12} {row[4]:<12}")

    print(f"\n共 {len(rows)} 筆中部地區資料")


# ============================================================
# 主程式
# ============================================================
def main():
    """主程式：獲取氣溫資料並存入 SQLite3 資料庫。"""

    # Step 1: 調用 CWA API 獲取天氣預報資料
    data = fetch_weekly_forecast()

    # Step 2: 提取氣溫記錄
    records = extract_temperature_records(data)
    print(f"\n共提取 {len(records)} 筆氣溫記錄")

    # 使用 json.dumps 觀察前幾筆資料
    print("\n提取的氣溫記錄範例（前 5 筆）：")
    print(json.dumps(records[:5], ensure_ascii=False, indent=2))

    # Step 3: 建立資料庫與資料表
    conn = create_database()

    # Step 4: 將資料存入資料庫
    insert_records(conn, records)

    # Step 5: 查詢資料庫，驗證資料是否正確
    verify_data(conn)

    # 關閉資料庫連線
    conn.close()
    print(f"\n資料庫連線已關閉。")


if __name__ == "__main__":
    main()
