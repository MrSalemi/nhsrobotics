# NHS Robotics — Project

Home folder for the robotics curriculum. Three files:

- **`STATUS.md`** (this file) — what is being worked on right now.
- **[DECISIONS.md](DECISIONS.md)** — settled calls, numbered and permanent.
- **[REFERENCE.md](REFERENCE.md)** — durable knowledge: guide production, what the course
  teaches and why, measured hardware behaviour, and the silent failure modes.

## Where these live, and why it matters

**These three files live in `nhsrobotics`, the robotics repo.** Ray moved them
here on 2026-08-09, out of `Class Development`.

The reason is the rule, not the tidy-up: **`Class Development` holds more than
one class.** Physics and Engineering are in there too, and each class needs its
own threads and its own history. A single `PROJECT.md` at the top of a folder
shared by three courses would mix them, and a thread about Physics would open
by reading the state of Robotics.

So: **never put `STATUS.md`, `DECISIONS.md` or `REFERENCE.md` in
`Class Development`.** Each class keeps its own set, in its own home.

## Folders involved

- **`nhsrobotics`** (`~/vaults/nhsrobotics`) — **this folder, and home
  for the project.** The code: student scaffolds in `projects/`, reference
  answers in `solutions/`, the shared library in `nhs_lib/`, guide source in
  `guides/`, the builder symlinked as `shared/`, the
  testbench in `tests/`. Guides are generated from the markdown in `guides/`
  and never hand-edited. **The
  repo is also the Obsidian vault** — see [DECISIONS #35](DECISIONS.md).
- **`~/vaults/shared`** — the guide builder, `MrSalemi/vault-shared`, cloned
  once and linked into every vault. Not a submodule — see
  [DECISIONS #45](DECISIONS.md). Every vault lives directly under `~/vaults/` on
  both machines so that `../shared` resolves the same way on each.
- **`Class Development`** — the documents, and NOT home. Deployed robotics
  guides land in `Robotics/Project Guides/`, retired old-voice guides in its
  `Previous Versions/`, capstone specs and the pacing plan under `Robotics/`,
  and the school calendar at the top level. Physics and Engineering also live
  there and are out of scope for this project.

  It is one Drive folder owned by `rdsalemi@gmail.com` and shared to
  `rsalemi@natickps.org`, so its local path differs per machine — `My
  Drive/Teaching/Class Development` at home, `.shortcut-targets-by-id/<id>/Class
  Development` at school. The builder finds it by searching rather than by a
  stored path; see [DECISIONS #45](DECISIONS.md).

**The Cowork project mounts exactly these three, and nothing else:**

```
nhsrobotics          the work
shared               the builder, reached from the vault by symlink
Class Development    where -d deploys
```

**`Classroom` is not `Class Development`.** Google Drive holds a separate
`My Drive/Classroom`, and adding that one instead leaves a thread unable to
deploy while everything looks mounted. On 2026-09-04 a thread spent several
exchanges on this. If `ls` on the mount root shows `Classroom` and no
`Class Development`, the wrong folder is in Context.

A Context folder added mid-thread does not appear — the mount set is fixed
when the session starts. Change it, then start a new thread.

`shared` has to be its own entry. The vault reaches it through
`shared -> ../shared`, and a symlink resolves only to something that is also
mounted — mounts land side by side under one root, so `..` from inside the
vault finds the others.

`Class Development` is needed only because a *thread* deploys. `build-all.sh`
searches `$HOME/Library/CloudStorage` and `/sessions/*/mnt`; on Ray's Mac the
first finds it, but in a thread's sandbox `$HOME` has no `Library`, so only the
mount can match. Drop it from Context if deploying becomes Ray's job alone.

~~Mount `~/vaults` rather than a single vault.~~ — 2026-08-30: superseded. A
Cowork project takes several Context folders, so the three above are named
directly. Mounting `~/vaults` also works but hands every project all five
courses and lists `nhsrobotics` twice.

## Sandbox setup

Nothing per-session. Per *machine*, the guide pipeline needs `node`, `soffice`
(LibreOffice), `pdftoppm` (Poppler), `mpremote`, the **Carlito** font, and
`~/vaults/shared/node_modules` from one `npm install`. Both of Ray's Macs were
brought to matching versions on 2026-08-30. **The school network blocks npm and
GitHub**, so anything needing a download has to happen at home.

Full list with verified versions, and why each is needed, is in
[shared/TOOLS.md](shared/TOOLS.md) §3. Check any machine with:

```bash
for t in node npm git soffice pdftoppm mpremote; do
  printf "%-12s " "$t"; command -v $t >/dev/null && echo ok || echo MISSING
done
printf "%-12s %s\n" carlito "$(fc-list | grep -ic carlito) faces (want 4)"
[ -d ~/vaults/shared/node_modules ] && echo "node_modules ok" || echo "node_modules MISSING"
```

~~The fonts Carlito **and Roboto Mono**.~~ — 2026-08-30: Roboto Mono is no
longer used. See [DECISIONS #46](DECISIONS.md).

`build-all.sh` now catches a missing `node_modules` itself and prints the
command, instead of dying in a node stack trace.

## Current unit

**This repo also carries the Physics and Engineering robot payloads.**
`init_bot/` holds four source trees — `nhs_robot`, `phy_robot`, `eng_bot`
and the `factory_alivk` archive — and all three live ones point `lib` at
the same `../../nhs_lib`. So a physics program is built and synced from
here even though the physics *course* lives in the `physics` vault. As of
2026-09-04 `phy_robot` boots into `accelerator.py`, the lesson 1.8
constant-acceleration activity; `marsRoverDrop.py` is still on the robot
and is wanted later.

**P00 First Lights is new, and P07-P09 have still never been run on a robot.**

P00 was written 2026-08-29 as a day-one project that needs nothing but a USB
cable — no WiFi, no browser, no Bluetooth, no controller. Four steps in one
loop: left red / right green, swap, both yellow, dark. The one real idea is
that yellow is not on the list of colors and has to be made from red plus
green. The three setup lines are GIVEN here and typed by hand in P01.

Numbering it zero was deliberate — nothing above it moved, so no guide, scaffold
or cross-reference was renumbered.

**P00 is on the robots and its guide is deployed.** It has not been taught, and
it is not in the calendar.

| # | Project | State |
|---|---|---|
| P00 | First Lights — two LEDs, a pattern, and a USB cable | Guide V01, scaffold V01, solution V01. Deployed and on the robots. Never taught. |
| P07 | The Parking Sensor — seconds on the OLED, blink rate from distance, then drive | Guide V08, scaffold and solution written. Never run on a robot. |
| P08 | The Security Bot — patrol, advance, and run away. Introduces the state machine | Guide V04, scaffold V03, solution V03. Never run on a robot. |
| P09 | The Sumo Bot — patrol the ring, charge, and never fall out | Guide V01, scaffold V01, solution V01. Never run on a robot. |

**P08 is no longer the line-sensor project.** Line alignment moved to Term 2 —
see [DECISIONS #26](DECISIONS.md). Its solution is parked at `solutions/sol1x_line_alignment.py`.

Ray is designing **only** through P09. P10 onward get decided in October, after
he has run the class. Do not spend design effort past P09, and do not use any
P10+ project as an argument about P07-P09 — those slots may be rewritten or cut.

## What's done

**2026-09-04 — the physics accelerator, and the sync stopped deleting the
robot's driver.**

- **`init_bot/phy_robot/accelerator.py` V01 is written and on one robot.**
  Physics lesson 1.8: marks at 10/20/30/40/50 cm beside a metre stick, the
  robot's own touch pads for UP, DOWN and CANCEL, no OLED, brake at 52 cm so
  neither run stops on a mark somebody is timing. UP runs from rest at
  +0.010 m/s², DOWN from 0.080 m/s at −0.005 m/s². Both numbers were forced
  by the robot's top speed and by Ray's requirement that the two runs not be
  mirrors — see [DECISIONS #49](DECISIONS.md). `phy_robot/main.py` now
  imports it instead of `marsRoverDrop`.
- **It steers on the pose rather than commanding speed.**
  [DECISIONS #50](DECISIONS.md). Simulated times land within 0.09 s of the
  profile at every mark, which is inside what a student can read.
- **`tests/regression_accelerator.py`** — eleven checks, every one
  mutation-tested, folded into `run_solution_regression.py` and therefore
  into the host suite. Solution suite is 24 pass / 9 skip; host is 35 / 9.
- **The testbench's model of the 0.21 s lag changed.**
  [DECISIONS #51](DECISIONS.md). It used to stop the robot dead for 210 ms
  after *any* command change, which makes a ramp impossible. It now slews.
  `plant.py` also gained a `max_speed_cms` knob, because without one the sim
  accelerates forever and a profile that saturates on the real floor passes
  every check.
- **`initialize_robot.sh` is v31 and refuses to run on a broken symlink.**
  [DECISIONS #52](DECISIONS.md). Its banner also said v29 while the header
  said v30; fixed. Four laptop-side checks in
  `tests/regression_initbot.py`, one of which reads the three real source
  trees as they sit on disk.

**Nobody has run `accelerator.py` on the floor.** Everything above is
simulated.

**2026-08-29 — the builder stopped being a submodule, and the guides got their
fonts and spacing settled.** A long session; the detail is in DECISIONS #45 and
#46. In short:

- **`shared/` is a symlink to `../shared`, one clone at `~/vaults/shared`,
  linked into all five vaults.** A submodule is right for code you consume and
  wrong for code you author — every builder edit had cost two commits in two
  repos plus a pointer bump per vault, on top of a preflight for detached HEAD,
  missing fetch refspec, and a stale checkout. [DECISIONS #45](DECISIONS.md).
- **The builder finds Class Development by searching** `~/Library/CloudStorage`
  for the folder named in `deploy.txt`, which now holds the whole path
  (`Class Development/Robotics/Project Guides`). One line works on a machine
  that owns the folder and on one that reaches it through a shortcut.
- **Guides are set in Carlito and Courier New, at 1.2 line spacing.** Both
  earlier choices — Calibri and Roboto Mono — rendered differently on Ray's two
  Macs, and the Roboto Mono failure was silent: school fell back to a serif
  *proportional* face for code and the build reported success.
  [DECISIONS #46](DECISIONS.md).
- **`guides/worksheet.js` had been broken since 2026-08-16**, still pointing at
  `../builder/` after the move to `shared/`. Fixed.
- **All ten guides plus the worksheet rebuilt and deployed** from one machine,
  so Drive is internally consistent for the first time today.

**2026-08-30 — the builder documents and defends itself.** Same session, into
Sunday morning.

- **[shared/TOOLS.md](shared/TOOLS.md) is new** — the operator manual, as
  opposed to `README.md`'s user manual. Every tool and how it is invoked, what
  makes a guide stale, how to add a check, the external programs and fonts with
  verified versions, how deploy finds Class Development, and the push gate. It
  ends with a list of everything that has bitten. `start-thread` now reads it.
- **`shared/preflight.sh` is the gate, and a `pre-push` hook runs it.** It
  checks the tools, checks the installed tree matches `package.json` the way
  `npm ci` will on the runner, then runs the suite twice: as the machine is, and
  with `NO_SOFFICE=1`, which is what CI sees. **`build-all.sh` wires the hook
  itself** on the first build after a clone, so there is nothing to remember.
- **The GitHub Action was red and is green.** A check added with the `folder:`
  feature ran a real `-d` deploy, so it needed LibreOffice, which the runner
  deliberately does not have. PDF-dependent checks now report `SKIP` by name.
  The workflow also moved off node 20, which GitHub has deprecated.
- **Two silent bugs found and fixed.** `math.js` was missing from
  `BUILDER_FILES`, so editing it left every guide reporting "up to date" and the
  change never appeared. And a check hunted for tools in a hardcoded list of
  directories, which stopped finding `node` the moment it moved to Homebrew —
  it then withheld node from its own fixture and failed naming the wrong tool.
- **`start-thread`, `close-out-thread` and `save-memory` take the vault from
  the project instructions** rather than scanning for `STATUS.md`. Scanning
  found one when a single vault was mounted and five when `~/vaults` was; the
  project already knows which course it is. Named, or ask — see
  [DECISIONS #47](DECISIONS.md).

- ~~**The builder is now a shared submodule at `builder/`**, the same repo and
  the same commit Engineering uses~~ — 2026-08-29: superseded. It is a symlink
  to a sibling clone now, not a submodule, and the path is `shared/` not
  `builder/`. See [DECISIONS #45](DECISIONS.md). The rest of #43 still stands:
  `guide_builder/` is gone, the guides and their pictures are in `guides/`, and
  one builder serves every course. [DECISIONS #43](DECISIONS.md).
- **The worksheet is generated and deployed with the guides.**
  `guides/worksheet.js` is the source and writes
  *Robotics_Project_Worksheet.pdf*; `guides/extras.txt` gets one
  `build-all.sh -d` to remake and deploy the guides and the worksheet together.
  It used to exist only in Drive as a `.docx`, with no source anywhere.
  [DECISIONS #44](DECISIONS.md).
- **P01-P06 are rebuilt and in the new voice.** Version and approval status
  live in [REFERENCE.md](REFERENCE.md) in this folder. P04 is rebuilt but Ray has not
  approved it.
- **The fall calendar was read directly** (`Red Blue 2627 Calendar.xlsx`,
  sheet `Schedule`, column G "Robotics Red 1"). It contains exactly twelve
  entries: Out of School 8/26; P01 Due 9/01; P02 9/08; P03 9/14; P04 9/18;
  P05 9/25; P06 10/01; **P07 10/09; P08 10/16; P09 Sumo Battles 10/26 and
  10/28**; End of Term 1 10/30. There is **no P10 anywhere in the calendar.**
- **Term 1 is 22 Red class days, 8/28-10/30** — counted from the sheet.
- **P09's build window is two periods**, 10/20 and 10/22, with the battles on
  10/26 and 10/28. Every other project in the course also gets two periods;
  P07 gets three.
- **P07 is written and built.** Named *The Parking Sensor*. Guide V08 deployed to
  Project Guides at 8 pages (4 sheets), `projects/p07_parking_sensor.py`,
  `solutions/sol07_parking_sensor.py`. WORK 1 is now a seconds clock on the OLED,
  not a distance readout — see [DECISIONS #18](DECISIONS.md). **Nobody has run it on a robot.**
- **P08 The Security Bot is written.** Guide V04 at 8 pages (4 sheets),
  `projects/p08_security_bot.py`, `solutions/sol08_security_bot.py`. Four
  states, one elif tree. The retreat blocks on `move()`/`rotate()` because
  nothing needs watching during it — [DECISIONS #28](DECISIONS.md). The FLEX is a fifth state,
  `PEEKING`, implemented in the solution and marked so it can be cut in one
  edit.
- **P09 The Sumo Bot is written.** Guide V01 at 6 pages (3 sheets),
  `projects/p09_sumo_bot.py`, `solutions/sol09_sumo_bot.py`. Three states plus
  a guard above the tree — [DECISIONS #30](DECISIONS.md). It is a capstone in style: the guide
  prints code from P03, P04, P06 and P08 and the student adapts it, rather than
  printing the lines to type — [DECISIONS #29](DECISIONS.md).
- **The line-sensor threshold was measured**, 2026-08-09, marker on white paper:
  white reads about 50, a sensor on the line reads 300-650. `LINE_THRESHOLD = 200`.
  During rotation all three sensors swing 50-350. See [DECISIONS #21](DECISIONS.md). Still true;
  it now belongs to the Term 2 project.
- **The `GIVEN:` comment convention was extended to P01-P06 scaffolds.** Comments
  only; no code changed, so the approved guides still match.
- **`projects/` and `solutions/` hold P00-P09, and nothing else.**
  ~~Everything from P10 up is in `old_projects/` and `old_solutions/`.~~ —
  2026-08-29: those folders were deleted. They lived *inside* `projects/`, which
  is symlinked onto every student robot, so ten dead scaffolds with colliding
  numbers were shipping to the class. Git has them: they were moved in
  `09df78d`, so any file is recoverable with
  `git show 09df78d^:projects/p10_traffic_light.py`.
- **The solution testbench covers P08 and P09.** `tests/tb/plant.py` V02 gained a
  `Target` — stand, flee, chase or glued to the robot's nose, visible only
  inside a 30 degree cone — and a ring, so the line sensors read black-high
  inside and white-low on the rim. Nine new named tests. `run_solution_regression.py`
  reports 13 pass, 0 fail, 9 skip; `run_host_regression.py` reports 20 pass,
  0 fail, 9 skip. See [DECISIONS #22](DECISIONS.md) and [#31](DECISIONS.md).
- **A missing HuskyLens is no longer reported as an error.** `nhs_lib` change
  plus a test that patches the driver rather than poking I2C — [DECISIONS #32](DECISIONS.md).
- **`initialize_robot.sh` is at v30.** It strips `__pycache__`, `.DS_Store` and
  stray `.pyc` from the staging copy, and deletes them from the robot ahead of
  the whitelist check — [DECISIONS #33](DECISIONS.md).

**2026-08-12 — the guides became PDFs and the repo became a vault.** None of
this changed a word of any guide; all nine still render identically to what was
approved.

- **The printed guide is a PDF.** Word left the chain entirely: a `.docx` is
  built in a temp folder, converted, and deleted. The nine `.docx` files are out
  of `Project Guides` and into its `Previous Versions`.
  [DECISIONS #36](DECISIONS.md).
- **Built guides are no longer committed.** The markdown is the source and the
  build reproduces it. [DECISIONS #37](DECISIONS.md).
- **`build-all.sh` v04 skips guides that are already current**, the way make
  does, and takes `-f` to force. A full no-op run is under a second instead of
  about a minute. [DECISIONS #38](DECISIONS.md).
- **The builder understands links and Obsidian image embeds**, and a link prints
  as its label only. [DECISIONS #39](DECISIONS.md).
- **Pictures are capped at 6.5 × 4.5 inches** and no longer chain together
  across a page break. [DECISIONS #40](DECISIONS.md).
- **`shared/test-build.js`** — no robot and no Word, building into a temp
  folder. It was 26 checks when written; it is well past 300 lines now and
  covers deploy behaviour, page layout, math and idempotence. Run it after any
  builder change. [DECISIONS #41](DECISIONS.md).
- **The three project files carry real links now**, and `Home.md` is the vault's
  front door.

**Current page counts, measured 2026-08-29:** P00 6, P01 8, P02 8, P03 8, P04 8,
P05 8, P06 10, P07 8, P08 10, P09 6. That is **40 sheets per student**, duplex,
up from 31.

The guides grew when the builder came forward to `aa57c06`, Ray's 2026-08-20
print-readability change: 12pt body, open line spacing, left-aligned rather
than justified, following the British Dyslexia Association's print guidance and
WCAG 1.4.8. Written for Engineering and inherited by Robotics on 2026-08-29.
The 12pt and the ragged right are kept as written; the spacing was cut from 1.5
to 1.2 after comparing rendered pages, which gave back four sheets a student and
reads better. See [DECISIONS #46](DECISIONS.md).

## What's open

**`accelerator.py` has never been run on a robot**

Sim only. Put it beside the metre stick at full charge and again at half,
since the ceiling moves with the battery. The tell for trouble is the UP
run's last two marks coming in late while the early ones are fine — that is
the speed ceiling, and 0.010 has to come down. Each run prints its own mark
times over USB, so the robot can be checked against a stopwatch.

**Physics 1.8 is only half specified**

Ray's note covered the two runs. How a student controls the change from
forward to backward was parked, deliberately, and the program answers it the
simplest way: two buttons, one run each, and the robot has to be carried
back. Nobody has said that is the procedure they want.

**How the Alvik follows a *changing* speed setpoint has never been measured**

Every number in `accelerator.py` rests on it, and the testbench now assumes
a first-order response with a 0.21 s time constant
([DECISIONS #51](DECISIONS.md)). The measured 0.21 s was a startup lag from
standstill; nobody has watched the base track a ramp. This is the single
thing most likely to make the real robot miss the printed times.

**The real top speed is somewhere between 11.5 and 12.5 cm/s**

70 RPM on a 34 mm wheel is 12.46 cm/s, and `drive()` delivers 92.6% of what
you ask, but whether the deficit applies before or after the motors run out
of RPM is unknown. Both accelerator runs stay under 10.2 cm/s so that it does
not matter. Anything faster needs the measurement first.

**Submodule checkout is a live hazard on both machines**

`nhs_lib/arduino_alvik`, `nhs_lib/qwiic_i2c` and `nhs_lib/qwiic_buzzer.py`
are symlinks into `libs_on_github/`. With those submodules not checked out,
they dangle. The school Mac was repaired on 2026-09-04; the home Mac has not
been checked. `git submodule update --init --recursive` works with no
network, since the objects are already in `.git/modules`.

**The other four vaults have not had the font and spacing change deployed**

`shared` is one clone linked into all five vaults, so `nhsengineering`,
`advrobotics` and `physics` pick up Carlito, Courier New and 1.2 spacing the
moment anyone rebuilds — but their guides in Drive are still the old rendering,
and their page counts will move when they are rebuilt. Their guide folders are
`guides/unit01`, `guides/unit02`, `guides/squarebot` and `lectures/`. Robotics
only was rebuilt on 2026-08-29.

Each also needs its own Cowork project with the three Context folders, and its
own `~/vaults/shared` clone on whichever machine has not got one.

**The home machine has not run a `-d` build since the font change**

Everything on 2026-08-30 was verified on the school Mac and in a thread's
sandbox. Home built `p00.md` and matched, but has not deployed, and its
`preflight.sh` and `pre-push` hook have not been exercised. Nothing suggests
they will not work; nobody has watched them.

**P07**

- ~~**The name.**~~ — 2026-08-09: settled, *The Parking Sensor*.
- ~~**Does an unthrottled OLED write bog the loop or flicker?**~~ — 2026-08-09:
  moot. The screen is now written once a second by design. See [DECISIONS #18](DECISIONS.md).
- **P07 has never been run on a robot.** The guide, scaffold and solution are all
  written and unverified.

**Line alignment — moved to Term 2, 2026-08-09**

Ray ran it on hardware and it aligns well from an oblique approach and badly
near square. The design that works stops on the CENTRE sensor and spins it
through an arc, using the outer two only to pick the spin direction; because
the centre sensor sits on the centreline its arc peaks exactly at square, so
the two crossings are symmetric for any approach angle and there is no maximum
oblique angle. See [REFERENCE.md](REFERENCE.md). It was moved out of Term 1 because the guide
would have to teach the arc-and-mirror argument, which is a geometry lesson
rather than a state-machine one — [DECISIONS #26](DECISIONS.md).

Still unresolved, for whenever it comes back:

- **The forward coast before the pose is zeroed** and the rotational coast at
  the end both push the correction the same way, so the robot over-turns.
  Sensitivity goes as 1/sin of the approach angle, which is why it is worst
  near square. One cheap measurement settles the size: print theta at the
  instant of the trigger and again after the settle.
- **A minimum approach angle exists and has not been found.** Trial and error.
- `solutions/sol1x_line_alignment.py` is the parked file. The nine testbench
  checks for it are written for a LATER design than that file and are skipped
  on purpose; see the guard at the top of each in `tests/regression_solutions.py`.

**P07, P08 and P09 have never been run on a robot**

The guides, scaffolds and solutions are all written and all unverified against
hardware. The testbench covers P08 and P09 against a modelled robot, which is
not the same thing.

**P09 numbers that are still guesses**

- **`EDGE_THRESHOLD = 200`** in the sumo solution and scaffold. Nobody has put a
  line sensor on the real ring. Black floor should read high and the white rim
  low; the number between them is assumed.
- **The 3 cm charge threshold.** Ray states the ToF returns a usable number at
  3 cm and that floor false positives start further out, around 5 cm. Not
  measured on the ring.

**P09 tournament rules**

How a bout starts beyond the CROSS press, how it ends, how students place, and
how many robots per bout. Ray's ruling 2026-08-09: not a design input for the
code, so the project was written without them.

**The deadlock nothing solves**

Two sumo bots meet head-on, both see something inside 3 cm, both charge, and
neither moves. The three given states cannot break it. This is deliberate — it
is where a student's own fourth state, and the podium, are won.

**Renumbering not yet done in the repo**

- ~~`projects/p07_sumo_skills.py` and `solutions/sol07_sumo_skills.py` still carry
  the old number~~ — 2026-08-09: Ray moved them out of `projects/` and
  `solutions/` himself.
- ~~`projects/p09_robot_timers.py` and `solutions/sol09_robot_timers.py` must
  become P07~~ — 2026-08-09: superseded. P07 was written fresh as
  `p07_parking_sensor.py`; the old timer files went to `old_projects/`.
- ~~Two cross-references chase the swap~~ — 2026-08-09: both files are now in
  `old_projects/` and out of the deploy path.
- `Capstone1_Sumo_Tournament_Spec.docx` still needs its fate decided — rewrite as
  a project guide, or retire. P09 is written and does not use it. Note that
  "capstone" is now only a description of how P09's guide works, not a
  designation; [DECISIONS #8](DECISIONS.md) still stands. Whether Capstone 2 Navigation Race
  keeps its designation is also undecided.
- **`tests/tb` is on the robots.** It is now in `init_bot/nhs_robot/.robotignore`
  so it will not be uploaded again, but a whitelisted path is one the sync
  leaves alone, so any copy already on a robot needs one `mpremote rm -r :tests/tb`.
- **`projects/old_projects` is on the robots**, same trap. The folder is gone
  from the repo as of 2026-08-29, but the sync only stops *sending* it — every
  robot already initialised keeps its copy until it gets one
  `mpremote rm -r :projects/old_projects`. Ten dead scaffolds with numbers that
  collide with the real ones, in a folder students can open.

**Library work owed**

- **A buzzer passthrough** if the non-visual proximity cue is wanted. A Qwiic
  buzzer already exists in `nhs_lib/nhs_robotics/peripherals.py` with note
  constants and effects including a siren, and `RobotUI` already plays effects.
  There is no `sb.` passthrough. Any `nhs_lib` change needs a test.
- Version prints still missing in `gamepad.py`, `ui.py`, `navigation.py`,
  `vision.py`, `line_follower.py`, `controller.py`. `vision.py` was edited
  2026-08-09 and deliberately did NOT get one — Ray was cutting boot noise at
  the time.
- ~~`sb.drive_to_line()` passthrough before P11 is printed~~ — 2026-08-09:
  P11 is in `old_projects/`. Revisit only if a redesigned P11 needs it.
- **An `sb.get_line_sensors()` passthrough.** The parked line-alignment solution
  and P09's given `edge_detected()` both call `alvik.get_line_sensors()`
  directly. Not urgent, and any `nhs_lib` change needs a test.

**Deferred to October, deliberately**

P10 through P14, the home for lists, whether P10 Traffic Light survives now that
P08 teaches state machines, where line alignment lands in Term 2, and the total
project count. P07-P09 now exist on disk, so a recount is allowed — but nothing
past P09 has been designed.

**Long-standing**

- The worksheet is now generated by `guides/worksheet.js` and deploys as
  *Robotics_Project_Worksheet.pdf* — see [DECISIONS #44](DECISIONS.md). Part A's
  wording and Part B question 1 are still Ray's to settle; change them in the
  script, not in the output.
- `dev/curve_pose_test.py` has never been run. It measures `rotate()`, `drive()`
  with both arguments, and whether pose y survives a curve. P05 rests on the
  second of those, and P09's curved hunt patterns now do too.

## Paths not taken

- **Keeping a private copy of the builder.** Held until 2026-08-13 on the
  grounds that Robotics is its own course. Every one of #38, #39, #40 and #41
  ends "Affects both repos," and each was hand-carried; that was the argument
  against it. [DECISIONS #43](DECISIONS.md).
- **The worksheet as a `.docx`.** It had always been one, and it was rebuilt as
  one first. Reversed the same day: a Word file invites a hand-fix the next build
  discards, and a form is where reflow hurts most. [DECISIONS #44](DECISIONS.md).
- **Five ToF zones for opponent bearing.** Rejected 2026-08-05 in favour of the
  3 cm threshold. Students never see the zones.
- **`get_distance_top()` / `get_distance_bottom()` for opponent detection.**
  Proposed and wrong: those face perpendicular to the top and bottom of the
  robot, not forward, so neither can see an opponent. The white-floor problem is
  IR reflection into the horizontal zones, not geometry.
- **Controller rumble as the proximity cue.** No rumble exists anywhere in the
  codebase; it would need robot-side and browser-side work plus a regression
  test. The buzzer already there does the same job.
- ~~**Two independent timers in P07**~~ — 2026-08-09: reversed. P07 has two timer
  checks, introduced one WORK apart. See [DECISIONS #18](DECISIONS.md).
- **P07 as a distance-sensor project** ("drive to the wall and stop at a
  distance"). Dropped — that is `p04_drive_to_the_wall_and_back.py`'s WORK 2
  verbatim, with `WALL_THRESHOLD_CM` already given at the top of the file.
- **P08 as timers plus a state machine.** Superseded when timers moved to P07.
- **Writing line alignment's three sequential `while` loops.** Wrong: each is
  a blocking wait that deafens the robot to everything else, and the sequence
  branches on which sensor trips first, since the approach angle is arbitrary.
  It needs one loop with a state variable.
- **A four-state alignment machine with no STOP.** Tried and wrong on hardware. Without
  a state that brakes and then watches the pose until it stops changing, the
  robot rolls onto the band during the 0.2 s the base takes to act, and the
  sweep measures nothing. See [DECISIONS #20](DECISIONS.md).
- **Re-issuing `drive()` every pass of the loop.** The robot went straight over
  the line without seeing it. `drive()` sets a speed that stays set.
- **The Guard Bot with two thresholds.** P08 was first written as a guard that
  became alarmed at 20 cm and calmed at 35, with the gap doing the work of
  forcing the state variable. Killed by the robot: the alert state spun, which
  swung the sensor off the intruder and read 999, so the gap never did anything.
  A state cannot both turn away from the thing its exit test is about and use
  that test. See [DECISIONS #27](DECISIONS.md).
- **Line alignment as the Term 1 state-machine project.** Moved to Term 2 —
  [DECISIONS #26](DECISIONS.md).
- **A timed state anywhere in P09.** There is nowhere left for one: the retreat
  blocks, the countdown is a human calling "one, two, three, go", and the
  gamepad wait is given. [DECISIONS #14](DECISIONS.md) said timed states were P09's new idea;
  that part of it is retired — [DECISIONS #30](DECISIONS.md).
- **Leaving the state machine at P10 Traffic Light.** Rejected — P10 is in the
  undesigned zone, so the course Ray actually runs this fall would never teach
  the SWBAT.
- **The Variable Blinker's up/down button interval control.** Replaced by a
  rate driven by the distance sensor, which removes the button-debounce problem
  that was the old material's biggest source of confusion.
- **A "Confirming Target" disambiguation state for P09.** Moot — the 3 cm
  threshold replaces it.
- **Gamepads in the sumo tournament.** Removed entirely. This also removes
  pairing, WiFi, Chrome focus and the silent flat-battery failure from
  tournament day.
