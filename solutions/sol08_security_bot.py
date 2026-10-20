# Project 08: The Security Bot -- SOLUTION
# Version: V04
#
# Teacher copy. Four states in one elif tree keyed on current_state,
# plus the FLEX fifth state at the bottom.
#
#   PATROLLING  green, drive forward, watch for anything inside SPOT_CM
#   WARNING     red, flashing, stand still for five seconds, two ways out
#   TURNING     blue, back up, then turn 135 degrees away
#   RUNNING     blue, drive away
#
# V04: the robot no longer advances. The distance sensor sees the floor
# at about 19 cm, so SPOT_CM had to come down to 10 and there was no room
# left to advance in. It stops and warns instead.
#
# WHY THIS ONE NEEDS A STATE VARIABLE.
#
# Follow a single sensor reading of 8 cm through the machine:
#
#   PATROLLING  8 is inside SPOT_CM        -> stop and warn it off
#   WARNING     8 is not past FLED_CM      -> it is still there, keep warning
#   TURNING     8 means nothing at all     -> ignored, we are leaving
#   RUNNING     8 means nothing at all     -> ignored, we are leaving
#
# One number, four correct answers, and nothing in the number says
# which. Only current_state says which.
#
# The better argument is the timer. "It is still there after five
# seconds" is not a fact about a reading. Five seconds after WHAT? After
# the robot started warning -- and only a program that remembers it is
# warning, and when it started, can say that sentence.
#
# WHICH STATES WATCH, AND WHICH DO NOT.
#
# PATROLLING and WARNING are watching states. They set a speed with
# drive(), which returns immediately, and then test the sensor and the
# clock -- so the loop keeps running and the robot can change its mind.
#
# TURNING and RUNNING are not watching anything. The robot has already
# decided to leave. So they use move() and rotate(), which block. That
# is what P07 warned against, and it is right here for the opposite
# reason -- there is nothing to watch.

import time

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

PATROLLING = "PATROLLING"
WARNING = "WARNING"
TURNING = "TURNING"
RUNNING = "RUNNING"
PEEKING = "PEEKING"          # FLEX only

PATROL_SPEED_CMS = 10.0

# The sensor reads the floor at about 19 cm with nothing in front of it.
# Both numbers sit below that, or the floor looks like a clown.
# Inside SPOT_CM: something is there. Past FLED_CM: it left. The gap
# between them stops a clown at exactly 10 cm flicking the robot in and
# out of WARNING. The robot is standing still, so the gap works -- it
# is not turning away from the thing it is measuring (DECISIONS #27).
SPOT_CM = 10.0
FLED_CM = 15.0

# How long the warning lasts, and how fast the red light flashes.
WARNING_MS = 5000
FLASH_MS = 250

# The retreat. Back up first, so the turn does not swing the robot's
# corner into the clown. 135 and not 180 so the robot does not retrace
# its own path and bounce between the same two walls.
BACK_UP_CM = 10.0
RETREAT_TURN_DEG = 135.0
RUN_CM = 50.0

# FLEX only. The peek looks back down the path the robot just ran, and
# that is half a turn from where it is now -- not another 135.
PEEK_TURN_DEG = 180.0

current_state = PATROLLING
last_state = ""

# When the warning started, and the flash -- P07's blink, unchanged.
warning_start = time.ticks_ms()
last_flash = time.ticks_ms()
red_is_on = False

try:
    while not sb.held('cancel'):

        distance = sb.get_closest_distance()
        now = time.ticks_ms()

        if current_state != last_state:
            last_state = current_state
            sb.update_display("Security:", current_state)

        # --- WORK 1: PATROLLING ---
        if current_state == PATROLLING:
            sb.light_both_leds(0, 1, 0)
            alvik.drive(PATROL_SPEED_CMS, 0)

            # The clock starts here, on the way in, because this is the
            # only line that knows the warning has just begun.
            if distance < SPOT_CM:
                warning_start = now
                current_state = WARNING

        # --- WORK 2: WARNING ---
        elif current_state == WARNING:
            alvik.drive(0, 0)

            if time.ticks_diff(now, last_flash) > FLASH_MS:
                last_flash = now
                red_is_on = not red_is_on
            if red_is_on:
                sb.light_both_leds(1, 0, 0)
            else:
                sb.light_both_leds(0, 0, 0)

            # Two ways out. It left, or it outlasted the warning.
            # With nothing in front, the reading is the floor at about
            # 19 cm -- past FLED_CM -- so "it left" still works.
            if distance > FLED_CM:
                current_state = PATROLLING
            elif time.ticks_diff(now, warning_start) > WARNING_MS:
                current_state = TURNING

        # --- WORK 3: TURNING ---
        # move() and rotate() both block, so the back-up and the whole
        # turn happen on this one pass.
        elif current_state == TURNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(-BACK_UP_CM)
            alvik.rotate(RETREAT_TURN_DEG)
            current_state = RUNNING

        # --- WORK 3: RUNNING ---
        elif current_state == RUNNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(RUN_CM)

            # Without the FLEX this line reads
            #     current_state = PATROLLING
            current_state = PEEKING

        # --- FLEX: PEEKING ---
        # Turns round to look back the way it ran. Seeing something
        # sends it to TURNING, which it has already been through once.
        elif current_state == PEEKING:
            sb.light_both_leds(1, 1, 0)
            alvik.rotate(PEEK_TURN_DEG)

            # rotate() blocked through the whole turn, so the reading
            # from the top of this pass is from before the turn.
            if sb.get_closest_distance() < SPOT_CM:
                current_state = TURNING
            else:
                current_state = PATROLLING

        # --- The catch-all ---
        # A state name misspelled inside quotes is still a good word, so
        # Python raises nothing and every branch above fails to match.
        # Every new state goes ABOVE this else. It is always last.
        else:
            sb.light_both_leds(1, 0, 0)
            sb.log_info("Bad:", current_state)
            time.sleep_ms(3000)
            break

        # A moment for the robot's own background work. Nothing in this
        # project is timed by it.
        time.sleep_ms(50)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
