#!/bin/bash

# Cores para o log do GitHub
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_DIR=$1
MALWARE_FOUND=false

echo -e "${GREEN}[*] Iniciando Varredura de Segurança na pasta: $TARGET_DIR${NC}"

# Lista de strings proibidas (Regex)
BANNED_PATTERNS=(
    "rm -rf /"
    "rm -rf \$HOME"
    "termux-setup-storage"
    "chmod 777 /"
    "curl.*|.*bash"
    ":(){:|:&};:"
)

for pattern in "${BANNED_PATTERNS[@]}"; do
    if grep -rE "$pattern" "$TARGET_DIR"; then
        echo -e "${RED}[!] PERIGO: Padrão malicioso encontrado: $pattern${NC}"
        MALWARE_FOUND=true
    fi
done

if [ "$MALWARE_FOUND" = true ]; then
    exit 1
else
    echo -e "${GREEN}[V] Código limpo. BINGO!${NC}"
    exit 0
fi
