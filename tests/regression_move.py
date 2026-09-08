# tests/regression_move.py -- the physics motion program. V01
#
# Runs init_bot/phy_robot/move.py, unmodified, inside the testbench. No
# robot: the fakes stand in for the hardware and the program's own sleep
# drives a simulated clock, so a whole run finishes in milliseconds.
#
# Every test returns (status, message): 1 pass, 0 fail, 2 skip.
#
# The claim under test is one sentence: on each of the first six seconds
# the robot is where the mode says it should be. That is what a student reads
# off the metre stick, so it is the only thing worth asserting.
#
# Expectations are computed from the profile, never from the program's own
# arithmetic (DECISIONS #22). Sharing a formula with the code under test
# only proves Python can still multiply.

import os
import tempfile

from tb.env import Environment, REPO
from tb.plant import Plant, DEFAULT_DEFECTS

DUT = os.path.join(REPO, "init_bot", "phy_robot", "move.py")

READINGS = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)

# The three modes as the header table states them, in centimetres. Keyed
# the way a run is chosen: mode name, then which arrow.
PROFILES = {
    ("STOPPED", "up"): (0.0, 0.0),
    ("STOPPED", "down"): (0.0, 0.0),
    ("CONSTANT", "up"): (10.0, 0.0),
    ("CONSTANT", "down"): (10.0, 0.0),
    ("ACCELERATE", "up"): (0.0, 1.5),
    ("ACCELERATE", "down"): (10.0, -1.0),
}

# How many left/right presses from startup to reach each mode. Startup is
# STOPPED, and right steps forwards.
STEPS_TO = {"STOPPED": 0, "CONSTANT": 1, "ACCELERATE": 2}

# A run that starts from rest tracks the profile closely. One that starts
# at speed cannot -- the robot is not doing 10 cm/s at t=0 and spends the
# first moment catching up. Ray's call on 2026-09-04: no rolling start,
# because a student eyeballing a moving robot is the larger error. So the
# tolerance is per-reading and loosest at t=1, which is exactly where the
# lag lands.
TOLERANCE_CM = 1.0
FIRST_READING_TOLERANCE_CM = 3.0

WATCHDOG_MS = 40000


def _expected_cm(profile, seconds):
    """Where the profile puts the robot. Distance travelled, not position."""
    v0, accel = profile
    return v0 * seconds + 0.5 * accel * seconds * seconds


class SamplingPlant(Plant):
    """A plant that remembers where it was, and when.

    The monitor records what the program did. Nothing records where the
    robot actually ended up, so this does.
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

    def runs(self):
        """One distance-against-time trace per run the program started.

        A run begins at a reset_pose() and ends at the next one, or at the
        end of the session.
        """
        out = []
        starts = self.clock_restarts
        for index, (start_ms, start_cm) in enumerate(starts):
            end_ms = (starts[index + 1][0] if index + 1 < len(starts)
                      else float("inf"))
            out.append([((ms - start_ms) / 1000.0, cm - start_cm)
                        for ms, cm in self.trace
                        if start_ms <= ms < end_ms])
        return out

    def distance_at(self, run, seconds):
        """Distance travelled at a moment inside one run."""
        found = 0.0
        for stamp, distance in run:
            if stamp > seconds:
                break
            found = distance
        return found


class Script:
    """Presses buttons on a timetable.

    Every entry is (name, at_ms). A press is held for 200 ms, which is
    long enough for a 20 ms poll to see the rising edge and short enough
    not to look like a hold.
    """

    HOLD_MS = 200

    def __init__(self, presses, cancel_at_ms=None):
        self.presses = presses
        self.cancel_at_ms = cancel_at_ms

    def touch(self, name, env):
        now = env.clock.now_ms
        if name == "cancel":
            return (self.cancel_at_ms is not None
                    and now >= self.cancel_at_ms)
        for pressed, at_ms in self.presses:
            if pressed == name and at_ms <= now < at_ms + self.HOLD_MS:
                return True
        return False


def _have_dut():
    return os.path.exists(DUT)


def _select(mode_name, then, cancel_at_ms, first_press_ms=300):
    """Build a press list: walk to a mode, press OK, then run.

    `then` is a list of (arrow, at_ms) for the runs themselves.
    """
    presses = []
    when = first_press_ms
    for _ in range(STEPS_TO[mode_name]):
        presses.append(("right", when))
        when += 300
    presses.append(("ok", when))
    return presses + then, cancel_at_ms


def _run(presses, cancel_at_ms, defects=None):
    plant = SamplingPlant(defects=defects)
    env = Environment(plant=plant,
                      stimulus=Script(presses, cancel_at_ms),
                      watchdog_ms=WATCHDOG_MS)
    env.run(DUT)
    return env, plant


def _drive_one(mode_name, arrow, defects=None, run_at_ms=2000):
    """Select a mode, do one run with one arrow, then quit."""
    presses, cancel = _select(mode_name, [(arrow, run_at_ms)],
                              run_at_ms + 12000)
    return _run(presses, cancel, defects=defects)


def _check_readings(plant, mode_name, arrow, run_index=0):
    profile = PROFILES[(mode_name, arrow)]
    runs = plant.runs()
    if len(runs) <= run_index:
        return 0, "the program never started run %d" % (run_index + 1)
    run = runs[run_index]
    if not run:
        return 0, "run %d has no trace" % (run_index + 1)

    for seconds in READINGS:
        want = _expected_cm(profile, seconds)
        got = plant.distance_at(run, seconds)
        allowed = (FIRST_READING_TOLERANCE_CM if seconds == READINGS[0]
                   else TOLERANCE_CM)
        if abs(got - want) > allowed:
            return 0, ("%s %s at %.0f s: %.1f cm, profile says %.1f "
                       "(off by %.1f, allowed %.1f)"
                       % (mode_name, arrow, seconds, got, want,
                          abs(got - want), allowed))
    return 1, ""


# --------------------------------------------------------------------------
# The three modes
# --------------------------------------------------------------------------

def test_constant_holds_its_speed():
    """10 cm/s puts the robot on 10, 20, 30, 40, 50, 60 cm."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("CONSTANT", "up")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_readings(plant, "CONSTANT", "up")


def test_accelerate_forwards_matches_the_profile():
    """+1.5 cm/s^2 from rest gives 0.75, 3, 6.75, 12, 18.75, 27 cm."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("ACCELERATE", "up")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_readings(plant, "ACCELERATE", "up")


def test_accelerate_backwards_slows_down():
    """10 cm/s decaying at 1 cm/s^2 gives 9.5 ... 42 cm."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("ACCELERATE", "down")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_readings(plant, "ACCELERATE", "down")


def test_stopped_does_not_move():
    """Red mode goes dark for six seconds and stays put."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("STOPPED", "up")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if plant.distance_travelled_cm > 0.5:
        return 0, ("moved %.1f cm in stopped mode"
                   % plant.distance_travelled_cm)
    if not plant.clock_restarts:
        return 0, "pressing up in stopped mode did nothing at all"
    return 1, ""


def test_down_is_backwards_in_every_mode():
    """UP and DOWN are direction, not two different experiments.

    Constant mode must cover the same ground either way, in opposite
    directions -- so a station can send the robot back to its start.
    """
    if not _have_dut():
        return 2, "move.py not present"
    results = {}
    for arrow in ("up", "down"):
        env, plant = _drive_one("CONSTANT", arrow)
        if not env.result.ok:
            return 0, "%s raised: %r" % (arrow, env.result.error)
        runs = plant.runs()
        if not runs:
            return 0, "no run for %s" % arrow
        results[arrow] = (plant.x, plant.distance_at(runs[0], 5.0))

    forward_x, forward_cm = results["up"]
    back_x, back_cm = results["down"]
    if forward_x <= 0:
        return 0, "up did not move the robot forwards (x %.1f)" % forward_x
    if back_x >= 0:
        return 0, "down did not move the robot backwards (x %.1f)" % back_x
    if abs(forward_cm - back_cm) > TOLERANCE_CM:
        return 0, ("up covered %.1f cm and down %.1f cm; constant mode "
                   "should be the same run either way" % (forward_cm, back_cm))
    return 1, ""


# --------------------------------------------------------------------------
# Mode selection
# --------------------------------------------------------------------------

def test_right_steps_forwards_through_the_modes():
    """One press of right is CONSTANT, two is ACCELERATE."""
    if not _have_dut():
        return 2, "move.py not present"
    for mode_name in ("STOPPED", "CONSTANT", "ACCELERATE"):
        env, plant = _drive_one(mode_name, "up")
        if not env.result.ok:
            return 0, "%s raised: %r" % (mode_name, env.result.error)
        status, message = _check_readings(plant, mode_name, "up")
        if status == 0:
            return 0, "walking to %s: %s" % (mode_name, message)
    return 1, ""


def test_left_steps_backwards_and_wraps():
    """One press of left from startup must reach ACCELERATE.

    RED <- GREEN <- BLUE <- RED, so going left once off the first mode
    wraps to the last. A cycle that only runs one way passes every other
    check here.
    """
    if not _have_dut():
        return 2, "move.py not present"
    presses = [("left", 300), ("ok", 600), ("up", 2000)]
    env, plant = _run(presses, 14000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_readings(plant, "ACCELERATE", "up")


def test_the_arrows_do_nothing_before_ok():
    """Up and down are dead while a mode is still being picked."""
    if not _have_dut():
        return 2, "move.py not present"
    presses = [("up", 300), ("down", 700), ("right", 1100), ("ok", 1500),
               ("up", 3000)]
    env, plant = _run(presses, 15000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    runs = plant.runs()
    if len(runs) != 1:
        return 0, ("%d runs happened; the two presses before OK should have "
                   "been ignored" % len(runs))
    return _check_readings(plant, "CONSTANT", "up")


def test_the_mode_cannot_change_after_ok():
    """Left and right are dead once a mode is locked in.

    The only way back to selection is a restart, so a stray press at the
    station must not quietly turn a constant run into an accelerating one.
    """
    if not _have_dut():
        return 2, "move.py not present"
    presses = [("right", 300), ("ok", 600),
               ("right", 1000), ("right", 1400), ("left", 1800),
               ("up", 2500)]
    env, plant = _run(presses, 15000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    return _check_readings(plant, "CONSTANT", "up")


# --------------------------------------------------------------------------
# Lights, timing and quitting
# --------------------------------------------------------------------------

def _led_state_at(env, when_ms):
    """What the lights were showing at a moment.

    A level, not an edge. Asking "was any dark event recorded during the
    run" passes trivially when the program simply stopped touching the
    LEDs, which is the bug this has to catch.
    """
    color = None
    for stamp, kind, args in env.monitor.transactions:
        if kind == "led" and stamp <= when_ms:
            color = args[1]
    return color


def test_the_lights_say_which_state_it_is_in():
    """Solid while picking, blinking while armed, dark while running.

    Three states a teacher reads across the room, so each has to look
    different from the other two. Timings match _drive_one: right at
    300 ms, OK at 600, up at 2000, and the run lasts six seconds.
    """
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("CONSTANT", "up")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)

    leds = [(stamp, args[1]) for stamp, kind, args
            in env.monitor.transactions if kind == "led"]
    if not leds:
        return 0, "the lights never came on at all"

    # Picking: from the first light until OK, never dark.
    picking = [color for stamp, color in leds if leds[0][0] <= stamp < 600]
    if any(color == (0, 0, 0) for color in picking):
        return 0, "the lights blinked while a mode was being picked"
    if _led_state_at(env, 599) != (0, 1, 0):
        return 0, ("green was not showing when OK was pressed; saw %s"
                   % (_led_state_at(env, 599),))

    # Armed: it has to go both on and off, or it is not blinking.
    armed = [color for stamp, color in leds if 650 <= stamp < 2000]
    if not any(color == (0, 1, 0) for color in armed):
        return 0, "never showed green while armed"
    if not any(color == (0, 0, 0) for color in armed):
        return 0, "green never blinked while armed; it stayed solid"

    # Running: dark, sampled as a level at three moments inside the run.
    for probe in (3000, 4500, 6000):
        state = _led_state_at(env, probe)
        if state != (0, 0, 0):
            return 0, ("lights were %s at %d ms, part way through a run"
                       % (state, probe))
    return 1, ""


def test_a_run_lasts_six_and_a_half_seconds():
    """All three modes run 6.5 s, so they compare and nothing is read
    while the robot is braking."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _drive_one("CONSTANT", "up")
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    runs = plant.runs()
    if not runs:
        return 0, "no run happened"
    # The trace ends when the next run starts or the session does, so
    # measure to the brake instead.
    brakes = env.monitor.of("brake")
    if not brakes:
        return 0, "never braked"

    start_ms = plant.clock_restarts[0][0]
    length_s = (brakes[0][0] - start_ms) / 1000.0
    if abs(length_s - 6.5) > 0.3:
        return 0, "the run lasted %.2f s, not 6.5" % length_s
    return 1, ""


def test_it_goes_back_to_waiting_after_a_run():
    """A finished run returns to the blink, and a second run works."""
    if not _have_dut():
        return 2, "move.py not present"
    presses, cancel = _select("CONSTANT",
                              [("up", 2000), ("down", 10000)], 20000)
    env, plant = _run(presses, cancel)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    runs = plant.runs()
    if len(runs) < 2:
        return 0, ("only %d run(s); it never returned to waiting"
                   % len(runs))
    return _check_readings(plant, "CONSTANT", "down", run_index=1)


def test_an_arrow_during_a_run_is_ignored():
    """Pressing up mid-run must not restart or stack a second run."""
    if not _have_dut():
        return 2, "move.py not present"
    presses, cancel = _select("CONSTANT",
                              [("up", 2000), ("up", 4000), ("down", 5000)],
                              16000)
    env, plant = _run(presses, cancel)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    runs = plant.runs()
    if len(runs) != 1:
        return 0, ("%d runs happened; presses during a run should be "
                   "ignored" % len(runs))
    return _check_readings(plant, "CONSTANT", "up")


def test_cancel_quits_from_selection():
    """Cancel before anything is chosen ends the program cleanly."""
    if not _have_dut():
        return 2, "move.py not present"
    env, plant = _run([], 500)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if env.result.watchdog:
        return 0, "Cancel did not end the program"
    if not env.monitor.saw("stop"):
        return 0, "the finally block never called alvik.stop()"
    if plant.distance_travelled_cm > 0.5:
        return 0, "the robot moved before a mode was even chosen"
    return 1, ""


def test_cancel_quits_during_a_run():
    """Cancel works mid-run, not only while waiting."""
    if not _have_dut():
        return 2, "move.py not present"
    presses, _ = _select("CONSTANT", [("up", 2000)], None)
    env, plant = _run(presses, 4000)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    if env.result.watchdog:
        return 0, "Cancel mid-run did not end the program"
    if not env.monitor.saw("stop"):
        return 0, "the finally block never called alvik.stop()"
    runs = plant.runs()
    if runs and plant.distance_at(runs[0], 5.0) > 35.0:
        return 0, "the run finished anyway; Cancel was ignored"
    return 1, ""


def test_the_lights_go_out_at_the_end():
    """Nothing is left lit after the finally block."""
    if not _have_dut():
        return 2, "move.py not present"
    env, _ = _run([], 500)
    if not env.result.ok:
        return 0, "DUT raised: %r" % (env.result.error,)
    last = {}
    for _stamp, kind, args in env.monitor.transactions:
        if kind == "led":
            last[args[0]] = args[1]
    still_on = [name for name, color in last.items() if any(color)]
    if still_on:
        return 0, "left on: %s" % still_on
    nano = env.monitor.of("nano_led")
    if nano and any(nano[-1][2][0]):
        return 0, "Nano LED left on"
    return 1, ""


# --------------------------------------------------------------------------
# The hardware it has to survive
# --------------------------------------------------------------------------

def test_immune_to_the_drive_speed_error():
    """The 8% drive() error must not reach the numbers.

    Same readings, run with the defect and without it. A program that
    commands speed open-loop passes one and fails the other.
    """
    if not _have_dut():
        return 2, "move.py not present"
    for scale in (0.90, 1.00):
        defects = dict(DEFAULT_DEFECTS)
        defects["drive_scale"] = scale
        env, plant = _drive_one("CONSTANT", "up", defects=defects)
        if not env.result.ok:
            return 0, "raised at scale %.2f: %r" % (scale, env.result.error)
        status, message = _check_readings(plant, "CONSTANT", "up")
        if status == 0:
            return 0, "drive_scale %.2f: %s" % (scale, message)
    return 1, ""


def test_the_readings_check_has_teeth():
    """Cap the robot's speed and the readings check must fail.

    Without this, every check above would also pass on a robot that
    quietly stops accelerating -- the failure the real floor produces and
    the simulation cannot see.
    """
    if not _have_dut():
        return 2, "move.py not present"
    defects = dict(DEFAULT_DEFECTS)
    defects["max_speed_cms"] = 4.0
    env, plant = _drive_one("CONSTANT", "up", defects=defects)
    status, _ = _check_readings(plant, "CONSTANT", "up")
    if status == 1:
        return 0, ("a robot capped at 4 cm/s still passed the readings "
                   "check, so the check proves nothing")
    return 1, ""


def test_it_never_asks_for_more_than_the_robot_has():
    """The correction must not command past the motors' limit."""
    if not _have_dut():
        return 2, "move.py not present"
    worst = 0.0
    for mode_name, arrow in (("CONSTANT", "up"), ("ACCELERATE", "up"),
                             ("ACCELERATE", "down")):
        env, _ = _drive_one(mode_name, arrow)
        if not env.result.ok:
            return 0, "%s %s raised: %r" % (mode_name, arrow,
                                            env.result.error)
        for _stamp, kind, args in env.monitor.transactions:
            if kind == "drive":
                worst = max(worst, abs(args[0]))
    if worst > 12.5:
        return 0, "asked for %.1f cm/s; the robot tops out near 12.5" % worst
    return 1, ""


def test_drive_is_not_re_issued_every_pass():
    """DECISIONS #20 -- flooding the link stops the robot listening."""
    if not _have_dut():
        return 2, "move.py not present"
    env, _ = _drive_one("ACCELERATE", "up")
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
