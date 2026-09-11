#!/bin/bash
# ============================================================
# INSTALADOR — MeuReserva (Mac)
# Duplo-clique neste arquivo para instalar.
# ============================================================

set -e
trap 'echo ""; echo "ERRO: Instalacao falhou. Verifique a mensagem acima."; echo ""; read -p "Pressione ENTER para fechar..."; exit 1' ERR
cd "$(dirname "$0")"

echo ""
echo "================================================================"
echo "  Instalando MeuReserva"
echo "  Seu assistente financeiro pessoal — orcamento 50/30/20"
echo "================================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 nao esta instalado."
    echo ""
    echo "Baixe e instale em: https://www.python.org/downloads/"
    echo "Depois rode este instalador novamente."
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

echo "[1/5] Descompactando o app..."
if [ ! -d "meureserva" ]; then
    unzip -q meureserva.zip
fi

echo "[2/5] Criando ambiente Python..."
cd meureserva
python3 -m venv .venv

echo "[3/5] Instalando dependencias..."
.venv/bin/python3 -m pip install --quiet --upgrade pip
.venv/bin/python3 -m pip install --quiet -r requirements.txt

echo "[4/5] Configurando (gerando chave de seguranca)..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    SECRET=$(.venv/bin/python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/^SECRET_KEY=$/SECRET_KEY=$SECRET/" .env && rm -f .env.bak
fi

echo "[5/5] Testando instalacao..."
.venv/bin/python3 -c "import streamlit, plotly, pandas, qrcode; print('OK: dependencias instaladas')"

echo ""
echo "================================================================"
echo "  Instalacao concluida com sucesso!"
echo ""
echo "  Para usar o app, de duplo-clique em:"
echo "     2-RODAR-mac.command"
echo "================================================================"
echo ""
read -p "Pressione ENTER para fechar..."
