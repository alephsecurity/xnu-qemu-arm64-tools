src := $(wildcard src/*.c) $(wildcard src/**/*.c)

ifndef XNU_SOURCES
$(error XNU_SOURCES not set!)
endif

ifndef KERNEL_SYMBOLS_FILE
$(error KERNEL_SYMBOLS_FILE not set!)
endif

ifndef QEMU_DIR
$(error QEMU_DIR is not set)
endif

ifndef NUM_BLOCK_DEVS
$(error NUM_BLOCK_DEVS is not set)
endif

TARGET = bin/aleph_bdev_drv
CROSS = aarch64-none-elf-
CC = $(CROSS)gcc
OBJCOPY = $(CROSS)objcopy
LDFLAGS = -Wl,-T,flat.ld,-N
DEFINES = -DOUT_OF_TREE_BUILD -DBCM2837 -DKERNEL -DXNU_KERNEL_PRIVATE -D__arm64__ -D__LITTLE_ENDIAN__ -DNUM_BLOCK_DEVS=$(NUM_BLOCK_DEVS)
INCLUDES = -I$(XNU_SOURCES)/bsd \
           -I$(XNU_SOURCES)/osfmk \
           -I$(XNU_SOURCES)/osfmk/libsa \
           -I$(XNU_SOURCES)/libkern \
           -I$(XNU_SOURCES)/pexpert \
           -I$(XNU_SOURCES)/EXTERNAL_HEADERS \
           -I$(QEMU_DIR)/include
CFLAGS = -fpie -flto -fwhole-program -fno-plt -nostdlib -nostartfiles $(DEFINES) $(LDFLAGS) $(INCLUDES)

$(TARGET).bin: $(TARGET).elf
	@echo "Creating a flat binary..."
	@$(OBJCOPY) -O binary $^ $@

$(TARGET).elf: $(src) kernel.ld
	@echo "Building elf from source..."
	@$(CC) -o $@ $(CFLAGS) $(src)

kernel.ld:
	@echo "Generating symbols for linker..."
	@python3 getsymbols.py $(KERNEL_SYMBOLS_FILE) $@

.PHONY: clean
clean:
	rm kernel.ld
	rm -f $(TARGET)*
