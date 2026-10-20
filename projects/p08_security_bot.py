# Project 08: The Security Bot
# Version: V03
#
# GOAL: A robot that patrols a room, advances on whatever it finds,
# and either scares it off or loses its nerve and runs away.
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
ADVANCING = "ADVANCING"
TURNING = "TURNING"
RUNNING = "RUNNING"

# GIVEN: how fast the robot drives in each of its moods, in centimeters
# per second. Menacing is slow, on purpose.
PATROL_SPEED_CMS = 10.0
ADVANCE_SPEED_CMS = 6.0

# GIVEN: the three distances the whole story turns on, in centimeters.
# SPOT_CM is 24 inches -- close enough to be worth investigating.
# FLED_CM means it got away. STUBBORN_CM means it did not.
SPOT_CM = 10.0
FLED_CM = 10.0
STUBBORN_CM = 7.0

# GIVEN: how far the retreat turns, and how far it runs afterwards.
# 135 and not 180, on purpose. The guide explains why, and it is a
# better reason than it looks.
RETREAT_TURN_DEG = 135.0
RUN_CM = 50.0

# GIVEN: the state the robot is in right now. This one variable decides
# everything the robot does. It is the whole project.
current_state = PATROLLING

# GIVEN: what the screen said last time, so the state gets written only
# when it actually changes. Same trick as the clock in P07.
last_state = ""

try:
    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # GIVEN: how much room is in front of the robot this time round.
        # With nothing in front of it, this reads 999.
        distance = sb.get_closest_distance()

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

        # --- WORK 2: ADVANCING ---
        # An "elif" branch, ABOVE the else you just wrote. Red lights,
        # and drive forward slowly -- menacing is deliberate, not fast.
        # This state has TWO ways out, so its branch ends with two
        # tests, not one:
        #   the target fled       -- further away than FLED_CM
        #   the target did not    -- closer than STUBBORN_CM
        # One of them goes back to patrolling. The other one starts the
        # retreat.

        # --- WORK 3: TURNING and RUNNING ---
        # Two more "elif" branches, still above the else, and together
        # they are the retreat. TURNING turns the robot away, then hands
        # over to RUNNING. RUNNING drives off, then goes back on patrol.
        # These two are shorter than you expect -- three lines each --
        # and the guide explains why they are allowed to be.

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
