import xnu.constants as const
import xnu.utils as utils
import xnu.sys_info as sys_info
import gdb


# thread
class Thread:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.address = address
            self.task_ptr = utils.get_8_byte_at(
                address + const.ThreadOffsets.TASK.value)
            self.tid = utils.get_8_byte_at(
                address + const.ThreadOffsets.THREAD_ID.value)
            self.continuation = utils.get_8_byte_at(
                address + const.ThreadOffsets.CONTINUATION.value)
            self.global_threads_ptr = address + const.ThreadOffsets.GLOBAL_THREADS.value
            self.curr_task_threads_ptr = address + const.ThreadOffsets.TASK_THREADS.value
            self.ucontext_data = utils.get_8_byte_at(
                address + const.ThreadOffsets.CONTEXT_USER_DATA_PTR.value)
            self.kernel_stack_ptr = utils.get_8_byte_at(
                address + const.ThreadOffsets.KSTACK_PTR.value)
            self.voucher_ptr = utils.get_8_byte_at(
                address + const.ThreadOffsets.VOUCHER_PTR.value)

            self.initialized = True

            # Meta Data
            self.next_pc = const.NULL_PTR
            if self.is_currect():
                self.next_pc = utils.print_val('$pc')
            elif self.ucontext_data != const.NULL_PTR:
                user_saved_state = ThreadSavedState(self.ucontext_data)
                self.next_pc = user_saved_state.pc
            elif self.kernel_stack_ptr != const.NULL_PTR:
                self.next_pc = self.get_kernel_next_pc()

            self.task_object = Task(self.task_ptr)
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    # we cheating here.
    # the context switch happens in Switch_context function,
    # which is called only from thread_invoke function.
    # thread_invoke function called from thread_block_reason or thread_run.
    # Address to Switch_context function as next PC won't give as any valuable info
    # When thread_run called once when thread created
    # In addidtion, the context switch can be driven from exception or regular call
    # We want to know what function we had been called from.
    # For this, we need to come three frames backwards (to the thread_block_reason or thread_run)
    # From there we will check whether the next methon is exception_return
    # (i.e context switch came from ecxeption).
    # If not we will return the next pc (LR) to be called.
    # if the next function is exeption_return we will go one more frame further.
    def get_kernel_next_pc(self):
        if self.initialized is False or self.kernel_stack_ptr == const.NULL_PTR:
            return const.NULL_PTR
        # Get SP of thread_invoke. From Switch_context's frame
        kernel_saved_state = ThreadSavedState(self.kernel_stack_ptr)
        stack_ptr_thread_invoke = kernel_saved_state.sp
        # we are in thread_invoke context frame.
        # Look at LR and see if the next function is thread_invoke or thread_run
        next_to_thread_invoke = utils.get_8_byte_at(
            stack_ptr_thread_invoke +
            const.NextPcHelpOffsets.STORED_LR_IN_THREAD_INVOKE_FRAME.value)
        if next_to_thread_invoke == const.NextPcHelpOffsets.NEXT_IN_THREAD_RUN.value:
            # we came to thread invoke from thread_run.
            # The next LR will point to the function that we want
            kernel_next_pc = utils.get_8_byte_at(
                stack_ptr_thread_invoke +
                const.NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x38)
        elif next_to_thread_invoke == const.NextPcHelpOffsets.NEXT_IN_THREAD_BLOCK.value:
            # we came to thread invoke from thread_block.
            # The next LR will point to the function that we want or to exception return
            kernel_next_pc = utils.get_8_byte_at(
                stack_ptr_thread_invoke +
                const.NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x48)
        else:
            gdb.write(
                f"Something went wrong for thread {hex(self.address)} "
                f"with getting the next pc, maybe in a middle of thread's "
                f"create/exit")
            return const.NULL_PTR

        # Now we can check whether the next running function is exception_return.
        # If so, we need to go one more frame further
        if kernel_next_pc == const.NextPcHelpOffsets.EXEPTION_RETURN_PTR.value:
            # From the kernel code (Switch_context) we know that the pointer to
            # saved state is stored in x21
            next_x21_ptr = utils.get_8_byte_at(
                stack_ptr_thread_invoke + const.NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value +
                const.NextPcHelpOffsets.X21_IN_THREAD_INVOKE_FRAME.value)
            if next_x21_ptr == const.NULL_PTR:
                return const.NULL_PTR
            saved_state_exception_return = ThreadSavedState(next_x21_ptr)
            # now we have the saved state we can get the PC
            pc_from_saved_state = saved_state_exception_return.pc
            kernel_next_pc = pc_from_saved_state
        return kernel_next_pc

    def print_thead_info_short(self, max_length_proc, max_length_cont, max_length_pc):
        if self.initialized is False:
            return ""

        res_str = ""
        is_user = (self.ucontext_data != const.NULL_PTR)
        is_current = (self.address == sys_info.get_current_thread_ptr())
        res_str += '*' if is_current else ' '
        res_str += 'U |' if is_user else 'K |'
        if self.task_object.initialized is True and \
            self.task_object.bsdinfo_object.initialized is True:
            res_str += f" [{self.task_object.bsdinfo_object.bsd_pid}] |"
            res_str += f" {self.task_object.bsdinfo_object.bsd_name:<{max_length_proc}} |"
        else:
            res_str += f" [X] |"
            res_str += f' {"N/A":<{max_length_proc}} |'
        res_str += f" {self.tid} | {hex(self.address)} |"
        res_str += f' {"N/A":^{max_length_cont}} |' if self.continuation == const.NULL_PTR \
            else f" {sys_info.get_symbol(hex(self.continuation)):^{max_length_cont}} |"
        res_str += f' {"N/A":^{max_length_pc}} |' if self.next_pc == const.NULL_PTR \
            else f" {sys_info.get_symbol(hex(self.next_pc)):^{max_length_pc}} |"

        return res_str

    def print_thread_info_long(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        if sys_info.is_user_thread(self):
            res_str += "This is a user space thread\n\n"
        else:
            res_str += "This is a kernel thread\n\n"

        res_str += f"Next pc: {sys_info.get_symbol(hex(self.next_pc))}\n\n" \
            if self.next_pc != const.NULL_PTR else ""
        res_str += f"thread->task: " \
                f"{utils.print_ptr_as_string(self.task_ptr)}\n"
        if self.task_object.initialized is True:
            res_str += f"thread->task->bsd_info: "\
                f"{utils.print_ptr_as_string(self.task_object.bsd_info_ptr)}\n"
        if self.task_object.initialized is True:
            res_str += f"thread->task->bsd_info->p_name: "\
                f"{self.task_object.bsdinfo_object.bsd_name}\n"
            res_str += f"thread->task->bsd_info->p_pid: "\
                f"{utils.print_ptr_as_string(self.task_object.bsdinfo_object.bsd_pid)}\n"
        res_str += f"thread->thread_id: {str(self.tid)}\n"
        res_str += f"thread->continuation: "\
                f"{utils.print_ptr_as_string(self.continuation)}\n"
        res_str += f"thread->machine.contextData: "\
                f"{utils.print_ptr_as_string(self.ucontext_data)}\n"
        if self.ucontext_data:
            saved_state = ThreadSavedState(self.ucontext_data)
            res_str += saved_state.print_saved_state("thread->machine.contextData")
        res_str += f"thread->machine.kstackptr: "\
                f"{utils.print_ptr_as_string(self.kernel_stack_ptr)}\n"
        if self.kernel_stack_ptr:
            saved_state = ThreadSavedState(self.kernel_stack_ptr)
            res_str += saved_state.print_saved_state("thread->machine.kstackptr")
        res_str += f"thread->ith_voucher: "\
                f"{utils.print_ptr_as_string(self.voucher_ptr)}\n"

        return res_str

    def is_currect(self):
        if self.initialized is False:
            return False
        return self.address == sys_info.get_current_thread_ptr()


# proc
class BsdInfo:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.bsd_pid = utils.get_4_byte_at(
                address + const.BSDInfoOffsets.PID_IN_BSD_INFO.value)
            self.bsd_name = utils.get_string_at(
                address + const.BSDInfoOffsets.NAME_INBSD_INFO.value)
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

# ipc_space
class IPCSpace:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.is_table = utils.get_8_byte_at(
                address + const.IPCSpaceOffsets.IS_TABLE.value)
            self.is_table_size = utils.get_4_byte_at(
                address + const.IPCSpaceOffsets.IS_TABLE_SIZE.value)
            self.is_table_free = utils.get_4_byte_at(
                address + const.IPCSpaceOffsets.IS_TABLE_FREE.value)
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_ipc_space_info(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        res_str += f"ipc_space->is_table: {hex(self.is_table)}\n"
        res_str += f"ipc_space->is_table_size: {self.is_table_size} - (first reserved)\n"
        res_str += f"ipc_space->is_table_free: {self.is_table_free}\n"
        return res_str


class IPCEntry:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.address = address
            self.ie_object = utils.get_8_byte_at(address)
            self.ie_bits = utils.get_4_byte_at(
                address + const.IPCEntryOffsets.IE_BITS.value)
            self.ie_index = utils.get_4_byte_at(
                address + const.IPCEntryOffsets.IE_INDEX.value)
            self.index = utils.get_4_byte_at(
                address + const.IPCEntryOffsets.INDEX.value)

            if self.ie_object:
                self.ie_object_object = IPCObject(self.ie_object)
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_ipc_entry_info(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        res_str += f"ipc_entry->ie_object: {utils.print_ptr_as_string(self.ie_object)}\n"
        res_str += f"ipc_entry->ie_bits: {hex(self.ie_bits)}\n"
        res_str += f"ipc_entry->ie_index: {hex(self.ie_index)}\n"
        res_str += f"ipc_entry->ie_next: {hex(self.index)}\n"
        return res_str


class IPCObject:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.io_bits = utils.get_4_byte_at(
                address)  # parse it from ipc_object
            self.io_references = utils.get_4_byte_at(
                address + const.IPCObjectOffsets.IO_REFS.value)
            self.io_lock_data_1 = utils.get_8_byte_at(
                address + const.IPCObjectOffsets.IO_LOCK_DATA.value)
            self.io_lock_data_2 = utils.get_8_byte_at(
                address + const.IPCObjectOffsets.IO_LOCK_DATA.value + 0x08)  # next
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_ipc_object_info(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        res_str += f"ip_object->io_bits: "\
                f"{const.IO_BITS_TYPES[self.io_bits & const.IO_BITS_KOTYPE]}\n"
        res_str += f"ip_object->io_references: {hex(self.io_references)}\n"
        res_str += f"ip_object->io_lock_data[0]: {hex(self.io_lock_data_1)}\n"
        res_str += f"ip_object->io_lock_data[1]: {hex(self.io_lock_data_2)}\n"
        return res_str


class IPCPort:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.ip_object_object = IPCObject(address)
            self.ip_messages = utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_MSG.value)
            self.data = utils.get_8_byte_at(
                address + const.IPCPortOffsets.DATA.value)
            self.kdata = utils.get_8_byte_at(
                address + const.IPCPortOffsets.KDATA.value)
            self.kdata2 = utils.get_8_byte_at(
                address + const.IPCPortOffsets.KDATA2.value)
            self.ip_context = utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_CTXT.value)
            four_byte_data = utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value)
            self.ip_sprequests = (four_byte_data & (1 << 0))
            self.ip_spimportant = (four_byte_data & (1 << 1))
            self.ip_impdonation = (four_byte_data & (1 << 2))
            self.ip_tempowner = (four_byte_data & (1 << 3))
            self.ip_guarded = (four_byte_data & (1 << 4))
            self.ip_strict_guard = (four_byte_data & (1 << 5))
            self.ip_specialreply = (four_byte_data & (1 << 6))
            self.ip_sync_link_state = (four_byte_data & (0x000001ff))
            self.ip_impcount = (four_byte_data & (0xfffffe00))
            self.ip_mscount = utils.get_4_byte_at(
                address + const.IPCPortOffsets.IP_MSCNT.value)
            self.ip_srights = utils.get_4_byte_at(
                address + const.IPCPortOffsets.IP_SRIGHTS.value)
            self.ip_sorights = utils.get_4_byte_at(
                address + const.IPCPortOffsets.IP_SORIGHTS.value)
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_ipc_port_info(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        if self.ip_object_object.initialized is True:
            res_str += f"ipc_port->ip_object.io_bits: "\
                    f"{const.IO_BITS_TYPES[self.ip_object_object.io_bits & const.IO_BITS_KOTYPE]}\n"
            res_str += f"ipc_port->ip_object.io_references: "\
                f"{hex(self.ip_object_object.io_references)}\n"
            res_str += f"ipc_port->ip_object.io_lock_data[0]: "\
                f"{hex(self.ip_object_object.io_lock_data_1)}\n"
            res_str += f"ipc_port->ip_object.io_lock_data[1]: "\
                f"{hex(self.ip_object_object.io_lock_data_2)}\n"
        res_str += f"ipc_port->ip_messages: {self.ip_messages }\n"
        res_str += f"ipc_port->data: {utils.print_ptr_as_string(self.data) }\n"
        res_str += f"ipc_port->kdata: {utils.print_ptr_as_string(self.kdata) }\n"
        res_str += f"ipc_port->kdata2: {utils.print_ptr_as_string(self.kdata2 )}\n"
        res_str += f"ipc_port->ip_context: {self.ip_context }\n"
        res_str += f"ipc_port->ip_sprequests: {self.ip_sprequests }\n"
        res_str += f"ipc_port->ip_spimportant: {self.ip_spimportant }\n"
        res_str += f"ipc_port->ip_impdonation: {self.ip_impdonation }\n"
        res_str += f"ipc_port->ip_tempowner: {self.ip_tempowner }\n"
        res_str += f"ipc_port->ip_guarded: {self.ip_guarded }\n"
        res_str += f"ipc_port->ip_strict_guard: {self.ip_strict_guard }\n"
        res_str += f"ipc_port->ip_specialreply: {self.ip_specialreply }\n"
        res_str += f"ipc_port->ip_sync_link_state: {self.ip_sync_link_state }\n"
        res_str += f"ipc_port->ip_impcount: {self.ip_impcount }\n"
        res_str += f"ipc_port->ip_mscount: {hex(self.ip_mscount)}\n"
        res_str += f"ipc_port->ip_srights: {hex(self.ip_srights)}\n"
        res_str += f"ipc_port->ip_sorights: {hex(self.ip_sorights)}\n"
        return res_str


class Task:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.address = address
            self.task_lst_ptr = address + const.TaskOffsets.TASK_NEXT.value
            self.threads_lst_ptr = address + const.TaskOffsets.THREAD_LST_FROM_TASK.value
            self.bsd_info_ptr = utils.get_8_byte_at(
                address + const.TaskOffsets.BSD_INFO.value)
            self.itk_self = utils.get_8_byte_at(
                address + const.TaskOffsets.ITK_SELF.value)
            self.ipc_space = utils.get_8_byte_at(
                address + const.TaskOffsets.IPC_SPACE.value)

            self.ipc_space_object = IPCSpace(self.ipc_space)
            self.bsdinfo_object = BsdInfo(self.bsd_info_ptr)
            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_task_info_short(self, max_length_proc):
        if self.initialized is False:
            return ""
        res_str = ""
        is_current = (self.address == sys_info.get_current_task_ptr())
        res_str += '*' if is_current else ' '
        if self.bsdinfo_object.initialized is True:
            res_str += f" [{self.bsdinfo_object.bsd_pid:^2}] | "\
                f"{self.bsdinfo_object.bsd_name:<{max_length_proc}} |"
        else:
            res_str += f" [{'X':^2}] | {'N/A':<{max_length_proc}} |"
        res_str += f"  {hex(self.address)} "

        return res_str

    def print_task_info_long(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        res_str += f"task->bsd_info: {utils.print_ptr_as_string(self.bsd_info_ptr)}\n"
        if self.bsdinfo_object.initialized is True:
            res_str += f"task->bsd_info->p_name: {self.bsdinfo_object.bsd_name}\n"
            res_str += f"task->bsd_info->p_pid: {hex(self.bsdinfo_object.bsd_pid)}\n"
        res_str += f"task->itk_self: {utils.print_ptr_as_string(self.itk_self)}\n"
        res_str += f"task->ipc_space: {utils.print_ptr_as_string(self.ipc_space)}\n"
        if self.ipc_space_object.initialized is True:
            res_str += f"task->ipc_space->is_table: "\
                    f"{utils.print_ptr_as_string(self.ipc_space_object.is_table)}\n"
        return res_str

# Saved State


class ThreadSavedState:
    def __init__(self, address):
        if address != const.NULL_PTR:
            address += 0x08  # skip arm_state_hdr_t ash at arm_saved_state
            self._x0 = utils.get_8_byte_at(address)
            self._x1 = utils.get_8_byte_at(address + 0x08)
            self._x2 = utils.get_8_byte_at(address + 0x10)
            self._x3 = utils.get_8_byte_at(address + 0x18)
            self._x4 = utils.get_8_byte_at(address + 0x20)
            self._x5 = utils.get_8_byte_at(address + 0x28)
            self._x6 = utils.get_8_byte_at(address + 0x30)
            self._x7 = utils.get_8_byte_at(address + 0x38)
            self._x8 = utils.get_8_byte_at(address + 0x40)
            self._x9 = utils.get_8_byte_at(address + 0x48)
            self._x10 = utils.get_8_byte_at(address + 0x50)
            self._x11 = utils.get_8_byte_at(address + 0x58)
            self._x12 = utils.get_8_byte_at(address + 0x60)
            self._x13 = utils.get_8_byte_at(address + 0x68)
            self._x14 = utils.get_8_byte_at(address + 0x70)
            self._x15 = utils.get_8_byte_at(address + 0x78)
            self._x16 = utils.get_8_byte_at(address + 0x80)
            self._x17 = utils.get_8_byte_at(address + 0x88)
            self._x18 = utils.get_8_byte_at(address + 0x90)
            self._x19 = utils.get_8_byte_at(address + 0x98)
            self._x20 = utils.get_8_byte_at(address + 0xa0)
            self._x21 = utils.get_8_byte_at(address + 0xa8)
            self._x22 = utils.get_8_byte_at(address + 0xb0)
            self._x23 = utils.get_8_byte_at(address + 0xb8)
            self._x24 = utils.get_8_byte_at(address + 0xc0)
            self._x25 = utils.get_8_byte_at(address + 0xc8)
            self._x26 = utils.get_8_byte_at(address + 0xd0)
            self._x27 = utils.get_8_byte_at(address + 0xd8)
            self._x28 = utils.get_8_byte_at(address + 0xe0)
            self._fp = utils.get_8_byte_at(address + 0xe8)
            self._lr = utils.get_8_byte_at(address + 0xf0)
            self.sp = utils.get_8_byte_at(address + 0xf8)
            self.pc = utils.get_8_byte_at(address + 0x100)
            self._cpsr = utils.get_4_byte_at(address + 0x108)
            self._reserved = utils.get_4_byte_at(address + 0x10c)
            self._far = utils.get_8_byte_at(address + 0x110)
            self._esr = utils.get_4_byte_at(address + 0x118)
            self._exception = utils.get_4_byte_at(address + 0x11c)

            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_saved_state(self, previous_struct):
        if self.initialized is False:
            return ""
        res_str = ""
        res_str += f"{previous_struct}->x0: {utils.print_ptr_as_string(self._x0)}\n"
        res_str += f"{previous_struct}->x1: {utils.print_ptr_as_string(self._x1)}\n"
        res_str += f"{previous_struct}->x2: {utils.print_ptr_as_string(self._x2)}\n"
        res_str += f"{previous_struct}->x3: {utils.print_ptr_as_string(self._x3)}\n"
        res_str += f"{previous_struct}->x4: {utils.print_ptr_as_string(self._x4)}\n"
        res_str += f"{previous_struct}->x5: {utils.print_ptr_as_string(self._x5)}\n"
        res_str += f"{previous_struct}->x6: {utils.print_ptr_as_string(self._x6)}\n"
        res_str += f"{previous_struct}->x7: {utils.print_ptr_as_string(self._x7)}\n"
        res_str += f"{previous_struct}->x8: {utils.print_ptr_as_string(self._x8)}\n"
        res_str += f"{previous_struct}->x9: {utils.print_ptr_as_string(self._x9)}\n"
        res_str += f"{previous_struct}->x10: {utils.print_ptr_as_string(self._x10)}\n"
        res_str += f"{previous_struct}->x11: {utils.print_ptr_as_string(self._x11)}\n"
        res_str += f"{previous_struct}->x12: {utils.print_ptr_as_string(self._x12)}\n"
        res_str += f"{previous_struct}->x13: {utils.print_ptr_as_string(self._x13)}\n"
        res_str += f"{previous_struct}->x14: {utils.print_ptr_as_string(self._x14)}\n"
        res_str += f"{previous_struct}->x15: {utils.print_ptr_as_string(self._x15)}\n"
        res_str += f"{previous_struct}->x16: {utils.print_ptr_as_string(self._x16)}\n"
        res_str += f"{previous_struct}->x17: {utils.print_ptr_as_string(self._x17)}\n"
        res_str += f"{previous_struct}->x18: {utils.print_ptr_as_string(self._x18)}\n"
        res_str += f"{previous_struct}->x19: {utils.print_ptr_as_string(self._x19)}\n"
        res_str += f"{previous_struct}->x20: {utils.print_ptr_as_string(self._x20)}\n"
        res_str += f"{previous_struct}->x21: {utils.print_ptr_as_string(self._x21)}\n"
        res_str += f"{previous_struct}->x22: {utils.print_ptr_as_string(self._x22)}\n"
        res_str += f"{previous_struct}->x23: {utils.print_ptr_as_string(self._x23)}\n"
        res_str += f"{previous_struct}->x24: {utils.print_ptr_as_string(self._x24)}\n"
        res_str += f"{previous_struct}->x25: {utils.print_ptr_as_string(self._x25)}\n"
        res_str += f"{previous_struct}->x26: {utils.print_ptr_as_string(self._x26)}\n"
        res_str += f"{previous_struct}->x27: {utils.print_ptr_as_string(self._x27)}\n"
        res_str += f"{previous_struct}->x28: {utils.print_ptr_as_string(self._x28)}\n"
        res_str += f"{previous_struct}->fp: {utils.print_ptr_as_string(self._fp)}\n"
        res_str += f"{previous_struct}->lr: {utils.print_ptr_as_string(self._lr)}\n"
        res_str += f"{previous_struct}->sp: {utils.print_ptr_as_string(self.sp)}\n"
        res_str += f"{previous_struct}->pc: \
{sys_info.get_symbol(utils.print_ptr_as_string(self.pc))}\n"
        res_str += f"{previous_struct}->cpsr: {hex(self._cpsr)}\n"
        res_str += f"{previous_struct}->reserved: {hex(self._reserved)}\n"
        res_str += f"{previous_struct}->far: {utils.print_ptr_as_string(self._far)}\n"
        res_str += f"{previous_struct}->esr: {hex(self._esr)}\n"
        res_str += f"{previous_struct}->exception: {hex(self._exception)}\n"

        return res_str

# Voucher

#TODO offsets
class ThreadVoucher:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.iv_hash = utils.get_8_byte_at(address)
            self.iv_sum = utils.get_8_byte_at(address + 0x04)
            self.iv_refs = utils.get_8_byte_at(address + 0x08)
            self.iv_table_size = utils.get_8_byte_at(address + 0x0c)
            self.iv_inline_table = utils.get_8_byte_at(address + 0x10)
            self.iv_table = utils.get_8_byte_at(address + 0x30)
            self.iv_port = utils.get_8_byte_at(address + 0x38)
            self.iv_hash_link = utils.get_8_byte_at(address + 0x40)

            self.initialized = True
        else:
            self.initialized = False
            #gdb.write(f"WARNING: null pointer in {__name__}: {self.__class__.__name__}\n")

    def print_voucher_info(self):
        if self.initialized is False:
            return ""
        res_str = "\n"
        res_str += f"ipc_voucher->iv_hash: {hex(self.iv_hash)}\n"
        res_str += f"ipc_voucher->iv_sum: {hex(self.iv_sum)}\n"
        res_str += f"ipc_voucher->iv_refs: {hex(self.iv_refs)}\n"
        res_str += f"ipc_voucher->iv_table_size: {hex(self.iv_table_size)}\n"
        res_str += f"ipc_voucher->iv_inline_table: {hex(self.iv_inline_table)}\n"
        res_str += f"ipc_voucher->iv_table: {hex(self.iv_table)}\n"
        res_str += f"ipc_voucher->iv_port: {hex(self.iv_port)}\n"
        res_str += f"ipc_voucher->iv_hash_link: {hex((self.iv_hash_link))}\n"
        return res_str



# THREAD ITERATOR
class ThreadsIterator:
    def __init__(self, is_global=False, task=None):
        self.next_thread_ptr = None
        self.stop_contition = None
        self.result = None
        if is_global:
            self.type = const.ThrdItrType.GLOBAL
        else:
            self.type = const.ThrdItrType.TASK
            if task != const.NULL_PTR and task is not None:
                self.task_ptr = task
            else:
                raise gdb.GdbError("ThreadsIterator: null task pointer!")


    def __iter__(self):
        if self.type == const.ThrdItrType.GLOBAL:
            self.next_thread_ptr = utils.get_8_byte_at(
                const.GLOBAL_THREADS_PTR)
            self.stop_contition = const.GLOBAL_THREADS_PTR
        else:
            relevant_task = Task(self.task_ptr)
            self.next_thread_ptr = utils.get_8_byte_at(
                relevant_task.threads_lst_ptr)
            self.stop_contition = self.task_ptr + \
                const.TaskOffsets.THREAD_LST_FROM_TASK.value
        return self

    def __next__(self):
        if self.next_thread_ptr != self.stop_contition:
            self.result = Thread(self.next_thread_ptr)
            if self.type == const.ThrdItrType.GLOBAL:
                self.next_thread_ptr = utils.get_8_byte_at(
                    self.result.global_threads_ptr)
            else:
                self.next_thread_ptr = utils.get_8_byte_at(
                    self.result.curr_task_threads_ptr)
            return self.result
        raise StopIteration


class TasksIterator:
    def __init__(self):
        self.stop_contition = const.GLOBAL_TASKS_PTR
        self.next_task_ptr = utils.get_8_byte_at(const.GLOBAL_TASKS_PTR)
        self.result = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_task_ptr != self.stop_contition:
            self.result = Task(self.next_task_ptr)
            self.next_task_ptr = utils.get_8_byte_at(self.result.task_lst_ptr)
            return self.result
        raise StopIteration


class IPCEntryIterator:
    def __init__(self, address):
        if sys_info.is_valid_ptr(address):
            self.entry = IPCSpace(address).is_table
            self.size = IPCSpace(address).is_table_size
            self.index = 0
        else:
            raise gdb.GdbError(f"Wrong ipc_entry pointer {address}")

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < self.size:
            result = IPCEntry(self.entry + (self.index * 0x18))
            self.index += 1
            if (result.ie_bits & const.IE_BITS_TYPE_MASK) != 0:
                return result
        raise StopIteration


# Global functions
def is_task_exist(task):
    return task in list(tmptask.address for tmptask in iter(TasksIterator()))


def is_thread_exist(thread):
    return thread in list(tmpthread.address for tmpthread in iter(ThreadsIterator(is_global=True)))


def get_max_length_proc_name():
    max_length = 0
    for task in iter(TasksIterator()):
        if task.bsdinfo_object.initialized is True and \
            len(task.bsdinfo_object.bsd_name) > max_length:
            max_length = len(task.bsdinfo_object.bsd_name)
    return max_length


def get_max_length_cont_name():
    max_length = 0
    for thread in iter(ThreadsIterator(True)):
        if len(sys_info.get_symbol(utils.print_ptr_as_string(thread.continuation))) > max_length:
            max_length = len(sys_info.get_symbol(
                utils.print_ptr_as_string(thread.continuation)))
    return max_length


def get_max_length_pc_name():
    max_length = 0
    for thread in iter(ThreadsIterator(True)):
        if len(sys_info.get_symbol(utils.print_ptr_as_string(thread.next_pc))) > max_length:
            max_length = len(sys_info.get_symbol(
                utils.print_ptr_as_string(thread.next_pc)))
    return max_length


def get_thead_info_title(max_length_proc, max_length_cont, max_length_pc):
    res_str = ""
    res_str += f'U/K| PID | {"NAME":^{max_length_proc}} | TID |     '\
f'THREAD_PTR     | {"CONTINUATION":^{max_length_cont}} | {"NEXT_PC*":^{max_length_pc}} |'
    return res_str
