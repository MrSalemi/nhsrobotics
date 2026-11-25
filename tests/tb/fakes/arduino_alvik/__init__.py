# tests/tb/fakes/arduino_alvik/__init__.py -- the BFM. V02
#
# Shadows the real arduino_alvik package while a DUT runs. It decides
# nothing. Every call is translated into a plant command or a plant query,
# and recorded on the monitor on the way past.
#
# The method list here is deliberately the exact set the course uses. A
# solution that reaches for something else gets an AttributeError, which
# is a loud failure telling us the API surface grew.

from tb import wiring


class _Led:
    def __init__(self, name):
        self.name = name
        self.color = (0, 0, 0)

    def set_color(self, red, green, blue):
        self.color = (red, green, blue)
        wiring.active().monitor.record("led", self.name, self.color)


class ArduinoAlvik:
    def __init__(self):
        self.left_led = _Led("left")
        self.right_led = _Led("right")
        self.began = False
        self.stopped = False

    # --- lifecycle ---

    def begin(self):
        self.began = True
        wiring.active().monitor.record("begin")
        return 0

    def stop(self):
        self.stopped = True
        wiring.active().monitor.record("stop")

    # --- motion ---

    def drive(self, forward, turn, linear_unit=None, angular_unit=None):
        env = wiring.active()
        env.monitor.record("drive", forward, turn)
        env.plant.drive(forward, turn)

    def set_wheels_speed(self, left, right, unit=None):
        env = wiring.active()
        env.monitor.record("set_wheels_speed", left, right)
        env.plant.set_wheels_speed(left, right)

    def brake(self):
        env = wiring.active()
        env.monitor.record("brake")
        env.plant.brake()

    def move(self, distance, unit=None, blocking=True):
        env = wiring.active()
        env.monitor.record("move", distance)
        env.plant.move(distance)

    def rotate(self, angle, unit=None, blocking=True):
        env = wiring.active()
        env.monitor.record("rotate", angle)
        env.plant.rotate(angle)

    # --- pose ---

    def get_pose(self):
        return wiring.active().plant.get_pose()

    def reset_pose(self, x=0.0, y=0.0, theta=0.0):
        env = wiring.active()
        env.monitor.record("reset_pose", x, y, theta)
        env.plant.reset_pose(x, y, theta)

    def get_orientation(self):
        return wiring.active().plant.get_orientation()

    # --- sensors ---

    def get_line_sensors(self):
        return wiring.active().plant.get_line_sensors()

    def get_distance(self, unit=None):
        return wiring.active().plant.get_distance()

    # --- touch pads ---

    def get_touch_up(self):
        return wiring.active().touch("up")

    def get_touch_down(self):
        return wiring.active().touch("down")

    def get_touch_left(self):
        return wiring.active().touch("left")

    def get_touch_right(self):
        return wiring.active().touch("right")

    def get_touch_ok(self):
        return wiring.active().touch("ok")

    def get_touch_cancel(self):
        return wiring.active().touch("cancel")

    def get_touch_center(self):
        return wiring.active().touch("center")
