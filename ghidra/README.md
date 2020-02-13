# GHIDRA- Color Executed Instructions

Given a file with the QEMU CPU trace, color the instructions that were executed in the program

TL;DR:
To get an CPU trace:
```
$qemu-system-aarch64 -d exec -D /tmp/qemu-trace.log ...
```
- Ghidra-> CodeBrowser-> Window -> Script Manager
- Find the script (filter by name) and run
- Choose the log file (/tmp/qemu-trace.log)
- To see better the actual flow of the program, it is better to use *Graph* window 
intead of *Listing*
---
This small script will color all executed instructions according to the provided trace log. That is, the previously executed program's flow will be available at any time it is needed during the reverse engineering task.

![](https://user-images.githubusercontent.com/9990629/74430108-e9893180-4e64-11ea-8c72-3b1bad4980ce.png)
