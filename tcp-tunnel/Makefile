ifndef IOS_DIR
$(error IOS_DIR is not set)
endif

ifndef QEMU_DIR
$(error QEMU_DIR is not set)
endif

src := $(wildcard src/*.c) $(wildcard src/**/*.c)

CC = clang
FLAGS = -DOUT_OF_TREE_BUILD -I$(QEMU_DIR)/include -fno-stack-check -fno-stack-protector -arch arm64 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk
TARGET = tunnel

bin/$(TARGET): $(src)
	@echo "Compiling from source..."
	@mkdir -p bin
	@$(CC) -o $@ $(FLAGS) $^
	
.PHONY: clean
clean:
	rm -f bin/$(TARGET)

.PHONY: install
install: bin/$(TARGET)
	@echo "Installing into the iOS image..."
	@hdiutil attach -imagekey diskimage-class=CRawDiskImage $(IOS_DIR)/hfs.main
	@sudo cp $^ /Volumes/PeaceB16B92.arm64UpdateRamDisk/bin/
	@hdiutil detach /Volumes/PeaceB16B92.arm64UpdateRamDisk
	@echo "Signing with entitlements..."
	@jtool --sign --ent ent.xml --inplace $^
	@jtool --sig --ent $^ | grep CDHash | cut -d' ' -f6 | cut -c 1-40 >> $(IOS_DIR)/tchashes
	@echo "Updating static trustcache..."
	@python $(IOS_DIR)/xnu-qemu-arm64-tools/bootstrap_scripts/create_trustcache.py $(IOS_DIR)/tchashes $(IOS_DIR)/static_tc
