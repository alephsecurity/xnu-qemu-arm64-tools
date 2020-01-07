# pic-binary

A sample PIC (position-independent code) binary, that can be loaded into kernel
memory for execution.

## Prerequisites

### Kernel Sources

Get the XNU sources from Apple's Github:

```
git clone https://github.com/apple/darwin-xnu.git
```

Set the environment variable `XNU_SOURCES` to point to the darwin-xnu folder,
for example:

```
export XNU_SOURCES=/Users/aronsky/Source/darwin-xnu
```

### ARM64 GCC cross-compiler

Use aarch64-none-elf-gcc, availabe from Sergio Benitez through Homebrew:

```
$ brew tap SergioBenitez/osxct
$ brew install aarch64-none-elf
```

### Kernel Symbols CSV

From Ghidra, export the symbols to a CSV by opening the symbol table
(Window->Symbol Table), selecting all the symbols, right-clicking the
selection, and choosing Export->Export to CSV:

![Export to CSV](https://1.bp.blogspot.com/-MY1TykT2Qic/XRqlzEcdtRI/AAAAAAAABK8/z6M1WuahFS8J3GRpY7UNWIppvLtlN5XOACLcBGAs/s1600/lst2x64dbg%282%29.png)

Set the environment variable `KERNEL_SYMBOLS_FILE` to point to the exported
file.

## Writing New Code

Writing new code should work out of the box. In theory, any stuff that's
available through the XNU headers should be usable. However, there are two
limitations:

* Correct include folders: the include folders of XNU are not set up for
driver development (a la SDK), but for building the kernel. Therefore, some
changes might be required for the `INCLUDES` variable in the Makefile.
* The linking step depends on the presence of the relevant symbols in the
kernel. If a symbol is missing, the function needs to be found and created in
Ghidra (make sure to add an `_` in front of the name), and the CSV file has to
be exported again.

## Building

Just run `make` to build the code. The command will produce two files:

* `bin/pic.elf` - a regular ELF binary (albeit with reduced number of segments)
* `bin/pic.bin` - a flat binary with all the required sections, to be loaded
into the kernel for execution

## Running

This section is not ready - to be continued...