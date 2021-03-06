# -*- coding: utf-8 -*-

import argparse
from csv_parser import ParsersRunner

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='CSV filter')
        parser.add_argument('-p', '--path', type=str, metavar='', help='directory path')
        parser.add_argument('-f', '--file', type=int, metavar='', help='files in the one thread')
        args = parser.parse_args()
        ParsersRunner(src=args.path, numbers_thread=args.file).run()
    except FileNotFoundError as exc:
        print(f"Error: {exc} type {(type(exc))}")
