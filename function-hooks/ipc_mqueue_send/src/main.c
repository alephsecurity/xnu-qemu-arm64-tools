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

#include <string.h>
#include <stdint.h>

#include "kern_funcs.h"
#include "utils.h"
#include "qemu-guest-services.h"
#include "ipc-obj.h"

void _start() __attribute__((section(".start")));

void _start() {
    //hope that first time is non ovrelapping because it is not really protected
    //TODO: initialize from outside the hook to remove this assumption
    //ugly solution to use preallocated global data in the hooks/drivers at
    //a fixed address allocated in the "boot loader"
    //TODO: find a less ugly solution for this global storage
    void *mtx_grp;
    void **global_mtx = (void *)0xFFFFFFF009BF4C00;
    if (NULL == *global_mtx) {
        mtx_grp = lck_grp_alloc_init("log_file_mutex", NULL);
        *global_mtx = lck_mtx_alloc_init(mtx_grp, NULL);
    }
    uint64_t kmsg_uint;
    asm volatile ("mov %0, x19" : "=r"(kmsg_uint) ::);
    ipc_kmsg *kmsg = (ipc_kmsg *)kmsg_uint;
    lck_mtx_lock(*global_mtx);
    size_t size = 16384;
    char *message = kern_os_malloc(size);
    message[0] = '\0';
    strncat(message, "^^^^^^^^^^^^^^^^^^^^^^^^ ipc_mqueue_send()\n", size);
    print_ipc_kmsg(kmsg, message, size);
    qc_write_file(message, strlen(message), (uint64_t)qc_size_file(2), 2);
    kern_os_free(message);
    lck_mtx_unlock(*global_mtx);
}
