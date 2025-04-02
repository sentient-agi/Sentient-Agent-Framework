import asyncio
import threading
from flask import (
    Flask,
    Response,
    request
)
from sentient_agent_framework.implementation.default_response_handler import DefaultResponseHandler
from sentient_agent_framework.implementation.default_session import DefaultSession
from sentient_agent_framework.implementation.base_server_agent import BaseServerAgent
from sentient_agent_framework.interface.events import DoneEvent
from sentient_agent_framework.interface.request import Request


class DefaultServer():
    """
    Flask server that streams agent output to the client via Server-Sent Events.
    """

    def __init__(
            self,
            agent: BaseServerAgent
        ):
        self._agent = agent

        # Create Flask app
        self._app = Flask(__name__)
        self._app.route('/assist')(self.assist_endpoint)


    def run(self, debug=True):
        """Start the Flask server"""

        # Separate running the server from setting up the server because 
        # running the server is a blocking operation that should only happen 
        # when everything else is ready.
        self._app.run(debug=debug)


    def __stream_agent_output(self, request_json):
        """Yield agent output as SSE events."""

        # Request
        request: Request = Request.model_validate(request_json)

        # Session
        session = DefaultSession(request.session) if request.session else None
        
        # ResponseHandler
        response_handler = DefaultResponseHandler(self._agent.identity, self._agent.hook)

        # Run the agent's assist function in it's own thread
        threading.Thread(target=lambda: asyncio.run(self._agent.assist(session, request.query, response_handler))).start()
        
        # Stream the response handler events
        while True:
            event = self._agent.response_queue.get()
            yield f"data: {event}\n\n"
            if type(event) == DoneEvent:
                break


    def assist_endpoint(self):
        """Endpoint that streams agent output to client as SSE events."""
        
        request_json = request.get_json()
        return Response(self.__stream_agent_output(request_json), content_type='text/event-stream')