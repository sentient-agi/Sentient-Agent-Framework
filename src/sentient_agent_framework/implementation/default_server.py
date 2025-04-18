import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sentient_agent_framework.implementation.default_hook import DefaultHook
from sentient_agent_framework.implementation.default_response_handler import DefaultResponseHandler
from sentient_agent_framework.implementation.default_session import DefaultSession
from sentient_agent_framework.interface.agent import AbstractAgent
from sentient_agent_framework.interface.events import DoneEvent
from sentient_agent_framework.interface.identity import Identity
from sentient_agent_framework.interface.request import Request


class DefaultServer():
    """
    FastAPI server that streams agent output to the client via Server-Sent Events.
    """

    def __init__(
            self,
            agent: AbstractAgent
        ):
        self._agent = agent

        # Create FastAPI app
        self._app = FastAPI()
        self._app.post('/assist')(self.assist_endpoint)


    def run(
            self, 
            host: str = "0.0.0.0",
            port: int = 8000
        ):
        """Start the FastAPI server"""

        # Separate running the server from setting up the server because 
        # running the server is a blocking operation that should only happen 
        # when everything else is ready.
        uvicorn.run(
            self._app,
            host=host, 
            port=port
        )


    async def __stream_agent_output(self, request):
        """Yield agent output as SSE events."""

        # Get session from request
        session = DefaultSession(request.session)

        # Get identity using processor id from session
        identity = Identity(id=session.processor_id, name=self._agent.name)

        # Create response queue
        response_queue = asyncio.Queue()

        # Create hook
        hook = DefaultHook(response_queue)

        # Create response handler
        response_handler = DefaultResponseHandler(identity, hook)

        # Run the agent's assist function
        asyncio.create_task(self._agent.assist(session, request.query, response_handler))
        
        # Stream the response handler events
        while True:
            event = await response_queue.get()
            yield f"event: {event.event_name}\n"
            yield f"data: {event.model_dump_json()}\n\n"
            response_queue.task_done()
            if type(event) == DoneEvent:
                break


    async def assist_endpoint(self, request: Request):
        """Endpoint that streams agent output to client as SSE events."""
        
        return StreamingResponse(self.__stream_agent_output(request), media_type="text/event-stream")