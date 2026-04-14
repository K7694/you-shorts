@echo off
:: YOU — Windows Task Scheduler setup
:: Run this ONCE as Administrator to schedule 3 daily video runs.
:: Videos will be created at 9AM, 3PM, and 9PM every day.

echo.
echo  YOU — Setting up automatic video schedule...
echo  3 videos per day: 9AM, 3PM, 9PM
echo.

set SCRIPT=%~dp0run_video.bat

:: Morning (9:00 AM)
schtasks /create /tn "YOU_Morning" ^
  /tr "%SCRIPT%" ^
  /sc daily /st 09:00 ^
  /ru "%USERNAME%" ^
  /f

:: Afternoon (3:00 PM)
schtasks /create /tn "YOU_Afternoon" ^
  /tr "%SCRIPT%" ^
  /sc daily /st 15:00 ^
  /ru "%USERNAME%" ^
  /f

:: Evening (9:00 PM)
schtasks /create /tn "YOU_Evening" ^
  /tr "%SCRIPT%" ^
  /sc daily /st 21:00 ^
  /ru "%USERNAME%" ^
  /f

echo.
echo  Done! Scheduled tasks created:
echo    YOU_Morning   — 9:00 AM daily
echo    YOU_Afternoon — 3:00 PM daily
echo    YOU_Evening   — 9:00 PM daily
echo.
echo  To verify: open Task Scheduler and look for YOU_Morning / YOU_Afternoon / YOU_Evening
echo  To remove: run  schtasks /delete /tn "YOU_Morning" /f  (and same for the others)
echo  Logs saved to: %~dp0logs\
echo.
pause
