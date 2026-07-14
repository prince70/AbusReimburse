@echo off
chcp 65001 >nul
echo ==============================================
echo           开始更新 ABUS 项目代码
echo ==============================================
echo.

cd /d D:\Web\Reimbursement

echo 正在清理 Python 缓存...
del /s /q *.pyc 2>nul >nul
for /d /r . %%d in (__pycache__) do rd /s /q "%%d" 2>nul >nul

echo.
echo 正在拉取代码...
git pull origin main
if %errorlevel% equ 0 (
    echo ✅ 代码更新成功
) else (
    echo ❌ 代码更新失败
)
echo.

echo 正在重建前端...
cd /d D:\Web\Reimbursement\ABUS
call npm run build
if %errorlevel% equ 0 (
    echo ✅ 前端构建成功
) else (
    echo ❌ 前端构建失败
)
echo.

echo 正在重启后端...
:: 停止旧后端进程
taskkill /f /im python.exe >nul 2>nul
:: 启动新后端
start "ABUS Backend" cmd /c "cd /d D:\Web\Reimbursement\fastapi && python main.py"
if %errorlevel% equ 0 (
    echo ✅ 后端已重启
) else (
    echo ❌ 后端重启失败
)
echo.

echo ==============================================
echo                所有操作执行完毕
echo ==============================================
pause
