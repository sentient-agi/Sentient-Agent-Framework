from sentient_agent_framework.interface.request import SessionObject
from sentient_agent_framework.interface.session import Interaction
from typing import AsyncIterable
from ulid import ULID


class DefaultSession:
    """
    Default implementation of the Session interface.

    Simply returns the appropriate values from the session object.
    """

    def __init__(self, session_object: SessionObject):
        self._session_object = session_object


    @property
    def processor_id(self) -> str:
        return self._session_object.processor_id


    @property
    def activity_id(self) -> ULID:
        return self._session_object.activity_id


    @property
    def request_id(self) -> ULID:
        return self._session_object.request_id


    def get_interactions(self) -> AsyncIterable[Interaction]:
        return self._session_object.interactions
