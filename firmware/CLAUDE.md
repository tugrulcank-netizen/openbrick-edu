# OpenBrick EDU — Firmware Instructions

ESP32-S3 MicroPython + C firmware for the OpenBrick EDU hub.

## Platform Constraints

- **MCU:** ESP32-S3-WROOM-1 (dual-core Xtensa LX7, 240 MHz)
- **RAM:** ~520 KB SRAM — budget carefully; large buffers must be allocated once and reused
- **Flash:** 8 MB (partitioned: firmware + 20 user program slots + OTA staging post-MVP)
- **Runtime:** MicroPython with C extensions for performance-critical HAL paths
- **BLE:** Bluetooth 5.0 LE via ESP-IDF NimBLE stack

## Module Structure

```
firmware/
├── boot/          # Startup, hardware init, LED splash, battery check
├── ble/           # BLE GATT service definitions, connection mgmt, protocol handler
├── usb/           # USB serial REPL and protocol handler
├── hal/           # Hardware abstraction: Port, Sensor, Motor base classes
│   ├── port.py        # Port base class with auto-detect handshake
│   ├── sensor.py      # Sensor ABC: init(), read(), calibrate(), get_type()
│   └── motor.py       # Motor ABC: run(), stop(), run_to_position(), get_angle()
├── drivers/       # Individual sensor and motor driver implementations
│   ├── imu.py         # MPU6050 — onboard gyro/accelerometer
│   ├── color.py       # TCS34725 — I2C color sensor
│   ├── distance.py    # VL53L0X (ToF) or HC-SR04 (ultrasonic)
│   ├── force.py       # HX711 + load cell
│   └── motor_geekservo.py  # Geekservo LEGO-compatible motor + encoder
├── executor/      # Sandboxed MicroPython program runner with watchdog
├── matrix/        # 5×5 WS2812B LED matrix animation engine
├── audio/         # Piezo speaker: tones, melodies, sound effects
├── storage/       # Program slot manager (flash-backed, 20 slots)
└── ota/           # WiFi OTA update handler with rollback (post-MVP)
```

## HAL Interface Contracts

All sensor drivers MUST inherit from `hal/sensor.py`:

```python
class Sensor(ABC):
    @abstractmethod
    def init(self, port: Port) -> None: ...
    @abstractmethod
    def read(self) -> dict: ...          # Returns typed dict, never raw bytes
    @abstractmethod
    def calibrate(self) -> None: ...
    @abstractmethod
    def get_type(self) -> str: ...       # e.g., "color", "distance", "force"
```

All motor drivers MUST inherit from `hal/motor.py`:

```python
class Motor(ABC):
    @abstractmethod
    def run(self, speed: int) -> None: ...         # speed: -100 to 100
    @abstractmethod
    def stop(self, brake: bool = True) -> None: ...
    @abstractmethod
    def run_to_position(self, degrees: int, speed: int = 50) -> None: ...
    @abstractmethod
    def get_angle(self) -> int: ...                # cumulative degrees
    @abstractmethod
    def reset_angle(self) -> None: ...
```

**New drivers must follow the pattern in `drivers/color.py` exactly** — it is the reference implementation for style, error handling, docstrings, and test structure.

## BLE GATT Services

| Service               | UUID Prefix | Characteristics                                  |
|----------------------|-------------|--------------------------------------------------|
| Device Info          | 0x180A      | Firmware version, hardware revision, serial       |
| Program Upload       | Custom      | Write: chunked binary (256-byte frames, CRC-16)  |
| Program Control      | Custom      | Write: run/stop/list; Notify: status updates      |
| Sensor Telemetry     | Custom      | Notify: sensor readings at 50 Hz per port         |
| Motor Command        | Custom      | Write: speed, position, stop commands per port    |
| Hub Status           | Custom      | Notify: battery %, temperature, error codes       |

Full protocol specification: load skill `@.claude/skills/ble-protocol.md`

## Memory Management Rules

- **No dynamic allocation in hot loops.** Pre-allocate sensor read buffers at init.
- **Use `memoryview` and `struct.pack/unpack`** for BLE frame encoding — avoid string concatenation.
- **Limit import depth.** Each `import` costs RAM. Use lazy imports for non-boot modules.
- **Profile with `micropython.mem_info()`** after any change that adds buffers or data structures.
- **Target: < 80% RAM usage** at boot with all 6 ports active. Log to `docs/nfr-status.md` if exceeded.

## Flash Storage Layout

| Partition      | Size     | Purpose                          |
|---------------|----------|----------------------------------|
| firmware       | 2 MB     | MicroPython + C extensions       |
| programs       | 2 MB     | 20 user program slots (100KB ea) |
| config         | 256 KB   | Calibration data, settings       |
| ota_staging    | 2 MB     | OTA update staging (post-MVP)    |
| filesystem     | ~1.5 MB  | General file system (logs, etc.) |

## PID Motor Control

- Geekservo motors use magnetic encoders for position feedback.
- PID tuning defaults: Kp=1.0, Ki=0.05, Kd=0.1 — adjust per motor unit in `config/`.
- Target accuracy: ±2° repeatability (NFR requirement).
- PID loop runs at 100 Hz in a dedicated timer interrupt — never block this with I2C reads.
- Full control details: load skill `@.claude/skills/motor-control.md`

## I2C Bus Configuration

- **Bus 0 (internal):** MPU6050 IMU only (address 0x68)
- **Bus 1 (external ports):** Shared by all sensor ports; use mutex for concurrent access
- **Clock speed:** 400 kHz (Fast Mode) — some sensors may need 100 kHz fallback
- **Pull-ups:** 4.7 kΩ on SDA/SCL for each bus

## Testing

- **Framework:** pytest with `micropython-stubs` for type checking
- **Mocking:** Mock I2C/GPIO at the HAL level — never mock the driver internals
- **Coverage target:** ≥ 80% line coverage; 100% for HAL interfaces
- **Hardware-in-the-loop:** Run on real ESP32-S3 dev board weekly; log results in `docs/validation-log.md`
- **Commands:**
  ```bash
  pytest tests/                          # All unit tests
  pytest tests/drivers/test_color.py     # Single driver
  ruff check firmware/                   # Lint
  mypy firmware/                         # Type check
  pytest --cov=firmware tests/           # Coverage report
  ```

## Build & Flash

```bash
# Build firmware image
mpremote connect /dev/ttyUSB0 fs cp -r firmware/ :
# Or using esptool for full image
esptool.py --chip esp32s3 write_flash 0x0 build/firmware.bin
```

## Critical Rules

- NEVER hardcode I2C addresses — use constants from `hal/addresses.py`
- NEVER block the main loop for > 10 ms — use async/await or timer callbacks
- ALWAYS handle I2C `OSError` with retry (max 3 attempts, 10 ms delay)
- ALWAYS validate sensor readings before returning (range check, NaN check)
- ALWAYS use the watchdog timer in the executor — user programs must not hang the hub
- When adding a new driver, load `@.claude/skills/sensor-driver-pattern.md` for the full template
