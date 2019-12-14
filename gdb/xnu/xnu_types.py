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
            raise gdb.GdbError(f"Null pointer in {__name__}")

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
            raise gdb.GdbError(
                "Something went wrong with getting the next pc, maybe running on another kernel?")

        # Now we can check whether the next running function is exception_return.
        # If so, we need to go one more frame further
        if kernel_next_pc == const.NextPcHelpOffsets.EXEPTION_RETURN_PTR.value:
            # From the kernel code (Switch_context) we know that the pointer to
            # saved state is stored in x21
            next_x21_ptr = utils.get_8_byte_at(
                stack_ptr_thread_invoke + const.NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value +
                const.NextPcHelpOffsets.X21_IN_THREAD_INVOKE_FRAME.value)
            saved_state_exception_return = ThreadSavedState(next_x21_ptr)
            # now we have the saved state we can get the PC
            pc_from_saved_state = saved_state_exception_return.pc
            kernel_next_pc = pc_from_saved_state
        return kernel_next_pc

    def print_thead_info_short(self, max_length_proc, max_length_cont, max_length_pc):
        res_str = ""
        is_user = True if self.ucontext_data != const.NULL_PTR else False
        is_current = True if self.address == sys_info.get_current_thread_ptr() else False
        res_str += '*' if is_current else ' '
        res_str += 'U |' if is_user else 'K |'
        res_str += f" [{self.task_object.bsdinfo_object.bsd_pid}] |"
        res_str += f" {self.task_object.bsdinfo_object.bsd_name:<{max_length_proc}} |"
        res_str += f" {self.tid} | {hex(self.address)} |"
        res_str += f' {"N/A":^{max_length_cont}} |' if self.continuation == const.NULL_PTR \
            else f" {sys_info.get_symbol(hex(self.continuation)):^{max_length_cont}} |"
        res_str += f' {"N/A":^{max_length_pc}} |' if self.next_pc == const.NULL_PTR \
            else f" {sys_info.get_symbol(hex(self.next_pc)):^{max_length_pc}} |"

        return res_str

    def print_thread_info_long(self):
        res_str = ""
        if sys_info.is_user_thread(self):
            res_str += "This is a user space thread\n\n"
        else:
            res_str += "This is a kernel thread\n\n"

        res_str += f"Next pc: {sys_info.get_symbol(hex(self.next_pc))}\n\n" \
            if self.next_pc != const.NULL_PTR else ""
        res_str += f"thread->task\
            {utils.print_ptr_as_string(self.task_ptr)}\n"
        if self.task_object:
            res_str += f"thread->task->bsd_info\
                {utils.print_ptr_as_string(self.task_object.bsd_info_ptr)}\n"
        if self.task_object.bsd_info_ptr:
            res_str += f"thread->task->bsd_info->bsd_name\
                {self.task_object.bsdinfo_object.bsd_name}\n"
            res_str += f"thread->task->bsd_info->bsd_pid\
                {utils.print_ptr_as_string(self.task_object.bsdinfo_object.bsd_pid)}\n"
        res_str += f"thread->tid                            {str(self.tid)}\n"
        res_str += f"thread->continuation\
            {utils.print_ptr_as_string(self.continuation)}\n"
        res_str += f"thread->ucontext_data\
            {utils.print_ptr_as_string(self.ucontext_data)}\n"
        if self.ucontext_data:
            saved_state = ThreadSavedState(self.ucontext_data)
            res_str += saved_state.print_saved_state("thread->ucontext_data")
        res_str += f"thread->kstackptr\
            {utils.print_ptr_as_string(self.kernel_stack_ptr)}\n"
        if self.kernel_stack_ptr:
            saved_state = ThreadSavedState(self.kernel_stack_ptr)
            res_str += saved_state.print_saved_state("thread->kstackptr")
        res_str += f"thread->voucher_ptr\
            {utils.print_ptr_as_string(self.voucher_ptr)}\n"

        return res_str

    def is_currect(self):
        return self.address == sys_info.get_current_thread_ptr()


# proc
class BsdInfo:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.bsd_pid = utils.get_4_byte_at(
                address + const.BSDInfoOffsets.PID_IN_BSD_INFO.value)
            self.bsd_name = utils.get_string_at(
                address + const.BSDInfoOffsets.NAME_INBSD_INFO.value)
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")



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
        else:
            raise gdb.GdbError(f"Null pointer for {__name__}")

    def print_ipc_space_info(self):
        res_str = ""
        res_str += f"ipc_space->is_table {hex(self.is_table)}\n"
        res_str += f"ipc_space->is_table_size {self.is_table_size} - (first reserved)\n"
        res_str += f"ipc_space->is_table_free {self.is_table_free}\n"
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
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Entry {address}")

    def print_ipc_entry_info(self):
        res_str = ""
        res_str += f"ipc_entry->ie_object = {utils.print_ptr_as_string(self.ie_object)}\n"
        res_str += f"ipc_entry->ie_bits = {hex(self.ie_bits)}\n"
        res_str += f"ipc_entry->ie_index = {hex(self.ie_index)}\n"
        res_str += f"ipc_entry->ie_next = {hex(self.index)}\n"
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
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Object {address}")

    def print_ipc_object_info(self):
        res_str = ""
        res_str += f"ip_object->io_bits \
{const.IO_BITS_TYPES[self.io_bits & const.IO_BITS_KOTYPE]}\n"
        res_str += f"ip_object->io_references   {hex(self.io_references)}\n"
        res_str += f"ip_object->io_lock_data[0] {hex(self.io_lock_data_1)}\n"
        res_str += f"ip_object->io_lock_data[1] {hex(self.io_lock_data_2)}\n"
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
            self.ip_sprequests = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 0))
            self.ip_spimportant = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 1))
            self.ip_impdonation = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 2))
            self.ip_tempowner = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 3))
            self.ip_guarded = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 4))
            self.ip_strict_guard = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 5))
            self.ip_specialreply = (
                utils.get_4_byte_at(address + const.IPCPortOffsets.IP_SPREQ.value) & (1 << 6))
            self.ip_sync_link_state = (utils.get_4_byte_at(
                address + const.IPCPortOffsets.IP_SPREQ.value) & (0x000001ff))
            self.ip_impcount = (utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_SPREQ.value) & (0xfffffe00))
            self.ip_mscount = utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_MSCNT.value)
            self.ip_srights = utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_SRIGHTS.value)
            self.ip_sorights = utils.get_8_byte_at(
                address + const.IPCPortOffsets.IP_SORIGHTS.value)

    def print_ipc_port_info(self):
        res_str = ""
        res_str += self.ip_object_object.print_ipc_object_info()
        res_str += f"ipc_port->ip_messages       {self.ip_messages }\n"
        res_str += f"ipc_port->data       {utils.print_ptr_as_string(self.data) }\n"
        res_str += f"ipc_port->kdata       {utils.print_ptr_as_string(self.kdata) }\n"
        res_str += f"ipc_port->kdata2       {utils.print_ptr_as_string(self.kdata2 )}\n"
        res_str += f"ipc_port->ip_context       {self.ip_context }\n"
        res_str += f"ipc_port->ip_sprequests       {self.ip_sprequests }\n"
        res_str += f"ipc_port->ip_spimportant       {self.ip_spimportant }\n"
        res_str += f"ipc_port->ip_impdonation       {self.ip_impdonation }\n"
        res_str += f"ipc_port->ip_tempowner       {self.ip_tempowner }\n"
        res_str += f"ipc_port->ip_guarded       {self.ip_guarded }\n"
        res_str += f"ipc_port->ip_strict_guard       {self.ip_strict_guard }\n"
        res_str += f"ipc_port->ip_specialreply       {self.ip_specialreply }\n"
        res_str += f"ipc_port->ip_sync_link_state       {self.ip_sync_link_state }\n"
        res_str += f"ipc_port->ip_impcount       {self.ip_impcount }\n"
        res_str += f"ipc_port->ip_mscount       {self.ip_mscount }\n"
        res_str += f"ipc_port->ip_srights       {self.ip_srights }\n"
        res_str += f"ipc_port->ip_sorights       {self.ip_sorights }\n"
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
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")

    def print_task_info_short(self):
        res_str = ""
        is_current = True if self.address == sys_info.get_current_task_ptr() else False
        res_str += '*' if is_current else ' '
        res_str += f" [{self.bsdinfo_object.bsd_pid}] | {self.bsdinfo_object.bsd_name:<15} |"
        res_str += f"  {hex(self.address)} "

        return res_str

    def print_task_info_long(self):
        res_str = "\n"
        res_str += f"task->bsd_info = {utils.print_ptr_as_string(self.bsd_info_ptr)}\n"
        res_str += f"task->itk_self = {utils.print_ptr_as_string(self.itk_self)}\n"
        res_str += f"task->ipc_space = {utils.print_ptr_as_string(self.ipc_space)}\n"
        res_str += f"task->ipc_space->is_table = \
            {utils.print_ptr_as_string(self.ipc_space_object.is_table)}\n"
        return res_str

# Saved State


class ThreadSavedState:
    def __init__(self, address):
        if address != const.NULL_PTR:
            address += 0x08  # skip arm_state_hdr_t ash at arm_saved_state
            self.x0 = utils.get_8_byte_at(address)
            self.x1 = utils.get_8_byte_at(address + 0x08)
            self.x2 = utils.get_8_byte_at(address + 0x10)
            self.x3 = utils.get_8_byte_at(address + 0x18)
            self.x4 = utils.get_8_byte_at(address + 0x20)
            self.x5 = utils.get_8_byte_at(address + 0x28)
            self.x6 = utils.get_8_byte_at(address + 0x30)
            self.x7 = utils.get_8_byte_at(address + 0x38)
            self.x8 = utils.get_8_byte_at(address + 0x40)
            self.x9 = utils.get_8_byte_at(address + 0x48)
            self.x10 = utils.get_8_byte_at(address + 0x50)
            self.x11 = utils.get_8_byte_at(address + 0x58)
            self.x12 = utils.get_8_byte_at(address + 0x60)
            self.x13 = utils.get_8_byte_at(address + 0x68)
            self.x14 = utils.get_8_byte_at(address + 0x70)
            self.x15 = utils.get_8_byte_at(address + 0x78)
            self.x16 = utils.get_8_byte_at(address + 0x80)
            self.x17 = utils.get_8_byte_at(address + 0x88)
            self.x18 = utils.get_8_byte_at(address + 0x90)
            self.x19 = utils.get_8_byte_at(address + 0x98)
            self.x20 = utils.get_8_byte_at(address + 0xa0)
            self.x21 = utils.get_8_byte_at(address + 0xa8)
            self.x22 = utils.get_8_byte_at(address + 0xb0)
            self.x23 = utils.get_8_byte_at(address + 0xb8)
            self.x24 = utils.get_8_byte_at(address + 0xc0)
            self.x25 = utils.get_8_byte_at(address + 0xc8)
            self.x26 = utils.get_8_byte_at(address + 0xd0)
            self.x27 = utils.get_8_byte_at(address + 0xd8)
            self.x28 = utils.get_8_byte_at(address + 0xe0)
            self.fp = utils.get_8_byte_at(address + 0xe8)
            self.lr = utils.get_8_byte_at(address + 0xf0)
            self.sp = utils.get_8_byte_at(address + 0xf8)
            self.pc = utils.get_8_byte_at(address + 0x100)
            self.cpsr = utils.get_4_byte_at(address + 0x108)
            self.reserved = utils.get_4_byte_at(address + 0x10c)
            self.far = utils.get_8_byte_at(address + 0x110)
            self.esr = utils.get_4_byte_at(address + 0x118)
            self.exception = utils.get_4_byte_at(address + 0x11c)

    def print_saved_state(self, previous_struct):
        res_str = ""
        res_str += f"{previous_struct}->x0			{utils.print_ptr_as_string(self.x0)}\n"
        res_str += f"{previous_struct}->x1			{utils.print_ptr_as_string(self.x1)}\n"
        res_str += f"{previous_struct}->x2			{utils.print_ptr_as_string(self.x2)}\n"
        res_str += f"{previous_struct}->x3			{utils.print_ptr_as_string(self.x3)}\n"
        res_str += f"{previous_struct}->x4			{utils.print_ptr_as_string(self.x4)}\n"
        res_str += f"{previous_struct}->x5			{utils.print_ptr_as_string(self.x5)}\n"
        res_str += f"{previous_struct}->x6			{utils.print_ptr_as_string(self.x6)}\n"
        res_str += f"{previous_struct}->x7			{utils.print_ptr_as_string(self.x7)}\n"
        res_str += f"{previous_struct}->x8			{utils.print_ptr_as_string(self.x8)}\n"
        res_str += f"{previous_struct}->x9			{utils.print_ptr_as_string(self.x9)}\n"
        res_str += f"{previous_struct}->x10			{utils.print_ptr_as_string(self.x10)}\n"
        res_str += f"{previous_struct}->x11			{utils.print_ptr_as_string(self.x11)}\n"
        res_str += f"{previous_struct}->x12			{utils.print_ptr_as_string(self.x12)}\n"
        res_str += f"{previous_struct}->x13			{utils.print_ptr_as_string(self.x13)}\n"
        res_str += f"{previous_struct}->x14			{utils.print_ptr_as_string(self.x14)}\n"
        res_str += f"{previous_struct}->x15			{utils.print_ptr_as_string(self.x15)}\n"
        res_str += f"{previous_struct}->x16			{utils.print_ptr_as_string(self.x16)}\n"
        res_str += f"{previous_struct}->x17			{utils.print_ptr_as_string(self.x17)}\n"
        res_str += f"{previous_struct}->x18			{utils.print_ptr_as_string(self.x18)}\n"
        res_str += f"{previous_struct}->x19			{utils.print_ptr_as_string(self.x19)}\n"
        res_str += f"{previous_struct}->x20			{utils.print_ptr_as_string(self.x20)}\n"
        res_str += f"{previous_struct}->x21			{utils.print_ptr_as_string(self.x21)}\n"
        res_str += f"{previous_struct}->x22			{utils.print_ptr_as_string(self.x22)}\n"
        res_str += f"{previous_struct}->x23			{utils.print_ptr_as_string(self.x23)}\n"
        res_str += f"{previous_struct}->x24			{utils.print_ptr_as_string(self.x24)}\n"
        res_str += f"{previous_struct}->x25			{utils.print_ptr_as_string(self.x25)}\n"
        res_str += f"{previous_struct}->x26			{utils.print_ptr_as_string(self.x26)}\n"
        res_str += f"{previous_struct}->x27			{utils.print_ptr_as_string(self.x27)}\n"
        res_str += f"{previous_struct}->x28			{utils.print_ptr_as_string(self.x28)}\n"
        res_str += f"{previous_struct}->fp			{utils.print_ptr_as_string(self.fp)}\n"
        res_str += f"{previous_struct}->lr			{utils.print_ptr_as_string(self.lr)}\n"
        res_str += f"{previous_struct}->sp			{utils.print_ptr_as_string(self.sp)}\n"
        res_str += f"{previous_struct}->pc			\
{sys_info.get_symbol(utils.print_ptr_as_string(self.pc))}\n"
        res_str += f"{previous_struct}->cpsr			{hex(self.cpsr)}\n"
        res_str += f"{previous_struct}->reserved             {hex(self.reserved)}\n"
        res_str += f"{previous_struct}->far			{utils.print_ptr_as_string(self.far)}\n"
        res_str += f"{previous_struct}->esr			{hex(self.esr)}\n"
        res_str += f"{previous_struct}->exception		{hex(self.exception)}\n"

        return res_str

# Voucher


class ThreadVoucher:
    def __init__(self, address):
        if address != const.NULL_PTR:
            self.iv_hash = utils.get_8_byte_at(address)
            self.iv_sum = utils.get_8_byte_at(address + 0x04)
            self.iv_refs = utils.get_8_byte_at(address + 0x08)
            self.iv_table_size = utils.get_8_byte_at(address + 0x0c)
            self.iv_inline_table = utils.get_8_byte_at(address + 0x10)
            self.iv_tabl = utils.get_8_byte_at(address + 0x30)
            self.iv_port = utils.get_8_byte_at(address + 0x38)
            self.iv_hash_link = utils.get_8_byte_at(address + 0x40)

    def print_voucher_info(self):
        res_str = ""
        res_str += f"iv_hash			{hex(self.iv_hash)}\n"
        res_str += f"iv_sum			{hex(self.iv_sum)}\n"
        res_str += f"iv_refs			{hex(self.iv_refs)}\n"
        res_str += f"iv_table_size		{hex(self.iv_table_size)}\n"
        res_str += f"iv_inline_table	        {hex(self.iv_inline_table)}\n"
        # res_str += f"iv_table		{hex(self.iv_table)}\n" #TODO
        res_str += f"iv_port			{hex(self.iv_port)}\n"
        res_str += f"iv_hash_link		{hex((self.iv_hash_link))}\n"
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
                self.task_ptr = sys_info.get_current_task_ptr()

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
        else:
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
        else:
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
        if len(task.bsdinfo_object.bsd_name) > max_length:
            max_length = len(task.bsdinfo_object.bsd_name)
    return max_length

# TODO make generic!


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
    res_str += f'U/K| PID | {"NAME":^{max_length_proc}} | TID |     \
THREAD_PTR     | {"CONTINUATION":^{max_length_cont}} | {"NEXT_PC*":^{max_length_pc}} |'
    return res_str
