"""Runtime context — metadata carried across the graph execution."""

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True, slots=True)
class Context:
    """Context passed through the graph execution.

    Attributes
    ----------
    thinking : bool
        Whether the model should engage in deeper reasoning (e.g. use
        a thinking/reasoning model like deepseek-r1) or reply quickly
        with a standard model.
    """

    thinking: bool = False
