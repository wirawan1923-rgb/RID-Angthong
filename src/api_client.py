"""
ApiClient - จัดการการติดต่อกับ API ของกรมชลประทาน
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from config.settings import (
    API_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_DELAY
)


class ApiClient:
    """คลาสสำหรับจัดการการเรียก API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = API_URL
        self.last_request_time = 0
        
    def _wait_for_rate_limit(self):
        """รอเพื่อป้องกันการถูกบล็อก"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.5:  # อย่างน้อย 0.5 วินาทีต่อครั้ง
            time.sleep(0.5 - time_since_last)
        self.last_request_time = time.time()
    
    def fetch_data_by_date(self, target_date: datetime, station_id: str) -> Optional[List[Dict]]:
        """
        ดึงข้อมูลสำหรับวันที่ระบุ
        
        Args:
            target_date: วันที่ต้องการดึงข้อมูล
            station_id: รหัสสถานี
            
        Returns:
            List[Dict]: รายการข้อมูล หรือ None หากไม่สำเร็จ
        """
        self._wait_for_rate_limit()
        
        params = {'option': '2'}
        date_str = target_date.strftime('%d/%m/%Y')
        
        data = {
            'DW[UtokID]': station_id,
            'DW[TimeCurrent]': date_str,
            '_search': 'false',
            'nd': str(int(time.time() * 1000)),
            'rows': '10000',
            'page': '1',
            'sidx': 'indexcount',
            'sord': 'asc'
        }
        
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = self.session.post(
                    self.base_url,
                    params=params,
                    data=data,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result and 'rows' in result:
                        parsed_data = []
                        for row in result.get('rows', []):
                            cell_data = row.get('cell', [])
                            if len(cell_data) >= 2:
                                parsed_data.append({
                                    'date': target_date.strftime('%Y-%m-%d'),
                                    'station_id': station_id,
                                    'water_level': str(cell_data[1]) if len(cell_data) > 1 else 'N/A',
                                    'time': str(cell_data[2]) if len(cell_data) > 2 else 'N/A',
                                    'status': str(cell_data[3]) if len(cell_data) > 3 else 'N/A'
                                })
                        return parsed_data
                else:
                    if attempt < RETRY_ATTEMPTS - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                        
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                print(f"Error fetching data for {date_str}: {str(e)}")
                
        return None
    
    def fetch_historical_data(
        self, 
        station_id: str, 
        days_back: int,
        callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict]:
        """
        ดึงข้อมูลย้อนหลัง
        
        Args:
            station_id: รหัสสถานี
            days_back: จำนวนวันย้อนหลัง
            callback: ฟังก์ชันสำหรับอัปเดตความคืบหน้า (current, total, message)
            
        Returns:
            List[Dict]: รายการข้อมูลทั้งหมด
        """
        all_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        total_days = (end_date - start_date).days + 1
        
        current_date = start_date
        success_count = 0
        
        for day in range(total_days):
            if callback:
                callback(day + 1, total_days, f"กำลังดึงวันที่ {current_date.strftime('%d/%m/%Y')}")
            
            result = self.fetch_data_by_date(current_date, station_id)
            if result:
                all_data.extend(result)
                success_count += 1
            
            current_date += timedelta(days=1)
        
        return all_data
    
    def fetch_today_data(self, station_id: str) -> List[Dict]:
        """
        ดึงข้อมูลของวันนี้
        
        Args:
            station_id: รหัสสถานี
            
        Returns:
            List[Dict]: รายการข้อมูลวันนี้
        """
        today = datetime.now()
        result = self.fetch_data_by_date(today, station_id)
        return result if result else []
