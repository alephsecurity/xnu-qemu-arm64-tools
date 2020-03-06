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

#include "mclass_reg.h"
#include "kern_funcs.h"
#include "aleph_block_dev.h"
#include "utils.h"

#include "hw/arm/guest-services/general.h"

void add_to_classes_dict(char *name, void **mc)
{
    uint32_t *dict = *(uint32_t **)SALLCLASSESDICT_PTR;
    if (NULL == dict) {
        cancel();
    }

    //fOptions =& ~kImmutable
    dict[4] = dict[4] & ~(uint32_t)1;
    void *sym = OSSymbol_withCStringNoCopy(name);
    OSDictionary_setObject((void *)dict, sym, mc);

    char *c_class_name = (char *)mc[3];
    if (NULL != c_class_name) {
        mc[3] = OSSymbol_withCStringNoCopy(c_class_name);
    }
}

void mclass_reg_alock_lock()
{
    if (NULL == *(void **)SALLCLASSESLOCK_PTR) {
        cancel();
    }
    lck_mtx_lock(*(void **)SALLCLASSESLOCK_PTR);
}

void mclass_reg_alock_unlock()
{
    lck_mtx_unlock(*(void **)SALLCLASSESLOCK_PTR);
}

void mclass_reg_slock_lock()
{
    if (NULL == *(void **)SSTALLEDCLASSESLOCK_PTR) {
        cancel();
    }
    lck_mtx_lock(*(void **)SSTALLEDCLASSESLOCK_PTR);
}

void mclass_reg_slock_unlock()
{
    lck_mtx_unlock(*(void **)SSTALLEDCLASSESLOCK_PTR);
}

