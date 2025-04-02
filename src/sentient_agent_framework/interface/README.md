# Interface
## Architecture
#### Agent Abstract Base Class
The `AbstractAgent` class is an abstract base class that defines the specification for an agent. It is not intended to be used directly, but rather to be subclassed by concrete agents that implement the `assist()` method. It, along with all of the interfaces that it depends on, are defined but not implemented in the `interface` module.

```mermaid
classDiagram
    class AbstractAgent {
        <<abstract>>
        +Identity identity
        +assist(Session, Query, ResponseHandler)
    }
    
    class ResponseHandler {
        <<interface>>
        +respond(event_name, response)
        +emit_json(event_name, data)
        +emit_text_block(event_name, content)
        +create_text_stream(event_name)
        +emit_error(error_message, error_code, details)
        +complete()
        +is_complete()
    }
    
    class StreamEventEmitter~T~ {
        <<interface>>
        +complete()
        +id()
        +is_complete()
        +emit_chunk(chunk)
    }
    
    class Session {
        <<interface>>
        +processor_id
        +activity_id
        +request_id
        +get_interactions()
    }
    
    class Hook {
        <<interface>>
        +emit(Event)
    }
    
    class Event {
        +content_type
        +event_name
    }
    
    AbstractAgent --> ResponseHandler : uses
    AbstractAgent --> Session : uses
    ResponseHandler --> StreamEventEmitter : creates
    ResponseHandler --> Event : emits via Hook
    StreamEventEmitter --> Event : emits via Hook
    Hook --> Event : emits
```

#### Request Interface
The `Request` interface defines the specification for HTTP requests to an agent (requests would be sent by Sentient Chat - agent developers are not responsible for building and sending these requests).

```mermaid
classDiagram    
    class Query {
        +ULID id
        +str prompt
    }
    
    class Request {
        +Query query
        +Optional[SessionObject] session
    }
    
    class SessionObject {
        +str processor_id
        +ULID activity_id
        +ULID request_id
        +List[Interaction] interactions
    }
    
    class Interaction {
        +M request
        +Sequence[ResponseMessage] responses
    }

    Request *-- Query : contains
    Request *-- SessionObject : contains (optional)
    SessionObject *-- Interaction : contains list
```

#### Session Interface
The `Session` interface defines the specification for a Sentient Chat session between a user and an agent. 

```mermaid
classDiagram    
    class SessionObject {
        +str processor_id
        +ULID activity_id
        +ULID request_id
        +List[Interaction] interactions
    }
    
    class Interaction {
        +M request
        +Sequence[ResponseMessage] responses
    }
    
    class RequestMessage {
        +AssistRequest event
    }
    
    class ResponseMessage {
        +ResponseEvent event
    }
    
    class AssistRequest {
        +ULID id
        +ULID chat_id
        +AssistRequestContent content
        +Optional[ULID] parent_request_id
        +Optional[ULID] root_request_id
    }
    
    class AssistRequestContent {
        +str capability
        +AssistRequestContentParts request_payload
    }
    
    class AssistRequestContentParts {
        +List[AssistRequestContentPart] parts
    }
    
    class AssistRequestContentPart {
        +str prompt
        +List[str] files_ids
    }

    SessionObject *-- Interaction : contains list
    Interaction *-- RequestMessage : contains
    Interaction *-- ResponseMessage : contains sequence
    RequestMessage *-- AssistRequest : contains
    AssistRequest *-- AssistRequestContent : contains
    AssistRequestContent *-- AssistRequestContentParts : contains
    AssistRequestContentParts *-- AssistRequestContentPart : contains list
```

## Key Components
#### AbstractAgent
- Abstract class that must be subclasses by concrete agents that implement the `assist()` method
- Uses `ResponseHandler` to emit responses
- Processes `Request` objects
- Key methods:
    - `assist()`: Process `Request` objects and emit responses

#### ResponseHandler
- Protocol (interface) for handling different types of responses
- Emits `Event` objects to the client using a `Hook`
- Key methods:
    - `respond()`: Sends complete responses
    - `emit_json()`: Sends JSON events
    - `emit_text_block()`: Sends text blocks
    - `create_text_stream()`: Creates text streams
    - `emit_error()`: Sends error events
    - `complete()`: Marks response as complete

#### Hook
- Interface for emitting events to external systems
- Key methods:
    - `emit()`: Emits an event

#### Events
```
Event (base class)
└── BaseEvent
    ├── AtomicEvent (single messages)
    │   ├── DocumentEvent
    │   ├── TextBlockEvent
    │   ├── ErrorEvent
    │   └── DoneEvent
    └── StreamEvent
        └── TextChunkEvent (streaming text)
```
- `DocumentEvent`: JSON content
- `TextBlockEvent`: Complete text blocks
- `TextChunkEvent`: Streaming text chunks
- `ErrorEvent`: Error messages
- `DoneEvent`: Completion markers

#### Session
- Provides context for agent interactions
- Key methods:
    - `processor_id`: (Getter) Identifies the processor
    - `activity_id`: (Getter) Identifies the activity (e.g., chat)
    - `request_id`: (Getter) Identifies specific request
    - `get_interactions()`: (Getter) Interaction history