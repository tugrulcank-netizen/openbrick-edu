"""
HAL Port Manager for OpenBrick EDU.

The PortManager owns all sensor and motor instances registered to physical
ports on the hub. It is responsible for:

  - Holding driver instances per port number (1–6)
  - Calling init() on all registered devices at boot
  - Calling deinit() on all registered devices at shutdown
  - Providing get_sensor(port) / get_motor(port) access to higher layers

The BootManager holds a reference to PortManager and calls init_all()
after BLE is up. The BLE service calls get_sensor() / get_motor() to
fulfil telemetry and command requests from the IDE.

Driver instances are created externally (in main.py or tests) and
injected via register_sensor() / register_motor() — consistent with
the I2C injection pattern (ADR-005).
"""


class PortManager:
    """Manages all sensor and motor driver instances by port number.

    Usage:
        pm = PortManager()
        pm.register_sensor(1, MPU6050(port=1, i2c=i2c_bus))
        pm.register_motor(2, MotorN20(port=2, pwm=pwm, ...))
        pm.init_all()                  # called once at boot
        sensor = pm.get_sensor(1)
        motor  = pm.get_motor(2)
        pm.deinit_all()               # called at shutdown
    """

    def __init__(self):
        self._sensors: dict = {}   # port -> Sensor instance
        self._motors:  dict = {}   # port -> Motor instance

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_sensor(self, port: int, sensor) -> None:
        """Register a sensor driver on the given port number."""
        self._sensors[port] = sensor

    def register_motor(self, port: int, motor) -> None:
        """Register a motor driver on the given port number."""
        self._motors[port] = motor

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get_sensor(self, port: int):
        """Return the sensor registered on port, or None if not registered."""
        return self._sensors.get(port)

    def get_motor(self, port: int):
        """Return the motor registered on port, or None if not registered."""
        return self._motors.get(port)

    def list_ports(self) -> dict:
        """Return dict of registered port numbers.

        Returns:
            {"sensors": [port, ...], "motors": [port, ...]}
        """
        return {
            "sensors": list(self._sensors.keys()),
            "motors":  list(self._motors.keys()),
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def init_all(self) -> bool:
        """Call init() on every registered sensor and motor.

        Returns True if all devices initialised successfully.
        Returns False if any device fails — continues initialising
        remaining devices so partial failures are visible.
        """
        all_ok = True
        for port, sensor in self._sensors.items():
            if not sensor.init():
                all_ok = False
        for port, motor in self._motors.items():
            if not motor.init():
                all_ok = False
        return all_ok

    def deinit_all(self) -> None:
        """Call deinit() on every registered sensor and motor."""
        for sensor in self._sensors.values():
            try:
                sensor.deinit()
            except Exception:
                pass
        for motor in self._motors.values():
            try:
                motor.deinit()
            except Exception:
                pass
