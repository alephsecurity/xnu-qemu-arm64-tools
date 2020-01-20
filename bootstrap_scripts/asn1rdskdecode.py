#!/usr/bin/python2

import sys
from pyasn1.codec.der.decoder import decode as der_decoder

def decode(data):
    try:
        decoded = der_decoder(data)
    except Exception as e:
        print "can't asn1 decode the file given: " + str(e)
    try:
        if "IM4P" != str(decoded[0][0]):
            print "failed: unexpected element: " + str(decoded[0][0])
            return ""
        if "rdsk" != str(decoded[0][1]):
            print "failed: unexpected element: " + str(decoded[0][1])
            return ""
        return str(decoded[0][3])
    except Exception as e:
        print "unexpected exception: " + str(e)

if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    out_data = decode(data)
    open(sys.argv[2], "wb").write(out_data)
