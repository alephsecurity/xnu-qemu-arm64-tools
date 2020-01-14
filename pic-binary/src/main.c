#include <libkern/libkern.h>
#include <libkern/OSRuntime.h>
#include <mach/mach_types.h>
#include <string.h>

void _start() __attribute__((section(".start")));

void _start() {
    char str[] = "Hello, PIC world!";
    char *buf = kern_os_malloc(sizeof(str));

    memcpy(&str[7], "iOS", 3);
    memcpy(buf, str, strlen(str));

}