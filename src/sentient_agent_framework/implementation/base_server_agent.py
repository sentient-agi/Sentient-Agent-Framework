from queue import Queue
from sentient_agent_framework.implementation.default_hook import DefaultHook
from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.identity import Identity


class BaseServerAgent(AbstractAgent):
    """
    Agent that instantiates a response queue and hook.

    Defines the minimal set of requirements the server needs from any agent 
    implementation. Used to avoid a circular dependency between the BaseAgent 
    and DefaultServer classes (both classes depend on this class rather than 
    directly on each other).

    NOT a concrete implementation, still needs to be subclassed and the 
    `assist` method needs to be implemented.
    """

    def __init__(
            self,
            identity: Identity,
    ):
        super().__init__(identity)

        # Create Queue for Hook
        self.response_queue = Queue()

        # Create Hook for ResponseHandler
        self.hook = DefaultHook(self.response_queue)