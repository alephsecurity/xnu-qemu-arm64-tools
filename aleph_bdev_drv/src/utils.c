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

#include "utils.h"
#include "kern_funcs.h"

void cancel()
{
    *(uint64_t *)(0) = 0xffffffffffffffff;
}

char *my_itoa(uint64_t num, char *str)
{
    char digits[64];
    char *dp;
    char *cp = str;

    if (num == 0) {
        *cp++ = '0';
    }
    else {
        dp = digits;
        while (num) {
            *dp++ = '0' + num % 10;
            num /= 10;
        }
        while (dp != digits) {
            *cp++ = *--dp;
        }
    }
    *cp++ = '\0';

    return str;
}

//Print to console
void log_uint64(const char *name, uint64_t num)
{
    char str[1024];

    IOLog(name);
    my_itoa((uint64_t)num, &str[0]);
    IOLog(&str[0]);
    IOLog("\n");
}
