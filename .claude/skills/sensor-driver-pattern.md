# Skill: Sensor Driver Pattern

Load this skill when implementing or modifying sensor drivers for the OpenBrick EDU hub firmware.

---

## HAL Sensor Base Class Contract

All sensor drivers inherit from `firmware/hal/sensor.py`:

```python
from abc import ABC, abstractmethod
from machine import I2C, Pin
from hal.port import Port


class Sensor(ABC):
    """Base class for all OpenBrick EDU sensor drivers.

    Every driver MUST implement all abstract methods.
    Every driver MUST validate readings before returning.
    Every driver MUST handle I2C errors with retry logic.
    """

    def __init__(self, port: Port) -> None:
        self._port = port
        self._i2c: I2C | None = None
        self._calibration: dict = {}
        self._initialized: bool = False

    @abstractmethod
    def init(self) -> None:
        """Initialize the sensor hardware.

        Must configure I2C, set sensor registers, and verify
        communication. Raise SensorInitError on failure.
        """
        ...

    @abstractmethod
    def read(self) -> dict:
        """Read current sensor values.

        Returns a dict with typed values. Keys are sensor-specific.
        Must validate readings (range check, NaN check) before returning.
        Raise SensorReadError on failure after retries.
        """
        ...

    @abstractmethod
    def calibrate(self) -> None:
        """Run sensor-specific calibration routine.

        Store calibration values in self._calibration.
        Persist to flash via storage module if needed.
        """
        ...

    @abstractmethod
    def get_type(self) -> str:
        """Return sensor type identifier string.

        Must be one of: 'color', 'distance', 'force', 'imu'
        Used for auto-detection and telemetry type codes.
        """
        ...

    def is_initialized(self) -> bool:
        """Check if sensor has been successfully initialized."""
        return self._initialized

    def get_calibration(self) -> dict:
        """Return current calibration data."""
        return self._calibration.copy()
```

---

## I2C Communication Patterns

### Initialization

```python
from machine import I2C, Pin
from hal.port import Port
from hal.errors import SensorInitError

def _init_i2c(self) -> None:
    """Initialize I2C bus for this sensor's port."""
    self._i2c = I2C(
        self._port.i2c_bus,          # Bus 1 for external ports
        scl=Pin(self._port.scl_pin),
        sda=Pin(self._port.sda_pin),
        freq=400_000,                # 400 kHz Fast Mode
    )

    # Verify sensor is present
    devices = self._i2c.scan()
    if self.I2C_ADDRESS not in devices:
        raise SensorInitError(
            f"{self.get_type()} sensor not found on port {self._port.number} "
            f"(expected address 0x{self.I2C_ADDRESS:02X}, found {devices})"
        )
```

### Register Read with Retry

```python
from hal.errors import SensorReadError
import time

# Constants — define at class level
_MAX_RETRIES: int = 3
_RETRY_DELAY_MS: int = 10

def _read_register(self, reg: int, num_bytes: int) -> bytes:
    """Read bytes from an I2C register with retry logic.

    Args:
        reg: Register address
        num_bytes: Number of bytes to read

    Returns:
        Raw bytes read from register

    Raises:
        SensorReadError: After all retries exhausted
    """
    for attempt in range(self._MAX_RETRIES):
        try:
            return self._i2c.readfrom_mem(self.I2C_ADDRESS, reg, num_bytes)
        except OSError as e:
            if attempt < self._MAX_RETRIES - 1:
                time.sleep_ms(self._RETRY_DELAY_MS)
            else:
                raise SensorReadError(
                    f"I2C read failed on {self.get_type()} port {self._port.number} "
                    f"reg 0x{reg:02X} after {self._MAX_RETRIES} attempts: {e}"
                ) from e

def _write_register(self, reg: int, data: bytes) -> None:
    """Write bytes to an I2C register with retry logic."""
    for attempt in range(self._MAX_RETRIES):
        try:
            self._i2c.writeto_mem(self.I2C_ADDRESS, reg, data)
            return
        except OSError as e:
            if attempt < self._MAX_RETRIES - 1:
                time.sleep_ms(self._RETRY_DELAY_MS)
            else:
                raise SensorReadError(
                    f"I2C write failed on {self.get_type()} port {self._port.number} "
                    f"reg 0x{reg:02X} after {self._MAX_RETRIES} attempts: {e}"
                ) from e
```

### Reading Validation

```python
import math

def _validate_reading(self, name: str, value: float, min_val: float, max_val: float) -> float:
    """Validate a sensor reading is within expected range.

    Args:
        name: Human-readable name for error messages
        value: The reading to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value

    Returns:
        The validated value (clamped to range)

    Raises:
        SensorReadError: If value is NaN or inf
    """
    if math.isnan(value) or math.isinf(value):
        raise SensorReadError(
            f"Invalid {name} reading from {self.get_type()} on port "
            f"{self._port.number}: {value}"
        )
    return max(min_val, min(max_val, value))
```

---

## GPIO Initialization (for non-I2C sensors)

Some sensors (e.g., HC-SR04 ultrasonic) use GPIO trigger/echo instead of I2C:

```python
from machine import Pin, time_pulse_us
import time

class DistanceSensorHCSR04(Sensor):
    """HC-SR04 ultrasonic distance sensor (GPIO-based)."""

    TRIGGER_PULSE_US: int = 10
    TIMEOUT_US: int = 30_000       # ~5 meter max range
    SPEED_OF_SOUND_CM_US: float = 0.0343  # cm per microsecond

    def init(self) -> None:
        self._trigger = Pin(self._port.gpio_out_pin, Pin.OUT, value=0)
        self._echo = Pin(self._port.gpio_in_pin, Pin.IN)
        self._initialized = True

    def read(self) -> dict:
        # Send 10µs trigger pulse
        self._trigger.value(0)
        time.sleep_us(2)
        self._trigger.value(1)
        time.sleep_us(self.TRIGGER_PULSE_US)
        self._trigger.value(0)

        # Measure echo duration
        try:
            duration_us = time_pulse_us(self._echo, 1, self.TIMEOUT_US)
        except OSError:
            raise SensorReadError("HC-SR04 echo timeout")

        if duration_us < 0:
            raise SensorReadError("HC-SR04 echo timeout (negative)")

        # Convert to distance
        distance_mm = (duration_us * self.SPEED_OF_SOUND_CM_US / 2) * 10
        distance_mm = self._validate_reading("distance", distance_mm, 20.0, 4000.0)

        return {"distance_mm": int(distance_mm)}
```

---

## Calibration Routine Template

```python
def calibrate(self) -> None:
    """Calibrate the sensor by taking baseline readings.

    Call with sensor in known state (e.g., no object for distance,
    white surface for color). Stores offsets in self._calibration.
    """
    if not self._initialized:
        raise SensorInitError("Cannot calibrate: sensor not initialized")

    # Take multiple readings and average
    readings = []
    for _ in range(20):
        reading = self.read()
        readings.append(reading)
        time.sleep_ms(50)

    # Compute calibration offsets (sensor-specific logic here)
    self._calibration = {
        "offset": sum(r["value"] for r in readings) / len(readings),
        "timestamp": time.time(),
    }

    # Optionally persist to flash
    # storage.save_calibration(self._port.number, self._calibration)
```

---

## Driver Registration

After implementing a driver, register it in `firmware/hal/port_detect.py`:

```python
from drivers.color import ColorSensorTCS34725
from drivers.distance import DistanceSensorVL53L0X
from drivers.force import ForceSensorHX711

# Sensor type detection registry
# Maps I2C address → driver class
SENSOR_REGISTRY: dict[int, type[Sensor]] = {
    0x29: DistanceSensorVL53L0X,    # VL53L0X default address
    0x29: ColorSensorTCS34725,       # Note: conflicts! See ADR for resolution
    0x48: ForceSensorHX711,          # HX711 via I2C adapter
}

# For GPIO-based sensors, detection uses a handshake protocol:
# 1. Send a known pulse pattern on GPIO out
# 2. Check for expected response on GPIO in
# 3. Match response to sensor type
GPIO_SENSOR_REGISTRY: dict[str, type[Sensor]] = {
    "hcsr04": DistanceSensorHCSR04,
}

def detect_sensor(port: Port) -> Sensor | None:
    """Auto-detect which sensor is connected to a port.

    Tries I2C scan first, then GPIO handshake.
    Returns instantiated (but not initialized) driver, or None.
    """
    # I2C detection
    try:
        i2c = I2C(port.i2c_bus, scl=Pin(port.scl_pin), sda=Pin(port.sda_pin), freq=100_000)
        devices = i2c.scan()
        for addr in devices:
            if addr in SENSOR_REGISTRY:
                return SENSOR_REGISTRY[addr](port)
    except OSError:
        pass

    # GPIO detection (for HC-SR04 etc.)
    # ... handshake logic ...

    return None
```

---

## Unit Test Mock Strategy

Mock at the HAL level (I2C bus), not inside the driver. This tests the driver's actual logic.

### Test Template

File: `tests/drivers/test_{sensor_name}.py`

```python
import pytest
from unittest.mock import MagicMock, patch
from drivers.color import ColorSensorTCS34725
from hal.port import Port
from hal.errors import SensorInitError, SensorReadError


@pytest.fixture
def mock_port() -> Port:
    """Create a mock port with standard pin assignments."""
    port = MagicMock(spec=Port)
    port.number = 1
    port.i2c_bus = 1
    port.scl_pin = 9
    port.sda_pin = 8
    return port


@pytest.fixture
def mock_i2c():
    """Create a mock I2C bus."""
    with patch("drivers.color.I2C") as mock_cls:
        i2c = MagicMock()
        mock_cls.return_value = i2c
        yield i2c


class TestColorSensorInit:
    def test_init_success(self, mock_port, mock_i2c):
        """Should initialize when sensor responds at expected address."""
        mock_i2c.scan.return_value = [0x29]  # TCS34725 address
        mock_i2c.readfrom_mem.return_value = b"\x44"  # Device ID

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()

        assert sensor.is_initialized()

    def test_init_sensor_not_found(self, mock_port, mock_i2c):
        """Should raise SensorInitError when sensor not on bus."""
        mock_i2c.scan.return_value = []  # No devices

        sensor = ColorSensorTCS34725(mock_port)
        with pytest.raises(SensorInitError, match="not found"):
            sensor.init()

    def test_init_wrong_device_id(self, mock_port, mock_i2c):
        """Should raise SensorInitError for unexpected device ID."""
        mock_i2c.scan.return_value = [0x29]
        mock_i2c.readfrom_mem.return_value = b"\xFF"  # Wrong ID

        sensor = ColorSensorTCS34725(mock_port)
        with pytest.raises(SensorInitError, match="unexpected device"):
            sensor.init()


class TestColorSensorRead:
    def test_read_returns_rgb_dict(self, mock_port, mock_i2c):
        """Should return dict with r, g, b, c keys."""
        mock_i2c.scan.return_value = [0x29]
        mock_i2c.readfrom_mem.side_effect = [
            b"\x44",                            # Device ID (init)
            b"\x01",                            # Status: valid
            b"\x64\x00\x32\x00\x19\x00\xC8\x00",  # c=100, r=50, g=25, b=200
        ]

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()
        result = sensor.read()

        assert "r" in result
        assert "g" in result
        assert "b" in result
        assert "c" in result
        assert isinstance(result["r"], int)

    def test_read_retries_on_i2c_error(self, mock_port, mock_i2c):
        """Should retry up to 3 times on I2C OSError."""
        mock_i2c.scan.return_value = [0x29]
        mock_i2c.readfrom_mem.side_effect = [
            b"\x44",                      # Device ID (init)
            OSError("I2C bus error"),      # First read fails
            b"\x01",                       # Status retry succeeds
            b"\x64\x00\x32\x00\x19\x00\xC8\x00",  # Data
        ]

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()
        result = sensor.read()  # Should succeed after retry

        assert "r" in result

    def test_read_raises_after_max_retries(self, mock_port, mock_i2c):
        """Should raise SensorReadError after 3 failed retries."""
        mock_i2c.scan.return_value = [0x29]
        mock_i2c.readfrom_mem.side_effect = [
            b"\x44",                      # Device ID (init)
            OSError("error"),             # Retry 1
            OSError("error"),             # Retry 2
            OSError("error"),             # Retry 3 — gives up
        ]

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()
        with pytest.raises(SensorReadError, match="after 3 attempts"):
            sensor.read()

    def test_read_validates_range(self, mock_port, mock_i2c):
        """Should clamp out-of-range values."""
        mock_i2c.scan.return_value = [0x29]
        mock_i2c.readfrom_mem.side_effect = [
            b"\x44",                           # Device ID
            b"\x01",                           # Status
            b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF",  # Max values
        ]

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()
        result = sensor.read()

        assert 0 <= result["r"] <= 65535
        assert 0 <= result["g"] <= 65535
        assert 0 <= result["b"] <= 65535


class TestColorSensorCalibrate:
    def test_calibrate_requires_init(self, mock_port, mock_i2c):
        """Should raise if calibrate called before init."""
        sensor = ColorSensorTCS34725(mock_port)
        with pytest.raises(SensorInitError, match="not initialized"):
            sensor.calibrate()

    def test_calibrate_stores_offsets(self, mock_port, mock_i2c):
        """Should store calibration data after successful calibration."""
        mock_i2c.scan.return_value = [0x29]
        # Setup: init + 20 calibration reads
        mock_i2c.readfrom_mem.side_effect = [
            b"\x44",  # Device ID
        ] + [
            b"\x01" + b"\x64\x00\x32\x00\x19\x00\xC8\x00"
            for _ in range(20)  # 20 calibration samples
        ]

        sensor = ColorSensorTCS34725(mock_port)
        sensor.init()
        sensor.calibrate()

        cal = sensor.get_calibration()
        assert "offset" in cal
        assert "timestamp" in cal


class TestColorSensorGetType:
    def test_returns_color(self, mock_port):
        """Should return 'color' as the type identifier."""
        sensor = ColorSensorTCS34725(mock_port)
        assert sensor.get_type() == "color"
```

---

## Worked Example: TCS34725 Color Sensor Driver

See `firmware/drivers/color.py` for the complete reference implementation. Key characteristics:

- I2C address: `0x29`
- Device ID register: `0x12` (expected value: `0x44` or `0x4D`)
- Integration time: 154ms (adjustable via register `0x01`)
- RGBC data registers: `0x14–0x1B` (8 bytes, little-endian uint16 pairs)
- Gain settings: 1×, 4×, 16×, 60× (register `0x0F`)

This driver is the **style reference** for all other sensor drivers. Match its:
- Docstring format
- Error handling pattern
- Register constant naming (`_REG_ENABLE`, `_REG_ATIME`, etc.)
- Read/validate flow
- Test structure
