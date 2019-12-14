# XNU Kernel Debug - GDB Helper Functions

To ease kernel debugging for our project we'd developed some gdb scripts that will help us along the way.
Here listed what had been implemented already, just use find to search for information that you looking for, if it is not here - PR it :) 

> This is an open source project! Feel more than welcome to contribute! Lets bring the iOS on QEMU up and running :)

### Important Note
Those scripts works on the kernel version presented in our work. Some of the functionality was availeble only after reversing the relevant code of specific kernelcashe. Scripts do not support debugging of kernelcache that runs with KSLR!

### Install
After completing all steps described [here](https://alephsecurity.com/2019/06/17/xnu-qemu-arm64-1/), copy this project to your project directory (or any other place), run gdb, connect to the QEMU server (target remote :1234) and run:
```shell
  $ source load.py
```
 Also, run it after any edit of the scripts for the change to take effect

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
Show threads of specific *task*
```shell
  $ xnu-threads ${TASK_PTR}
```
Show all parsed info of specific *thread*
```shell
  $ xnu-thread-info ${THREAD_PTR}
```
Show all parsed info of specific *task*
```shell
  $ xnu-task-info ${TASK_PTR}
```
Print the metadata of all the kernel allocation zones
```shell
  $ xnu-zones
```
Show *is_table* of *itk_space* of specific *task*/*space*
```shell
  $ xnu-ipc_entry-list -task ${TASK_PTR}
  $ xnu-ipc_entry-list -space ${SPACE_PTR}
```
Show parsed info of *ipc_port*
```shell
  $ xnu-ipc-port-info ${IPC_PORT_PTR}
```
Show *ipc_voucher* info of specific *thread*
```shell
  $ xnu-voucher-info ${THREAD_PTR}
```
