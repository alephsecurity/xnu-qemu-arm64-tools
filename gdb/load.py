import os
import sys
import traceback
import importlib
import logging

sys.path.insert(0, os.path.dirname(os.path.expanduser(__file__)))
logging.getLogger("xnu").setLevel(logging.WARNING)
MODULES_TO_IPMORT = [
    "xnu.constants",
    "xnu.utils",
    "xnu.sys_info",
    "xnu.zone",
    "xnu.xnu_types",
    "xnu.tasks",
    ]

try:
    for module in MODULES_TO_IPMORT:
        if module not in sys.modules:
            importlib.import_module(module)
        else:
            importlib.reload(importlib.import_module(module))

except Exception as error:
    gdb.write(
        f"NOTE: Could not init the gdb module: {error} {traceback.format_exc()}\n")
