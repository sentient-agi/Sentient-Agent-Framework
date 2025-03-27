class ProcessorError(Exception):
    """Base class for exception due to error in processor."""


class AgentError(ProcessorError):
    """Base class for exception due to error in agents error."""


class ResponseStreamClosedError(ProcessorError):
    """Exception raised when the connection is closed."""


class TextStreamClosedError(ProcessorError):
    """Exception raised when text stream is closed."""