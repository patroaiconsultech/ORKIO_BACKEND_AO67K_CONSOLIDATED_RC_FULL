import traceback

print("AO01_IMPORT_PROBE_START")

try:
    import app.main
    print("IMPORT_OK")
except Exception:
    traceback.print_exc()
    raise
