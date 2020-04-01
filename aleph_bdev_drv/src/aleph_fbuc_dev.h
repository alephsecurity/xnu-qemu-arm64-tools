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

#include "mclass_reg.h"

#ifndef ALEPH_FBUC_DEV_H
#define ALEPH_FBUC_DEV_H

//just in case.
#define ALEPH_FBUC_SIZE (0x2000)
#define FBUC_MEMBERS_OFFSET (0x800)
#define FBUC_MAX_EXT_FUNCS (0x60)
#define FBUC_MAX_NOTIF_PORTS (8)

#define FBUC_CLASS_NAME "IOMobileFramebufferDeviceUserClient"


typedef struct {
    uint64_t type;
    uint64_t ref;
    void *port;
    uint64_t asnyc_ref64[8];
} NotifPortInfo;

typedef struct {
    void *task;
    NotifPortInfo notif_ports[FBUC_MAX_NOTIF_PORTS];
    IOExternalMethodDispatch fbuc_external_methods[FBUC_MAX_EXT_FUNCS];

} FBUCMembers;

void *get_fbuc_mclass_inst(void);

//our driver virtual functions
void *fbuc_getMetaClass(void *this);
uint64_t fbuc_externalMethod(void *this, uint32_t selector,
                             IOExternalMethodArguments *args,
                             IOExternalMethodDispatch *dispatch,
                             void *target, void *reference);
uint64_t fbuc_start(void *this);
uint64_t fbuc_clientClose(void *this);
uint64_t fbuc_connectClient(void *this, void *user_client);
uint64_t fbuc_getNotificationSemaphore(void *this, uint64_t type, void *sem);
uint64_t fbuc_clientMemoryForType(void *this, uint64_t type, void *opts,
                                  void **mem);
uint64_t fbuc_registerNotificationPort(void *this, void *port,
                                       uint64_t type, uint64_t ref);
uint64_t fbuc_initWithTask(void *this, void *task, void *sid, uint64_t type);
uint64_t fbuc_destructor(void *this);

#endif
