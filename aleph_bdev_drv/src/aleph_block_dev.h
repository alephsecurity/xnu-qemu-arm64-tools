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

#ifndef ALEPH_BLOCK_DEV_H
#define ALEPH_BLOCK_DEV_H

#define ALEPH_BDEV_MEMBERS_OFFSET (0x800)
#define ALEPH_BDEV_BUFFER_OFFSET (0x1000)
#define ALEPH_BDEV_BUFFER_SIZE (0x1000)
//just in case. IOBlockStorageDevice is of size 0x90
#define ALEPH_BDEV_SIZE (0x2000)

#define BLOCK_SIZE (0x1000)

#define BDEV_CLASS_NAME "AlephStorageBlockDevice"

typedef struct {
    void *mtx_grp;
    void *lck_mtx;
    uint64_t size;
    uint64_t block_count;
} AlephBDevMembers;

AlephBDevMembers *get_bdev_members(void *bdev);
void *get_bdev_buffer(void *bdev);
void *get_mclass_inst(void);

//our driver virtual functions
void *AlephBlockDevice_getMetaClass(void *this);
uint64_t AlephBlockDevice_reportRemovability(void *this, char *isRemovable);
uint64_t AlephBlockDevice_reportMediaState(void *this,
                                           char *mediaPresent,
                                           char *changedState);
uint64_t AlephBlockDevice_reportBlockSize(void *this, uint64_t *param);
uint64_t AlephBlockDevice_reportMaxValidBlock(void *this, uint64_t *param);
uint64_t AlephBlockDevice_somefunc3(void *this, char *param);
char *AlephBlockDevice_getVendorString(void *this);
char *AlephBlockDevice_getProductString(void *this);
uint64_t AlephBlockDevice_doAsyncReadWrite(void *this, void **buffer,
                                         uint64_t block, uint64_t nblks,
                                         void *attrs, void **completion);

//used for the last param of the AlephBlockDevice_doAsyncReadWrite() func
typedef void (*FuncCompletionAction)(uint64_t p1, uint64_t p2,
                                     uint64_t p3, uint64_t p4);

//IOStorageBlockDevice virtual function defs
typedef void (*FuncIOStorageBdevInit)(void *this, void *dict);
typedef void (*FuncIOStorageBdevRegisterService)(void *this, uint64_t opts);

//IOStorageBlockDevice virtual function indices

#define IOSTORAGEBDEV_GETMCLASS_INDEX (7)
#define IOSTORAGEBDEV_INIT_INDEX (20)
#define IOSTORAGEBDEV_REG_SERVICE_INDEX (83)
#define IOSTORAGEBDEV_GETVENDORSTRING_INDEX (171)
#define IOSTORAGEBDEV_GETPRODUCTSTRING_INDEX (172)
#define IOSTORAGEBDEV_REPORTBSIZE_INDEX (175)
#define IOSTORAGEBDEV_REPORTMAXVALIDBLOCK_INDEX (177)
#define IOSTORAGEBDEV_REPORTMEDIASTATE_INDEX (178)
#define IOSTORAGEBDEV_REPORTREMOVABILITY_INDEX (179)
#define IOSTORAGEBDEV_SOMEFUNC3_INDEX (180)
#define IOSTORAGEBDEV_DOASYNCREADWRITE_INDEX (183)

#endif
