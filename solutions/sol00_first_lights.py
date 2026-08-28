# Project 00 SOLUTION: First Lights
# Version: V01
#
# Teacher copy. Four steps, three of them WORK, and nothing in the file
# that needs WiFi, a browser, a controller or a paired anything. That
# absence is the point of the project: a first day where the only way to
# fail is a typo, and a typo is fixable in front of the kid.
#
# The three setup lines are GIVEN here and typed by hand in P01. Day one
# buys a win; day two buys the understanding.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

try:
    while not sb.held('cancel'):

        # --- WORK 1: LEFT RED, RIGHT GREEN ---
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(0, 1, 0)
        time.sleep(0.5)

        # --- WORK 2: SWAP THEM ---
        # Deliberately the same three lines with two values traded. A
        # student who got WORK 1 right cannot get this one wrong, and
        # that is what it is for.
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(1, 0, 0)
        time.sleep(0.5)

        # --- WORK 3: BOTH YELLOW, THEN DARK ---
        # Red and green at once is yellow. This is the first time a
        # color is made rather than picked, and it is the one idea in
        # the project a student can actually get stuck on.
        alvik.left_led.set_color(1, 1, 0)
        alvik.right_led.set_color(1, 1, 0)
        time.sleep(0.5)

        # The dark gap. Without it the pattern runs into itself and the
        # loop's restart is invisible.
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        time.sleep(0.5)

        # --- FLEX: A FOURTH STEP, IN A COLOR THEY MIX THEMSELVES ---
        # Not printed anywhere. Magenta is red plus blue, cyan is green
        # plus blue. Anything that is not red, green or yellow counts.
        #
        # alvik.left_led.set_color(1, 0, 1)      # magenta
        # alvik.right_led.set_color(0, 1, 1)     # cyan
        # time.sleep(0.5)

finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
