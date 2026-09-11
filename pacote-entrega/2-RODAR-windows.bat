@echo off
REM ============================================================
REM RODAR — MeuReserva (Windows)
REM Duplo-clique neste arquivo para abrir o app.
REM ============================================================

cd /d "%~dp0\meureserva"

echo.
echo ================================================================
echo   Abrindo MeuReserva no seu navegador...
echo   Endereco: http://localhost:8512
echo.
echo   Para encerrar o app, feche esta janela ou pressione Ctrl+C.
echo ================================================================
echo.

timeout /t 5 /nobreak >nul
start "" "http://localhost:8512"

.venv\Scripts\streamlit.exe run app.py --server.port 8512 --browser.gatherUsageStats false
