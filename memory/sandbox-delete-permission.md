---
name: sandbox-delete-permission
description: "When rm fails with \"Operation not permitted\" in a mounted folder, request permission instead of declaring it impossible."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fec45b3f-d17f-4cd6-912b-559c47953c3e
  modified: 2026-08-28T19:01:06.745Z
---

A failed `rm` in a mounted folder ("Operation not permitted") is a permission
prompt waiting to happen, not a dead end. Call
`mcp__cowork__allow_cowork_file_delete` with the path; Ray approves once and
deletion is enabled for that whole folder for the session.

**Why:** on 2026-08-28 I created `__pycache__` and a stray `.writetest` in Ray's
nhsrobotics vault, hit "Operation not permitted" on `rm`, and twice handed him
the cleanup as an action item. He was under time pressure and told me to stop
giving him work. The tool was available the whole time.

**How to apply:** clean up my own artifacts silently — request the permission,
delete, say nothing unless it fails. Better still, don't create them: compile
with `python3 -B` so no `__pycache__` is written. Never report my own mess as
something for Ray to do. See [[no-git-writes-through-cowork-mount]].
