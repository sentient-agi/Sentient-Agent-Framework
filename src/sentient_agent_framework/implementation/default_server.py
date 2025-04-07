import asyncio
import threading
from flask import (
    Flask,
    Response,
    request
)
from queue import Queue
from sentient_agent_framework.implementation.default_hook import DefaultHook
from sentient_agent_framework.implementation.default_response_handler import DefaultResponseHandler
from sentient_agent_framework.implementation.default_session import DefaultSession
from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.events import DoneEvent
from sentient_agent_framework.interface.identity import Identity
from sentient_agent_framework.interface.request import Request


class DefaultServer():
    """
    Flask server that streams agent output to the client via Server-Sent Events.
    """

    def __init__(
            self,
            agent: AbstractAgent
        ):
        self._agent = agent

        # Create Flask app
        self._app = Flask(__name__)
        self._app.route('/assist', methods=['POST'])(self.assist_endpoint)


    def run(self, debug=True):
        """Start the Flask server"""

        # Separate running the server from setting up the server because 
        # running the server is a blocking operation that should only happen 
        # when everything else is ready.
        self._app.run(debug=debug)


    def __stream_agent_output(self, request_json):
        """Yield agent output as SSE events."""

        # Validate request
        request: Request = Request.model_validate(request_json)

        # Get session from request
        session = DefaultSession(request.session)

        # Get identity from session
        identity = Identity(id=session.processor_id, name=self._agent.name)

        # Create response queue
        response_queue = Queue()

        # Create hook
        hook = DefaultHook(response_queue)

        # Create response handler
        response_handler = DefaultResponseHandler(identity, hook)

        # Run the agent's assist function in it's own thread
        threading.Thread(target=lambda: asyncio.run(self._agent.assist(session, request.query, response_handler))).start()
        
        # Stream the response handler events
        while True:
            event = response_queue.get()
            yield f"event: {event.event_name}\n"
            yield f"data: {event}\n\n"
            if type(event) == DoneEvent:
                break


    def assist_endpoint(self):
        """Endpoint that streams agent output to client as SSE events."""
        
        request_json = request.get_json()
        return Response(self.__stream_agent_output(request_json), content_type='text/event-stream')