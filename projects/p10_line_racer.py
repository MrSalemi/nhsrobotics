# Project 10: The Line Racer
# Version: V01
#
# GOAL: A robot that follows the line, goes around the obstacle in the
# middle, finds the line again, and races to the end.
#
# YOU DESIGN THE STATES. The file gives you the start, the speeds and
# the screen. Every state -- its name, its light, its branch and its
# way in -- is yours.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p10.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): the ping-pong racer. The guide says what it does.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: following speed, in RPM, the same as P03. 30 is safe. Race
# pace is about 40-45. Keep it at 50 or below: the motors top out at
# 70, and the steering needs room to speed one wheel up.
DRIVE_RPM = 30

# GIVEN: how close the obstacle gets before you go around it, in cm.
# Tune it. The white board can fool the sensor into seeing something
# at about 15 cm, so keep this number under that.
OBSTACLE_CM = 10

# --- WORK 1, 2 and 3: your state names and numbers ---
# HINT: one state for each thing the robot does. Following the line is
# one. Going around the obstacle is another. Finding the line again is
# a third. Name each one here, spelled once, the way P08 and P09 did.
# Any number your states need goes here too.


# HOW TO FOLLOW THE LINE: sb.follow_line() does the steering for you.
# Each pass of the loop, ask it for two wheel speeds and give them to
# the wheels:
#
# left_speed, right_speed = sb.follow_line(DRIVE_RPM)
# alvik.set_wheels_speed(left_speed, right_speed)
#
# Call this once, just before you start following -- at the start, and
# every time you find the line again. It clears what the steering
# remembers about the last line it saw:
#
# sb.reset_line()
#
# When no sensor sees the line, sb.follow_line() drives straight.

# HOW TO SEE BLACK: a line sensor reads HIGH over black and LOW over
# white. A reading above sb.LINE_THRESHOLD means that sensor sees black.


# GIVEN: the three line sensors, left to right.
def read_line_sensors():
    """The three line sensors, left, center and right.

    Each sensor reads None until its first packet arrives. None is not
    a reading, so it comes back here as 0, which counts as white.
    """
    readings = alvik.get_line_sensors()
    return [0 if reading is None else reading for reading in readings]


# --- WORK 1: your first state ---
# Set this to the state the robot starts the race in.
current_state = ""

# GIVEN: what the screen said last time, so it is written only when the
# state changes.
last_state = ""

# GIVEN: True when the run was started with Center. That is the FLEX.
ping_pong = False

try:
    # GIVEN: P09's start, with two buttons. The lights flash white until
    # somebody holds OK (the race) or Center (the FLEX). Cancel gets you
    # out before the start.
    while not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

        if sb.held('ok'):
            break
        if sb.held('center'):
            ping_pong = True
            break

    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # GIVEN: how much room is in front of the robot this time round,
        # and what the three line sensors see.
        distance = sb.get_closest_distance()
        left_line, center_line, right_line = read_line_sensors()

        # GIVEN: the state on the screen.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Racer:", current_state)

        # --- WORK 1: follow the line ---
        # Your first state. Put it where the "pass" is, then delete the
        # "pass" line.
        pass

        # --- WORK 2: go around the obstacle ---
        # An "elif" under WORK 1. Everyone goes around to the LEFT, so
        # two robots that meet head-on pass each other.

        # --- WORK 3: find the line and follow it again ---
        # Another "elif" under WORK 2. Then P08's catch-all "else" as
        # the very last thing in the chain.

        # GIVEN: a moment for the robot to get on with its own work.
        # Short, because the steering needs to look at the line often.
        time.sleep_ms(20)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
