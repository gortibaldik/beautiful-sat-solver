from argparse import ArgumentParser

def add_parser_debug_levels(parser: ArgumentParser):
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--warning', action='store_true')