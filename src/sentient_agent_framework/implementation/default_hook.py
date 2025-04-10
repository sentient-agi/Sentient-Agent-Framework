import asyncio
from sentient_agent_framework.implementation.default_id_generator import DefaultIdGenerator
from sentient_agent_framework.interface.events import (
    BaseEvent,
    Event
)
from typing import cast


class DefaultHook:
    """
    An async event queue hook that collects events in a queue.
    
    Default implementation of the Hook protocl.
    """

    def __init__(
            self,
            queue: asyncio.Queue[Event],
            id_generator: DefaultIdGenerator | None = None,
            timeout_ms: int | None = None
    ):
        self._queue = queue
        self._id_generator = id_generator or DefaultIdGenerator()
        self._timeout_secs = timeout_ms / 1000 if timeout_ms else None


    async def emit(self, event: Event) -> None:
        """Add event to queue."""
        
        # Make sure that the event id is greater than the previous one.
        event = cast(BaseEvent, event)
        event.id = await self._id_generator.get_next_id(event.id)

        # Add the event to the queue, block till there is a free slot if a
        # timeout is not specified.
        if self._timeout_secs is None:
            # Add to queue, wait if necessary.
            await self._queue.put(event)
            return
        
        # Add element to queue with a timeout.
        await asyncio.wait_for(
            self._queue.put(event),
            self._timeout_secs
        )