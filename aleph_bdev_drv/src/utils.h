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

#ifndef UTILS_H
#define UTILS_H

void cancel();

char *my_itoa(uint64_t num, char *str);
void log_uint64(const char *name, uint64_t num);

//IOMemoryDescriptor virtual function defs

typedef uint64_t (*FuncIOMemDescGetDirection)(void *this);
typedef uint64_t (*FuncIOMemDescReadBytes)(void *this, uint64_t offset,
                                           void *bytes, uint64_t length);
typedef uint64_t (*FuncIOMemDescWriteBytes)(void *this, uint64_t offset,
                                            void *bytes, uint64_t length);

//IOMemoryDescriptor virtual function indices

#define IOMEMDESCGETDIRECTION_INDEX (20)
#define IOMEMDESCREADBYTES_INDEX (24)
#define IOMEMDESCWRITEBYTES_INDEX (25)

#endif
