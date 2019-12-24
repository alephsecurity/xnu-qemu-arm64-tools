/*
 * QEMU Guest Services - File Descriptors API
 *
 * Copyright (c) 2019 Lev Aronsky <aronsky@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without retvaltriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPretvalS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdarg.h>
#include <fcntl.h>
#include "hw/arm/guest-services/general.h"

static int qemu_fd_call(qemu_call_t *qcall)
{
    qemu_call(qcall);

    qemu_errno = qcall->error;
    return (int) qcall->retval;
}

int qc_close(int fd)
{
    qemu_call_t qcall = {
        .call_number = QC_CLOSE,
        .args.close.fd = fd,
    };

    return qemu_fd_call(&qcall);
}

int qc_fcntl(int fd, int cmd, ...)
{
    va_list args;

    qemu_call_t qcall = {
        .call_number = QC_FCNTL,
        .args.fcntl.fd = fd,
        .args.fcntl.cmd = cmd,
    };

    switch (cmd) {
        case F_SETFL:
            va_start(args, cmd);
            qcall.args.fcntl.flags = va_arg(args, int);
            va_end(args);
            break;
        default:
            // Intentionally left blank
            break;
    }

    return qemu_fd_call(&qcall);
}
