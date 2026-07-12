ORKIO — OEC-004 IMMUTABLE AGENT OWNERSHIP
==========================================

BASELINE
- Built from uploaded file: main_98_retificado.py
- The complete replacement file is packaged as main.py.

FILES
- main.py
- runtime/agent_ownership_enforcement.py
- tests/test_oec004_agent_ownership_enforcement.py
- docs/orion/OEC004_IMMUTABLE_AGENT_OWNERSHIP.md
- OEC004_IMMUTABLE_AGENT_OWNERSHIP.diff

INSTALL
1. Create a backup/tag of the current backend.
2. Extract this ZIP at the repository root.
3. Confirm main.py replaced the current root main.py.
4. Run:
   python -m pytest -q tests/test_oec004_agent_ownership_enforcement.py
5. Deploy.
6. Test with Orion selected and a thread containing recent Chris context.

EXPECTED
- UI displays Orion.
- assistant_message.agent_name is Orion.
- final_speaker is Orion.
- AO45A is skipped.
- No frontend changes.
- No migration.
- No mutation permission changes.

ROLLBACK
- Restore previous main.py.
- Remove the new runtime helper, test and documentation.
