import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

try:
    import xnu.tasks
    import xnu.utils
    import xnu.sys_info
    import xnu.log
    import xnu.xnu_types
    import xnu.constants
except:
    gdb.write("NOTE: Could not init the gdb module.\n")