from typing import Any, Dict
from .models import KernelInput, KernelResult
from .response_builder import build_response

def build_orkio_kernel_response(
    message: str,
    user_context: Dict[str, Any] | None = None,
    thread_context: Dict[str, Any] | None = None,
    capability_registry: Dict[str, Any] | None = None,
    governance_policy: Dict[str, Any] | None = None,
) -> KernelResult:
    return build_response(KernelInput(
        message=message or "",
        user_context=user_context or {},
        thread_context=thread_context or {},
        capability_registry=capability_registry or {},
        governance_policy=governance_policy or {},
    ))
