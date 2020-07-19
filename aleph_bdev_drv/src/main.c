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
#include "aleph_fb_dev.h"
#include "aleph_fb_mclass.h"
#include "aleph_fbuc_dev.h"
#include "aleph_fbuc_mclass.h"

#include "hw/arm/guest-services/general.h"

#define NUM_BLOCK_DEVS_MAX (10)

#ifndef NUM_BLOCK_DEVS
#define NUM_BLOCK_DEVS (2)
#endif

void _start() __attribute__((section(".start")));

static uint8_t executed = 0;

void _start() {
    uint64_t i = 0;
    //in case the hook gets called more than once we want to make sure
    //it starts only once
    if (executed) {
        return;
    }
    executed = 1;

    if (NUM_BLOCK_DEVS > NUM_BLOCK_DEVS_MAX) {
        cancel();
    }

    register_bdev_meta_class();
    register_fb_meta_class();
    register_fbuc_meta_class();

    //TODO: release this object ref
    void *match_dict = IOService_serviceMatching("AppleARMPE", NULL);
    //TODO: release this object ref
    void *service = waitForMatchingService(match_dict, -1);
    //TODO: release this object ref
    if (0 == service) {
        cancel();
    }

    //TODO: release this object ref
    void *match_dict_disp = IOService_nameMatching("disp0", NULL);
    //TODO: release this object ref
    void *service_disp = waitForMatchingService(match_dict_disp, -1);

    if (0 == service_disp) {
        cancel();
    }

    char bdev_prod_name[] = "0AlephBDev";
    char bdev_vendor_name[] = "0Aleph";
    char bdev_mutex_name[] = "0AM";

    for (i = 0; i < NUM_BLOCK_DEVS; i++) {
        //TODO: release this object ref?
        bdev_prod_name[0]++;
        bdev_vendor_name[0]++;
        bdev_mutex_name[0]++;
        create_new_aleph_bdev(bdev_prod_name, bdev_vendor_name,
                              bdev_mutex_name, i, service);

        //TODO: hack for now to make the first registered bdev disk0 instead
        //of having the system change the order
        IOSleep(1000);
        ////wait for the first disk to be loaded as disk0
        //if (0 == i) {
        //    void *match_dict_first = IOService_serviceMatching("IOMediaBSDClient", NULL);
        //    void *service_first = waitForMatchingService(match_dict_first, -1);
        //}
    }

    create_new_aleph_fbdev(service_disp);
}
