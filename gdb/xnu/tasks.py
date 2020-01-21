""" This module exposes functions available to user from th gdb """
import traceback
import xnu.xnu_types as types
import xnu.sys_info as sys_info
import gdb


class PrintThreadList(gdb.Command):
    """ Gdb command to print all threads """
    def __init__(self):
        super(PrintThreadList, self).__init__("xnu-threads", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ Parsing arguments, invoking printing.
        You can print all theeads of current task (no argument to command),
        All threads of current task xnu-threads current
        All user threads - xnu-threads user
        All threads whithin the system - xnu-threads
        All threads of specific task - xnu-threads ${task_ptr}
        """
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return        
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 0:
                self.print_all_threads(is_global=True)
            elif len(argv) == 1:
                if argv[0] == "user":
                    self.print_all_threads(user_only=True, is_global=True)
                elif argv[0] == "current":
                    task = sys_info.get_current_task_ptr()
                    self.print_all_threads(task=task)
                else:
                    try:
                        requested_task = int(argv[0], 0)
                        if sys_info.is_valid_ptr(requested_task):
                            if not types.is_task_exist(requested_task):
                                gdb.write(f"\nRequested task {argv[0]} do not exist"
                                          f" in the tasks list of the system!\n\n\n")
                            self.print_all_threads(task=requested_task)
                    except Exception:
                        gdb.GdbError(gdb.GdbError("wrong args"))
            else:
                raise gdb.GdbError("wrong args")
        except Exception:
            raise gdb.GdbError(traceback.format_exc())

    def print_all_threads(self, user_only=False, is_global=False, task=None):
        """ Iterate over threads iterator and print data for each """
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
    """ Gdb command to print all tasks """
    def __init__(self):
        super(PrintTaskList, self).__init__("xnu-tasks", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ Go over task iterator and print all task data """
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return
        try:
            max_length_proc = types.get_max_length_proc_name()
            for task in iter(types.TasksIterator()):
                gdb.write(task.print_task_info_short(max_length_proc)+'\n')
        except Exception:
            raise gdb.GdbError(traceback.format_exc())


PrintTaskList()


class PrintThreadInfo(gdb.Command):
    """ gdb command to print all known info of specific thread """
    def __init__(self):
        super(PrintThreadInfo, self).__init__(
            "xnu-thread-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ print info of given thread, checking if exist"""
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1:
                thread = int(argv[0], 0)
                if types.is_thread_exist(thread):
                    gdb.write(types.Thread(thread).print_thread_info_long()+'\n')
                else:
                    gdb.write("Given thread do not exist\n")
            else:
                gdb.write("wrong args\n")
        except  Exception:
            raise gdb.GdbError(traceback.format_exc())


PrintThreadInfo()


class PrintTaskInfo(gdb.Command):
    """ gdb command to print all known info of specific task """
    def __init__(self):
        super(PrintTaskInfo, self).__init__("xnu-task-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ print info of given task, checking if exist"""
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return        
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1:
                task = int(argv[0], 0) #convert to integer
                if sys_info.is_valid_ptr(task):
                    if not types.is_task_exist(task):
                        gdb.write(f"\nRequested task {argv[0]} do not exist in the task "
                                  f"list of the system!\n\n\n")
                    gdb.write(types.Task(task).print_task_info_long()+'\n')
                else:
                    gdb.write("Given task do not exist\n")
            else:
                gdb.write("wrong args\n")
        except Exception:
            raise gdb.GdbError(traceback.format_exc())


PrintTaskInfo()


class PrintVoucherInfo(gdb.Command):
    """
    gdb command to print all known info of specific mach voucher
    xnu kernel ref: darwin-xnu/osfmk/ipc/ipc_voucher.h (ipc_voucher)
    """

    def __init__(self):
        super(PrintVoucherInfo, self).__init__(
            "xnu-voucher-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return        
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1 and sys_info.is_valid_ptr(int(argv[0], 0)):
                voucher = int(argv[0], 0)
                gdb.write(types.ThreadVoucher(voucher).print_voucher_info()+'\n')
            else:
                gdb.write("wrong args\n")
        except Exception:
            raise gdb.GdbError(traceback.format_exc())


PrintVoucherInfo()


class PrintIpcPortInfo(gdb.Command):
    """
    gdb command to print all known info of specific xnu ipc_port
    xnu kernel ref: darwin-xnu/osfmk/ipc/ipc_port.h (ipc_port)
    """
    def __init__(self):
        super(PrintIpcPortInfo, self).__init__(
            "xnu-ipc-port-info", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ print info """
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return         
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 1 and sys_info.is_valid_ptr(int(argv[0], 0)):
                ipc_port = int(argv[0], 0)
                gdb.write(types.IPCPort(ipc_port).print_ipc_port_info()+'\n')
            else:
                gdb.write("wrong args\n")
        except Exception:
            raise gdb.GdbError(traceback.format_exc())


PrintIpcPortInfo()


class PrintIPCEntryList(gdb.Command):
    """
    gdb command to print a tabl of ipc_entry(ies) of ipc space
    xnu kernel ref:
    darwin-xnu/osfmk/ipc/ipc_space.h  (ipc_space)
    darwin-xnu/osfmk/ipc/ipc_entry.h  (ipc_entry)
    """
    def __init__(self):
        super(PrintIPCEntryList, self).__init__(
            "xnu-ipc_entry-list", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        """ Can get as argument pointer to task or pointer to space"""
        if sys_info.is_in_kernel_space() is False:
            gdb.write("\nYou are currently in user space, "\
                "this functionality is not available here.\n\n")
            return         
        try:
            argv = gdb.string_to_argv(arg)
            if len(argv) == 2 and sys_info.is_valid_ptr(int(argv[1], 0)):
                if argv[0] == "-task":
                    task = int(argv[1], 0)
                    if not types.is_task_exist(task):
                        gdb.write(f"\nRequested task {argv[1]} do not exist in the tasks"
                                  f"list of the system!\n\n\n")
                    self.print_ipc_space_table(types.Task(task).ipc_space)
                elif argv[0] == "-space":
                    space = int(argv[1], 0)
                    self.print_ipc_space_table(space)
                else:
                    gdb.write(
                        "wrong args, usage $ xnu-ipc_entry-list -task/table {PTR} \n")
            else:
                gdb.write(f"wrong args\n")
        except Exception:
            raise gdb.GdbError(traceback.format_exc())

    def print_ipc_space_table(self, address):
        """ print info """
        gdb.write("=================================================\n")
        gdb.write(types.IPCSpace(address).print_ipc_space_info())
        gdb.write("=================================================\n\n")
        for entry in iter(types.IPCEntryIterator(address)):
            gdb.write(f"{entry.print_ipc_entry_info():<47}")
            gdb.write("-----------------------------------------------\n")


PrintIPCEntryList()
