import traceback
import  logging
import gdb
from xnu.constants import NULL_PTR_STR

LOGGER = logging.getLogger("xnu")

def getPointerAt(addr):
    return executeGetVal(addr, 'g')


def getLongAt(addr):
    return executeGetVal(addr, 'g')


def getIntAt(addr):
    return executeGetVal(addr, 'w')


def printValueOf(value):
    return printVal(value)


def getStringAt(value):
    return executeGetString(value)

def executeGetString(value):
    try:
        command = f"x /1s {str(value)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        res = " ".join(res.split()[1:])
        LOGGER.debug("Got a result %s ", str(res))
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())


def executeGetVal(val, size):
    try:
        checkArguments(size)
        command = f"x /1x{size} {hex(val)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        res = int(res.split()[1], 0)
        LOGGER.debug("Got a result %s ", str(res))
        return res
    except Exception:
        raise gdb.GdbError(f"{traceback.format_exc()}")


def printVal(var):
    try:
        command = f"print /1x {str(var)}"
        LOGGER.debug("Going to excute %s ", command)
        res = gdb.execute(command, to_string=True)
        LOGGER.debug("Got a result %s ", str(res))
        res = int(res.split()[2], 0)
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())


def checkArguments(size):
    return size in ['b', 'h', 'w', 'g']


def printInfo(val):
    attrs = vars(val)
    gdb.write('\n'.join("%s: %s" % item for item in attrs.items()))


def printPtrAsString(addr):
    return NULL_PTR_STR if not addr else hex(addr)
