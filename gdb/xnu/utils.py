import gdb
import traceback
from xnu.constants import NULL_PTR_STR

import xnu.log as log

logger = None

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
        logger.debug(f"Going to excute {command}")
        res = gdb.execute(command,to_string=True)
        res = " ".join(res.split()[1:])
        logger.debug(f"Got a result {str(res)}")
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())

def executeGetVal(val, size):
    try:
        checkArguments(size)
        command = f"x /1x{size} {hex(val)}"
        logger.debug(f"Going to excute {command} ")
        res = gdb.execute(command,to_string=True)
        res = int(res.split()[1], 0)
        logger.debug(f"Got a result {str(res)}")
        return res
    except Exception:
        raise gdb.GdbError(f"{traceback.format_exc()}")

def printVal(var):
    try:
        command = f"print /1x {str(var)}"
        logger.debug(f"Going to excute {command}")
        res = gdb.execute(command,to_string=True)
        logger.debug(f"Got a result {str(res)}")
        res = int(res.split()[2], 0)
        return res
    except Exception:
        raise gdb.GdbError(traceback.format_exc())

def checkArguments(size):
    return size in ['b','h','w','g']

def setupLoger():
    global logger 
    if logger == None:
        logger = log.setup_logger('xnu')

def getLogger():
    global logger 
    if logger != None:
        return logger
    else:
        gdb.Error("NO LOGGER")

setupLoger()

def printInfo(val):
    attrs = vars(val)
    gdb.write('\n'.join("%s: %s" % item for item in attrs.items()))

def printPtrAsString(addr):
    return NULL_PTR_STR if not addr else hex(addr) 
