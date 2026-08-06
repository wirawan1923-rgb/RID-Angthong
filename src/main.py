"""
Hydrology Data Bot - Main Entry Point
ดึงข้อมูลระดับน้ำจากกรมชลประทาน
"""

import sys
import os
import tkinter as tk

# เพิ่ม path เพื่อให้ import โฟลเดอร์อื่นได้
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import HydrologyApp
from config.settings import APP_NAME, APP_VERSION


def main():
    """ฟังก์ชันหลักในการเริ่มต้นแอปพลิเคชัน"""
    root = tk.Tk()
    app = HydrologyApp(root)
    
    # ตั้งชื่อหน้าต่าง
    root.title(f"{APP_NAME} v{APP_VERSION}")
    
    # กำหนดขนาดหน้าต่าง
    root.geometry("1100x800")
    
    # ให้ปรับขนาดได้
    root.resizable(True, True)
    
    # เริ่มแอป
    root.mainloop()


if __name__ == "__main__":
    main()
