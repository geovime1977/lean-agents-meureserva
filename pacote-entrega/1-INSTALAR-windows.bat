@echo off
REM ============================================================
REM INSTALADOR — MeuReserva (Windows)
REM Duplo-clique neste arquivo para instalar.
REM ============================================================

cd /d "%~dp0"

echo.
echo ================================================================
echo   Instalando MeuReserva
echo   Seu assistente financeiro pessoal — orcamento 50/30/20
echo ================================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python 3 nao esta instalado.
    echo.
    echo Baixe e instale em: https://www.python.org/downloads/
    echo IMPORTANTE: Na instalacao, marque a opcao "Add Python to PATH".
    echo Depois rode este instalador novamente.
    echo.
    pause
    exit /b 1
)

echo [1/5] Descompactando o app...
if not exist "meureserva\" (
    powershell -Command "Expand-Archive -Path meureserva.zip -DestinationPath . -Force"
)

echo [2/5] Criando ambiente Python...
cd meureserva
python -m venv .venv

echo [3/5] Instalando dependencias...
.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
if errorlevel 1 (
    echo ERRO: Falha ao atualizar pip. Instalacao interrompida.
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias. Instalacao interrompida.
    pause
    exit /b 1
)

echo [4/5] Configurando (gerando chave de seguranca)...
if not exist ".env" (
    copy /Y .env.example .env >nul
    for /f "delims=" %%s in ('.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"') do set SECRET=%%s
    powershell -Command "(Get-Content .env) -replace '^SECRET_KEY=$', 'SECRET_KEY=%SECRET%' | Set-Content .env"
)

echo [5/5] Testando instalacao...
.venv\Scripts\python.exe -c "import streamlit, plotly, pandas, qrcode; print('OK: dependencias instaladas')"

echo.
echo ================================================================
echo   Instalacao concluida com sucesso!
echo.
echo   Para usar o app, de duplo-clique em:
echo      2-RODAR-windows.bat
echo ================================================================
echo.
pause
