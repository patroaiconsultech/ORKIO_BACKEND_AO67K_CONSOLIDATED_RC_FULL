from pathlib import Path
import importlib.util

module_path = Path(__file__).resolve().parents[1] / "runtime" / "direct_chat_persistence.py"
spec = importlib.util.spec_from_file_location("direct_chat_persistence", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FakeDB:
    def __init__(self):
        self.added = []
        self.committed = False
        self.rolled_back = False
    def add(self, item):
        self.added.append(item)
    def commit(self):
        self.committed = True
    def rollback(self):
        self.rolled_back = True

class FakeMessage:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class FakeLogger:
    def info(self, *args, **kwargs):
        pass
    def exception(self, *args, **kwargs):
        pass

db = FakeDB()
result = module.persist_direct_assistant_message(
    db=db,
    org="default",
    text="ok",
    thread_id="thread-1",
    Message=FakeMessage,
    select=None,
    new_id=lambda: "msg-1",
    now_ts=lambda: 123,
    logger=FakeLogger(),
    trace_id="trace-1",
    agent_id=None,
    agent_name="Orkio",
)

assert db.committed is True
assert db.rolled_back is False
assert result["assistant_message_id"] == "msg-1"
assert result["thread_id"] == "thread-1"
assert db.added[0].content == "ok"
print("AO72_HF3_DIRECT_CHAT_PERSISTENCE_SMOKE_PASS")
