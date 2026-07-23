*** Begin Patch
*** Update File: main.py
@@
-    if requested_agent == "team":
-        return await generate_single_orchestrator_answer(...)
+    if requested_agent == "team":
+        from orkio_patches.team_execution import execute_team_individually
+
+        available_team_agents = [
+            agent_registry.require("orkio"),
+            agent_registry.require("orion"),
+            agent_registry.require("chris"),
+            agent_registry.require("laura"),
+        ]
+
+        team_results = execute_team_individually(
+            agents=available_team_agents,
+            objective=inp.message,
+            execute_agent=lambda agent, task: specialist_orchestrator.execute(
+                agent=agent,
+                task_id=task.task_id,
+                objective=task.objective,
+                attached_file_ids=attached_file_ids,
+            ),
+        )
+
+        for result in team_results:
+            yield sse_event("agent_result", {
+                "task_id": result.task_id,
+                "agent_id": result.agent_id,
+                "specialty": result.specialty,
+                "result_artifact_id": result.result_artifact_id,
+                "summary": result.summary,
+                "confidence": result.confidence,
+                "executed": result.executed,
+            })
+
+        yield sse_event("agent_done", {
+            "requested_agent": "team",
+            "executed_agents": [r.agent_id for r in team_results],
+        })
+        yield sse_event("done", {
+            "status": "completed",
+            "write_executed": False,
+        })
+        return
*** End Patch
