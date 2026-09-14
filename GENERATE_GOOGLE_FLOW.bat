@echo off
title Prometheus Core - Google Flow Generator
cd /d "%~dp0"
echo ============================================================
echo   PROMETHEUS CORE: GOOGLE FLOW VEO 3.1 GENERATION DISPATCH
echo ============================================================
echo.
python -u scripts\generate_in_flow_browser.py
pause
