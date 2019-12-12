from xnu.constants import NextPcHelpOffsets ,IPCSpaceOffsets,IPCEntryOffsets,IPCObjectOffsets
from xnu.constants import ThreadOffsets,BSDInfoOffsets, TaskOffsets, IPCPortOffsets,ThrdItrType, io_bits_types
from xnu.constants import  NULL_PTR, GLOBAL_THREADS_PTR, GLOBAL_TASKS_PTR, NULL_PTR_STR, IE_BITS_TYPE_MASK, IO_BITS_KOTYPE
from xnu.utils import getPointerAt,getLongAt,getIntAt,printValueOf,getStringAt,printPtrAsString
from xnu.sys_info import getCurrentTaskPtr, getCurrentThreadPtr, isUserThread,getSymbol, isValidPtr
import traceback
import gdb


#THREAD
class Thread:
    def __init__(self, address):
        if address != NULL_PTR:
            self.address = address
            self.task_ptr       = getPointerAt(address + ThreadOffsets.TASK.value)
            self.tid            = getLongAt(address + ThreadOffsets.THREAD_ID.value)
            self.continuation   = getPointerAt(address + ThreadOffsets.CONTINUATION.value)
            self.global_threads_ptr = address + ThreadOffsets.GLOBAL_THREADS.value
            self.curr_task_threads_ptr = address + ThreadOffsets.TASK_THREADS.value
            self.uContextData       = getPointerAt(address + ThreadOffsets.CONTEXT_USER_DATA_PTR.value)
            self.kernel_stack_ptr   = getPointerAt(address + ThreadOffsets.KSTACK_PTR.value)
            self.voucher_ptr    = getPointerAt(address + ThreadOffsets.VOUCHER_PTR.value)
            
            #Meta Data
            self.next_pc = NULL_PTR
            if self.isCurrect():
                self.next_pc = printValueOf('$pc')
            elif self.uContextData != NULL_PTR:
                userSavedState = ThreadSavedState(self.uContextData)
                self.next_pc = userSavedState.pc
            elif self.kernel_stack_ptr != NULL_PTR:
                self.next_pc = self.getKernelNextPc()

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
    # From there we will check whether the next methon is exception_return (i.e context switch came from ecxeption).
    # If not we will return the next pc (LR) to be called.
    # if the next function is exeption_return we will go one more frame further.
    def getKernelNextPc(self):
        #Get SP of thread_invoke. From Switch_context's frame
        kernel_saved_state = ThreadSavedState(self.kernel_stack_ptr)
        stack_ptr_thread_invoke = kernel_saved_state.sp
        #we are in thread_invoke context frame. Look at LR and see if the next function is thread_invoke or thread_run
        next_to_thread_invoke = getPointerAt(stack_ptr_thread_invoke + NextPcHelpOffsets.STORED_LR_IN_THREAD_INVOKE_FRAME.value)
        if next_to_thread_invoke == NextPcHelpOffsets.NEXT_IN_THREAD_RUN.value:
            #we came to thread invoke from thread_run. The next LR will point to the function that we want
            kernel_next_pc = getPointerAt(stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x38)
        elif next_to_thread_invoke == NextPcHelpOffsets.NEXT_IN_THREAD_BLOCK.value:
            #we came to thread invoke from thread_block. The next LR will point to the function that we want or to exception return
            kernel_next_pc = getPointerAt(stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + 0x48)
        else:
            raise gdb.GdbError("Something went wrong with getting the next pc, maybe running on another kernel?")
        
        #Now we can check whether the next running function is exception_return. If so, we need to go one more frame further
        if kernel_next_pc == NextPcHelpOffsets.EXEPTION_RETURN_PTR.value:
            #From the kernel code (Switch_context) we know that the pointer to saved state is stored in x21
            next_x21_ptr = getPointerAt(stack_ptr_thread_invoke + NextPcHelpOffsets.THREAD_INVOKE_FRAME_SIZE.value + NextPcHelpOffsets.X21_IN_THREAD_INVOKE_FRAME.value)
            saved_state_exception_return = ThreadSavedState(next_x21_ptr)
            #now we have the saved state we can get the PC
            pc_from_saved_state = saved_state_exception_return.pc
            kernel_next_pc = pc_from_saved_state
        return kernel_next_pc

    def printTheadInfoShort(self,max_length_proc,max_length_cont, max_length_pc):
        res_str = ""
        is_user = True if self.uContextData != NULL_PTR else False
        is_current = True if self.address  == getCurrentThreadPtr() else False
        res_str += '*' if is_current else ' '
        res_str += 'U |' if is_user else 'K |'
        res_str += f" [{self.task_object.bsdinfo_object.bsd_pid}] | {self.task_object.bsdinfo_object.bsd_name:<{max_length_proc}} |"
        res_str += f" {self.tid} | {hex(self.address)} |"
        res_str += f' {"N/A":^{max_length_cont}} |' if self.continuation == NULL_PTR else f" {getSymbol(hex(self.continuation)):^{max_length_cont}} |"
        res_str += f' {"N/A":^{max_length_pc}} |' if self.next_pc == NULL_PTR else f" {getSymbol(hex(self.next_pc)):^{max_length_pc}} |"

        return res_str

    def printThreadInfoLong(self):
        res_str = ""
        if isUserThread(self):
            res_str += "This is a user space thread\n\n"
        else:
            res_str += "This is a kernel thread\n\n"

        res_str += f"Next pc: {getSymbol(hex(self.next_pc))}\n\n" if self.next_pc != NULL_PTR else ""
        res_str += f"thread->task                           {printPtrAsString(self.task_ptr)}\n"
        if self.task_object:
            res_str += f"thread->task->bsd_info                 {printPtrAsString(self.task_object.bsd_info_ptr)}\n"
        if self.task_object.bsd_info_ptr:
            res_str += f"thread->task->bsd_info->bsd_name       {self.task_object.bsdinfo_object.bsd_name}\n"
            res_str += f"thread->task->bsd_info->bsd_pid        {printPtrAsString(self.task_object.bsdinfo_object.bsd_pid)}\n"
        res_str += f"thread->tid                            {str(self.tid)}\n"
        res_str += f"thread->continuation                   {printPtrAsString(self.continuation)}\n"
        res_str += f"thread->uContextData                   {printPtrAsString(self.uContextData)}\n"
        if self.uContextData:
            saved_state = ThreadSavedState(self.uContextData)
            res_str += saved_state.printSavedState("thread->uContextData")
        res_str += f"thread->kstackptr                      {printPtrAsString(self.kernel_stack_ptr)}\n"
        if self.kernel_stack_ptr:
            saved_state = ThreadSavedState(self.kernel_stack_ptr)
            res_str += saved_state.printSavedState("thread->kstackptr")
        res_str += f"thread->voucher_ptr                    {printPtrAsString(self.voucher_ptr)}\n"

        return res_str

    def isCurrect(self):
        return self.address == getCurrentThreadPtr()



#BSD_INFO
class BsdInfo:
    def __init__(self, address):
        if address != NULL_PTR:
            self.bsd_pid = getIntAt(address + BSDInfoOffsets.PID_IN_BSD_INFO.value)
            self.bsd_name = getStringAt(address + BSDInfoOffsets.NAME_INBSD_INFO.value)
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")

#ipc_space
class IPCSpace:
    def __init__(self, address):
        if address != NULL_PTR:
            self.is_table  = getPointerAt(address +  IPCSpaceOffsets.IS_TABLE.value)
            self.is_table_size = getIntAt(address + IPCSpaceOffsets.IS_TABLE_SIZE.value)
            self.is_table_free = getIntAt(address + IPCSpaceOffsets.IS_TABLE_FREE.value)
        else:
            raise gdb.GdbError(f"Null pointer for {__name__}")
    def printIPCSpaceInfo(self):
        res_str = ""
        res_str += f"ipc_space->is_table {hex(self.is_table)}\n"
        res_str += f"ipc_space->is_table_size {self.is_table_size} - (first reserved)\n"
        res_str += f"ipc_space->is_table_free {self.is_table_free}\n"
        return res_str


class IPCEntry:
    def __init__(self, address):
        if address != NULL_PTR:
            self.address = address
            self.ie_object = getPointerAt(address)
            self.ie_bits = getIntAt(address + IPCEntryOffsets.IE_BITS.value)
            self.ie_index = getIntAt(address + IPCEntryOffsets.IE_INDEX.value)
            self.index =  getIntAt(address + IPCEntryOffsets.INDEX.value)

            if self.ie_object:
                self.ie_object_object = IPCObject(self.ie_object)
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Entry {address}")

    def printIPCEntryInfo(self):
        res_str = ""
        res_str += f"ipc_entry->ie_object = {printPtrAsString(self.ie_object)}\n"
        res_str += f"ipc_entry->ie_bits = {hex(self.ie_bits)}\n"
        res_str += f"ipc_entry->ie_index = {hex(self.ie_index)}\n"
        res_str += f"ipc_entry->ie_next = {hex(self.index)}\n"
        return res_str

class IPCObject:
    def __init__(self,address):
        if address != NULL_PTR:
            self.io_bits = getIntAt(address) #parse it from ipc_object
            self.io_references = getIntAt(address + IPCObjectOffsets.IO_REFS.value)
            self.io_lock_data_1 = getPointerAt(address + IPCObjectOffsets.IO_LOCK_DATA.value)
            self.io_lock_data_2 = getPointerAt(address + IPCObjectOffsets.IO_LOCK_DATA.value + 0x08) #next
        else:
            raise gdb.GdbError(f"Wrong pointer to IPC Object {address}")

    def printIPCObjectInfo(self):
        res_str = ""
        res_str += f"ip_object->io_bits {io_bits_types[self.io_bits & IO_BITS_KOTYPE]}\n"
        res_str += f"ip_object->io_references   {hex(self.io_references)}\n"
        res_str += f"ip_object->io_lock_data[0] {hex(self.io_lock_data_1)}\n"
        res_str += f"ip_object->io_lock_data[1] {hex(self.io_lock_data_2)}\n"
        return res_str


class IPCPort:
    def __init__(self, address):
        if address != NULL_PTR:
            self.ip_object_object = IPCObject(address)
            self.ip_messages = getPointerAt(address + IPCPortOffsets.IP_MSG.value)
            self.data = getPointerAt(address + IPCPortOffsets.DATA.value)
            self.kdata = getPointerAt(address + IPCPortOffsets.KDATA.value)
            self.kdata2 = getPointerAt(address + IPCPortOffsets.KDATA2.value)
            self.ip_context = getPointerAt(address + IPCPortOffsets.IP_CTXT.value)
            self.ip_sprequests = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value)  & (1<<0))
            self.ip_spimportant = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<1))
            self.ip_impdonation = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<2))
            self.ip_tempowner = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<3))
            self.ip_guarded = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<4))
            self.ip_strict_guard = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<5))
            self.ip_specialreply = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (1<<6))
            self.ip_sync_link_state = (getIntAt(address + IPCPortOffsets.IP_SPREQ.value) & (0x000001ff))
            self.ip_impcount = (getPointerAt(address + IPCPortOffsets.IP_SPREQ.value) & (0xfffffe00))
            self.ip_mscount = getPointerAt(address + IPCPortOffsets.IP_MSCNT.value)
            self.ip_srights = getPointerAt(address + IPCPortOffsets.IP_SRIGHTS.value)
            self.ip_sorights = getPointerAt(address + IPCPortOffsets.IP_SORIGHTS.value)
    
    def printIPCPortInfo(self):
        res_str = ""
        res_str += self.ip_object_object.printIPCObjectInfo()
        res_str += f"ipc_port->ip_messages       {self.ip_messages }\n"
        res_str += f"ipc_port->data       {printPtrAsString(self.data) }\n"
        res_str += f"ipc_port->kdata       {printPtrAsString(self.kdata) }\n"
        res_str += f"ipc_port->kdata2       {printPtrAsString(self.kdata2 )}\n"
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

#TASK
class Task:
    def __init__(self, address):
        if address != NULL_PTR:
            self.address = address
            self.task_lst_ptr = address + TaskOffsets.TASK_NEXT.value
            self.threads_lst_ptr =  address + TaskOffsets.THREAD_LST_FROM_TASK.value
            self.bsd_info_ptr = getPointerAt(address + TaskOffsets.BSD_INFO.value)
            self.itk_self = getPointerAt(address +  TaskOffsets.ITK_SELF.value)
            self.ipc_space = getPointerAt(address +  TaskOffsets.IPC_SPACE.value)

            self.ipc_space_object = IPCSpace(self.ipc_space)
            self.bsdinfo_object = BsdInfo(self.bsd_info_ptr)
        else:
            raise gdb.GdbError(f"Null pointer in {__name__}")

    def printTaskInfoShort(self):
        res_str = ""
        is_current = True if self.address  == getCurrentTaskPtr() else False
        res_str += '*' if is_current else ' '
        res_str += f" [{self.bsdinfo_object.bsd_pid}] | {self.bsdinfo_object.bsd_name:<15} |"
        res_str += f"  {hex(self.address)} "

        return res_str

    def printTaskInfoLong(self):
        res_str = "\n"
        res_str += f"task->bsd_info = {printPtrAsString(self.bsd_info_ptr)}\n"
        res_str += f"task->itk_self = {printPtrAsString(self.itk_self)}\n"
        res_str += f"task->ipc_space = {printPtrAsString(self.ipc_space)}\n"
        res_str += f"task->ipc_space->is_table = {printPtrAsString(self.ipc_space_object.is_table)}\n"

        return res_str
        
#Saved State
class ThreadSavedState:
    def __init__(self, address):
        if address != NULL_PTR:
            address += 0x08 # skip arm_state_hdr_t ash at arm_saved_state
            self.x0 =  getPointerAt(address)
            self.x1 =  getPointerAt(address + 0x08 )
            self.x2 =  getPointerAt(address + 0x10 )
            self.x3 =  getPointerAt(address + 0x18 )
            self.x4 =  getPointerAt(address + 0x20 )
            self.x5 =  getPointerAt(address + 0x28 )
            self.x6 =  getPointerAt(address + 0x30 )
            self.x7 =  getPointerAt(address + 0x38 )
            self.x8 =  getPointerAt(address + 0x40 )
            self.x9 =  getPointerAt(address + 0x48 )
            self.x10 =  getPointerAt(address + 0x50 )
            self.x11 =  getPointerAt(address + 0x58 )
            self.x12 =  getPointerAt(address + 0x60 )
            self.x13 =  getPointerAt(address + 0x68 )
            self.x14 =  getPointerAt(address + 0x70 )
            self.x15 =  getPointerAt(address + 0x78 )
            self.x16 =  getPointerAt(address + 0x80 )
            self.x17 =  getPointerAt(address + 0x88 )
            self.x18 =  getPointerAt(address + 0x90 )
            self.x19 =  getPointerAt(address + 0x98 )
            self.x20 =  getPointerAt(address + 0xa0 )
            self.x21 =  getPointerAt(address + 0xa8 )
            self.x22 =  getPointerAt(address + 0xb0 )
            self.x23 =  getPointerAt(address + 0xb8 )
            self.x24 =  getPointerAt(address + 0xc0 )
            self.x25 =  getPointerAt(address + 0xc8 )
            self.x26 =  getPointerAt(address + 0xd0 )
            self.x27 =  getPointerAt(address + 0xd8 )
            self.x28 =  getPointerAt(address + 0xe0 )
            self.fp = getPointerAt(address + 0xe8 )
            self.lr = getPointerAt(address + 0xf0 )
            self.sp = getPointerAt(address + 0xf8 )
            self.pc = getPointerAt(address + 0x100 )
            self.cpsr = getIntAt(address + 0x108 )
            self.reserved = getIntAt(address + 0x10c )
            self.far = getPointerAt(address + 0x110 )
            self.esr = getIntAt(address + 0x118 )
            self.exception = getIntAt(address + 0x11c )
    
    def printSavedState(self,previous_struct):
        res_str = ""
        res_str += f"{previous_struct}->x0			{printPtrAsString(self.x0)}\n"
        res_str += f"{previous_struct}->x1			{printPtrAsString(self.x1)}\n"
        res_str += f"{previous_struct}->x2			{printPtrAsString(self.x2)}\n"
        res_str += f"{previous_struct}->x3			{printPtrAsString(self.x3)}\n"
        res_str += f"{previous_struct}->x4			{printPtrAsString(self.x4)}\n"
        res_str += f"{previous_struct}->x5			{printPtrAsString(self.x5)}\n"
        res_str += f"{previous_struct}->x6			{printPtrAsString(self.x6)}\n"
        res_str += f"{previous_struct}->x7			{printPtrAsString(self.x7)}\n"
        res_str += f"{previous_struct}->x8			{printPtrAsString(self.x8)}\n"
        res_str += f"{previous_struct}->x9			{printPtrAsString(self.x9)}\n"
        res_str += f"{previous_struct}->x10			{printPtrAsString(self.x10)}\n"
        res_str += f"{previous_struct}->x11			{printPtrAsString(self.x11)}\n"
        res_str += f"{previous_struct}->x12			{printPtrAsString(self.x12)}\n"
        res_str += f"{previous_struct}->x13			{printPtrAsString(self.x13)}\n"
        res_str += f"{previous_struct}->x14			{printPtrAsString(self.x14)}\n"
        res_str += f"{previous_struct}->x15			{printPtrAsString(self.x15)}\n"
        res_str += f"{previous_struct}->x16			{printPtrAsString(self.x16)}\n"
        res_str += f"{previous_struct}->x17			{printPtrAsString(self.x17)}\n"
        res_str += f"{previous_struct}->x18			{printPtrAsString(self.x18)}\n"
        res_str += f"{previous_struct}->x19			{printPtrAsString(self.x19)}\n"
        res_str += f"{previous_struct}->x20			{printPtrAsString(self.x20)}\n"
        res_str += f"{previous_struct}->x21			{printPtrAsString(self.x21)}\n"
        res_str += f"{previous_struct}->x22			{printPtrAsString(self.x22)}\n"
        res_str += f"{previous_struct}->x23			{printPtrAsString(self.x23)}\n"
        res_str += f"{previous_struct}->x24			{printPtrAsString(self.x24)}\n"
        res_str += f"{previous_struct}->x25			{printPtrAsString(self.x25)}\n"
        res_str += f"{previous_struct}->x26			{printPtrAsString(self.x26)}\n"
        res_str += f"{previous_struct}->x27			{printPtrAsString(self.x27)}\n"
        res_str += f"{previous_struct}->x28			{printPtrAsString(self.x28)}\n"
        res_str += f"{previous_struct}->fp			{printPtrAsString(self.fp)}\n"
        res_str += f"{previous_struct}->lr			{printPtrAsString(self.lr)}\n"
        res_str += f"{previous_struct}->sp			{printPtrAsString(self.sp)}\n"
        res_str += f"{previous_struct}->pc			{getSymbol(printPtrAsString(self.pc))}\n"
        res_str += f"{previous_struct}->cpsr			{hex(self.cpsr)}\n"
        res_str += f"{previous_struct}->reserved             {hex(self.reserved)}\n"
        res_str += f"{previous_struct}->far			{printPtrAsString(self.far)}\n"
        res_str += f"{previous_struct}->esr			{hex(self.esr)}\n"
        res_str += f"{previous_struct}->exception		{hex(self.exception)}\n"

        return res_str

#Voucher
class ThreadVoucher:
    def __init__(self, address):
        if address != NULL_PTR:
            self.iv_hash  = getPointerAt(address )
            self.iv_sum  = getPointerAt(address + 0x04)
            self.iv_refs  = getPointerAt(address + 0x08)
            self.iv_table_size  = getPointerAt(address + 0x0c)
            self.iv_inline_table  = getPointerAt(address + 0x10)
            self.iv_table  = getPointerAt(address + 0x30)
            self.iv_port  = getPointerAt(address + 0x38)
            self.iv_hash_link  = getPointerAt(address + 0x40)

    def printVoucherInfo(self):
        res_str = ""
        res_str += f"iv_hash			{hex(self.iv_hash)}\n"
        res_str += f"iv_sum			{hex(self.iv_sum)}\n"
        res_str += f"iv_refs			{hex(self.iv_refs)}\n"
        res_str += f"iv_table_size		{hex(self.iv_table_size)}\n"
        res_str += f"iv_inline_table	        {hex(self.iv_inline_table)}\n"
        res_str += f"iv_table		{hex(self.iv_table)}\n"
        res_str += f"iv_port			{hex(self.iv_port)}\n"
        res_str += f"iv_hash_link		{hex((self.iv_hash_link))}\n"
        return res_str
        
#THREAD ITERATOR
class ThreadsIterator:
    def __init__(self, is_global=False, task=None):
        if is_global :
            self.type = ThrdItrType.GLOBAL
        else:
            self.type = ThrdItrType.TASK
            if task != NULL_PTR and task != None:
                self.task_ptr = task
            else:
                self.task_ptr = getCurrentTaskPtr()
                
    def __iter__(self):
        if self.type == ThrdItrType.GLOBAL:
            self.next_thread_ptr = getPointerAt(GLOBAL_THREADS_PTR)
            self.stop_contition = GLOBAL_THREADS_PTR
        else:
            relevant_task = Task(self.task_ptr)
            self.next_thread_ptr = getPointerAt(relevant_task.threads_lst_ptr)
            self.stop_contition = self.task_ptr + TaskOffsets.THREAD_LST_FROM_TASK.value
        return self

    def __next__(self):
        if self.next_thread_ptr != self.stop_contition:
            self.result = Thread(self.next_thread_ptr)
            if self.type == ThrdItrType.GLOBAL:
                self.next_thread_ptr = getPointerAt(self.result.global_threads_ptr)
            else:
                self.next_thread_ptr = getPointerAt(self.result.curr_task_threads_ptr)
            return self.result
        else:
            raise StopIteration               
                


class TasksIterator:
    def __init__(self):
        self.stop_contition = GLOBAL_TASKS_PTR
        self.next_task_ptr = getPointerAt(GLOBAL_TASKS_PTR)

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_task_ptr != self.stop_contition:
            self.result = Task(self.next_task_ptr)
            self.next_task_ptr = getPointerAt(self.result.task_lst_ptr)
            return self.result
        else:
            raise StopIteration     


class IPCEntryIterator:
    def __init__(self,address):
        if isValidPtr(address):
            self.entry = IPCSpace(address).is_table
            self.size = IPCSpace(address).is_table_size 
            self.index = 0
        else:
            raise gdb.GdbError(f"Worng ipc_entry poiner {address}")
    def __iter__(self):
        return self
    def __next__(self):
        while self.index < self.size:
            result = IPCEntry(self.entry + (self.index * 0x18))
            self.index += 1
            if (result.ie_bits & IE_BITS_TYPE_MASK) != 0:
                return result
        raise StopIteration


#Global functions
def isTaskExist(task):
    return task in list(tmptask.address for tmptask in iter(TasksIterator()))

def isThreadExist(thread):
    return thread in list(tmpthread.address for tmpthread in iter(ThreadsIterator(is_global=True))) 

def getMaxLengthProcName():
    max_length = 0
    for task in iter(TasksIterator()):
        if len(task.bsdinfo_object.bsd_name) > max_length:
            max_length = len(task.bsdinfo_object.bsd_name)
    return max_length

#TODO make generic!
def getMaxLengthContName():
    max_length = 0
    for thread in iter(ThreadsIterator(True)):
        if len(getSymbol(printPtrAsString(thread.continuation))) > max_length:
            max_length = len(getSymbol(printPtrAsString(thread.continuation)))
    return max_length

def getMaxLengthPcName():
    max_length = 0
    for thread in iter(ThreadsIterator(True)):
        if len(getSymbol(printPtrAsString(thread.next_pc))) > max_length:
            max_length = len(getSymbol(printPtrAsString(thread.next_pc)))
    return max_length


def getTheadInfoTitle(max_length_proc,max_length_cont, max_length_pc):
    res_str = ""
    res_str += f'U/K| PID | {"NAME":^{max_length_proc}} | TID |     THREAD_PTR     | {"CONTINUATION":^{max_length_cont}} | {"NEXT_PC*":^{max_length_pc}} |'
    return res_str