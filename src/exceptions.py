from engrate_sdk.utils import log


logger = log.get_logger(__name__)

class ControlledException(Exception):
    """Base class for known, controlled exceptions."""
    pass


class MissingError(ControlledException):
    """Exception used for missing resources."""

    def __init__(self, kind: str, id: str):
        self.kind = kind
        self.id = id
        super().__init__(f"No {kind} with ID {id} found")


class NotEnabledError(ControlledException):
    """Exception used for features that are not enabled or allowed."""

    def __init__(self):
        super().__init__("Operation not enabled")


class IllegalArgumentError(ControlledException):
    """Illegal argument provided"""

    def __init__(self):
        super().__init__("Illegal argument provided")

class IllegalStateError(ControlledException):
    """state of the system is not valid for the operation"""

    def __init__(self,str):
        super().__init__(f"System is in an illegal state for the operation: {str}")

class UnexpectedValue(ControlledException):
    """Unexpected value provided. Mostly for serialization errors."""

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"Unexpected value provided: {details}")

class UncontrolledException(Exception):
    """Base class for unknown, uncontrolled exceptions.
    Generally meaning we can't recover and need to be alerted in all instances.
    May also occur outside of FastAPI context."""

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"{details}")


class UnknownError(UncontrolledException):
    """Nobody knows."""

    def __init__(self, details: str):
        super().__init__(details)


class InitError(UncontrolledException):
    """Exception used for initialization errors."""

    def __init__(self, details: str):
        super().__init__(f"Init failure: {details}")
