"""
DataManager - จัดการการจัดเก็บและโหลดข้อมูล
"""

import json
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from config.settings import DATA_DIR


class DataManager:
    """คลาสสำหรับจัดการข้อมูล"""
    
    def __init__(self):
        self.data: List[Dict] = []
        self.data_file = os.path.join(DATA_DIR, 'water_data.json')
        
    def add_data(self, new_data: List[Dict]) -> int:
        """
        เพิ่มข้อมูลใหม่ (ตรวจสอบข้อมูลซ้ำ)
        
        Args:
            new_data: รายการข้อมูลที่จะเพิ่ม
            
        Returns:
            int: จำนวนข้อมูลที่เพิ่มใหม่
        """
        added = 0
        for item in new_data:
            if not self.is_duplicate(item):
                self.data.append(item)
                added += 1
        return added
    
    def is_duplicate(self, item: Dict) -> bool:
        """ตรวจสอบว่าข้อมูลซ้ำหรือไม่"""
        for existing in self.data:
            if (existing.get('date') == item.get('date') and 
                existing.get('water_level') == item.get('water_level') and
                existing.get('station_id') == item.get('station_id')):
                return True
        return False
    
    def get_data_file_path(self) -> str:
        """คืนค่า path ของไฟล์ข้อมูล"""
        return self.data_file
    
    def load_from_file(self, file_path: str) -> bool:
        """โหลดข้อมูลจากไฟล์"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def save_to_file(self) -> bool:
        """บันทึกข้อมูลลงไฟล์"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def save_to_csv(self, file_path: str) -> bool:
        """บันทึกข้อมูลเป็น CSV"""
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def save_to_json(self, file_path: str) -> bool:
        """บันทึกข้อมูลเป็น JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    def clear(self):
        """ล้างข้อมูลทั้งหมด"""
        self.data = []
    
    def get_statistics(self) -> Dict:
        """คำนวณสถิติของข้อมูล"""
        if not self.data:
            return {}
        
        try:
            df = pd.DataFrame(self.data)
            water_levels = df['water_level'].apply(
                lambda x: float(x) if x.replace('.', '').isdigit() else None
            ).dropna()
            
            return {
                'total': len(self.data),
                'station_id': df['station_id'].iloc[0] if not df.empty else 'N/A',
                'start_date': df['date'].min() if not df.empty else 'N/A',
                'end_date': df['date'].max() if not df.empty else 'N/A',
                'days_count': df['date'].nunique() if not df.empty else 0,
                'avg_water_level': water_levels.mean() if not water_levels.empty else 0,
                'max_water_level': water_levels.max() if not water_levels.empty else 0,
                'min_water_level': water_levels.min() if not water_levels.empty else 0
            }
        except:
            return {'total': len(self.data)}
