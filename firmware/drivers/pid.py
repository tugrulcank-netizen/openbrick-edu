"""
PID controller for OpenBrick EDU.

Pure math utility — no hardware dependencies. Designed for motor
angle positioning but reusable for any closed-loop control need.

Usage:
    pid = PID(kp=2.0, ki=0.1, kd=0.05, output_min=-100, output_max=100)
    # In control loop (call at fixed dt intervals):
    output = pid.compute(setpoint=90.0, measurement=current_angle, dt=0.05)
    motor.run(int(output))

Tuning defaults for N20 motor angle control (starting point):
    Kp = 1.5   — proportional: main driver toward target
    Ki = 0.05  — integral: eliminate steady-state error
    Kd = 0.02  — derivative: dampen oscillation
    integral_limit = 50  — prevent windup on large angle errors
"""


class PID:
    """Discrete PID controller with integral windup protection.

    Args:
        kp: Proportional gain.
        ki: Integral gain.
        kd: Derivative gain.
        output_min: Lower clamp on output (default -100).
        output_max: Upper clamp on output (default 100).
        integral_limit: Clamp on integral accumulator (optional).
            If None, integral is only limited by output_min/output_max.
    """

    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.0,
        kd: float = 0.0,
        output_min: float = -100.0,
        output_max: float = 100.0,
        integral_limit: float | None = None,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self._integral_limit = integral_limit

        self._integral   = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint: float, measurement: float, dt: float) -> float:
        """Compute PID output for one time step.

        Args:
            setpoint:    Desired value (e.g. target angle in degrees).
            measurement: Current value (e.g. current angle in degrees).
            dt:          Time elapsed since last call in seconds.

        Returns:
            Control output clamped to [output_min, output_max].
        """
        error = setpoint - measurement

        # Proportional
        p = self.kp * error

        # Integral with optional windup limit
        self._integral += error * dt
        if self._integral_limit is not None:
            self._integral = max(
                -self._integral_limit,
                min(self._integral_limit, self._integral),
            )
        i = self.ki * self._integral

        # Derivative (on error, not measurement — avoids derivative kick)
        d = self.kd * (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        raw = p + i + d
        return max(self.output_min, min(self.output_max, raw))

    def reset(self) -> None:
        """Reset internal state. Call when re-engaging after a stop."""
        self._integral   = 0.0
        self._prev_error = 0.0
