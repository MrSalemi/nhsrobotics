---
name: no-remembering-as-a-fix
description: Ray counts "you have to remember to do X" as technical debt. Make it structural or automatic, never a documented step.
metadata:
  type: feedback
---

Ray's rule, verbatim: *"No technical debt, that includes having to remember
stuff."*

A checklist item, a README line, or a "run this first" instruction is not a
solution to him. It is the same bug with a delay on it, and it fails precisely
when he is busy — which is when it matters.

**Why:** on 2026-08-29/30 I proposed a documented rule three times and he
rejected it three times. A `.robotignore` entry instead of deleting dead code.
"Reattach the submodule before editing" as a note. `preflight.sh` as a manual
step before pushing. Each time the fix was to make it structural: delete the
folder, remove the submodule entirely, and put the gate in a `pre-push` hook
that `build-all.sh` installs itself.

**How to apply:** when the answer is "just remember to…", stop and find where
the machine can do it. Ask which action already happens reliably and often, and
hang the enforcement off that. If it genuinely cannot be automated, say so
plainly rather than dressing a checklist up as a fix.

He applies this to himself too — he removed his school Google account from his
home Mac rather than keep two mounted and be careful about which was which.

Related: [[start-at-the-output]], [[sandbox-delete-permission]].
