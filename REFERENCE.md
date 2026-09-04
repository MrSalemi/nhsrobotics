# NHS Robotics — Reference

Durable knowledge: how the guides get built, what the course teaches and why,
what the hardware actually does, and the failures that don't announce
themselves. Current state is in [PROJECT.md](PROJECT.md); settled calls are in
[DECISIONS.md](DECISIONS.md). Nothing here is a status report.

## Guide production

Guides are **generated from the markdown in `nhsrobotics/guides/`**, and
the guide that gets printed is a **PDF**. Word is not in the chain at all: a
`.docx` is built in a temp folder, converted, and deleted. There is no editable
copy of a guide anywhere, which is the point — an edit that is not in the
markdown cannot survive, so it cannot be made by accident.

**Content and builder are separate folders.** `guides/` holds the markdown,
`images/`, `course.js`, `deploy.txt` and the built PDFs. `shared/` is the
builder — `MrSalemi/vault-shared`, **shared with `nhsengineering` and
`advrobotics`** — and holds no guides, no pictures and no course text.

**`shared/` is a symlink to `../shared`, not a submodule.** The builder is
cloned once at `~/vaults/shared` and every vault links to it, so an edit is one
commit in one repo and every vault sees it at once. All vaults live directly
under `~/vaults/` on both machines, which is what makes the relative link work
across two different account names. See [DECISIONS #45](DECISIONS.md). If
`shared/build-all.sh: No such file` appears on a new machine, `~/vaults/shared`
has not been cloned yet.

Run the build from `guides/`.

```bash
cd guides
../shared/build-all.sh p05.md -d   # build one guide and deploy it
../shared/build-all.sh -d          # build every guide that needs it, deploy
../shared/build-all.sh -f          # rebuild everything, current or not
node ../shared/test-build.js       # the builder's own test suite
```

The builder needs `node`, `soffice` (LibreOffice) and `pdftoppm` (Poppler) on
`PATH`, plus `shared/node_modules` — `cd ~/vaults/shared && npm install` once
per machine.

The words behind `{{SAVE}}`, `{{PARTA}}` and `{{GRADING}}` are in
`guides/course.js`, not in the builder — a shared builder cannot carry one
course's grading rule. It is called with the guide's frontmatter, which is how
`SAVE` gets the project number and scaffold name.

**A guide is only rebuilt when it is stale**, the way make works: its markdown,
one of its pictures, or the builder itself is newer than the PDF. Pagination is
measured by running the file through LibreOffice, which is slow, so this is the
difference between a minute and a second.

Deploying writes into Google Drive. A PDF open in a viewer is only being read,
so it will not make a conflicted copy the way an open Word file could.

`node ../shared/test-build.js` from `guides/` checks the builder — no
robot and no Word, building into a temp folder so it never touches a deployed
guide. Run it after any change to `build.js`, `parse.js` or `make.js`.

[shared/README.md](shared/README.md) explains the builder itself. Rules that bite:

- **Images must be real PNGs.** The builder reads the PNG header and refuses
  anything else. A JPEG renamed `.png` fails the build. Crop tight, export
  around 300–500 px wide.
- **A picture is capped at 6.5 × 4.5 inches**, proportions kept. Height was
  uncapped until 2026-08-12, which is how an oversized canvas used to eat a
  sheet without saying so.
- **A picture carries `keepNext` only when the next block is not a picture.**
  `keepNext` glues a paragraph to the one after it, so a run of pictures used to
  chain into a single unbreakable block — and a block taller than a page shunted
  the whole run to the next sheet and left the current one empty. Found in the
  engineering guides, fixed in both builders. See
  [DECISIONS #40](DECISIONS.md).
- **Length costs sheets, not pages.** Printing is double-sided and odd page
  counts are padded, so 7 and 8 pages are both 4 sheets. Only an even-to-odd
  crossing matters.
- **A link prints as its label and nothing else**, and a bare `[[p03]]` is
  refused by the build because it would print a filename at a student. Links
  between guides belong in the `related` property, which is never printed. See
  [DECISIONS #39](DECISIONS.md).

### Where the rebuild stands

| Project | Guide | Scaffold | Solution | Ray approved |
|---|---|---|---|---|
| P00 First Lights | V01 | V01 | V01 | **new, never run on a robot** |
| P01 Gamepad Lights | V10 | V04 | V02 | yes |
| P02 Flashing Lights | V15 | V06 | V06 | yes |
| P03 Gamepad Driving | V08 | V04 | V03 | yes |
| P04 Drive to the Wall and Back | V06 | V04 | V06 | **not yet** |
| P05 Around the Cone | V03 | V01 | V01 | yes |
| P06 The Magic Circle | V01 | V01 | V01 | runs on hardware; guide reviewed |
| P07 The Parking Sensor | V08 | V01 | V01 | **never run on a robot** |
| P08 The Security Bot | V04 | V03 | V03 | **never run on a robot** |
| P09 The Sumo Bot | V01 | V01 | V01 | **never run on a robot** |
| Line alignment (Term 2) | — | — | `sol1x` | works obliquely, poorly near square |

**P01–P03 and P05 are the reference set.** Match those, not the older files.

## What the course teaches, and why

Ray's own words: *"I have a tendency to want to teach them a bunch of cool
things the robot can do, but then lose the thread in terms of why."* This is the
thread.

### The movement API is only two ideas, at two levels

| | Per wheel | Per robot |
|---|---|---|
| **Set a speed** (runs forever) | `set_wheels_speed()` | `drive()` |
| **Set a destination** (stops itself) | `set_wheels_position()` | `move()`, `rotate()` |

**The question that picks the method: does the robot need to pay attention while
it moves?** `move()` and `rotate()` block — the robot is deaf and blind until it
arrives. `drive()` returns instantly, so your code stays free to watch
something. That is a real engineering idea, not robot trivia.

- **`move()` / `rotate()`** — you know where you are going and nothing on the way
  can change your mind. Accurate, self-correcting, one line. For a beginner
  usually the right answer.
- **`drive()`** — the robot must keep its eyes open (stop at a wall, follow a
  line, turn until a sensor fires, respond to a controller), or you need a
  **curve**, which nothing else can do.
- **`set_wheels_speed()`** — conceptual value only. Two motors, two numbers, no
  abstraction; it is how a student *feels* a differential drive. P03's gamepad
  mapping is perfect for it. Teach once, never return.
- **`set_wheels_position()`** — no classroom use anyone could construct. Cut.

Also cut: the `'%'` angular unit. The constant behind it was broken, and
percent-of-max teaches nothing cm/s does not.

### What each project adds

| | What it adds |
|---|---|
| P03 | Two motors, two numbers. Feel the hardware. |
| P04 | Watch a sensor while moving vs. go somewhere blind — both families, contrasted in one project. |
| P05 | The second argument. Curves. Tune by trial. |
| P06 | The pose. Let the robot measure itself instead of tuning. |

Each is "here is a new thing worth watching," not "here is another command."

## Project design rationale

### P05 Around the Cone

A port of Ray's PRIZM "Turning the Robot" project, which his students enjoyed.
Foamboard course: start box, drive out, curve 180° around a cone, drive back,
park in a box level with the start box.

- WORK 1 straight out, WORK 2 the arc (`drive()` with both arguments — the new
  idea), WORK 3 straight into the box. One tuned number per leg.
- **FLEX:** the boxes are level, so leg 3 equals leg 1. Read the pose after leg 1
  and use `alvik.move(distance_out)` instead of a tuned time. The guide points at
  P04 rather than printing the code.
- **No pose anywhere in the WORK.** P05 is pure tuning; the pose is P06's reveal.
  Pain before the fix, at the project level.
- Per-student speed comes from a **formula, not a list**: multiply your student
  number by 5, subtract 41 until under 41, divide by 10, add 4. Twenty-four
  distinct values, 4.3–8.0 cm/s, no two adjacent closer than 0.5.
- Board geometry fixes the arc radius at 12 cm (boxes 24 cm apart, centre to
  centre). That is what makes the random speed do work — each student must find
  their own turn rate.

### P06 The Magic Circle

The robot hides an invisible ring on the floor within 100 cm of itself, 20 cm
across. The student drives with the P03 gamepad and finds it using only the
feedback they build. Roll inside and the robot brakes, spins to celebrate, and
hides a new one.

**The thing being taught is not the pose. It is translating information into
feedback a person can act on.** Ray's words. Three WORK items, three
translations: number → screen (Pythagoras on the two offsets, distance on the
OLED); sign → two lights (light the LED on the side the ring is on, both off
when aimed); number → colour (Nano LED red when hot, blue when cold). The dance
and the next ring are **given**, because an outcome is not a translation.

**FLEX: an autopilot on a held button.** Hold `R1` and the robot hunts the ring
itself; release and the sticks are back. Purely additive —
`set_wheels_speed()` is an order rather than a setting, so a second call later
in the same loop pass overrules the first, and with R1 up the block never fires.
An earlier version had students *replace* the tank drive with autonomous code,
which breaks the additive rule. **Do not go back to that.** This FLEX is also
the on-ramp to autonomous Sumo.

**`Circle` is defined in the student file**, not in `nhs_lib` — a curious student
can read it and nothing has to be imported. API: `circle = Circle(max_dist,
diameter)` then `dir, dx, dy = circle.get_bearings()`, with dir 1 left, −1 right,
0 aimed.

**No trigonometry reaches the student.** The class computes the relative bearing
internally and returns only a sign, which needs `sin` and `cos` but never
`atan2` — and because no angle is produced there is no ±180 wrap, and unbounded
theta passes straight through since `sin` is periodic. Students write Pythagoras
and a colour proportion, which are 8th-grade maths they own.

`MAX_DIST_CM` 100, `TOLERANCE_DEG` 6, `RING_DIAMETER_CM` 20. The tolerance is
divided by distance, so the aimed window is a fixed number of degrees and a
shrinking number of centimetres as the robot closes — 10 cm of slack at a metre,
2 cm at twenty. What would break the game is a tolerance too tight to hold with
tank-drive sticks; 6° is a 12° window.

**Why it is immune to the hardware defects.** Nothing depends on an accurate
distance or angle. The ring exists only in the robot's own pose frame, so there
is no physical ring for a drifting pose to disagree with, and the student is the
control loop.

**Two gaps in the guide, Ray's call, not made:** Part 1 never says the file
already gives you the tank drive (and that it came from P03), and never says it
already calls `reset_pose()` before the first ring.

### The Security Bot (P08)

Patrol on green at 10 cm/s. Anything inside `SPOT_CM` (60) and the robot goes
red and advances at 6 cm/s — slow is the menacing part. Then exactly two things
can happen to the gap while the robot keeps rolling: it opens past `FLED_CM`
(90) because the target backed off faster, or it shuts inside `STUBBORN_CM`
(15) because the target never moved. There is no third case. A target that
bolts out of the room sends `get_closest_distance()` to 999, so the fast escape
and the slow one are the same test.

**The argument for the state variable is not the reading, it is the sentence.**
"It did not flee" is a fact about what happened *while* the robot was doing
something. A program that only sees this instant cannot say it, however many
`if`s you give it.

The retreat — `rotate(135)` then `move(50)` — **blocks**, which is the opposite
of P07's rule and right for the opposite reason: the robot has decided to leave
and nothing it could see would change that. 135 rather than 180 so it does not
retrace its own path; a robot that always reverses runs the same line forever
and bounces between two walls in a corner.

**FLEX is a fifth state, `PEEKING`:** turn back, look, and run again if the
clown followed. Its turn is 180, not `RETREAT_TURN_DEG` — reusing 135 leaves
the robot looking 90 degrees off the path it just ran.

### The Sumo Bot (P09)

Black ring floor, white rim about 3 inches wide, robots started by a CROSS
press on the gamepad — the gamepad is read in a GIVEN loop before the match and
never during it, so a flat controller costs a start and not a bout. Three
states: PATROLLING at 50 RPM, TURNING (back off `BACKUP_CM` then turn), and
ATTACKING at 70 RPM inside `ATTACK_CM` (3).

**The edge test is a guard above the elif tree, not a transition inside one.**
It takes effect on the same pass, which is the point and is exactly what P08
taught transitions do not do. Consequences worth keeping:

- The screen write must sit BELOW the guard. Above it, a state the guard sets
  and the tree clears on the same pass is never displayed at all.
- A robot cannot win itself out of the ring. Shove an opponent over the rim and
  the winner is standing on the rim, so the guard fires before the attack
  branch. Nobody writes that case.
- The margin from first white to falling out shrinks in proportion to speed,
  and attack speed is exactly when a robot is least interested in looking down.

`edge_detected()` and `waiting_for_gamepad()` are given at the top of the
student file, not in `nhs_lib` — the P06 `Circle` precedent. Students never
touch the line sensors in this project.

**Two given helpers, three states, and a deliberate hole:** two robots meeting
head-on both charge and neither moves. That is where a student's own state, and
the podium, are won.

### Line alignment (Term 2)

Ray's design, and the version that works on hardware: drive until the **centre**
sensor sees the line, brake, settle, reset the pose, then spin — using the two
outer sensors only to pick the spin direction. The centre sensor's reading
rises as it goes deeper onto the tape and falls again on the way out, so the
sweep ends when it drops back through the threshold, and half of that sweep is
the correction.

- **Never `alvik.rotate()` in this project.** Every turn watches something.
- **Why there is no maximum approach angle.** A sensor's distance to the tape
  peaks when the robot is turned so that sensor points straight at it. For an
  OUTER sensor that peak is `atan(spacing / forward offset)` off square, and
  past that tilt the sweep stops at the near crossing and saturates — the robot
  reports the same angle however crooked it started. The centre sensor sits on
  the centreline, so its peak is exactly square and the two crossings are
  symmetric for any approach. Both endpoints are also the same threshold on the
  same sensor, so a threshold offset cancels the way the odometry scale does.
- **Why it is worst near square.** Sensitivity to any error in the tape's
  distance goes as `1 / sin` of the approach angle. At 40 degrees a few
  millimetres of brake coast cost almost nothing; near square they cost a lot.
  Both coasts — the forward one before the pose is zeroed and the rotational
  one at the end — push the correction the same way, so the robot over-turns.
- **Measured 2026-08-09**, marker on white paper: white about 50, a sensor on
  the line 300-650, and during rotation all three swing between 50 and 350.
  `LINE_THRESHOLD` 150 is safer than 200 — it is 100 above paper, so it trips
  while the sensor is still at the EDGE of the tape rather than on it, which is
  what lets a small turn pull it back under.

  **Neither number is in any file.** 2026-09-04: `LINE_THRESHOLD` is defined
  nowhere in the repo — [DECISIONS #21](DECISIONS.md) settled 200, the
  paragraph above prefers 150, and the parked `sol1x` does not set it. The
  only live threshold on a line sensor is P09's `EDGE_THRESHOLD = 200`, which
  is a different measurement on a different surface. Pick one when the
  project comes back, and put it in the file.
- **The spin starts one wheel at a time.** In `set_wheels_speed(S, -S)` the
  positive wheel moves first, so for that gap the robot pivots about the
  stationary wheel rather than the axle midpoint. Lands in the measured sweep.
- **The sensor geometry has never been measured.** The testbench assumes 5.0 cm
  forward and ±1.5 cm apart. Both invented. They do not affect the halving,
  which needs only symmetry, but they set the range over which halving is valid.

## Hardware truth, measured

Measured over 2026-08-03 and 2026-08-04 on three robots of different ages.

- **`drive()` delivers 92.6% of what you ask, in both axes**, plus a 0.21 s
  startup lag. Same on all three, so it is firmware, not wear. Almost certainly a
  time-base error in the STM32 velocity loop; the physical geometry measures
  correct.
- **`move()` is accurate** — 495 mm on a 500 mm command.
- **`theta` from `get_pose()` is wheel odometry. `yaw` from `get_orientation()`
  is the IMU. They are separate packets and never touch.** Proven by lifting the
  robot and turning it by hand (yaw moves, theta does not) and by spinning the
  wheels in the air (theta climbs, the robot has not moved).
- **theta over-reports rotation by 8–13%** against yaw as ground truth. On one
  spin the robot physically turned about 146° on a 180° command while theta
  claimed 163°. Wheels measure 33 mm and the track 88 mm, which predicts only a
  3% over-report, so **geometry does not explain it** — the residual is in the
  STM32 binary. The Python constants are documentation; the firmware has its own.
- **yaw does not drift** — parked two minutes, no creep. It is the only heading
  source no wheel error can touch. But **yaw is 0–360 and it wraps** (observed
  358.8 → 359.2 → 4.6), so any use of it needs unwrapping.
- **Negative angular velocity turns right**, positive turns left.
- **`brake()` stops in about 0.5 s** — 6 mm at 4.6 cm/s, 6.4° at 36 deg/s.
- **The pose origin is the midpoint of the wheel axle**, not the nose. Proven by
  a spin log: x and y sat at 0.0 through a full rotation.
- **The pose keeps integrating under `set_wheels_speed()`**, not just `drive()`.
  Mixing `'J'` and `'V'` packets in one program is fine — P06 does it.
- **`ROBOT_MAX_DEG_S` was exactly 2× too big**, and the fix is fragile. See
  below.

### The `ROBOT_MAX_DEG_S` fix, and why it keeps getting lost

**There is only one copy of the Alvik library on disk.**
`nhs_lib/arduino_alvik` is a *symlink* to
`../libs_on_github/arduino-alvik-mpy/arduino_alvik`, so the library the robots
run and the fork submodule are the same file. Earlier notes claiming the fix was
applied to "both working copies" were wrong — there is one, and touching the
submodule changes what deploys.

The correct line in `arduino_alvik/robot_definitions.py`:

```python
ROBOT_MAX_DEG_S = 6*(MOTOR_MAX_RPM*WHEEL_DIAMETER_MM)/WHEEL_TRACK_MM
```

- `git submodule update` in the parent is the repair: it checks out the SHA the
  parent records, which is the good commit.
- **Never commit the parent while `git status` reports the submodule modified**
  without reading `git diff --submodule=log` first. `(rewind)` with a `<` line
  means you are about to record the regression.
- Before any classroom deploy:
  `grep ROBOT_MAX_DEG_S nhs_lib/arduino_alvik/robot_definitions.py` — there must
  be no `2*`.
- The fix has never been filed as a PR upstream, and may still need pushing to
  the fork's `main`.

### Two standing rulings

**Students never see the velocity error.** Do not teach it, do not compensate for
it in `nhs_lib`, and **never write a step of the form "drive for N seconds" that
asks a student to compute the time.** Tuning a time by hand is fine — the error
gets absorbed and never surfaces, which is exactly what P05 does. Hide it through
project design.

**No calibration program and no per-robot constant on the filesystem.** The real
error is an unexplained residual that differs between the linear and angular
axes, sits in a binary nobody can read, and comes with a 0.21 s lag. Hidden
per-robot state fails silently and differently on 24 shared robots, and gets
stomped every time a student breaks `main.py`. If calibration ever belongs in the
course it is a project, not plumbing.

### Top speed

**70 RPM on a 34 mm wheel is 12.46 cm/s**, from `MOTOR_MAX_RPM` and
`WHEEL_DIAMETER_MM` in `robot_definitions.py`. `drive()` delivers 92.6% of
what is asked, so the usable ceiling is **somewhere between 11.5 and 12.5
cm/s** — which of those depends on whether the deficit applies before or
after the motors run out of RPM, and that has not been measured. Treat 11.5
as the safe number.

This is what caps every physics activity: an accelerating run from rest
covers at most **6.25 cm per second of runtime**, so distance is bought with
time and nothing else. See [DECISIONS #49](DECISIONS.md).

### Still unmeasured

- **How the base follows a *changing* speed setpoint.** The 0.21 s below is
  a startup lag from standstill; nobody has watched the robot track a ramp.
  `tests/tb/plant.py` now assumes a first-order response with that same time
  constant — see [DECISIONS #51](DECISIONS.md) — and
  `init_bot/phy_robot/accelerator.py` rests on it entirely. One bench run
  settles it: command a ramp, log the pose.
- **`rotate()` has never been tested.** Accuracy is inferred from `move()`.
  P04's WORK 3 depends on it.
- **`drive()` with both arguments has never been tested.** Prediction: the curve
  radius is right even though the traverse is 7.4% slow, because the radius is
  forward ÷ turn and the error cancels. P05 rests on this, and P09's curved hunt
  patterns now do too.
- **Saturation behaviour is unknown.** Budget rule: `forward + turn ÷ 13 ≤ 12.5`
  in cm/s and deg/s. Nobody knows what the firmware does past that.

`init_bot/factory_alivk/` is an archive — a dump of what was inside a robot out
of the box, including an older library with the old constant. Nothing references
it. **Leave it alone.**

## Failures that don't announce themselves

**A dangling symlink in a robot source tree deletes files off the robot.**
`initialize_robot.sh` decides a remote file is stale with `[ -d ]` and
`[ -f ]`, both of which follow links, so an unchecked-out submodule reads as
"deleted on purpose". On 2026-09-04 that removed the whole Alvik driver from
a robot and reported success. v31 refuses to start on a broken link —
[DECISIONS #52](DECISIONS.md) — but the lesson generalises: **a symlink is a
claim about something else, and a tool that resolves it cannot tell a broken
promise from a deliberate absence.**

**A flat controller battery.** A dying PS4/PS5 controller does not raise.
~~`RobotController.update()`~~ — 2026-09-04: the class is `Controller`, in
`nhs_lib/controller.py`. There is no `RobotController` anywhere in the repo
and never was; the behaviour below is accurate, only the name was wrong.
`Controller.update()` opens with `if not self.is_connected():
self._reset_state()`, which zeroes every stick and clears every button, and the
socket path catches `OSError` and calls `_close_ws()`. Nothing propagates. The
symptom is a robot that quietly stops driving while everything else in the loop
keeps running. **When a gamepad project mysteriously stops driving, check the
battery before the code.** A `try`/`except` around the gamepad read is useless
here — one was added and reverted the same day.

**`is_connected()` is closed.** Polling it is the only real fix and Ray ruled it
not worth the trouble: it would mean reaching through `gamepad.controller.`,
worse than the banned `sb.<subthing>.method()` shape, and it reverses the
decision to pull `is_connected()` out of the student-facing API. P01 and P03 have
the same silent behaviour and that is accepted. **Do not propose it again.**

**A dead OLED shows nothing and raises nothing.** `RobotUI.__init__` catches an
init failure and leaves `self.screen` as `None`, after which every
`update_display()` call quietly does nothing. The screen works and Ray uses it
constantly — but a robot with a loose display will run a whole program with a
blank screen and no error.

## `dev/` and tests

`dev/` holds bench programs, not student projects: `pose_source_test.py` (proves
theta and yaw are different sources, on the OLED with no cable) and
`curve_pose_test.py` (measures `rotate()`, `drive()` with both arguments, and
whether pose y survives a curve — **never run**), plus Ray's own
`approach_box.py`, `capstone.py`, `capstone_student.py`, `face2d.py`,
`line_sensor_probe.py`, `rolling_superbot.py`, `state_approach.py`.

Four programs an earlier handoff listed — `spin_rate_test.py`,
`spin_ramp_test.py`, `straight_line_test.py`, `turn_sign_test.py` — are **not in
the repo** and git shows nothing deleted. The 2026-08-03 measurement code may
exist only on a robot. **Do not gitignore `dev/` itself.**

```bash
python3 tests/run_host_regression.py    # no robot needed
```

Any change to `nhs_lib` needs a test in `tests/regression_host.py` and a line in
both runners.

## Deploying to robots

`./initialize_robot.sh -d init_bot/nhs_robot -c` per robot. `lib@` and
`projects@` are symlinks into the live repo, so library and scaffold changes flow
automatically. The script deletes anything on the robot that no longer exists
locally, which clears stale old-numbered files. `-c` also wipes `/workspace` —
safe only while no student work exists.

**`-c` is also what resets `main.py`.** Without it the sync keeps whatever
`main.py` is already on the robot, on purpose — from P04 on it is the
student's file. So a change to the shipped `main.py` does not land unless
`-c` is passed.

**Four source trees, one library.** `init_bot/` holds `nhs_robot`,
`phy_robot` and `eng_bot`, all three pointing `lib` at `../../nhs_lib`, plus
the `factory_alivk` archive. Only `nhs_robot` also links `projects` and
`tests`, so syncing `phy_robot` to a robot that was set up for robotics
correctly removes the project scaffolds — and incidentally clears the
stale `tests/tb` from that one robot.

**v31 refuses to start on a broken symlink in the source tree** —
[DECISIONS #52](DECISIONS.md). If it stops with a list of dead links, run
`git submodule update --init --recursive` from the repo root. That works with
no network, because the objects are already in `.git/modules`, which matters
at school.
