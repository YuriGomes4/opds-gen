# OPDS Generator

Sistema completo de geração de feed OPDS para KOReader com servidor HTTP integrado.

## 📚 Sobre

O OPDS Generator é uma ferramenta Python que escaneia um diretório de livros digitais e gera automaticamente um feed OPDS (Open Publication Distribution System) compatível com o KOReader e outros leitores de e-books. O sistema inclui um servidor HTTP para servir tanto o catálogo OPDS quanto os arquivos dos livros.

### Características

- ✅ Geração automática de feed OPDS compatível com KOReader
- ✅ Suporte a múltiplos formatos: EPUB, PDF, MOBI, AZW, AZW3, FB2, DJVU, CBZ, CBR, TXT
- ✅ Regeneração automática do catálogo a cada 5 minutos (configurável)
- ✅ Servidor HTTP integrado para servir o feed e os livros
- ✅ Organização automática por categorias e autores
- ✅ Detecção automática de metadados baseada na estrutura de diretórios
- ✅ Zero dependências externas (apenas Python padrão)

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
├── opds-gen.py          # Script principal
├── opds_generator.py    # Módulo de geração de OPDS
├── opds_server.py       # Servidor HTTP
├── requirements.txt     # Dependências (nenhuma!)
└── README.md           # Este arquivo
```

## 🔧 Como Funciona

1. **Escaneamento**: O sistema escaneia recursivamente o diretório de livros
2. **Geração**: Cria um feed OPDS em formato XML com todos os livros encontrados
3. **Servidor**: Inicia um servidor HTTP que serve:
   - `/opds` - O feed OPDS atualizado
   - `/books/*` - Os arquivos dos livros
4. **Regeneração**: A cada N segundos (padrão: 300), o catálogo é regerado automaticamente

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

### Usando systemd (Linux)

Crie um arquivo `/etc/systemd/system/opds-gen.service`:

```ini
[Unit]
Description=OPDS Generator Service
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/opds-gen
ExecStart=/usr/bin/python3 /caminho/para/opds-gen/opds-gen.py -dir /media/HD/Media/Livros -port 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable opds-gen
sudo systemctl start opds-gen
```

## 🐛 Solução de Problemas

### O servidor não inicia

- Verifique se a porta não está em uso: `netstat -tuln | grep 8080`
- Tente usar outra porta: `./opds-gen.py -dir /caminho -port 9090`

### KOReader não consegue conectar

- Verifique se o servidor está rodando
- Confirme que está usando o IP correto da máquina
- Verifique se o firewall não está bloqueando a porta
- Teste acessar `http://SEU_IP:PORTA/opds` em um navegador

### Livros não aparecem no catálogo

- Verifique se os arquivos têm extensões suportadas
- Confirme que o diretório está correto
- Aguarde alguns segundos para a regeneração do catálogo

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
