@echo off
cd /d "%~dp0"
echo El bot corre solo en GitHub Actions las 24 hs.
echo Esto abre el dashboard local para verlo (se sincroniza solo).
start "TradingBot - Dashboard" cmd /k python dashboard.py
timeout /t 3 /nobreak >nul
start http://localhost:8800
