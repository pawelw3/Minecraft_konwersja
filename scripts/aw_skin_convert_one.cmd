@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0aw_skin_convert_one.ps1" "%~1" "%~2"
exit /b %ERRORLEVEL%
