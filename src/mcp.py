
import os
import sys
import subprocess
import json
import zipfile
import hashlib
import time

# --- AUTO-INSTALADOR DE DEPENDÊNCIAS ---
try:
    import requests
except ImportError:
    print("\033[1;33m[*] Instalando requests para comunicação com o Repo...\033[0m")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# --- CONFIGURAÇÃO DO SEU IMPÉRIO ---
REPO_URL = "https://mcpor.surge.sh"

def gerar_mid(nome_projeto):
    semente = f"{nome_projeto}{time.time()}"
    return hashlib.md5(semente.encode()).hexdigest()[:8].upper()

def mostrar_help():
    print(f"""
\033[1;34m      __   tray   ____     \033[0m
\033[1;34m     /  |/  /____/ __ \    \033[0m
\033[1;34m    / /|_/ / ___/ /_/ /    \033[0m
\033[1;34m   / /  / / /__/ ____/     \033[0m
\033[1;34m  /_/  /_/\___/_/          \033[0m v1.5
    
\033[1;37mComandos Disponíveis:\033[0m
\033[1;32msetup\033[0m    : Inicia o projeto e gera o \033[1;33mMID\033[0m.
\033[1;32mpack\033[0m     : Valida e compacta em um pacote \033[1;35m.mcp\033[0m.
\033[1;32mmpush\033[0m    : Envia o seu .mcp para o servidor (Surge).
\033[1;32mminstall\033[0m : Busca e instala uma ferramenta do Repo.
\033[1;32m/help\033[0m    : Exibe este manual.
    """)

def setup():
    print("\033[1;34m[*] Iniciando Setup...\033[0m")
    nome = input("Nome do projeto: ").strip().replace(" ", "_")
    versao = input("Versão [ex: 1.0]: ")
    autor = input("Seu nick: ")
    
    mid = gerar_mid(nome)
    nome_pasta = f"RI_BIN_N_{mid}"
    os.makedirs(nome_pasta, exist_ok=True)
    
    manifesto = {
        "mid": mid,
        "name": nome,
        "version": versao,
        "author": autor,
        "timestamp": int(time.time())
    }
    
    with open(os.path.join(nome_pasta, "mcp_manifest.json"), "w") as f:
        json.dump(manifesto, f, indent=4)
        
    print(f"\n\033[1;32m[SUCESSO]\033[0m Pasta \033[1;36m{nome_pasta}\033[0m criada.")
    print(f"Coloque seus arquivos nela e use: \033[1;33mmcp pack\033[0m")

def pack():
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith("RI_BIN_N_")]
    if not pastas:
        print("\033[31mErro: Nenhuma pasta de projeto encontrada.\033[0m")
        return

    for pasta in pastas:
        manifest_path = os.path.join(pasta, "mcp_manifest.json")
        if not os.path.exists(manifest_path): continue
        
        with open(manifest_path, 'r') as f:
            meta = json.load(f)
        
        arquivo_mcp = f"{meta['name']}.mcp"
        with zipfile.ZipFile(arquivo_mcp, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(pasta):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), '.'))
        
        print(f"\033[1;32m[BINGO!]\033[0m Pacote \033[1;35m{arquivo_mcp}\033[0m gerado.")

def mpush():
    arquivos = [f for f in os.listdir('.') if f.endswith('.mcp')]
    if not arquivos:
        print("\033[31mErro: Nenhum arquivo .mcp para enviar.\033[0m")
        return
    
    arquivo = arquivos[0]
    print(f"\033[1;34m[*] Enviando {arquivo} para o servidor...\033[0m")
    os.system(f"surge {arquivo} {REPO_URL}/incoming")
    print("\033[1;32m[ENVIADO]\033[0m Aguarde a análise da Sandbox.")

def minstall():
    print("\033[1;34m[MCP INSTALLER]\033[0m")
    nome_app = input("Ferramenta para instalar: ").strip()
    
    try:
        print(f"Conectando ao Repo... \033[1;32mOK\033[0m")
        r = requests.get(f"{REPO_URL}/repo.json")
        if r.status_code != 200:
            print("\033[31mErro: Não foi possível ler o repo.json no Surge.\033[0m")
            return
            
        repo = r.json()
        if nome_app in repo["packages"]:
            pkg = repo["packages"][nome_app]
            mid_folder = pkg["folder"]
            print(f"Baixando {nome_app} v{pkg['version']}...")
            
            # Simulação de Download e Extração
            base_path = os.path.expanduser("~/RI_BIN")
            os.makedirs(base_path, exist_ok=True)
            # Aqui entraria o requests.get(url_do_mcp)
            
            print(f"\033[1;32m[SUCESSO]\033[0m Instalado em ~/RI_BIN/{mid_folder}")
        else:
            print("\033[31mErro: Ferramenta não listada no Repo Oficial.\033[0m")
    except Exception as e:
        print(f"\033[31mErro: {e}\033[0m")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        mostrar_help()
    else:
        cmd = sys.argv[1].lower()
        if cmd == "setup": setup()
        elif cmd == "pack": pack()
        elif cmd == "mpush": mpush()
        elif cmd == "minstall": minstall()
        elif cmd in ["/help", "help"]: mostrar_help()
        else: mostrar_help()
