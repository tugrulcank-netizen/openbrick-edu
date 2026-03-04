# Skill: Motor Control

Load this skill when working on motor drivers, PID control algorithms, or motor calibration for the OpenBrick EDU hub.

---

## Motor Types Supported

### Geekservo LEGO-Compatible Motors (Primary)

| Parameter              | 9g Grey Servo       | 2kg Red Servo        | Continuous Motor     |
|-----------------------|---------------------|----------------------|----------------------|
| Model                 | Geekservo 9g        | Geekservo 2kg        | Geekservo 360°       |
| Type                  | Positional servo    | Positional servo     | Continuous rotation   |
| Voltage               | 3.3–6V              | 3.3–6V               | 3.3–6V               |
| Torque                | 0.5 kg·cm @ 4.8V   | 2.0 kg·cm @ 4.8V    | 0.5 kg·cm @ 4.8V    |
| Rotation range        | 0–360° (with limits)| 0–360° (with limits) | Continuous            |
| Control signal        | PWM (50 Hz, 500–2500µs) | PWM (50 Hz, 500–2500µs) | PWM (50 Hz)    |
| Position feedback     | None (open-loop)    | None (open-loop)     | None (open-loop)     |
| LEGO compatible       | Yes (Technic axle)  | Yes (Technic axle)   | Yes (Technic axle)   |

### N20 Micro Gear Motors with Encoder (Alternative)

| Parameter              | Value                                      |
|-----------------------|--------------------------------------------|
| Voltage               | 3–6V DC                                    |
| RPM (no load, 6V)    | ~200 RPM                                   |
| Gear ratio            | 1:100 (typical)                            |
| Encoder type          | Magnetic, dual-channel (A/B quadrature)    |
| Encoder resolution    | 7 pulses per motor revolution (700 per output) |
| Position feedback     | Yes — closed-loop PID possible              |
| LEGO compatible       | Requires custom 3D-printed mount + axle adapter |

**ADR note:** The choice between Geekservo and N20 is recorded in `docs/adr/ADR-002-motor-selection.md`. Geekservo is preferred for its native LEGO compatibility. N20 is an alternative when precise closed-loop control is required.

---

## HAL Motor Base Class Contract

```python
from abc import ABC, abstractmethod
from hal.port import Port


class Motor(ABC):
    """Base class for all OpenBrick EDU motor drivers."""

    def __init__(self, port: Port) -> None:
        self._port = port
        self._angle: int = 0          # Cumulative angle in degrees
        self._speed: int = 0          # Current speed (-100 to 100)
        self._stalled: bool = False
        self._initialized: bool = False

    @abstractmethod
    def init(self) -> None:
        """Initialize motor hardware (PWM, encoder, GPIO)."""
        ...

    @abstractmethod
    def run(self, speed: int) -> None:
        """Run motor at given speed.

        Args:
            speed: -100 (full reverse) to 100 (full forward). 0 = stop.
        """
        ...

    @abstractmethod
    def stop(self, brake: bool = True) -> None:
        """Stop the motor.

        Args:
            brake: True = actively hold position, False = coast to stop.
        """
        ...

    @abstractmethod
    def run_to_position(self, degrees: int, speed: int = 50) -> None:
        """Move motor to an absolute angular position.

        Args:
            degrees: Target angle in degrees (absolute from reset point).
            speed: Movement speed, 1–100. Ignored by open-loop servos.

        Blocks until position reached or timeout (2 seconds).
        """
        ...

    @abstractmethod
    def get_angle(self) -> int:
        """Return current cumulative angle in degrees."""
        ...

    @abstractmethod
    def reset_angle(self) -> None:
        """Reset cumulative angle to zero at current position."""
        ...

    def is_stalled(self) -> bool:
        """Check if motor is stalled (overcurrent detected)."""
        return self._stalled

    def get_speed(self) -> int:
        """Return current commanded speed."""
        return self._speed
```

---

## Geekservo PWM Control Implementation

### PWM Configuration

```python
from machine import Pin, PWM

# PWM constants for Geekservo
_PWM_FREQ: int = 50           # 50 Hz (20ms period) — standard for servos
_PULSE_MIN_US: int = 500      # 0° position
_PULSE_MAX_US: int = 2500     # 360° position (or max for limited range)
_PULSE_CENTER_US: int = 1500  # 180° / center / stop (for continuous)

def _speed_to_pulse(speed: int) -> int:
    """Convert speed (-100 to 100) to PWM pulse width in microseconds.

    For continuous rotation Geekservo:
      -100 → 500µs (full reverse)
         0 → 1500µs (stop)
       100 → 2500µs (full forward)

    For positional Geekservo:
      This maps speed to a rotation rate, not directly to a position.
    """
    speed = max(-100, min(100, speed))
    return _PULSE_CENTER_US + (speed * (_PULSE_MAX_US - _PULSE_CENTER_US) // 100)

def _angle_to_pulse(degrees: int) -> int:
    """Convert angle (0–360) to PWM pulse width.

    For positional Geekservo:
      0° → 500µs
      180° → 1500µs
      360° → 2500µs
    """
    degrees = max(0, min(360, degrees))
    return _PULSE_MIN_US + (degrees * (_PULSE_MAX_US - _PULSE_MIN_US) // 360)


class GeekservoMotor(Motor):
    """Driver for Geekservo LEGO-compatible motors (PWM-controlled)."""

    def init(self) -> None:
        self._pwm = PWM(Pin(self._port.pwm_pin), freq=_PWM_FREQ)
        self._pwm.duty_ns(0)  # Start stopped
        self._initialized = True

    def run(self, speed: int) -> None:
        if not self._initialized:
            raise MotorError("Motor not initialized")
        self._speed = max(-100, min(100, speed))
        pulse_us = _speed_to_pulse(self._speed)
        self._pwm.duty_ns(pulse_us * 1000)  # duty_ns takes nanoseconds

    def stop(self, brake: bool = True) -> None:
        if brake:
            # Send center pulse to hold position
            self._pwm.duty_ns(_PULSE_CENTER_US * 1000)
        else:
            # Disable PWM entirely — motor coasts
            self._pwm.duty_ns(0)
        self._speed = 0

    def run_to_position(self, degrees: int, speed: int = 50) -> None:
        """Move to angular position (open-loop for Geekservo).

        Note: Geekservo positional servos are open-loop — accuracy
        depends on calibration, not PID. ±5° typical accuracy.
        For ±2° accuracy, use N20 motors with PID (see below).
        """
        pulse_us = _angle_to_pulse(degrees)
        self._pwm.duty_ns(pulse_us * 1000)
        self._angle = degrees
        # Wait for servo to reach position (approximate)
        time.sleep_ms(max(200, abs(degrees - self._angle) * 2))

    def get_angle(self) -> int:
        # Open-loop: return last commanded angle
        return self._angle

    def reset_angle(self) -> None:
        self._angle = 0
```

---

## PID Controller for N20 Encoder Motors

### PID Implementation

```python
import time


class PIDController:
    """Discrete PID controller for motor position control.

    Runs at 100 Hz in a timer interrupt. Do NOT block this with
    I2C reads or other slow operations.
    """

    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.05,
        kd: float = 0.1,
        output_min: int = -100,
        output_max: int = 100,
        deadband: int = 2,          # ±2° dead zone — don't correct tiny errors
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.deadband = deadband

        self._setpoint: float = 0.0
        self._integral: float = 0.0
        self._last_error: float = 0.0
        self._last_time_ms: int = 0
        self._enabled: bool = False

        # Anti-windup: clamp integral to prevent runaway
        self._integral_max: float = 50.0

    def set_target(self, target_degrees: float) -> None:
        """Set the target angle in degrees."""
        self._setpoint = target_degrees
        self._integral = 0.0  # Reset integral on new target
        self._last_error = 0.0
        self._enabled = True

    def update(self, current_degrees: float) -> int:
        """Compute PID output. Call at 100 Hz from timer interrupt.

        Args:
            current_degrees: Current encoder-measured angle

        Returns:
            Motor speed command: -100 to 100
        """
        if not self._enabled:
            return 0

        now_ms = time.ticks_ms()
        dt = time.ticks_diff(now_ms, self._last_time_ms) / 1000.0
        self._last_time_ms = now_ms

        if dt <= 0 or dt > 0.1:  # Guard against timer glitches
            dt = 0.01  # Default to 10ms

        error = self._setpoint - current_degrees

        # Deadband: if close enough, stop correcting
        if abs(error) <= self.deadband:
            self._integral = 0.0
            self._enabled = False
            return 0

        # Proportional
        p = self.kp * error

        # Integral with anti-windup
        self._integral += error * dt
        self._integral = max(-self._integral_max, min(self._integral_max, self._integral))
        i = self.ki * self._integral

        # Derivative
        d = self.kd * (error - self._last_error) / dt if dt > 0 else 0.0
        self._last_error = error

        # Output
        output = p + i + d
        output = max(self.output_min, min(self.output_max, int(output)))

        return output

    def stop(self) -> None:
        """Disable PID controller."""
        self._enabled = False
        self._integral = 0.0
```

### Encoder Reading

```python
from machine import Pin


class QuadratureEncoder:
    """Read quadrature encoder for N20 motor position feedback.

    Uses ESP32 PCNT (Pulse Counter) peripheral for hardware-accelerated
    counting. Falls back to interrupt-based counting if PCNT unavailable.
    """

    def __init__(self, pin_a: int, pin_b: int, pulses_per_rev: int = 700) -> None:
        self._pin_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self._pin_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self._pulses_per_rev = pulses_per_rev
        self._count: int = 0
        self._offset: int = 0

        # Setup interrupt-based counting
        self._pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._isr)

    def _isr(self, pin) -> None:
        """Interrupt handler for encoder pulse."""
        if self._pin_a.value() == self._pin_b.value():
            self._count += 1
        else:
            self._count -= 1

    def get_angle_degrees(self) -> int:
        """Return current angle in degrees (cumulative)."""
        return int((self._count - self._offset) * 360 / self._pulses_per_rev)

    def reset(self) -> None:
        """Reset angle to zero at current position."""
        self._offset = self._count
```

### Combining PID + Encoder + Motor

```python
from machine import Timer


class N20MotorWithPID(Motor):
    """N20 gear motor with magnetic encoder and PID position control."""

    PID_FREQ_HZ: int = 100  # 100 Hz PID loop

    def init(self) -> None:
        # Initialize PWM for motor driver (H-bridge, not servo PWM)
        self._pwm_fwd = PWM(Pin(self._port.motor_fwd_pin), freq=20_000)
        self._pwm_rev = PWM(Pin(self._port.motor_rev_pin), freq=20_000)

        # Initialize encoder
        self._encoder = QuadratureEncoder(
            self._port.encoder_a_pin,
            self._port.encoder_b_pin,
        )

        # Initialize PID
        self._pid = PIDController(kp=1.0, ki=0.05, kd=0.1)

        # Start PID timer (100 Hz)
        self._timer = Timer(self._port.timer_id)
        self._timer.init(
            freq=self.PID_FREQ_HZ,
            mode=Timer.PERIODIC,
            callback=self._pid_tick,
        )

        self._initialized = True

    def _pid_tick(self, timer) -> None:
        """Timer callback: update PID and apply motor output."""
        current = self._encoder.get_angle_degrees()
        output = self._pid.update(current)
        self._apply_speed(output)

    def _apply_speed(self, speed: int) -> None:
        """Apply speed to H-bridge motor driver.

        speed > 0: forward, speed < 0: reverse, speed == 0: brake
        """
        duty = abs(speed) * 1023 // 100  # 0–1023 duty range
        if speed > 0:
            self._pwm_fwd.duty(duty)
            self._pwm_rev.duty(0)
        elif speed < 0:
            self._pwm_fwd.duty(0)
            self._pwm_rev.duty(duty)
        else:
            # Active brake: both pins high
            self._pwm_fwd.duty(1023)
            self._pwm_rev.duty(1023)

    def run(self, speed: int) -> None:
        self._pid.stop()  # Disable PID for direct speed control
        self._speed = max(-100, min(100, speed))
        self._apply_speed(self._speed)

    def stop(self, brake: bool = True) -> None:
        self._pid.stop()
        self._speed = 0
        if brake:
            self._apply_speed(0)  # Active brake
        else:
            self._pwm_fwd.duty(0)
            self._pwm_rev.duty(0)

    def run_to_position(self, degrees: int, speed: int = 50) -> None:
        """Move to target angle using PID.

        Blocks until position reached (within ±2°) or 2-second timeout.
        """
        self._pid.output_max = abs(speed)
        self._pid.output_min = -abs(speed)
        self._pid.set_target(degrees)

        # Wait for PID to converge
        timeout_ms = 2000
        start = time.ticks_ms()
        while self._pid._enabled:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                self._pid.stop()
                self._stalled = True
                break
            time.sleep_ms(10)

        self._angle = self._encoder.get_angle_degrees()

    def get_angle(self) -> int:
        return self._encoder.get_angle_degrees()

    def reset_angle(self) -> None:
        self._encoder.reset()
        self._angle = 0
```

---

## Motor Calibration Procedure

### Geekservo Calibration

1. **Center calibration:** Send center pulse (1500µs). Mark physical position as 0°.
2. **Range calibration:** Sweep from 500µs to 2500µs, measure actual angle with protractor.
3. **Dead zone detection:** Slowly increase pulse from center — note the pulse at which motion starts.
4. Store calibration in `config/motor_calibration.json`:

```json
{
  "port": 1,
  "motor_type": "geekservo_360",
  "center_pulse_us": 1500,
  "min_pulse_us": 520,
  "max_pulse_us": 2480,
  "dead_zone_us": 30,
  "calibration_date": "2026-03-15"
}
```

### N20 PID Tuning

1. **Start with Kp only:** Set Ki=0, Kd=0. Increase Kp until the motor oscillates around the target, then reduce by 50%.
2. **Add Kd:** Increase Kd until oscillation is damped. Typical: Kd = Kp × 0.1.
3. **Add Ki:** Small Ki to eliminate steady-state error. Typical: Ki = Kp × 0.05.
4. **Test:**
   - Step response: 0° → 90° — should reach target within 500ms, overshoot < 5°.
   - Accuracy: command 10 positions, measure actual — target ±2° (NFR requirement).
   - Disturbance rejection: push motor gently — should return to target.
5. Store tuned values per motor unit (they vary) in `config/pid_tuning.json`.

---

## Stall Detection

```python
# Stall detection constants
_STALL_CURRENT_THRESHOLD: int = 800   # ADC reading indicating stall
_STALL_DURATION_MS: int = 500         # Must exceed threshold for this long

def _check_stall(self) -> bool:
    """Check if motor is stalled by monitoring current draw.

    Uses ESP32-S3 ADC to read motor driver current sense pin.
    Stall = sustained overcurrent for > 500ms.
    """
    current = self._adc.read()
    if current > _STALL_CURRENT_THRESHOLD:
        if not self._stall_start:
            self._stall_start = time.ticks_ms()
        elif time.ticks_diff(time.ticks_ms(), self._stall_start) > _STALL_DURATION_MS:
            self._stalled = True
            self.stop(brake=False)  # Coast to reduce stress
            return True
    else:
        self._stall_start = None
        self._stalled = False
    return False
```

---

## Testing Motor Drivers

### Key Test Cases

- [ ] `run(100)` applies forward PWM, `run(-100)` applies reverse
- [ ] `run(0)` stops the motor
- [ ] Speed values are clamped to -100..100
- [ ] `stop(brake=True)` holds position, `stop(brake=False)` coasts
- [ ] `run_to_position()` reaches target within ±2° (with encoder)
- [ ] `run_to_position()` times out after 2 seconds if target unreachable
- [ ] `reset_angle()` sets current position as zero
- [ ] Stall detection triggers after sustained overcurrent
- [ ] PID integral resets on new target (no windup carryover)
- [ ] PID deadband prevents micro-corrections at target

### Mock Strategy

- Mock `machine.PWM` and `machine.Pin` — verify duty cycle values
- Mock `machine.Timer` — call the PID tick callback manually in tests
- Mock encoder `_isr` — simulate pulse counts by setting `_count` directly
- Test PID controller independently with synthetic position data
