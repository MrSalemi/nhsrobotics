# Project 06 SOLUTION: Sensor Assist
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
bot = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 45
STOP_DISTANCE = 15

try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # 1. SENSE
        gamepad.update()
        distance_cm = bot.get_closest_distance()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        # WORK 1 version — simple but traps you at the wall:
        # if distance_cm < STOP_DISTANCE:
        #     left_speed = 0
        #     right_speed = 0

        # WORK 2 version — block forward only, allow escape.
        # The LED lines are WORK 3 (red while blocking, green when clear):
        if distance_cm < STOP_DISTANCE:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)
finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
