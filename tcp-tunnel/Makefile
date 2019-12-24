ifndef IOS_DIR
$(error IOS_DIR is not set)
endif

ifndef QEMU_DIR
$(error QEMU_DIR is not set)
endif

ifndef IOSBINPACK_DIR
IOSBINPACK_DIR = jb
endif

src := $(wildcard src/*.c) $(wildcard src/**/*.c)

CC = clang
FLAGS = -DOUT_OF_TREE_BUILD -I$(QEMU_DIR)/include -fno-stack-check -fno-stack-protector -arch arm64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk

bin/tunnel: $(src)
	@echo "Compiling from source..."
	$(CC) -o $@ $(FLAGS) $^
	jtool --sign --ent ent.xml --inplace $@
	jtool --sig --ent $@ | grep CDHash | cut -d' ' -f6 | cut -c 1-40 >> $(IOS_DIR)/tchashes
	python $(IOS_DIR)/xnu-qemu-arm64-scripts/create_trustcache.py $(IOS_DIR)/tchashes $(IOS_DIR)/static_tc

.PHONY: clean
clean:
	rm -f bin/tunnel

.PHONY: install
install: bin/tunnel
	@echo "Installing into the iOS image..."
	hdiutil attach -imagekey diskimage-class=CRawDiskImage $(IOS_DIR)/048-32651-104.dmg.out
	sudo cp $^ /Volumes/PeaceB16B92.arm64UpdateRamDisk/$(IOSBINPACK_DIR)/usr/bin/
	hdiutil detach /Volumes/PeaceB16B92.arm64UpdateRamDisk