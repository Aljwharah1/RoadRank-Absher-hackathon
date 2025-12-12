import importlib, traceback
try:
    importlib.invalidate_caches()
    importlib.import_module('main')
    print('OK: main imported')
except Exception:
    traceback.print_exc()
