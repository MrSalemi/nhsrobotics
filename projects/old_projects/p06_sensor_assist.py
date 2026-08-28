# Project 06: Sensor Assist
# GOAL: Blend HUMAN control with SENSOR control. You drive with the
# gamepad, but the robot refuses to crash into a wall.
#
# This is the pattern every real robot uses:
#     1. SENSE   (read gamepad + sensors)
#     2. THINK   (decide: is the human about to do something bad?)
#     3. ACT     (send the final, possibly corrected, speeds)
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p06.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
bot = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 45
STOP_DISTANCE = 15   # centimeters

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # --- 1. SENSE ---
        gamepad.update()
        distance_cm = bot.get_closest_distance()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # --- 2. THINK ---
        # WORK 1: if distance_cm is closer than STOP_DISTANCE,
        # force BOTH speeds to 0.

        # WORK 2: WORK 1 has a problem — once you're trapped
        # near the wall, you can't back away! Fix it: only zero out a
        # speed if it is POSITIVE (driving forward). Backing up
        # (negative speed) should always be allowed.
        # HINT: test each speed separately:  if left_speed > 0: ...

        # WORK 3: LED feedback — turn the LEDs red while the assist is
        # blocking (closer than STOP_DISTANCE), green otherwise.

        # --- 3. ACT ---
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
