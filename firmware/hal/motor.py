# HAL Motor base class
class Motor:
    """Base class for all OpenBrick EDU motors."""

    def __init__(self, port: int):
        self.port = port
        self._initialized = False

    def init(self) -> bool:
        """Initialize the motor. Returns True on success."""
        raise NotImplementedError

    def run(self, speed: int) -> None:
        """Run motor at speed (-100 to 100)."""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop the motor."""
        raise NotImplementedError

    def angle(self) -> float:
        """Return current angle in degrees."""
        raise NotImplementedError

    def deinit(self) -> None:
        """Release motor resources."""
        self._initialized = False
