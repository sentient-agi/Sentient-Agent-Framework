from abc import ABC, abstractmethod
from sentient_agent_framework.interface.request import Query
from sentient_agent_framework.interface.response_handler import ResponseHandler
from sentient_agent_framework.interface.session import Session


class AbstractAgent(ABC):
    """An agent that has an identity and an assist method."""

    def __init__(
            self,
            name: str,
    ):
        self.name = name
        

    @abstractmethod
    async def assist(
            self,
            session: Session,
            query: Query,
            response_handler: ResponseHandler
    ):
        """Process the request and generate a response."""