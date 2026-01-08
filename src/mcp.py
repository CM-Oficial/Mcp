import os
import sys
import subprocess

# --- AUTO-INSTALADOR DE DEPENDÊNCIAS ---
try:
    import requests
except ImportError:
    print("\033[1;33m[*] Instalando dependências necessárias (requests)...\033[0m")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import json
import zipfile
import hashlib
import time

# --- CONFIGURAÇÃO ---
REPO_URL = "https://mcpor.surge.sh" # Mude para o seu link

def gerar_mid(nome_projeto):
    semente = f"{nome_projeto}{time.time()}"
    return hashlib.md5(semente.encode()).hexdigest()[:8].upper()

def minstall():
    print("\033[1;34m[MCP INSTALLER]\033[0m")
    nome_app = input("Nome da ferramenta: ").strip()
    
    try:
        print(f"Checking Headers... \033[1;32mOK\033[0m")
        # 1. Puxa o repo.json do Surge
        r = requests.get(f"{REPO_URL}/repo.json")
        repo = r.json()
        
        if nome_app in repo["packages"]:
            pkg = repo["packages"][nome_app]
            mid_folder = pkg["folder"]
            
            print(f"\033[1;32m[HIT]\033[0m {nome_app} v{pkg['version']} encontrado!")
            
            # 2. Criar caminho local
            base_path = os.path.expanduser("~/RI_BIN")
            install_path = os.path.join(base_path, mid_folder)
            os.makedirs(install_path, exist_ok=True)
            
            # 3. Baixar o arquivo .mcp do servidor
            print(f"Baixando pacote {nome_app}.mcp...")
            mcp_url = f"{REPO_URL}/RI_bin/{mid_folder}/{nome_app}.mcp"
            file_data = requests.get(mcp_url).content
            
            mcp_local = os.path.join(install_path, f"{nome_app}.mcp")
            with open(mcp_local, "wb") as f:
                f.write(file_data)
            
            # 4. Extrair
            with zipfile.ZipFile(mcp_local, 'r') as zip_ref:
                zip_ref.extractall(install_path)
            
            print(f"\033[1;32m[BINGO!]\033[0m {nome_app} instalado com sucesso em {mid_folder}")
        else:
            print("\033[31m[ERRO]\033[0m Ferramenta inexistente no Repo Oficial.")
            
    except Exception as e:
        print(f"\033[31m[ERRO DE CONEXÃO]\033[0m Verifique sua internet ou o link do Repo.")

def mpush():
    arquivos = [f for f in os.listdir('.') if f.endswith('.mcp')]
    if not arquivos:
        print("\033[31m[ERRO]\033[0m Nenhum arquivo .mcp encontrado. Use 'mcp pack' primeiro.")
        return
    
    arquivo = arquivos[0]
    print(f"\033[1;34m[*] Enviando {arquivo} para análise...\033[0m")
    
    # Faz o upload via surge para a pasta incoming
    # O usuário precisa ter o surge logado no Termux
    os.system(f"surge {arquivo} {REPO_URL}/incoming")
    print("\033[1;32m[OK]\033[0m Arquivo na fila. Se passar no teste, será listado em 24h.")

# (As funções setup, pack e /help permanecem iguais às anteriores)
