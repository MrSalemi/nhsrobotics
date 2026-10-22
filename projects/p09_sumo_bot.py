# Project 09: The Sumo Bot
# Version: V02
#
# GOAL: A robot that patrols the sumo ring, backs off when it reaches
# the white rim, and charges anything it finds in front of it.
#
# THIS IS THE TERM-ENDING PROJECT. You put together the skills from
# P01 through P08. The guide shows you each pattern the way an earlier
# project taught it, and you write the P09 version yourself. There is
# one new idea: the edge guard.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p09.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): win the tournament.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

# GIVEN: the robot and the suit.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: the names of the three states, spelled once each, the same as
# P08. Misspell the name and Python stops and tells you where; misspell
# a word inside quotes and nobody tells you anything at all.
#
# You are allowed more states than these. The three below make a robot
# that plays. They do not make a robot that wins.
PATROLLING = "PATROLLING"
ATTACKING = "ATTACKING"
TURNING = "TURNING"

# GIVEN: wheel speeds, in RPM, the same as P03. 70 is as fast as these
# motors go, so the charge is everything the robot has.
PATROL_RPM = 50
ATTACK_RPM = 70

# GIVEN: the two limits of a charge, in centimeters, with a gap between
# them the way P08 had one. Closer than ATTACK_CM: charge. Further than
# LOST_CM: it got away. 3 cm is not a round number by accident -- the
# ring floor gives the distance sensor false readings from about 5 cm
# out, so the charge is set underneath the lies.
ATTACK_CM = 3.0
LOST_CM = 5.0

# GIVEN: how far to back off the rim before turning, the same name as
# P08. It has to be more than the robot's nose has already crept over
# the white, or it turns with a sensor still on the rim and does the
# whole thing again.
BACK_UP_CM = 10.0

# --- WORK 3: YOUR TURN ANGLE ---
# Give the turn after the rim its own name here, in degrees.

# GIVEN: the ring floor is black and the rim is white, and the line
# sensors read HIGH on black. So the rim is a reading that DROPS. If the
# robot drives over the white with your guard in place, this number
# does not match the ring.
EDGE_THRESHOLD = 200


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


def waiting_for_gamepad(gamepad):
    """Hold the robot still until its driver presses CROSS.

    Building the gamepad, further down, already blinked the lights
    yellow until the controller connected. From here they blink green:
    connected, and waiting for the match to start.

    Nothing in the match reads the gamepad. It exists to start you, and
    once you are started a flat controller battery cannot cost you a
    bout.

    Cancel gets out of here too, so a robot that is connected but never
    gets its start can still be stopped.
    """
    lights_on = False
    last_blink = time.ticks_ms()
    while not gamepad.pressed('cross') and not sb.held('cancel'):
        gamepad.update()
        if time.ticks_diff(time.ticks_ms(), last_blink) > 300:
            last_blink = time.ticks_ms()
            lights_on = not lights_on
            if lights_on:
                sb.light_both_leds(0, 1, 0)
            else:
                sb.light_both_leds(0, 0, 0)
        time.sleep_ms(20)
    sb.light_both_leds(0, 0, 0)


# GIVEN: the state the robot is in right now. One variable decides
# everything the robot does.
current_state = PATROLLING

# GIVEN: what the screen said last time, so it is written only when the
# state changes.
last_state = ""

# GIVEN: the gamepad. Building it stops the robot until a controller
# connects, so it happens here, before anything else.
gamepad = RobotGamepad(alvik)

try:
    # GIVEN: nothing moves until CROSS is pressed.
    waiting_for_gamepad(gamepad)

    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # GIVEN: how much room is in front of the robot this time round.
        distance = sb.get_closest_distance()

        # --- WORK 3: THE EDGE GUARD ---
        # Two lines, and they go right here: above the screen and above
        # the tree. Use edge_detected(). The guide says why it cannot go
        # inside a branch.

        # GIVEN: the state on the screen. It sits BELOW the guard on
        # purpose, so that a state the guard has just set gets shown.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Sumo:", current_state)

        # --- WORK 1: PATROLLING, and the catch-all ---
        # P08's pattern: actions on top, the transition at the bottom.
        # Green light, both wheels at PATROL_RPM, and the test that
        # starts a charge. Put it where the "pass" is, then delete the
        # "pass" line. Write the catch-all "else" at the end of the whole
        # chain too -- you want it from your first run.
        pass

        # --- WORK 2: ATTACKING ---
        # An "elif", ABOVE the else. Steady red, both wheels at
        # ATTACK_RPM, and one way out: further than LOST_CM goes back to
        # patrolling.

        # --- WORK 3: TURNING ---
        # An "elif", ABOVE the else. P08's retreat: blue, back up, turn
        # your own angle. Then straight back to patrolling -- there is no
        # RUNNING here.

        # GIVEN: a moment for the robot to get on with its own work.
        time.sleep_ms(50)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
