from xnu.constants import CURRENT_THREAD, NULL_PTR, ThreadOffsets
from xnu.utils import printValueOf,getPointerAt
import gdb 
import json
import os

sym_dict = {}
foundFuctName_dict = {}
SYMDIRPATH = os.path.dirname(__file__)

def getCurrentTaskPtr():
    try:
        address = printValueOf(CURRENT_THREAD)
        return getPointerAt(address + ThreadOffsets.TASK.value)
    except Exception:
        raise gdb.GdbError(f"Error occured, maybe in user land?")

def getCurrentThreadPtr():
    try:
        return printValueOf(CURRENT_THREAD)
    except Exception:
        raise gdb.GdbError(f"Error occured, maybe in user land?")

#TODO put into thread class
def isUserThread(thread):
    return True if thread.uContextData != NULL_PTR else False

def isValidPtr(ptr):
    try:
        getPointerAt(ptr)
        return True
    except:
        raise gdb.GdbError(f"Wrong pointer! {hex(ptr)}")


def loadSymbols():
    global sym_dict
    global foundFuctName_dict
    with open(os.path.join(SYMDIRPATH,"SymbolsNew"),"r") as sym_file:
        sym_dict = json.load(sym_file)
    with open(os.path.join(SYMDIRPATH,"KnownLables"),"r") as oundFuctName_file:
        foundFuctName_dict = json.load(oundFuctName_file)

    # gdb.write("Symbols loaded\n")

loadSymbols()

def getSymbol(addrr):
    if addrr in sym_dict:
        if 'FUN_' not in sym_dict[addrr]:
            return sym_dict[addrr]
    if addrr in foundFuctName_dict:
        return foundFuctName_dict[addrr]
    return addrr