from evolution.conversation.batch import ConversationBatchProcessor
from evolution.conversation.idempotency import make_idempotency_key


conversation_a = "Vamos corrigir o erro no Knowledge Bridge."
conversation_b = "Decidimos registrar o risco e criar melhoria no Distiller."
conversation_a_duplicate = "  vamos   corrigir o erro no Knowledge Bridge.  "

processor = ConversationBatchProcessor()
report = processor.distill_batch([conversation_a, conversation_b, conversation_a_duplicate, ""])

assert report.processed == 2
assert report.duplicates == 1
assert report.skipped == 2
assert len(report.results) == 4

processed = [item for item in report.results if item.status == "processed"]
duplicates = [item for item in report.results if item.status == "duplicate"]
skipped = [item for item in report.results if item.status == "skipped"]

assert len(processed) == 2
assert len(duplicates) == 1
assert len(skipped) == 1

assert processed[0].idempotency_key == make_idempotency_key(conversation_a)
assert duplicates[0].idempotency_key == make_idempotency_key(conversation_a)
assert processed[0].result is not None
assert processed[1].result is not None

print("OEP004_2_BATCH_IDEMPOTENCY_PASS")
