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

#include "aleph_fbuc_mclass.h"
#include "kern_funcs.h"
#include "aleph_fbuc_dev.h"
#include "utils.h"
#include "mclass_reg.h"

#include "hw/arm/guest-services/general.h"

static void *fbuc_vtable[FBUC_VTABLE_SIZE];
static MetaClassVTable fbuc_meta_class_vtable;

void create_fbuc_vtable(void)
{
    memcpy(&fbuc_vtable[0],
           (void *)IOUC_VTABLE_PTR,
           sizeof(fbuc_vtable));
    fbuc_vtable[IOSERVICE_DESTRUCTOR_INDEX] = &fbuc_destructor;
    fbuc_vtable[IOSERVICE_GETMCLASS_INDEX] = &fbuc_getMetaClass;
    fbuc_vtable[IOUC_EXTERNAL_METHOD_INDEX] = &fbuc_externalMethod;
    fbuc_vtable[IOUC_INIT_WITH_TASK_INDEX] = &fbuc_initWithTask;
    fbuc_vtable[IOUC_CLIENT_CLOSE_INDEX] = &fbuc_clientClose;
    fbuc_vtable[IOUC_REG_NOTIF_PORT_INDEX] = &fbuc_registerNotificationPort;
    fbuc_vtable[IOUC_GET_NOTIFICATION_SEMAPHORE_INDEX] =
                                                &fbuc_getNotificationSemaphore;
    fbuc_vtable[IOUC_CONNECT_CLIENT_INDEX] = &fbuc_connectClient;
    fbuc_vtable[IOUC_CLIENT_MEM_FOR_TYPE_INDEX] = &fbuc_clientMemoryForType;
    fbuc_vtable[IOSERVICE_START_INDEX] = &fbuc_start;
    log_uint64("fbuc vtable: ", (uint64_t)&fbuc_vtable[0]);
}

void *fbuc_alloc(void)
{
    void **obj = OSObject_new(ALEPH_FBUC_SIZE);
    log_uint64("fbuc obj: ", (uint64_t)obj);
    IOUserClient_IOUserClient(obj, get_fbuc_mclass_inst());
    obj[0] = &fbuc_vtable[0];
    OSMetaClass_instanceConstructed(get_fbuc_mclass_inst());
    return obj;
}

void create_fbuc_metaclass_vtable(void)
{
    memcpy(&fbuc_meta_class_vtable, (void *)IOUC_MCLASS_VTABLE_PTR,
           sizeof(MetaClassVTable));
    fbuc_meta_class_vtable.alloc = fbuc_alloc;
}

void register_fbuc_meta_class()
{
    mclass_reg_slock_lock();

    create_fbuc_vtable();
    create_fbuc_metaclass_vtable();

    void **mc = OSMetaClass_OSMetaClass(get_fbuc_mclass_inst(),
                                  FBUC_CLASS_NAME,
                                  (void *)IOUC_MCLASS_INST_PTR,
                                  ALEPH_FBUC_SIZE);
    if (NULL == mc) {
        cancel();
    }
    mc[0] = &fbuc_meta_class_vtable;

    mclass_reg_alock_lock();

    add_to_classes_dict(FBUC_CLASS_NAME, mc);

    mclass_reg_alock_unlock();
    mclass_reg_slock_unlock();
}
