## Architecture

> [!NOTE]  
> The class diagram below omits the `DefaultIdGenerator` class, which is used by the `DefaultHook` class to generate unique IDs for events.

```mermaid
classDiagram
    class AbstractAgent {
        -str name
        +assist(Session, Query, ResponseHandler)
    }

    class DefaultServer {
        -AbstractAgent _agent
        -Flask _app
        +run(debug)
        +assist_endpoint()
        -__stream_agent_output(request_json)
    }

    class DefaultSession {
        -SessionObject _session_object
        +processor_id
        +activity_id
        +request_id
        +get_interactions()
    }

    class DefaultHook {
        -Queue _queue
        -IdGenerator _id_generator
        -float _timeout_secs
        +emit(Event)
    }
    
    class DefaultResponseHandler {
        -Identity _source
        -Hook _hook
        -Cuid _cuid_generator
        -dict[str, StreamEventEmitter] _streams
        -bool _is_complete
        +respond(event_name, response)
        +emit_json(event_name, data)
        +emit_text_block(event_name, content)
        +create_text_stream(event_name)
        +emit_error(error_message, error_code, details)
        +complete()
        +is_complete()
        -__emit_event(event)
    }
    
    class DefaultTextStream {
        -Identity _event_source
        -str _event_name
        -str _stream_id
        -Hook _hook
        -bool _is_complete
        +emit_chunk(chunk)
        +complete()
        +id()
        +is_complete()
    }
    
    AbstractAgent --> DefaultServer : passed into
    DefaultServer --> DefaultSession : creates
    DefaultServer --> DefaultHook : creates
    DefaultServer --> DefaultResponseHandler : creates
    DefaultServer --> AbstractAgent : calls assist()
    DefaultResponseHandler --> DefaultHook : uses
    DefaultResponseHandler --> DefaultTextStream : creates
    DefaultTextStream --> DefaultHook : uses
```


## Operation Flow 
#### Request Handling
```mermaid
sequenceDiagram
    Client->>DefaultServer: HTTP Request
    DefaultServer->>AstractAgent: Creates DefaultSession, DefaultHook, DefaultResponseHandler, calls AbstractAgent.assist()
    AstractAgent->>DefaultHook: Generates response, emits events with hook
    DefaultHook->>DefaultServer: Adds id, metadata, etc. to emitted events and then adds to response queue
    DefaultServer->>Client: Pulls events from response queue, serves to client via SSE
```

#### Event Processing
```mermaid
sequenceDiagram
    AbstractAgent->>DefaultResponseHandler: Creates response event, calls one of DefaultResponseHandler's emit methods
    DefaultResponseHandler->>DefaultHook: Uses DefaultHook to emit event
    DefaultHook->>Queue: Adds event to queue
    Queue->>DefaultServer: Pulls event from queue
    DefaultServer->>Client: Serves event via SSE
```


## Key Components
#### AbstractAgent
- Abstract class for all agents (defined in the interface module)
- Core features:
    - `assist()`: Abstract method for agent execution

#### DefaultResponseHandler
- Implements `ResponseHandler` protocol
- Core features:
    - Event source tracking
    - Stream management
    - Event emission via hook
- Key methods:
    - `respond()`: Sends complete responses
    - `emit_json()`: Sends JSON events
    - `emit_text_block()`: Sends text blocks
    - `create_text_stream()`: Creates text streams
    - `emit_error()`: Sends error events
    - `complete()`: Marks response as complete

#### DefaultTextStream
- Implements `StreamEventEmitter` protocol
- Core features:
    - Stream source tracking
    - Completion state tracking
    - Chunk emission
- Key methods:
    - `emit_chunk()`: Sends text chunks
    - `complete()`: Marks stream as complete

#### DefaultHook
- Implements `Hook` protocol using a `Queue`
- Features:
    - Event ID generation
    - Timeout management
    - Queue management
- Key methods:
    - `emit()`: Adds event to queue

#### DefaultServer
- Flask-based SSE server
- Core features:
    - Exposes `assist` HTTP endpoint
    - Processes requests
    - Streams agent output
- Key methods:
    - `assist_endpoint()`: `assist` HTTP endpoint
    - `stream_agent_output()`: Calls agent's `assist()` method and yields the output as well-formed SSE events

#### DefaultSession
- Implements `Session` protocol

#### DefaultIdGenerator
- ULID-based identifier generator
- Core features:
    - Monotonic ID generation
    - Thread-safe operation
    - Timestamp-based offsets
- Key methods:
    - `get_next_id()`: Generates a new ULID