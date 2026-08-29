# NHS Robotics — Decision Log

Numbers are permanent. A reversal is struck with its reason, not deleted.

Current state is in [PROJECT.md](PROJECT.md); durable knowledge is in
[REFERENCE.md](REFERENCE.md).

Entries 1-6 were written in `nhsrobotics/DECISIONS.md` on 2026-08-05 and are
carried here verbatim; that copy is now superseded and points here. Unless
noted, a decision affects both repos.

1. **Sumo (Capstone 1 tournament) is numbered P09, not P07.** — 2026-08-05

2. ~~**P07 is the line-alignment project**: drive until a line sensor sees the
   line, then square up on it regardless of approach angle (angle assumed
   acute). It introduces the line sensors, which P09 Sumo Skills previously
   did as a side effect of its edge guard.~~ — 2026-08-05
   — **2026-08-07: reversed by #10.** Line alignment is P08. P07 is the timer
   project. The reasoning above still holds for the project itself, only the
   number changed.

3. **Fall Term 1 is 22 periods (8/28-10/30); Term 2 is 21 (11/3-1/14).** Read
   from Ray's own calendar (`Red Blue 2627 Calendar.xlsx`, column G) and
   confirmed by him. — 2026-08-05

4. **Term 1's last period is not slack.** Students start P10 on 10/30 and
   finish it in Term 2 — the term boundary is a grading boundary, not a work
   boundary. — 2026-08-05
   — **2026-08-07: the calendar does not say this.** Column G's 10/30 cell
   reads only "End of Term 1"; P10 appears nowhere in the sheet. 10/30 is a
   real class day with no project assigned. The principle may still be Ray's
   intent, but it is not recorded anywhere and P10 is deferred to October.

5. **Cross-course date collisions are not treated as scheduling conflicts.**
   Ray's ruling: "we are not a one-room schoolhouse." A Robotics due date
   landing on a Physics exam day is not a problem to solve. — 2026-08-05

6. **The class's SWBAT for the state-machine unit is the `elif` tree keyed on
   a state variable** — not "state machines" as a general topic, and not any
   specific theme. Whatever project teaches it, a new state must be forced by
   real ambiguity or by a memoryless bug, never added to pad the count.
   — 2026-08-05

7. **Sumo (P09) is autonomous only. No gamepads.** Four robots start back to
   back, each runs a hunting pattern, and a robot charges when it detects
   another robot directly in front of it. Hitting the ring edge is a
   manoeuvre — back up, turn, resume hunting — not a veto on a human driver.
   The hunting pattern is where student individuality lives now that driver
   skill is gone. — 2026-08-07

8. **P09 is no longer designated Capstone 1.** It is a normal project, which
   means it may teach new material rather than only combining earlier work.
   — 2026-08-07

9. **Opponent detection is a 3 cm charge threshold. The five ToF zones are not
   taught.** The white floor produces IR false positives in the horizontal
   zones; rather than filtering them, the robot only believes readings close
   enough that an opponent is essentially touching it. Charge means shove from
   near-contact, so matches turn on the quality of the hunt pattern rather than
   on sensing range. — 2026-08-07

10. **The sequence through the designed portion of the course is P07 timers,
    P08 line sensor, P09 sumo.** This reverses #2 — line alignment moves from
    P07 to P08. P07 becomes the old P09 "Robot Timers" material; P07 and P09
    swap numbers in the repo. — 2026-08-07

11. **P07 is a driveable proximity alarm, built from the old Robot Timers
    material.** WORK 1 read the distance sensor and show it on the OLED while
    holding the robot in your hand. WORK 2 add a blink that speeds up as the
    distance closes. WORK 3 add tank drive, so display, blink and driving all
    run at once. FLEX: refuse positive motor speeds inside 5 cm, reverse always
    allowed. The split is deliberately additive — nothing rewrites an earlier
    WORK, so the one-checkpoint rule needs no exception. — 2026-08-07

12. **P07 has exactly one timer.** There is no display-refresh clock; the OLED
    is written every lap. `ticks_ms` appears in WORK 2, at the moment the
    student would otherwise reach for `sleep()` and discover it freezes the
    display they just built. Two independent clocks in one loop was considered
    and rejected as too much at once. — 2026-08-07

13. **P07 blinks both Alvik LEDs together via `sb.light_both_leds()`**, the
    helper P02 teaches and P04 uses. Individual `left_led` / `right_led` calls
    are for cases where the two differ, as in P06. The guide is built around
    the callback: P02 gave students a `blink()` that works by freezing the
    robot, and P07 is the same blink on the same lights, made not to freeze.
    — 2026-08-07

14. **The state machine is introduced at P08 and scaled at P09.** P08's
    alignment cannot be written as three sequential `while` loops: each is a
    blocking wait, and the sequence branches on which sensor trips first
    because the approach angle is arbitrary. So P08 gets one loop with a state
    variable on a job that ends. P09 reuses the shape for hunt, charge and
    edge recovery on a loop that never ends, and adds timed states — "how long
    have I been in this state" — as its one new idea. — 2026-08-07

15. **Every robot has an OLED, set up by students on the first day. Projects
    may assume it.** — 2026-08-07

16. **No controller rumble.** It exists nowhere in the codebase and would need
    robot-side and browser-side work plus a regression test. The Qwiic buzzer
    already in `peripherals.py` covers the same non-visual cue and needs only
    an `sb.` passthrough. — 2026-08-07

17. **Design work stops at P09.** P10 through P14 are decided in October, after
    Ray has run the class. No P10+ project may be used as an argument about
    P07-P09, because those slots may be rewritten or cut. — 2026-08-07

18. **P07 has two timer checks, not one. This reverses #12.** WORK 1 is a
    seconds clock on the OLED — divide elapsed milliseconds by 1000 and write
    the screen only when the whole number changes. WORK 2 adds the blink
    interval. The two arrive one WORK apart rather than together, which is what
    #12 rejected. The `sleep()` reasoning under #12 is also withdrawn: the
    course never offers `sleep()` as the timing tool, and P02's freezing
    `blink()` already supplied the pain. — 2026-08-09

19. **P07 is named "The Parking Sensor."** — 2026-08-09

20. **A P08 state machine alternates orders and watchers**, and every order is
    given exactly once by a state that exists to give it. `START_DRIVE` then
    `WATCH_DRIVE`, and so on. Re-issuing `drive()` on every pass floods the link
    to the STM32 and the robot stops seeing the line. A STOP state is required
    after first contact: brake, then watch the pose until it stops changing.
    Never assume a command has taken effect — the base is about 0.2 s behind.
    Affects `nhsrobotics` solutions. — 2026-08-09

21. **`LINE_THRESHOLD = 200`**, measured on marker over white paper: white reads
    about 50, a sensor on the line reads 300-650. During rotation all three
    sensors swing between 50 and 350, so while turning the robot looks at *only*
    the sensor it is waiting for. — 2026-08-09

22. **Solutions get a regression testbench, and it is for us, not students.**
    `nhsrobotics/tests/tb/` models the robot's world — pose, line, sensors — and
    shadows `arduino_alvik`, `nhs_robotics` and `time` on `sys.path` so the real
    solution files run unmodified. The DUT's own `sleep_ms` drives a simulated
    clock, so the suite finishes in under a second with no robot. Checks compute
    expectations from the world model, never from the solution's own arithmetic.
    The measured hardware defects are knobs, so an immunity claim can be a test
    rather than a comment. Run with `tests/run_solution_regression.py`; it is
    also folded into `tests/run_host_regression.py`. No pytest — Ray's call.
    Affects `nhsrobotics`. — 2026-08-09

23. **Scaffold `GIVEN:` comments say why the line is there, not just that it is
    given.** Applied across P01-P06 on 2026-08-09. Comments only; no code
    changed, so the approved guides still match. Affects `nhsrobotics`.
    — 2026-08-09

24. **`int(a / b)`, never `a // b`.** Floor division is a second operator to
    explain for no gain; `int()` is a function, and functions are a shape
    students already own from P02. Affects guides and code. — 2026-08-09

25. **Projects P08 and up were moved out of the active folders.**
    `projects/old_projects/` and `solutions/old_solutions/` hold P08-P14, moved
    with `git mv`. `projects/` and `solutions/` are P01-P07 only, so a deploy
    cannot push a stale numbered file. Affects `nhsrobotics`. — 2026-08-09

26. **Line alignment leaves Term 1 and becomes a Term 2 project.** It works on
    hardware — the version that stops on the CENTRE sensor and sweeps its arc
    aligns well from any oblique approach — but the guide would have to teach
    the arc-and-mirror argument to justify halving the angle, and that is a
    geometry lesson wearing a state machine's coat. Term 2 can carry it. The
    solution is parked at `solutions/sol1x_line_alignment.py`; its nine
    testbench checks are written for a later design than that file and skip on
    purpose. Affects both repos. — 2026-08-09

27. **A state may not turn away from the thing its own exit test measures.**
    P08 was first written as a Guard Bot with hysteresis: alarmed inside 20 cm,
    calm past 35, and the gap between them forcing the state variable. The
    alert state spun in place, which swung the distance sensor off the intruder
    and read 999 — past the calm threshold — so the alert ended in a few
    degrees and the two thresholds never did anything. The lesson generalises:
    if a state's exit depends on a reading, the state's actions must keep that
    reading meaningful. — 2026-08-09

28. **P08 is The Security Bot.** Patrol on green, advance slowly on anything
    inside 60 cm, and then one of two things: it fled past 90 cm, or it never
    moved and is now inside 15 cm, in which case turn 135 degrees and run.
    "It did not flee" is a fact about a stretch of time, not about a reading,
    which is the honest argument for a state variable. The retreat uses
    blocking `move()` and `rotate()` — the opposite of P07's rule, for the
    opposite reason: nothing needs watching while you leave. 135 and not 180 so
    the robot does not retrace its own path and bounce between two walls.
    Affects both repos. — 2026-08-09

29. **P09's guide prints code from earlier projects, not the lines to type.**
    Every other guide prints what to write. This one shows the student what
    they wrote in P03, P04, P06 and P08 to solve the same problem, and asks
    what has to change. "Capstone" here describes that method only; DECISIONS
    #8 stands and P09 is not designated Capstone 1. Affects `Class Development`.
    — 2026-08-09

30. **P09's one new idea is a guard above the elif tree, and it has no timer.**
    The edge test cannot live inside a branch — a robot must leave the rim
    whether it was patrolling or charging — so it sits above the tree and takes
    effect on the same pass, which is exactly what P08 taught transitions do
    not do. That contrast is the lesson. The consequence: the screen write must
    sit BELOW the guard, or a state the guard sets and the tree clears on one
    pass is never displayed. This also retires the timed-state half of
    DECISIONS #14 — the retreat blocks, the countdown is a human voice, and the
    gamepad wait is given, so there is nowhere for a clock. Affects both repos.
    — 2026-08-09

31. **The solution testbench models targets and rings, and every check is
    mutation-tested.** `tests/tb/plant.py` V02 adds a `Target` (stand, flee,
    chase, or glued to the nose, visible only in a 30 degree cone) and a ring
    (black inside, white rim, radius and width). A check is only trusted once
    the code has been broken on purpose and the check has failed: deleting
    P09's guard sends the robot 4.8 m from the ring centre and is caught;
    inverting P08's `distance < SPOT_CM` is caught by the empty-room test and
    NOT by the reaches-every-state or ordering checks. Affects `nhsrobotics`.
    — 2026-08-09

32. **Absent hardware is news, not a fault.** `RobotVision` reported a missing
    HuskyLens with `log_error` on every boot of every robot, and almost no
    robot has one. Downgraded to `log_info`, and the three per-attempt search
    prints dropped. A suite or a robot that cries wolf teaches everybody to
    skim past the word ERROR. Covered by a test that patches `QwiicHuskylens`
    rather than poking I2C, so it runs the same on a laptop and on a robot.
    Affects `nhsrobotics`. — 2026-08-09

33. **The deploy never ships the laptop's droppings.** `initialize_robot.sh`
    v30 strips `__pycache__`, `.DS_Store` and stray `.pyc` from the staging
    copy, and deletes them from the robot BEFORE the whitelist check. The order
    matters: a `.robotignore` entry means "leave this alone", so naming junk
    there preserves it instead of removing it. `.robotignore` is read from the
    folder passed to `-d`, not from `init_bot/`. Affects `nhsrobotics`.
    — 2026-08-09

34. **`PROJECT.md`, `DECISIONS.md` and `REFERENCE.md` live in the class's own
    repo, never in `Class Development`.** Moved into `nhsrobotics` on
    2026-08-09. `Class Development` holds Physics and Engineering as well as
    Robotics, and each class needs its own threads and its own history; one set
    of project files at the top of a shared folder would mix them, and a thread
    about one course would open by reading the state of another. Affects
    `nhsrobotics` and any future class repo. — 2026-08-09

35. **The robotics repo is the Obsidian vault, and the vault root is the repo.**
    Not a folder inside it and not a separate vault: a second copy of the guides
    would be a second source of truth, which is what the builder exists to
    prevent. `builder/node_modules` and `libs_on_github` are excluded from
    search. `.obsidian/` is committed except `workspace.json`, which is
    per-machine layout. Affects `nhsrobotics`. — 2026-08-12

36. **The printed guide is a PDF. Word is not in the chain.** A `.docx` is built
    in a temp folder, converted by LibreOffice, and deleted. No office suite is
    needed to make a guide or to print one, and — the real reason — there is no
    editable copy, so an edit that is not in the markdown cannot survive and
    therefore cannot be made by accident. The nine deployed `.docx` moved to
    `Project Guides/Previous Versions/`. Affects both repos. — 2026-08-12

37. **Built guides are not committed.** The markdown is the source and the build
    reproduces it, so the repo stays text — which was the point of moving to
    Obsidian. A rebuilt file always looks modified to git anyway, because the
    format carries a creation time. The copies that matter live in
    `Project Guides`, with retired ones in its `Previous Versions`. Affects both
    repos. — 2026-08-12

38. **`build-all.sh` only rebuilds what is stale, the way make does.** A guide is
    rebuilt when its markdown, one of its pictures, or the builder itself
    (`build.js`, `parse.js`, `make.js`) is newer than the PDF; `-f` forces.
    Pagination is measured by running the file through LibreOffice, so a full
    no-op run went from about a minute to under a second. With `-d` the deployed
    copy is compared too, so a guide built earlier without `-d` still gets
    copied. Affects both repos. — 2026-08-12

39. **A link prints as its label and nothing else, and a bare link to another
    guide is refused.** Guides are read on paper, where a clickable target is
    worthless and a filename is noise, so `[[p03|Gamepad Driving]]` and
    `[Gamepad Driving](p03.md)` both print *Gamepad Driving*. A bare `[[p03]]`
    prints "p03", a name no student has ever seen, and it is the first thing
    Obsidian's autocomplete offers — so the build refuses it and says what to
    write. A guide is recognised by there being a `.md` of that name in the
    builder folder, so the rule needs no list. Frontmatter is exempt: `related:`
    is bare links on purpose and is never printed. Obsidian's `![[picture.png]]`
    embed is understood and resolved against `images/`. Affects both repos.
    — 2026-08-12

40. **A picture is capped at 6.5 × 4.5 inches, and carries `keepNext` only when
    the next block is not a picture.** Height was never capped before, so a
    portrait screenshot rendered seven inches tall and owned a sheet. And
    `keepNext` on every picture chained consecutive ones into a single
    unbreakable block; a block taller than a page shunted the whole run to the
    next sheet and left the current one empty. Both were found in the imported
    engineering guides, but the fix belongs to both builders. Affects both
    repos. — 2026-08-12

41. **The guide builder has its own test suite, `builder/test-build.js`.**
    24 checks: every guide builds, links print as labels, a bare guide link is
    refused, frontmatter properties change nothing on the page, and two builds
    of the same markdown produce the same document. It builds into a temp folder
    so it never touches the deployed guides, and needs no robot and no Word.
    Every check was mutation-tested — broken on purpose and confirmed to fail.
    Affects both repos. — 2026-08-12

    2026-08-13: it moved into the shared builder with everything else (#43), so
    it is run as `node ../builder/test-build.js` from `guides/` and is pointed at
    a course's guides folder rather than assuming the guides sit beside it. Two
    checks were added — a guides folder with no `course.js` is refused, and the
    count is no longer 24.

42. **Guide frontmatter carries `tags` and `related`.** The builder reads only
    `out`, `version`, `title`, `number` and `scaffold`, so the extra keys are
    inert and provably change nothing in the output. They exist to make the
    Obsidian graph and backlinks show how projects feed each other — P09's
    `related` names P03, P04, P06 and P08, which is [DECISIONS #29](DECISIONS.md)
    made visible. Affects both repos. — 2026-08-12

43. **The builder is one shared repository, `rsalemiTeaches/guide-builder`, a
    submodule at `builder/` in both courses.** `guide_builder/` is gone. The
    guides, `images/` and the built PDFs are in `guides/`.

    Entries #38, #39, #40 and #41 each end "Affects both repos," and every one
    of them was carried across by hand. That was the argument: the copies never
    diverged on purpose, only by neglect. Engineering reversed its own decision
    to keep a separate copy — its DECISIONS #5, reversed by #11 — and this is
    the same call from this side.

    **Each course pins its own commit**, so a change arrives when the pin moves
    and not before. Bumping a pin means rebuilding and *looking at* the guides in
    both courses: pagination is the shared failure mode and it fails quietly.
    Moving to the shared builder repaginated P06 — the same eight pages and the
    same words, but the breaks fall differently, because a picture no longer
    glues itself to the heading underneath it.

    Three things had to change for one builder to serve two courses:

    - **The builder holds no course text.** `SAVE`, `PARTA` and `GRADING` moved
      out of `build.js` into `guides/course.js`, which is called with the
      guide's frontmatter — that is how `SAVE` still gets the project number and
      the scaffold filename. A guides folder without a `course.js` is refused
      rather than guessed at. This is the one thing that genuinely differs
      between the courses, and it is now the only thing.
    - **The builder does not assume it sits beside the guides.** Pictures and
      sibling guides resolve against the folder the markdown is in, and the
      deploy target is named in `guides/deploy.txt` rather than hardcoded.
    - **A guide is a letter and two digits**, `p07.md` or `e07.md`. The glob was
      `e*.md`, which is Engineering's naming and found nothing here.

    Robotics also gains what Engineering had found in the meantime: markdown
    tables, a preflight that names a missing `soffice` or `pdftoppm` instead of
    exiting silently, and `extras.txt` for the things that ship with the guides
    but are not guides. — 2026-08-13

44. **The project worksheet is generated, not written.**
    `guides/worksheet.js` is the source and writes
    *Robotics_Project_Worksheet.pdf*; it is gitignored like the guides and never
    edited by hand, for the same reason no guide has an editable copy. It is
    listed in `guides/extras.txt`, so one `build-all.sh -d` remakes and deploys
    the guides and the worksheet together. Until now the worksheet lived only in
    Drive, with no source anywhere and nothing to rebuild it from.

    **It is a PDF, not the `.docx` it used to be.** A Word file invites a
    hand-fix that the next build throws away, and a form is exactly where reflow
    between Word versions hurts — ruled lines and box widths move. It reaches PDF
    through the builder's `topdf.js`, the same temp-and-discard chain a guide
    uses, so no editable copy exists anywhere.

    The builder does not make it: the sheet is a form, not a guide — ruled
    write-on lines, checkbox glyphs, and answer space measured in blank lines.
    It borrows the builder's `docx` package rather than keeping a second one.
    Engineering's checkoff sheet works the same way; see its DECISIONS #13.

    Two things changed in the move, both because the old layout said something
    it did not mean:

    - **The two redo gates get their own row.** "Robot works" and
      "Explanations OK" were spread across the four score columns, which read as
      though passing explanations belonged to Late and Redo. They are conditions
      on the whole sheet.
    - **Ruled answer lines are table rows, not bordered paragraphs.** Word treats
      a run of adjacent paragraphs with identical borders as one bordered block
      and draws the rule once around the group, so four ruled lines came out as
      a single line with a lot of white above it. — 2026-08-13

45. **The shared builder is a sibling directory reached by a symlink. It is not a
    submodule.**

    The builder is cloned once at `~/vaults/shared`, and every vault holds
    `shared -> ../shared`, a committed relative symlink. All vaults sit directly
    under `~/vaults/` on both machines, which is what makes the relative path
    work regardless of the account name — `rsalemi` at school, `raysalemi` at
    home.

    **A submodule is right for code you consume and wrong for code you author.**
    The Qwiic libraries are the right shape: third-party, rarely changed, pinned
    on purpose, and moving to a new version is a deliberate event. The builder is
    the opposite in every dimension. Ray writes it, it changes weekly, all vaults
    want the newest, and it has no stable interface — changing the format of
    `deploy.txt` required coordinated edits in three consumers, which is exactly
    what pinning does not help with.

    The cost was ceremony. Every builder change meant two commits in two repos
    plus a pointer bump per vault, on top of a preflight for detached HEAD, a
    missing fetch refspec, and a stale local checkout. On 2026-08-29 the local
    copy was eight commits and 106 lines of `build-all.sh` behind while looking
    perfectly healthy; the edit was written against the stale file and had to be
    thrown away and redone. When a routine edit needs a 130-line checklist, the
    container is wrong.

    **What this gives up is pinning.** A bad builder commit now breaks every
    course at once instead of leaving Engineering insulated until it chooses to
    move. That isolation was mostly theoretical — [#43](DECISIONS.md) records
    that every fix was hand-carried into both repos anyway — and recovery is one
    `git checkout` in `~/vaults/shared`.

    **No paths change.** `guides/../shared/topdf.js` still resolves,
    `worksheet.js` needs no edit, `node ../shared/test-build.js` still runs. The
    symlink is committed, matching the `lib`, `projects` and `tests` links in
    `init_bot/nhs_robot/`, so a fresh clone gets it and fails loudly and
    obviously if `~/vaults/shared` is not there.

    **Paths not taken.** Putting the builder on `PATH` is architecturally
    cleaner — it is a tool, not content, and `build-all.sh` already resolves its
    own location and takes the guides from `pwd`. But `worksheet.js` resolves
    `../shared/node_modules/docx` and `../shared/topdf.js` as siblings, so it
    would need a refactor in every vault, and a cloned vault would carry no hint
    that a builder exists at all. Keeping a private copy per repo is #43's
    rejected option and the reason the submodule existed in the first place.
    — 2026-08-29

46. **Guides are set in Carlito and Courier New, and Robotics keeps the 12pt
    readability settings.**

    Two font changes and one inherited setting, all settled the same evening.

    **Carlito, not Calibri, for body text.** Calibri ships with Microsoft
    Office, so whether a machine has it — and how many of its four faces — is an
    accident of what else is installed. Ray's home Mac had Regular and Bold
    only, which means italic text was a *synthesised* slant of Regular, and a
    synthesised slant is not the width of a real italic. The school Mac had no
    Calibri at all. Carlito is the free metric-compatible clone, installs as a
    complete family (`brew install --cask font-carlito`), and every machine then
    lays out from the same file instead of from something merely compatible.

    **Courier New, not Roboto Mono, for code.** Roboto Mono installs as a
    *variable* font (`RobotoMono[wght].ttf`), and LibreOffice's handling of
    those is not dependable. Two Macs with byte-identical font files and the
    same LibreOffice build disagreed: one embedded `RobotoMono-Regular`, the
    other silently fell back to Linux Libertine G — **a serif proportional
    face**. Code set in a proportional font is a broken handout, and the build
    reports success either way, so the failure is invisible until somebody opens
    the PDF. Courier New ships with macOS and Windows, Drive's viewer has it,
    and where it is absent LibreOffice substitutes Liberation Mono, its exact
    metric clone. Both machines now produce structurally identical documents.

    **The guides got bigger, and the spacing came back down to 1.2.** Coming
    forward to the current builder brought `aa57c06`, the 2026-08-20
    print-readability change — 12pt body, 1.5 line spacing, left-aligned rather
    than justified, following the British Dyslexia Association's print guidance
    and WCAG 1.4.8. It was written for Engineering, and Robotics inherited it.

    The 12pt and the ragged right are kept exactly as written; they are doing
    most of the work and they cost little. The spacing was cut from 1.5 to 1.2
    after comparing rendered pages side by side: at 1.5 the paragraphs stopped
    holding together as blocks and the page read as airy rather than open. 1.2
    keeps the lines clearly separated, which is what the guidance protects. A
    full set went 31 sheets per student → 44 at 1.5 → **40 at 1.2**.

    `LINE` is now an environment override, so the next comparison needs no edit:
    `LINE=312 ./build-all.sh -f p00.md`. The test that guarded this asserted
    `w:line="360"` exactly, which pinned the digit rather than the decision and
    failed the moment the number moved; it now asserts a floor, so the value can
    be tuned but a guide cannot quietly fall back to single spacing.

    **The lesson underneath all three:** a font named in the source is a
    *request*, not a guarantee. What actually rendered is in the PDF, and
    `pdffonts` is the only honest answer. Page-count drift between two machines
    is the visible symptom of a silent substitution somewhere. — 2026-08-29
