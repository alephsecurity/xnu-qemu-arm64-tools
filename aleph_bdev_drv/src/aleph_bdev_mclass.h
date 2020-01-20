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

#ifndef ALEPH_BDEV_MCLASS_H
#define ALEPH_BDEV_MCLASS_H

//just in case not sure how much is required
#define ALEPH_MCLASS_SIZE (0x1000)

//not sure what the original vtable size is, use this for now
#define BDEV_VTABLE_SIZE (0x1000)

typedef void (*VoidFunc)(void);
typedef void* (*AllocFunc)(void);
typedef void (*ObjConstructor)(void *);

typedef struct {
    VoidFunc destructor1;
    VoidFunc destructor2;
    VoidFunc release1;
    VoidFunc getRetainCount;
    VoidFunc retain;
    VoidFunc release2;
    VoidFunc serialize;
    VoidFunc getMetaClass;
    VoidFunc isEqualTo;
    VoidFunc taggedRetain;
    VoidFunc taggedRelease1;
    VoidFunc taggedRelease2;
    AllocFunc alloc;
} MetaClassVTable;

void create_bdev_vtable(void);
void create_bdev_metaclass_vtable(void);
void register_bdev_meta_class();

//our driver metaclass virtual functions
void *bdev_alloc(void);

#endif
