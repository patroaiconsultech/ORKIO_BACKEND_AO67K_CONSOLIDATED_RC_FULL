*** Begin Patch
*** Update File: main.py
@@
-            input_model = (
-                GlipAriaDocumentArtifactGenerateIn.model_validate(input_payload)
-                if owner_slug == "aria"
-                else DocumentArtifactGenerateIn.model_validate(input_payload)
-            )
+            # AO-01 PREMIUM: keep strict Pydantic validation, but remove
+            # builder-only metadata not declared by the target contract.
+            from orkio_patches.document_payload_guard import validate_document_payload
+
+            input_model = (
+                validate_document_payload(
+                    GlipAriaDocumentArtifactGenerateIn,
+                    input_payload,
+                )
+                if owner_slug == "aria"
+                else validate_document_payload(
+                    DocumentArtifactGenerateIn,
+                    input_payload,
+                )
+            )
@@
-        ao01_agent_turn_context = resolve_agent_turn_context(...)
+        ao01_agent_turn_context = resolve_agent_turn_context(...)
+        from orkio_patches.agent_ownership import (
+            AgentTurnContext as PremiumAgentTurnContext,
+            enforce_explicit_agent_ownership,
+        )
+        _ctx = PremiumAgentTurnContext(
+            requested_agent=ao01_agent_turn_context.requested_agent,
+            orchestrator_agent=ao01_agent_turn_context.orchestrator_agent,
+            turn_owner=ao01_agent_turn_context.turn_owner,
+            display_agent=ao01_agent_turn_context.display_agent,
+            technical_lead=ao01_agent_turn_context.technical_lead,
+            route_family=ao01_agent_turn_context.route_family,
+            ownership_locked=ao01_agent_turn_context.ownership_locked,
+        )
+        _ctx = enforce_explicit_agent_ownership(
+            _ctx,
+            available_agents={"orkio", "orion", "chris", "laura"},
+        )
+        ao01_agent_turn_context = ao01_agent_turn_context._replace(
+            turn_owner=_ctx.turn_owner,
+            display_agent=_ctx.display_agent,
+            ownership_locked=_ctx.ownership_locked,
+        )
@@
-            owner_slug = "orkio"
+            # AO-01 PREMIUM: document work follows immutable ownership.
+            from orkio_patches.document_agent_resolver import resolve_document_agent
+            owner_slug = resolve_document_agent(ao01_agent_turn_context)
*** End Patch
