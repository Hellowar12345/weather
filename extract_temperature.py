"""
HW2-2: 分析資料，提取最高與最低氣溫的資料
分析天氣預報資料的 JSON 格式，找出最高與最低氣溫的資料位置，並提取出來。
"""

import requests
import json
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

# 定義台灣各區域對應的縣市
REGION_MAPPING = {
    "北部": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣"],
    "中部": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣", "澎湖縣"],
    "東北部": ["宜蘭縣"],
    "東部": ["花蓮縣"],
    "東南部": ["臺東縣"],
}


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
# 分析 JSON 結構，說明最高與最低氣溫的資料位置
# ============================================================
def analyze_json_structure(data):
    """
    分析 JSON 資料結構，找出最高與最低氣溫的資料位置。

    JSON 資料結構路徑：
      data
      └─ records
         └─ Locations[0]
            └─ Location[]              ← 各縣市
               ├─ LocationName         ← 縣市名稱
               └─ WeatherElement[]     ← 天氣要素列表
                  ├─ ElementName: "最高溫度"  ← 最高氣溫
                  │  └─ Time[]               ← 各時段
                  │     ├─ StartTime
                  │     ├─ EndTime
                  │     └─ ElementValue[0]
                  │        └─ MaxTemperature  ← 最高溫度值
                  └─ ElementName: "最低溫度"  ← 最低氣溫
                     └─ Time[]
                        ├─ StartTime
                        ├─ EndTime
                        └─ ElementValue[0]
                           └─ MinTemperature  ← 最低溫度值

    Args:
        data (dict): API 回傳的 JSON 資料。
    """
    print("\n" + "=" * 60)
    print("JSON 資料結構分析 — 最高與最低氣溫位置")
    print("=" * 60)

    # 取第一個縣市作為範例分析
    location = data["records"]["Locations"][0]["Location"][0]
    county_name = location["LocationName"]
    print(f"\n以「{county_name}」為例，觀察 WeatherElement 列表：")

    for i, elem in enumerate(location["WeatherElement"]):
        elem_name = elem["ElementName"]
        marker = " << 目標" if elem_name in ("最高溫度", "最低溫度") else ""
        print(f"  [{i}] ElementName: {elem_name}{marker}")

    # 顯示最高溫度的完整路徑範例
    for elem in location["WeatherElement"]:
        if elem["ElementName"] == "最高溫度":
            print(f"\n最高溫度的完整資料路徑：")
            print(f'  data["records"]["Locations"][0]["Location"][0]'
                  f'["WeatherElement"][?]["Time"][0]["ElementValue"][0]["MaxTemperature"]')
            sample = elem["Time"][0]
            print(f"\n  範例：{county_name} 第一個時段")
            print(f"    StartTime: {sample['StartTime']}")
            print(f"    EndTime:   {sample['EndTime']}")
            print(f"    MaxTemperature: {sample['ElementValue'][0]['MaxTemperature']}°C")
            break

    for elem in location["WeatherElement"]:
        if elem["ElementName"] == "最低溫度":
            print(f"\n最低溫度的完整資料路徑：")
            print(f'  data["records"]["Locations"][0]["Location"][0]'
                  f'["WeatherElement"][?]["Time"][0]["ElementValue"][0]["MinTemperature"]')
            sample = elem["Time"][0]
            print(f"\n  範例：{county_name} 第一個時段")
            print(f"    StartTime: {sample['StartTime']}")
            print(f"    EndTime:   {sample['EndTime']}")
            print(f"    MinTemperature: {sample['ElementValue'][0]['MinTemperature']}°C")
            break


# ============================================================
# 提取最高與最低氣溫資料
# ============================================================
def extract_temperature_data(data):
    """
    從天氣預報資料中提取各縣市的最高與最低氣溫資料。

    Args:
        data (dict): API 回傳的 JSON 資料。

    Returns:
        dict: 按區域分類的氣溫資料。
    """
    all_locations = data["records"]["Locations"][0]["Location"]
    temperature_data = {}

    for region, cities in REGION_MAPPING.items():
        region_temps = []

        for location in all_locations:
            county = location["LocationName"]
            if county not in cities:
                continue

            county_info = {
                "縣市": county,
                "最高溫度": [],
                "最低溫度": [],
            }

            for elem in location["WeatherElement"]:
                if elem["ElementName"] == "最高溫度":
                    for time_period in elem["Time"]:
                        county_info["最高溫度"].append({
                            "開始時間": time_period["StartTime"],
                            "結束時間": time_period["EndTime"],
                            "溫度": time_period["ElementValue"][0]["MaxTemperature"],
                        })

                elif elem["ElementName"] == "最低溫度":
                    for time_period in elem["Time"]:
                        county_info["最低溫度"].append({
                            "開始時間": time_period["StartTime"],
                            "結束時間": time_period["EndTime"],
                            "溫度": time_period["ElementValue"][0]["MinTemperature"],
                        })

            region_temps.append(county_info)

        temperature_data[region] = region_temps

    return temperature_data


def display_temperature_json(temperature_data):
    """
    使用 json.dumps 觀察提取的最高與最低氣溫資料。

    Args:
        temperature_data (dict): 按區域分類的氣溫資料。
    """
    print("\n" + "=" * 60)
    print("提取的最高與最低氣溫 JSON 資料")
    print("=" * 60)

    for region, counties in temperature_data.items():
        print(f"\n【{region}】")
        # 顯示第一個縣市的完整資料
        if counties:
            sample = json.dumps(counties[0], ensure_ascii=False, indent=2)
            print(sample)

    # 顯示完整資料的 json.dumps 輸出
    print("\n" + "=" * 60)
    print("完整氣溫資料 json.dumps 輸出（前 3000 字元）")
    print("=" * 60)
    full_json = json.dumps(temperature_data, ensure_ascii=False, indent=2)
    print(full_json[:3000])
    if len(full_json) > 3000:
        print(f"... (共 {len(full_json)} 字元)")


def display_temperature_summary(temperature_data):
    """
    顯示各區域氣溫摘要表格。

    Args:
        temperature_data (dict): 按區域分類的氣溫資料。
    """
    print("\n" + "=" * 60)
    print("各區域一週氣溫摘要")
    print("=" * 60)

    for region, counties in temperature_data.items():
        print(f"\n{'─' * 50}")
        print(f"【{region}】")
        print(f"{'─' * 50}")
        print(f"  {'縣市':<8} {'最低溫(°C)':<12} {'最高溫(°C)':<12}")
        print(f"  {'─' * 40}")

        for county in counties:
            name = county["縣市"]
            # 找出整週的最低與最高溫
            min_temps = [int(t["溫度"]) for t in county["最低溫度"]]
            max_temps = [int(t["溫度"]) for t in county["最高溫度"]]

            week_min = min(min_temps) if min_temps else "N/A"
            week_max = max(max_temps) if max_temps else "N/A"

            print(f"  {name:<8} {str(week_min):<12} {str(week_max):<12}")


def save_json_file(data, filename):
    """
    將資料儲存為 JSON 檔案。

    Args:
        data (dict): 要儲存的資料。
        filename (str): 輸出的檔案名稱。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n已儲存 JSON 檔案: {filename}")


# ============================================================
# 主程式
# ============================================================
def main():
    """主程式：分析並提取最高與最低氣溫資料。"""

    # Step 1: 調用 CWA API 獲取天氣預報資料
    data = fetch_weekly_forecast()

    # Step 2: 分析 JSON 結構，找出最高與最低氣溫的位置
    analyze_json_structure(data)

    # Step 3: 提取最高與最低氣溫資料
    temperature_data = extract_temperature_data(data)

    # Step 4: 使用 json.dumps 觀察提取的資料
    display_temperature_json(temperature_data)

    # Step 5: 顯示各區域氣溫摘要
    display_temperature_summary(temperature_data)

    # Step 6: 儲存氣溫資料為 JSON 檔案
    save_json_file(temperature_data, "temperature_data.json")


if __name__ == "__main__":
    main()
