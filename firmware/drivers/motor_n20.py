"""
N20 micro gear motor driver with magnetic quadrature encoder.

Hardware interface (all injected at construction per ADR-005):
  pwm     : PWM output pin → motor driver IC speed control
  dir_pin : GPIO output pin → motor driver IC direction
  enc_a   : GPIO input pin with IRQ → encoder channel A
  enc_b   : GPIO input pin with IRQ → encoder channel B

Speed → PWM mapping:
  Input range : -100 to 100 (clamped)
  Output range: 0 to 65535 (16-bit PWM duty cycle)
  Direction   : dir_pin = 1 (forward) / 0 (reverse)

Encoder → angle conversion:
  counts_per_rev defaults to 360 (12 CPR × 30:1 gear ratio = 1 count/degree)
  angle = encoder_count / counts_per_rev * 360.0

PWM frequency: 20kHz (above audible range, reduces motor whine).
"""

from hal.motor import Motor

PWM_FREQ_HZ  = 20_000
PWM_MAX      = 65535   # 16-bit full duty
SPEED_MAX    = 100


def _speed_to_duty(speed: int) -> int:
    """Convert speed (0–100 absolute) to 16-bit PWM duty cycle."""
    return int(abs(speed) / SPEED_MAX * PWM_MAX)


class MotorN20(Motor):
    """Driver for N20 micro gear motor with magnetic encoder.

    Usage:
        motor = MotorN20(port=1, pwm=..., dir_pin=..., enc_a=..., enc_b=...)
        if motor.init():
            motor.run(50)       # 50% forward
            motor.run(-30)      # 30% reverse
            deg = motor.angle() # degrees from start
            motor.stop()
        motor.deinit()
    """

    def __init__(
        self,
        port: int,
        pwm,
        dir_pin,
        enc_a,
        enc_b,
        counts_per_rev: int = 360,
    ):
        super().__init__(port)
        self._pwm           = pwm
        self._dir_pin       = dir_pin
        self._enc_a         = enc_a
        self._enc_b         = enc_b
        self._counts_per_rev = counts_per_rev
        self._encoder_count  = 0

    # ------------------------------------------------------------------
    # Motor interface
    # ------------------------------------------------------------------

    def init(self) -> bool:
        """Initialise the motor driver.

        - Sets PWM frequency to 20kHz
        - Leaves motor stopped (duty = 0)
        - Registers encoder IRQ handlers on enc_a and enc_b
        - Resets encoder count to 0

        Returns True on success, False if hardware setup fails.
        """
        try:
            self._pwm.freq(PWM_FREQ_HZ)
            self._pwm.duty_u16(0)
            self._encoder_count = 0

            # Register rising-edge IRQ on encoder channel A
            # In production firmware this calls machine.Pin.IRQ_RISING
            # The handler increments/decrements based on channel B state
            self._enc_a.irq(handler=self._enc_a_handler, trigger=1)
            self._enc_b.irq(handler=self._enc_b_handler, trigger=1)

            self._initialized = True
            return True

        except OSError:
            return False

    def run(self, speed: int) -> None:
        """Run motor at speed (-100 to 100).

        Positive speed = forward (dir_pin = 1).
        Negative speed = reverse (dir_pin = 0).
        Speed is clamped to [-100, 100].

        Raises RuntimeError if init() has not been called.
        """
        if not self._initialized:
            raise RuntimeError("MotorN20 not initialised. Call init() first.")

        speed = max(-SPEED_MAX, min(SPEED_MAX, speed))

        if speed >= 0:
            self._dir_pin.value(1)
        else:
            self._dir_pin.value(0)

        self._pwm.duty_u16(_speed_to_duty(speed))

    def stop(self) -> None:
        """Stop the motor immediately (duty = 0).

        Raises RuntimeError if init() has not been called.
        """
        if not self._initialized:
            raise RuntimeError("MotorN20 not initialised. Call init() first.")
        self._pwm.duty_u16(0)

    def angle(self) -> float:
        """Return current shaft angle in degrees from the last reset.

        Raises RuntimeError if init() has not been called.
        """
        if not self._initialized:
            raise RuntimeError("MotorN20 not initialised. Call init() first.")
        return self._encoder_count / self._counts_per_rev * 360.0

    def reset_angle(self) -> None:
        """Reset encoder count to zero (redefine current position as 0°)."""
        self._encoder_count = 0

    def deinit(self) -> None:
        """Stop motor, release PWM resource, mark uninitialised."""
        if self._initialized:
            try:
                self._pwm.duty_u16(0)
            except OSError:
                pass
            try:
                self._pwm.deinit()
            except OSError:
                pass
        super().deinit()

    # ------------------------------------------------------------------
    # Encoder IRQ handlers (called from interrupt context on real hardware)
    # ------------------------------------------------------------------

    def _enc_a_handler(self, pin) -> None:
        """Channel A rising edge — direction determined by channel B state."""
        if self._enc_b.value():
            self._encoder_count -= 1
        else:
            self._encoder_count += 1

    def _enc_b_handler(self, pin) -> None:
        """Channel B rising edge — direction determined by channel A state."""
        if self._enc_a.value():
            self._encoder_count += 1
        else:
            self._encoder_count -= 1
