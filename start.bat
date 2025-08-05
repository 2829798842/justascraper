@echo off
chcp 65001 >nul
title 青岛人社局通知监控系统

echo.
echo 🔧 青岛人社局通知监控系统启动器
echo =======================================
echo.

:: 检查是否在scraper目录
if not exist "scraper.py" (
    echo ❌ 错误：请在scraper目录下运行此脚本
    echo 💡 当前目录应包含scraper.py文件
    pause
    exit /b 1
)

:: 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo 🔄 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ 警告：未找到虚拟环境，使用系统Python
)

:: 运行开机自检
echo.
echo 🔍 执行开机自检...
python startup_check.py
if errorlevel 1 (
    echo.
    echo ❌ 开机自检失败，请解决问题后重试
    pause
    exit /b 1
)

echo.
echo 🎉 自检通过！
echo.
echo 请选择运行模式：
echo 1. 一次性检查（测试用）
echo 2. 长期监控模式（推荐）
echo 3. 退出
echo.
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🔍 执行一次性检查...
    python scraper.py --once
) else if "%choice%"=="2" (
    echo.
    echo 🚀 启动长期监控模式...
    echo 💡 按 Ctrl+C 可停止监控
    echo.
    python scraper.py --daemon
) else if "%choice%"=="3" (
    echo 👋 退出程序
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

echo.
echo 📝 程序已结束
pause
