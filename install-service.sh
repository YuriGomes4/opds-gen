#!/bin/bash

###############################################################################
# Script de Instalação do OPDS Generator como Serviço Systemd
###############################################################################

set -e  # Parar em caso de erro

echo "=========================================="
echo "OPDS Generator - Instalação de Serviço"
echo "=========================================="
echo

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  ERRO: Não execute este script como root (sudo)!"
    echo "   Execute como usuário normal. O script pedirá sudo quando necessário."
    exit 1
fi

# Obter diretório atual
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Diretório do projeto: $SCRIPT_DIR"
echo

# Verificar se opds-gen.py existe
if [ ! -f "$SCRIPT_DIR/opds-gen.py" ]; then
    echo "❌ Erro: opds-gen.py não encontrado em $SCRIPT_DIR"
    exit 1
fi

# Pedir informações ao usuário
echo "📝 Por favor, forneça as seguintes informações:"
echo

read -p "📚 Diretório dos livros (ex: /media/HD/Media/Livros): " BOOKS_DIR
if [ ! -d "$BOOKS_DIR" ]; then
    echo "⚠️  Aviso: Diretório '$BOOKS_DIR' não existe!"
    read -p "   Deseja continuar mesmo assim? (s/N): " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        echo "Instalação cancelada."
        exit 1
    fi
fi

read -p "🔌 Porta do servidor (padrão: 8080): " PORT
PORT=${PORT:-8080}

read -p "⏱️  Intervalo de reescaneamento em segundos (padrão: 300): " INTERVAL
INTERVAL=${INTERVAL:-300}

echo
echo "📋 Resumo da Configuração:"
echo "   Usuário: $USER"
echo "   Grupo: $(id -gn)"
echo "   Diretório de trabalho: $SCRIPT_DIR"
echo "   Diretório de livros: $BOOKS_DIR"
echo "   Porta: $PORT"
echo "   Intervalo: $INTERVAL segundos"
echo

read -p "Confirmar instalação? (s/N): " CONFIRM
if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo "Instalação cancelada."
    exit 0
fi

echo
echo "🔧 Instalando serviço..."

# Encontrar caminho do Python
PYTHON_PATH=$(which python3)
echo "   Python encontrado em: $PYTHON_PATH"

# Criar arquivo de serviço temporário
TEMP_SERVICE=$(mktemp)

cat > "$TEMP_SERVICE" << EOF
[Unit]
Description=OPDS Generator - Servidor de catálogo de livros para KOReader
Documentation=https://github.com/YuriGomes4/opds-gen
After=network.target

[Service]
Type=simple
User=$USER
Group=$(id -gn)
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_PATH $SCRIPT_DIR/opds-gen.py -dir $BOOKS_DIR -port $PORT -interval $INTERVAL
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=opds-gen

[Install]
WantedBy=multi-user.target
EOF

# Copiar para /etc/systemd/system/
echo "   Copiando arquivo de serviço para /etc/systemd/system/..."
sudo cp "$TEMP_SERVICE" /etc/systemd/system/opds-gen.service
rm "$TEMP_SERVICE"

# Tornar o script executável
echo "   Tornando opds-gen.py executável..."
chmod +x "$SCRIPT_DIR/opds-gen.py"

# Recarregar systemd
echo "   Recarregando systemd..."
sudo systemctl daemon-reload

# Habilitar serviço
echo "   Habilitando serviço para iniciar no boot..."
sudo systemctl enable opds-gen

# Iniciar serviço
echo "   Iniciando serviço..."
sudo systemctl start opds-gen

# Aguardar um momento
sleep 2

# Verificar status
echo
echo "=========================================="
echo "✅ Instalação Concluída!"
echo "=========================================="
echo

sudo systemctl status opds-gen --no-pager -l

echo
echo "📊 Comandos úteis:"
echo "   Ver status:        sudo systemctl status opds-gen"
echo "   Ver logs:          sudo journalctl -u opds-gen -f"
echo "   Parar serviço:     sudo systemctl stop opds-gen"
echo "   Reiniciar serviço: sudo systemctl restart opds-gen"
echo "   Desabilitar:       sudo systemctl disable opds-gen"
echo
echo "🌐 Acesse o catálogo OPDS em:"
echo "   http://localhost:$PORT/opds"
echo "   http://$(hostname -I | awk '{print $1}'):$PORT/opds"
echo
echo "📱 Configure no KOReader com a URL:"
echo "   http://SEU_IP:$PORT/opds"
echo
