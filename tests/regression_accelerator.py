# tests/regression_accelerator.py -- the physics accelerator. V01
#
# Runs init_bot/phy_robot/accelerator.py, unmodified, inside the testbench.
# Every test returns (status, message): 1 pass, 0 fail, 2 skip.
#
# What is actually being checked is one claim: the distance the robot has
# travelled at time t matches the constant-acceleration profile the guide
# prints. That is the only thing a student measures, so it is the only
# thing worth asserting.
#
# Expectations come from the profile, never from the program's arithmetic
# (DECISIONS #22). If the program and the check ever share a formula, the
# check is only testing that Python still multiplies.

import math
import os

from tb.env import Environment, REPO
from tb.plant import Plant, DEFAULT_DEFECTS

DUT = os.path.join(REPO, "init_bot", "phy_robot", "accelerator.py")

MARKS_CM = (10.0, 20.0, 30.0, 40.0, 50.0)

# The two runs, as the guide states them. Metres in the guide, centimetres
# here, because that is what the robot's API speaks.
UP = {"v0": 0.0, "accel": 1.0}
DOWN = {"v0": 8.0, "accel": -0.5}

# The robot is corrected at 10 Hz and takes 0.21 s to answer a command, so
# it cannot sit exactly on the curve. It measures 0.09 s late at worst,
# which is inside the 0.1 s a student can read off a stopwatch. The limit
# is set just above that: loose enough to survive tuning, tight enough
# that losing the correction fails the check.
TOLERANCE_S = 0.15

WATCHDOG_MS = 40000


def _expected_time(spec, distance_cm):
    """When the profile says the robot passes a mark.

    Solves distance = v0*t + a*t^2/2 for the first positive t.
    """
    v0, accel = spec["v0"], spec["accel"]
    if accel == 0.0:
        return distance_cm / v0
    disc = v0 * v0 + 2.0 * accel * distance_cm
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    for t in sorted(((-v0 + root) / accel, (-v0 - root) / accel)):
        if t > 0.0:
            return t
    return None


class SamplingPlant(Plant):
    """A plant that remembers where it was, and when.

    The monitor records what the DUT did; nothing records where the robot
    ended up. This does, without the DUT knowing.
    """

    def __init__(self, *args, **kwargs):
        self.trace = []
        self.clock_restarts = []
        super().__init__(*args, **kwargs)

    def step(self, dt_ms):
        super().step(dt_ms)
        self.trace.append((self.elapsed_ms, self.distance_travelled_cm))

    def reset_pose(self, x, y, theta):
        super().reset_pose(x, y, theta)
        self.clock_restarts.append(
            (self.elapsed_ms, self.distance_travelled_cm))

    def timed_window(self):
        """Distance against time for the run that is actually timed.

        The DUT zeroes the pose once for a rolling start and again when the
        stopwatch starts, so the last reset is the one that counts.
        """
        if not self.clock_restarts:
            return []
        start_ms, start_cm = self.clock_restarts[-1]
        return [((ms - start_ms) / 1000.0, cm - start_cm)
                for ms, cm in self.trace if ms >= start_ms]

    def distance_at_ms(self, when_ms):
        """Total distance travelled as of a sim timestamp."""
        travelled = 0.0
        for ms, cm in self.trace:
            if ms > when_ms:
                break
            travelled = cm
        return travelled

    def crossings(self, marks=MARKS_CM):
        """The time each mark was first reached, in the timed window."""
        window = self.timed_window()
        found = {}
        for mark in marks:
            for seconds, distance in window:
                if distance >= mark:
                    found[mark] = seconds
                    break
        return found


class ButtonScript:
    """Push one button at the start, then Cancel at a set time."""

    def __init__(self, first=None, cancel_at_ms=None, press_ms=200):
        self.first = first
        self.cancel_at_ms = cancel_at_ms
        self.press_ms = press_ms

    def touch(self, name, env):
        now = env.clock.now_ms
        if name == "cancel":
            return (self.cancel_at_ms is not None
                    and now >= self.cancel_at_ms)
        if self.first and name == self.first:
            return now < self.press_ms
        return False


def _have_dut():
    return os.path.exists(DUT)


def _run(button, cancel_at_ms, defects=None):
    plant = SamplingPlant(defects=defects)
    env = Environment(plant=plant,
                      stimulus=ButtonScript(button, cancel_at_ms),
                      watchdog_ms=WATCHDOG_MS)
    env.run(DUT)
    return env, plant


def _check_profile(plant, spec, tolerance_s=TOLERANCE_S):
    crossings = plant.crossings()
    missing = [m for m in MARKS_CM if m not in crossings]
    if missing:
        return 0, "never reached %s cm" % missing

    worst_mark, worst_error = None, 0.0
    for mark in MARKS_CM:
        want = _expected_time(spec, mark)
        got = crossings[mark]
        error = abs(got - want)
        if error > worst_error:
            worst_mark, worst_error = mark, error

    if worst_error > tolerance_s:
        want = _expected_time(spec, worst_mark)
        return 0, ("%.0f cm reached at %.2f s, profile says %.2f s "
                   "(off by %.2f s, allowed %.2f)"
                   % (worst_mark, crossings[worst_mark], want,
                      worst_error, tolerance_s))
    return 1, ""


# --------------------------------------------------------------------------
# The profiles
# --------------------------------------------------------------------------

def test_up_matches_the_profile():
    """Speeding up: distance is a*t^2/2 at all five marks."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, plant = _run("up", 16000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_profile(plant, UP)


def test_down_matches_the_profile():
    """Slowing down: distance is v0*t - a*t^2/2 at all five marks."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, plant = _run("down", 16000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_profile(plant, DOWN)


def test_up_immune_to_the_speed_error():
    """The 8% drive() error must not reach the numbers.

    Same check, run with the defect and again without it. A program that
    commands speed open-loop passes one and fails the other.
    """
    if not _have_dut():
        return 2, "accelerator.py not present"
    results = []
    for scale in (0.90, 1.00):
        defects = dict(DEFAULT_DEFECTS)
        defects["drive_scale"] = scale
        env, plant = _run("up", 16000, defects=defects)
        if not env.result.ok:
            return 0, "DUT raised at scale %.2f: %r" % (scale,
                                                        env.result.error)
        status, message = _check_profile(plant, UP)
        if status == 0:
            return 0, "drive_scale %.2f: %s" % (scale, message)
        results.append(scale)
    return 1, ""


def test_the_profile_check_has_teeth():
    """Break the robot's top speed and the profile check must fail.

    Without this, every check above would also pass on a robot that
    quietly stops accelerating -- which is exactly the failure the real
    floor produces and the sim cannot see.
    """
    if not _have_dut():
        return 2, "accelerator.py not present"
    defects = dict(DEFAULT_DEFECTS)
    defects["max_speed_cms"] = 4.0        # saturates before the 20 cm mark
    env, plant = _run("up", 30000, defects=defects)
    status, _ = _check_profile(plant, UP)
    if status == 1:
        return 0, ("a robot capped at 4 cm/s still passed the profile "
                   "check, so the check proves nothing")
    return 1, ""


# --------------------------------------------------------------------------
# Behaviour around the runs
# --------------------------------------------------------------------------

def test_neither_run_brakes_on_a_mark():
    """The profile has to still be running when the last mark goes by.

    Braking AT the 50 mark corrupts the reading a student is taking at
    that moment, so the brake must come afterwards with room to spare.
    """
    if not _have_dut():
        return 2, "accelerator.py not present"
    for button in ("up", "down"):
        env, plant = _run(button, 16000)
        if not env.result.ok:
            return 0, "%s raised: %r" % (button, env.result.error)
        brakes = env.monitor.of("brake")
        if not brakes:
            return 0, "%s never braked" % button
        start_cm = plant.clock_restarts[-1][1]
        at_brake = plant.distance_at_ms(brakes[0][0]) - start_cm
        if at_brake < MARKS_CM[-1] + 1.0:
            return 0, ("%s braked at %.1f cm, too close to the %.0f cm mark"
                       % (button, at_brake, MARKS_CM[-1]))
    return 1, ""


def test_the_robot_is_stopped_between_runs():
    """A finished run must leave the robot still, not rolling.

    drive() sets a speed that stays set, so a run that returns to the
    blink loop without braking leaves the robot walking off the desk
    while the lights cheerfully blink.
    """
    if not _have_dut():
        return 2, "accelerator.py not present"
    cancel_at = 16000
    env, plant = _run("up", cancel_at)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if env.result.watchdog:
        return 0, "watchdog had to force it; it never returned to waiting"
    crept = (plant.distance_at_ms(cancel_at)
             - plant.distance_at_ms(cancel_at - 1000))
    if crept > 0.2:
        return 0, ("robot moved %.1f cm in the last second of blinking; "
                   "the run never stopped it" % crept)
    return 1, ""


def test_cancel_while_blinking_quits():
    """Cancel with no run in progress exits through the finally block."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, plant = _run(None, 500)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if env.result.watchdog:
        return 0, "Cancel did not end the program"
    if not env.monitor.saw("stop"):
        return 0, "finally block never called alvik.stop()"
    if plant.distance_travelled_cm > 0.5:
        return 0, ("robot moved %.1f cm while only blinking"
                   % plant.distance_travelled_cm)
    return 1, ""


def test_cancel_during_a_run_quits():
    """Cancel must work mid-run, not only while blinking."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, plant = _run("up", 4000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if env.result.watchdog:
        return 0, "Cancel mid-run did not end the program"
    if not env.monitor.saw("stop"):
        return 0, "finally block never called alvik.stop()"
    window = plant.timed_window()
    if window and window[-1][1] >= MARKS_CM[-1]:
        return 0, "the run finished anyway; Cancel was ignored"
    return 1, ""


def test_lights_go_out_at_the_end():
    """Both LEDs and the Nano LED are off after the finally block."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, _ = _run(None, 500)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    leds = env.monitor.of("led")
    if not leds:
        return 0, "the lights never blinked, so nobody knows to push"
    last = {}
    for _, _kind, args in env.monitor.transactions:
        if _kind == "led":
            last[args[0]] = args[1]
    still_on = [name for name, color in last.items() if any(color)]
    if still_on:
        return 0, "left on: %s" % still_on
    nano = env.monitor.of("nano_led")
    if nano and any(nano[-1][2][0]):
        return 0, "Nano LED left on"
    return 1, ""


def test_drive_is_not_re_issued_every_pass():
    """DECISIONS #20 -- flooding the link stops the robot listening.

    A ramp has to re-issue drive(), so the guard is the rate, not the
    fact. 10 Hz commanded, so anything past 15 Hz means the update
    interval has been lost.
    """
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, plant = _run("up", 16000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    drives = env.monitor.of("drive")
    if not drives:
        return 0, "never drove"
    span_s = (drives[-1][0] - drives[0][0]) / 1000.0
    if span_s <= 0:
        return 0, "every drive() landed on the same timestamp"
    rate = len(drives) / span_s
    if rate > 15.0:
        return 0, "drive() called %.1f times a second" % rate
    return 1, ""


def test_it_never_asks_for_more_than_the_robot_has():
    """The correction term must not command past the motors' limit."""
    if not _have_dut():
        return 2, "accelerator.py not present"
    env, _ = _run("up", 16000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    worst = 0.0
    for _, _kind, args in env.monitor.transactions:
        if _kind == "drive":
            worst = max(worst, abs(args[0]))
    if worst > 12.5:
        return 0, "asked for %.1f cm/s; the robot tops out near 12.5" % worst
    return 1, ""
