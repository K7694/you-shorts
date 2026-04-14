@echo off
:: YOU — Single video run (called by Windows Task Scheduler)
cd /d C:\You-shorts

:: Create logs folder if missing
if not exist logs mkdir logs

:: Log file named by date
set LOGFILE=logs\autopilot_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log

echo. >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo %date% %time% — Starting video run >> %LOGFILE%
echo ======================================== >> %LOGFILE%

:: Run with UTF-8 output
set PYTHONIOENCODING=utf-8
python you.py >> %LOGFILE% 2>&1

echo %date% %time% — Done >> %LOGFILE%
