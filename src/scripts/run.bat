@echo off
title Hydrology Data Bot - กรมชลประทาน

echo ========================================
echo   Hydrology Data Bot v1.0.0
echo   กรมชลประทาน
echo ========================================
echo.

REM ตรวจสอบว่า Python ติดตั้งหรือไม่
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python กรุณาติดตั้ง Python ก่อน
    echo ดาวน์โหลดได้ที่: https://python.org
    pause
    exit /b 1
)

echo [OK] พบ Python
echo.

REM ตรวจสอบและติดตั้งไลบรารี
echo กำลังตรวจสอบไลบรารีที่จำเป็น...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo [ERROR] ไม่สามารถติดตั้งไลบรารีได้
    pause
    exit /b 1
)

echo.
echo [OK] พร้อมใช้งาน
echo.

REM เปลี่ยนไปที่ไดเรกทอรีหลัก
cd /d "%~dp0\..

echo กำลังเปิดแอปพลิเคชัน...
python src/main.py

pause
