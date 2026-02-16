"""Domain layer — core entities, ports, and business rules.

This layer has ZERO external dependencies. It defines the agent's
core concepts (State, Context, Prompts) and the abstract ports
(LLMPort, CheckpointPort, ToolRegistryPort) that the infrastructure
layer must implement.
"""

from .context import Context
from .ports import CheckpointPort, LLMPort, ToolRegistryPort
from .prompts import DIRECT_REPLY_SYSTEM_PROMPT, HEALTHCHECK_PHRASES, SYSTEM_PROMPT
from .routing import RoutingPolicy
from .state import State

__all__ = [
    "CheckpointPort",
    "Context",
    "DIRECT_REPLY_SYSTEM_PROMPT",
    "HEALTHCHECK_PHRASES",
    "LLMPort",
    "RoutingPolicy",
    "SYSTEM_PROMPT",
    "State",
    "ToolRegistryPort",
]
