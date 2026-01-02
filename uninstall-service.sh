#!/bin/bash

###############################################################################
# Script de Desinstalação do OPDS Generator Service
###############################################################################

set -e

echo "=========================================="
echo "OPDS Generator - Desinstalação de Serviço"
echo "=========================================="
echo

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  ERRO: Não execute este script como root (sudo)!"
    echo "   Execute como usuário normal. O script pedirá sudo quando necessário."
    exit 1
fi

# Confirmar desinstalação
read -p "⚠️  Tem certeza que deseja desinstalar o serviço opds-gen? (s/N): " CONFIRM
if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo "Desinstalação cancelada."
    exit 0
fi

echo
echo "🔧 Desinstalando serviço..."

# Parar o serviço
if sudo systemctl is-active --quiet opds-gen; then
    echo "   Parando serviço..."
    sudo systemctl stop opds-gen
fi

# Desabilitar o serviço
if sudo systemctl is-enabled --quiet opds-gen; then
    echo "   Desabilitando serviço..."
    sudo systemctl disable opds-gen
fi

# Remover arquivo de serviço
if [ -f /etc/systemd/system/opds-gen.service ]; then
    echo "   Removendo arquivo de serviço..."
    sudo rm /etc/systemd/system/opds-gen.service
fi

# Recarregar systemd
echo "   Recarregando systemd..."
sudo systemctl daemon-reload
sudo systemctl reset-failed

echo
echo "=========================================="
echo "✅ Desinstalação Concluída!"
echo "=========================================="
echo
echo "O serviço foi completamente removido do sistema."
echo "Os arquivos do projeto não foram removidos."
echo
