@echo off
title Hydrology Data Bot
echo ====================================
echo   Hydrology Data Bot
echo   กรมชลประทาน
echo ====================================
echo.
echo กำลังตรวจสอบไลบรารีที่จำเป็น...
echo.

REM ตรวจสอบและติดตั้งไลบรารี
pip install -r requirements.txt --quiet

echo.
echo กำลังเปิดแอปพลิเคชัน...
echo.
python hydrology_app.py

pause
