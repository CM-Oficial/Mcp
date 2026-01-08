import os, sys, subprocess, json, zipfile, hashlib, time

# Tenta importar requests ou instala automaticamente
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

# --- CONFIGURAÇÕES ---
REPO_URL = "https://mcpor-oficial.surge.sh"
HEADERS = {'User-Agent': 'MCP-Console-Client/1.6'}

def gerar_mid(nome):
    return hashlib.md5(f"{nome}{time.time()}".encode()).hexdigest()[:8].upper()

def setup():
    nome = input("Nome do projeto: ").strip().replace(" ", "_")
    mid = gerar_mid(nome)
    pasta = f"RI_BIN_N_{mid}"
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "mcp_manifest.json"), "w") as f:
        json.dump({"mid": mid, "name": nome, "author": "CM-oficial", "date": time.strftime("%Y-%m-%d")}, f, indent=4)
    print(f"\n[OK] Pasta {pasta} criada! ID: {mid}")

def pack():
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith("RI_BIN_N_")]
    if not pastas: return print("\n[!] Erro: Nenhuma pasta RI_BIN_N_ encontrada.")
    for p in pastas:
        try:
            with open(os.path.join(p, "mcp_manifest.json"), "r") as f:
                nome_zip = json.load(f)['name']
            arquivo_mcp = f"{nome_zip}.mcp"
            with zipfile.ZipFile(arquivo_mcp, 'w', zipfile.ZIP_DEFLATED) as z:
                for raiz, _, arquivos in os.walk(p):
                    for arq in arquivos:
                        caminho_f = os.path.join(raiz, arq)
                        z.write(caminho_f, os.path.relpath(caminho_f, '.'))
            print(f"[OK] Pacote gerado: {arquivo_mcp}")
        except Exception as e: print(f"[!] Erro no pack: {e}")

def mpush():
    arqs = [f for f in os.listdir('.') if f.endswith('.mcp')]
    if not arqs: return print("\n[!] Erro: Use 'pack' primeiro.")
    
    repo_data = {"packages": {}}
    try:
        r = requests.get(f"{REPO_URL}/repo.json", headers=HEADERS, timeout=10)
        if r.status_code == 200: repo_data = r.json()
    except: print("[!] Criando novo catalogo no servidor...")

    os.makedirs("upload_temp/RI_bin", exist_ok=True)
    for arquivo_nome in arqs:
        nome_ferramenta = arquivo_nome.replace(".mcp", "")
        # Busca a pasta física para obter o ID correto
        for d in os.listdir('.'):
            if os.path.isdir(d) and d.startswith("RI_BIN_N_"):
                with open(os.path.join(d, "mcp_manifest.json"), "r") as f:
                    if json.load(f)['name'] == nome_ferramenta:
                        caminho_dst = os.path.join("upload_temp/RI_bin", d)
                        os.makedirs(caminho_dst, exist_ok=True)
                        os.system(f"cp {arquivo_nome} {caminho_dst}/")
                        repo_data["packages"][nome_ferramenta] = {"folder": d, "date": time.strftime("%Y-%m-%d")}

    with open("upload_temp/repo.json", "w") as f:
        json.dump(repo_data, f, indent=4)

    print("[+] Subindo para o Surge...")
    # Remove o https:// para o comando surge funcionar
    domain = REPO_URL.replace("https://", "").replace("http://", "")
    os.system(f"surge upload_temp {domain}")
    os.system("rm -rf upload_temp")
    print("[BINGO] Servidor Atualizado!")

def minstall():
    print("\n--- INSTALADOR MCP ---")
    try:
        r = requests.get(f"{REPO_URL}/repo.json", headers=HEADERS, allow_redirects=True, timeout=10)
        if r.status_code != 200: return print(f"[!] Erro {r.status_code}: Servidor offline.")
        
        repo = r.json()
        packs = list(repo["packages"].keys())
        if not packs: return print("[!] Servidor vazio.")
        
        print(f"Disponiveis: {', '.join(packs)}")
        nome = input("Ferramenta para baixar: ").strip()
        
        if nome in repo["packages"]:
            info = repo["packages"][nome]
            url_dl = f"{REPO_URL}/RI_bin/{info['folder']}/{nome}.mcp"
            print(f"[+] Baixando de: {url_dl}")
            dl = requests.get(url_dl, headers=HEADERS, allow_redirects=True)
            
            if dl.status_code == 200:
                pasta_dst = os.path.expanduser(f"~/RI_BIN/{info['folder']}")
                os.makedirs(pasta_dst, exist_ok=True)
                path_mcp = os.path.join(pasta_dst, f"{nome}.mcp")
                with open(path_mcp, "wb") as f: f.write(dl.content)
                with zipfile.ZipFile(path_mcp, 'r') as z: z.extractall(pasta_dst)
                print(f"[OK] Instalado em: {pasta_dst}")
            else: print(f"[!] Erro {dl.status_code}: Arquivo nao encontrado no servidor.")
    except Exception as e: print(f"[!] Erro: {e}")

def main():
    while True:
        print("\n=== MCP CONSOLE V1.6 ===")
        print("Comandos: setup, pack, mpush, minstall, exit")
        cmd = input("mcp > ").strip().lower()
        if cmd == "setup": setup()
        elif cmd == "pack": pack()
        elif cmd == "mpush": mpush()
        elif cmd == "minstall": minstall()
        elif cmd == "exit": break

if __name__ == "__main__":
    main()
