from __future__ import annotations

from typing import Dict, List

from .models import Proposal

OEP_001_SIMULATION_ENGINE_VERSION = "OEP_001_SIMULATION_ENGINE_V1"

class SimulationEngine:
    def simulate(self, proposal: Proposal) -> Dict[str, object]:
        impacted = self._impacted_layers(proposal.files or [])
        return {
            "version": OEP_001_SIMULATION_ENGINE_VERSION,
            "proposal_id": proposal.proposal_id,
            "impacted_layers": impacted,
            "risk_flags": self._risk_flags(proposal.files or [], impacted),
            "required_tests": self._required_tests(impacted, proposal.tests),
            "simulation_only": True,
            "write_executed": False,
            "deploy_executed": False,
        }

    def _impacted_layers(self, files: List[str]) -> List[str]:
        layers = set()
        for file in files:
            f = file.lower()
            if "frontend" in f or f.endswith((".jsx", ".tsx", ".js", ".ts")):
                layers.add("frontend")
            if "backend" in f or f.endswith(".py"):
                layers.add("backend")
            if any(x in f for x in ["realtime", "stream", "sse", "voice", "webrtc", "session"]):
                layers.add("runtime")
            if "auth" in f:
                layers.add("auth")
        return sorted(layers or {"unknown"})

    def _risk_flags(self, files: List[str], impacted: List[str]) -> List[str]:
        flags = []
        if "frontend" in impacted and "backend" in impacted:
            flags.append("cross_layer_change")
        if "runtime" in impacted:
            flags.append("runtime_sensitive")
        if len(files) > 5:
            flags.append("large_surface_area")
        if not files:
            flags.append("no_files_declared")
        return flags

    def _required_tests(self, impacted: List[str], declared: List[str]) -> List[str]:
        tests = set(declared or [])
        if "frontend" in impacted:
            tests.add("vite build")
        if "backend" in impacted:
            tests.add("python -m py_compile")
        if "runtime" in impacted:
            tests.add("smoke realtime/manual switch")
        return sorted(tests)
