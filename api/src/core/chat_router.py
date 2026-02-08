"""
Chat router for AI integration using Jayce.

This demonstrates how to consume the Jayce AI Engine as an external library
following the SOLID principle of Low Coupling.
"""

from ninja import Router, Schema
from pydantic import Field

from jayce import JayceConfig, create_assistant

router = Router(tags=["chat"])


# =============================================================================
# SCHEMAS
# =============================================================================


class ChatRequest(Schema):
    """Request schema for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=10000)
    thread_id: str | None = Field(default=None, description="Optional thread for context")


class ChatResponse(Schema):
    """Response schema for chat endpoint."""

    response: str
    thread_id: str


# =============================================================================
# SINGLETON ASSISTANT (Thread-safe lazy initialization)
# =============================================================================


class AssistantManager:
    """
    Manages a singleton Jayce assistant instance.
    
    This follows the Dependency Injection pattern - configuration
    is injected at runtime, not hardcoded.
    """

    _instance = None
    _config = None

    @classmethod
    def get_assistant(cls, config: JayceConfig | None = None):
        """Get or create the assistant singleton."""
        if cls._instance is None or (config and config != cls._config):
            cls._config = config or JayceConfig(
                # Use environment-based defaults
                system_prompt=(
                    "Você é Jayce, um assistente de produtividade inteligente. "
                    "Ajude o usuário com suas tarefas, calendário, finanças e projetos. "
                    "Responda sempre em português brasileiro e formate em markdown."
                ),
            )
            cls._instance = create_assistant(cls._config)
        return cls._instance


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/", response=ChatResponse)
def chat(request, payload: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI assistant.
    
    Args:
        payload: Chat request with message and optional thread_id
        
    Returns:
        AI response with the thread_id for context persistence
    """
    assistant = AssistantManager.get_assistant()
    
    # Set thread if provided
    if payload.thread_id:
        assistant.set_thread(payload.thread_id)
    
    # Get response from Jayce
    response = assistant.chat(payload.message)
    
    return ChatResponse(
        response=response,
        thread_id=assistant._thread_id,
    )


@router.post("/reset")
def reset_chat(request) -> dict:
    """Reset the conversation context."""
    assistant = AssistantManager.get_assistant()
    assistant.reset()
    return {"status": "ok", "new_thread_id": assistant._thread_id}
