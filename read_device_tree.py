#!/usr/bin/python

import sys
import struct
import urllib

keep_compatibles = ["uart-1,samsung\0", "N66AP\0iPhone8,2\0AppleARM\0", "wdt,s8000\0wdt,s5l8960x\0", "arm-io,s8000\0"]
remove_names = ["backlight\0"]
remove_device_types = ["backlight\0"]

added_props = 0
node_index = 0
out_tree = ""

def add_prop(name, length, data):
    global out_tree
    global added_props
    #align for 4 bytes start of the next property
    if 0 != (len(out_tree) % 4):
        out_tree += "\0" * (4 - (len(out_tree) % 4))

    out_tree += name[:32]
    out_tree += "\0" * (32 - len(name[:32]))

    out_tree += struct.pack("<I", length)

    out_tree += data[:length]

    added_props += 1

    print("new added prop: " + name)
    print("prop len: " + str(length))
    print "data: ",
    for i in xrange(length):
        print hex(ord(data[i])),
    print("")
    print "data string: " + data.rstrip('\0')
    print("")

def read_prop(node_bytes, index):
    global out_tree
    pre_index = index
    #align for 4 bytes start of the next property
    if 0 != (len(out_tree) % 4):
        out_tree += "\0" * (4 - (len(out_tree) % 4))

    if 0 != (index % 4):
        index += 4 - (index % 4)

    name = node_bytes[index : index + 32].rstrip('\0')

    #remove this prop as it is responsible for the waited for event in PE that never happens
    if name == "secure-root-prefix":
        print("######################### removing prop name for: " + \
              "secure-root-prefix")
        name = "~" * 32
        out_tree += "~" * 32
    else:
        out_tree += node_bytes[index : index + 32]

    index += 32

    length = struct.unpack("<I", node_bytes[index : index + 4])
    #it seems sometimes the upper bit is set for the prop len for some reason?
    length = length[0] & 0x7fffffff
    index += 4

    #must zero the DT_PROP_FLAG_PLACEHOLDER flag in final prop length that the kernel reads (instead of iboot doing it)
    out_tree += struct.pack("<I", length)

    data = ""
    orig_data = node_bytes[index : index + length]

    #panic if timebase-frequency is 0 (doing this instead of iboot)
    if name == "timebase-frequency":
        data = struct.pack("<Q", 24000000)
    elif name == "fixed-frequency":
        data = struct.pack("<Q", 24000000)
    elif name =="random-seed":
        for i in xrange(length / 4):
            data += struct.pack("<I", 0xdead000d)
    elif name == "compatible" and not orig_data in keep_compatibles:
        print("######################### removing compatible for: " + \
              urllib.quote_plus(data))
        data += ("~" * (length - 1)) + "\0"
    elif name == "name" and orig_data in remove_names:
        print("######################### removing name for: " + \
              urllib.quote_plus(data))
        data = "~" + orig_data[1:]
    elif name == "device_type" and orig_data in remove_device_types:
        print("######################### removing device type for: " + \
              urllib.quote_plus(data))
        data = "~" + orig_data[1:]
    else:
        data = "".join(orig_data)

    out_tree += data

    index += length
    print("new prop: " + urllib.quote_plus(name))
    print("prop len: " + str(length))
    print("data len: " + str(len(data)))
    print "data: ",
    for i in xrange(length):
        print hex(ord(data[i])),
    print("")
    print "data string: " + urllib.quote_plus(data)
    print "orig_data string: " + urllib.quote_plus(orig_data)
    print("")

    #these are needed by the image4 parser module
    if name == "name" and data.rstrip('\0') == "chosen":
        add_prop("security-domain", 4, "\0\0\0\0")
        add_prop("chip-epoch", 4, "\0\0\0\0")
        add_prop("debug-enabled", 4, "\255\255\255\255")

    return index

def read_node(node_bytes, index, level):
    global node_index
    global out_tree
    global added_props

    node_index += 1

    #align for 4 bytes start of the next node
    if 0 != (index % 4):
        index += 4 - (index % 4)

    if 0 != (len(out_tree) % 4):
        out_tree += "\0" * (4 - (len(out_tree) % 4))

    pre_index = index

    prop_c = struct.unpack("<I", node_bytes[index : index + 4])
    index += 4
    child_c = struct.unpack("<I", node_bytes[index : index + 4])
    index += 4

    print("")
    print("--------------------------------")
    print("new node: " + str(node_index))
    print("node level: " + str(level))
    print("prop count: " + str(prop_c))
    print("child count: " + str(child_c))
    print("--------------------------------")
    print("")

    prop_c_out_index = len(out_tree)
    out_tree += node_bytes[pre_index : index]

    for i in xrange(prop_c[0]):
        index = read_prop(node_bytes, index)

    if added_props > 0:
        new_prop_c_str = struct.pack("<I", prop_c[0] + added_props)
        out_tree = out_tree[:prop_c_out_index] + new_prop_c_str + \
                   out_tree[prop_c_out_index + 4:]
        added_props = 0


    for i in xrange(child_c[0]):
        index = read_node(node_bytes, index, level + 1)

    return index

if __name__ == "__main__":
    dev_tree_bytes = open(sys.argv[1], "rb").read()
    read_node(dev_tree_bytes, 0, 0)
    open(sys.argv[2], "wb").write(out_tree)

