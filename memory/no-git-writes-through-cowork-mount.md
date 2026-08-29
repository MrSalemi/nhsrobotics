---
name: no-git-writes-through-cowork-mount
description: "Never run write-mode git against Ray's vaults through the Cowork mount — it leaves locks and absolute sandbox paths in the repo's plumbing. Note that git status counts as a write."
metadata:
  node_type: memory
  type: feedback
  originSessionId: fec45b3f-d17f-4cd6-912b-559c47953c3e
  modified: 2026-08-29T23:40:00.000Z
---

Reads that touch no index — `log`, `show`, `ls-tree`, `merge-base`,
`cat-file`, `rev-list` — are fine through the mount. Anything that writes is
not, and **`git status` writes**: it refreshes the index and takes
`.git/index.lock`. I left a stale one on 2026-08-29 doing exactly that, which
then blocked Ray's `git config` and cost him a confusing detour.

**Why:** Cowork mounts the vault at a per-session sandbox path like
`/sessions/<name>/mnt/<vault>`, git writes that absolute path into its own
plumbing, and the sandbox cannot always clean up its own lock files. On
2026-08-28 every submodule `.git` pointer in nhsrobotics was aimed at
`/sessions/sweet-adoring-goodall/...`, a path that exists on no Mac, and
`git status` died outright. The fix was rewriting each as a *relative*
`gitdir:` path.

~~That poisoning was caused by a Cowork session crashing mid-operation.~~ —
2026-08-29: not established. The reflog showed the detached HEAD came from an
ordinary `git submodule update --init` five minutes after a fresh clone, which
is simply what that command does. I told Ray a confident causal story and had to
retract it. Say "I'm inferring" when inferring.

**How to apply:** use Write/Edit for file changes and hand Ray the git commands
to run himself. He runs every commit and push, in every repo, without
exception. See [[sandbox-delete-permission]] and [[start-at-the-output]].
