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
    print("Instalando dependencias (requests)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

# Configurações do Servidor
REPO_URL = "https://mcpor.surge.sh"

def gerar_mid(nome):
    return hashlib.md5(f"{nome}{time.time()}".encode()).hexdigest()[:8].upper()

def help_menu():
    print("\n--- MCP MANAGER PRO V1.5 ---")
    print("setup    : Criar nova pasta de projeto")
    print("pack     : Gerar pacote .mcp dos projetos locais")
    print("mpush    : Automatizar upload e atualizar catalogo no Surge")
    print("minstall : Baixar e instalar ferramenta do servidor")
    print("help     : Mostrar esta lista de comandos")
    print("exit     : Fechar o console")

def setup():
    nome = input("Nome do projeto: ").strip().replace(" ", "_")
    mid = gerar_mid(nome)
    pasta = f"RI_BIN_N_{mid}"
    os.makedirs(pasta, exist_ok=True)
    
    manifesto = {
        "mid": mid,
        "name": nome,
        "author": "CM-oficial",
        "date": time.strftime("%Y-%m-%d")
    }
    
    with open(os.path.join(pasta, "mcp_manifest.json"), "w") as f:
        json.dump(manifesto, f, indent=4)
    
    print(f"\n[OK] Pasta {pasta} criada com sucesso!")

def pack():
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith("RI_BIN_N_")]
    if not pastas:
        return print("\n[!] Erro: Nenhuma pasta RI_BIN_N_ encontrada.")

    for p in pastas:
        try:
            with open(os.path.join(p, "mcp_manifest.json"), "r") as f:
                dados = json.load(f)
                nome_zip = dados['name']
            
            arquivo_mcp = f"{nome_zip}.mcp"
            with zipfile.ZipFile(arquivo_mcp, 'w', zipfile.ZIP_DEFLATED) as z:
                for raiz, _, arquivos in os.walk(p):
                    for arq in arquivos:
                        caminho_f = os.path.join(raiz, arq)
                        z.write(caminho_f, os.path.relpath(caminho_f, '.'))
            print(f"[OK] Pacote gerado: {arquivo_mcp}")
        except Exception as e:
            print(f"[!] Erro ao empacotar {p}: {e}")

def mpush():
    arqs = [f for f in os.listdir('.') if f.endswith('.mcp')]
    if not arqs:
        return print("\n[!] Erro: Nenhum arquivo .mcp encontrado. Use 'pack' primeiro.")
    
    arquivo_nome = arqs[0]
    nome_ferramenta = arquivo_nome.replace(".mcp", "")
    
    print(f"\n[+] Iniciando sincronizacao de '{nome_ferramenta}'...")

    # 1. Tenta baixar o repo.json atual do servidor
    repo_data = {"packages": {}}
    try:
        r = requests.get(f"{REPO_URL}/repo.json", timeout=5)
        if r.status_code == 200:
            repo_data = r.json()
    except:
        print("[!] Aviso: Nao foi possivel ler o servidor. Criando novo catalogo.")

    # 2. Localiza o MID da pasta local
    mid_local = ""
    for d in os.listdir('.'):
        if os.path.isdir(d) and d.startswith("RI_BIN_N_"):
            m_path = os.path.join(d, "mcp_manifest.json")
            if os.path.exists(m_path):
                with open(m_path, "r") as f:
                    if json.load(f)['name'] == nome_ferramenta:
                        mid_local = d
                        break
    
    if not mid_local:
        return print("[!] Erro: Nao encontrei a pasta RI_BIN_N correspondente.")

    # 3. Atualiza o dicionário do catálogo
    repo_data["packages"][nome_ferramenta] = {
        "folder": mid_local,
        "date": time.strftime("%Y-%m-%d")
    }

    # 4. Prepara a pasta temporária de upload (Protege seus .py fonte)
    os.makedirs("upload_temp/RI_bin", exist_ok=True)
    caminho_destino_mcp = os.path.join("upload_temp/RI_bin", mid_local)
    os.makedirs(caminho_destino_mcp, exist_ok=True)
    
    # Copia apenas o necessário
    os.system(f"cp {arquivo_nome} {caminho_destino_mcp}/")
    with open("upload_temp/repo.json", "w") as f:
        json.dump(repo_data, f, indent=4)

    # 5. Sobe para o Surge
    print(f"[+] Enviando para o Surge...")
    os.system(f"surge upload_temp {REPO_URL}")
    
    # 6. Limpa o lixo local
    os.system("rm -rf upload_temp")
    print(f"\n[BINGO] '{nome_ferramenta}' esta online e catalogada!")

def minstall():
    print("\n--- INSTALADOR MCP ---")
    try:
        r = requests.get(f"{REPO_URL}/repo.json")
        if r.status_code != 200:
            return print("[!] Erro: O servidor esta vazio ou offline.")
        
        repo = r.json()
        packs = list(repo["packages"].keys())
        print(f"Disponiveis: {', '.join(packs)}")
        
        nome = input("Ferramenta para baixar: ").strip()
        if nome in repo["packages"]:
            info = repo["packages"][nome]
            mid = info["folder"]
            # URL corrigida para a estrutura RI_bin
            url_dl = f"{REPO_URL}/RI_bin/{mid}/{nome}.mcp"
            
            print(f"[+] Baixando de: {url_dl}")
            dl = requests.get(url_dl)
            
            if dl.status_code == 200:
                pasta_dst = os.path.expanduser(f"~/RI_BIN/{mid}")
                os.makedirs(pasta_dst, exist_ok=True)
                path_mcp = os.path.join(pasta_dst, f"{nome}.mcp")
                
                with open(path_mcp, "wb") as f:
                    f.write(dl.content)
                with zipfile.ZipFile(path_mcp, 'r') as z:
                    z.extractall(pasta_dst)
                print(f"[OK] Instalado com sucesso em: {pasta_dst}")
            else:
                print(f"[!] Erro {dl.status_code}: Arquivo nao encontrado no servidor.")
        else:
            print("[!] Nome nao consta no catalogo.")
    except Exception as e:
        print(f"[!] Erro tecnico: {e}")

def main():
    while True:
        print("\n===============================")
        print("    MCP SYSTEM CONSOLE V1.5    ")
        print("===============================")
        help_menu()
        try:
            cmd = input("\nmcp > ").strip().lower()
            if cmd == "setup": setup()
            elif cmd == "pack": pack()
            elif cmd == "mpush": mpush()
            elif cmd == "minstall": minstall()
            elif cmd == "help": help_menu()
            elif cmd == "exit": 
                print("Encerrando..."); break
            else: print(f"Comando '{cmd}' desconhecido.")
        except Exception as e: print(f"Erro: {e}")

if __name__ == "__main__":
    main()
