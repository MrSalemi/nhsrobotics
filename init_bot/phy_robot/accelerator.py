# accelerator.py
# Version: V01
#
# Physics lesson 1.8 -- constant acceleration, on the floor beside a metre
# stick. Marks go at 10, 20, 30, 40 and 50 cm. Students time the robot
# past each mark and graph distance against time.
#
#   UP      starts from rest and speeds up at 0.010 m/s^2
#   DOWN    starts at 0.080 m/s and slows down at 0.005 m/s^2
#   CANCEL  quits, at any time
#
# Both runs are parabolas. UP curves up, DOWN curves down, and the two
# accelerations differ by 2x so no reading from one run can be confused
# with a reading from the other.
#
# Expected times, in seconds:
#
#       mark      10    20    30    40    50
#       UP       4.5   6.3   7.7   8.9  10.0
#       DOWN     1.3   2.7   4.3   6.2   8.5
#
# WHY THE ROBOT STEERS ITSELF TO THE NUMBER
#
# drive() delivers about 92.6% of the speed you ask for and takes 0.21 s
# to get going, so a program that just commands "a * t" and hopes is off
# by 8% plus a dead patch at the start -- worst exactly where t is small.
# Instead this program works out where it SHOULD be, reads the pose to see
# where it actually is, and corrects. The distance-versus-time curve is
# then right by construction, which is the only part students measure.
#
# WHY DOWN DOES NOT NEED A ROLLING START
#
# The DOWN profile begins at 0.080 m/s and no robot reaches that speed
# instantly, so this program was written to roll up to speed first. It
# turns out not to be needed: the base answers in about 0.2 s and the
# first mark is not reached until 1.3 s, so the correction has absorbed
# the standing start long before anything is measured. Both runs are now
# timed from the moment the robot starts moving, which is one procedure
# for students to learn instead of two.
#
# If the real robot comes in late at the DOWN 10 cm mark, set PREROLL_CM
# back to 10.0 and time that run from the 50 mark instead.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms, ticks_ms, ticks_diff

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# --- THE TWO RUNS -------------------------------------------------------
# Everything is centimetres and seconds, because that is what drive() and
# get_pose() speak. 1 cm/s^2 is 0.010 m/s^2.

RUN_UP = {
    "name": "UP",
    "v0_cms": 0.0,
    "accel_cms2": 1.0,          # +0.010 m/s^2
    "heading": 1,               # forwards
}

RUN_DOWN = {
    "name": "DOWN",
    "v0_cms": 8.0,              # 0.080 m/s
    "accel_cms2": -0.5,         # -0.005 m/s^2
    "heading": -1,              # backwards, so it returns to its start
}

MARKS_CM = (10.0, 20.0, 30.0, 40.0, 50.0)

# Brake past the last mark, so neither run comes to rest on a mark
# somebody is timing.
STOP_CM = 52.0

# How far DOWN rolls before its clock starts. Zero means no rolling start;
# see the note in the header before changing it.
PREROLL_CM = 0.0

# --- LIMITS -------------------------------------------------------------
# 70 RPM on a 34 mm wheel is 12.5 cm/s, and drive() delivers 92.6% of the
# command, so the real ceiling is somewhere between 11.5 and 12.5 cm/s.
# Nobody has measured which. Both runs stay under 10.2 cm/s so it does not
# matter, and this clamp keeps the correction term from asking for the
# impossible.
MAX_SPEED_CMS = 11.5

# Correction strength: cm/s of extra speed per cm of position error.
GAIN = 1.5

# 10 Hz. DECISIONS #20 -- re-issuing drive() every pass of a fast loop
# floods the link to the STM32.
UPDATE_MS = 100

# brake() only asks. The robot rolls for about half a second.
SETTLE_MS = 600

BLINK_MS = 250


def travelled_cm():
    """How far the robot has gone since the last reset_pose().

    Distance, not position -- DOWN drives backwards, so its pose x runs
    negative and the sign would otherwise flip the whole profile.
    """
    x, _, _ = alvik.get_pose()
    return abs(x)


def wait_for_button():
    """Blink until somebody pushes something.

    Returns a run to do, or None if they pushed Cancel. Never sleeps for
    long, so all three buttons stay responsive.
    """
    lit = False
    last = ticks_ms()

    while True:
        if sb.held('cancel'):
            return None
        if sb.pressed('up'):
            return RUN_UP
        if sb.pressed('down'):
            return RUN_DOWN

        if ticks_diff(ticks_ms(), last) >= BLINK_MS:
            last = ticks_ms()
            lit = not lit
            sb.light_both_leds(0, 0, 1) if lit else sb.light_both_leds(0, 0, 0)

        sleep_ms(20)


def roll_up_to_speed(spec):
    """Get to the profile's starting speed before the timing starts.

    Returns False if Cancel was pushed.
    """
    alvik.reset_pose(0, 0, 0)
    alvik.drive(spec["heading"] * spec["v0_cms"], 0)

    while travelled_cm() < PREROLL_CM:
        if sb.held('cancel'):
            return False
        sleep_ms(UPDATE_MS)

    return True


def do_run(spec):
    """Drive one constant-acceleration profile. Returns False on Cancel."""
    v0 = spec["v0_cms"]
    accel = spec["accel_cms2"]
    heading = spec["heading"]

    if PREROLL_CM > 0.0 and v0 > 0.0 and not roll_up_to_speed(spec):
        return False

    alvik.reset_pose(0, 0, 0)
    started = ticks_ms()
    times = []
    next_mark = 0

    while True:
        if sb.held('cancel'):
            return False

        seconds = ticks_diff(ticks_ms(), started) / 1000.0
        gone = travelled_cm()

        if gone >= STOP_CM:
            break

        # Log the marks as they go by, so a run can be checked against the
        # table in the header without anybody holding a stopwatch.
        while next_mark < len(MARKS_CM) and gone >= MARKS_CM[next_mark]:
            times.append((MARKS_CM[next_mark], seconds))
            next_mark += 1

        # Where the profile says it should be, and how fast it should be
        # going, plus a nudge for however far off it actually is.
        should_be_at = v0 * seconds + 0.5 * accel * seconds * seconds
        speed = v0 + accel * seconds + GAIN * (should_be_at - gone)

        if speed > MAX_SPEED_CMS:
            speed = MAX_SPEED_CMS
        elif speed < 0.0:
            speed = 0.0

        alvik.drive(heading * speed, 0)
        sleep_ms(UPDATE_MS)

    alvik.brake()
    sleep_ms(SETTLE_MS)

    print(spec["name"], "run:")
    for mark, seconds in times:
        print("   %4.0f cm  %5.2f s" % (mark, seconds))
    print("   stopped at %.1f cm" % travelled_cm())
    return True


try:
    print("accelerator V01 -- UP speeds up, DOWN slows down, CANCEL quits.")

    going = True
    while going:
        spec = wait_for_button()
        if spec is None:
            going = False
        else:
            sb.light_both_leds(0, 1, 0)
            going = do_run(spec)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    sb.nano_led.off()
    alvik.stop()   # GIVEN, never a WORK item.
