"""
HW2-1: 獲取天氣預報資料
使用 CWA API 獲取台灣北部、中部、南部、東北部、東部及東南部地區一週的天氣預報資料。
"""

import requests
import json
import urllib3

# 關閉 SSL 驗證警告（CWA 伺服器憑證問題）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
# 設定 CWA API 參數
# ============================================================
API_KEY = "CWA-C3D49702-79E1-4035-812F-EE485D61EEE3"
BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
DATASET_ID = "F-D0047-091"  # 鄉鎮天氣預報 - 臺灣未來1週天氣預報

# ============================================================
# 定義台灣各區域對應的縣市
# ============================================================
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
        dict: API 回傳的 JSON 資料（字典格式）。
    """
    url = f"{BASE_URL}/{DATASET_ID}"
    params = {
        "Authorization": API_KEY,
        "format": "JSON",
    }

    print(f"正在調用 CWA API...")
    print(f"URL: {url}")

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()  # 若 HTTP 狀態碼非 200，會拋出例外

    print(f"HTTP 狀態碼: {response.status_code}")
    data = response.json()

    return data


def display_raw_json(data, indent=2):
    """
    使用 json.dumps 觀察 API 回傳的原始 JSON 資料。

    Args:
        data (dict): API 回傳的 JSON 資料。
        indent (int): JSON 縮排空格數。
    """
    formatted_json = json.dumps(data, ensure_ascii=False, indent=indent)
    print("\n" + "=" * 60)
    print("原始 JSON 資料（前 2000 字元）")
    print("=" * 60)
    print(formatted_json[:2000])
    print("...")
    print(f"\n[JSON 資料總長度: {len(formatted_json)} 字元]")


def organize_by_region(data):
    """
    將 API 回傳的天氣預報資料按區域分類整理。

    Args:
        data (dict): API 回傳的 JSON 資料。

    Returns:
        dict: 按區域分類的天氣預報資料。
    """
    regions_data = {region: [] for region in REGION_MAPPING}

    # F-D0047-091 的結構: records -> Locations[0] -> Location[]
    locations = data.get("records", {}).get("Locations", [])
    if not locations:
        print("警告：未取得任何地點資料！")
        return regions_data

    all_locations = locations[0].get("Location", [])

    for location in all_locations:
        location_name = location.get("LocationName", "")
        for region, cities in REGION_MAPPING.items():
            if location_name in cities:
                regions_data[region].append(location)
                break

    return regions_data


def display_regional_forecast(regions_data):
    """
    顯示各區域的天氣預報摘要。

    Args:
        regions_data (dict): 按區域分類的天氣預報資料。
    """
    print("\n" + "=" * 60)
    print("各區域一週天氣預報摘要")
    print("=" * 60)

    for region, locations in regions_data.items():
        print(f"\n{'─' * 40}")
        print(f"【{region}】 共 {len(locations)} 個縣市")
        print(f"{'─' * 40}")

        for loc in locations:
            name = loc.get("LocationName", "未知")
            weather_elements = loc.get("WeatherElement", [])

            # 取得天氣現象 (Wx)
            wx = ""
            for elem in weather_elements:
                if elem.get("ElementName") == "天氣現象":
                    time_periods = elem.get("Time", [])
                    if time_periods:
                        elem_value = time_periods[0].get("ElementValue", [])
                        if elem_value:
                            wx = elem_value[0].get("Weather", "")
                    break

            # 取得最高溫 (MaxT) 與最低溫 (MinT)
            max_t, min_t = "", ""
            for elem in weather_elements:
                elem_name = elem.get("ElementName", "")
                if elem_name == "最高溫度":
                    time_periods = elem.get("Time", [])
                    if time_periods:
                        elem_value = time_periods[0].get("ElementValue", [])
                        if elem_value:
                            max_t = elem_value[0].get("MaxTemperature", "")
                elif elem_name == "最低溫度":
                    time_periods = elem.get("Time", [])
                    if time_periods:
                        elem_value = time_periods[0].get("ElementValue", [])
                        if elem_value:
                            min_t = elem_value[0].get("MinTemperature", "")

            print(f"  {name}: {wx}，溫度 {min_t}°C ~ {max_t}°C")


def display_region_json(regions_data):
    """
    使用 json.dumps 顯示各區域分類後的 JSON 資料。

    Args:
        regions_data (dict): 按區域分類的天氣預報資料。
    """
    print("\n" + "=" * 60)
    print("各區域天氣預報 JSON 資料")
    print("=" * 60)

    for region, locations in regions_data.items():
        region_json = json.dumps(
            {region: [loc.get("LocationName") for loc in locations]},
            ensure_ascii=False,
            indent=2,
        )
        print(f"\n【{region}】包含縣市：")
        print(region_json)

        # 顯示第一個縣市的部分 JSON 資料作為範例
        if locations:
            sample = json.dumps(
                locations[0],
                ensure_ascii=False,
                indent=2,
            )
            print(f"\n  範例 - {locations[0].get('LocationName', '')} 資料（前 500 字元）：")
            print(f"  {sample[:500]}")
            if len(sample) > 500:
                print(f"  ... (共 {len(sample)} 字元)")


# ============================================================
# 主程式
# ============================================================
def save_json_file(data, filename):
    """
    將資料儲存為 JSON 檔案。

    Args:
        data (dict): 要儲存的資料。
        filename (str): 輸出的檔案名稱。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已儲存 JSON 檔案: {filename}")


def main():
    """主程式：獲取並展示一週天氣預報資料。"""

    # Step 1: 調用 CWA API 獲取天氣預報資料
    data = fetch_weekly_forecast()

    # Step 2: 使用 json.dumps 觀察原始 JSON 資料
    display_raw_json(data)

    # Step 3: 儲存原始 JSON 資料到檔案
    save_json_file(data, "weather_raw.json")

    # Step 4: 將資料按區域分類
    regions_data = organize_by_region(data)

    # Step 5: 顯示各區域天氣預報摘要
    display_regional_forecast(regions_data)

    # Step 6: 使用 json.dumps 顯示各區域 JSON 資料
    display_region_json(regions_data)

    # Step 7: 儲存各區域分類後的 JSON 資料到檔案
    save_json_file(regions_data, "weather_by_region.json")


if __name__ == "__main__":
    main()
