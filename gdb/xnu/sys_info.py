import json
import os
import xnu.constants as const
import xnu.utils as utils
import gdb


def get_current_task_ptr():
    try:
        address = utils.print_val(const.CURRENT_THREAD)
        return utils.get_8_byte_at(address + const.ThreadOffsets.TASK.value)
    except Exception:
        raise gdb.GdbError(f"Error occured, maybe in user land?")


def get_current_thread_ptr():
    try:
        return utils.print_val(const.CURRENT_THREAD)
    except Exception:
        raise gdb.GdbError(f"Error occured, maybe in user land?")

# TODO put into thread class
def is_user_thread(thread):
    return True if thread.ucontext_data != const.NULL_PTR else False


def is_valid_ptr(ptr):
    try:
        utils.get_8_byte_at(ptr)
        return True
    except:
        raise gdb.GdbError(f"Wrong pointer! {hex(ptr)}")


class Symbols:
    def __init__(self):
        self.sym_dict = {}
        self.found_fuct_name_dict = {}
        self.sym_dir_path = os.path.dirname(__file__)
        self.load_symbols()

    def load_symbols(self):
        with open(os.path.join(self.sym_dir_path, "SymbolsNew"), "r") as sym_file:
            self.sym_dict = json.load(sym_file)
        with open(os.path.join(self.sym_dir_path, "KnownLables"), "r") as known_func_name_file:
            self.found_fuct_name_dict = json.load(known_func_name_file)

    def get_symbol_internal(self, addrr):
        if addrr in self.sym_dict:
            if 'FUN_' not in self.sym_dict[addrr]:
                return self.sym_dict[addrr]
        if addrr in self.found_fuct_name_dict:
            return self.found_fuct_name_dict[addrr]
        return addrr


SYMBOLS = Symbols()


def get_symbol(addrr):
    return SYMBOLS.get_symbol_internal(addrr)
