import sys
import sysconfig

is_freethreaded = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
gil_status = sys._is_gil_enabled()

if gil_status:
    print("GIL is enabled.")
else:
    print("GIL is disabled.")

print(f"Python support Free-threaded: {is_freethreaded}")
