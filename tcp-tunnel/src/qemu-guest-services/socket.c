/*
 * QEMU Guest Services - Socket API
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

#include "hw/arm/guest-services/general.h"

static int qemu_sckt_call(qemu_call_t *qcall)
{
    qemu_call(qcall);

    guest_svcs_errno = qcall->error;
    return (int) qcall->retval;
}

int qc_socket(int domain, int type, int protocol)
{
    qemu_call_t qcall = {
        .call_number = QC_SOCKET,
        .args.socket.domain = domain,
        .args.socket.type = type,
        .args.socket.protocol = protocol,
    };

    return qemu_sckt_call(&qcall);
}

int qc_accept(int sckt, struct sockaddr *addr, socklen_t *addrlen)
{
    qemu_call_t qcall = {
        .call_number = QC_ACCEPT,
        .args.accept.socket = sckt,
        .args.accept.addr = addr,
        .args.accept.addrlen = addrlen,
    };

    return qemu_sckt_call(&qcall);
}

int qc_bind(int sckt, const struct sockaddr *addr, socklen_t addrlen)
{
    qemu_call_t qcall = {
        .call_number = QC_BIND,
        .args.bind.socket = sckt,
        .args.bind.addr = (struct sockaddr *) addr,
        .args.bind.addrlen = addrlen,
    };

    return qemu_sckt_call(&qcall);
}

int qc_connect(int sckt, const struct sockaddr *addr, socklen_t addrlen)
{
    qemu_call_t qcall = {
        .call_number = QC_CONNECT,
        .args.connect.socket = sckt,
        .args.connect.addr = (struct sockaddr *) addr,
        .args.connect.addrlen = addrlen,
    };

    return qemu_sckt_call(&qcall);
}

int qc_listen(int sckt, int backlog)
{
    qemu_call_t qcall = {
        .call_number = QC_LISTEN,
        .args.listen.socket = sckt,
        .args.listen.backlog = backlog,
    };

    return qemu_sckt_call(&qcall);
}

ssize_t qc_recv(int sckt, void *buffer, size_t length, int flags)
{
    qemu_call_t qcall = {
        .call_number = QC_RECV,
        .args.recv.socket = sckt,
        .args.recv.buffer = buffer,
        .args.recv.length = length,
        .args.recv.flags = flags,
    };

    return qemu_sckt_call(&qcall);
}

ssize_t qc_send(int sckt, const void *buffer, size_t length, int flags)
{
    qemu_call_t qcall = {
        .call_number = QC_SEND,
        .args.send.socket = sckt,
        .args.send.buffer = (void *) buffer,
        .args.send.length = length,
        .args.send.flags = flags,
    };

    return qemu_sckt_call(&qcall);
}
