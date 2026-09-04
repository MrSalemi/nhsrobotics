# tests/tb/plant.py -- the reference model of the robot's world. V02
#
# The plant owns the truth: where the robot really is, where the line
# really is, what the sensors would really report. The DUT never sees any
# of it directly -- it sees only what the fake ArduinoAlvik hands back,
# which is the truth after the measured defects have been applied.
#
# The scoreboard checks against the plant's truth, never against the DUT's
# own numbers. A checker that recomputes the DUT's arithmetic is a mirror
# and passes whenever the DUT is wrong in an interesting way.
#
# GEOMETRY CAVEAT: the sensor placement below is a MODEL, not a
# measurement. Nobody has put calipers on an Alvik for these numbers. The
# alignment results are therefore correct up to this geometry -- which is
# fine, because P08's claim is that halving cancels a scale error, and
# that claim does not depend on the exact spacing. Measure and update if a
# test ever turns on the absolute numbers.

import math

# --- robot geometry, modelled ---
SENSOR_FORWARD_CM = 5.0        # line sensors ahead of the wheel axle
SENSOR_HALF_SPACING_CM = 1.5   # outer sensors either side of centre
LINE_HALF_WIDTH_CM = 1.0       # 2 cm tape

# Measured 2026-08-09: white paper reads about 50, a sensor solidly on
# the line reads 300-650. The sensor reads HIGH over black, whatever the
# black happens to be -- tape on paper in the line projects, the floor of
# the sumo ring in P09. In the ring the polarity of the QUESTION flips,
# not the polarity of the sensor: the rim is white, so an edge is a
# reading that drops.
SENSOR_ON_VALUE = 400
SENSOR_OFF_VALUE = 50

# --- things in front of the robot ---
TARGET_RADIUS_CM = 5.0     # an Alvik-sized object, measured from centre
SENSOR_CONE_DEG = 30.0     # the ToF sees roughly what is ahead of it


class Target:
    """Something the distance sensor can see: a hand, a clown, another bot.

    mode:
        'stand'  never moves
        'flee'   backs directly away once the robot is inside notice_cm
        'chase'  closes on the robot the whole time
        'glued'  holds a fixed gap off the robot's nose whatever the robot
                 does. Models a shove that never ends -- which is how a
                 test proves that something ELSE ends it.
    """

    def __init__(self, x, y, mode="stand", speed_cms=0.0,
                 notice_cm=60.0, gap_cm=2.0, radius_cm=TARGET_RADIUS_CM):
        self.x = float(x)
        self.y = float(y)
        self.mode = mode
        self.speed_cms = float(speed_cms)
        self.notice_cm = float(notice_cm)
        self.gap_cm = float(gap_cm)
        self.radius_cm = float(radius_cm)
        # Once something has noticed a robot coming at it, it does not
        # un-notice. Without this latch a fleeing target stops the moment
        # it is back outside notice_cm, and the two settle into a chase
        # that never resolves either way.
        self.spooked = False


# --- measured hardware defects, from REFERENCE.md ---
# Every one of these is a knob so a test can prove a project is immune to
# it, rather than a comment claiming so.
DEFAULT_DEFECTS = {
    "drive_scale": 0.926,       # drive() delivers 92.6% of what you ask
    "drive_lag_ms": 210,        # and takes this long to get going
    "theta_scale": 1.10,        # pose theta over-reports rotation 8-13%
    "brake_settle_ms": 500,     # brake() asks; the robot rolls on
    "sensor_dead_ms": 0,        # sensors return None this long after boot
    "yaw_offset_deg": 0.0,      # where the IMU happens to start
    "oled_present": True,       # a loose OLED silently shows nothing
    "max_speed_cms": 11.5,      # 70 RPM on a 34 mm wheel, after drive_scale
}


class Plant:
    def __init__(self, line_point=(40.0, 0.0), line_angle_deg=90.0,
                 start=(0.0, 0.0, 0.0), wall_distance_cm=None, defects=None,
                 target=None, ring=None):
        self.defects = dict(DEFAULT_DEFECTS)
        if defects:
            self.defects.update(defects)

        # Truth. The DUT can never read these.
        self.x, self.y, self.theta = start
        self.line_point = line_point
        self.line_angle = line_angle_deg

        # A sumo ring, as (radius_cm, rim_width_cm), centred on the
        # origin. When one is set the line sensors report the ring
        # instead of a strip of tape.
        self.ring = ring
        self.target = target
        self.max_radius_cm = math.hypot(self.x, self.y)
        self.left_ring = False
        self.wall_distance_cm = wall_distance_cm

        # What reset_pose() last set the reported frame to.
        self._pose_origin = (self.x, self.y, self.theta)
        self._pose_offset = (0.0, 0.0, 0.0)

        # Commanded velocity, and how long it has been commanded, so the
        # startup lag can be modelled.
        self._cmd_v = 0.0
        self._cmd_w = 0.0
        self._cmd_age_ms = 0
        self._braking_ms = 0

        # What the wheels are actually doing, which trails the command.
        self._delivered_v = 0.0
        self._delivered_w = 0.0

        self.elapsed_ms = 0
        self.distance_travelled_cm = 0.0

    # ---------- commands in ----------

    def drive(self, forward_cms, turn_deg_s):
        if (forward_cms, turn_deg_s) != (self._cmd_v, self._cmd_w):
            self._cmd_age_ms = 0
        self._cmd_v = float(forward_cms)
        self._cmd_w = float(turn_deg_s)
        self._braking_ms = 0

    def set_wheels_speed(self, left_rpm, right_rpm):
        """Modelled, not measured. Enough to move the robot sensibly for
        the gamepad projects; no test scores absolute distance on it."""
        wheel_circumference_cm = math.pi * 3.3
        left_cms = left_rpm * wheel_circumference_cm / 60.0
        right_cms = right_rpm * wheel_circumference_cm / 60.0
        track_cm = 8.8
        self.drive((left_cms + right_cms) / 2.0,
                   math.degrees((right_cms - left_cms) / track_cm))

    def brake(self):
        self._braking_ms = self.defects["brake_settle_ms"]

    def move(self, distance_cm):
        """move() is accurate -- 495 mm on a 500 mm command."""
        self._advance_pose(distance_cm * 0.99, 0.0)

    def rotate(self, angle_deg):
        """Never measured on real hardware. Modelled as accurate, and no
        project that a test scores is allowed to use it anyway."""
        self._advance_pose(0.0, angle_deg)

    def reset_pose(self, x, y, theta):
        self._pose_origin = (self.x, self.y, self.theta)
        self._pose_offset = (x, y, theta)

    # ---------- time ----------

    def step(self, dt_ms):
        self.elapsed_ms += dt_ms
        self._cmd_age_ms += dt_ms
        self._step_target(dt_ms)

        scale = self.defects["drive_scale"]

        if self._braking_ms > 0:
            # Rolling to a stop: still moving, at a decaying rate.
            settle = self.defects["brake_settle_ms"] or 1
            fraction = max(0.0, self._braking_ms / settle)
            self._braking_ms = max(0, self._braking_ms - dt_ms)
            if self._braking_ms == 0:
                self._cmd_v = self._cmd_w = 0.0
            self._delivered_v = self._cmd_v * scale * fraction
            self._delivered_w = self._cmd_w * scale * fraction
        else:
            wanted_v = self._cmd_v * scale
            wanted_w = self._cmd_w * scale

            # The motors run out of RPM. Without this the sim happily
            # accelerates forever, and a physics profile that saturates on
            # the real floor passes every check here.
            cap = self.defects.get("max_speed_cms")
            if cap:
                if wanted_v > cap:
                    wanted_v = cap
                elif wanted_v < -cap:
                    wanted_v = -cap

            # The base does not answer instantly. It slews toward a new
            # setpoint with the measured 0.21 s time constant, so a HELD
            # command loses about v * tau of distance getting going --
            # which is what the startup lag measured on 2026-08-03 -- and
            # a command that keeps CHANGING is followed with a lag instead
            # of stalling outright. Modelling the lag as a dead stop after
            # every change was fine while every project set a speed once,
            # but it makes any ramp impossible, which is not what the
            # measurement said.
            tau_ms = self.defects["drive_lag_ms"]
            alpha = min(1.0, float(dt_ms) / tau_ms) if tau_ms > 0 else 1.0
            self._delivered_v += (wanted_v - self._delivered_v) * alpha
            self._delivered_w += (wanted_w - self._delivered_w) * alpha

        seconds = dt_ms / 1000.0
        self._advance_pose(self._delivered_v * seconds,
                           self._delivered_w * seconds)

    def _advance_pose(self, distance_cm, turn_deg):
        # Small enough steps that straight-line integration is fine; the
        # DUTs all sleep 10-50 ms, which is well under a degree per step.
        self.theta += turn_deg
        radians = math.radians(self.theta)
        self.x += distance_cm * math.cos(radians)
        self.y += distance_cm * math.sin(radians)
        self.distance_travelled_cm += abs(distance_cm)

        radius = math.hypot(self.x, self.y)
        self.max_radius_cm = max(self.max_radius_cm, radius)
        if self.ring is not None and radius > self.ring[0]:
            self.left_ring = True

    def _step_target(self, dt_ms):
        target = self.target
        if target is None or target.mode == "stand":
            return

        nose_x, nose_y = self.nose_point()

        if target.mode == "glued":
            # Pinned to the robot's nose, so the gap never opens on its
            # own. Anything that ends the charge has to come from the
            # robot's own code.
            radians = math.radians(self.theta)
            reach = target.gap_cm + target.radius_cm
            target.x = nose_x + reach * math.cos(radians)
            target.y = nose_y + reach * math.sin(radians)
            return

        dx = target.x - nose_x
        dy = target.y - nose_y
        span = math.hypot(dx, dy) or 1.0
        step = target.speed_cms * dt_ms / 1000.0

        if target.mode == "flee":
            if span - target.radius_cm <= target.notice_cm:
                target.spooked = True
            if not target.spooked:
                return
            step = +step
        elif target.mode == "chase":
            step = -step
        else:
            return

        target.x += step * dx / span
        target.y += step * dy / span

    def nose_point(self):
        radians = math.radians(self.theta)
        return (self.x + SENSOR_FORWARD_CM * math.cos(radians),
                self.y + SENSOR_FORWARD_CM * math.sin(radians))

    # ---------- sensors out ----------

    def get_pose(self):
        """Reported pose. theta carries the odometry over-report; x and y
        are handed back clean, because nothing in the course leans on
        their absolute accuracy and no measurement exists for them."""
        ox, oy, otheta = self._pose_origin
        rx, ry, rtheta = self._pose_offset
        return (rx + (self.x - ox),
                ry + (self.y - oy),
                rtheta + (self.theta - otheta) * self.defects["theta_scale"])

    def get_orientation(self):
        """(roll, pitch, yaw). Yaw is the IMU: true, but 0-360 and wrapping."""
        yaw = (self.theta + self.defects["yaw_offset_deg"]) % 360.0
        return (0.0, 0.0, yaw)

    def sensor_positions(self):
        radians = math.radians(self.theta)
        forward = (math.cos(radians), math.sin(radians))
        left = (-math.sin(radians), math.cos(radians))
        nose = (self.x + SENSOR_FORWARD_CM * forward[0],
                self.y + SENSOR_FORWARD_CM * forward[1])
        offsets = (SENSOR_HALF_SPACING_CM, 0.0, -SENSOR_HALF_SPACING_CM)
        return [(nose[0] + off * left[0], nose[1] + off * left[1])
                for off in offsets]

    def _distance_to_line(self, point):
        radians = math.radians(self.line_angle)
        direction = (math.cos(radians), math.sin(radians))
        dx = point[0] - self.line_point[0]
        dy = point[1] - self.line_point[1]
        return abs(dx * direction[1] - dy * direction[0])

    def get_line_sensors(self):
        if self.elapsed_ms < self.defects["sensor_dead_ms"]:
            return (None, None, None)

        if self.ring is not None:
            # Black floor inside, white rim outside. Black reads high, so
            # a sensor out on the rim reads LOW -- the edge is a drop.
            inner_radius = self.ring[0] - self.ring[1]
            return tuple(
                SENSOR_OFF_VALUE
                if math.hypot(point[0], point[1]) > inner_radius
                else SENSOR_ON_VALUE
                for point in self.sensor_positions())

        return tuple(
            SENSOR_ON_VALUE if self._distance_to_line(p) <= LINE_HALF_WIDTH_CM
            else SENSOR_OFF_VALUE
            for p in self.sensor_positions())

    def get_distance(self):
        """Five ToF zones: a target, a wall straight ahead, or nothing."""
        if self.target is not None:
            gap = self._gap_to_target()
            if gap is None:
                return (0, 0, 0, 0, 0)  # nothing in the cone -- no echo
            return tuple([gap] * 5)

        if self.wall_distance_cm is None:
            return (0, 0, 0, 0, 0)      # no echo -- SuperBot turns this into 999
        remaining = max(0.0, self.wall_distance_cm - self.distance_travelled_cm)
        return tuple([remaining] * 5)

    def _gap_to_target(self):
        """Centimetres of clear air ahead, or None if the target is not in
        front of the robot. Turning away really does lose sight of it,
        which is what makes a retreat testable."""
        nose_x, nose_y = self.nose_point()
        dx = self.target.x - nose_x
        dy = self.target.y - nose_y
        bearing = math.degrees(math.atan2(dy, dx))
        error = (bearing - self.theta + 180.0) % 360.0 - 180.0
        if abs(error) > SENSOR_CONE_DEG:
            return None
        gap = math.hypot(dx, dy) - self.target.radius_cm
        return max(gap, 0.5)

    # ---------- truth, for the scoreboard only ----------

    def heading_error_to_square_deg(self):
        """How far the robot's heading is from square AND facing the line.

        Square means the sensor pair is parallel to the line. Two headings
        satisfy that, 180 degrees apart, and only one of them has the
        robot facing the line -- the other has it driving away. Measuring
        modulo 180 would call both correct, which is a hole: a robot that
        turns too far ends up perpendicular, backwards, and scores clean.
        So the error is measured against the perpendicular that points at
        the line, in the range -180..180.
        """
        import math
        to_line = math.degrees(math.atan2(self.line_point[1] - self.y,
                                          self.line_point[0] - self.x))
        # Nearest perpendicular to the line, on the side the robot faces.
        best = None
        for candidate in (self.line_angle + 90.0, self.line_angle - 90.0):
            facing = (candidate - to_line + 180.0) % 360.0 - 180.0
            if best is None or abs(facing) < abs(best[1]):
                best = (candidate, facing)
        error = (self.theta - best[0] + 180.0) % 360.0 - 180.0
        return error

    def sensor_line_state(self):
        readings = self.get_line_sensors()
        return tuple(r is not None and r > 200 for r in readings)
