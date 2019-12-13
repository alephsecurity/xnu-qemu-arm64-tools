import traceback
import xnu.xnu_types as types
import xnu.sys_info as sys_info
import gdb


class PrintThreadList(gdb.Command):
    def __init__(self):
        super(PrintThreadList, self).__init__("xnu-threads", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 0:
                self.print_all_threads()
            elif len(argv) == 1:
                if argv[0] == "user":
                    self.print_all_threads(user_only=True, is_global=True)
                elif argv[0] == "global":
                    self.print_all_threads(is_global=True)
                else:
                    try:
                        requested_task = int(argv[0], 0)
                        if types.is_task_exist(requested_task):  # May be not safe...
                            self.print_all_threads(task=requested_task)
                    except Exception:
                        gdb.GdbError(gdb.GdbError("wrong args"))
            else:
                raise gdb.GdbError("wrong args")
        except:
            raise gdb.GdbError(traceback.format_exc())

    def print_all_threads(self, user_only=False, is_global=False, task=None):
        counter = 0
        max_length_proc = types.get_max_length_proc_name()
        max_length_cont = types.get_max_length_cont_name()
        max_length_pc = types.get_max_length_pc_name()
        gdb.write(
            types.get_thead_info_title(max_length_proc, max_length_cont, max_length_pc)+'\n')
        for thread in iter(types.ThreadsIterator(is_global, task)):
            if user_only is False or sys_info.is_user_thread(thread):
                counter += 1
                gdb.write(thread.print_thead_info_short(
                    max_length_proc, max_length_cont, max_length_pc)+'\n')
        gdb.write(f"TOTAL {counter}\n")


PrintThreadList()


class PrintTaskList(gdb.Command):
    def __init__(self):
        super(PrintTaskList, self).__init__("xnu-tasks", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            self.print_all_tasks()
        except:
            raise gdb.GdbError(traceback.format_exc())

    def print_all_tasks(self):
        counter = 0
        for task in iter(types.TasksIterator()):
            counter += 1
            gdb.write(task.print_task_info_short()+'\n')
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
                if is_thread_exist(thread):
                    gdb.write(Thread(thread).print_thread_info_long()+'\n')
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
                if is_task_exist(task):
                    gdb.write(Task(task).print_task_info_long()+'\n')
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
            if len(argv) == 1 and is_valid_ptr(int(argv[0], 0)):
                voucher = int(argv[0], 0)
                gdb.write(ThreadVoucher(voucher).print_voucher_info()+'\n')
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())


PrintVoucherInfo()


class PrintIpcPortInfo(gdb.Command):
    def __init__(self):
        super(PrintIpcPortInfo, self).__init__(
            "xnu-ipc-port-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1 and is_valid_ptr(int(argv[0], 0)):
                ipc_port = int(argv[0], 0)
                gdb.write(IPCPort(ipc_port).print_ipc_port_info()+'\n')
            else:
                gdb.write("wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())

PrintIpcPortInfo()


class PrintIPCEntryList(gdb.Command):
    def __init__(self):
        super(PrintIPCEntryList, self).__init__(
            "xnu-ipc_entry-list", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 2 and is_valid_ptr(int(argv[1], 0)):
                if argv[0] == "-task" and is_task_exist(int(argv[1], 0)):
                    task = int(argv[1], 0)
                    self.print_all_tasks(Task(task).ipc_space)
                elif argv[0] == "-space":
                    space = int(argv[1], 0)
                    self.print_all_tasks(space)
                else:
                    gdb.write(
                        "wrong args, usage $ xnu-ipc_entry-list -task/table {PTR} \n")
            else:
                gdb.write(f"wrong args\n")
        except:
            raise gdb.GdbError(traceback.format_exc())

    def print_all_tasks(self, address):
        gdb.write("=================================================\n")
        gdb.write(types.IPCSpace(address).print_ipc_space_info())
        gdb.write("=================================================\n\n")
        for entry in iter(types.IPCEntryIterator(address)):
            gdb.write(f"{entry.print_ipc_entry_info():<47}")
            gdb.write("-----------------------------------------------\n")


PrintIPCEntryList()
