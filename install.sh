#!/bin/bash

echo "Instalando MakeCPkg (MCP)..."

# 1. Instala dependências do Termux
pkg install python python-pip nodejs -y
npm install -g surge

# 2. Baixa o script principal do seu Repo
mkdir -p ~/mcp_system
curl -sL https://raw.githubusercontent.com/CM-oficial/MakeCPkg/main/src/mcp.py -o ~/mcp_system/mcp.py

# 3. Cria o atalho (Alias)
echo "alias mcp='python3 ~/mcp_system/mcp.py'" >> ~/.bashrc
source ~/.bashrc

echo "--------------------------------------"
echo "BINGO! Digite 'mcp' para começar."
echo "--------------------------------------"
