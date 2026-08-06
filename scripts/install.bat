@echo off
echo ========================================
echo   ติดตั้ง Hydrology Data Bot
echo ========================================
echo.

REM ตรวจสอบ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python!
    echo กรุณาติดตั้ง Python จาก https://python.org
    pause
    exit /b 1
)

echo [OK] พบ Python
python --version
echo.

REM ติดตั้งไลบรารี
echo กำลังติดตั้งไลบรารีที่จำเป็น...
echo (อาจใช้เวลาสักครู่)
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] การติดตั้งล้มเหลว
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ ติดตั้งสำเร็จ!
echo   ใช้ scripts\run.bat เพื่อเริ่มแอป
echo ========================================
pause
