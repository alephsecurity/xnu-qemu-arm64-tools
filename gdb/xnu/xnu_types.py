from xnu.constants import NextPcHelpOffsets, IPCSpaceOffsets, IPCEntryOffsets, IPCObjectOffsets
from xnu.constants import ThreadOffsets, BSDInfoOffsets, TaskOffsets, IPCPortOffsets, ThrdItrType, IO_BITS_TYPES
from xnu.constants import NULL_PTR, GLOBAL_THREADS_PTR, GLOBAL_TASKS_PTR, IE_BITS_TYPE_MASK, IO_BITS_KOTYPE
from xnu.utils import get_8_byte_at, get_4_byte_at, print_val, get_string_at, print_ptr_as_string
from xnu.sys_info import get_current_task_ptr, get_current_thread_ptr, is_user_thread, get_symbol, is_valid_ptr
import gdb


# THREAD
class Thread:
    def __init__(self, address):
        if address != NULL_PTR:
            self.address = address
            self.task_ptr = get_8_byte_at(address + ThreadOffsets.TASK.value)
            self.tid = get_8_byte_at(address + ThreadOffsets.THREAD_ID.value)
            self.continuation = get_8_byte_at(
                address + ThreadOffsets.CONTINUATION.value)
            self.global_threads_ptr = address + ThreadOffsets.GLOBAL_THREADS.value
            self.curr_task_threads_ptr = address + ThreadOffsets.TASK_THREADS.value
            self.ucontext_data = get_8_byte_at(
                address + ThreadOffsets.CONTEXT_USER_DATA_PTR.value)
            self.kernel_stack_ptr = get_8_byte_at(
                address + ThreadOffsets.KSTACK_PTR.value)
            self.voucher_ptr = get_8_byte_at(
                address + ThreadOffsets.VOUCHER_PTR.value)

            # Meta Data
            self.next_pc = NULL_PTR
            if self.is_currect():
                self.next_pc = print_val('$pc')
            elif self.ucontext_data != NULL_PTR:
                user_saved_state = ThreadSavedState(self.ucontext_data)
                self.next_pc = user_saved_state.pc
            elif self.kernel_stack_ptr != NULL_PTR:
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
        next_to_thread_invoke = get_8_byte_at(
            stack_ptr_thread_invoke + NextPcHelpOffsets.STORED_LR_IN_THREAD_INVOKE_FRAME.value)
        if next_to_thread_invoke == NextPcHelpOffsets.NEXT_IN_THREAD_RUN.value:
            # we came to thread invoke from thread_run.
            # The next LR will point to the function that we want
            kernel_next_pc = get_8_byte_at(
                stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x38)
        elif next_to_thread_invoke == NextPcHelpOffsets.NEXT_IN_THREAD_BLOCK.value:
            # we came to thread invoke from thread_block.
            # The next LR will point to the function that we want or to exception return
            kernel_next_pc = get_8_byte_at(
                stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x48)
        else:
            raise gdb.GdbError(
                "Something went wrong with getting the next pc, maybe running on another kernel?")

        # Now we can check whether the next running function is exception_return.
        # If so, we need to go one more frame further
        if kernel_next_pc == NextPcHelpOffsets.EXEPTION_RETURN_PTR.value:
            # From the kernel code (Switch_context) we know that the pointer to
            # saved state is stored in x21
            next_x21_ptr = get_8_byte_at(
                stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value +
                NextPcHelpOffsets.X21_IN_THREAD_INVOKE_FRAME.value)
            saved_state_exception_return = ThreadSavedState(next_x21_ptr)
            # now we have the saved state we can get the PC
            pc_from_saved_state = saved_state_exception_return.pc
            kernel_next_pc = pc_from_saved_state
        return kernel_next_pc

    def print_thead_info_short(self, max_length_proc, max_length_cont, max_length_pc):
        res_str = ""
        is_user = True if self.ucontext_data != NULL_PTR else False
        is_current = True if self.address == get_current_thread_ptr() else False
        res_str += '*' if is_current else ' '
        res_str += 'U |' if is_user else 'K |'
        res_str += f" [{self.task_object.bsdinfo_object.bsd_pid}] |"
        res_str += f" {self.task_object.bsdinfo_object.bsd_name:<{max_length_proc}} |"
        res_str += f" {self.tid} | {hex(self.address)} |"
        res_str += f' {"N/A":^{max_length_cont}} |' if self.continuation == NULL_PTR \
            else f" {get_symbol(hex(self.continuation)):^{max_length_cont}} |"
        res_str += f' {"N/A":^{max_length_pc}} |' if self.next_pc == NULL_PTR \
            else f" {get_symbol(hex(self.next_pc)):^{max_length_pc}} |"

        return res_str

    def print_thread_info_long(self):
        res_str = ""
        if is_user_thread(self):
            res_str += "This is a user space thread\n\n"
        else:
            res_str += "This is a kernel thread\n\n"

        res_str += f"Next pc: {get_symbol(hex(self.next_pc))}\n\n" \
            if self.next_pc != NULL_PTR else ""
        res_str += f"thread->task                           {print_ptr_as_string(self.task_ptr)}\n"
        if self.task_object:
            res_str += f"thread->task->bsd_info\
                {print_ptr_as_string(self.task_object.bsd_info_ptr)}\n"
        if self.task_object.bsd_info_ptr:
            res_str += f"thread->task->bsd_info->bsd_name\
                {self.task_object.bsdinfo_object.bsd_name}\n"
            res_str += f"thread->task->bsd_info->bsd_pid\
                {print_ptr_as_string(self.task_object.bsdinfo_object.bsd_pid)}\n"
        res_str += f"thread->tid                            {str(self.tid)}\n"
        res_str += f"thread->continuation\
            {print_ptr_as_string(self.continuation)}\n"
        res_str += f"thread->ucontext_data\
            {print_ptr_as_string(self.ucontext_data)}\n"
        if self.ucontext_data:
            saved_state = ThreadSavedState(self.ucontext_data)
            res_str += saved_state.print_saved_state("thread->ucontext_data")
        res_str += f"thread->kstackptr\
            {print_ptr_as_string(self.kernel_stack_ptr)}\n"
        if self.kernel_stack_ptr:
            saved_state = ThreadSavedState(self.kernel_stack_ptr)
            res_str += saved_state.print_saved_state("thread->kstackptr")
        res_str += f"thread->voucher_ptr\
            {print_ptr_as_string(self.voucher_ptr)}\n"

        return res_str

    def is_currect(self):
        return self.address == get_current_thread_ptr()


# BSD_INFO
class BsdInfo:
    def __init__(self, address):
        if address != NULL_PTR:
            self.bsd_pid = get_4_byte_at(
                address + BSDInfoOffsets.PID_IN_BSD_INFO.value)
            self.bsd_name = get_string_at(
                address + BSDInfoOffsets.NAME_INBSD_INFO.value)
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")

# ipc_space


class IPCSpace:
    def __init__(self, address):
        if address != NULL_PTR:
            self.is_table = get_8_byte_at(
                address + IPCSpaceOffsets.IS_TABLE.value)
            self.is_table_size = get_4_byte_at(
                address + IPCSpaceOffsets.IS_TABLE_SIZE.value)
            self.is_table_free = get_4_byte_at(
                address + IPCSpaceOffsets.IS_TABLE_FREE.value)
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
        if address != NULL_PTR:
            self.address = address
            self.ie_object = get_8_byte_at(address)
            self.ie_bits = get_4_byte_at(
                address + IPCEntryOffsets.IE_BITS.value)
            self.ie_index = get_4_byte_at(
                address + IPCEntryOffsets.IE_INDEX.value)
            self.index = get_4_byte_at(address + IPCEntryOffsets.INDEX.value)

            if self.ie_object:
                self.ie_object_object = IPCObject(self.ie_object)
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Entry {address}")

    def print_ipc_entry_info(self):
        res_str = ""
        res_str += f"ipc_entry->ie_object = {print_ptr_as_string(self.ie_object)}\n"
        res_str += f"ipc_entry->ie_bits = {hex(self.ie_bits)}\n"
        res_str += f"ipc_entry->ie_index = {hex(self.ie_index)}\n"
        res_str += f"ipc_entry->ie_next = {hex(self.index)}\n"
        return res_str


class IPCObject:
    def __init__(self, address):
        if address != NULL_PTR:
            self.io_bits = get_4_byte_at(address)  # parse it from ipc_object
            self.io_references = get_4_byte_at(
                address + IPCObjectOffsets.IO_REFS.value)
            self.io_lock_data_1 = get_8_byte_at(
                address + IPCObjectOffsets.IO_LOCK_DATA.value)
            self.io_lock_data_2 = get_8_byte_at(
                address + IPCObjectOffsets.IO_LOCK_DATA.value + 0x08)  # next
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Object {address}")

    def print_ipc_object_info(self):
        res_str = ""
        res_str += f"ip_object->io_bits {IO_BITS_TYPES[self.io_bits & IO_BITS_KOTYPE]}\n"
        res_str += f"ip_object->io_references   {hex(self.io_references)}\n"
        res_str += f"ip_object->io_lock_data[0] {hex(self.io_lock_data_1)}\n"
        res_str += f"ip_object->io_lock_data[1] {hex(self.io_lock_data_2)}\n"
        return res_str


class IPCPort:
    def __init__(self, address):
        if address != NULL_PTR:
            self.ip_object_object = IPCObject(address)
            self.ip_messages = get_8_byte_at(
                address + IPCPortOffsets.IP_MSG.value)
            self.data = get_8_byte_at(address + IPCPortOffsets.DATA.value)
            self.kdata = get_8_byte_at(address + IPCPortOffsets.KDATA.value)
            self.kdata2 = get_8_byte_at(address + IPCPortOffsets.KDATA2.value)
            self.ip_context = get_8_byte_at(
                address + IPCPortOffsets.IP_CTXT.value)
            self.ip_sprequests = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 0))
            self.ip_spimportant = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 1))
            self.ip_impdonation = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 2))
            self.ip_tempowner = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 3))
            self.ip_guarded = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 4))
            self.ip_strict_guard = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 5))
            self.ip_specialreply = (
                get_4_byte_at(address + IPCPortOffsets.IP_SPREQ.value) & (1 << 6))
            self.ip_sync_link_state = (get_4_byte_at(
                address + IPCPortOffsets.IP_SPREQ.value) & (0x000001ff))
            self.ip_impcount = (get_8_byte_at(
                address + IPCPortOffsets.IP_SPREQ.value) & (0xfffffe00))
            self.ip_mscount = get_8_byte_at(
                address + IPCPortOffsets.IP_MSCNT.value)
            self.ip_srights = get_8_byte_at(
                address + IPCPortOffsets.IP_SRIGHTS.value)
            self.ip_sorights = get_8_byte_at(
                address + IPCPortOffsets.IP_SORIGHTS.value)

    def print_ipc_port_info(self):
        res_str = ""
        res_str += self.ip_object_object.print_ipc_object_info()
        res_str += f"ipc_port->ip_messages       {self.ip_messages }\n"
        res_str += f"ipc_port->data       {print_ptr_as_string(self.data) }\n"
        res_str += f"ipc_port->kdata       {print_ptr_as_string(self.kdata) }\n"
        res_str += f"ipc_port->kdata2       {print_ptr_as_string(self.kdata2 )}\n"
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

# TASK


class Task:
    def __init__(self, address):
        if address != NULL_PTR:
            self.address = address
            self.task_lst_ptr = address + TaskOffsets.TASK_NEXT.value
            self.threads_lst_ptr = address + TaskOffsets.THREAD_LST_FROM_TASK.value
            self.bsd_info_ptr = get_8_byte_at(
                address + TaskOffsets.BSD_INFO.value)
            self.itk_self = get_8_byte_at(address + TaskOffsets.ITK_SELF.value)
            self.ipc_space = get_8_byte_at(
                address + TaskOffsets.IPC_SPACE.value)

            self.ipc_space_object = IPCSpace(self.ipc_space)
            self.bsdinfo_object = BsdInfo(self.bsd_info_ptr)
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")

    def print_task_info_short(self):
        res_str = ""
        is_current = True if self.address == get_current_task_ptr() else False
        res_str += '*' if is_current else ' '
        res_str += f" [{self.bsdinfo_object.bsd_pid}] | {self.bsdinfo_object.bsd_name:<15} |"
        res_str += f"  {hex(self.address)} "

        return res_str

    def print_task_info_long(self):
        res_str = "\n"
        res_str += f"task->bsd_info = {print_ptr_as_string(self.bsd_info_ptr)}\n"
        res_str += f"task->itk_self = {print_ptr_as_string(self.itk_self)}\n"
        res_str += f"task->ipc_space = {print_ptr_as_string(self.ipc_space)}\n"
        res_str += f"task->ipc_space->is_table = \
            {print_ptr_as_string(self.ipc_space_object.is_table)}\n"
        return res_str

# Saved State


class ThreadSavedState:
    def __init__(self, address):
        if address != NULL_PTR:
            address += 0x08  # skip arm_state_hdr_t ash at arm_saved_state
            self.x0 = get_8_byte_at(address)
            self.x1 = get_8_byte_at(address + 0x08)
            self.x2 = get_8_byte_at(address + 0x10)
            self.x3 = get_8_byte_at(address + 0x18)
            self.x4 = get_8_byte_at(address + 0x20)
            self.x5 = get_8_byte_at(address + 0x28)
            self.x6 = get_8_byte_at(address + 0x30)
            self.x7 = get_8_byte_at(address + 0x38)
            self.x8 = get_8_byte_at(address + 0x40)
            self.x9 = get_8_byte_at(address + 0x48)
            self.x10 = get_8_byte_at(address + 0x50)
            self.x11 = get_8_byte_at(address + 0x58)
            self.x12 = get_8_byte_at(address + 0x60)
            self.x13 = get_8_byte_at(address + 0x68)
            self.x14 = get_8_byte_at(address + 0x70)
            self.x15 = get_8_byte_at(address + 0x78)
            self.x16 = get_8_byte_at(address + 0x80)
            self.x17 = get_8_byte_at(address + 0x88)
            self.x18 = get_8_byte_at(address + 0x90)
            self.x19 = get_8_byte_at(address + 0x98)
            self.x20 = get_8_byte_at(address + 0xa0)
            self.x21 = get_8_byte_at(address + 0xa8)
            self.x22 = get_8_byte_at(address + 0xb0)
            self.x23 = get_8_byte_at(address + 0xb8)
            self.x24 = get_8_byte_at(address + 0xc0)
            self.x25 = get_8_byte_at(address + 0xc8)
            self.x26 = get_8_byte_at(address + 0xd0)
            self.x27 = get_8_byte_at(address + 0xd8)
            self.x28 = get_8_byte_at(address + 0xe0)
            self.fp = get_8_byte_at(address + 0xe8)
            self.lr = get_8_byte_at(address + 0xf0)
            self.sp = get_8_byte_at(address + 0xf8)
            self.pc = get_8_byte_at(address + 0x100)
            self.cpsr = get_4_byte_at(address + 0x108)
            self.reserved = get_4_byte_at(address + 0x10c)
            self.far = get_8_byte_at(address + 0x110)
            self.esr = get_4_byte_at(address + 0x118)
            self.exception = get_4_byte_at(address + 0x11c)

    def print_saved_state(self, previous_struct):
        res_str = ""
        res_str += f"{previous_struct}->x0			{print_ptr_as_string(self.x0)}\n"
        res_str += f"{previous_struct}->x1			{print_ptr_as_string(self.x1)}\n"
        res_str += f"{previous_struct}->x2			{print_ptr_as_string(self.x2)}\n"
        res_str += f"{previous_struct}->x3			{print_ptr_as_string(self.x3)}\n"
        res_str += f"{previous_struct}->x4			{print_ptr_as_string(self.x4)}\n"
        res_str += f"{previous_struct}->x5			{print_ptr_as_string(self.x5)}\n"
        res_str += f"{previous_struct}->x6			{print_ptr_as_string(self.x6)}\n"
        res_str += f"{previous_struct}->x7			{print_ptr_as_string(self.x7)}\n"
        res_str += f"{previous_struct}->x8			{print_ptr_as_string(self.x8)}\n"
        res_str += f"{previous_struct}->x9			{print_ptr_as_string(self.x9)}\n"
        res_str += f"{previous_struct}->x10			{print_ptr_as_string(self.x10)}\n"
        res_str += f"{previous_struct}->x11			{print_ptr_as_string(self.x11)}\n"
        res_str += f"{previous_struct}->x12			{print_ptr_as_string(self.x12)}\n"
        res_str += f"{previous_struct}->x13			{print_ptr_as_string(self.x13)}\n"
        res_str += f"{previous_struct}->x14			{print_ptr_as_string(self.x14)}\n"
        res_str += f"{previous_struct}->x15			{print_ptr_as_string(self.x15)}\n"
        res_str += f"{previous_struct}->x16			{print_ptr_as_string(self.x16)}\n"
        res_str += f"{previous_struct}->x17			{print_ptr_as_string(self.x17)}\n"
        res_str += f"{previous_struct}->x18			{print_ptr_as_string(self.x18)}\n"
        res_str += f"{previous_struct}->x19			{print_ptr_as_string(self.x19)}\n"
        res_str += f"{previous_struct}->x20			{print_ptr_as_string(self.x20)}\n"
        res_str += f"{previous_struct}->x21			{print_ptr_as_string(self.x21)}\n"
        res_str += f"{previous_struct}->x22			{print_ptr_as_string(self.x22)}\n"
        res_str += f"{previous_struct}->x23			{print_ptr_as_string(self.x23)}\n"
        res_str += f"{previous_struct}->x24			{print_ptr_as_string(self.x24)}\n"
        res_str += f"{previous_struct}->x25			{print_ptr_as_string(self.x25)}\n"
        res_str += f"{previous_struct}->x26			{print_ptr_as_string(self.x26)}\n"
        res_str += f"{previous_struct}->x27			{print_ptr_as_string(self.x27)}\n"
        res_str += f"{previous_struct}->x28			{print_ptr_as_string(self.x28)}\n"
        res_str += f"{previous_struct}->fp			{print_ptr_as_string(self.fp)}\n"
        res_str += f"{previous_struct}->lr			{print_ptr_as_string(self.lr)}\n"
        res_str += f"{previous_struct}->sp			{print_ptr_as_string(self.sp)}\n"
        res_str += f"{previous_struct}->pc			{get_symbol(print_ptr_as_string(self.pc))}\n"
        res_str += f"{previous_struct}->cpsr			{hex(self.cpsr)}\n"
        res_str += f"{previous_struct}->reserved             {hex(self.reserved)}\n"
        res_str += f"{previous_struct}->far			{print_ptr_as_string(self.far)}\n"
        res_str += f"{previous_struct}->esr			{hex(self.esr)}\n"
        res_str += f"{previous_struct}->exception		{hex(self.exception)}\n"

        return res_str

# Voucher


class ThreadVoucher:
    def __init__(self, address):
        if address != NULL_PTR:
            self.iv_hash = get_8_byte_at(address)
            self.iv_sum = get_8_byte_at(address + 0x04)
            self.iv_refs = get_8_byte_at(address + 0x08)
            self.iv_table_size = get_8_byte_at(address + 0x0c)
            self.iv_inline_table = get_8_byte_at(address + 0x10)
            self.iv_tabl = get_8_byte_at(address + 0x30)
            self.iv_port = get_8_byte_at(address + 0x38)
            self.iv_hash_link = get_8_byte_at(address + 0x40)

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
            self.type = ThrdItrType.GLOBAL
        else:
            self.type = ThrdItrType.TASK
            if task != NULL_PTR and task is not None:
                self.task_ptr = task
            else:
                self.task_ptr = get_current_task_ptr()

    def __iter__(self):
        if self.type == ThrdItrType.GLOBAL:
            self.next_thread_ptr = get_8_byte_at(GLOBAL_THREADS_PTR)
            self.stop_contition = GLOBAL_THREADS_PTR
        else:
            relevant_task = Task(self.task_ptr)
            self.next_thread_ptr = get_8_byte_at(relevant_task.threads_lst_ptr)
            self.stop_contition = self.task_ptr + TaskOffsets.THREAD_LST_FROM_TASK.value
        return self

    def __next__(self):
        if self.next_thread_ptr != self.stop_contition:
            self.result = Thread(self.next_thread_ptr)
            if self.type == ThrdItrType.GLOBAL:
                self.next_thread_ptr = get_8_byte_at(
                    self.result.global_threads_ptr)
            else:
                self.next_thread_ptr = get_8_byte_at(
                    self.result.curr_task_threads_ptr)
            return self.result
        else:
            raise StopIteration


class TasksIterator:
    def __init__(self):
        self.stop_contition = GLOBAL_TASKS_PTR
        self.next_task_ptr = get_8_byte_at(GLOBAL_TASKS_PTR)
        self.result = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_task_ptr != self.stop_contition:
            self.result = Task(self.next_task_ptr)
            self.next_task_ptr = get_8_byte_at(self.result.task_lst_ptr)
            return self.result
        else:
            raise StopIteration


class IPCEntryIterator:
    def __init__(self, address):
        if is_valid_ptr(address):
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
            if (result.ie_bits & IE_BITS_TYPE_MASK) != 0:
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
        if len(get_symbol(print_ptr_as_string(thread.continuation))) > max_length:
            max_length = len(get_symbol(
                print_ptr_as_string(thread.continuation)))
    return max_length


def get_max_length_pc_name():
    max_length = 0
    for thread in iter(ThreadsIterator(True)):
        if len(get_symbol(print_ptr_as_string(thread.next_pc))) > max_length:
            max_length = len(get_symbol(print_ptr_as_string(thread.next_pc)))
    return max_length


def get_thead_info_title(max_length_proc, max_length_cont, max_length_pc):
    res_str = ""
    res_str += f'U/K| PID | {"NAME":^{max_length_proc}} | TID |     \
THREAD_PTR     | {"CONTINUATION":^{max_length_cont}} | {"NEXT_PC*":^{max_length_pc}} |'
    return res_str
