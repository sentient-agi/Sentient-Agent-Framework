from sentient_agent_framework.interface.events import Event
from typing import Protocol


class Hook(Protocol):
    """
    A hook is used to emit processor events to the outside world.
    """
    async def emit(self, event: Event) -> None:
        """
        Emit a processor event.
        """