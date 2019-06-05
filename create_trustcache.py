#!/usr/bin/python

import sys
import struct
import urllib

def create_tc(hashes):
    tc = ""

    #number of trustcaches in the trust cache buffer
    tc += struct.pack("<I", 1)

    #offset within the buffer for the first trust cache
    tc += struct.pack("<I", 8)

    #write the header
    #version
    tc += struct.pack("<I", 1)

    #unknown header properties
    tc += struct.pack("<I", 0)
    tc += struct.pack("<I", 0)
    tc += struct.pack("<I", 0)
    tc += struct.pack("<I", 0)

    #number of hashes in the trust cache
    tc += struct.pack("<I", len(hashes))

    for hash_txt in hashes:
        assert(len(hash_txt) == 40)

        #write the hash itself
        for i in xrange(5):
            four_bytes = hash_txt[i * 8 : (i + 1) * 8]
            number = int(four_bytes, 16)
            tc += struct.pack(">I", number)

        #hash type
        tc += struct.pack("B", 0)
        #hash flags
        tc += struct.pack("B", 0)
    return tc

if __name__ == "__main__":
    hashes_txt = open(sys.argv[1], "rb").read()
    hashes = hashes_txt.splitlines()
    hashes = [hash.strip() for hash in hashes]
    #the kernel does a binary search for the hash so they must be sorted
    hashes = sorted(hashes)
    tc = create_tc(hashes)
    open(sys.argv[2], "wb").write(tc)

