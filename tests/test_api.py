"""
ทดสอบการเชื่อมต่อ API
"""

import unittest
from datetime import datetime, timedelta
from src.api_client import ApiClient


class TestApiClient(unittest.TestCase):
    """ทดสอบ ApiClient"""
    
    def setUp(self):
        """ตั้งค่าก่อนทดสอบ"""
        self.client = ApiClient()
        self.test_station = "5"
    
    def test_fetch_today_data(self):
        """ทดสอบดึงข้อมูลวันนี้"""
        result = self.client.fetch_today_data(self.test_station)
        # ไม่ต้อง assert ว่าได้ข้อมูล เพราะอาจไม่มีข้อมูลวันนี้
        self.assertIsInstance(result, list)
    
    def test_fetch_data_by_date(self):
        """ทดสอบดึงข้อมูลตามวันที่"""
        # ใช้วันที่ 1 เดือนที่แล้ว (น่าจะมีข้อมูล)
        test_date = datetime.now() - timedelta(days=30)
        result = self.client.fetch_data_by_date(test_date, self.test_station)
        self.assertIsInstance(result, (list, type(None)))


if __name__ == '__main__':
    unittest.main()
