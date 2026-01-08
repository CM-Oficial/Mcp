import os
import sys
import subprocess
import json
import zipfile
import hashlib
import time

# --- AUTO-INSTALADOR DA LIB REQUESTS ---
try:
    import requests
except ImportError:
    print("Instalando dependencias necessarias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

# URL do seu servidor Surge
REPO_URL = "https://mcpor.surge.sh"

def gerar_mid(nome):
    return hashlib.md5(f"{nome}{time.time()}".encode()).hexdigest()[:8].upper()

def help_menu():
    print("\n--- MCP MANAGER (CONSOLE) ---")
    print("setup    : Criar nova pasta de projeto")
    print("pack     : Gerar pacote .mcp dos projetos locais")
    print("mpush    : Enviar o pacote .mcp para o servidor")
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
    
    print(f"\n[OK] Pasta {pasta} criada com sucesso.")
    print(f"Coloque seus arquivos dentro dela antes de dar 'pack'.")

def pack():
    # Procura por pastas que começam com o padrão RI_BIN_N_
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith("RI_BIN_N_")]
    
    if not pastas:
        print("\n[!] Erro: Nenhuma pasta de projeto (RI_BIN_N_...) encontrada.")
        return

    for p in pastas:
        try:
            with open(os.path.join(p, "mcp_manifest.json"), "r") as f:
                dados = json.load(f)
                nome_zip = dados['name']
            
            # Cria o arquivo .mcp (que é um zip)
            arquivo_mcp = f"{nome_zip}.mcp"
            with zipfile.ZipFile(arquivo_mcp, 'w', zipfile.ZIP_DEFLATED) as z:
                for raiz, dirs, arquivos in os.walk(p):
                    for arq in arquivos:
                        caminho_completo = os.path.join(raiz, arq)
                        caminho_relativo = os.path.relpath(caminho_completo, '.')
                        z.write(caminho_completo, caminho_relativo)
            
            print(f"[OK] Pacote gerado: {arquivo_mcp}")
        except Exception as e:
            print(f"[!] Erro ao empacotar {p}: {e}")

def mpush():
    # Busca arquivos .mcp na pasta atual
    arqs = [f for f in os.listdir('.') if f.endswith('.mcp')]
    
    if not arqs:
        print("\n[!] Erro: Nenhum arquivo .mcp encontrado. Rode o 'pack' primeiro.")
        return
    
    arquivo = arqs[0] # Pega o primeiro que encontrar
    print(f"\n[+] Preparando upload de: {arquivo}")

    # RESOLUÇÃO DO ERRO ENOTDIR: O Surge precisa subir uma pasta
    os.makedirs("upload_temp", exist_ok=True)
    os.system(f"cp {arquivo} upload_temp/")

    print(f"[+] Enviando para {REPO_URL}...")
    # O comando abaixo envia o conteudo de upload_temp para a raiz do seu surge
    # Se quiser que vá para uma pasta /incoming, o REPO_URL deve ter isso ou mudar aqui
    os.system(f"surge upload_temp {REPO_URL}")

    # Limpa a pasta temporaria
    os.system("rm -rf upload_temp")
    print("\n[BINGO] Upload concluido.")

def minstall():
    print("\n--- INSTALADOR MCP ---")
    nome = input("Digite o nome da ferramenta: ").strip()
    
    try:
        # Busca o catalogo no servidor
        r = requests.get(f"{REPO_URL}/repo.json")
        if r.status_code != 200:
            print("[!] Erro: Nao foi possivel acessar o arquivo repo.json no servidor.")
            return
            
        repo = r.json()
        
        if nome in repo["packages"]:
            info = repo["packages"][nome]
            mid = info["folder"]
            # Tenta baixar o arquivo .mcp da estrutura de pastas do servidor
            url_dl = f"{REPO_URL}/RI_bin/{mid}/{nome}.mcp"
            
            print(f"[+] Baixando {nome} de {url_dl}...")
            dl = requests.get(url_dl)
            
            if dl.status_code == 200:
                pasta_destino = os.path.expanduser(f"~/RI_BIN/{mid}")
                os.makedirs(pasta_destino, exist_ok=True)
                
                caminho_mcp = os.path.join(pasta_destino, f"{nome}.mcp")
                with open(caminho_mcp, "wb") as f:
                    f.write(dl.content)
                
                # Extrai os arquivos
                with zipfile.ZipFile(caminho_mcp, 'r') as z:
                    z.extractall(pasta_destino)
                
                print(f"[OK] Ferramenta instalada em: {pasta_destino}")
            else:
                print(f"[!] Erro: O arquivo {nome}.mcp nao foi encontrado no servidor.")
        else:
            print(f"[!] Erro: A ferramenta '{nome}' nao esta registrada no repo.json.")
            
    except Exception as e:
        print(f"[!] Erro de conexao ou processamento: {e}")

# --- LOOP DO CONSOLE INTERATIVO ---
def main():
    print("\n===============================")
    print("    MCP SYSTEM CONSOLE V1.0    ")
    print("===============================")
    help_menu()
    
    while True:
        try:
            # Prompt de comando seco, sem barras
            cmd = input("\nmcp > ").strip().lower()
            
            if not cmd:
                continue
            elif cmd == "setup":
                setup()
            elif cmd == "pack":
                pack()
            elif cmd == "mpush":
                mpush()
            elif cmd == "minstall":
                minstall()
            elif cmd == "help":
                help_menu()
            elif cmd == "exit" or cmd == "quit":
                print("Encerrando console...")
                break
            else:
                print(f"Comando '{cmd}' desconhecido. Digite 'help' para ver as opcoes.")
        except KeyboardInterrupt:
            print("\nUse 'exit' para fechar o programa.")
        except Exception as e:
            print(f"\n[!] Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
