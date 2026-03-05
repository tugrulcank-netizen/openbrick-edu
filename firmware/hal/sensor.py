# HAL Sensor base class
class Sensor:
    """Base class for all OpenBrick EDU sensors."""

    def __init__(self, port: int):
        self.port = port
        self._initialized = False

    def init(self) -> bool:
        """Initialize the sensor. Returns True on success."""
        raise NotImplementedError

    def read(self) -> dict:
        """Read sensor value. Returns dict of named values."""
        raise NotImplementedError

    def deinit(self) -> None:
        """Release sensor resources."""
        self._initialized = False
