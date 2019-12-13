from xnu.xnu_types import ThreadsIterator, TasksIterator, IPCEntryIterator, isTaskExist, isThreadExist, getMaxLengthProcName, IPCPort
from xnu.xnu_types import Thread, Task, IPCEntry, IPCSpace, ThreadVoucher, getTheadInfoTitle, getMaxLengthPcName, getMaxLengthContName
from xnu.sys_info import isUserThread, isValidPtr
import xnu.utils as utils
import traceback
import gdb


class PrintThreadList(gdb.Command):
    def __init__(self):
        super(PrintThreadList, self).__init__("xnu-threads", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 0:
                self.printAllThreads()
            elif len(argv) == 1:
                if argv[0] == "user":
                    self.printAllThreads(user_only=True, is_global=True)
                elif argv[0] == "global":
                    self.printAllThreads(is_global=True)
                else:
                    try:
                        requested_task = int(argv[0], 0)
                        if isTaskExist(requested_task):  # May be not safe...
                            self.printAllThreads(task=requested_task)
                    except:
                        gdb.GdbError(gdb.GdbError("wrong args"))
            else:
                raise gdb.GdbError("wrong args")
        except:
            raise gdb.GdbError(traceback.format_exc())

    def printAllThreads(self, user_only=False, is_global=False, task=None):
        counter = 0
        max_length_proc = getMaxLengthProcName()
        max_length_cont = getMaxLengthContName()
        max_length_pc = getMaxLengthPcName()
        gdb.write(getTheadInfoTitle(max_length_proc,
                                    max_length_cont, max_length_pc)+'\n')
        for thread in iter(ThreadsIterator(is_global, task)):
            if user_only == False or isUserThread(thread):
                counter += 1
                gdb.write(thread.printTheadInfoShort(
                    max_length_proc, max_length_cont, max_length_pc)+'\n')
        gdb.write(f"TOTAL {counter}\n")


PrintThreadList()


class PrintTaskList(gdb.Command):
    def __init__(self):
        super(PrintTaskList, self).__init__("xnu-tasks", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            self.printAllTasks()
        except:
            raise gdb.GdbError(traceback.format_exc())

    def printAllTasks(self):
        counter = 0
        for task in iter(TasksIterator()):
            counter += 1
            gdb.write(task.printTaskInfoShort()+'\n')
        gdb.write(f"TOTAL {counter}\n")


PrintTaskList()


class PrintThreadInfo(gdb.Command):
    def __init__(self):
        super(PrintThreadInfo, self).__init__(
            "xnu-thread-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1:
                thread = int(argv[0], 0)
                if isThreadExist(thread):
                    gdb.write(Thread(thread).printThreadInfoLong()+'\n')
                else:
                    gdb.write("Given thread do not exist\n")
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())


PrintThreadInfo()


class PrintTaskInfo(gdb.Command):
    def __init__(self):
        super(PrintTaskInfo, self).__init__("xnu-task-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1:
                task = int(argv[0], 0)
                if isTaskExist(task):
                    gdb.write(Task(task).printTaskInfoLong()+'\n')
                else:
                    gdb.write("Given task do not exist\n")
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())


PrintTaskInfo()


class PrintVoucherInfo(gdb.Command):
    def __init__(self):
        super(PrintVoucherInfo, self).__init__(
            "xnu-voucher-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1 and isValidPtr(int(argv[0], 0)):
                voucher = int(argv[0], 0)
                gdb.write(ThreadVoucher(voucher).printVoucherInfo()+'\n')
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())


PrintVoucherInfo()


class PrintIPCPortInfo(gdb.Command):
    def __init__(self):
        super(PrintIPCPortInfo, self).__init__(
            "xnu-ipc-port-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1 and isValidPtr(int(argv[0], 0)):
                ipc_port = int(argv[0], 0)
                gdb.write(IPCPort(ipc_port).printIPCPortInfo()+'\n')
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())


PrintIPCPortInfo()


class PrintIPCEntryList(gdb.Command):
    def __init__(self):
        super(PrintIPCEntryList, self).__init__(
            "xnu-ipc_entry-list", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 2 and isValidPtr(int(argv[1], 0)):
                if argv[0] == "-task" and isTaskExist(int(argv[1], 0)):
                    task = int(argv[1], 0)
                    self.printAllEntries(Task(task).ipc_space)
                elif argv[0] == "-space":
                    space = int(argv[1], 0)
                    self.printAllEntries(space)
                else:
                    gdb.write(
                        "wrong args, usage $ xnu-ipc_entry-list -task/table \{PTR\}\n")
            else:
                gdb.write(f"wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())

    def printAllEntries(self, address):
        gdb.write("=================================================\n")
        gdb.write(IPCSpace(address).printIPCSpaceInfo())
        gdb.write("=================================================\n\n")
        for entry in iter(IPCEntryIterator(address)):
            gdb.write(f"{entry.printIPCEntryInfo():<47}")
            gdb.write("-----------------------------------------------\n")


PrintIPCEntryList()
