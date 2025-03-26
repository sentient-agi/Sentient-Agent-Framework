from enum import Enum
from typing import (
    Annotated,
    Any,
    Literal,
    Mapping,
    Optional,
    TypeAlias,
    Union
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter
)
from ulid import ULID


# Constants
ERROR = "error"
DEFAULT_ERROR_CODE = 500


class BaseEventType(str, Enum):
    """Base event types."""
    ATOMIC = "atomic"
    CHUNKED = "chunked"


class EventContentType(str, Enum):
    """Event content types."""
    # Atomic events
    JSON = "atomic.json"
    TEXTBLOCK = "atomic.textblock"

    # Chunked events
    TEXT_STREAM = "chunked.text"
    ERROR = "atomic.error"
    DONE = "atomic.done"

    @property
    def base_type(self) -> BaseEventType:
        """Get the base event type."""
        prefix = self.value.split('.')[0]
        return BaseEventType(prefix)


EventMetadata: TypeAlias = Mapping[str,
                                   Union[str, int, float, bool, list[str]]]


StringKeyDict = Mapping[str, Any]


class Event(BaseModel):
    """
    An event is used to send response chunk from the processor to the outside
    world.  These could be intermediatory result from during the life cycle of 
    processor with streaming capabilities.
    """
    content_type: EventContentType = Field(
        description="Type of the event."
    )
    event_name: str = Field(
        description="Name of the event as defined by event publisher."
    )


class BaseEvent(Event):
    """A bese event."""
    schema_version: str = Field(
        default="1.0",
        description="Schema version for handling future changes"
    )

    id: ULID = Field(
        default_factory=ULID,
        description="Uniquely identifies a base event."
    )
    source: str = Field(
        description="Identifier of the source that raised the event."
    )
    metadata: Optional[EventMetadata] = Field(
        default=None,
        description="Extra metadata related to the event. The content of "
        "the metadata cannot exceed 16 key-value pairs."
    )


class AtomicEvent(BaseEvent):
    """An atomic event."""


class StreamEvent(BaseEvent):
    """
    A base implementation for streaming events.
    """
    stream_id: str = Field(
        description="Stream identifier."
    )
    is_complete: bool = Field(
        description=" determines if stream is complete "
    )


class DocumentEvent(AtomicEvent):
    """A document event."""
    content_type: Literal[EventContentType.JSON] = EventContentType.JSON
    content: Mapping[Any, Any] = Field(
        description="the atomic json content event"
    )


class TextBlockEvent(AtomicEvent):
    """A text block event."""
    content_type: Literal[EventContentType.TEXTBLOCK] = EventContentType.TEXTBLOCK
    content: str = Field(
        description="Normal text content "
    )


class TextChunkEvent(StreamEvent):
    """
    An event used to transmit response token chunks to the outside world.
    """
    model_config = ConfigDict(populate_by_name=True)

    content_type: Literal[EventContentType.TEXT_STREAM] = EventContentType.TEXT_STREAM
    content: str = Field(
        description=" group of token that needs to rendered in the UI ",
        min_length=0
    )


class ErrorContent(BaseModel):
    """Error event content."""
    error_message: str = Field(
        description=" description about error messages. "
    )
    error_code: int = Field(
        default=DEFAULT_ERROR_CODE,
        description=" error code (HTTP status code wherever possible) "
    )
    details: Optional[Mapping[str, Any]] = Field(
        default=None,
        description=" optional details about error messages. "
    )


class ErrorEvent(AtomicEvent):
    """An error event."""
    content_type:  Literal[EventContentType.ERROR] = EventContentType.ERROR
    event_name: str = Field(
        default=ERROR,
        frozen=True
    )
    content: ErrorContent = Field(
        description=" details about the error content "
    )


class DoneEvent(AtomicEvent):
    """A done event."""
    content_type: Literal[EventContentType.DONE] = EventContentType.DONE
    event_name: str = "done"


ResponseEvent = Annotated[
    Union[DocumentEvent, TextBlockEvent,
          TextChunkEvent, ErrorEvent, DoneEvent],
    Field(discriminator="content_type")
]

ResponseEventAdapter = TypeAdapter[ResponseEvent](ResponseEvent)
ResponseEventListAdapter = TypeAdapter[list[ResponseEvent]](
    list[ResponseEvent])