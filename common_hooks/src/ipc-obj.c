/*
 * Copyright (c) 2020 Jonathan Afek <jonyafek@me.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdint.h>
#include <string.h>

#include "utils.h"
#include "kern_funcs.h"
#include "ipc-obj.h"

void print_task(task_t *task, char *message, size_t size)
{
    strncat(message, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n", size);
    strncat_int64(message, "task->bsd_info: ", size, (uint64_t)task->bsd_info);
    //sanity
    if (NULL != task->bsd_info) {
        strncat_int64(message, "task->bsd_info->p_pid: ", size, (uint64_t)task->bsd_info->p_pid);
        strncat(message, "task name: ", size);
        strncat(message, &task->bsd_info->p_name[0], size);
        strncat(message, "\n", size);
    }
    strncat(message, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n", size);
}

void print_ipc_space(ipc_space_t *space, char *message, size_t size)
{
    strncat(message, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", size);
    strncat_int64(message, "space->is_table_size: ", size, (uint64_t)space->is_table_size);
    strncat_int64(message, "space->is_table_free: ", size, (uint64_t)space->is_table_free);
    strncat_int64(message, "space->is_table: ", size, (uint64_t)space->is_table);
    strncat_int64(message, "space->is_task: ", size, (uint64_t)space->is_task);
    //kernel ipc_space doesn't point to the kernel task so it is NULL
    if (NULL != space->is_task) {
        print_task(space->is_task, message, size);
    }
    strncat(message, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", size);
}

void print_ipc_port(ipc_port_t *port, char *message, size_t size)
{
    uint32_t is_active = (port->ip_object.io_bits >> 31) & 1;
    uint32_t otype = (port->ip_object.io_bits >> 16) & 0x7FFF;
    uint32_t is_preallocated = (port->ip_object.io_bits >> 15) & 1;
    uint32_t kotype = port->ip_object.io_bits & 0xFFF;

    strncat(message, "===========================================================\n", size);

    strncat_int64(message, "port->ip_object.io_bits: ", size, (uint64_t)port->ip_object.io_bits);
    strncat_int64(message, "is_active: ", size, (uint64_t)is_active);
    //strncat(message, "otype map: \n"
    //           "#define IOT_PORT            0\n"
    //           "#define IOT_PORT_SET        1\n"
    //           "#define IOT_NUMBER          2   /* number of types used */\n"
    //           ""
    //           ,
    //           size);
    strncat_int64(message, "otype: ", size, (uint64_t)otype);
    switch (otype) {
        case 0:
            strncat(message, "(IOT_PORT)\n", size);
            break;
        case 1:
            strncat(message, "(IOT_PORT_SET)\n", size);
            break;
        case 2:
            strncat(message, "(IOT_NUMBER)\n", size);
            break;
        default:
            strncat(message, "(OTHER TYPE)\n", size);
            break;
    }
    strncat_int64(message, "is_preallocated: ", size, (uint64_t)is_preallocated);
    //strncat(message, "kotype map: \n"
    //           "#define IKOT_NONE                   0\n"
    //           "#define IKOT_THREAD                 1\n"
    //           "#define IKOT_TASK                   2\n"
    //           "#define IKOT_HOST                   3\n"
    //           "#define IKOT_HOST_PRIV              4\n"
    //           "#define IKOT_PROCESSOR              5\n"
    //           "#define IKOT_PSET                   6\n"
    //           "#define IKOT_PSET_NAME              7\n"
    //           "#define IKOT_TIMER                  8\n"
    //           "#define IKOT_PAGING_REQUEST         9\n"
    //           "#define IKOT_MIG                    10\n"
    //           "#define IKOT_MEMORY_OBJECT          11\n"
    //           "#define IKOT_XMM_PAGER              12\n"
    //           "#define IKOT_XMM_KERNEL             13\n"
    //           "#define IKOT_XMM_REPLY              14\n"
    //           "#define IKOT_UND_REPLY              15\n"
    //           "#define IKOT_HOST_NOTIFY            16\n"
    //           "#define IKOT_HOST_SECURITY          17\n"
    //           "#define IKOT_LEDGER                 18\n"
    //           "#define IKOT_MASTER_DEVICE          19\n"
    //           "#define IKOT_TASK_NAME              20\n"
    //           "#define IKOT_SUBSYSTEM              21\n"
    //           "#define IKOT_IO_DONE_QUEUE          22\n"
    //           "#define IKOT_SEMAPHORE              23\n"
    //           "#define IKOT_LOCK_SET               24\n"
    //           "#define IKOT_CLOCK                  25\n"
    //           "#define IKOT_CLOCK_CTRL             26\n"
    //           "#define IKOT_IOKIT_IDENT            27\n"
    //           "#define IKOT_NAMED_ENTRY            28\n"
    //           "#define IKOT_IOKIT_CONNECT          29\n"
    //           "#define IKOT_IOKIT_OBJECT           30\n"
    //           "#define IKOT_UPL                    31\n"
    //           "#define IKOT_MEM_OBJ_CONTROL        32\n"
    //           "#define IKOT_AU_SESSIONPORT         33\n"
    //           "#define IKOT_FILEPORT               34\n"
    //           "#define IKOT_LABELH                 35\n"
    //           "#define IKOT_TASK_RESUME            36\n"
    //           "#define IKOT_VOUCHER                37\n"
    //           "#define IKOT_VOUCHER_ATTR_CONTROL   38\n"
    //           "#define IKOT_WORK_INTERVAL          39\n"
    //           "#define IKOT_UX_HANDLER             40\n"
    //           "#define IKOT_UNKNOWN                41\n"
    //           ""
    //           , size);
    strncat_int64(message, "kotype: ", size, (uint64_t)kotype);
    switch (kotype) {
        case 0:
            strncat(message, "(IKOT_NONE)\n", size);
            break;
        case 1:
            strncat(message, "(IKOT_THREAD)\n", size);
            break;
        case 2:
            strncat(message, "(IKOT_TASK)\n", size);
            break;
        case 3:
            strncat(message, "(IKOT_HOST)\n", size);
            break;
        case 4:
            strncat(message, "(IKOT_HOST_PRIV)\n", size);
            break;
        case 41:
            strncat(message, "(IKOT_UNKNOWN)\n", size);
            break;
        default:
            strncat(message, "(OTHER TYPE)\n", size);
            break;
    }
    strncat_int64(message, "port->ip_object.io_references: ", size, (uint64_t)port->ip_object.io_references);
    strncat_int64(message, "port->ip_object.io_lock_data: ", size, (uint64_t)port->ip_object.io_lock_data);
    strncat_int64(message, "port->receiver: ", size, (uint64_t)port->receiver);
    //TODO: JONATHANA make sure it is both active and not in transfer...
    if (is_active && (NULL != port->receiver)) {
        print_ipc_space(port->receiver, message, size);
    }
    strncat(message, "===========================================================\n", size);
}

void print_port_bits_text(uint64_t bits, char *message, size_t size)
{
    switch (bits) {
        case 16:
            strncat(message, "(MACH_MSG_TYPE_MOVE_RECEIVE)\n", size);
            break;
        case 17:
            strncat(message, "(MACH_MSG_TYPE_MOVE_SEND)\n", size);
            break;
        case 18:
            strncat(message, "(MACH_MSG_TYPE_MOVE_SEND_ONCE)\n", size);
            break;
        case 19:
            strncat(message, "(MACH_MSG_TYPE_COPY_SEND)\n", size);
            break;
        case 20:
            strncat(message, "(MACH_MSG_TYPE_MAKE_SEND)\n", size);
            break;
        case 21:
            strncat(message, "(MACH_MSG_TYPE_MAKE_SEND_ONCE)\n", size);
            break;
        case 22:
            strncat(message, "(MACH_MSG_TYPE_COPY_RECEIVE)\n", size);
            break;
        case 24:
            strncat(message, "(MACH_MSG_TYPE_DISPOSE_RECEIVE)\n", size);
            break;
        case 25:
            strncat(message, "(MACH_MSG_TYPE_DISPOSE_SEND)\n", size);
            break;
        case 26:
            strncat(message, "(MACH_MSG_TYPE_DISPOSE_SEND_ONCE)\n", size);
            break;
        default:
            strncat(message, "(OTHER TYPE)\n", size);
            break;
    }
}

void print_ipc_kmsg(ipc_kmsg *kmsg, char *message, size_t size)
{
    strncat(message, "*********************************************************************************************\n", size);
    task_t *cur_task = (task_t *)current_task();
    strncat_int64(message, "current task: ", size, (uint64_t)cur_task);
    print_task(cur_task, message, size);
    strncat_int64(message, "ipc_kmsg_send() kmsg: ", size, (uint64_t)kmsg);
    strncat_int64(message, "kmsg->size: ", size, (uint64_t)kmsg->size);
    strncat_int64(message, "kmsg->next: ", size, (uint64_t)kmsg->next);
    strncat_int64(message, "kmsg->prev: ", size, (uint64_t)kmsg->prev);
    strncat_int64(message, "kmsg->hdr: ", size, (uint64_t)kmsg->hdr);

    uint64_t local_bits = (uint64_t)MACH_MSGH_BITS_LOCAL(kmsg->hdr->msgh_bits);
    uint64_t remote_bits = (uint64_t)MACH_MSGH_BITS_REMOTE(kmsg->hdr->msgh_bits);
    uint64_t voucher_bits = (uint64_t)MACH_MSGH_BITS_VOUCHER(kmsg->hdr->msgh_bits);
    uint64_t is_complex_bits = (uint64_t)MACH_MSGH_BITS_IS_COMPLEX(kmsg->hdr->msgh_bits);
    uint64_t is_raiseimp_bits = (uint64_t)MACH_MSGH_BITS_RAISED_IMPORTANCE(kmsg->hdr->msgh_bits);
    uint64_t is_impholdasrt_bits = (uint64_t)MACH_MSGH_BITS_HOLDS_IMPORTANCE_ASSERTION(kmsg->hdr->msgh_bits);
    uint64_t is_circular_bits = (uint64_t)MACH_MSGH_BITS_IS_CIRCULAR(kmsg->hdr->msgh_bits);
    //strncat(message, "bit rights map: \n"
    //           "#define MACH_MSG_TYPE_MOVE_RECEIVE      16 /* Must hold receive right */\n"
    //           "#define MACH_MSG_TYPE_MOVE_SEND         17 /* Must hold send right(s) */\n"
    //           "#define MACH_MSG_TYPE_MOVE_SEND_ONCE    18 /* Must hold sendonce right */\n"
    //           "#define MACH_MSG_TYPE_COPY_SEND         19 /* Must hold send right(s) */\n"
    //           "#define MACH_MSG_TYPE_MAKE_SEND         20 /* Must hold receive right */\n"
    //           "#define MACH_MSG_TYPE_MAKE_SEND_ONCE    21 /* Must hold receive right */\n"
    //           "#define MACH_MSG_TYPE_COPY_RECEIVE      22 /* NOT VALID */\n"
    //           "#define MACH_MSG_TYPE_DISPOSE_RECEIVE   24 /* must hold receive right */\n"
    //           "#define MACH_MSG_TYPE_DISPOSE_SEND      25 /* must hold send right(s) */\n"
    //           "#define MACH_MSG_TYPE_DISPOSE_SEND_ONCE 26 /* must hold sendonce right */\n"
    //           ""
    //           ,  size);
    strncat_int64(message, "kmsg->hdr->msgh_bits(local): ", size, (uint64_t)local_bits);
    print_port_bits_text((uint64_t)local_bits, message, size);
    strncat_int64(message, "kmsg->hdr->msgh_bits(remote): ", size, (uint64_t)remote_bits);
    print_port_bits_text((uint64_t)remote_bits, message, size);
    strncat_int64(message, "kmsg->hdr->msgh_bits(voucher): ", size, (uint64_t)voucher_bits);
    print_port_bits_text((uint64_t)voucher_bits, message, size);
    strncat_int64(message, "kmsg->hdr->msgh_bits(is_complex): ", size, (uint64_t)is_complex_bits);
    strncat_int64(message, "kmsg->hdr->msgh_bits(is_raiseimp_bits): ", size, (uint64_t)is_raiseimp_bits);
    strncat_int64(message, "kmsg->hdr->msgh_bits(is_impholdasrt_bits): ", size, (uint64_t)is_impholdasrt_bits);
    strncat_int64(message, "kmsg->hdr->msgh_bits(is_circular_bits): ", size, (uint64_t)is_circular_bits);
    strncat_int64(message, "kmsg->hdr->size: ", size, (uint64_t)kmsg->hdr->size);
    strncat_int64(message, "kmsg->hdr->msgh_remote_port: ", size, (uint64_t)kmsg->hdr->msgh_remote_port);
    strncat_int64(message, "kmsg->hdr->msgh_local_port: ", size, (uint64_t)kmsg->hdr->msgh_local_port);
    strncat_int64(message, "kmsg->hdr->msgh_voucher_port_name: ", size, (uint64_t)kmsg->hdr->msgh_voucher_port_name);
    strncat_int64(message, "kmsg->hdr->msgh_id: ", size, (uint64_t)kmsg->hdr->msgh_id);
    if (0 != remote_bits) {
        strncat(message, "kmsg->hdr->msgh_remote_port CONTENT: \n", size);
        print_ipc_port(kmsg->hdr->msgh_remote_port, message, size);
    }
    if (0 != local_bits) {
        strncat(message, "kmsg->hdr->msgh_local_port CONTENT: \n", size);
        print_ipc_port(kmsg->hdr->msgh_local_port, message, size);
    }
    strncat(message, "*********************************************************************************************\n", size);
}
