"""
Tests for the MPU6050 IMU driver.

Mock strategy: replace the I2C bus with MockI2C, which simulates
MPU6050 register responses without requiring physical hardware.

MPU6050 key registers:
  0x75 WHO_AM_I      -> 0x68 (identity check on init)
  0x6B PWR_MGMT_1   -> write 0x00 to wake device
  0x1C ACCEL_CONFIG -> write to set accel range (default ±2g)
  0x1B GYRO_CONFIG  -> write to set gyro range (default ±250°/s)
  0x3B ACCEL_XOUT_H -> start of 14-byte burst read (accel + temp + gyro)
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch, call

# Make firmware packages importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from hal.sensor import Sensor  # noqa: E402


# ---------------------------------------------------------------------------
# Mock I2C bus
# ---------------------------------------------------------------------------

MPU6050_ADDR = 0x68

# Raw 16-bit big-endian values for a known sensor reading.
# accel: ax=1024, ay=-512, az=16384 (1g), gx=100, gy=-200, gz=50
# temp raw = 0 (maps to 36.53°C via formula: temp/340 + 36.53)
_ACCEL_AX_H = (1024 >> 8) & 0xFF
_ACCEL_AX_L = 1024 & 0xFF
_ACCEL_AY_H = ((-512) & 0xFFFF) >> 8
_ACCEL_AY_L = (-512) & 0xFF
_ACCEL_AZ_H = (16384 >> 8) & 0xFF
_ACCEL_AZ_L = 16384 & 0xFF
_TEMP_H = 0x00
_TEMP_L = 0x00
_GYRO_GX_H = (100 >> 8) & 0xFF
_GYRO_GX_L = 100 & 0xFF
_GYRO_GY_H = ((-200) & 0xFFFF) >> 8
_GYRO_GY_L = (-200) & 0xFF
_GYRO_GZ_H = (50 >> 8) & 0xFF
_GYRO_GZ_L = 50 & 0xFF

BURST_READ_BYTES = bytes([
    _ACCEL_AX_H, _ACCEL_AX_L,
    _ACCEL_AY_H, _ACCEL_AY_L,
    _ACCEL_AZ_H, _ACCEL_AZ_L,
    _TEMP_H,     _TEMP_L,
    _GYRO_GX_H,  _GYRO_GX_L,
    _GYRO_GY_H,  _GYRO_GY_L,
    _GYRO_GZ_H,  _GYRO_GZ_L,
])

ACCEL_SCALE_2G = 16384.0   # LSB/g for ±2g range
GYRO_SCALE_250 = 131.0     # LSB/°/s for ±250°/s range


def _make_mock_i2c(who_am_i: int = 0x68):
    """Return a MockI2C that simulates an MPU6050 on address 0x68."""
    mock_i2c = MagicMock()

    def readfrom_mem(addr, reg, nbytes):
        if reg == 0x75:  # WHO_AM_I
            return bytes([who_am_i])
        if reg == 0x3B:  # ACCEL_XOUT_H — burst read
            return BURST_READ_BYTES[:nbytes]
        return bytes(nbytes)  # default: all zeros

    mock_i2c.readfrom_mem.side_effect = readfrom_mem
    return mock_i2c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_driver(port: int = 1, i2c=None):
    """Import and instantiate the MPU6050 driver with an injected I2C bus."""
    from drivers.mpu6050 import MPU6050
    if i2c is None:
        i2c = _make_mock_i2c()
    return MPU6050(port=port, i2c=i2c)


# ---------------------------------------------------------------------------
# 1. Class contract — inherits from Sensor
# ---------------------------------------------------------------------------

class TestMPU6050Inheritance:
    def test_is_sensor_subclass(self):
        from drivers.mpu6050 import MPU6050
        assert issubclass(MPU6050, Sensor)

    def test_stores_port(self):
        driver = _make_driver(port=3)
        assert driver.port == 3

    def test_not_initialized_at_construction(self):
        driver = _make_driver()
        assert driver._initialized is False


# ---------------------------------------------------------------------------
# 2. init() — happy path
# ---------------------------------------------------------------------------

class TestMPU6050Init:
    def test_init_returns_true_on_success(self):
        driver = _make_driver()
        assert driver.init() is True

    def test_init_sets_initialized_flag(self):
        driver = _make_driver()
        driver.init()
        assert driver._initialized is True

    def test_init_wakes_device(self):
        """init() must write 0x00 to PWR_MGMT_1 (0x6B) to wake the MPU6050."""
        mock_i2c = _make_mock_i2c()
        driver = _make_driver(i2c=mock_i2c)
        driver.init()
        mock_i2c.writeto_mem.assert_any_call(MPU6050_ADDR, 0x6B, bytes([0x00]))

    def test_init_checks_who_am_i(self):
        """init() reads WHO_AM_I register to confirm device identity."""
        mock_i2c = _make_mock_i2c()
        driver = _make_driver(i2c=mock_i2c)
        driver.init()
        mock_i2c.readfrom_mem.assert_any_call(MPU6050_ADDR, 0x75, 1)

    def test_init_returns_false_on_wrong_who_am_i(self):
        """init() returns False if WHO_AM_I doesn't match 0x68."""
        mock_i2c = _make_mock_i2c(who_am_i=0xFF)
        driver = _make_driver(i2c=mock_i2c)
        assert driver.init() is False

    def test_init_leaves_uninitialized_on_wrong_who_am_i(self):
        mock_i2c = _make_mock_i2c(who_am_i=0xFF)
        driver = _make_driver(i2c=mock_i2c)
        driver.init()
        assert driver._initialized is False

    def test_init_returns_false_on_i2c_error(self):
        """init() returns False (does not raise) if I2C raises OSError."""
        mock_i2c = _make_mock_i2c()
        mock_i2c.readfrom_mem.side_effect = OSError("I2C error")
        driver = _make_driver(i2c=mock_i2c)
        assert driver.init() is False


# ---------------------------------------------------------------------------
# 3. read() — data correctness
# ---------------------------------------------------------------------------

class TestMPU6050Read:
    def setup_method(self):
        self.mock_i2c = _make_mock_i2c()
        self.driver = _make_driver(i2c=self.mock_i2c)
        self.driver.init()

    def test_read_returns_dict(self):
        result = self.driver.read()
        assert isinstance(result, dict)

    def test_read_has_required_keys(self):
        result = self.driver.read()
        required = {"ax", "ay", "az", "gx", "gy", "gz", "temp"}
        assert required.issubset(result.keys())

    def test_read_accel_x_correct(self):
        """ax raw=1024, scale=16384 → 1024/16384 ≈ 0.0625 g"""
        result = self.driver.read()
        assert abs(result["ax"] - (1024 / ACCEL_SCALE_2G)) < 1e-4

    def test_read_accel_y_correct(self):
        """ay raw=-512 → -512/16384 ≈ -0.03125 g"""
        result = self.driver.read()
        assert abs(result["ay"] - (-512 / ACCEL_SCALE_2G)) < 1e-4

    def test_read_accel_z_correct(self):
        """az raw=16384 → 1.0 g (pointing down at rest)"""
        result = self.driver.read()
        assert abs(result["az"] - (16384 / ACCEL_SCALE_2G)) < 1e-4

    def test_read_gyro_x_correct(self):
        """gx raw=100 → 100/131 ≈ 0.7634 °/s"""
        result = self.driver.read()
        assert abs(result["gx"] - (100 / GYRO_SCALE_250)) < 1e-4

    def test_read_gyro_y_correct(self):
        """gy raw=-200 → -200/131 ≈ -1.5267 °/s"""
        result = self.driver.read()
        assert abs(result["gy"] - (-200 / GYRO_SCALE_250)) < 1e-4

    def test_read_gyro_z_correct(self):
        """gz raw=50 → 50/131 ≈ 0.3817 °/s"""
        result = self.driver.read()
        assert abs(result["gz"] - (50 / GYRO_SCALE_250)) < 1e-4

    def test_read_temp_correct(self):
        """temp raw=0 → 0/340 + 36.53 = 36.53 °C"""
        result = self.driver.read()
        assert abs(result["temp"] - 36.53) < 1e-2

    def test_read_does_burst_read_from_0x3B(self):
        """read() must burst-read 14 bytes starting at register 0x3B."""
        self.driver.read()
        self.mock_i2c.readfrom_mem.assert_any_call(MPU6050_ADDR, 0x3B, 14)

    def test_read_raises_if_not_initialized(self):
        """read() raises RuntimeError if called before init()."""
        fresh_driver = _make_driver(i2c=_make_mock_i2c())
        with pytest.raises(RuntimeError):
            fresh_driver.read()


# ---------------------------------------------------------------------------
# 4. deinit()
# ---------------------------------------------------------------------------

class TestMPU6050Deinit:
    def test_deinit_clears_initialized_flag(self):
        driver = _make_driver()
        driver.init()
        assert driver._initialized is True
        driver.deinit()
        assert driver._initialized is False

    def test_deinit_puts_device_to_sleep(self):
        """deinit() writes sleep bit (0x40) to PWR_MGMT_1."""
        mock_i2c = _make_mock_i2c()
        driver = _make_driver(i2c=mock_i2c)
        driver.init()
        mock_i2c.writeto_mem.reset_mock()
        driver.deinit()
        mock_i2c.writeto_mem.assert_any_call(MPU6050_ADDR, 0x6B, bytes([0x40]))

    def test_deinit_safe_when_not_initialized(self):
        """deinit() must not raise if called on a fresh (uninit) driver."""
        driver = _make_driver()
        driver.deinit()  # should not raise
        assert driver._initialized is False
