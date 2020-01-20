#!/usr/bin/env python3

import csv
import sys

def csv2ld(in_file, out_file):
    reader = csv.reader(open(in_file))
    writer = open(out_file, 'wt')

    fields = next(reader)

    for values in reader:
        name = values[fields.index('Name')]
        location = values[fields.index('Location')]
        symtype = values[fields.index('Symbol Type')]
        namespace = values[fields.index('Namespace')]

        if symtype != 'Function' or namespace != 'Global':
            continue

        if name.startswith('_'):
            name = name[1:]

        print(f"PROVIDE ({name} = 0x{location});", file=writer)

def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python3 getsymbols.py <exported-kernel-symbols> [kernel-symbols-ld-provider]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) == 3 else "kernel.ld"

    csv2ld(in_file, out_file)

if __name__ == "__main__":
    main()