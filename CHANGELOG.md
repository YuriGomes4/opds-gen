# Changelog

## [1.2.0] - 2026-01-02

### Corrigido
- **Encoding de URLs**: Resolvido problema "Bad request syntax" do KOReader com nomes de arquivos contendo espaços, acentos e caracteres especiais
  - URLs agora são corretamente encodadas (ex: "Stephen King" → "Stephen%20King")
  - Servidor atualizado para protocolo HTTP/1.1
  - Adicionado tratamento robusto de erros com logs detalhados
  - Suporte completo a nomes de arquivos em UTF-8

### Melhorado
- **Geração Dinâmica de OPDS**: O feed agora é gerado em tempo real a cada requisição (não há mais arquivo OPDS estático)
- **Reescaneamento Inteligente**: Thread periódica agora apenas reescaneia o diretório de livros, não regera o OPDS completo
- **Performance**: Melhor performance ao evitar regeneração desnecessária de XML
- **Logs**: Adicionados logs detalhados para facilitar debugging

## [1.1.0] - 2026-01-02

### Corrigido
- **Links dinâmicos baseados em Host**: O sistema agora gera URLs personalizadas no feed OPDS baseadas no cabeçalho `Host` da requisição HTTP. Isso resolve o problema de links com `0.0.0.0` que não funcionavam em outros dispositivos.
  - O servidor detecta automaticamente o IP/hostname usado pelo cliente
  - Cada cliente recebe um feed OPDS personalizado com links funcionais
  - Downloads agora funcionam corretamente de qualquer dispositivo na rede

### Como funciona
- Quando um cliente acessa `http://192.168.1.100:8080/opds`, o servidor detecta o host `192.168.1.100:8080` da requisição
- O feed OPDS é gerado dinamicamente com links como `http://192.168.1.100:8080/books/...`
- Não é mais necessário configurar um IP específico - funciona automaticamente!

## [1.0.0] - 2026-01-02

### Adicionado
- Sistema completo de geração de feed OPDS para KOReader
- Suporte a múltiplos formatos de e-books (EPUB, PDF, MOBI, etc.)
- Servidor HTTP integrado
- Regeneração automática do catálogo a cada 5 minutos
- Detecção automática de metadados baseada na estrutura de diretórios
- Zero dependências externas
