# Custom Block Device Driver for iOS Kernel

Up until now, we had the whole system written to ramdisk. Ramdisk block device has two big disadvantages:
1. No support for disk larger than 1.5 GB.
2. Ramdisk is read-only.

So we decided to write a block device driver by ourselves

To execute the driver we will hook one of the kernel's functions. Because the driver is executed by hooking the kernel code, we need to compile the driver to flat binary. 

We will use the same technique that was described in [pic-binary](https://github.com/alephsecurity/xnu-qemu-arm64-tools-private/blob/master/pic-binary/README.md).

### Instructions

1. Get the XNU sources from Apple's Github:
```
$ git clone https://github.com/apple/darwin-xnu.git 
```
2. Get the xnu-qemu-arm64 sources from Aleph:
```
$ git clone https://github.com/alephsecurity/xnu-qemu-arm64.git
```
3. Get the xnu-qemu-arm64-tools sources:
```
$ git clone https://github.com/alephsecurity/xnu-qemu-arm64-tools.git
```
4. Get the Cross Compiler for AARCH64. We will use the toolchain provided by @github/SergioBenitez:
```
$ brew tap SergioBenitez/osxct
$ brew install aarch64-none-elf
```
5. To be able to use the functions from the iOS Kernel within the driver code, we need to link the driver along with the symbols from the kernel.

Import the `kernelcache.release.n66.out` binary
![](https://user-images.githubusercontent.com/9990629/74612553-fc269380-510e-11ea-98d0-ed7cd3ce948b.png)
Import as single file
![](https://user-images.githubusercontent.com/9990629/74612596-57588600-510f-11ea-9832-8520572cc98e.png)
Go to Window->Symbol Table. Select All. Export the symbols from the iOS Kernel into csv file (Can be done with Ghidra):
![](https://user-images.githubusercontent.com/9990629/74463818-16583b80-4e9b-11ea-99fc-1649fcc8df18.png)
6. Create the Environment Variables
```
$ export XNU_SOURCES=path_dir_to_darwin-xnu
$ export KERNEL_SYMBOLS_FILE=path_dir_to_symbols.csv
$ export QEMU_DIR=path_dir_to_xnu-qemu-arm64
$ export NUM_BLOCK_DEVS=2
```
7. Build
```
$ make
```

The compilation process generated `bin/aleph_bdev_drv.bin`, the flat compiled code of the driver.

Now that we have the driver compiled we can use it by the hook mechanism implemented in the [alephsecurity/xnu-qemu-arm64](https://github.com/alephsecurity/xnu-qemu-arm64)
