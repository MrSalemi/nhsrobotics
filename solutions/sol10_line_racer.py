# Project 10: The Line Racer -- SOLUTION
# Version: V01
#
# Teacher copy. Students never see it.
#
# One answer of many: students design their own states. This one has
# FOLLOWING, DODGING, SEARCHING and ALIGNING for WORK 1-3, and
# BACKING_UP plus TURNING_AROUND for the FLEX (ping-pong between the two
# black end regions). The dodge is the gentle shape from the guide: 45
# left, drive, 90 right, then cross the line at 45 degrees. ALIGNING
# turns the robot to lie along the line before following starts, so the
# sensors never sit across the line where all three read black.

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

# --- WORK 1, 2 and 3: state names and numbers ---
FOLLOWING = "FOLLOWING"
DODGING = "DODGING"
SEARCHING = "SEARCHING"
ALIGNING = "ALIGNING"

DODGE_OUT_DEG = 45      # turn left, away from the line
DODGE_CM = 25           # drive past the obstacle
DODGE_BACK_DEG = -90    # turn right, back toward the line
SEARCH_RPM = 25         # straight ahead until a sensor sees black
SENSOR_AHEAD_CM = 5     # line sensors sit this far ahead of the wheels
# Undo the dodge's net turn, so the robot points along the line again.
ALIGN_DEG = -(DODGE_OUT_DEG + DODGE_BACK_DEG)

# --- FLEX: state names and numbers ---
BACKING_UP = "BACKING_UP"
TURNING_AROUND = "TURNING_AROUND"


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


# --- WORK 1: the first state ---
current_state = FOLLOWING

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

    # WORK 1: clear the steering before the first line.
    sb.reset_line()

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
        if current_state == FOLLOWING:
            sb.light_both_leds(0, 1, 0)
            left_speed, right_speed = sb.follow_line(DRIVE_RPM)
            alvik.set_wheels_speed(left_speed, right_speed)

            if distance < OBSTACLE_CM:
                current_state = DODGING
            # FLEX: all three on black is an end region.
            elif ping_pong and min(left_line, center_line,
                                   right_line) > sb.LINE_THRESHOLD:
                current_state = BACKING_UP

        # --- WORK 2: go around the obstacle, to the LEFT ---
        # Blocking is fine: nothing needs watching on the way round.
        elif current_state == DODGING:
            sb.light_both_leds(0, 0, 1)
            alvik.brake()
            alvik.rotate(DODGE_OUT_DEG)
            alvik.move(DODGE_CM)
            alvik.rotate(DODGE_BACK_DEG)
            current_state = SEARCHING

        # --- WORK 3: find the line and follow it again ---
        elif current_state == SEARCHING:
            sb.light_both_leds(1, 1, 0)
            alvik.set_wheels_speed(SEARCH_RPM, SEARCH_RPM)

            if max(left_line, center_line,
                   right_line) > sb.LINE_THRESHOLD:
                current_state = ALIGNING

        # --- WORK 3 (continued): turn to lie along the line ---
        # The sensors found the line; the wheels are still short of it.
        # Roll up onto it and turn back the way we were racing. The line
        # ends up somewhere under the sensors, and follow_line does the
        # rest. Blocking is fine: nothing needs watching.
        elif current_state == ALIGNING:
            sb.light_both_leds(0, 1, 1)
            alvik.brake()
            alvik.move(SENSOR_AHEAD_CM)
            alvik.rotate(ALIGN_DEG)
            sb.reset_line()
            current_state = FOLLOWING

        # --- FLEX: back off the black, or the spin lands on it again ---
        elif current_state == BACKING_UP:
            sb.light_both_leds(1, 0, 1)
            alvik.set_wheels_speed(-SEARCH_RPM, -SEARCH_RPM)

            if min(left_line, center_line,
                   right_line) < sb.LINE_THRESHOLD:
                current_state = TURNING_AROUND

        # --- FLEX: spin 180 and race back ---
        elif current_state == TURNING_AROUND:
            sb.light_both_leds(1, 0, 1)
            alvik.brake()
            alvik.rotate(180)
            sb.reset_line()
            current_state = FOLLOWING

        else:
            sb.light_both_leds(1, 0, 0)
            sb.log_info("Bad:", current_state)
            time.sleep_ms(3000)
            break

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
