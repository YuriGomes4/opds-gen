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
        help='Intervalo de regeneração em segundos (padrão: 300 = 5 minutos)'
    )
    parser.add_argument(
        '-host',
        '--host',
        default='0.0.0.0',
        help='Host para o servidor HTTP (padrão: 0.0.0.0)'
    )
    
    return parser.parse_args()


def regenerate_opds_periodically(generator, interval):
    """
    Thread que regenera o OPDS periodicamente.
    
    Args:
        generator: Instância do OPDSGenerator
        interval: Intervalo em segundos entre regenerações
    """
    while True:
        time.sleep(interval)
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Regenerando OPDS...")
        try:
            generator.generate()
            print("OPDS regenerado com sucesso!")
        except Exception as e:
            print(f"Erro ao regenerar OPDS: {e}")


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
    print(f"Intervalo de regeneração: {args.interval} segundos")
    print("=" * 60)
    
    # Criar gerador OPDS
    generator = OPDSGenerator(books_dir, args.host, args.port)
    
    # Gerar OPDS inicial
    print("\nGerando OPDS inicial...")
    try:
        generator.generate()
        print("OPDS gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar OPDS: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Iniciar thread de regeneração periódica
    regeneration_thread = threading.Thread(
        target=regenerate_opds_periodically,
        args=(generator, args.interval),
        daemon=True
    )
    regeneration_thread.start()
    print(f"\nThread de regeneração iniciada (intervalo: {args.interval}s)")
    
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
