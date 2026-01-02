#!/usr/bin/env python3
"""
OPDS Generator - Sistema de geração de feed OPDS para KOReader
"""

import argparse
import os
import sys
import threading
import time
from pathlib import Path

from opds_generator import OPDSGenerator
from opds_server import OPDSServer


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Gera feed OPDS e serve via HTTP para KOReader'
    )
    parser.add_argument(
        '-dir',
        '--directory',
        required=True,
        help='Diretório contendo os livros'
    )
    parser.add_argument(
        '-port',
        '--port',
        type=int,
        default=8080,
        help='Porta para o servidor HTTP (padrão: 8080)'
    )
    parser.add_argument(
        '-interval',
        '--interval',
        type=int,
        default=300,
        help='Intervalo de reescaneamento em segundos (padrão: 300 = 5 minutos)'
    )
    parser.add_argument(
        '-host',
        '--host',
        default='0.0.0.0',
        help='Host para o servidor HTTP (padrão: 0.0.0.0)'
    )
    
    return parser.parse_args()


def rescan_books_periodically(generator, interval):
    """
    Thread que reescaneia o diretório de livros periodicamente.
    
    O OPDS é gerado dinamicamente a cada requisição, mas precisamos
    reescanear os livros para detectar novos arquivos ou remoções.
    
    Args:
        generator: Instância do OPDSGenerator
        interval: Intervalo em segundos entre escaneamentos
    """
    while True:
        time.sleep(interval)
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Reescaneando diretório de livros...")
        try:
            generator.generate()
            print(f"Escaneamento concluído! {len(generator.books_cache)} livros encontrados.")
        except Exception as e:
            print(f"Erro ao escanear livros: {e}")


def main():
    """Função principal."""
    args = parse_arguments()
    
    # Validar diretório
    books_dir = Path(args.directory)
    if not books_dir.exists():
        print(f"Erro: Diretório '{args.directory}' não existe!", file=sys.stderr)
        sys.exit(1)
    
    if not books_dir.is_dir():
        print(f"Erro: '{args.directory}' não é um diretório!", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("OPDS Generator - Sistema de geração de feed OPDS")
    print("=" * 60)
    print(f"Diretório de livros: {books_dir.absolute()}")
    print(f"Servidor HTTP: http://{args.host}:{args.port}")
    print(f"Intervalo de reescaneamento: {args.interval} segundos")
    print("=" * 60)
    
    # Criar gerador OPDS
    generator = OPDSGenerator(books_dir, args.host, args.port)
    
    # Gerar OPDS inicial
    print("\nEscaneando livros pela primeira vez...")
    try:
        generator.generate()
        print(f"Escaneamento concluído! {len(generator.books_cache)} livros encontrados.")
    except Exception as e:
        print(f"Erro ao escanear livros: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Iniciar thread de reescaneamento periódico
    rescan_thread = threading.Thread(
        target=rescan_books_periodically,
        args=(generator, args.interval),
        daemon=True
    )
    rescan_thread.start()
    print(f"\nThread de reescaneamento iniciada (intervalo: {args.interval}s)")
    print("O feed OPDS é gerado dinamicamente a cada requisição com URLs personalizadas.")
    
    # Iniciar servidor HTTP
    print(f"\nIniciando servidor HTTP em {args.host}:{args.port}...")
    server = OPDSServer(books_dir, generator, args.host, args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\nEncerrando servidor...")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro ao iniciar servidor: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
