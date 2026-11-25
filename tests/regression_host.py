"""Tests for nhs_lib that need no hardware. V05

Same (status, message) contract as the other regression_*.py modules, so
RegressionRunner reports them the same way:

    1 = pass, 0 = fail, 2 = skip

These run in two places. On the robot they are picked up by run_regression.py
along with everything else. On a laptop they are run by run_host_regression.py,
which is the point: a change to nhs_lib gets checked before anything is flashed.

Off the robot, the MicroPython-only modules do not exist, so they are stubbed
below. On the robot the real ones are already imported and nothing is faked.
"""

import sys


def _stub_micropython_modules():
    """Only does anything on a desktop. Returns True if stubs were installed."""
    try:
        import machine          # noqa: F401
        return False            # we are on the robot
    except ImportError:
        pass

    # Imported HERE and not at the top of the file. MicroPython has no
    # `types` module, so a top-level import kills this file on the robot --
    # where the line below is never reached anyway, because the robot took
    # the early return above.
    import types

    class _Stub(types.ModuleType):
        def __getattr__(self, name):
            return type(name, (), {"__init__": lambda self, *a, **k: None})

    for name in ("machine", "ubinascii", "ssd1306", "qwiic_buzzer",
                 "qwiic_huskylens", "qwiic_i2c", "qwiic_i2c.micropython_i2c",
                 "controller"):
        sys.modules.setdefault(name, _Stub(name))
    return True


_stub_micropython_modules()

from nhs_robotics.superbot import SuperBot          # noqa: E402
from nhs_robotics.gamepad import RobotGamepad       # noqa: E402
from nhs_robotics.peripherals import Button         # noqa: E402


# --- fakes -----------------------------------------------------------------

class FakeLed:
    def __init__(self):
        self.calls = []

    def set_color(self, r, g, b):
        self.calls.append((r, g, b))


class FakeAlvik:
    """Just enough Alvik for the parts of SuperBot that touch no I2C."""

    def __init__(self):
        self.left_led = FakeLed()
        self.right_led = FakeLed()
        self.touch = dict.fromkeys(
            ("up", "down", "left", "right", "ok", "cancel", "center"), False)

    def __getattr__(self, name):
        if name.startswith("get_touch_"):
            pad = name[len("get_touch_"):]
            return lambda: self.touch[pad]
        raise AttributeError(name)


class FakeController:
    def __init__(self):
        self.left_x = self.left_y = self.right_x = self.right_y = 0.0
        self.buttons = dict.fromkeys(RobotGamepad.BUTTON_NAMES, False)


# CPython can skip a constructor with cls.__new__(cls). MicroPython cannot
# -- user classes have no __new__ there -- so the portable way to get an
# object without running its hardware constructor is a subclass whose
# __init__ does nothing. These tests run on the laptop AND on the robot,
# so they have to use the one that works in both.
class _BareSuperBot(SuperBot):
    def __init__(self):
        pass


class _BareGamepad(RobotGamepad):
    def __init__(self):
        pass


def _bare_superbot(alvik):
    """A SuperBot without its hardware constructor. The touch pads are
    wired by the real SuperBot._wire_touch(), so these tests exercise
    the library's own wiring rather than a copy of it."""
    sb = _BareSuperBot()
    sb.alvik = alvik
    sb._wire_touch()
    return sb


def _bare_gamepad():
    """A RobotGamepad without its WiFi constructor."""
    gp = _BareGamepad()
    gp.controller = FakeController()
    gp._edges = {n: Button(gp._make_getter(n))
                 for n in RobotGamepad.BUTTON_NAMES}
    return gp


def test_missing_huskylens_is_not_an_error():
    """A robot with no HuskyLens is the normal case in this class.

    RobotVision used to end its search with log_error("No HuskyLens"), so
    every boot of every robot printed ERROR. A suite -- or a robot -- that
    reports a fault when nothing is wrong teaches everybody to skim past
    the word, and then a real one goes unread.

    The class under test is patched rather than the hardware poked, so
    this runs the same on a laptop and on a robot, and touches no I2C.
    """
    from nhs_robotics import vision

    class _NeverFinds:
        def __init__(self, **kwargs):
            pass

        def begin(self):
            return False

    class _RecordingUI:
        def __init__(self):
            self.infos = []
            self.errors = []

        def log_info(self, *args, sep=' '):
            self.infos.append(sep.join(str(a) for a in args))

        def log_error(self, *args, sep=' '):
            self.errors.append(sep.join(str(a) for a in args))

    real = vision.QwiicHuskylens
    ui = _RecordingUI()
    try:
        vision.QwiicHuskylens = _NeverFinds
        eyes = vision.RobotVision(qwiic_driver=object(), ui=ui, nav=None)
    finally:
        vision.QwiicHuskylens = real

    if ui.errors:
        return 0, "logged an error for absent hardware: %s" % ui.errors
    if eyes.husky is not None:
        return 0, "kept a HuskyLens handle that never answered"
    if not any("HuskyLens" in line for line in ui.infos):
        return 0, "said nothing at all about the missing HuskyLens"
    return 1, ""


# --- tests -----------------------------------------------------------------

def test_light_both_leds():
    """One call sets both lights to the same color."""
    alvik = FakeAlvik()
    sb = _bare_superbot(alvik)

    sb.light_both_leds(0, 1, 0)
    if alvik.left_led.calls != [(0, 1, 0)]:
        return 0, "left LED got %s" % alvik.left_led.calls
    if alvik.right_led.calls != [(0, 1, 0)]:
        return 0, "right LED got %s" % alvik.right_led.calls

    sb.light_both_leds(0, 0, 0)
    if alvik.left_led.calls[-1] != (0, 0, 0):
        return 0, "left LED did not turn off"
    if alvik.right_led.calls[-1] != (0, 0, 0):
        return 0, "right LED did not turn off"
    return 1, ""


def test_stick_deadzone():
    """A resting stick reads exactly 0.0; a real push passes through."""
    gp = _bare_gamepad()
    c = gp.controller

    for noise in (0.0, 0.01, -0.01, 0.049, -0.049):
        c.left_x = c.left_y = c.right_x = c.right_y = noise
        for axis, value in (("left_y", gp.left_y), ("right_y", gp.right_y),
                            ("left_x", gp.left_x), ("right_x", gp.right_x)):
            if value != 0.0:
                return 0, "%s reported %s for noise %s" % (axis, value, noise)

    for real in (0.06, -0.06, 0.5, -0.5, 1.0, -1.0):
        c.left_y = real
        if gp.left_y != real:
            return 0, "left_y changed %s into %s" % (real, gp.left_y)
    return 1, ""


def test_gamepad_held_and_pressed():
    """held() is true while down; pressed() fires once per press."""
    gp = _bare_gamepad()
    c = gp.controller

    if gp.held('cross') or gp.pressed('cross'):
        return 0, "a button nobody touched reported down"

    c.buttons['cross'] = True
    edges = [gp.pressed('cross') for _ in range(3)]
    if edges != [True, False, False]:
        return 0, "holding cross gave pressed() %s" % edges
    if not all(gp.held('cross') for _ in range(3)):
        return 0, "held() went false while cross was still down"

    c.buttons['cross'] = False
    gp.pressed('cross')
    c.buttons['cross'] = True
    if not gp.pressed('cross'):
        return 0, "a second press did not fire"
    return 1, ""


def test_touch_held_and_pressed():
    """Same two methods behave the same on the robot's own pads."""
    alvik = FakeAlvik()
    sb = _bare_superbot(alvik)

    if sb.held('cancel'):
        return 0, "cancel reported held before it was touched"

    alvik.touch['cancel'] = True
    if not sb.held('cancel'):
        return 0, "cancel did not report held"
    edges = [sb.pressed('cancel') for _ in range(3)]
    if edges != [True, False, False]:
        return 0, "holding cancel gave pressed() %s" % edges
    return 1, ""


def test_unknown_button_name_raises():
    """A typo fails loudly instead of quietly reporting False."""
    gp = _bare_gamepad()
    sb = _bare_superbot(FakeAlvik())

    for call, bad in ((gp.held, 'crss'), (gp.pressed, 'crss'),
                      (sb.held, 'okk'), (sb.pressed, 'okk')):
        try:
            call(bad)
        except ValueError as e:
            if bad not in str(e):
                return 0, "error did not name the bad button: %s" % e
        else:
            return 0, "%s accepted '%s'" % (call.__name__, bad)
    return 1, ""


def test_closest_valid():
    """Junk readings, silent sensors and empty tuples all behave."""
    from nhs_robotics.superbot import SuperBot, NO_READING_CM

    cases = (
        ((10, 20, -1, 5, 0), 5, "picks the smallest usable reading"),
        ((-1, 0, -5, 0, 0), NO_READING_CM, "no usable reading"),
        ((None, None, 30, None, None), 30, "ignores sensors that never reported"),
        ((None, None, None, None, None), NO_READING_CM, "every sensor silent"),
        ((None, 0, -2, 12, None), 12, "None and junk mixed together"),
        ((7,), 7, "a shorter tuple"),
        ((), NO_READING_CM, "an empty tuple"),
    )

    for readings, expected, why in cases:
        result = SuperBot.closest_valid(readings)
        if result != expected:
            return 0, "%s: expected %s from %s, got %s" % (
                why, expected, readings, result)
    return 1, ""


def test_center_pad():
    """The pad between the four arrows answers to 'center'.

    P10 starts its ping-pong run on it, so it has to behave like the
    other six: held while touched, pressed once per touch, and no other
    pad wakes it.
    """
    alvik = FakeAlvik()
    sb = _bare_superbot(alvik)

    alvik.touch['ok'] = True
    if sb.held('center'):
        return 0, "touching ok made center report held"
    alvik.touch['ok'] = False

    alvik.touch['center'] = True
    if not sb.held('center'):
        return 0, "center did not report held"
    edges = [sb.pressed('center') for _ in range(3)]
    if edges != [True, False, False]:
        return 0, "holding center gave pressed() %s" % edges
    if sb.held('ok'):
        return 0, "touching center made ok report held"
    return 1, ""


def test_line_threshold():
    """sb.LINE_THRESHOLD splits white from black on the measured numbers.

    DECISIONS #21: white reads about 50, a sensor on the line 300-650.
    The threshold has to sit clear of both, or a project comparing
    against it sees black on white paper or misses the line.
    """
    white_max = 50 * 2      # twice the white reading: scuffs and glare
    black_min = 300
    t = SuperBot.LINE_THRESHOLD
    if not white_max < t < black_min:
        return 0, "LINE_THRESHOLD %s is not between %s and %s" % (
            t, white_max, black_min)
    sb = _bare_superbot(FakeAlvik())
    if sb.LINE_THRESHOLD != t:
        return 0, "sb.LINE_THRESHOLD is not the class value"
    return 1, ""


def test_follow_line_no_kick_after_reset():
    """The first steering step after reset_line() is proportional only.

    reset() zeroes the last error. Compared against zero, a robot that
    starts beside the line reads its whole offset as a jump in one 20 ms
    tick, and the derivative term slams one wheel backwards. In the P10
    sim that spun the robot in place on the line instead of following.
    """
    from nhs_robotics import line_follower

    class _Clock:
        def __init__(self):
            self.now = 0

        def ticks_ms(self):
            return self.now

        def ticks_diff(self, later, earlier):
            return later - earlier

    class _Sensors:
        reading = (500, 200, 50)        # line under the left sensor

        def get_line_sensors(self):
            return self.reading

    real_time = line_follower.time
    clock = _Clock()
    line_follower.time = clock
    try:
        lf = line_follower.LineFollower(_Sensors())
        l, c, r = _Sensors.reading
        error = (r - l) / (l + c + r)
        for label in ("first call", "after reset"):
            clock.now += 20
            if label == "after reset":
                lf.reset()
            clock.now += 20
            left, right = lf.follow(30)
            proportional = abs(lf.KP * error)
            if abs(left - 30) > proportional + 1e-6:
                return 0, "%s: steered %.1f, P alone is %.1f" % (
                    label, abs(left - 30), proportional)
            # Moving the robot is still allowed to use the derivative.
            clock.now += 20
            lf.follow(30)
    finally:
        line_follower.time = real_time
    return 1, ""


print("Loaded regression_host.py V05")
