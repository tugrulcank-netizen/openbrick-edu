# Boot Manager
# Runs on power-on: init hardware, show splash, start BLE, signal ready


class BootManager:
    """Manages the ESP32-S3 boot sequence."""

    def __init__(self):
        self.ready = False
        self.matrix = None
        self.ble = None

    def run(self) -> bool:
        """Execute boot sequence. Returns True if ready."""
        self.matrix.init()
        self.matrix.splash()

        if not self.ble.init():
            return False

        self.ready = True
        return True
