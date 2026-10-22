# Project 09: The Sumo Bot -- SOLUTION
# Version: V02
#
# Teacher copy. Three states, one elif tree, and one test that lives
# outside the tree.
#
#   PATROLLING  green, patrol speed, hunting                    WORK 1
#   ATTACKING   red, full speed into whatever is in front       WORK 2
#   TURNING     blue, back off the rim and turn away            WORK 3
#
# THE TERM-ENDING PROJECT. The guide prints no P09 code. Each WORK shows
# a pattern the way an earlier project taught it -- P08's branch shape,
# catch-all, two-limit gap and retreat; P03's set_wheels_speed() -- and
# the student writes the P09 version.
#
# WHAT IS NEW HERE, AND IT IS ONLY ONE THING.
#
# Every transition the class has ever written lived inside a branch, and
# so took effect on the NEXT pass of the loop. The edge test cannot wait
# for the next pass and cannot be repeated in every branch, so it sits
# above the tree and writes current_state before the tree runs. That
# makes it take effect on THIS pass: the tree sees the new state and the
# TURNING branch executes immediately.
#
# WHY THE GUARD HAS TO OUTRANK THE CHARGE. The rim is about 7.6 cm. At
# 50 RPM that is a little under a second from first white to falling
# out; at 70 RPM about six tenths. 70 RPM is exactly when the robot is
# least interested in looking down.
#
# It also means a robot cannot win itself out of the ring. Shove an
# opponent over the rim and the winner is standing on the rim, so the
# guard fires before the attack branch runs. Nobody writes that case.
#
# WHY THE CHARGE HAS TWO LIMITS. P08's SPOT_CM / FLED_CM gap, reused. In
# at ATTACK_CM, out past LOST_CM, so an opponent wobbling at the
# threshold does not flip the robot between red and green mid-shove.
#
# WHAT IS NOT SOLVED, ON PURPOSE. Two robots nose to nose both see
# something inside ATTACK_CM, both charge, and neither moves. Nothing in
# these three states breaks that. It is where a fourth state -- and the
# tournament -- is won.

import time

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

PATROLLING = "PATROLLING"
ATTACKING = "ATTACKING"
TURNING = "TURNING"

PATROL_RPM = 50
ATTACK_RPM = 70

# The ring floor false-positives the distance sensor from about 5 cm
# out, so the charge starts underneath the lies and ends just past them.
ATTACK_CM = 3.0
LOST_CM = 5.0

# Must be further than the nose has already crept over the white, or the
# robot turns with a sensor still on the rim and guards again forever.
BACK_UP_CM = 10.0

# WORK 3: the student's own angle. P08's 135 is one answer: 180 runs the
# same diameter forever, a quarter turn runs along the rim and back into
# it.
TURN_DEG = 135

# Black floor reads high, white rim reads low, so the rim is a reading
# that DROPS. Not yet measured on the real ring.
EDGE_THRESHOLD = 200


def edge_detected():
    """True when any line sensor has reached the white rim.

    Given to students. The line sensors appear nowhere else in the
    project, so this is the only place that knows they return None until
    their first packet arrives, and the only place that knows the rim is
    low rather than high.

    Any one sensor is enough. Waiting for all three means waiting until
    the robot is most of the way off the ring.
    """
    left, center, right = alvik.get_line_sensors()
    if left is None or center is None or right is None:
        return False
    return (left < EDGE_THRESHOLD
            or center < EDGE_THRESHOLD
            or right < EDGE_THRESHOLD)


def waiting_for_gamepad(gamepad):
    """Hold the robot still until its driver presses CROSS.

    RobotGamepad's constructor already blinks yellow until the
    controller connects, and Cancel cannot get out of that wait. This
    covers the second half: blinking green while the robot waits for the
    start of the match.

    The blink is not timed by a sleep, because the button has to stay
    responsive -- pressed() only sees a push if update() is called
    often enough to catch it.

    Cancel gets out of here, so a connected robot that never gets its
    start can still be stopped.
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


current_state = PATROLLING
last_state = ""

gamepad = RobotGamepad(alvik)

try:
    waiting_for_gamepad(gamepad)

    while not sb.held('cancel'):

        distance = sb.get_closest_distance()

        # --- WORK 3: THE EDGE GUARD ---
        # Above the tree, so it beats every branch in it.
        if edge_detected():
            current_state = TURNING

        # The screen is written AFTER the guard, and that is not a
        # detail. TURNING is set by the guard and cleared by its own
        # branch on the same pass, so a screen written above the guard
        # never sees it.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Sumo:", current_state)

        # --- WORK 1: PATROLLING ---
        if current_state == PATROLLING:
            sb.light_both_leds(0, 1, 0)
            alvik.set_wheels_speed(PATROL_RPM, PATROL_RPM)

            if distance < ATTACK_CM:
                current_state = ATTACKING

        # --- WORK 2: ATTACKING ---
        elif current_state == ATTACKING:
            sb.light_both_leds(1, 0, 0)
            alvik.set_wheels_speed(ATTACK_RPM, ATTACK_RPM)

            # The opponent got away, or was pushed out. During a real
            # shove it stays inside LOST_CM and this never fires -- the
            # guard ends the attack instead, at the rim.
            if distance > LOST_CM:
                current_state = PATROLLING

        # --- WORK 3: TURNING ---
        # Both moves block, and the robot is leaving, so there is
        # nothing it needs to watch while they run.
        elif current_state == TURNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(-BACK_UP_CM)
            alvik.rotate(TURN_DEG)
            current_state = PATROLLING

        # --- The catch-all ---
        else:
            sb.light_both_leds(1, 0, 0)
            sb.log_info("Bad:", current_state)
            time.sleep_ms(3000)
            break

        time.sleep_ms(50)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
