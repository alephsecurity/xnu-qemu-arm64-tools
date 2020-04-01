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

#include "aleph_block_dev.h"
#include "aleph_bdev_mclass.h"
#include "kern_funcs.h"
#include "utils.h"
#include "mclass_reg.h"

#include "hw/arm/guest-services/general.h"

static uint8_t aleph_bdev_meta_class_inst[ALEPH_MCLASS_SIZE];

AlephBDevMembers *get_bdev_members(void *bdev)
{
    AlephBDevMembers *members;
    members = (AlephBDevMembers *)&((uint8_t *)bdev)[ALEPH_BDEV_MEMBERS_OFFSET];
    return members;
}

void *get_bdev_buffer(void *bdev)
{
    return (void *)&(((uint8_t *)bdev)[ALEPH_BDEV_BUFFER_OFFSET]);
}

void *get_bdev_mclass_inst(void)
{
    return (void *)&aleph_bdev_meta_class_inst[0];
}

//virtual functions of our driver

void *AlephBlockDevice_getMetaClass(void *this)
{
    return get_bdev_mclass_inst();
}

uint64_t AlephBlockDevice_reportRemovability(void *this, char *isRemovable)
{
    *isRemovable = 0;
    return 0;
}

uint64_t AlephBlockDevice_reportMediaState(void *this,
                                           char *mediaPresent,
                                           char *changedState)
{
    *mediaPresent = 1;
    *changedState = 0;
    return 0;
}

uint64_t AlephBlockDevice_reportBlockSize(void *this, uint64_t *param)
{
    *param = BLOCK_SIZE;
    return 0;
}

uint64_t AlephBlockDevice_reportMaxValidBlock(void *this, uint64_t *param)
{
    AlephBDevMembers *members = get_bdev_members(this);
    *param = members->block_count - 1;
    return 0;
}

//could be reportLockability or reportWriteProtection?
uint64_t AlephBlockDevice_somefunc3(void *this, char *param)
{
    *param = 0;
    return 0;
}

char *AlephBlockDevice_getVendorString(void *this)
{
    AlephBDevMembers *members = get_bdev_members(this);
    return &members->vendor_name[0];
}

char *AlephBlockDevice_getProductString(void *this)
{
    AlephBDevMembers *members = get_bdev_members(this);
    return &members->product_name[0];
}

uint64_t AlephBlockDevice_doAsyncReadWrite(void *this, void **buffer,
                                         uint64_t block, uint64_t nblks,
                                         void *attrs, void **completion)
{
    uint64_t i = 0;
    void *dev_buf = get_bdev_buffer(this);
    AlephBDevMembers *members = get_bdev_members(this);

    lck_mtx_lock(members->lck_mtx);

    void **buffer_vtable = buffer[0];
    FuncIOMemDescGetDirection get_dir_f =
        (FuncIOMemDescGetDirection)buffer_vtable[IOMEMDESCGETDIRECTION_INDEX];
    FuncIOMemDescReadBytes read_bytes_f =
        (FuncIOMemDescReadBytes)buffer_vtable[IOMEMDESCREADBYTES_INDEX];
    FuncIOMemDescWriteBytes write_bytes_f =
        (FuncIOMemDescWriteBytes)buffer_vtable[IOMEMDESCWRITEBYTES_INDEX];

    uint64_t direction = get_dir_f(buffer);

    uint64_t byte_count = 0;
    uint64_t offset = 0;
    uint64_t length = 0;

    if (kIODirectionIn == direction) {
        for (i = 0; i < nblks; i++) {
            offset = BLOCK_SIZE * (i + block);
            length = BLOCK_SIZE;
            if ((offset + length) > members->size) {
                length = members->size - offset;
            }
            if ((offset + length) >= members->size + BLOCK_SIZE) {
                cancel();
            }

            qc_read_file(dev_buf, length, offset, members->qc_file_index);
            byte_count += write_bytes_f(buffer, (i * BLOCK_SIZE),
                                        dev_buf, length);
        }
    } else if (kIODirectionOut == direction) {
        for (i = 0; i < nblks; i++) {
            offset = BLOCK_SIZE * (i + block);
            length = BLOCK_SIZE;
            if ((offset + length) > members->size) {
                length = members->size - offset;
            }
            if ((offset + length) >= members->size + BLOCK_SIZE) {
                cancel();
            }

            byte_count += read_bytes_f(buffer, (i * BLOCK_SIZE),
                                       dev_buf, length);
            qc_write_file(dev_buf, length, offset, members->qc_file_index);
        }
    } else {
        cancel();
    }

    if (NULL != completion) {
        FuncCompletionAction comp_act_f = (FuncCompletionAction)completion[1];
        comp_act_f((uint64_t)completion[0], (uint64_t)completion[2], 0,
                   byte_count);
    }

    lck_mtx_unlock(members->lck_mtx);
    return 0;
}

void create_new_aleph_bdev(const char *prod_name, const char *vendor_name,
                           const char *mutex_name, uint64_t bdev_file_index,
                           void *parent_service)
{
    //TODO: release this object ref?
    void *bdev = OSMetaClass_allocClassWithName(BDEV_CLASS_NAME);
    if (NULL == bdev) {
        cancel();
    }
    void **vtable_ptr = (void **)*(uint64_t *)bdev;

    FuncIOServiceInit vfunc_init =
                (FuncIOServiceInit)vtable_ptr[IOSERVICE_INIT_INDEX];
    vfunc_init(bdev, NULL);

    AlephBDevMembers *members = get_bdev_members(bdev);
    members->qc_file_index = bdev_file_index;
    strncpy(&members->product_name[0], prod_name, VENDOR_NAME_SIZE);
    strncpy(&members->vendor_name[0], vendor_name, VENDOR_NAME_SIZE);
    members->vendor_name[0] += bdev_file_index;
    strncpy(&members->mutex_name[0], mutex_name, VENDOR_NAME_SIZE);
    members->mutex_name[0] += bdev_file_index;
    members->mtx_grp = lck_grp_alloc_init(&members->mutex_name[0], NULL);
    members->lck_mtx = lck_mtx_alloc_init(members->mtx_grp, NULL);
    members->size = qc_size_file(bdev_file_index);
    members->block_count = (members->size + BLOCK_SIZE - 1) / BLOCK_SIZE;

    if (NULL == parent_service) {
        cancel();
    }

    FuncIOServiceAttach vfunc_attach =
                (FuncIOServiceAttach)vtable_ptr[IOSERVICE_ATTACH_INDEX];
    vfunc_attach(bdev, parent_service);

    FuncIOSerivceRegisterService vfunc_reg_service =
        (FuncIOSerivceRegisterService)vtable_ptr[IOSERVICE_REG_SERVICE_INDEX];
    vfunc_reg_service(bdev, 0);
}
