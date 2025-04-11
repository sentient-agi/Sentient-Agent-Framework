from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)
from sentient_agent_framework.interface.events import (
    Event,
    ResponseEvent
)
from typing import (
    AsyncIterable,
    Generic,
    List,
    Literal,
    Protocol,
    Self,
    Sequence,
    TypeVar
)
from ulid import ULID


DEFAULTY_CAPABILITY = "default"
ASSIST_CAPABILITY = "assist"


I = TypeVar("I", bound=BaseModel, contravariant=True)
O = TypeVar("O", bound=BaseModel, covariant=True)
M = TypeVar("M", bound="InteractionMessage")


class CapabilitySpec(BaseModel):
    """Processor capability specification."""

    name: str = Field(
        description="Name of a processor-capability. Unique for a processor."
    )

    description: str = Field(
        description="Description of the capability."
    )

    stream_response: bool = Field(
        description="Type of the capability."
    )


class AtomicCapabilitySpec(CapabilitySpec, Generic[I, O]):
    """Atomic capability specification."""
    
    stream_response: Literal[False] = False

    input_schema: type[I] = Field(
        description="Schema of the input."
    )

    output_schema: type[O] = Field(
        description="Schema of the response content."
    )


class StreamCapabilitySpec(CapabilitySpec, Generic[I]):
    """Streaming capability specification."""

    stream_response: Literal[True] = True

    input_schema: type[I] = Field(
        description="Schema of the request content."
    )
    output_events_schema: List[Event] = Field(
        description="Schema for each event returned by the streaming capability.")


class CapabilityConfig(BaseModel):
    """Externally configurable attributes of a processor-capability."""

    name: str = Field(
        description="Uniquely identifies the capability of a processor."
    )

    id: str = Field(
        description="Uniquely identifies a processor capability globally."
    )
    
    description: str | None = Field(
        default=None,
        description="Overridden description of the processor capability."
    )


class CapabilityRequestContent(BaseModel, Generic[I]):
    """Capability request content."""

    capability: str = Field(
        description="Capability name."
    )

    request_payload: I = Field(
        description="Request content."
    )


class AssistRequestContentPart(BaseModel):
    """Assist request content part."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={"examples": [
            {"prompt": "Hello", "fileIds": ["id1", "id2"]}
        ]}
    )

    prompt: str = Field(
        description=" prompt from user "
    )

    files_ids: List[str] = Field(
        description=" List of file ids attached to the request part",
        alias="fileIds"
    )


class AssistRequestContentParts(BaseModel):
    """Collection of assist request content parts."""

    parts: List[AssistRequestContentPart]


class AssistRequestContent(CapabilityRequestContent[AssistRequestContentParts]):
    """Assist request content."""

    capability: str = ASSIST_CAPABILITY

    request_payload: AssistRequestContentParts = Field(
        description="Request content parts."
    )


class Request(BaseModel, Generic[I]):
    """Chat inference request."""

    model_config = ConfigDict(populate_by_name=True)

    id: ULID = Field(
        default_factory=ULID,
        description="Uniquely identifies a request."
    )
    chat_id: ULID = Field(
        description="Chat identifier.",
        alias="chatId"
    )
    content: CapabilityRequestContent[I] = Field(
        description="Request content."
    )
    parent_request_id: ULID | None = Field(
        default=None,
        description="Parent request identifier."
    )
    root_request_id: ULID | None = Field(
        default=None,
        description="The identifier of the first request in the chain."
    )


    @model_validator(mode="after")
    def stamp_and_validate_root_request_id(self) -> Self:
        """Stamp root request identifier if not provided."""

        # If parent request identifier is provided, then we need root request
        # identifier also to be provided.
        if self.parent_request_id is not None \
                and self.root_request_id is None:
            raise ValueError(
                "Root request identifier is required when parent request "
                "identifier is provided."
            )
        # If not provided use request identifier as root identifier.
        if self.root_request_id is None:
            self.root_request_id = self.id
        # Make sure that parent request identifier is less than the request
        # identifier.
        if self.parent_request_id is not None \
                and self.parent_request_id >= self.id:
            raise ValueError(
                "Parent request identifier should be less than the request "
                "identifier."
            )
        # Make sure that root request identifier is not greater than the parent
        # request identifier.
        if self.parent_request_id is not None \
                and self.root_request_id > self.parent_request_id:
            raise ValueError(
                "Root request identifier should be less than or equal to the "
                "parent request identifier."
            )
        return self


class AssistRequest(Request[AssistRequestContentParts]):
    """Assist request."""

    content: AssistRequestContent = Field(
        description="Request content."
    )


class InteractionMessage(BaseModel):
    """A persisted interaction message"""

    sender: str | None = Field(
        default=None,
        description="The sender of the message."
    )
    recipients: set[str] | None = Field(
        default=None,
        description="The recipients of the message."
    )


class RequestMessage(InteractionMessage):
    """A persisted request interaction message."""
    event: AssistRequest = Field(
        description="The assist request."
    )


class ResponseMessage(InteractionMessage):
    """A persisted response interaction message."""

    event: ResponseEvent = Field(
        description="The response event."
    )


class Interaction(BaseModel, Generic[M]):
    """Interaction between user and agent."""

    request: M = Field(
        description="User request."
    )
    responses: Sequence[ResponseMessage] = Field(
        description="Agent responses."
    )


class SessionObject(BaseModel):
    """Agent session."""

    processor_id: str = Field(
        description="Processor ID."
    )
    activity_id: ULID = Field(
        description="Activity ID."
    )
    request_id: ULID = Field(
        description="Request ID."
    )
    interactions: List[Interaction] = Field(
        description="Past interactions."
    )


class Session(Protocol):
    """Sessions represent a chat (set of interactions) between a user and an agent."""

    @property
    def processor_id(self) -> str:
        """Get the processor identifier for the session."""

    @property
    def activity_id(self) -> ULID:
        """Get the activity identifier for the session."""

    @property
    def request_id(self) -> ULID:
        """Get the request identifier for the session."""

    async def get_interactions(
            self, **kwargs
    ) -> AsyncIterable[Interaction]:
        """Get interactions from the session."""