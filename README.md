# OPDS Generator

Sistema completo de geração de feed OPDS para KOReader com servidor HTTP integrado.

## 📚 Sobre

O OPDS Generator é uma ferramenta Python que escaneia um diretório de livros digitais e gera automaticamente um feed OPDS (Open Publication Distribution System) compatível com o KOReader e outros leitores de e-books. O sistema inclui um servidor HTTP para servir tanto o catálogo OPDS quanto os arquivos dos livros.

### Características

- ✅ Geração automática de feed OPDS compatível com KOReader
- ✅ **URLs dinâmicas**: Links gerados automaticamente baseados no host da requisição
- ✅ Suporte a múltiplos formatos: EPUB, PDF, MOBI, AZW, AZW3, FB2, DJVU, CBZ, CBR, TXT
- ✅ Regeneração automática do catálogo a cada 5 minutos (configurável)
- ✅ Servidor HTTP integrado para servir o feed e os livros
- ✅ Organização automática por categorias e autores
- ✅ Detecção automática de metadados baseada na estrutura de diretórios
- ✅ Zero dependências externas (apenas Python padrão)

## 🌟 Destaque: URLs Dinâmicas

O sistema agora gera **URLs personalizadas automaticamente** baseadas no endereço usado para acessar o servidor! Isso significa:

- ✨ Não precisa configurar IP manualmente
- ✨ Funciona automaticamente com qualquer interface de rede (Wi-Fi, Ethernet, VPN)
- ✨ Downloads funcionam corretamente de qualquer dispositivo na rede
- ✨ Cada cliente recebe links funcionais baseados em como ele acessou o servidor

**Exemplo**: Se você acessa via `http://192.168.1.100:8080/opds`, todos os links no feed usarão `192.168.1.100:8080`. Se outro cliente acessa via `http://servidor.local:8080/opds`, os links usarão `servidor.local:8080`.

## 🚀 Instalação

### Requisitos

- Python 3.6 ou superior

### Clone o Repositório

```bash
git clone https://github.com/YuriGomes4/opds-gen.git
cd opds-gen
```

### Tornar o Script Executável

```bash
chmod +x opds-gen.py
```

### Instalação como Serviço (Linux - Recomendado)

Para instalar o OPDS Generator como um serviço systemd que inicia automaticamente no boot:

```bash
# Tornar o instalador executável
chmod +x install-service.sh

# Executar o instalador
./install-service.sh
```

O script irá solicitar:
- 📚 Diretório dos livros
- 🔌 Porta do servidor (padrão: 8080)
- ⏱️ Intervalo de reescaneamento (padrão: 300 segundos)

Veja mais detalhes na seção [Executando em Background](#-executando-em-background).

## 📖 Uso

### Uso Básico

```bash
python3 opds-gen.py -dir /caminho/para/seus/livros -port 8080
```

ou

```bash
./opds-gen.py -dir /caminho/para/seus/livros -port 8080
```

### Exemplo Real

```bash
./opds-gen.py -dir /media/HD/Media/Livros -port 8080
```

### Opções da Linha de Comando

```
opções:
  -h, --help            Mostra esta mensagem de ajuda e sai
  
  -dir DIRECTORY, --directory DIRECTORY
                        Diretório contendo os livros (obrigatório)
  
  -port PORT, --port PORT
                        Porta para o servidor HTTP (padrão: 8080)
  
  -interval INTERVAL, --interval INTERVAL
                        Intervalo de regeneração em segundos (padrão: 300 = 5 minutos)
  
  -host HOST, --host HOST
                        Host para o servidor HTTP (padrão: 0.0.0.0)
```

### Exemplos de Uso

```bash
# Porta personalizada
./opds-gen.py -dir /media/HD/Media/Livros -port 9090

# Intervalo de regeneração personalizado (10 minutos = 600 segundos)
./opds-gen.py -dir /media/HD/Media/Livros -port 8080 -interval 600

# Host específico
./opds-gen.py -dir /media/HD/Media/Livros -port 8080 -host 192.168.1.100
```

## 📁 Organização dos Livros

Para melhor detecção de metadados, organize seus livros seguindo esta estrutura:

```
/media/HD/Media/Livros/
├── Ficção/
│   ├── Isaac Asimov/
│   │   ├── Fundação.epub
│   │   └── Eu, Robô.epub
│   └── J.R.R. Tolkien/
│       ├── O Hobbit.epub
│       └── O Senhor dos Anéis.pdf
├── Técnicos/
│   ├── Python/
│   │   ├── Python Fluente.pdf
│   │   └── Automate the Boring Stuff.epub
│   └── Linux/
│       └── The Linux Command Line.pdf
└── Não Ficção/
    └── Sapiens.epub
```

O sistema irá:
- Detectar categorias pelo primeiro nível de diretórios (Ficção, Técnicos, etc.)
- Detectar autores pelo segundo nível (quando disponível)
- Usar o nome do arquivo como título do livro

## 🔌 Configuração no KOReader

1. Inicie o servidor OPDS em seu computador/servidor
2. Anote o IP da máquina onde o servidor está rodando
3. No KOReader:
   - Toque em **Menu** → **Buscar** → **Catálogo OPDS**
   - Toque em **Adicionar catálogo**
   - Insira:
     - **Nome**: Meus Livros (ou qualquer nome)
     - **URL**: `http://SEU_IP:8080/opds` (substitua SEU_IP pelo IP real)
   - Toque em **Salvar**
4. Agora você pode navegar e baixar seus livros diretamente no KOReader!

### Exemplo de URL

Se o servidor estiver rodando em um computador com IP `192.168.1.100` na porta `8080`:

```
http://192.168.1.100:8080/opds
```

## 🛠️ Estrutura do Projeto

```
opds-gen/
├── opds-gen.py              # Script principal
├── opds_generator.py        # Módulo de geração de OPDS
├── opds_server.py           # Servidor HTTP
├── requirements.txt         # Dependências (nenhuma!)
├── opds-gen.service         # Arquivo de exemplo do serviço systemd
├── install-service.sh       # Script de instalação automatizada
├── uninstall-service.sh     # Script de desinstalação
├── README.md                # Este arquivo
├── CHANGELOG.md             # Histórico de versões
└── FIXES.md                 # Resumo técnico das correções
```

## 🔧 Como Funciona

1. **Escaneamento Inicial**: O sistema escaneia recursivamente o diretório de livros na inicialização
2. **Servidor HTTP**: Inicia um servidor que responde a:
   - `/opds` - Gera o feed OPDS **dinamicamente em tempo real** com URLs personalizadas
   - `/books/*` - Serve os arquivos dos livros com encoding correto
3. **Reescaneamento Periódico**: A cada N segundos (padrão: 300), o sistema reescaneia o diretório para detectar:
   - Novos livros adicionados
   - Livros removidos
   - Mudanças na estrutura de pastas
4. **Geração Dinâmica**: Cada vez que um cliente acessa `/opds`:
   - O servidor detecta o cabeçalho `Host` da requisição HTTP
   - Gera o feed OPDS em tempo real com URLs baseadas nesse host
   - Aplica encoding correto (URL encode) para caracteres especiais (espaços, acentos, etc.)
   - Garante que todos os links funcionem corretamente para aquele cliente

### Exemplo de URLs Dinâmicas

```
Cliente 1 acessa: http://192.168.1.100:8080/opds
  → Recebe links: http://192.168.1.100:8080/books/Stephen%20King/It_%20A%20coisa.epub

Cliente 2 acessa: http://servidor.local:8080/opds
  → Recebe links: http://servidor.local:8080/books/Stephen%20King/It_%20A%20coisa.epub

Cliente 3 acessa: http://10.0.0.5:8080/opds
  → Recebe links: http://10.0.0.5:8080/books/Stephen%20King/It_%20A%20coisa.epub
```

Todos recebem links funcionais com encoding correto, adaptados ao endereço que usaram!

## 📋 Formatos Suportados

| Formato | Extensão | MIME Type |
|---------|----------|-----------|
| EPUB    | .epub    | application/epub+zip |
| PDF     | .pdf     | application/pdf |
| MOBI    | .mobi    | application/x-mobipocket-ebook |
| AZW     | .azw     | application/vnd.amazon.ebook |
| AZW3    | .azw3    | application/vnd.amazon.ebook |
| FB2     | .fb2     | text/fb2+xml |
| DJVU    | .djvu    | image/vnd.djvu |
| CBZ     | .cbz     | application/x-cbz |
| CBR     | .cbr     | application/x-cbr |
| TXT     | .txt     | text/plain |

## 🚦 Executando em Background

### Linux/macOS

Para executar o servidor em background:

```bash
nohup ./opds-gen.py -dir /media/HD/Media/Livros -port 8080 > opds-gen.log 2>&1 &
```

Para parar:

```bash
pkill -f opds-gen.py
```

### Usando systemd (Linux) - RECOMENDADO

O systemd é a forma mais robusta de executar o servidor em background no Linux. Ele garante que o serviço:
- ✅ Inicie automaticamente no boot
- ✅ Reinicie automaticamente em caso de falha
- ✅ Tenha logs centralizados
- ✅ Seja facilmente gerenciado

#### 🚀 Instalação Rápida (Script Automatizado)

A forma mais fácil é usar o script de instalação:

```bash
# Tornar o script executável
chmod +x install-service.sh

# Executar o instalador
./install-service.sh
```

O script irá:
1. ✅ Solicitar as configurações (diretório de livros, porta, intervalo)
2. ✅ Criar o arquivo de serviço systemd automaticamente
3. ✅ Habilitar e iniciar o serviço
4. ✅ Mostrar o status e comandos úteis

Para desinstalar:

```bash
# Tornar o script executável
chmod +x uninstall-service.sh

# Executar o desinstalador
./uninstall-service.sh
```

#### 📝 Instalação Manual (Passo a Passo)

Se preferir fazer manualmente ou entender o processo:

#### Passo 1: Criar o arquivo de serviço

Crie um arquivo de serviço systemd. Substitua os valores conforme seu ambiente:

```bash
sudo nano /etc/systemd/system/opds-gen.service
```

Cole o seguinte conteúdo (ajuste os caminhos e configurações):

```ini
[Unit]
Description=OPDS Generator - Servidor de catálogo de livros para KOReader
Documentation=https://github.com/YuriGomes4/opds-gen
After=network.target

[Service]
Type=simple
User=yuri
Group=yuri
WorkingDirectory=/home/yuri/Documentos/GitHub/opds-gen

# Comando para executar o servidor
# Ajuste -dir, -port e -interval conforme necessário
ExecStart=/usr/bin/python3 /home/yuri/Documentos/GitHub/opds-gen/opds-gen.py \
          -dir /media/HD/Media/Livros \
          -port 8080 \
          -interval 300

# Reiniciar automaticamente em caso de falha
Restart=on-failure
RestartSec=5s

# Limites de recursos (opcional)
# LimitNOFILE=65536

# Segurança adicional (opcional)
# NoNewPrivileges=true
# PrivateTmp=true

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=opds-gen

[Install]
WantedBy=multi-user.target
```

**Importante**: Ajuste os seguintes valores:
- `User=yuri` → Seu usuário Linux
- `Group=yuri` → Seu grupo Linux
- `WorkingDirectory=...` → Caminho completo onde está o opds-gen
- `ExecStart=...` → Caminho completo do Python e do script
- `-dir /media/HD/Media/Livros` → Seu diretório de livros
- `-port 8080` → Porta desejada
- `-interval 300` → Intervalo de reescaneamento (segundos)

#### Passo 2: Verificar caminhos

Confirme o caminho do Python:

```bash
which python3
# Saída exemplo: /usr/bin/python3
```

Confirme o caminho completo do script:

```bash
readlink -f opds-gen.py
# Saída exemplo: /home/yuri/Documentos/GitHub/opds-gen/opds-gen.py
```

#### Passo 3: Recarregar o systemd

```bash
sudo systemctl daemon-reload
```

#### Passo 4: Habilitar o serviço (iniciar no boot)

```bash
sudo systemctl enable opds-gen
```

#### Passo 5: Iniciar o serviço

```bash
sudo systemctl start opds-gen
```

#### Comandos de Gerenciamento

```bash
# Ver status do serviço
sudo systemctl status opds-gen

# Parar o serviço
sudo systemctl stop opds-gen

# Reiniciar o serviço
sudo systemctl restart opds-gen

# Ver logs em tempo real
sudo journalctl -u opds-gen -f

# Ver logs das últimas 100 linhas
sudo journalctl -u opds-gen -n 100

# Ver logs de hoje
sudo journalctl -u opds-gen --since today

# Desabilitar inicialização automática
sudo systemctl disable opds-gen
```

#### Verificando se está funcionando

```bash
# Ver status
sudo systemctl status opds-gen

# Deve mostrar "active (running)" em verde

# Testar o servidor
curl http://localhost:8080/opds

# Ou em um navegador
firefox http://localhost:8080/opds
```

#### Exemplo de Output de Status

```
● opds-gen.service - OPDS Generator - Servidor de catálogo de livros para KOReader
     Loaded: loaded (/etc/systemd/system/opds-gen.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-01-02 04:30:15 -03; 2min ago
       Docs: https://github.com/YuriGomes4/opds-gen
   Main PID: 12345 (python3)
      Tasks: 3 (limit: 18985)
     Memory: 25.6M
        CPU: 450ms
     CGroup: /system.slice/opds-gen.service
             └─12345 /usr/bin/python3 /home/yuri/Documentos/GitHub/opds-gen/opds-gen.py...

Jan 02 04:30:15 servidor systemd[1]: Started OPDS Generator - Servidor de catálogo...
Jan 02 04:30:15 servidor opds-gen[12345]: ========================================
Jan 02 04:30:15 servidor opds-gen[12345]: OPDS Generator - Sistema de geração de...
Jan 02 04:30:16 servidor opds-gen[12345]: Escaneamento concluído! 1523 livros en...
Jan 02 04:30:16 servidor opds-gen[12345]: Servidor OPDS rodando em http://0.0.0....
```

#### Solução de Problemas do Serviço

##### Serviço não inicia

```bash
# Ver logs detalhados
sudo journalctl -u opds-gen -n 50 --no-pager

# Verificar sintaxe do arquivo de serviço
sudo systemd-analyze verify /etc/systemd/system/opds-gen.service

# Testar manualmente o comando
sudo -u yuri /usr/bin/python3 /caminho/completo/opds-gen.py -dir /media/HD/Media/Livros -port 8080
```

##### Permissões

Certifique-se de que o usuário do serviço tem permissões:

```bash
# Permissão para ler o script
chmod +x /home/yuri/Documentos/GitHub/opds-gen/opds-gen.py

# Permissão para ler o diretório de livros
ls -la /media/HD/Media/Livros
# O usuário 'yuri' deve ter permissão de leitura
```

##### Porta em uso

```bash
# Verificar se a porta está em uso
sudo netstat -tuln | grep 8080
# ou
sudo ss -tuln | grep 8080

# Se estiver em uso, escolha outra porta no arquivo de serviço
```

### Exemplo Completo de Configuração

Arquivo de serviço real de exemplo (`/etc/systemd/system/opds-gen.service`):

```ini
[Unit]
Description=OPDS Generator - Servidor de catálogo de livros para KOReader
Documentation=https://github.com/YuriGomes4/opds-gen
After=network.target

[Service]
Type=simple
User=yuri
Group=yuri
WorkingDirectory=/home/yuri/Documentos/GitHub/opds-gen
ExecStart=/usr/bin/python3 /home/yuri/Documentos/GitHub/opds-gen/opds-gen.py -dir /media/HD/Media/Livros -port 8080 -interval 300
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=opds-gen

[Install]
WantedBy=multi-user.target
```

Comandos de configuração:

```bash
# 1. Criar o arquivo de serviço
sudo nano /etc/systemd/system/opds-gen.service
# (Cole o conteúdo acima, ajustando os caminhos)

# 2. Recarregar systemd
sudo systemctl daemon-reload

# 3. Habilitar para iniciar no boot
sudo systemctl enable opds-gen

# 4. Iniciar o serviço
sudo systemctl start opds-gen

# 5. Verificar status
sudo systemctl status opds-gen

# 6. Ver logs em tempo real
sudo journalctl -u opds-gen -f
```

Pronto! Seu servidor OPDS agora está rodando como um serviço do sistema e iniciará automaticamente no boot! 🎉

## 🐛 Solução de Problemas

### ~~Links com 0.0.0.0 não funcionam~~ ✅ RESOLVIDO!

**Este problema foi corrigido!** O sistema agora gera URLs dinâmicas automaticamente baseadas no host da requisição. Não é mais necessário configurar um IP específico.

### O servidor não inicia

- Verifique se a porta não está em uso: `netstat -tuln | grep 8080`
- Tente usar outra porta: `./opds-gen.py -dir /caminho -port 9090`

### KOReader não consegue conectar

- Verifique se o servidor está rodando
- Confirme que está usando o IP correto da máquina
  - Linux/macOS: `ip addr` ou `ifconfig`
  - Windows: `ipconfig`
- Verifique se o firewall não está bloqueando a porta
- Teste acessar `http://SEU_IP:PORTA/opds` em um navegador

### Livros não aparecem no catálogo

- Verifique se os arquivos têm extensões suportadas
- Confirme que o diretório está correto
- Aguarde alguns segundos para a regeneração do catálogo

### Downloads falham

- **Solução**: Este problema foi corrigido com as URLs dinâmicas!
- Verifique se você pode acessar diretamente `http://SEU_IP:PORTA/books/caminho/livro.epub` em um navegador
- Se o link funciona no navegador mas não no KOReader, tente recarregar o catálogo no KOReader

## 📜 Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e distribuir.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novos recursos
- Enviar pull requests

## 👨‍💻 Autor

Desenvolvido para facilitar o acesso a bibliotecas digitais através do KOReader e outros leitores compatíveis com OPDS.

## 🔗 Links Úteis

- [OPDS Specification](https://specs.opds.io/)
- [KOReader](https://github.com/koreader/koreader)
- [KOReader OPDS Documentation](https://github.com/koreader/koreader/wiki/OPDS-support)

---

**Aproveite sua biblioteca digital! 📚**
