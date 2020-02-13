
# xnu-qemu-arm64-tools-private


*This repository includes the tools we use to boot/debug iOS kernel above QEMU.*

## bootstrap_scripts ##
Python scripts used for extract, decode, decompress the needed files to load the iOS kernel on QEMU.

## gdb ##
GDB-Python scripts that enable to analyze the kernel in run time (print threads, tasks, etc)

## ghidra ##
Ghidra scripts that we wrote to ease the reverse engineering process.

## pic-binary ##
A sample PIC (position-independent code) binary, that can be loaded into kernel memory for execution.

## aleph_bdev_drv ##
Custom Block Device Driver that is used to mount two block devices into iOS.

## tcp-tunnel ##
Used for tunneling TCP connections into and out of an iOS system emulated on QEMU.
