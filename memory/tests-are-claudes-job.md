---
name: tests-are-claudes-job
description: "Ray wants the outcome of testing, never the plumbing — don't report harness changes, mutation runs, or how a check works."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 232a02d6-5fb8-4255-bea4-549e25f494ad
  modified: 2026-09-04T17:32:20.282Z
---

Ray's instruction, verbatim: *"You fix your own tests. I don't need to know
about it."*

**Why:** on 2026-09-04 I was writing a physics program and reported, in the
middle of the work, that the testbench's fake robot had no speed ceiling and
that I would add one. That is true, and it was mine to fix. Telling him
turned a solved problem into something on his desk. His model of
AI-assisted coding is clear direction plus test-based verification — the
tests existing and passing is the deliverable, and the mechanism is not his
concern.

**How to apply:** write the test, fix the harness, run the mutations, say
nothing about any of it. Report pass/fail counts at most one line. What
*does* reach him is only this: a number the tests cannot vouch for, a
decision about the system under test, or a change to a model of measured
hardware — because that last one changes what every other test means. "I
added a knob to the simulator" is plumbing. "The simulator's model of the
0.21 s lag was wrong, and the measurement behind it does not exist" is his.

Related: [[answer-the-question-asked]], [[no-remembering-as-a-fix]].
