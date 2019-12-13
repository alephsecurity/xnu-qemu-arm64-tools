import xnu.utils as utils
import gdb


class StructZone(object):
    zone_globals_16B92 = {
        "max_zones": 0xfffffff00763df48,
        "zone_array": 0xfffffff007624ef0,
        "zone_struct_size": 0x140
    }
    # TODO: support more versions
    globs = zone_globals_16B92

    struct_offsets_16B92 = {
        "zone_name": 0x118,
        "index": 0x114,
        "flags": 0x110,
        "flags_valid_shift": 26,
        "flags_valid_mask": 1,
        "sum_count": 0x108,
        "page_count": 0x100,
        "alloc_size": 0xf8,
        "elem_size": 0xf0,
        "max_size": 0xe8,
        "cur_size": 0xe0
    }

    def __init__(self, addr):
        # TODO: support more versions
        self.offsets = StructZone.struct_offsets_16B92
        self.globals = StructZone.zone_globals_16B92
        self.addr = addr
        self.cur_size = utils.get_8_byte_at(addr + self.offsets["cur_size"])
        self.max_size = utils.get_8_byte_at(addr + self.offsets["max_size"])
        self.elem_size = utils.get_8_byte_at(addr + self.offsets["elem_size"])
        self.alloc_size = utils.get_8_byte_at(addr + self.offsets["alloc_size"])
        self.page_count = utils.get_8_byte_at(addr + self.offsets["page_count"])
        self.sum_count = utils.get_8_byte_at(addr + self.offsets["sum_count"])
        self.flags = utils.get_4_byte_at(addr + self.offsets["flags"])
        self.index = utils.get_4_byte_at(addr + self.offsets["index"])
        name_ptr = utils.get_8_byte_at(addr + self.offsets["zone_name"])
        self.zone_name = utils.get_string_at(name_ptr)

    def is_valid(self):
        shift = self.offsets["flags_valid_shift"]
        mask = self.offsets["flags_valid_mask"]
        valid = (self.flags >> shift) & mask
        return (0 != valid)

    @classmethod
    def get_max_zones(cls):
        return cls.globs["max_zones"]

    @classmethod
    def get_zone_array(cls):
        return cls.globs["zone_array"]

    @classmethod
    def get_struct_size(cls):
        return cls.globs["zone_struct_size"]


class PrintZoneInformationCommand(gdb.Command):
    def __init__(self):
        super(PrintZoneInformationCommand,
              self).__init__("xnu-zones", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        self.print_zones()

    def print_zones(self):
        zone_arr_addr = StructZone.get_zone_array()
        max_zones_addr = StructZone.get_max_zones()
        max_zones = utils.get_4_byte_at(max_zones_addr)
        struct_size = StructZone.get_struct_size()
        out = "Printing zones info:\n"
        out += f"zone_arr_addr: 0x{zone_arr_addr:016x}\n"
        out += f"max_zones: {max_zones}\n"
        gdb.write(out)
        for i in range(max_zones):
            zone_addr = zone_arr_addr + (struct_size * i)
            zone = StructZone(zone_addr)
            if (not zone.is_valid()):
                continue
            out = f"Valid zone at 0x{zone_addr:016x} at index {i}\n"
            out += f"        zone_name: {zone.zone_name}\n"
            out += f"        elem_size: {zone.elem_size}\n"
            out += f"        index: {zone.index}\n"
            out += f"        flags: 0x{zone.flags:08x}\n"
            out += f"        sum_count: {zone.sum_count}\n"
            out += f"        page_count: {zone.page_count}\n"
            out += f"        alloc_size: 0x{zone.alloc_size:016x}\n"
            out += f"        max_size: 0x{zone.max_size:016x}\n"
            out += f"        cur_size: 0x{zone.cur_size:016x}\n"
            gdb.write(out)


PrintZoneInformationCommand()
