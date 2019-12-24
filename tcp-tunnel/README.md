# tcp-tunnel

Used for tunneling TCP connections into and out of an iOS system emulated on
QEMU.

## Prerequisites

The following environment variables are required:

* `IOS_DIR` - this should point to the location of the kernelcache, the RAM
disk images, etc.
* `QEMU_DIR` - this should point to the root of the QEMU source tree
(with guest-services support).
* `IOSBINPACK_DIR` - this should be the name of the root folder in the RAM
disk, that contains binaries from iosbinpack. This environment variable is
optional, and defaults to `jb`.

To use the project for SSH connections, the RAM disk image should contain the
dropbear binary. The easiest way to obtain it is through iosbinpack. The
Makefile assumes its extracted into a folder named `jb` (this can be changed
with the `IOSBINPACK_DIR` environment variable). Dropbear needs an SSH key to
run correctly (it can generate those on the fly, but since the filesystem is
mounted read-only, the workaround is to generate the key offline, and copy it
to the RAM disk image before boot). To generate it offline, install `dropbear`
(for example, via `brew install dropbear`), and then use the `dropbearkey`
command.

For an easier workflow, it's worth to symlink the binaries from `jb/bin`,
`jb/usr/bin`, etc. into the corresponding `/bin`, `/usr/bin`, etc. directories.
It is, in fact, a requirement for executing `scp`, since it doesn't respect the
`PATH` enviornment variable when spawned.

## Building

Just run `make` to build, and `make install` to copy the output to the RAM disk
image. The build process takes care of updating the trust cache. However,
notice that a new hash is added to the trust cache after each successful build,
so it will contain quite a bit of garbage after a while.

## Running

A basic execution of the tunnel looks like this:

```tunnel in 2222:127.0.0.1:22```

This will spawn an inward tunnel (from the outside world into the iOS system),
that will forward connections to port 2222 on the host to port 22 on the iOS
system. This is obviously only useful when Dropbear is executed - this is
achieved with the following command:

```/jb/usr/local/dropbear -r /var/dropbear/dropbear_ecdsa_host_key```

This, of course, assumes that iosbinpack has been extracted into the `/jb`
directory, and that an SSH key has been generated and put into `/var/dropbear`.

Alternatively, outward connections can be tunnelled, as well:

```tunnel out 80:93.184.216.34:80```

The above command will allow connections from the iOS system on port 80 to
`example.com`.
