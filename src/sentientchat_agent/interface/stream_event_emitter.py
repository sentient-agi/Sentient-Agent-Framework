from typing import (
    Generic,
    Protocol,
    TypeVar
)


T_contra = TypeVar('T_contra', contravariant=True)


class StreamEventEmitter(Protocol, Generic[T_contra]):
    async def complete(self) -> None:
        """Mark this stream as complete."""


    def id(self) -> str:
        """Get the stream ID."""


    def is_complete(self) -> bool:
        """Check if the stream is complete."""


    async def emit_chunk(self, chunk: T_contra):
        """ Send event chunk to this stream"""