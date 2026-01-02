"""
Servidor HTTP para servir o feed OPDS e os arquivos de livros
"""

import os
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class OPDSRequestHandler(SimpleHTTPRequestHandler):
    """Handler HTTP personalizado para servir OPDS e livros."""
    
    # Aumentar o tamanho máximo da linha de requisição para suportar URLs longas
    # e definir protocolo HTTP/1.1
    protocol_version = 'HTTP/1.1'
    
    def __init__(self, *args, books_dir=None, generator=None, **kwargs):
        """
        Inicializa o handler.
        
        Args:
            books_dir: Diretório contendo os livros
            generator: Instância do OPDSGenerator
        """
        self.books_dir = books_dir
        self.generator = generator
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override para logar mensagens de forma mais limpa."""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """Processa requisições GET."""
        try:
            # Parse URL - fazer decode completo
            parsed_path = urllib.parse.urlparse(self.path)
            
            # Decodificar o caminho (converte %20 para espaço, etc)
            path = urllib.parse.unquote(parsed_path.path, encoding='utf-8', errors='replace')
            
            # Log da requisição
            print(f"[GET] Caminho requisitado: {path}")
            
            # Rota para o feed OPDS
            if path == '/opds' or path == '/opds/':
                self.serve_opds()
            # Rota para livros
            elif path.startswith('/books/'):
                # Remove '/books/' e qualquer barra inicial extra
                relative_path = path[7:].lstrip('/')
                self.serve_book(relative_path)
            # Rota raiz - redirecionar para OPDS
            elif path == '/' or path == '':
                self.send_response(302)
                self.send_header('Location', '/opds')
                self.end_headers()
            else:
                self.send_error(404, "Recurso não encontrado")
        except Exception as e:
            print(f"[ERRO] Erro ao processar requisição: {e}")
            print(f"[ERRO] Caminho original: {self.path}")
            self.send_error(500, f"Erro ao processar requisição: {str(e)}")
    
    def serve_opds(self):
        """Serve o feed OPDS com URLs personalizadas baseadas no Host da requisição."""
        # Obter o Host do cabeçalho da requisição
        host_header = self.headers.get('Host')
        
        if host_header:
            # Usar o host da requisição (já inclui porta se fornecida)
            base_url = f"http://{host_header}"
        else:
            # Fallback: tentar detectar o IP do servidor
            # Pegar o IP da interface de rede que recebeu a conexão
            server_ip = self.request.getsockname()[0]
            base_url = f"http://{server_ip}:{self.generator.port}"
        
        # Gerar OPDS dinâmico com a URL correta
        opds_content = self.generator.get_opds_content(base_url)
        
        if opds_content:
            self.send_response(200)
            self.send_header('Content-Type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
            self.send_header('Content-Length', len(opds_content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(opds_content.encode('utf-8'))
        else:
            self.send_error(500, "Feed OPDS não disponível")
    
    def serve_book(self, relative_path):
        """
        Serve um arquivo de livro.
        
        Args:
            relative_path: Caminho relativo do livro
        """
        try:
            print(f"[BOOK] Servindo livro: {relative_path}")
            
            # Construir caminho completo
            # Normalizar o caminho para lidar com diferentes separadores
            relative_path = relative_path.replace('\\', '/')
            book_path = self.books_dir / relative_path
            
            print(f"[BOOK] Caminho completo: {book_path}")
            
            # Resolver o caminho (resolve links simbólicos e ..)
            book_path = book_path.resolve()
            books_dir_resolved = self.books_dir.resolve()
            
            print(f"[BOOK] Caminho resolvido: {book_path}")
            print(f"[BOOK] Diretório base: {books_dir_resolved}")
            
            # Verificação de segurança: garantir que o arquivo está dentro do diretório permitido
            if not str(book_path).startswith(str(books_dir_resolved)):
                print(f"[ERRO] Tentativa de acesso fora do diretório permitido")
                self.send_error(403, "Acesso negado")
                return
            
            if not book_path.exists():
                print(f"[ERRO] Arquivo não encontrado: {book_path}")
                self.send_error(404, "Livro não encontrado")
                return
            
            if not book_path.is_file():
                print(f"[ERRO] Não é um arquivo: {book_path}")
                self.send_error(400, "Recurso inválido")
                return
            
            # Determinar MIME type
            mime_type = self._get_mime_type(book_path)
            
            # Servir arquivo
            file_size = book_path.stat().st_size
            print(f"[BOOK] Enviando arquivo: {book_path.name} ({file_size} bytes, {mime_type})")
            
            with open(book_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            # Encoding do nome do arquivo para o cabeçalho
            filename_encoded = urllib.parse.quote(book_path.name.encode('utf-8'))
            self.send_header('Content-Disposition', f'attachment; filename*=UTF-8\'\'{filename_encoded}')
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            self.wfile.write(content)
            
            print(f"[BOOK] Arquivo enviado com sucesso!")
            
        except Exception as e:
            print(f"[ERRO] Erro ao servir livro '{relative_path}': {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, "Erro ao servir arquivo")
    
    def _get_mime_type(self, file_path):
        """
        Retorna o MIME type do arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            String com o MIME type
        """
        mime_map = {
            '.epub': 'application/epub+zip',
            '.pdf': 'application/pdf',
            '.mobi': 'application/x-mobipocket-ebook',
            '.azw': 'application/vnd.amazon.ebook',
            '.azw3': 'application/vnd.amazon.ebook',
            '.fb2': 'text/fb2+xml',
            '.djvu': 'image/vnd.djvu',
            '.cbz': 'application/x-cbz',
            '.cbr': 'application/x-cbr',
            '.txt': 'text/plain',
        }
        
        ext = file_path.suffix.lower()
        return mime_map.get(ext, 'application/octet-stream')


class OPDSServer:
    """Servidor HTTP para OPDS."""
    
    def __init__(self, books_dir, generator, host='0.0.0.0', port=8080):
        """
        Inicializa o servidor OPDS.
        
        Args:
            books_dir: Diretório contendo os livros
            generator: Instância do OPDSGenerator
            host: Host para o servidor
            port: Porta para o servidor
        """
        self.books_dir = Path(books_dir)
        self.generator = generator
        self.host = host
        self.port = port
        
        # Criar handler com contexto
        def handler(*args, **kwargs):
            return OPDSRequestHandler(
                *args,
                books_dir=self.books_dir,
                generator=self.generator,
                **kwargs
            )
        
        self.handler = handler
        self.httpd = None
    
    def start(self):
        """Inicia o servidor HTTP."""
        self.httpd = HTTPServer((self.host, self.port), self.handler)
        
        print(f"\nServidor OPDS rodando em http://{self.host}:{self.port}")
        print(f"Feed OPDS disponível em: http://{self.host}:{self.port}/opds")
        print("\nNo KOReader:")
        print(f"  1. Vá em 'Buscar' > 'Catálogo OPDS'")
        print(f"  2. Adicione novo catálogo com URL: http://[SEU_IP]:{self.port}/opds")
        print("\nPressione Ctrl+C para encerrar o servidor\n")
        
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if self.httpd:
                self.httpd.shutdown()
                self.httpd.server_close()
    
    def stop(self):
        """Para o servidor HTTP."""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
