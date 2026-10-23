@echo off
chcp 65001 >nul
title OmniVideo Studio
cd /d "%~dp0"

if exist "..\Transcriptor\entorno\Scripts\python.exe" (
    "..\Transcriptor\entorno\Scripts\python.exe" "app_omnivideo_studio.py"
) else (
    python "app_omnivideo_studio.py"
)
