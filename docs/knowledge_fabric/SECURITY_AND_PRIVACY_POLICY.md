# Security and Privacy Policy — Knowledge Fabric

## Principles

1. Google Drive is a source, not a runtime truth store.
2. Personal content must not be used for institutional answers.
3. Roadmap and brainstorm material must not be presented as production capability.
4. No document may enter runtime context without review and approval.
5. Service account secrets must never be committed to the repository.

## Default blocks

- Direct runtime RAG from Drive.
- Auto-canonization.
- Auto-publication.
- Auto-execution based on Drive content.
- Use of personal/founder-private material without explicit authorization.

## Required review states

- `blocked_pending_owner_review`
- `manual_review_required`
- `review_required`
- `approved_for_canon_candidate`
- `approved_for_runtime_context`

Only the last state may be used by Orkio runtime, and only after explicit human approval.
