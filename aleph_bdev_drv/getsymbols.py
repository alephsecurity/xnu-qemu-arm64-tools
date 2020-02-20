#!/usr/bin/env python3

import csv
import sys

def nm2ld(in_file, out_file):
    symbols = open(in_file).read()
    writer = open(out_file, 'wt')

    for symbol in symbols.splitlines():
        name = symbol.split(" ")[2]
        location = symbol.split(" ")[0]

        if name.startswith('_'):
            name = name[1:]

        print(f"PROVIDE ({name} = 0x{location});", file=writer)

def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python3 getsymbols.py <exported-kernel-symbols> [kernel-symbols-ld-provider]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) == 3 else "kernel.ld"

    nm2ld(in_file, out_file)

if __name__ == "__main__":
    main()
