#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$SCRIPT_DIR/backend"
FRONTEND="$SCRIPT_DIR/frontend"

echo ""
echo "  ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗██╗   ██╗███╗   ███╗"
echo "  ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝██║   ██║████╗ ████║"
echo "  ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   ██║   ██║██╔████╔██║"
echo "  ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   ██║   ██║██║╚██╔╝██║"
echo "  ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║"
echo "  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝"
echo ""
echo "  Ads Dashboard — Natal 2026"
echo ""

# Check .env
if [ ! -f "$BACKEND/.env" ]; then
  echo "  ⚠️  Arquivo .env não encontrado!"
  echo "  Copie e preencha: cp backend/.env.example backend/.env"
  echo ""
fi

# Install dependencies if needed
if [ ! -d "$BACKEND/.venv" ]; then
  echo "  → Criando ambiente virtual..."
  python3 -m venv "$BACKEND/.venv"
  echo "  → Instalando dependências..."
  "$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt"
  echo "  ✓ Dependências instaladas"
  echo ""
fi

echo "  → Backend:  http://localhost:8000"
echo "  → Docs API: http://localhost:8000/docs"
echo "  → Frontend: abra frontend/index.html no browser"
echo ""
echo "  Pressione Ctrl+C para parar."
echo ""

cd "$BACKEND"
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
