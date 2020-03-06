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

#include "aleph_bdev_mclass.h"
#include "kern_funcs.h"
#include "aleph_block_dev.h"
#include "utils.h"
#include "mclass_reg.h"

#include "hw/arm/guest-services/general.h"

static void *bdev_vtable[BDEV_VTABLE_SIZE];
static MetaClassVTable bdev_meta_class_vtable;


void create_bdev_vtable(void)
{
    memcpy(&bdev_vtable[0],
           (void *)IOBLOCKSTORAGEDEVICE_VTABLE_PTR,
           sizeof(bdev_vtable));
    bdev_vtable[IOSERVICE_GETMCLASS_INDEX] =
                                        &AlephBlockDevice_getMetaClass;
    bdev_vtable[IOSTORAGEBDEV_GETVENDORSTRING_INDEX] =
                                        &AlephBlockDevice_getVendorString;
    bdev_vtable[IOSTORAGEBDEV_GETPRODUCTSTRING_INDEX] =
                                        &AlephBlockDevice_getProductString;
    bdev_vtable[IOSTORAGEBDEV_REPORTBSIZE_INDEX] =
                                        &AlephBlockDevice_reportBlockSize;
    bdev_vtable[IOSTORAGEBDEV_REPORTMAXVALIDBLOCK_INDEX] =
                                        &AlephBlockDevice_reportMaxValidBlock;
    bdev_vtable[IOSTORAGEBDEV_REPORTMEDIASTATE_INDEX] =
                                        &AlephBlockDevice_reportMediaState;
    bdev_vtable[IOSTORAGEBDEV_REPORTREMOVABILITY_INDEX] =
                                        &AlephBlockDevice_reportRemovability;
    bdev_vtable[IOSTORAGEBDEV_SOMEFUNC3_INDEX] =
                                        &AlephBlockDevice_somefunc3;
    bdev_vtable[IOSTORAGEBDEV_DOASYNCREADWRITE_INDEX] =
                                        &AlephBlockDevice_doAsyncReadWrite;
}

void *bdev_alloc(void)
{
    ObjConstructor ioblockstoragedevice_constructor;
    ioblockstoragedevice_constructor =
                (ObjConstructor)IOBLOCKSTORAGEDEVICE_CONSTRUCTOR_FUNC_PTR;

    void **obj = OSObject_new(ALEPH_BDEV_SIZE);
    ioblockstoragedevice_constructor(obj);
    obj[0] = &bdev_vtable[0];
    OSMetaClass_instanceConstructed(get_bdev_mclass_inst());
    return obj;
}

void create_bdev_metaclass_vtable(void)
{
    memcpy(&bdev_meta_class_vtable,
           (void *)IOBLOCKSTORAGEDEVICE_MCLASS_VTABLE_PTR,
           sizeof(MetaClassVTable));
    bdev_meta_class_vtable.alloc = bdev_alloc;
}

void register_bdev_meta_class()
{
    mclass_reg_slock_lock();

    create_bdev_vtable();
    create_bdev_metaclass_vtable();

    void **mc = OSMetaClass_OSMetaClass(get_bdev_mclass_inst(),
                                  BDEV_CLASS_NAME,
                                  (void *)IOBLOCKSTORAGEDEVICE_MCLASS_INST_PTR,
                                  ALEPH_BDEV_SIZE);
    if (NULL == mc) {
        cancel();
    }
    mc[0] = &bdev_meta_class_vtable;

    mclass_reg_alock_lock();

    add_to_classes_dict(BDEV_CLASS_NAME, mc);

    mclass_reg_alock_unlock();
    mclass_reg_slock_unlock();

}
