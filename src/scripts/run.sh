#!/bin/bash

echo "========================================"
echo "  Hydrology Data Bot v1.0.0"
echo "  กรมชลประทาน"
echo "========================================"
echo ""

# ตรวจสอบ Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] ไม่พบ Python3 กรุณาติดตั้ง Python3"
    exit 1
fi

echo "[OK] พบ Python3"

# ตรวจสอบและติดตั้งไลบรารี
echo "กำลังตรวจสอบไลบรารีที่จำเป็น..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "[ERROR] ไม่สามารถติดตั้งไลบรารีได้"
    exit 1
fi

echo ""
echo "[OK] พร้อมใช้งาน"
echo ""

# เปลี่ยนไปที่ไดเรกทอรีหลัก
cd "$(dirname "$0")/.."

echo "กำลังเปิดแอปพลิเคชัน..."
python3 src/main.py
