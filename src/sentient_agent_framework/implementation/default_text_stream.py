from __future__ import annotations
from sentient_agent_framework.interface.events import TextChunkEvent
from sentient_agent_framework.interface.exceptions import TextStreamClosedError
from sentient_agent_framework.interface.hook import Hook
from sentient_agent_framework.interface.identity import Identity
from sentient_agent_framework.interface.stream_event_emitter import StreamEventEmitter


class DefaultTextStream(StreamEventEmitter[str]):
    def __init__(
        self,
        event_source: Identity,
        event_name: str,
        stream_id: str,
        hook: Hook
    ):
        self._event_source = event_source
        self._event_name = event_name
        self._stream_id = stream_id
        self._hook = hook
        self._is_complete = False


    async def emit_chunk(
        self, 
        chunk: str
    ) -> DefaultTextStream:
        """Send a chunk of text to this stream."""
        if self._is_complete:
            raise TextStreamClosedError(
                f"Cannot emit chunk to closed stream {self._stream_id}."
            )
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=False,
            content=chunk
        )
        await self._hook.emit(event)
        return self


    async def complete(self) -> None:
        """Mark this stream as complete."""
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=True,
            content=" "
        )
        await self._hook.emit(event)
        self._is_complete = True


    @property
    def id(self) -> str:
        """Get the stream ID."""
        return self._stream_id


    @property
    def is_complete(self) -> bool:
        """Check if the stream is complete."""
        return self._is_complete