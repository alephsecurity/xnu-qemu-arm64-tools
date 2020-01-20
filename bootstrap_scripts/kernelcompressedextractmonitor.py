#!/usr/bin/python2

import sys
import struct

def decode(data):
    if data[0:8] != "complzss":
        print "error: unsupported format: " + str(data[0:7])
        return ""
    compressed_size = struct.unpack(">I", data[16:20])

    end_of_compressed_data = compressed_size[0] + 0x180 #size of compression header

    return data[end_of_compressed_data:]

if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    out_data = decode(data)
    open(sys.argv[2], "wb").write(out_data)
