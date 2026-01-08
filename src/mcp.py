import os
import sys
import subprocess
import json
import zipfile
import hashlib
import time

# --- AUTO-INSTALADOR SILENCIOSO ---
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

REPO_URL = "https://mcpor.surge.sh"

def gerar_mid(nome):
    return hashlib.md5(f"{nome}{time.time()}".encode()).hexdigest()[:8].upper()

def help_menu():
    print("\n--- COMANDOS ---")
    print("setup    : Criar novo projeto local")
    print("pack     : Gerar pacote .mcp para envio")
    print("mpush    : Enviar ferramenta para o servidor")
    print("minstall : Instalar ferramenta do servidor")
    print("help     : Mostrar comandos")
    print("exit     : Sair do programa")

def setup():
    nome = input("Nome do projeto: ").strip().replace(" ", "_")
    mid = gerar_mid(nome)
    pasta = f"RI_BIN_N_{mid}"
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "mcp_manifest.json"), "w") as f:
        json.dump({"mid": mid, "name": nome, "author": "CM-oficial"}, f, indent=4)
    print(f"Sucesso: Pasta {pasta} criada.")

def pack():
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith("RI_BIN_N_")]
    if not pastas:
        print("Erro: Nenhuma pasta de projeto encontrada.")
        return
    for p in pastas:
        with open(os.path.join(p, "mcp_manifest.json")) as f:
            n = json.load(f)['name']
        with zipfile.ZipFile(f"{n}.mcp", 'w', zipfile.ZIP_DEFLATED) as z:
            for r, d, fs in os.walk(p):
                for f in fs:
                    z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), '.'))
        print(f"Pronto: {n}.mcp gerado.")

def mpush():
    arqs = [f for f in os.listdir('.') if f.endswith('.mcp')]
    if not arqs:
        print("Erro: Nenhum arquivo .mcp encontrado.")
        return
    print(f"Enviando {arqs[0]}...")
    os.system(f"surge {arqs[0]} {REPO_URL}/incoming")
    print("Enviado com sucesso!")

def minstall():
    print("\n[MCP INSTALLER]")
    ferramenta = input("Nome da ferramenta para baixar: ").strip()
    
    try:
        print("Buscando no repositório...")
        # Baixa a lista de pacotes
        r = requests.get(f"{REPO_URL}/repo.json")
        if r.status_code != 200:
            print("Erro: Nao foi possivel conectar ao servidor.")
            return
            
        repo = r.json()
        
        if ferramenta in repo["packages"]:
            pkg = repo["packages"][ferramenta]
            pasta_mid = pkg["folder"]
            # Link direto para o arquivo .mcp dentro da pasta RI_bin do servidor
            url_download = f"{REPO_URL}/RI_bin/{pasta_mid}/{ferramenta}.mcp"
            
            print(f"Baixando {ferramenta} (MID: {pasta_mid})...")
            download = requests.get(url_download)
            
            if download.status_code == 200:
                # Caminho de instalacao local
                caminho_local = os.path.expanduser(f"~/RI_BIN/{pasta_mid}")
                os.makedirs(caminho_local, exist_ok=True)
                
                arquivo_final = os.path.join(caminho_local, f"{ferramenta}.mcp")
                with open(arquivo_final, "wb") as f:
                    f.write(download.content)
                
                # Extrai o conteúdo
                with zipfile.ZipFile(arquivo_final, 'r') as zip_ref:
                    zip_ref.extractall(caminho_local)
                
                print(f"BINGO! {ferramenta} instalado em ~/RI_BIN/{pasta_mid}")
            else:
                print("Erro: Arquivo nao encontrado no servidor.")
        else:
            print("Erro: Ferramenta inexistente no Repo.")
            
    except Exception as e:
        print(f"Erro na conexao: {e}")

# --- LOOP INTERATIVO ---
def main():
    print("\n[ MCP CONSOLE INICIADO ]")
    help_menu()
    
    while True:
        comando = input("\nmcp > ").strip().lower()
        
        if comando == "setup":
            setup()
        elif comando == "pack":
            pack()
        elif comando == "mpush":
            mpush()
        elif comando == "minstall":
            minstall()
        elif comando == "help":
            help_menu()
        elif comando == "exit":
            print("Encerrando...")
            break
        elif not comando:
            continue
        else:
            print(f"Comando '{comando}' invalido. Use 'help'.")

if __name__ == "__main__":
    main()
