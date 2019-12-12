from enum import Enum

GLOBAL_THREADS_PTR = 0xfffffff00760f9e0
GLOBAL_TASKS_PTR = 0xfffffff00760f9c0
NULL_PTR = 0x0000000000000000
NULL_PTR_STR = "0x0000000000000000"
CURRENT_THREAD = "$TPIDR_EL1"

IE_BITS_TYPE_MASK = 0x001f0000

class NextPcHelpOffsets(Enum):
    NEXT_IN_THREAD_RUN = 0xfffffff0070e7d0c
    NEXT_IN_THREAD_BLOCK = 0xfffffff0070e3554
    EXEPTION_RETURN_PTR = 0xfffffff0070a1800
    SP_OFFSET_FROM_KRN_STACK = 0x100
    THREAD_INVOKE_FRAME_SIZE = 0x90
    X21_IN_THREAD_INVOKE_FRAME = 0x28
    STORED_LR_IN_THREAD_INVOKE_FRAME = 0x88


class ThrdItrType(Enum):
    GLOBAL = 0
    TASK = 1

class ThreadOffsets(Enum):
    CONTINUATION = 0x80
    CURRENT_STATE = 0xa0
    THREAD_ID = 0x3e0
    GLOBAL_THREADS = 0x348
    TASK_THREADS = 0x358
    TASK = 0x368
    CONTEXT_USER_DATA_PTR = 0x430
    KSTACK_PTR = 0x448
    VOUCHER_PTR = 0x510
    VOUCHER_NAME = 0x50C

class TaskOffsets(Enum):
    TASK_NEXT = 0x28
    THREAD_LST_FROM_TASK = 0x40
    ITK_SELF = 0xD8
    ITK_NSELF = 0xE0
    ITK_SSELF = 0xE8
    BSD_INFO = 0x358
    IPC_SPACE = 0x300

class BSDInfoOffsets(Enum):
    PID_IN_BSD_INFO = 0x60
    NAME_INBSD_INFO = 0x261

class IPCSpaceOffsets(Enum):
    IS_TABLE_SIZE = 0x14
    IS_TABLE_FREE = 0x18
    IS_TABLE = 0x20
    IS_LOW_MOD = 0x38
    IS_HIGH_MOD = 0x3C

class IPCEntryOffsets(Enum):
    IE_BITS = 0x08
    IE_INDEX = 0x0C
    INDEX = 0x10

class IPCObjectOffsets(Enum):
    IO_REFS = 0x04
    IO_LOCK_DATA = 0x08
    IP_MSG = 0x24

class IPCPortOffsets(Enum):
    IP_MSG = 0x18
    DATA = 0x60
    KDATA = 0x68
    IP_NSREQ = 0x70
    IP_PDREQ = 0x78
    IP_REQ = 0x80
    KDATA2 = 0x88
    IP_CTXT = 0x90
    IP_SPREQ = 0x98 #bitmap
    IP_MSCNT = 0x9C
    IP_SRIGHTS = 0xA0
    IP_SORIGHTS = 0xA4