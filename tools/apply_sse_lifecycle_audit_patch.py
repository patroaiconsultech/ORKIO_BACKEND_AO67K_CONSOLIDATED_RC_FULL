from pathlib import Path

TARGET = Path("main.py")

INSERTIONS = [
    {
        "name": "first_status_yield_audit",
        "old": b'logger.warning("AO29_BEFORE_FIRST_STATUS_YIELD trace_id=%s thread_id=%s", trace_id, tid_seed)\r\n        except Exception:',
        "new": b'logger.warning("AO29_BEFORE_FIRST_STATUS_YIELD trace_id=%s thread_id=%s", trace_id, tid_seed)\r\n            logger.warning("SSE_STATUS_YIELD_ATTEMPT trace_id=%s thread_id=%s", trace_id, tid_seed)\r\n        except Exception:',
        "sentinel": b"SSE_STATUS_YIELD_ATTEMPT",
    },
    {
        "name": "stream_exit_normal_audit",
        "old": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=normal", trace_id, tid_seed)\r\n            except Exception:',
        "new": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=normal", trace_id, tid_seed)\r\n                logger.warning("SSE_STREAM_EXIT_REACHED trace_id=%s thread_id=%s reason=normal", trace_id, tid_seed)\r\n            except Exception:',
        "sentinel": b"SSE_STREAM_EXIT_REACHED",
    },
    {
        "name": "stream_exit_cancelled_audit",
        "old": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=cancelled", trace_id, tid_seed)\r\n            except Exception:',
        "new": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=cancelled", trace_id, tid_seed)\r\n                logger.warning("CLIENT_CANCELLED_BEFORE_FIRST_EVENT trace_id=%s thread_id=%s", trace_id, tid_seed)\r\n            except Exception:',
        "sentinel": b"CLIENT_CANCELLED_BEFORE_FIRST_EVENT",
    },
    {
        "name": "stream_exit_exception_audit",
        "old": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=exception", trace_id, tid_seed)\r\n            except Exception:',
        "new": b'logger.warning("AO29_STREAM_EXIT trace_id=%s thread_id=%s reason=exception", trace_id, tid_seed)\r\n                logger.warning("SSE_STREAM_EXIT_REACHED trace_id=%s thread_id=%s reason=exception", trace_id, tid_seed)\r\n            except Exception:',
        "sentinel": b'SSE_STREAM_EXIT_REACHED trace_id=%s thread_id=%s reason=exception',
    },
]

def main() -> int:
    if not TARGET.exists():
        raise SystemExit("TARGET_NOT_FOUND: main.py")

    data = TARGET.read_bytes()
    changed = []
    missing = []

    for item in INSERTIONS:
        if item["sentinel"] in data:
            continue
        if item["old"] not in data:
            missing.append(item["name"])
            continue
        data = data.replace(item["old"], item["new"], 1)
        changed.append(item["name"])

    if missing:
        raise SystemExit("MARKER_NOT_FOUND: " + ",".join(missing))

    if not changed:
        print("NO_CHANGE: all audit markers already present")
        return 0

    TARGET.write_bytes(data)
    print("PATCHED main.py")
    for item in changed:
        print(f"- {item}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
