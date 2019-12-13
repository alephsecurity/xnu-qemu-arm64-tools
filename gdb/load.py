import os
import sys
import traceback
import importlib
import logging

sys.path.insert(0, os.path.dirname(os.path.expanduser(__file__)))
logging.getLogger("xnu").setLevel(logging.WARNING)
MODULES_TO_IPMORT = [
    "xnu.zone",
    "xnu.tasks",
    "xnu.utils",
    "xnu.sys_info",
    "xnu.xnu_types",
    "xnu.constants"]

try:
    for module in MODULES_TO_IPMORT:
        if module not in sys.modules:
            importlib.import_module(module)
        else:
            importlib.reload(importlib.import_module(module))

except Exception:
    gdb.write(
        f"NOTE: Could not init the gdb module: {traceback.format_exc()}\n")
