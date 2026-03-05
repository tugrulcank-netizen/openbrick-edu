"""
Integration test: Boot sequence wiring boot → BLE → HAL → drivers.

Day 5 goal: verify that BootManager correctly orchestrates all subsystems
and that the layers can be composed together without errors.

This is NOT a unit test of individual components (those exist in Days 1-4).
This tests the *wiring* — that components talk to each other correctly
through the BootManager as the central orchestrator.

Architecture under test:
    BootManager
        ├── matrix (LED matrix — mocked, hardware not available)
        ├── ble    (BLEService — real service.py + protocol.py)
        ├── hal    (PortManager — new Day 5 component)
        │     ├── port 1: MPU6050 sensor (mocked I2C)
        │     └── port 2: MotorN20 (mocked PWM/pins)
        └── ready flag

New component introduced today:
    firmware/hal/port_manager.py — owns all ports, creates and holds
    driver instances, exposes get_sensor(port) / get_motor(port).
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from boot.manager import BootManager          # noqa: E402
from ble.service import (                     # noqa: E402
    HUB_SERVICE_UUID, MSG_CMD_RUN, MSG_CMD_STOP,
)
from ble.protocol import (                    # noqa: E402
    encode_frame, decode_frame,
    build_cmd_run, build_cmd_stop, build_hub_status,
)
from drivers.mpu6050 import MPU6050          # noqa: E402
from drivers.motor_n20 import MotorN20       # noqa: E402
from drivers.pid import PID                  # noqa: E402


# ---------------------------------------------------------------------------
# Shared mock factories
# ---------------------------------------------------------------------------

def _make_mock_matrix():
    m = MagicMock()
    m.init = MagicMock(return_value=True)
    m.splash = MagicMock()
    return m


def _make_mock_ble_service():
    b = MagicMock()
    b.init = MagicMock(return_value=True)
    return b


def _make_mock_i2c(who_am_i=0x68):
    mock = MagicMock()
    def readfrom_mem(addr, reg, nbytes):
        if reg == 0x75:
            return bytes([who_am_i])
        # 14-byte zeroed burst read (ax=ay=gz=0, az=0, temp raw=0)
        return bytes(nbytes)
    mock.readfrom_mem.side_effect = readfrom_mem
    return mock


def _make_mock_motor_hw():
    pwm     = MagicMock()
    dir_pin = MagicMock()
    enc_a   = MagicMock()
    enc_b   = MagicMock()
    return pwm, dir_pin, enc_a, enc_b


# ---------------------------------------------------------------------------
# 1. BootManager + BLE integration
# ---------------------------------------------------------------------------

class TestBootBLEIntegration:
    def test_boot_succeeds_with_real_ble_service_mock(self):
        """BootManager.run() → True when BLE init succeeds."""
        bm = BootManager()
        bm.matrix = _make_mock_matrix()
        bm.ble = _make_mock_ble_service()
        assert bm.run() is True
        assert bm.ready is True

    def test_boot_fails_when_ble_fails(self):
        bm = BootManager()
        bm.matrix = _make_mock_matrix()
        bm.ble = _make_mock_ble_service()
        bm.ble.init.return_value = False
        assert bm.run() is False
        assert bm.ready is False

    def test_boot_sequence_order(self):
        """matrix.init → matrix.splash → ble.init (in that order)."""
        call_order = []
        bm = BootManager()
        bm.matrix = _make_mock_matrix()
        bm.ble = _make_mock_ble_service()
        bm.matrix.init.side_effect   = lambda: call_order.append("matrix.init")
        bm.matrix.splash.side_effect = lambda: call_order.append("matrix.splash")
        bm.ble.init.side_effect      = lambda: call_order.append("ble.init") or True
        bm.run()
        assert call_order == ["matrix.init", "matrix.splash", "ble.init"]

    def test_ble_protocol_encode_decode_survives_boot(self):
        """After boot, the BLE protocol layer correctly encodes CMD_RUN."""
        frame = build_cmd_run(slot=0)
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_CMD_RUN
        assert payload == bytes([0])

    def test_hub_status_frame_after_boot(self):
        """Hub can build a valid status frame post-boot."""
        frame = build_hub_status(battery_pct=100, state=1, error_code=0)
        msg_type, payload = decode_frame(frame)
        assert msg_type == 0x11
        assert payload[0] == 100   # battery


# ---------------------------------------------------------------------------
# 2. PortManager — new Day 5 component
# ---------------------------------------------------------------------------

class TestPortManager:
    def test_port_manager_importable(self):
        from hal.port_manager import PortManager
        assert PortManager is not None

    def test_port_manager_register_sensor(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        sensor = MPU6050(port=1, i2c=_make_mock_i2c())
        pm.register_sensor(port=1, sensor=sensor)
        assert pm.get_sensor(1) is sensor

    def test_port_manager_register_motor(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        pwm, dir_pin, enc_a, enc_b = _make_mock_motor_hw()
        motor = MotorN20(port=2, pwm=pwm, dir_pin=dir_pin, enc_a=enc_a, enc_b=enc_b)
        pm.register_motor(port=2, motor=motor)
        assert pm.get_motor(2) is motor

    def test_port_manager_get_unknown_sensor_returns_none(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        assert pm.get_sensor(99) is None

    def test_port_manager_get_unknown_motor_returns_none(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        assert pm.get_motor(99) is None

    def test_port_manager_init_all_inits_registered_devices(self):
        """init_all() calls init() on every registered sensor and motor."""
        from hal.port_manager import PortManager
        pm = PortManager()

        mock_sensor = MagicMock()
        mock_sensor.init.return_value = True
        mock_motor = MagicMock()
        mock_motor.init.return_value = True

        pm.register_sensor(1, mock_sensor)
        pm.register_motor(2, mock_motor)
        pm.init_all()

        mock_sensor.init.assert_called_once()
        mock_motor.init.assert_called_once()

    def test_port_manager_init_all_returns_true_when_all_succeed(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        s = MagicMock(); s.init.return_value = True
        m = MagicMock(); m.init.return_value = True
        pm.register_sensor(1, s)
        pm.register_motor(2, m)
        assert pm.init_all() is True

    def test_port_manager_init_all_returns_false_if_any_fails(self):
        from hal.port_manager import PortManager
        pm = PortManager()
        s = MagicMock(); s.init.return_value = False   # fails
        m = MagicMock(); m.init.return_value = True
        pm.register_sensor(1, s)
        pm.register_motor(2, m)
        assert pm.init_all() is False

    def test_port_manager_deinit_all(self):
        """deinit_all() calls deinit() on every registered device."""
        from hal.port_manager import PortManager
        pm = PortManager()
        s = MagicMock(); s.init.return_value = True
        m = MagicMock(); m.init.return_value = True
        pm.register_sensor(1, s)
        pm.register_motor(2, m)
        pm.init_all()
        pm.deinit_all()
        s.deinit.assert_called_once()
        m.deinit.assert_called_once()

    def test_port_manager_list_ports(self):
        """list_ports() returns dict with sensor and motor port numbers."""
        from hal.port_manager import PortManager
        pm = PortManager()
        s = MagicMock()
        m = MagicMock()
        pm.register_sensor(1, s)
        pm.register_motor(2, m)
        ports = pm.list_ports()
        assert 1 in ports["sensors"]
        assert 2 in ports["motors"]


# ---------------------------------------------------------------------------
# 3. Full stack integration — BootManager + PortManager + drivers
# ---------------------------------------------------------------------------

class TestFullStackIntegration:
    def _make_full_system(self):
        """Wire up BootManager with PortManager containing real driver instances."""
        from hal.port_manager import PortManager

        bm = BootManager()
        bm.matrix = _make_mock_matrix()
        bm.ble = _make_mock_ble_service()

        pm = PortManager()

        # Port 1: IMU sensor
        imu = MPU6050(port=1, i2c=_make_mock_i2c())
        pm.register_sensor(1, imu)

        # Port 2: Motor
        pwm, dir_pin, enc_a, enc_b = _make_mock_motor_hw()
        motor = MotorN20(port=2, pwm=pwm, dir_pin=dir_pin, enc_a=enc_a, enc_b=enc_b)
        pm.register_motor(2, motor)

        bm.port_manager = pm
        return bm, pm, imu, motor

    def test_full_boot_sequence_succeeds(self):
        bm, pm, imu, motor = self._make_full_system()
        assert bm.run() is True
        assert pm.init_all() is True

    def test_imu_readable_after_boot(self):
        bm, pm, imu, motor = self._make_full_system()
        bm.run()
        pm.init_all()
        data = imu.read()
        assert "ax" in data
        assert "gz" in data
        assert "temp" in data

    def test_motor_controllable_after_boot(self):
        bm, pm, imu, motor = self._make_full_system()
        bm.run()
        pm.init_all()
        motor.run(50)
        assert motor._initialized is True

    def test_motor_angle_zero_after_init(self):
        bm, pm, imu, motor = self._make_full_system()
        bm.run()
        pm.init_all()
        assert motor.angle() == 0.0

    def test_ble_frame_round_trip_after_boot(self):
        """BLE protocol works correctly in the context of a booted system."""
        bm, pm, imu, motor = self._make_full_system()
        bm.run()
        # Simulate IDE sending CMD_STOP
        frame = build_cmd_stop()
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_CMD_STOP
        assert payload == b""

    def test_deinit_all_after_boot(self):
        """Full teardown: all drivers deinit cleanly."""
        bm, pm, imu, motor = self._make_full_system()
        bm.run()
        pm.init_all()
        pm.deinit_all()   # must not raise
        assert imu._initialized is False
        assert motor._initialized is False
