# Tests for HAL base classes
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from firmware.hal.sensor import Sensor
from firmware.hal.motor import Motor


class TestSensorBase:
    def test_sensor_stores_port(self):
        s = Sensor(port=1)
        assert s.port == 1

    def test_sensor_not_initialized_on_create(self):
        s = Sensor(port=1)
        assert s._initialized is False

    def test_sensor_init_raises_not_implemented(self):
        s = Sensor(port=1)
        with pytest.raises(NotImplementedError):
            s.init()

    def test_sensor_read_raises_not_implemented(self):
        s = Sensor(port=1)
        with pytest.raises(NotImplementedError):
            s.read()

    def test_sensor_deinit_sets_initialized_false(self):
        s = Sensor(port=1)
        s._initialized = True
        s.deinit()
        assert s._initialized is False


class TestMotorBase:
    def test_motor_stores_port(self):
        m = Motor(port=2)
        assert m.port == 2

    def test_motor_not_initialized_on_create(self):
        m = Motor(port=2)
        assert m._initialized is False

    def test_motor_init_raises_not_implemented(self):
        m = Motor(port=2)
        with pytest.raises(NotImplementedError):
            m.init()

    def test_motor_run_raises_not_implemented(self):
        m = Motor(port=2)
        with pytest.raises(NotImplementedError):
            m.run(50)

    def test_motor_stop_raises_not_implemented(self):
        m = Motor(port=2)
        with pytest.raises(NotImplementedError):
            m.stop()

    def test_motor_angle_raises_not_implemented(self):
        m = Motor(port=2)
        with pytest.raises(NotImplementedError):
            m.angle()

    def test_motor_deinit_sets_initialized_false(self):
        m = Motor(port=2)
        m._initialized = True
        m.deinit()
        assert m._initialized is False
