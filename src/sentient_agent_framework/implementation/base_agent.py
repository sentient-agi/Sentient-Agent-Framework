from sentient_agent_framework.implementation.default_server import DefaultServer
from sentient_agent_framework.implementation.base_server_agent import BaseServerAgent
from sentient_agent_framework.interface.identity import Identity


class BaseAgent(BaseServerAgent):
    """
    Agent that uses a DefaultServer to host an endpoint for delivering responses.
    
    NOT a concrete implementation, still needs to be subclassed and the 
    `assist` method needs to be implemented.
    """
    
    def __init__(self, identity: Identity):
        super().__init__(identity)
        self._server = DefaultServer(self)
        

    def run_server(self, debug=True):
        # Separate running the server from setting up the server because 
        # running the server is a blocking operation that should only happen 
        # when everything else is ready.
        self._server.run(debug=debug)