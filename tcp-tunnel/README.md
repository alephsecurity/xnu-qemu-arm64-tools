# tcp-tunnel

Used for tunneling TCP connections into and out of an iOS system emulated on
QEMU.

## Prerequisites

The following environment variables are required:

* `IOS_DIR` - this should point to the location of the kernelcache, the
disk images, etc.
* `QEMU_DIR` - this should point to the root of the [QEMU with iOS] source tree
(make sure it is up to date).

To use the project for SSH connections, the disk image should contain the
dropbear binary. The easiest way to obtain it is through [rootlessJB]. The
Dropbear needs an SSH key to run correctly (it can generate those on the fly, but since the filesystem is
mounted read-only, the workaround is to generate the key offline, and copy it
to the RAM disk image before boot). To generate it offline, install `dropbear`
(for example, via `brew install dropbear`), and then use the `dropbearkey`
command.

## Building

Just run `make` to build the binary, and `make install` to sign, update the trust cache and copy the binary to the disk
image. Notice that a new hash is added to the trust cache after each successful `make install`,
so it will contain quite a bit of garbage after a while.

## Running

A basic execution of the tunnel looks like this:

```tunnel 2222:127.0.0.1:22```

This will spawn an inward tunnel (from the outside world into the iOS system),
that will forward connections to port 2222 on the host to port 22 on the iOS
system. This is obviously only useful when Dropbear is executed - this is
achieved with the following command:

```/jb/usr/local/dropbear -r /var/dropbear/dropbear_ecdsa_host_key```

This, of course, assumes that iosbinpack has been extracted into the `/jb`
directory, and that an SSH key has been generated and put into `/var/dropbear`.

Alternatively, outward connections can be tunnelled, as well:

```tunnel out:80:93.184.216.34:80```

The above command will allow connections from the iOS system on port 80 to
`example.com`.

The tunnel runs in the foreground. It can be shut down by pressing
<kbd>Ctrl</kbd>+<kbd>C</kbd>. All open sockets and connections are properly
closed upon shut down.

If background operation is required, the tunnel can be executed with the `-d`
(or `--daemonize`) command line argument (it must appear first, as the
address spec is expected to be the last argument). This argument will cause the
tunnel to fork into the background.

[QEMU with iOS]: https://github.com/alephsecurity/xnu-qemu-arm64-private.git
[rootlessJB]: https://github.com/jakeajames/rootlessJB

