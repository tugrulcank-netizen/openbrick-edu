"""
MPU6050 6-axis IMU driver for OpenBrick EDU.

Communicates over I2C. The I2C bus object is injected at construction time
to allow unit testing without physical hardware.

Registers used:
  0x75  WHO_AM_I       Identity check (expected: 0x68)
  0x6B  PWR_MGMT_1     Power management (0x00 = awake, 0x40 = sleep)
  0x1B  GYRO_CONFIG    Gyro full-scale range (default 0x00 = ±250 °/s)
  0x1C  ACCEL_CONFIG   Accel full-scale range (default 0x00 = ±2g)
  0x3B  ACCEL_XOUT_H   Start of 14-byte burst: accel(6) + temp(2) + gyro(6)

Scale factors (default ranges):
  Accelerometer ±2g  : 16384 LSB/g
  Gyroscope ±250°/s  : 131.0 LSB/°/s
  Temperature        : raw / 340 + 36.53  (°C)
"""

from hal.sensor import Sensor

MPU6050_ADDR   = 0x68

# Register addresses
REG_WHO_AM_I   = 0x75
REG_PWR_MGMT_1 = 0x6B
REG_GYRO_CFG   = 0x1B
REG_ACCEL_CFG  = 0x1C
REG_ACCEL_OUT  = 0x3B   # burst-read start

# Expected WHO_AM_I response
WHO_AM_I_RESPONSE = 0x68

# Scale factors for default configuration
ACCEL_SCALE = 16384.0   # LSB/g  (±2g range)
GYRO_SCALE  = 131.0     # LSB/°/s (±250°/s range)
TEMP_DIVISOR = 340.0
TEMP_OFFSET  = 36.53


def _to_signed_16(high: int, low: int) -> int:
    """Combine two bytes into a signed 16-bit integer."""
    value = (high << 8) | low
    if value >= 0x8000:
        value -= 0x10000
    return value


class MPU6050(Sensor):
    """Driver for the InvenSense MPU6050 6-axis IMU.

    Usage:
        imu = MPU6050(port=1, i2c=machine.I2C(...))
        if imu.init():
            data = imu.read()
            # data = {"ax": float, "ay": float, "az": float,
            #         "gx": float, "gy": float, "gz": float,
            #         "temp": float}
        imu.deinit()
    """

    def __init__(self, port: int, i2c):
        super().__init__(port)
        self._i2c = i2c

    # ------------------------------------------------------------------
    # Sensor interface
    # ------------------------------------------------------------------

    def init(self) -> bool:
        """Initialise the MPU6050.

        1. Reads WHO_AM_I to confirm device is present.
        2. Writes 0x00 to PWR_MGMT_1 to wake the device.
        3. Sets default accel (±2g) and gyro (±250°/s) ranges.

        Returns True on success, False if the device is not found or if
        an I2C error occurs.
        """
        try:
            who = self._i2c.readfrom_mem(MPU6050_ADDR, REG_WHO_AM_I, 1)[0]
            if who != WHO_AM_I_RESPONSE:
                return False

            # Wake device (clear sleep bit)
            self._i2c.writeto_mem(MPU6050_ADDR, REG_PWR_MGMT_1, bytes([0x00]))
            # Default ranges: ±2g accel, ±250°/s gyro (both register = 0x00)
            self._i2c.writeto_mem(MPU6050_ADDR, REG_GYRO_CFG,   bytes([0x00]))
            self._i2c.writeto_mem(MPU6050_ADDR, REG_ACCEL_CFG,  bytes([0x00]))

            self._initialized = True
            return True

        except OSError:
            return False

    def read(self) -> dict:
        """Read accelerometer, gyroscope, and temperature from the MPU6050.

        Returns a dict with keys:
            ax, ay, az  — acceleration in g
            gx, gy, gz  — angular rate in °/s
            temp        — temperature in °C

        Raises RuntimeError if init() has not been called successfully.
        """
        if not self._initialized:
            raise RuntimeError("MPU6050 not initialised. Call init() first.")

        raw = self._i2c.readfrom_mem(MPU6050_ADDR, REG_ACCEL_OUT, 14)

        ax_raw = _to_signed_16(raw[0],  raw[1])
        ay_raw = _to_signed_16(raw[2],  raw[3])
        az_raw = _to_signed_16(raw[4],  raw[5])
        temp_raw = _to_signed_16(raw[6],  raw[7])
        gx_raw = _to_signed_16(raw[8],  raw[9])
        gy_raw = _to_signed_16(raw[10], raw[11])
        gz_raw = _to_signed_16(raw[12], raw[13])

        return {
            "ax":   ax_raw   / ACCEL_SCALE,
            "ay":   ay_raw   / ACCEL_SCALE,
            "az":   az_raw   / ACCEL_SCALE,
            "gx":   gx_raw   / GYRO_SCALE,
            "gy":   gy_raw   / GYRO_SCALE,
            "gz":   gz_raw   / GYRO_SCALE,
            "temp": temp_raw / TEMP_DIVISOR + TEMP_OFFSET,
        }

    def deinit(self) -> None:
        """Release the MPU6050 back to sleep and mark as uninitialised."""
        if self._initialized:
            try:
                self._i2c.writeto_mem(MPU6050_ADDR, REG_PWR_MGMT_1, bytes([0x40]))
            except OSError:
                pass
        super().deinit()
