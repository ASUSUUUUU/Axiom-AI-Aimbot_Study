@echo off
chcp 65001 >nul
cd /d "%~dp0"
net session >nul 2>&1
if %errorlevel% NEQ 0 (
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -Verb RunAs -ArgumentList '/c','""%~f0"" %*'" 
	exit /b
)

src\python\python.exe src\main.py
pause

