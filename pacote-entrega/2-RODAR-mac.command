#!/bin/bash
# ============================================================
# RODAR — MeuReserva (Mac)
# Duplo-clique neste arquivo para abrir o app.
# ============================================================

set -e
cd "$(dirname "$0")/meureserva"

echo ""
echo "================================================================"
echo "  Abrindo MeuReserva no seu navegador..."
echo "  Endereco: http://localhost:8512"
echo ""
echo "  Para encerrar o app, feche esta janela ou pressione Ctrl+C."
echo "================================================================"
echo ""

sleep 5
open "http://localhost:8512" &

.venv/bin/streamlit run app.py --server.port 8512 --browser.gatherUsageStats false
