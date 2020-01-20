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
#include "aleph_block_dev.h"
#include "aleph_bdev_mclass.h"

#include "hw/arm/guest-services/general.h"

void _start() __attribute__((section(".start")));

static uint8_t executed = 0;

void _start() {
    //in case the hook gets called more than once we want to make sure
    //it starts only once
    if (executed) {
        return;
    }
    executed = 1;

    register_bdev_meta_class();
    void *bdev = OSMetaClass_allocClassWithName(BDEV_CLASS_NAME);
    if (NULL == bdev) {
        cancel();
    }
    void **vtable_ptr = (void **)*(uint64_t *)bdev;

    FuncIOStorageBdevInit vfunc_init =
                (FuncIOStorageBdevInit)vtable_ptr[IOSTORAGEBDEV_INIT_INDEX];
    vfunc_init(bdev, NULL);

    AlephBDevMembers *members = get_bdev_members(bdev);
    members->mtx_grp = lck_grp_alloc_init("AlephStorageDevMtx", NULL);
    members->lck_mtx = lck_mtx_alloc_init(members->mtx_grp, NULL);
    members->size = qc_size_file(0);
    members->block_count = (members->size + BLOCK_SIZE - 1) / BLOCK_SIZE;

    void *match_dict = IOService_serviceMatching("AppleARMPE", NULL);
    void *service = waitForMatchingService(match_dict, 0);
    if (0 == service) {
        cancel();
    }

    IOService_attach(bdev, service);

    FuncIOStorageBdevRegisterService vfunc_reg_service =
        (FuncIOStorageBdevRegisterService)vtable_ptr[IOSTORAGEBDEV_REG_SERVICE_INDEX];
    vfunc_reg_service(bdev, 0);
}
