# Project 09: The Sumo Bot -- SOLUTION
# Version: V04
#
# Teacher copy, for the testbench only. Students never see it.
#
# WORK 1 only: PATROLLING -> TURNING -> PATROLLING, with the edge guard
# above the tree as the only thing that causes a turn. WORK 2 and WORK 3
# are two states each student designs, so there is no single answer to
# put here.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: the names of the two states, spelled once each, the same as
# P08. Misspell the name and Python stops and tells you where; misspell
# a word inside quotes and nobody tells you anything at all.
PATROLLING = "PATROLLING"
TURNING = "TURNING"

# GIVEN: patrol speed, in RPM, the same as P03. 70 is as fast as these
# motors go.
PATROL_RPM = 50

# GIVEN: how far to back off the rim before turning, the same name as
# P08. It has to be more than the robot's nose has already crept over
# the white, or it turns with a sensor still on the rim and does the
# whole thing again.
BACK_UP_CM = 10.0

# GIVEN: how far to turn after backing off the rim, in degrees. 135 is
# P08's angle, for P08's reason. Change it if you like -- it decides
# where your robot goes for the whole match.
TURN_DEG = 135

# GIVEN: the ring floor is black and the rim is white, and the line
# sensors read HIGH on black. So the rim is a reading that DROPS. If the
# robot drives over the white, this number does not match the ring.
EDGE_THRESHOLD = 200

# --- WORK 2 and WORK 3: your names and numbers ---
# Each new state gets its name here, spelled once, like the two above.
# Any number your states need goes here too.


def edge_detected():
    """True when any line sensor has reached the white rim.

    You do not use the line sensors anywhere else in this project, and
    you do not have to understand this function to finish. Read it if
    you are curious -- there is no magic in it.

    Each sensor reads None until its first packet arrives. None is not a
    reading of zero, so it is checked for here and nowhere else.

    Any one sensor is enough. Waiting for all three would mean waiting
    until the robot is most of the way off the ring.
    """
    left, center, right = alvik.get_line_sensors()
    if left is None or center is None or right is None:
        return False
    return (left < EDGE_THRESHOLD
            or center < EDGE_THRESHOLD
            or right < EDGE_THRESHOLD)


# GIVEN: the state the robot is in right now. One variable decides
# everything the robot does.
current_state = PATROLLING

# GIVEN: what the screen said last time, so it is written only when the
# state changes.
last_state = ""

try:
    # GIVEN: P04's start. The lights flash white until somebody holds
    # OK, then the match begins. Cancel gets you out before the start.
    while not sb.held('ok') and not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # GIVEN: how much room is in front of the robot this time round.
        distance = sb.get_closest_distance()

        # --- WORK 1: THE EDGE GUARD ---
        # Above the screen and above the tree, so it beats every branch.
        if edge_detected():
            current_state = TURNING

        # GIVEN: the state on the screen. It sits BELOW the guard on
        # purpose, so that a state the guard has just set gets shown.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Sumo:", current_state)

        # --- WORK 1: PATROLLING ---
        if current_state == PATROLLING:
            sb.light_both_leds(0, 1, 0)
            alvik.set_wheels_speed(PATROL_RPM, PATROL_RPM)

        # --- WORK 1: TURNING ---
        # P08's retreat, with no RUNNING after it.
        elif current_state == TURNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(-BACK_UP_CM)
            alvik.rotate(TURN_DEG)
            current_state = PATROLLING

        # --- WORK 2: your first new state ---
        # An "elif" here, at the end of the chain, under TURNING.

        # --- WORK 3: your second new state ---
        # Another "elif" under WORK 2. Then P08's catch-all "else" as
        # the very last thing in the chain.

        # GIVEN: a moment for the robot to get on with its own work.
        time.sleep_ms(50)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
