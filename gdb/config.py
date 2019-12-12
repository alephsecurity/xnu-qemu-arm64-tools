import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.expanduser(__file__)))

try:
    import xnu.zone
    import xnu.tasks
    import xnu.utils
    import xnu.sys_info
    import xnu.log
    import xnu.xnu_types
    import xnu.constants
except:
    gdb.write(f"NOTE: Could not init the gdb module: {traceback.format_exc()}\n")
