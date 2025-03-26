from pydantic import (
    BaseModel,
    Field
)


class Identity(BaseModel):
    """
    Uniquely identifies an entity.
    Id is internal to the system whereas name is external to the system.
    """
    id: str = Field(
        description="Uniquely identifies an entity."
    )
    name: str = Field(
        description="Name of the entity, preferable unique."
    )


    def __str__(self):
        return f"{self.id}:{self.name}"