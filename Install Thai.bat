@echo off
"%~dp0bloodborne-thai.exe" %*
set "result=%errorlevel%"
pause
exit /b %result%
