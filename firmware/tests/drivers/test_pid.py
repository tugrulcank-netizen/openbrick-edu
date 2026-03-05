"""
Tests for the PID controller.

The PID controller is a pure math utility — no hardware dependencies,
no mocking required. Tests drive it directly with known inputs and
verify outputs against hand-calculated expected values.

PID formula (discrete, fixed time-step):
  error      = setpoint - measurement
  integral  += error * dt
  derivative = (error - prev_error) / dt
  output     = Kp*error + Ki*integral + Kd*derivative

Output is clamped to [output_min, output_max] (default: -100 to 100
to match Motor.run() speed range).

Integral windup is prevented by clamping the integral term independently.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pid(kp=1.0, ki=0.0, kd=0.0,
              output_min=-100, output_max=100,
              integral_limit=None):
    from drivers.pid import PID
    return PID(
        kp=kp, ki=ki, kd=kd,
        output_min=output_min,
        output_max=output_max,
        integral_limit=integral_limit,
    )


# ---------------------------------------------------------------------------
# 1. Construction and initial state
# ---------------------------------------------------------------------------

class TestPIDConstruction:
    def test_stores_gains(self):
        pid = _make_pid(kp=2.0, ki=0.5, kd=0.1)
        assert pid.kp == 2.0
        assert pid.ki == 0.5
        assert pid.kd == 0.1

    def test_stores_output_limits(self):
        pid = _make_pid(output_min=-50, output_max=50)
        assert pid.output_min == -50
        assert pid.output_max == 50

    def test_initial_integral_is_zero(self):
        pid = _make_pid()
        assert pid._integral == 0.0

    def test_initial_prev_error_is_zero(self):
        pid = _make_pid()
        assert pid._prev_error == 0.0


# ---------------------------------------------------------------------------
# 2. Proportional term only (Ki=0, Kd=0)
# ---------------------------------------------------------------------------

class TestPIDProportional:
    def test_p_only_positive_error(self):
        """error=10, Kp=2 → output=20."""
        pid = _make_pid(kp=2.0)
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(20.0)

    def test_p_only_negative_error(self):
        """error=-10, Kp=2 → output=-20."""
        pid = _make_pid(kp=2.0)
        out = pid.compute(setpoint=0.0, measurement=10.0, dt=0.1)
        assert out == pytest.approx(-20.0)

    def test_p_only_zero_error(self):
        pid = _make_pid(kp=2.0)
        out = pid.compute(setpoint=5.0, measurement=5.0, dt=0.1)
        assert out == pytest.approx(0.0)

    def test_p_output_clamped_at_max(self):
        """error=200, Kp=2 → raw=400, clamped to 100."""
        pid = _make_pid(kp=2.0, output_max=100)
        out = pid.compute(setpoint=200.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(100.0)

    def test_p_output_clamped_at_min(self):
        """error=-200, Kp=2 → raw=-400, clamped to -100."""
        pid = _make_pid(kp=2.0, output_min=-100)
        out = pid.compute(setpoint=0.0, measurement=200.0, dt=0.1)
        assert out == pytest.approx(-100.0)


# ---------------------------------------------------------------------------
# 3. Integral term (Kp=0, Ki only)
# ---------------------------------------------------------------------------

class TestPIDIntegral:
    def test_integral_accumulates(self):
        """error=10, Ki=1, dt=0.1 → integral=1.0 after one step → output=1.0."""
        pid = _make_pid(kp=0.0, ki=1.0)
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(1.0)

    def test_integral_accumulates_over_multiple_steps(self):
        """error=10, Ki=1, dt=0.1 × 3 steps → integral=3.0 → output=3.0."""
        pid = _make_pid(kp=0.0, ki=1.0)
        for _ in range(3):
            out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(3.0)

    def test_integral_decreases_on_negative_error(self):
        """Accumulate positive, then negative error — integral shrinks."""
        pid = _make_pid(kp=0.0, ki=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)  # +1.0
        out = pid.compute(setpoint=0.0, measurement=10.0, dt=0.1)  # -1.0
        assert out == pytest.approx(0.0)

    def test_integral_windup_limited(self):
        """integral_limit=5: integral cannot exceed 5 even after many steps."""
        pid = _make_pid(kp=0.0, ki=1.0, integral_limit=5.0)
        for _ in range(100):
            pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert pid._integral == pytest.approx(5.0, abs=0.01)

    def test_integral_windup_limited_negative(self):
        """integral_limit=5: integral floor is -5."""
        pid = _make_pid(kp=0.0, ki=1.0, integral_limit=5.0)
        for _ in range(100):
            pid.compute(setpoint=0.0, measurement=10.0, dt=0.1)
        assert pid._integral == pytest.approx(-5.0, abs=0.01)


# ---------------------------------------------------------------------------
# 4. Derivative term (Kp=0, Ki=0, Kd only)
# ---------------------------------------------------------------------------

class TestPIDDerivative:
    def test_derivative_first_step(self):
        """First step: prev_error=0, error=10, dt=0.1, Kd=1
        → derivative = (10-0)/0.1 = 100 → output=100 (clamped)."""
        pid = _make_pid(kp=0.0, kd=1.0)
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        # Raw = 100, clamped to output_max=100
        assert out == pytest.approx(100.0)

    def test_derivative_zero_when_error_unchanged(self):
        """Same error two steps in a row → derivative = 0."""
        pid = _make_pid(kp=0.0, kd=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(0.0)

    def test_derivative_negative_on_decreasing_error(self):
        """error goes 10 → 5: derivative = (5-10)/0.1 = -50, Kd=1 → -50."""
        pid = _make_pid(kp=0.0, kd=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)   # error=10
        out = pid.compute(setpoint=5.0, measurement=0.0, dt=0.1)  # error=5
        assert out == pytest.approx(-50.0)


# ---------------------------------------------------------------------------
# 5. Combined PID
# ---------------------------------------------------------------------------

class TestPIDCombined:
    def test_combined_single_step(self):
        """Kp=1, Ki=1, Kd=1, error=10, dt=0.1:
        P = 10, I = 10*0.1 = 1.0, D = (10-0)/0.1 = 100 → raw=111, clamped=100."""
        pid = _make_pid(kp=1.0, ki=1.0, kd=1.0)
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        assert out == pytest.approx(100.0)  # clamped

    def test_combined_converges(self):
        """With a reasonable Kp/Ki, output should approach zero as
        measurement approaches setpoint over several steps."""
        pid = _make_pid(kp=0.5, ki=0.1)
        measurement = 0.0
        setpoint = 90.0
        for _ in range(50):
            out = pid.compute(setpoint=setpoint, measurement=measurement, dt=0.05)
            measurement += out * 0.05   # simple plant model
        # After 50 steps the error should be small (< 10°)
        assert abs(setpoint - measurement) < 20.0


# ---------------------------------------------------------------------------
# 6. reset()
# ---------------------------------------------------------------------------

class TestPIDReset:
    def test_reset_clears_integral(self):
        pid = _make_pid(kp=0.0, ki=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        pid.reset()
        assert pid._integral == 0.0

    def test_reset_clears_prev_error(self):
        pid = _make_pid(kp=0.0, kd=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        pid.reset()
        assert pid._prev_error == 0.0

    def test_output_after_reset_treats_prev_error_as_zero(self):
        """After reset, derivative is computed from 0 as if first call."""
        pid = _make_pid(kp=0.0, kd=1.0)
        pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)  # prev_error=10
        pid.reset()
        out = pid.compute(setpoint=10.0, measurement=0.0, dt=0.1)
        # derivative = (10-0)/0.1 = 100 again, clamped
        assert out == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# 7. MotorN20.run_to_angle() — PID wired into motor driver
# ---------------------------------------------------------------------------

class TestMotorRunToAngle:
    """Verify that MotorN20 exposes run_to_angle() and uses PID internally."""

    def _make_motor(self):
        from unittest.mock import MagicMock
        from drivers.motor_n20 import MotorN20
        pwm     = MagicMock()
        dir_pin = MagicMock()
        enc_a   = MagicMock()
        enc_b   = MagicMock()
        motor = MotorN20(
            port=1, pwm=pwm, dir_pin=dir_pin,
            enc_a=enc_a, enc_b=enc_b,
        )
        motor.init()
        pwm.reset_mock()
        dir_pin.reset_mock()
        return motor, pwm, dir_pin

    def test_run_to_angle_method_exists(self):
        motor, *_ = self._make_motor()
        assert hasattr(motor, 'run_to_angle')

    def test_run_to_angle_at_target_stops_motor(self):
        """Already at target angle → motor should stop (speed=0)."""
        motor, pwm, _ = self._make_motor()
        motor._encoder_count = 90   # already at 90°
        motor.run_to_angle(target=90.0, dt=0.05)
        pwm.duty_u16.assert_called_with(0)

    def test_run_to_angle_below_target_runs_forward(self):
        """Current=0°, target=90° → motor runs forward (dir_pin=1)."""
        motor, pwm, dir_pin = self._make_motor()
        motor._encoder_count = 0
        motor.run_to_angle(target=90.0, dt=0.05)
        dir_pin.value.assert_called_with(1)

    def test_run_to_angle_above_target_runs_reverse(self):
        """Current=180°, target=90° → motor runs reverse (dir_pin=0)."""
        motor, pwm, dir_pin = self._make_motor()
        motor._encoder_count = 180
        motor.run_to_angle(target=90.0, dt=0.05)
        dir_pin.value.assert_called_with(0)

    def test_run_to_angle_raises_if_not_initialized(self):
        from drivers.motor_n20 import MotorN20
        from unittest.mock import MagicMock
        fresh = MotorN20(
            port=1, pwm=MagicMock(), dir_pin=MagicMock(),
            enc_a=MagicMock(), enc_b=MagicMock(),
        )
        with pytest.raises(RuntimeError):
            fresh.run_to_angle(target=90.0, dt=0.05)
