@echo off
cd /d "%~dp0"
echo Iniciando TradingBot...
start "TradingBot - Dashboard" cmd /k python dashboard.py
start "TradingBot - Bot en vivo" cmd /k python -u main.py live
timeout /t 3 /nobreak >nul
start http://localhost:8800
echo Listo. Se abrieron dos ventanas (bot + dashboard) y el navegador.
