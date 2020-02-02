import traceback
import logging
import gdb
from xnu.constants import NULL_PTR_STR

LOGGER = logging.getLogger("xnu")


def get_8_byte_at(addr):
    return execute_get_val(addr, 'g')


def get_4_byte_at(addr):
    return execute_get_val(addr, 'w')


def get_string_at(value):
    return execute_get_string(value)


def execute_get_string(value):
    try:
        command = f"x /1s {str(value)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        res = " ".join(res.split()[1:])
        LOGGER.debug("Got a result %s ", str(res))
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())


def execute_get_val(val, size):
    try:
        check_arguments(size)
        command = f"x /1x{size} {hex(val)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        res = int(res.split()[1], 0)
        LOGGER.debug("Got a result %s ", str(res))
        return res
    except Exception:
        raise gdb.GdbError(f"{traceback.format_exc()}")


def print_val(var):
    try:
        command = f"print /1x {str(var)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        LOGGER.debug("Got a result %s ", str(res))
        res = int(res.split()[2], 0)
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())


def check_arguments(size):
    return size in ['b', 'h', 'w', 'g']


def print_ptr_as_string(addr):
    return NULL_PTR_STR if not addr else f"0x{addr:016x}"


def gdb_continue():
    gdb.execute("continue")


def conf_curr_thread_watchpoint():
    bp = gdb.Breakpoint('$TPIDR_EL1', gdb.BP_WATCHPOINT, internal=True)
    bp.enabled = True
    bp.silent = True
    return bp


def delete_bp(bp):
    bp.delete()


def enable_all_bp():
    gdb.execute("enable br")


def disable_all_bp():
    gdb.execute("disable br")
