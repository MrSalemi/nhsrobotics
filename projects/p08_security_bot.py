# Project 08: The Security Bot
# Version: V04
#
# GOAL: A robot that patrols a room, stops and warns off whatever it
# finds, and runs away if the thing will not leave.
#
# Four states. One variable decides which one the robot is in, and
# every other line in the loop asks that variable first.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p08.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit. No gamepad -- this robot drives itself.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: the names of the four states, spelled once each. Everywhere
# else you use the name instead of typing the word again. Misspell the
# name and Python stops and tells you exactly where. Misspell a word
# inside quotes and nobody tells you anything -- the robot just quietly
# matches no branch at all, which is a much worse afternoon.
PATROLLING = "PATROLLING"
WARNING = "WARNING"
TURNING = "TURNING"
RUNNING = "RUNNING"

# GIVEN: how fast the robot patrols, in centimeters per second.
PATROL_SPEED_CMS = 10.0

# GIVEN: the two distances the story turns on, in centimeters.
# With nothing in front of it, the sensor sees the floor at about 19 cm,
# so both of these sit below that.
# Closer than SPOT_CM: something is there. Past FLED_CM: it left.
SPOT_CM = 10.0
FLED_CM = 15.0

# GIVEN: how long the warning lasts, and how fast the red light flashes,
# in milliseconds.
WARNING_MS = 5000
FLASH_MS = 250

# GIVEN: the retreat. How far it backs up, how far it turns, and how
# far it runs afterwards. 135 and not 180, on purpose. The guide
# explains why, and it is a better reason than it looks.
BACK_UP_CM = 10.0
RETREAT_TURN_DEG = 135.0
RUN_CM = 50.0

# GIVEN: the state the robot is in right now. This one variable decides
# everything the robot does. It is the whole project.
current_state = PATROLLING

# GIVEN: what the screen said last time, so the state gets written only
# when it actually changes. Same trick as the clock in P07.
last_state = ""

# GIVEN: when the warning started, and the flash. The flash is your P07
# blink: the last time the light changed, and whether it is on.
warning_start = time.ticks_ms()
last_flash = time.ticks_ms()
red_is_on = False

try:
    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # GIVEN: how much room is in front of the robot this time round.
        # With nothing in front of it, the sensor sees the floor and
        # reads about 19 cm.
        distance = sb.get_closest_distance()

        # GIVEN: what time it is, once per pass, the same as P07.
        now = time.ticks_ms()

        # GIVEN: the state on the screen, so you can always see what the
        # robot thinks it is doing. When something goes wrong, look here
        # before you look anywhere else.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Security:", current_state, distance)

        # --- WORK 1: PATROLLING, and the catch-all ---
        # Write the branch that runs while the robot is on patrol: green
        # lights, drive straight forward, and at the bottom of the
        # branch, the test that sends it after anything closer than
        # SPOT_CM.
        # Then write the "else" that goes at the very end of the whole
        # chain, and stops the robot with a message when current_state
        # holds a word that no branch matches. You want that from your
        # very first run. The guide has both. Put them where the "pass"
        # is, then delete the "pass" line.
        pass

        # --- WORK 2: WARNING ---
        # First, add one line to your WORK 1 test, so the clock starts
        # the moment the robot spots something.
        # Then an "elif" branch, ABOVE the else you just wrote. Stand
        # still, and flash the red lights the way P07 blinked them.
        # This state has TWO ways out, so its branch ends with two
        # tests, not one:
        #   it left               -- further away than FLED_CM
        #   it did not            -- WARNING_MS has gone by
        # One of them goes back to patrolling. The other one starts the
        # retreat.

        # --- WORK 3: TURNING and RUNNING ---
        # Two more "elif" branches, still above the else, and together
        # they are the retreat. TURNING backs up and turns the robot
        # away, then hands over to RUNNING. RUNNING drives off, then goes
        # back on patrol. These two are shorter than you expect, and the
        # guide explains why they are allowed to be.

        # GIVEN: a moment for the robot to get on with its own work.
        # Nothing in this project is timed by this line.
        time.sleep_ms(50)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
