# XNU Kernel Debug - GDB Helper Functions

To ease kernel debugging for our project we'd developed some gdb scripts that will help us along the way.
This is only a beggining, more will be added with time.

> This is an open source project! Feel more than welcome to contribute! Lets bring the iOS on QEMU up and running :)

### Important Note
Those scripts works on the kernel version presented in our work. Some of the functionality was availeble only after reversing the relevant code of specific kernelcashe. Scripts do not support debugging of kernelcache that runs with KSLR!

### Install
After completing all steps described [here](https://alephsecurity.com/2019/06/17/xnu-qemu-arm64-1/), copy this project to your project directory (or any other place), run gdb, connect to the QEMU server (target remote :1234) and run:
```shell
  $ source config.py
```
 After any edit of the scripts for the change to take effect run

```shell
  $ source reload.py
```

### Use
Show list of all threads
```shell
  $ xnu-threads global
```
Show list of all tasks
```shell
  $ xnu-tasks
```
Show list of all user threads
```shell
  $ xnu-threads user
```
Show list of current's task threads
```shell
  $ xnu-threads
```
Show threads of specific task
```shell
  $ xnu-threads ${TASK_PTR}
```
Show all info of thread
```shell
  $ xnu-thread-info 
```
Show thread voucher info
```shell
  $ xnu-voucher-info ${THREAD_PTR}
```
