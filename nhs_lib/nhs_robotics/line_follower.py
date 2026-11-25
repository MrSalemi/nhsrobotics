# line_follower.py
# nhs_robotics V04: PID line following for the Alvik's three line sensors.
#
# Reached through SuperBot: left_rpm, right_rpm = sb.follow_line(base_speed);
# sb.line_lost / sb.reset_line() proxy to this class. Can also be used
# standalone: lf = LineFollower(alvik); left_rpm, right_rpm = lf.follow(base_speed).
# Call follow() every loop tick (~10-20 ms). It reads the sensors itself.

import time


class LineFollower:
    # Tuning constants. KP is the workhorse; KD damps wiggle; KI stays 0
    # unless the robot consistently rides one side of the line.
    KP = 45.0
    KI = 0.0
    KD = 8.0
    LINE_MIN_SUM = 150   # below this total reflectance, the line is "lost"

    def __init__(self, alvik):
        self.alvik = alvik
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.ticks_ms()
        self._fresh = True
        self.line_lost = False

    def reset(self):
        """Clear PID state. Call after leaving the line on purpose."""
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.ticks_ms()
        self._fresh = True
        self.line_lost = False

    def _position(self):
        """Weighted line position: -1.0 (far left) .. +1.0 (far right).
        Returns None when no line is under the sensors."""
        l, c, r = self.alvik.get_line_sensors()
        if l is None or c is None or r is None:
            return None
        total = l + c + r
        if total < self.LINE_MIN_SUM:
            return None
        return (r - l) / total

    def follow(self, base_speed):
        """One PID step. Returns (left_rpm, right_rpm).
        If the line is lost, returns (base_speed, base_speed) and sets
        self.line_lost = True so caller code can react."""
        pos = self._position()
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last_time) / 1000.0
        self._last_time = now
        if dt <= 0:
            dt = 0.001

        if pos is None:
            self.line_lost = True
            return (base_speed, base_speed)
        self.line_lost = False

        error = pos
        # The first step after a reset has no last error to compare
        # with. Measuring against zero would read the whole offset as
        # a jump in 20 ms and slam one wheel backwards.
        if self._fresh:
            self._last_error = error
            self._fresh = False
        self._integral += error * dt
        # Anti-windup clamp
        if self._integral > 1.0:
            self._integral = 1.0
        elif self._integral < -1.0:
            self._integral = -1.0
        derivative = (error - self._last_error) / dt
        self._last_error = error

        correction = (self.KP * error
                      + self.KI * self._integral
                      + self.KD * derivative)

        left = base_speed + correction
        right = base_speed - correction

        # Clamp so one wheel never reverses hard at low base speeds
        limit = abs(base_speed) * 2.0
        left = max(-limit, min(limit, left))
        right = max(-limit, min(limit, right))
        return (left, right)
