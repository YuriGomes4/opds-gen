"""
Módulo para gerar feeds OPDS compatíveis com KOReader
"""

import os
import mimetypes
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import hashlib


class OPDSGenerator:
    """Gerador de feed OPDS para catálogos de livros."""
    
    # Extensões de arquivos suportadas
    SUPPORTED_EXTENSIONS = {
        '.epub', '.pdf', '.mobi', '.azw', '.azw3',
        '.fb2', '.djvu', '.cbz', '.cbr', '.txt'
    }
    
    # Namespaces OPDS
    NAMESPACES = {
        'xmlns': 'http://www.w3.org/2005/Atom',
        'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
        'xmlns:opds': 'http://opds-spec.org/2010/catalog',
    }
    
    def __init__(self, books_dir, host='0.0.0.0', port=8080):
        """
        Inicializa o gerador OPDS.
        
        Args:
            books_dir: Diretório contendo os livros
            host: Host do servidor
            port: Porta do servidor
        """
        self.books_dir = Path(books_dir)
        self.host = host
        self.port = port
        self.base_url = None  # Será definido dinamicamente
        self.opds_file = self.books_dir / '.opds_catalog.xml'
        self.books_cache = []
        
    def scan_books(self):
        """
        Escaneia o diretório de livros recursivamente.
        
        Returns:
            Lista de dicionários com informações dos livros
        """
        books = []
        
        print(f"Escaneando diretório: {self.books_dir}")
        
        for file_path in self.books_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # Pular o arquivo OPDS
                if file_path == self.opds_file:
                    continue
                
                # Obter informações do arquivo
                stat = file_path.stat()
                relative_path = file_path.relative_to(self.books_dir)
                
                # Extrair informações do nome do arquivo e caminho
                title = file_path.stem
                category = relative_path.parent.name if relative_path.parent != Path('.') else 'Sem Categoria'
                
                book_info = {
                    'title': title,
                    'author': self._extract_author(file_path),
                    'category': category,
                    'file_path': str(relative_path),
                    'file_size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat() + 'Z',
                    'extension': file_path.suffix.lower(),
                    'mime_type': self._get_mime_type(file_path),
                    'id': self._generate_id(str(relative_path)),
                }
                
                books.append(book_info)
        
        print(f"Encontrados {len(books)} livros")
        return books
    
    def _extract_author(self, file_path):
        """
        Tenta extrair o autor do caminho do arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Nome do autor ou "Desconhecido"
        """
        # Se o diretório pai for um autor (convenção comum)
        relative = file_path.relative_to(self.books_dir)
        
        # Verificar se há pelo menos 2 níveis (categoria/autor/livro.epub)
        if len(relative.parts) >= 2:
            # Assumir que o penúltimo diretório é o autor
            potential_author = relative.parts[-2]
            # Se não for a categoria raiz
            if potential_author != relative.parts[0]:
                return potential_author
        
        return "Autor Desconhecido"
    
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
    
    def _generate_id(self, path):
        """
        Gera um ID único para o livro baseado no caminho.
        
        Args:
            path: Caminho relativo do arquivo
            
        Returns:
            String com ID único
        """
        return hashlib.md5(path.encode()).hexdigest()
    
    def generate_opds_xml(self, books, base_url=None):
        """
        Gera o XML do feed OPDS.
        
        Args:
            books: Lista de dicionários com informações dos livros
            base_url: URL base para os links (ex: http://192.168.1.100:8080)
                     Se None, usa um placeholder
            
        Returns:
            String com XML formatado
        """
        # Se não foi fornecida uma URL base, usar placeholder
        if base_url is None:
            base_url = f"http://SERVER_IP:{self.port}"
        
        # Criar elemento raiz
        feed = Element('feed')
        for key, value in self.NAMESPACES.items():
            feed.set(key, value)
        
        # Metadados do feed
        SubElement(feed, 'id').text = 'opds-gen:root'
        SubElement(feed, 'title').text = 'Catálogo de Livros'
        SubElement(feed, 'updated').text = datetime.utcnow().isoformat() + 'Z'
        
        # Link para o próprio feed
        link_self = SubElement(feed, 'link')
        link_self.set('rel', 'self')
        link_self.set('type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
        link_self.set('href', f'{base_url}/opds')
        
        # Link de início
        link_start = SubElement(feed, 'link')
        link_start.set('rel', 'start')
        link_start.set('type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
        link_start.set('href', f'{base_url}/opds')
        
        # Adicionar cada livro como entry
        for book in sorted(books, key=lambda x: (x['category'], x['author'], x['title'])):
            entry = SubElement(feed, 'entry')
            
            # ID e título
            SubElement(entry, 'id').text = f"opds-gen:book:{book['id']}"
            SubElement(entry, 'title').text = book['title']
            SubElement(entry, 'updated').text = book['modified']
            
            # Autor
            author = SubElement(entry, 'author')
            SubElement(author, 'name').text = book['author']
            
            # Categoria
            category = SubElement(entry, 'category')
            category.set('term', book['category'])
            category.set('label', book['category'])
            
            # Sumário/Descrição
            summary = SubElement(entry, 'summary')
            summary.set('type', 'text')
            summary.text = f"{book['title']} por {book['author']} ({book['extension'].upper()})"
            
            # Link para download (aquisição)
            link_acquisition = SubElement(entry, 'link')
            link_acquisition.set('rel', 'http://opds-spec.org/acquisition')
            link_acquisition.set('type', book['mime_type'])
            link_acquisition.set('href', f"{base_url}/books/{book['file_path']}")
            
            # Adicionar tamanho do arquivo como atributo
            link_acquisition.set('length', str(book['file_size']))
        
        # Formatar XML de forma legível
        xml_str = tostring(feed, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
    
    def generate(self):
        """Gera o feed OPDS e salva em arquivo (versão estática para cache)."""
        # Escanear livros
        self.books_cache = self.scan_books()
        
        # Gerar XML com placeholder (apenas para referência)
        opds_xml = self.generate_opds_xml(self.books_cache)
        
        # Salvar arquivo
        with open(self.opds_file, 'w', encoding='utf-8') as f:
            f.write(opds_xml)
        
        print(f"Feed OPDS salvo em: {self.opds_file}")
        
        return self.opds_file
    
    def get_opds_content(self, base_url):
        """
        Retorna o conteúdo do feed OPDS com URLs personalizadas.
        
        Args:
            base_url: URL base para gerar os links (ex: http://192.168.1.100:8080)
        
        Returns:
            String com o conteúdo XML do feed personalizado
        """
        # Gerar OPDS dinâmico com a URL correta
        return self.generate_opds_xml(self.books_cache, base_url)
