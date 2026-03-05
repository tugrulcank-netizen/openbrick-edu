"""
Tests for the N20 micro gear motor driver with magnetic encoder.

Mock strategy:
  - MockPWM   : simulates the PWM output pin (motor speed control)
  - MockPin   : simulates a GPIO direction pin and encoder input pin
  - MockEncoder: simulates quadrature encoder pulse counting

N20 driver hardware interface:
  - pwm_pin   : PWM output → motor driver IC (speed)
  - dir_pin   : GPIO output → motor driver IC (direction)
  - enc_a_pin : GPIO input with interrupt → encoder channel A
  - enc_b_pin : GPIO input with interrupt → encoder channel B

Encoder → angle conversion:
  N20 motors typically have 12 CPR (counts per revolution) on the encoder
  shaft. With a 30:1 gear ratio (common N20 variant), that gives
  12 × 30 = 360 counts per output shaft revolution = 1 count per degree.
  We use COUNTS_PER_REV = 360 as the default (configurable at construction).
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from hal.motor import Motor  # noqa: E402


# ---------------------------------------------------------------------------
# Mock hardware peripherals
# ---------------------------------------------------------------------------

def _make_mock_pwm():
    """Simulates a PWM output pin (e.g. machine.PWM)."""
    mock = MagicMock()
    mock.freq = MagicMock()
    mock.duty_u16 = MagicMock()
    mock.deinit = MagicMock()
    return mock


def _make_mock_pin():
    """Simulates a GPIO pin (e.g. machine.Pin)."""
    mock = MagicMock()
    mock.value = MagicMock(return_value=0)
    mock.irq = MagicMock()
    return mock


def _make_driver(port=1, counts_per_rev=360):
    """Instantiate MotorN20 with all mock hardware injected."""
    from drivers.motor_n20 import MotorN20
    pwm  = _make_mock_pwm()
    dir_pin  = _make_mock_pin()
    enc_a    = _make_mock_pin()
    enc_b    = _make_mock_pin()
    return MotorN20(
        port=port,
        pwm=pwm,
        dir_pin=dir_pin,
        enc_a=enc_a,
        enc_b=enc_b,
        counts_per_rev=counts_per_rev,
    ), pwm, dir_pin, enc_a, enc_b


# ---------------------------------------------------------------------------
# 1. Class contract — inherits from Motor
# ---------------------------------------------------------------------------

class TestMotorN20Inheritance:
    def test_is_motor_subclass(self):
        from drivers.motor_n20 import MotorN20
        assert issubclass(MotorN20, Motor)

    def test_stores_port(self):
        driver, *_ = _make_driver(port=2)
        assert driver.port == 2

    def test_not_initialized_at_construction(self):
        driver, *_ = _make_driver()
        assert driver._initialized is False


# ---------------------------------------------------------------------------
# 2. init()
# ---------------------------------------------------------------------------

class TestMotorN20Init:
    def test_init_returns_true(self):
        driver, *_ = _make_driver()
        assert driver.init() is True

    def test_init_sets_initialized_flag(self):
        driver, *_ = _make_driver()
        driver.init()
        assert driver._initialized is True

    def test_init_sets_pwm_frequency(self):
        """init() must configure PWM frequency (target: 20kHz, above audible range)."""
        driver, pwm, *_ = _make_driver()
        driver.init()
        pwm.freq.assert_called_once_with(20_000)

    def test_init_stops_motor(self):
        """init() must leave motor stopped (duty = 0)."""
        driver, pwm, *_ = _make_driver()
        driver.init()
        pwm.duty_u16.assert_called_with(0)

    def test_init_registers_encoder_interrupts(self):
        """init() must register IRQ handlers on both encoder pins."""
        driver, _, _, enc_a, enc_b = _make_driver()
        driver.init()
        assert enc_a.irq.called
        assert enc_b.irq.called

    def test_init_resets_angle_to_zero(self):
        """Angle must be 0.0 after init()."""
        driver, *_ = _make_driver()
        driver.init()
        assert driver.angle() == 0.0

    def test_init_returns_false_on_error(self):
        """init() returns False (does not raise) if PWM setup raises."""
        from drivers.motor_n20 import MotorN20
        pwm = _make_mock_pwm()
        pwm.freq.side_effect = OSError("PWM error")
        driver = MotorN20(
            port=1, pwm=pwm,
            dir_pin=_make_mock_pin(),
            enc_a=_make_mock_pin(),
            enc_b=_make_mock_pin(),
        )
        assert driver.init() is False


# ---------------------------------------------------------------------------
# 3. run()
# ---------------------------------------------------------------------------

class TestMotorN20Run:
    def setup_method(self):
        self.driver, self.pwm, self.dir_pin, self.enc_a, self.enc_b = _make_driver()
        self.driver.init()
        self.pwm.reset_mock()
        self.dir_pin.reset_mock()

    def test_run_positive_speed_sets_forward_direction(self):
        """Positive speed → dir_pin = 1 (forward)."""
        self.driver.run(50)
        self.dir_pin.value.assert_called_with(1)

    def test_run_negative_speed_sets_reverse_direction(self):
        """Negative speed → dir_pin = 0 (reverse)."""
        self.driver.run(-50)
        self.dir_pin.value.assert_called_with(0)

    def test_run_zero_speed_stops_motor(self):
        """speed=0 → duty_u16 = 0."""
        self.driver.run(0)
        self.pwm.duty_u16.assert_called_with(0)

    def test_run_full_forward_sets_max_duty(self):
        """speed=100 → duty_u16 = 65535 (full 16-bit PWM)."""
        self.driver.run(100)
        self.pwm.duty_u16.assert_called_with(65535)

    def test_run_full_reverse_sets_max_duty(self):
        """speed=-100 → duty_u16 = 65535 (direction handled by dir_pin)."""
        self.driver.run(-100)
        self.pwm.duty_u16.assert_called_with(65535)

    def test_run_half_speed_sets_half_duty(self):
        """speed=50 → duty_u16 = 32767 (50% of 65535, rounded down)."""
        self.driver.run(50)
        self.pwm.duty_u16.assert_called_with(32767)

    def test_run_clamps_speed_above_100(self):
        """speed=150 is clamped to 100 → duty_u16 = 65535."""
        self.driver.run(150)
        self.pwm.duty_u16.assert_called_with(65535)

    def test_run_clamps_speed_below_minus_100(self):
        """speed=-150 is clamped to -100 → duty_u16 = 65535."""
        self.driver.run(-150)
        self.pwm.duty_u16.assert_called_with(65535)

    def test_run_raises_if_not_initialized(self):
        """run() raises RuntimeError if called before init()."""
        from drivers.motor_n20 import MotorN20
        fresh = MotorN20(
            port=1, pwm=_make_mock_pwm(),
            dir_pin=_make_mock_pin(),
            enc_a=_make_mock_pin(),
            enc_b=_make_mock_pin(),
        )
        with pytest.raises(RuntimeError):
            fresh.run(50)


# ---------------------------------------------------------------------------
# 4. stop()
# ---------------------------------------------------------------------------

class TestMotorN20Stop:
    def setup_method(self):
        self.driver, self.pwm, self.dir_pin, *_ = _make_driver()
        self.driver.init()
        self.pwm.reset_mock()

    def test_stop_sets_duty_to_zero(self):
        self.driver.run(75)
        self.pwm.reset_mock()
        self.driver.stop()
        self.pwm.duty_u16.assert_called_with(0)

    def test_stop_raises_if_not_initialized(self):
        from drivers.motor_n20 import MotorN20
        fresh = MotorN20(
            port=1, pwm=_make_mock_pwm(),
            dir_pin=_make_mock_pin(),
            enc_a=_make_mock_pin(),
            enc_b=_make_mock_pin(),
        )
        with pytest.raises(RuntimeError):
            fresh.stop()


# ---------------------------------------------------------------------------
# 5. angle() — encoder pulse counting
# ---------------------------------------------------------------------------

class TestMotorN20Angle:
    def setup_method(self):
        # Use 360 counts/rev → 1 count = 1 degree (easy mental arithmetic)
        self.driver, _, _, self.enc_a, self.enc_b = _make_driver(counts_per_rev=360)
        self.driver.init()

    def _pulse(self, count: int, forward: bool = True):
        """Simulate encoder pulses by calling the internal counter directly."""
        # Each pulse increments or decrements the internal count
        for _ in range(count):
            if forward:
                self.driver._encoder_count += 1
            else:
                self.driver._encoder_count -= 1

    def test_angle_zero_after_init(self):
        assert self.driver.angle() == 0.0

    def test_angle_positive_after_forward_pulses(self):
        self._pulse(90, forward=True)   # 90 counts → 90°
        assert self.driver.angle() == pytest.approx(90.0, abs=0.01)

    def test_angle_negative_after_reverse_pulses(self):
        self._pulse(45, forward=False)  # -45 counts → -45°
        assert self.driver.angle() == pytest.approx(-45.0, abs=0.01)

    def test_angle_full_revolution(self):
        self._pulse(360, forward=True)  # 360 counts → 360°
        assert self.driver.angle() == pytest.approx(360.0, abs=0.01)

    def test_angle_fractional_degree(self):
        """With counts_per_rev=720, each count = 0.5°."""
        driver, _, _, _, _ = _make_driver(counts_per_rev=720)
        driver.init()
        driver._encoder_count = 1
        assert driver.angle() == pytest.approx(0.5, abs=0.001)

    def test_reset_angle_zeroes_encoder(self):
        """reset_angle() must zero the encoder count."""
        self._pulse(180)
        self.driver.reset_angle()
        assert self.driver.angle() == 0.0

    def test_angle_raises_if_not_initialized(self):
        from drivers.motor_n20 import MotorN20
        fresh = MotorN20(
            port=1, pwm=_make_mock_pwm(),
            dir_pin=_make_mock_pin(),
            enc_a=_make_mock_pin(),
            enc_b=_make_mock_pin(),
        )
        with pytest.raises(RuntimeError):
            fresh.angle()


# ---------------------------------------------------------------------------
# 6. deinit()
# ---------------------------------------------------------------------------

class TestMotorN20Deinit:
    def test_deinit_clears_initialized_flag(self):
        driver, *_ = _make_driver()
        driver.init()
        driver.deinit()
        assert driver._initialized is False

    def test_deinit_stops_motor(self):
        driver, pwm, *_ = _make_driver()
        driver.init()
        driver.run(60)
        pwm.reset_mock()
        driver.deinit()
        pwm.duty_u16.assert_called_with(0)

    def test_deinit_releases_pwm(self):
        """deinit() calls pwm.deinit() to release the hardware resource."""
        driver, pwm, *_ = _make_driver()
        driver.init()
        driver.deinit()
        pwm.deinit.assert_called_once()

    def test_deinit_safe_when_not_initialized(self):
        driver, *_ = _make_driver()
        driver.deinit()  # must not raise
        assert driver._initialized is False
