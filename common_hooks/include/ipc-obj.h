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

#ifndef IPC_OBJ_H
#define IPC_OBJ_H

struct ipc_object {
    uint32_t io_bits;
    uint32_t io_references;
    uint64_t io_lock_data;
} __attribute__((packed));

typedef struct bsd_info {
    char reserved[0x60];
    uint32_t p_pid;
    char reserved1[0x1FD];
    char p_name[256]; //TODO: verify size

} __attribute__((packed)) bsd_info_t;

typedef struct task {
    char reserved[0x358];
    bsd_info_t *bsd_info;

} __attribute__((packed)) task_t;
typedef struct ipc_space {
    char is_lock_data[0x10]; //verify size?
    char is_bits[4]; /* holds refs, active, growing */ //verify size?
    uint32_t is_table_size; /* current size of table */
    uint32_t is_table_free; /* count of free elements */
    uint32_t reserved;
    void *is_table; /* an array of entries */
    task_t *is_task; /* associated task */

} __attribute__((packed)) ipc_space_t;

typedef struct {
    struct ipc_object ip_object;
    char reserved[0x50];
    struct ipc_space *receiver;
} __attribute__((packed)) ipc_port_t;

#define MACH_MSGH_BITS_ZERO (0x00000000)

#define MACH_MSGH_BITS_REMOTE_MASK (0x0000001f)
#define MACH_MSGH_BITS_LOCAL_MASK (0x00001f00)
#define MACH_MSGH_BITS_VOUCHER_MASK (0x001f0000)

#define MACH_MSGH_BITS_PORTS_MASK       \
        ((MACH_MSGH_BITS_REMOTE_MASK) | \
        (MACH_MSGH_BITS_LOCAL_MASK)   | \
        (MACH_MSGH_BITS_VOUCHER_MASK))

#define MACH_MSGH_BITS_COMPLEX (0x80000000U) /* message is complex */

#define MACH_MSGH_BITS_USER (0x801f1f1fU) /* allowed bits user->kernel */

#define MACH_MSGH_BITS_RAISEIMP (0x20000000U) /* importance raised due to msg */
#define MACH_MSGH_BITS_DENAP (MACH_MSGH_BITS_RAISEIMP)

#define MACH_MSGH_BITS_IMPHOLDASRT (0x10000000U) /* assertion help, userland private */
#define MACH_MSGH_BITS_DENAPHOLDASRT (MACH_MSGH_BITS_IMPHOLDASRT)

#define MACH_MSGH_BITS_CIRCULAR (0x10000000U) /* message circular, kernel private */

#define MACH_MSGH_BITS_USED (0xb01f1f1fU)

/* setter macros for the bits */
#define MACH_MSGH_BITS(remote, local)  /* legacy */ \
        ((remote) | ((local) << 8))
#define MACH_MSGH_BITS_SET_PORTS(remote, local, voucher)   \
        (((remote) & MACH_MSGH_BITS_REMOTE_MASK) |         \
        (((local) << 8) & MACH_MSGH_BITS_LOCAL_MASK) |     \
        (((voucher) << 16) & MACH_MSGH_BITS_VOUCHER_MASK))
#define MACH_MSGH_BITS_SET(remote, local, voucher, other)       \
        (MACH_MSGH_BITS_SET_PORTS((remote), (local), (voucher)) \
        | ((other) &~ MACH_MSGH_BITS_PORTS_MASK))

/* getter macros for pulling values out of the bits field */
#define MACH_MSGH_BITS_REMOTE(bits)             \
        ((bits) & MACH_MSGH_BITS_REMOTE_MASK)
#define MACH_MSGH_BITS_LOCAL(bits)              \
        (((bits) & MACH_MSGH_BITS_LOCAL_MASK) >> 8)
#define MACH_MSGH_BITS_VOUCHER(bits)            \
        (((bits) & MACH_MSGH_BITS_VOUCHER_MASK) >> 16)
#define MACH_MSGH_BITS_PORTS(bits)              \
        ((bits) & MACH_MSGH_BITS_PORTS_MASK)
#define MACH_MSGH_BITS_OTHER(bits)              \
        ((bits) &~ MACH_MSGH_BITS_PORTS_MASK)

/* checking macros */
#define MACH_MSGH_BITS_HAS_REMOTE(bits)             \
        (MACH_MSGH_BITS_REMOTE(bits) != MACH_MSGH_BITS_ZERO)
#define MACH_MSGH_BITS_HAS_LOCAL(bits)              \
        (MACH_MSGH_BITS_LOCAL(bits) != MACH_MSGH_BITS_ZERO)
#define MACH_MSGH_BITS_HAS_VOUCHER(bits)            \
        (MACH_MSGH_BITS_VOUCHER(bits) != MACH_MSGH_BITS_ZERO)
#define MACH_MSGH_BITS_IS_COMPLEX(bits)             \
        (((bits) & MACH_MSGH_BITS_COMPLEX) != MACH_MSGH_BITS_ZERO)

/* importance checking macros */
#define MACH_MSGH_BITS_RAISED_IMPORTANCE(bits)        \
        (((bits) & MACH_MSGH_BITS_RAISEIMP) != MACH_MSGH_BITS_ZERO)
#define MACH_MSGH_BITS_HOLDS_IMPORTANCE_ASSERTION(bits)     \
        (((bits) & MACH_MSGH_BITS_IMPHOLDASRT) != MACH_MSGH_BITS_ZERO)


#define MACH_MSGH_BITS_IS_CIRCULAR(bits)     \
        (((bits) & MACH_MSGH_BITS_CIRCULAR) != MACH_MSGH_BITS_ZERO)

#define MACH_MSG_TYPE_MOVE_RECEIVE      16 /* Must hold receive right */
#define MACH_MSG_TYPE_MOVE_SEND         17 /* Must hold send right(s) */
#define MACH_MSG_TYPE_MOVE_SEND_ONCE    18 /* Must hold sendonce right */
#define MACH_MSG_TYPE_COPY_SEND         19 /* Must hold send right(s) */
#define MACH_MSG_TYPE_MAKE_SEND         20 /* Must hold receive right */
#define MACH_MSG_TYPE_MAKE_SEND_ONCE    21 /* Must hold receive right */
#define MACH_MSG_TYPE_COPY_RECEIVE      22 /* NOT VALID */
#define MACH_MSG_TYPE_DISPOSE_RECEIVE   24 /* must hold receive right */
#define MACH_MSG_TYPE_DISPOSE_SEND      25 /* must hold send right(s) */
#define MACH_MSG_TYPE_DISPOSE_SEND_ONCE 26 /* must hold sendonce right */

typedef struct {
    uint32_t msgh_bits;
    uint32_t size;
    ipc_port_t *msgh_remote_port;
    ipc_port_t *msgh_local_port;
    uint32_t msgh_voucher_port_name;
    uint32_t msgh_id;
    uint64_t reserved3;
    uint64_t reserved4;
    uint64_t reserved5;
    uint64_t reserved6;
    uint64_t reserved7;
    uint64_t reserved8;
} __attribute__((packed)) mach_msg_header_t;

typedef struct {
    uint32_t size;
    uint32_t reserved;
    void *next;
    void *prev;
    mach_msg_header_t *hdr;
} __attribute__((packed)) ipc_kmsg;

void print_task(task_t *task, char *message, size_t size);
void print_ipc_space(ipc_space_t *space, char *message, size_t size);
void print_ipc_port(ipc_port_t *port, char *message, size_t size);
void print_port_bits_text(uint64_t bits, char *message, size_t size);
void print_ipc_kmsg(ipc_kmsg *kmsg, char *message, size_t size);

#endif
