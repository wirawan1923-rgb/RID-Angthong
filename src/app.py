"""
HydrologyApp - คลาสหลักของแอปพลิเคชัน
จัดการการทำงานทั้งหมดและการเชื่อมต่อระหว่างส่วนต่างๆ
"""

import threading
import time
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

from src.api_client import ApiClient
from src.data_manager import DataManager
from src.ui import MainUI
from config.settings import (
    DEFAULT_STATION_ID, 
    DEFAULT_DAYS_BACK, 
    DEFAULT_UPDATE_INTERVAL,
    CONFIG_FILE
)


class HydrologyApp:
    """คลาสหลักของแอปพลิเคชัน"""
    
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.is_fetching = False
        self.update_thread = None
        
        # สร้างตัวจัดการข้อมูล
        self.data_manager = DataManager()
        
        # สร้าง API Client
        self.api_client = ApiClient()
        
        # โหลดการตั้งค่า
        self.settings = self.load_settings()
        
        # สร้าง UI
        self.ui = MainUI(root, self)
        
        # อัปเดตการตั้งค่าใน UI
        self.ui.station_var.set(self.settings.get('station_id', DEFAULT_STATION_ID))
        self.ui.days_var.set(self.settings.get('days_back', DEFAULT_DAYS_BACK))
        self.ui.interval_var.set(self.settings.get('update_interval', DEFAULT_UPDATE_INTERVAL))
        
        # โหลดข้อมูลเก่า (ถ้ามี)
        self.load_existing_data()
        
        self.log("🚀 แอปพลิเคชันพร้อมทำงาน")
        self.log(f"📌 รหัสสถานี: {self.settings.get('station_id', DEFAULT_STATION_ID)}")
        
    def load_existing_data(self):
        """โหลดข้อมูลที่มีอยู่แล้ว"""
        try:
            data_file = self.data_manager.get_data_file_path()
            if os.path.exists(data_file):
                self.data_manager.load_from_file(data_file)
                self.log(f"📂 โหลดข้อมูลเก่า {len(self.data_manager.data)} รายการ")
                self.ui.refresh_table(self.data_manager.data)
                self.ui.update_status(
                    f"📊 โหลดข้อมูลสำเร็จ {len(self.data_manager.data)} รายการ",
                    records=len(self.data_manager.data)
                )
        except Exception as e:
            self.log(f"⚠️ ไม่สามารถโหลดข้อมูลเก่า: {str(e)}")
    
    def load_settings(self):
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"ไม่สามารถโหลดการตั้งค่า: {e}")
        return {}
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        try:
            settings = {
                'station_id': self.ui.station_var.get(),
                'days_back': int(self.ui.days_var.get()),
                'update_interval': int(self.ui.interval_var.get())
            }
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log("💾 บันทึกการตั้งค่าเรียบร้อย")
        except Exception as e:
            self.log(f"⚠️ ไม่สามารถบันทึกการตั้งค่า: {str(e)}")
    
    def log(self, message):
        """เพิ่มข้อความลงใน Log"""
        self.ui.add_log(message)
    
    def fetch_all_data(self):
        """ดึงข้อมูลทั้งหมด"""
        if self.is_fetching:
            messagebox.showwarning("แจ้งเตือน", "กำลังดึงข้อมูลอยู่ กรุณารอสักครู่")
            return
        
        self.is_fetching = True
        self.ui.set_fetching_state(True)
        
        # รันใน Thread
        thread = threading.Thread(target=self._fetch_all_data_thread)
        thread.daemon = True
        thread.start()
    
    def _fetch_all_data_thread(self):
        """Thread สำหรับดึงข้อมูล"""
        try:
            station_id = self.ui.station_var.get().strip()
            days_back = int(self.ui.days_var.get())
            
            self.log(f"📥 เริ่มดึงข้อมูล {days_back} วัน (สถานี {station_id})")
            self.ui.update_status(f"🔄 กำลังดึงข้อมูล... 0/{days_back} วัน", 0)
            
            # ดึงข้อมูล
            data = self.api_client.fetch_historical_data(
                station_id=station_id,
                days_back=days_back,
                callback=self._update_progress
            )
            
            if data:
                # บันทึกข้อมูล
                self.data_manager.data = data
                self.data_manager.save_to_file()
                
                # อัปเดต UI
                self.root.after(0, lambda: self._finish_fetch(data))
            else:
                self.root.after(0, lambda: self._fetch_error("ไม่พบข้อมูล"))
                
        except Exception as e:
            self.root.after(0, lambda: self._fetch_error(str(e)))
    
    def _update_progress(self, current, total, message):
        """อัปเดตความคืบหน้า"""
        progress = (current / total) * 100
        self.root.after(0, lambda: self.ui.update_status(
            f"🔄 {message} ({current}/{total})", 
            progress
        ))
    
    def _finish_fetch(self, data):
        """เมื่อดึงข้อมูลเสร็จ"""
        self.is_fetching = False
        self.ui.set_fetching_state(False)
        self.ui.refresh_table(data)
        self.ui.update_status(
            f"✅ ดึงข้อมูลเสร็จ! ได้ {len(data)} รายการ", 
            100,
            records=len(data)
        )
        self.log(f"✅ ดึงข้อมูลเสร็จสิ้น! ได้ทั้งหมด {len(data)} รายการ")
        messagebox.showinfo("สำเร็จ", f"ดึงข้อมูลเสร็จสิ้น!\nพบข้อมูล {len(data)} รายการ")
    
    def _fetch_error(self, error_msg):
        """เมื่อเกิดข้อผิดพลาดในการดึงข้อมูล"""
        self.is_fetching = False
        self.ui.set_fetching_state(False)
        self.log(f"❌ เกิดข้อผิดพลาด: {error_msg}")
        self.ui.update_status(f"❌ ข้อผิดพลาด: {error_msg}", 0)
        messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถดึงข้อมูลได้:\n{error_msg}")
    
    def start_auto_update(self):
        """เริ่มอัปเดตอัตโนมัติ"""
        if self.is_running:
            return
        
        # ตรวจสอบข้อมูล
        if len(self.data_manager.data) == 0:
            result = messagebox.askyesno(
                "แจ้งเตือน", 
                "ยังไม่มีข้อมูลในระบบ คุณต้องการดึงข้อมูลย้อนหลังก่อนหรือไม่?"
            )
            if result:
                self.fetch_all_data()
                return
        
        self.is_running = True
        self.ui.set_auto_update_state(True)
        
        interval = int(self.ui.interval_var.get())
        self.log(f"▶️ เริ่มอัปเดตอัตโนมัติทุก {interval} นาที")
        self.ui.update_status("🟢 กำลังอัปเดตอัตโนมัติ...", records=len(self.data_manager.data))
        
        # รันใน Thread
        self.update_thread = threading.Thread(
            target=self._auto_update_loop, 
            args=(interval,)
        )
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _auto_update_loop(self, interval_minutes):
        """ลูปอัปเดตอัตโนมัติ"""
        while self.is_running:
            try:
                station_id = self.ui.station_var.get().strip()
                self.log("🔄 กำลังอัปเดตข้อมูลล่าสุด...")
                
                # ดึงข้อมูลวันนี้
                new_data = self.api_client.fetch_today_data(station_id)
                
                if new_data:
                    # ตรวจสอบข้อมูลซ้ำ
                    added = 0
                    for item in new_data:
                        if not self.data_manager.is_duplicate(item):
                            self.data_manager.data.append(item)
                            added += 1
                    
                    if added > 0:
                        self.data_manager.save_to_file()
                        self.log(f"✅ อัปเดตสำเร็จ! เพิ่ม {added} รายการใหม่")
                        self.root.after(0, lambda: self.ui.refresh_table(self.data_manager.data))
                        self.root.after(0, lambda: self.ui.update_status(
                            f"🟢 อัปเดตล่าสุด {datetime.now().strftime('%H:%M:%S')}",
                            records=len(self.data_manager.data)
                        ))
                    else:
                        self.log("ℹ️ ไม่มีข้อมูลใหม่")
                
                # รอตามระยะเวลา
                for _ in range(interval_minutes * 60):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"⚠️ ข้อผิดพลาดในการอัปเดต: {str(e)}")
                time.sleep(30)  # รอแล้วลองใหม่
    
    def stop_auto_update(self):
        """หยุดอัปเดตอัตโนมัติ"""
        self.is_running = False
        self.ui.set_auto_update_state(False)
        self.log("⏹️ หยุดระบบอัปเดตอัตโนมัติ")
        self.ui.update_status("🟡 หยุดการทำงาน", records=len(self.data_manager.data))
    
    def save_data(self, file_path, format_type='csv'):
        """บันทึกข้อมูล"""
        try:
            if format_type == 'csv':
                self.data_manager.save_to_csv(file_path)
            elif format_type == 'json':
                self.data_manager.save_to_json(file_path)
            self.log(f"💾 บันทึกข้อมูลเป็น {format_type.upper()} ที่ {file_path}")
            return True
        except Exception as e:
            self.log(f"❌ ไม่สามารถบันทึกข้อมูล: {str(e)}")
            return False
    
    def clear_data(self):
        """ล้างข้อมูลทั้งหมด"""
        if len(self.data_manager.data) == 0:
            return
        
        if messagebox.askyesno("ยืนยัน", "ต้องการล้างข้อมูลทั้งหมดใช่หรือไม่?"):
            self.data_manager.clear()
            self.ui.refresh_table([])
            self.ui.update_status("🔄 ล้างข้อมูลเรียบร้อย", 0, 0)
            self.log("🗑️ ล้างข้อมูลทั้งหมดแล้ว")
    
    def show_statistics(self):
        """แสดงสถิติข้อมูล"""
        stats = self.data_manager.get_statistics()
        if not stats:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะแสดงสถิติ")
            return
        
        stats_text = f"""
📊 สถิติข้อมูล
═══════════════════════════════
📅 จำนวนข้อมูลทั้งหมด: {stats['total']} รายการ
📍 สถานี: {stats['station_id']}
📆 วันที่เริ่มต้น: {stats['start_date']}
📆 วันที่สิ้นสุด: {stats['end_date']}
📈 จำนวนวัน: {stats['days_count']} วัน
📊 ระดับน้ำเฉลี่ย: {stats['avg_water_level']:.2f}
📊 ระดับน้ำสูงสุด: {stats['max_water_level']:.2f}
📊 ระดับน้ำต่ำสุด: {stats['min_water_level']:.2f}
        """
        messagebox.showinfo("สถิติข้อมูล", stats_text)
    
    def exit_app(self):
        """ออกจากโปรแกรม"""
        if messagebox.askyesno("ยืนยัน", "ต้องการออกจากโปรแกรมใช่หรือไม่?"):
            self.save_settings()
            self.is_running = False
            self.is_fetching = False
            self.root.destroy()
