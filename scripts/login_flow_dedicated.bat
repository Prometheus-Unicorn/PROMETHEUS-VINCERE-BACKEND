@echo off
echo ======================================================================
echo  PROMETHEUS CORE: One-Time Google Flow Dedicated Profile Login
echo  Profile: C:\Users\HomePC\.prometheus_flow_user_data
echo ======================================================================
echo.
echo Launching native Google Chrome in dedicated persistent profile...
echo.
echo INSTRUCTIONS:
echo 1. In the Chrome window that opens, sign in to: ipsasummagnitudo@gmail.com
echo 2. Complete phone 2FA verification.
echo 3. Navigate into Google Flow workspace: https://flow.google.com
echo 4. Close Chrome when done (or leave it running).
echo.
echo Once completed, your credentials persist permanently on this machine.
echo ======================================================================

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\HomePC\.prometheus_flow_user_data" --remote-debugging-port=9222 --remote-allow-origins=* "https://flow.google.com"

pause
