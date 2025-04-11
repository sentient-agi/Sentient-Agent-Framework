from pydantic import (
    BaseModel,
    Field
)
from sentient_agent_framework.interface.session import SessionObject
from typing import Optional
from ulid import ULID


class Query(BaseModel):
    """Agent query."""

    id: ULID = Field(
        description="Query ID."
    )
    prompt: str = Field(
        description="Query prompt."
    )


class Request(BaseModel):
    """A Sentient Chat Agent API request."""

    query: Query = Field(
        description="Agent query."
    )
    session: Optional[SessionObject] = Field(
        default=None,
        description="Agent session."
    )