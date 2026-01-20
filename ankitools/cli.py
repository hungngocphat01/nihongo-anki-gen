import argparse
import sys
from ankitools.commands import gencards

def main():
    parser = argparse.ArgumentParser(
        prog='ankitools',
        description='Anki productivity tools'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Gencards subcommand
    gencards_parser = subparsers.add_parser('gencards', help='Generate Anki cards from wordlist')
    gencards.setup_parser(gencards_parser)
    
    args = parser.parse_args()
    
    if args.command == 'gencards':
        gencards.run(args)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
