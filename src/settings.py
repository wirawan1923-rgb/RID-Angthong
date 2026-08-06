"""
Settings - การตั้งค่าต่างๆ ของแอปพลิเคชัน
"""

import os

# ข้อมูลพื้นฐาน
APP_NAME = "Hydrology Data Bot"
APP_VERSION = "1.0.0"

# การตั้งค่า API
API_URL = 'http://hyd-app.rid.go.th/webservice/getDailyWaterLevelListReport5.ashx'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://hyd-app.rid.go.th/hydro5h.html',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'
}
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2

# การตั้งค่าเริ่มต้น
DEFAULT_STATION_ID = "5"
DEFAULT_DAYS_BACK = 30
DEFAULT_UPDATE_INTERVAL = 1

# เส้นทางไฟล์
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'config.json')

# สร้างโฟลเดอร์ถ้ายังไม่มี
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
