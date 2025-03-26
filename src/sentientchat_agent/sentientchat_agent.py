import asyncio
from queue import Queue
from src.sentientchat_agent.implementation.default_hook import DefaultHook
from src.sentientchat_agent.implementation.default_response_handler import DefaultResponseHandler
from src.sentientchat_agent.interface.identity import Identity


__all__ = [
    "DefaultHook",
    "DefaultResponseHandler",
    "Identity"
]


if __name__ == "__main__":
    response_queue = Queue()
    response_handler = DefaultResponseHandler(Identity(id="SSE-Demo", name="SSE Demo"), DefaultHook(response_queue))
    asyncio.run(response_handler.emit_text_block("TEST", "Hello, world!"))
    print(response_queue.get())