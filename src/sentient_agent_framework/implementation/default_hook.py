from asyncio import wait_for
from queue import Queue
from sentient_agent_framework.implementation.id_generator import (
    IdGenerator
)
from sentient_agent_framework.interface.events import (
    BaseEvent,
    Event
)
from typing import cast


class DefaultHook:
    """
    An async event queue hook that collects events in a queue.
    """
    def __init__(
            self,
            queue: Queue[Event],
            id_generator: IdGenerator | None = None,
            timeout_ms: int | None = None
    ):
        # Validate.
        if queue is None:
            raise ValueError("Event queue not specified.")
        # Initialize state.
        self._queue = queue
        self._id_generator = id_generator or IdGenerator()
        self._timeout_secs = timeout_ms / 1000 if timeout_ms else None


    async def emit(self, event: Event) -> None:
        """
        Collect the event into a queue.
        Raises TimeoutError if the queue was full and put waited for the 
        specified timeout.  If a timeout is not specified, emit will wait 
        until there is a free slot in the queue.
        """
        # Make sure that the event id is greater than the previous one.
        # As of now we only have base events, so we can cast.
        event = cast(BaseEvent, event)
        event.id = await self._id_generator.get_next_id(event.id)
        # Add the event to the queue, block till there is a free slot if a
        # timeout is not specified.
        if self._timeout_secs is None:
            # Add to queue, wait if necessary.
            self._queue.put(event)
            return
        # Add element to queue with a timeout.
        await wait_for(
            self._queue.put(event),
            self._timeout_secs
        )