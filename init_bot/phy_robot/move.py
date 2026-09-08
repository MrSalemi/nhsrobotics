# move.py
# Version: V01
#
# Straight-line motion for physics, in three modes, on the floor beside a
# metre stick. Students read the robot's position off the stick at 1, 2, 3,
# 4 and 5 seconds and graph distance against time.
#
#   STOPPED       red     does not move
#   CONSTANT      green   10 cm/s
#   ACCELERATE    blue    forwards from rest, or backwards slowing down
#
# UP is forwards and DOWN is backwards, in every mode.
#
# WHAT THE THREE MODES SHOW, AND WHY THESE NUMBERS
#
#   t                     1     2     3     4     5   seconds
#   CONSTANT             10    20    30    40    50   cm
#   ACCELERATE  up        1     4     9    16    25   cm
#   ACCELERATE  down    9.5    18  25.5    32  37.5   cm
#
# Take the gap between one reading and the next, then the gap between those
# gaps. Constant gives zero. Speeding up gives +2 cm every time. Slowing
# down gives -1 cm every time. That second difference IS the acceleration,
# and it is the same story in all three modes, which is what makes three
# stations worth comparing.
#
# The forwards numbers are the perfect squares on purpose.
#
# HOW THE ROBOT KEEPS ITS PROMISE
#
# drive() delivers about 92.6% of the speed you ask for and takes 0.21 s to
# answer, so commanding "v0 + a*t" and hoping is 8% slow with a dead patch
# at the start. Instead the program works out where the profile says it
# should be, reads the pose to see where it actually is, and corrects. What
# students measure is distance against time, so that is the thing made
# right.
#
# The one place this still loses is the first reading of a run that starts
# at speed -- CONSTANT, and ACCELERATE backwards. The robot cannot be doing
# 10 cm/s at t = 0, so it spends the first moment catching up. Ray's call,
# 2026-09-04: a student eyeballing a moving robot against a metre stick is
# a bigger error than that, so no rolling start.
#
# WHAT THE LIGHTS MEAN
#
#   solid       picking a mode. Left and right change it, OK locks it in.
#   blinking    locked and waiting. Press up or down to run.
#   dark        running.
#
# The teacher picks the mode when setting up the station. Once OK is
# pressed the mode is fixed, and the only way back is to restart the robot.
# CANCEL quits at any time.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms, ticks_ms, ticks_diff

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# --- THE MODES ----------------------------------------------------------
# Centimetres and seconds throughout, because that is what drive() and
# get_pose() speak. 2.0 cm/s^2 is 0.020 m/s^2.
#
# Each mode says what to do when UP is pressed and when DOWN is pressed, as
# a starting speed and an acceleration. Direction is handled separately, so
# "down" here is the same motion as "up" unless the mode says otherwise.

STOPPED = {
    "name": "STOPPED",
    "color": (1, 0, 0),
    "up": (0.0, 0.0),
    "down": (0.0, 0.0),
}

CONSTANT = {
    "name": "CONSTANT",
    "color": (0, 1, 0),
    "up": (10.0, 0.0),          # 10 cm/s, no acceleration
    "down": (10.0, 0.0),
}

ACCELERATE = {
    "name": "ACCELERATE",
    "color": (0, 0, 1),
    "up": (0.0, 2.0),           # from rest, +0.020 m/s^2
    "down": (10.0, -1.0),       # fast, then slowing at 0.010 m/s^2
}

# Right steps forwards through this list, left steps backwards. Both wrap.
MODES = (STOPPED, CONSTANT, ACCELERATE)

# Every run is the same length, so the three modes are directly comparable.
# Students read five of these seconds; the sixth is there so the last
# reading is not taken while the robot is stopping.
RUN_SECONDS = 6.0
READINGS = (1.0, 2.0, 3.0, 4.0, 5.0)

# --- LIMITS -------------------------------------------------------------
# 70 RPM on a 34 mm wheel is 12.5 cm/s. That is what the motors can be
# ASKED for; drive() then delivers about 92.6% of it, so the robot's real
# top speed is nearer 11.5.
#
# The clamp is on the command, so 12.5 is the right number and not 11.5.
# The difference is the correction's only authority: a run that starts at
# 10 cm/s loses about 2 cm to the startup lag, and clawing that back means
# briefly asking for more than 10. Clamped at 11.5 the surplus is under
# 1 cm/s and the robot is still 1.5 cm short at two seconds. Asking for
# 12.5 is honest -- the firmware caps the wheels anyway.
MAX_SPEED_CMS = 12.5

# Correction strength: cm/s of extra speed per cm of position error.
GAIN = 1.5

# 10 Hz. DECISIONS #20 -- re-issuing drive() every pass of a fast loop
# floods the link to the STM32.
UPDATE_MS = 100

# brake() only asks. The robot rolls for about half a second.
SETTLE_MS = 600

BLINK_MS = 250


def show(color):
    sb.light_both_leds(color[0], color[1], color[2])


def travelled_cm():
    """How far the robot has gone since the last reset_pose().

    Distance, not position -- a backwards run drives the pose x negative
    and the sign would otherwise invert the whole profile.
    """
    x, _, _ = alvik.get_pose()
    return abs(x)


def pick_mode():
    """Let the teacher choose a mode. Returns the mode, or None on Cancel.

    Solid colour, because this is being read rather than answered. The
    blinking starts once a mode is locked in.
    """
    index = 0
    show(MODES[index]["color"])

    while True:
        if sb.held('cancel'):
            return None
        if sb.pressed('ok'):
            return MODES[index]

        moved = 0
        if sb.pressed('right'):
            moved = 1
        elif sb.pressed('left'):
            moved = -1

        if moved:
            index = (index + moved) % len(MODES)
            show(MODES[index]["color"])
            print("mode:", MODES[index]["name"])

        sleep_ms(20)


def wait_to_run(mode):
    """Blink the mode's colour until somebody picks a direction.

    Returns 'up', 'down', or None on Cancel.
    """
    lit = False
    last = ticks_ms()

    while True:
        if sb.held('cancel'):
            return None
        if sb.pressed('up'):
            return 'up'
        if sb.pressed('down'):
            return 'down'

        if ticks_diff(ticks_ms(), last) >= BLINK_MS:
            last = ticks_ms()
            lit = not lit
            show(mode["color"] if lit else (0, 0, 0))

        sleep_ms(20)


def do_run(mode, direction):
    """One six-second run. Returns False if Cancel was pressed.

    STOPPED needs no special case: its profile is zero speed and zero
    acceleration, so the same loop holds the robot still.
    """
    v0, accel = mode[direction]
    heading = 1 if direction == 'up' else -1

    show((0, 0, 0))                 # dark means running
    alvik.reset_pose(0, 0, 0)
    started = ticks_ms()
    readings = []
    next_reading = 0

    while True:
        if sb.held('cancel'):
            return False

        seconds = ticks_diff(ticks_ms(), started) / 1000.0
        if seconds >= RUN_SECONDS:
            break

        gone = travelled_cm()

        # Log the marks as they pass, so a run can be checked against the
        # table in the header with nobody watching the stick.
        while (next_reading < len(READINGS)
               and seconds >= READINGS[next_reading]):
            readings.append((READINGS[next_reading], gone))
            next_reading += 1

        # Where the profile says it should be, how fast it should be going,
        # and a nudge for however far off it actually is.
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

    print(mode["name"], direction, "run:")
    for seconds, distance in readings:
        print("   %3.0f s  %5.1f cm" % (seconds, distance))
    return True


try:
    print("move V01 -- left/right pick a mode, OK locks it, up/down runs.")

    mode = pick_mode()
    going = mode is not None
    if going:
        print("locked:", mode["name"])

    while going:
        direction = wait_to_run(mode)
        if direction is None:
            going = False
        else:
            going = do_run(mode, direction)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    sb.nano_led.off()
    alvik.stop()   # GIVEN, never a WORK item.
