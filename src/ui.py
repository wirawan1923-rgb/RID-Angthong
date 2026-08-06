"""
MainUI - ส่วนติดต่อผู้ใช้ของแอปพลิเคชัน
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from typing import List, Dict


class MainUI:
    """คลาสสำหรับจัดการ UI"""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.log_count = 0
        
        # ตัวแปรสำหรับการตั้งค่า
        self.station_var = tk.StringVar(value="5")
        self.days_var = tk.StringVar(value="30")
        self.interval_var = tk.StringVar(value="1")
        
        # สร้าง UI
        self.create_widgets()
        
    def create_widgets(self):
        """สร้างส่วนประกอบ UI ทั้งหมด"""
        
        # ===== ส่วนบน: การตั้งค่า =====
        settings_frame = ttk.LabelFrame(self.root, text="⚙️ การตั้งค่า", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # แถวที่ 1
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="รหัสสถานี:").pack(side="left", padx=5)
        ttk.Entry(row1, textvariable=self.station_var, width=15).pack(side="left", padx=5)
        
        ttk.Label(row1, text="จำนวนวัน:").pack(side="left", padx=5)
        ttk.Spinbox(row1, from_=1, to=365, textvariable=self.days_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(row1, text="ความถี่ (นาที):").pack(side="left", padx=5)
        ttk.Spinbox(row1, from_=1, to=60, textvariable=self.interval_var, width=8).pack(side="left", padx=5)
        
        # แถวที่ 2: ปุ่มควบคุม
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill="x", pady=5)
        
        self.fetch_btn = ttk.Button(row2, text="📥 ดึงข้อมูลทั้งหมด", command=self.app.fetch_all_data, width=18)
        self.fetch_btn.pack(side="left", padx=5)
        
        self.start_btn = ttk.Button(row2, text="▶️ เริ่มอัปเดต", command=self.app.start_auto_update, width=18)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(row2, text="⏹️ หยุดอัปเดต", command=self.app.stop_auto_update, state="disabled", width=18)
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(row2, text="🗑️ ล้างข้อมูล", command=self.app.clear_data, width=15).pack(side="left", padx=5)
        
        # ===== ส่วนกลาง: สถานะ =====
        status_frame = ttk.LabelFrame(self.root, text="📊 สถานะ", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_row = ttk.Frame(status_frame)
        status_row.pack(fill="x")
        
        self.status_label = ttk.Label(status_row, text="🟢 พร้อมทำงาน", font=("Arial", 11))
        self.status_label.pack(side="left", padx=5)
        
        self.record_label = ttk.Label(status_row, text="จำนวนข้อมูล: 0 รายการ", font=("Arial", 11))
        self.record_label.pack(side="right", padx=5)
        
        self.progress = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress.pack(fill="x", pady=5)
        
        # ===== ตารางข้อมูล =====
        table_frame = ttk.LabelFrame(self.root, text="📋 ข้อมูล (แสดงล่าสุด 100 รายการ)", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("วันที่", "สถานี", "ระดับน้ำ", "เวลา", "สถานะ")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        col_widths = {"วันที่": 120, "สถานี": 100, "ระดับน้ำ": 120, "เวลา": 100, "สถานะ": 150}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== ส่วนล่าง: Log =====
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        log_frame = ttk.LabelFrame(bottom_frame, text="📝 บันทึก", padding=10)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # ปุ่มจัดการ
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="💾 บันทึก CSV", command=self.save_csv, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📁 บันทึก JSON", command=self.save_json, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 รีเฟรช", command=lambda: self.refresh_table(self.app.data_manager.data), width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 สถิติ", command=self.app.show_statistics, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🚪 ออก", command=self.app.exit_app, width=15).pack(side="right", padx=5)
    
    def add_log(self, message):
        """เพิ่มข้อความใน Log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_count += 1
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
        # จำกัดขนาด Log
        if self.log_count > 500:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "50.0")
            self.log_text.configure(state="disabled")
            self.log_count = 0
    
    def update_status(self, text, progress=None, records=None):
        """อัปเดตสถานะ"""
        self.status_label.config(text=text)
        if progress is not None:
            self.progress['value'] = progress
        if records is not None:
            self.record_label.config(text=f"จำนวนข้อมูล: {records} รายการ")
        self.root.update_idletasks()
    
    def refresh_table(self, data: List[Dict]):
        """รีเฟรชตารางข้อมูล"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # แสดง 100 รายการล่าสุด
        display_data = data[-100:] if len(data) > 100 else data
        for item in reversed(display_data):
            self.tree.insert("", "end", values=(
                item.get('date', ''),
                item.get('station_id', ''),
                item.get('water_level', ''),
                item.get('time', ''),
                item.get('status', '')
            ))
        
        self.record_label.config(text=f"จำนวนข้อมูล: {len(data)} รายการ")
    
    def set_fetching_state(self, is_fetching: bool):
        """เปลี่ยนสถานะการดึงข้อมูล"""
        if is_fetching:
            self.fetch_btn.config(state="disabled")
            self.start_btn.config(state="disabled")
        else:
            self.fetch_btn.config(state="normal")
            self.start_btn.config(state="normal")
    
    def set_auto_update_state(self, is_running: bool):
        """เปลี่ยนสถานะอัปเดตอัตโนมัติ"""
        if is_running:
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.fetch_btn.config(state="disabled")
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.fetch_btn.config(state="normal")
    
    def save_csv(self):
        """บันทึกเป็น CSV"""
        if not self.app.data_manager.data:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะบันทึก")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"water_data_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if file_path:
            success = self.app.save_data(file_path, 'csv')
            if success:
                messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูลเรียบร้อย")
    
    def save_json(self):
        """บันทึกเป็น JSON"""
        if not self.app.data_manager.data:
            messagebox.showwarning("แจ้งเตือน", "ไม่มีข้อมูลที่จะบันทึก")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"water_data_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        if file_path:
            success = self.app.save_data(file_path, 'json')
            if success:
                messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูลเรียบร้อย")
