# Project 00: First Lights
# Version: V01
#
# GOAL: Make the robot's two colored lights do what you tell them to.
# Left red and right green, then the two swapped, then both yellow,
# then dark -- over and over, until you touch Cancel.
#
# This is your first robot program. It needs nothing but the robot and a
# USB cable. No WiFi, no browser, no controller, no Bluetooth.
#
# THIS FILE IS MOSTLY EMPTY ON PURPOSE. You type the code yourself, from
# the guide. Copying it by hand is how you learn the shape of Python.
# Count your spaces -- four per level, never a tab.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p00.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit. Three lines that have to run before
# anything else can. You will type them yourself in P01 -- today they
# come with the file, so you can get straight to the lights.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

try:
    # GIVEN: the main loop. Touch Cancel on the robot to end the run, so
    # you never need Thonny's Stop button.
    while not sb.held('cancel'):

        # --- WORK 1: LEFT RED, RIGHT GREEN ---
        # Two lines that set the two lights to two different colors, and
        # a third that waits half a second so your eyes can catch it.
        # Copy them in from the guide where the "pass" line is, then
        # delete the "pass" line.
        pass

        # --- WORK 2: SWAP THEM ---
        # The same three lines again, with the colors traded. Left goes
        # green, right goes red. Nothing new here -- if WORK 1 worked,
        # this one works.

        # --- WORK 3: BOTH YELLOW, THEN DARK ---
        # There is no yellow setting on these lights. You make yellow by
        # turning red and green on at the same time. Then turn both
        # lights off and wait once more, so the pattern has a gap in it
        # before the loop starts the whole thing over.

finally:
    # GIVEN. A crash must never leave a light on.
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
