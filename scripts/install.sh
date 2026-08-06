#!/bin/bash

echo "========================================"
echo "  ติดตั้ง Hydrology Data Bot"
echo "========================================"
echo ""

# ตรวจสอบ Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] ไม่พบ Python3!"
    echo "กรุณาติดตั้ง Python3 จาก https://python.org"
    exit 1
fi

echo "[OK] พบ Python3"
python3 --version
echo ""

# ติดตั้งไลบรารี
echo "กำลังติดตั้งไลบรารีที่จำเป็น..."
echo "(อาจใช้เวลาสักครู่)"
echo ""

pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] การติดตั้งล้มเหลว"
    exit 1
fi

echo ""
echo "========================================"
echo "  ✅ ติดตั้งสำเร็จ!"
echo "  ใช้ ./scripts/run.sh เพื่อเริ่มแอป"
echo "========================================"
