@echo off
title FlipBoot - Cross-OS Boot Switcher
cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Set PYTHONPATH to include src directory
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"

python -m flipboot.main %* 2>nul
if %errorlevel% neq 0 (
    python src\flipboot\main.py %*
)
pause