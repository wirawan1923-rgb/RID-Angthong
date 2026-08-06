"""
Hydrology Data Bot - แอปดึงข้อมูลระดับน้ำจากกรมชลประทาน
เวอร์ชัน: 1.0.0
พัฒนาโดย: [Your Name]
วันที่: 2026-08-06
"""

import requests
import json
import time
import threading
import schedule
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys

class WaterDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hydrology Data Bot - กรมชลประทาน")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # กำหนดไอคอน (ถ้ามี)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # ตัวแปรหลัก
        self.is_running = False
        self.is_fetching = False
        self.fetch_thread = None
        self.update_thread = None
        self.data_cache = []
        self.api_url = 'http://hyd-app.rid.go.th/webservice/getDailyWaterLevelListReport5.ashx'
        self.log_count = 0
        
        # สร้าง UI
        self.create_widgets()
        
        # โหลดการตั้งค่า
        self.load_settings()
        
        self.log("🚀 แอปพลิเคชันพร้อมทำงาน")
        self.log("📌 รอการดำเนินการจากผู้ใช้...")
        
    def create_widgets(self):
        """สร้างส่วนประกอบ UI ทั้งหมด"""
        # ===== ส่วนบน: การตั้งค่า =====
        settings_frame = ttk.LabelFrame(self.root, text="⚙️ การตั้งค่า", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # แถวที่ 1: การตั้งค่าหลัก
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="รหัสสถานี:").pack(side="left", padx=5)
        self.station_var = tk.StringVar(value="5")
        ttk.Entry(row1, textvariable=self.station_var, width=15).pack(side="left", padx=5)
        
        ttk.Label(row1, text="จำนวนวันย้อนหลัง:").pack(side="left", padx=5)
        self.days_var = tk.StringVar(value="30")
        ttk.Spinbox(row1, from_=1, to=365, textvariable=self.days_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(row1, text="ความถี่ (นาที):").pack(side="left", padx=5)
        self.interval_var = tk.StringVar(value="1")
        ttk.Spinbox(row1, from_=1, to=60, textvariable=self.interval_var, width=8).pack(side="left", padx=5)
        
        # แถวที่ 2: ปุ่มควบคุม
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill="x", pady=5)
        
        self.fetch_all_btn = ttk.Button(row2, text="📥 ดึงข้อมูลทั้งหมด", command=self.start_fetch_all, width=20)
        self.fetch_all_btn.pack(side="left", padx=5)
        
        self.start_btn = ttk.Button(row2, text="▶️ เริ่มอัปเดตอัตโนมัติ", command=self.start_auto_update, width=20)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(row2, text="⏹️ หยุดอัปเดต", command=self.stop_auto_update, state="disabled", width=20)
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(row2, text="🗑️ ล้างข้อมูล", command=self.clear_data, width=15).pack(side="left", padx=5)
        
        # ===== ส่วนกลาง: สถานะ =====
        status_frame = ttk.LabelFrame(self.root, text="📊 สถานะการทำงาน", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_row = ttk.Frame(status_frame)
        status_row.pack(fill="x")
        
        self.status_label = ttk.Label(status_row, text="🟢 พร้อมทำงาน", font=("Arial", 11))
        self.status_label.pack(side="left", padx=5)
        
        self.record_label = ttk.Label(status_row, text="จำนวนข้อมูล: 0 รายการ", font=("Arial", 11))
        self.record_label.pack(side="right", padx=5)
        
        self.progress = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress.pack(fill="x", pady=5)
        
        # ===== ตารางแสดงข้อมูล =====
        table_frame = ttk.LabelFrame(self.root, text="📋 ข้อมูลที่ดึงได้ (แสดง 100 รายการล่าสุด)", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # สร้าง Treeview
        columns = ("วันที่", "สถานี", "ระดับน้ำ", "เวลา", "สถานะ")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # กำหนดหัวข้อคอลัมน์และความกว้าง
        col_widths = {"วันที่": 120, "สถานี": 100, "ระดับน้ำ": 120, "เวลา": 100, "สถานะ": 150}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== ส่วนล่าง: Log และปุ่ม =====
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(bottom_frame, text="📝 บันทึกการทำงาน", padding=10)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # ปุ่มจัดการข้อมูล
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="💾 บันทึก CSV", command=self.save_csv, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📁 บันทึก JSON", command=self.save_json, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 รีเฟรชตาราง", command=self.refresh_table, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 แสดงสถิติ", command=self.show_statistics, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🚪 ออกจากโปรแกรม", command=self.exit_app, width=15).pack(side="right", padx=5)
        
    def log(self, message):
        """เพิ่มข้อความลงใน Log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_count += 1
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
        # จำกัดจำนวน Log เพื่อป้องกันหน่วยความจำเต็ม
        if self.log_count > 1000:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "100.0")
            self.log_text.configure(state="disabled")
            self.log_count = 0
        
    def update_status(self, text, progress=None, records=None):
        """อัปเดตสถานะและ Progress Bar"""
        self.status_label.config(text=text)
        if progress is not None:
            self.progress['value'] = progress
        if records is not None:
            self.record_label.config(text=f"จำนวนข้อมูล: {records} รายการ")
        self.root.update_idletasks()
        
    def fetch_data_by_date(self, target_date, station_id):
        """ดึงข้อมูลสำหรับวันที่ระบุ"""
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
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://hyd-app.rid.go.th/hydro5h.html',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                params=params, 
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Error {response.status_code} สำหรับวันที่ {date_str}")
                return None
                
        except requests.exceptions.Timeout:
            self.log(f"⏰ Timeout สำหรับวันที่ {date_str}")
            return None
        except requests.exceptions.ConnectionError:
            self.log(f"🔌 Connection Error สำหรับวันที่ {date_str}")
            return None
        except Exception as e:
            self.log(f"⚠️ Exception สำหรับวันที่ {date_str}: {str(e)}")
            return None
    
    def start_fetch_all(self):
        """เริ่มต้นดึงข้อมูลทั้งหมดใน Thread แยก"""
        if self.is_fetching:
            messagebox.showwarning("แจ้งเตือน", "ระบบกำลังดึงข้อมูลอยู่ กรุณารอสักครู่")
            return
        
        self.is_fetching = True
        self.fetch_all_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.fetch_thread = threading.Thread(target=self.fetch_all_data)
        self.fetch_thread.daemon = True
        self.fetch_thread.start()
    
    def fetch_all_data(self):
        """ดึงข้อมูลย้อนหลังทั้งหมด"""
        try:
            station_id = self.station_var.get().strip()
            if not station_id.isdigit():
                self.log("❌ กรุณากรอกรหัสสถานีเป็นตัวเลข")
                self.root.after(0, self.reset_ui)
                return
                
            days_back = int(self.days_var.get())
            if days_back < 1 or days_back > 365:
                self.log("❌ จำนวนวันต้องอยู่ระหว่าง 1-365")
                self.root.after(0, self.reset_ui)
                return
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            self.log(f"📥 เริ่มดึงข้อมูล {days_back} วัน (สถานี {station_id})")
            self.log(f"📅 ช่วงวันที่: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            self.update_status(f"🔄 กำลังดึงข้อมูล... 0/{days_back} วัน", 0, len(self.data_cache))
            
            self.data_cache = []
            current_date = start_date
            total_days = (end_date - start_date).days + 1
            success_count = 0
            
            for day in range(total_days):
                if not self.is_fetching:
                    break
                    
                result = self.fetch_data_by_date(current_date, station_id)
                day_success = False
                
                if result and 'rows' in result and result['rows']:
                    rows_added = 0
                    for row in result.get('rows', []):
                        cell_data = row.get('cell', [])
                        if len(cell_data) >= 2:
                            # ตรวจสอบว่ามีข้อมูลซ้ำหรือไม่
                            is_duplicate = False
                            for existing in self.data_cache:
                                if (existing.get('date') == current_date.strftime('%Y-%m-%d') and 
                                    existing.get('water_level') == str(cell_data[1]) if len(cell_data) > 1 else ''):
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                self.data_cache.append({
                                    'date': current_date.strftime('%Y-%m-%d'),
                                    'station_id': station_id,
                                    'water_level': str(cell_data[1]) if len(cell_data) > 1 else 'N/A',
                                    'time': str(cell_data[2]) if len(cell_data) > 2 else 'N/A',
                                    'status': str(cell_data[3]) if len(cell_data) > 3 else 'N/A'
                                })
                                rows_added += 1
                    
                    if rows_added > 0:
                        day_success = True
                        success_count += 1
                        self.log(f"✅ วันที่ {current_date.strftime('%d/%m/%Y')}: เพิ่ม {rows_added} รายการ")
                
                # อัปเดต Progress
                progress = ((day + 1) / total_days) * 100
                self.root.after(0, lambda p=progress: self.update_status(
                    f"🔄 กำลังดึงข้อมูล... {day+1}/{total_days} วัน", 
                    p, 
                    len(self.data_cache)
                ))
                
                # หน่วงเวลาเพื่อป้องกันการถูกบล็อก
                time.sleep(0.5)
                current_date += timedelta(days=1)
            
            # อัปเดต UI
            self.root.after(0, self.finish_fetch)
            
        except ValueError as e:
            self.log(f"❌ ค่าที่กรอกไม่ถูกต้อง: {str(e)}")
            self.root.after(0, self.reset_ui)
        except Exception as e:
            self.log(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.root.after(0, self.reset_ui)
    
    def finish_fetch(self):
        """เมื่อดึงข้อมูลเสร็จ"""
        self.log(f"✅ ดึงข้อมูลเสร็จสิ้น! ได้ทั้งหมด {len(self.data_cache)} รายการ")
        self.update_status(f"✅ ดึงข้อมูลเสร็จสิ้น! ได้ {len(self.data_cache)} รายการ", 100, len(self.data_cache))
        self.refresh_table()
        self.reset_ui()
        messagebox.showinfo("สำเร็จ", f"ดึงข้อมูลเสร็จสิ้น!\nพบข้อมูลทั้งหมด {len(self.data_cache)} รายการ")
    
    def reset_ui(self):
        """รีเซ็ต UI กลับสู่สถานะปกติ"""
        self.is_fetching = False
        self.fetch_all_btn.config(state="normal")
        self.start_btn.config(state="normal")
        
    def refresh_table(self):
        """รีเฟรชข้อมูลในตาราง"""
        # ล้างข้อมูลเก่า
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # เพิ่มข้อมูลใหม่ (แสดง 100 รายการล่าสุด)
        display_data = self.data_cache[-100:] if len(self.data_cache) > 100 else self.data_cache
        for data in reversed(display_data):  # แสดงล่าสุดอยู่ด้านบน
            self.tree.insert("", "end", values=(
                data.get('date', ''),
                data.get('station_id', ''),
                data.get('water_level', ''),
                data.get('time', ''),
                data.get('status', '')
            ))
        
        self.record_label.config(text=f"จำนวนข้อมูล: {len(self.data_cache)} รายการ")
    
    def start_auto_update(self):
        """เริ่มการอัปเดตอัตโนมัติ"""
        if self.is_running:
            return
        
        # ตรวจสอบว่ามีข้อมูลหรือไม่
        if len(self.data_cache) == 0:
            result = messagebox.askyesno("แจ้งเตือน", 
                "ยังไม่มีข้อมูลในระบบ คุณต้องการดึงข้อมูลย้อนหลังก่อนหรือไม่?")
            if result:
                self.start_fetch_all()
                return
        
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.fetch_all_btn.config(state="disabled")
        
        self.log("▶️ เริ่มระบบอัปเดตอัตโนมัติ")
        interval = int(self.interval_var.get())
        self.log(f"⏱️ กำหนดอัปเดตทุก {interval} นาที")
        self.update_status("🟢 กำลังอัปเดตอัตโนมัติ...", records=len(self.data_cache))
        
        # รันใน Thread แยก
        self.update_thread = threading.Thread(target=self.auto_update_loop, args=(interval,))
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def auto_update_loop(self, interval_minutes):
        """ลูปสำหรับอัปเดตอัตโนมัติ"""
        while self.is_running:
            try:
                self.log("🔄 กำลังอัปเดตข้อมูลล่าสุด...")
                station_id = self.station_var.get().strip()
                today = datetime.now()
                
                result = self.fetch_data_by_date(today, station_id)
                if result and 'rows' in result:
                    count = 0
                    for row in result.get('rows', []):
                        cell_data = row.get('cell', [])
                        if len(cell_data) >= 2:
                            # ตรวจสอบว่ามีข้อมูลซ้ำหรือไม่
                            is_duplicate = False
                            for existing in self.data_cache:
                                if (existing.get('date') == today.strftime('%Y-%m-%d') and 
                                    existing.get('water_level') == str(cell_data[1]) if len(cell_data) > 1 else ''):
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                self.data_cache.append({
                                    'date': today.strftime('%Y-%m-%d'),
                                    'station_id': station_id,
                                    'water_level': str(cell_data[1]) if len(cell_data) > 1 else 'N/A',
                                    'time': str(cell_data[2]) if len(cell_data) > 2 else 'N/A',
                                    'status': str(cell_data[3]) if len(cell_data) > 3 else 'N/A'
                                })
                                count += 1
                    
                    if count > 0:
                        self.log(f"✅ อัปเดตสำเร็จ! เพิ่ม {count} รายการใหม่")
                        self.root.after(0, self.refresh_table)
                    else:
                        self.log("ℹ️ ไม่มีข้อมูลใหม่")
                    
                    self.root.after(0, lambda: self.update_status(
                        f"🟢 อัปเดตล่าสุด {datetime.now().strftime('%H:%M:%S')}", 
                        records=len(self.data_cache)
                    ))
                
                # รอตามระยะเวลาที่กำหนด
                for _ in range(interval_minutes * 60):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"⚠️ ข้อผิดพลาดในการอัปเดต: {str(e)}")
                time.sleep(30)  # รอแล้วลองใหม่
    
    def stop_auto_update(self):
        """หยุดการอัปเดตอัตโนมัติ"""
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.fetch_all_btn.config(state="normal")
        self.log("⏹️ หยุดระบบอัปเดตอัตโนมัติ")
        self.update_status("🟡 หยุดการทำงาน", records=len(self.data_cache))
    
    def save_csv(self):
        """บันทึกข้อมูลเป็น CSV"""
        if not self.data_cache:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะบันทึก")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"water_data_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.data_cache)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                self.log(f"💾 บันทึกข้อมูลเป็น CSV ที่ {file_path}")
                messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูล {len(self.data_cache)} รายการเรียบร้อย")
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถบันทึกไฟล์ได้: {str(e)}")
    
    def save_json(self):
        """บันทึกข้อมูลเป็น JSON"""
        if not self.data_cache:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะบันทึก")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"water_data_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data_cache, f, ensure_ascii=False, indent=2)
                self.log(f"💾 บันทึกข้อมูลเป็น JSON ที่ {file_path}")
                messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูล {len(self.data_cache)} รายการเรียบร้อย")
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถบันทึกไฟล์ได้: {str(e)}")
    
    def clear_data(self):
        """ล้างข้อมูลทั้งหมด"""
        if not self.data_cache:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะล้าง")
            return
            
        if messagebox.askyesno("ยืนยัน", "คุณต้องการล้างข้อมูลทั้งหมดใช่หรือไม่?"):
            self.data_cache = []
            self.refresh_table()
            self.log("🗑️ ล้างข้อมูลทั้งหมดแล้ว")
            self.update_status("🔄 พร้อมทำงานใหม่", 0, 0)
    
    def show_statistics(self):
        """แสดงสถิติข้อมูล"""
        if not self.data_cache:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะแสดงสถิติ")
            return
        
        try:
            df = pd.DataFrame(self.data_cache)
            stats = f"""
📊 สถิติข้อมูล
═══════════════════════════════
📅 จำนวนข้อมูลทั้งหมด: {len(df)} รายการ
📍 สถานี: {df['station_id'].iloc[0] if not df.empty else 'N/A'}
📆 ช่วงวันที่: {df['date'].min()} ถึง {df['date'].max()}
📈 จำนวนวัน: {df['date'].nunique()} วัน
📊 ระดับน้ำเฉลี่ย: {df['water_level'].apply(lambda x: float(x) if x.replace('.','').isdigit() else 0).mean():.2f}
📊 ระดับน้ำสูงสุด: {df['water_level'].apply(lambda x: float(x) if x.replace('.','').isdigit() else 0).max():.2f}
📊 ระดับน้ำต่ำสุด: {df['water_level'].apply(lambda x: float(x) if x.replace('.','').isdigit() else 0).min():.2f}
            """
            messagebox.showinfo("สถิติข้อมูล", stats)
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถแสดงสถิติได้: {str(e)}")
    
    def load_settings(self):
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.station_var.set(settings.get('station', '5'))
                    self.days_var.set(settings.get('days', '30'))
                    self.interval_var.set(settings.get('interval', '1'))
                    self.log("📂 โหลดการตั้งค่าสำเร็จ")
        except Exception as e:
            self.log(f"⚠️ ไม่สามารถโหลดการตั้งค่า: {str(e)}")
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        try:
            settings = {
                'station': self.station_var.get(),
                'days': self.days_var.get(),
                'interval': self.interval_var.get()
            }
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"⚠️ ไม่สามารถบันทึกการตั้งค่า: {str(e)}")
    
    def exit_app(self):
        """ออกจากโปรแกรม"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการออกจากโปรแกรมใช่หรือไม่?"):
            self.save_settings()
            self.is_running = False
            self.is_fetching = False
            self.root.destroy()

# ============ เริ่มต้นแอป ============
if __name__ == "__main__":
    root = tk.Tk()
    app = WaterDataApp(root)
    root.mainloop()
