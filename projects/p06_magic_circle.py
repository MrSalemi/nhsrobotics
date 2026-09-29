# Project 06: The Magic Circle
# Version: V01
#
# GOAL: The robot hides an invisible ring on the floor. You drive with the
# gamepad and find it, using nothing but the lights the robot gives you.
# Drive into the ring and it stops and dances.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p06.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import math
import random
import time

# GIVEN: the robot, the suit and the gamepad.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

# GIVEN: 70 is as fast as these motors go.
MAX_RPM = 70

# GIVEN: the ring is somewhere within this far of the robot, and this wide.
MAX_DIST_CM = 100
RING_DIAMETER_CM = 20


# GIVEN: the hidden ring. You do not have to change anything in here, but
# read it if you are curious -- there is no magic in it, only arithmetic.
class Circle:
    """A ring on the floor that only the robot can see."""

    TOLERANCE_DEG = 6       # this close to straight ahead counts as aimed
    MIN_DIST_CM = 40        # never hides right under the robot

    def __init__(self, max_dist, diameter):
        self.radius = diameter / 2
        # Pick a random direction and a random distance, then turn those
        # into a spot on the floor.
        away = random.uniform(self.MIN_DIST_CM, max_dist)
        bearing = math.radians(random.uniform(0, 360))
        self.x = away * math.cos(bearing)
        self.y = away * math.sin(bearing)

    def get_bearings(self):
        """Report where the ring is from where the robot is right now.

        Returns three things:
            direction  1 if the ring is off to the left
                -1 if the ring is off to the right
                 0 if the robot is pointed at it
            dx   how far away the ring is along one direction
            dy   how far away the ring is along the other
        """
        x, y, theta = alvik.get_pose()
        dx = self.x - x
        dy = self.y - y

        # Swing the ring around into "in front of me / beside me" terms.
        t = math.radians(theta)
        forward = dx * math.cos(t) + dy * math.sin(t)
        sideways = -dx * math.sin(t) + dy * math.cos(t)

        away = math.sqrt(dx * dx + dy * dy)
        limit = math.sin(math.radians(self.TOLERANCE_DEG))

        # Dividing by the distance keeps the aimed-at window the same size
        # whether the ring is close or far. The forward test matters: with
        # the ring directly BEHIND, sideways is also near zero, and without
        # it the robot would claim to be aimed while facing backwards.
        if away > 0.1 and forward > 0 and abs(sideways / away) < limit:
            return 0, dx, dy
        if sideways > 0:
            return 1, dx, dy
        return -1, dx, dy


# GIVEN: zero the pose, then hide the first ring. The ring is placed from
# wherever the robot is standing when this runs.
alvik.reset_pose(0, 0, 0)
circle = Circle(MAX_DIST_CM, RING_DIAMETER_CM)

try:
    # GIVEN: Cancel on the robot or Options on the gamepad ends the run.
    while not (sb.held('cancel') or gamepad.held('options')):
        gamepad.update()

        # GIVEN: tank drive, exactly as you wrote it in P03.
        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM
        alvik.set_wheels_speed(left_speed, right_speed)

        # GIVEN: ask the ring where it is.
        direction, dx, dy = circle.get_bearings()

        # GIVEN: a stand-in, so this file runs before you have written
        # anything. Your WORK 1 lines replace this one.
        distance = MAX_DIST_CM

        # --- WORK 1: WORK OUT THE DISTANCE ---
        # get_bearings() hands you dx and dy. It does NOT hand you the
        # distance. Use the Pythagorean theorem to work it out, put it in
        # a variable named distance, and show it on the screen. Copy the
        # lines in from the guide where the "pass" line is, then delete
        # the "pass" line.
        pass

        # --- WORK 2: TURN direction INTO TWO LIGHTS ---
        # A number on the screen is no use to somebody across the room
        # with a controller in their hands. Light the LED on the side the
        # ring is on, and no light at all when the robot is aimed at it.

        # --- WORK 3: TURN THE DISTANCE INTO A COLOR ---
        # The Nano's LED is your hot-and-cold meter. Red when you are on
        # top of the ring, blue when you are far from it, and every shade
        # in between.

        # GIVEN: the ending. When your distance says the robot is inside
        # the ring, it stops, dances, and hides a new one.
        if distance < RING_DIAMETER_CM / 2:
            alvik.brake()
            sb.light_both_leds(1, 1, 1)
            alvik.drive(0, 120)
            time.sleep(3.0)
            alvik.brake()
            sb.light_both_leds(0, 0, 0)
            time.sleep(1.0)
            alvik.reset_pose(0, 0, 0)
            circle = Circle(MAX_DIST_CM, RING_DIAMETER_CM)

        # GIVEN: a small pause, so the loop does not run away with the
        # processor.
        time.sleep(0.05)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    sb.nano_led.off()
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
