---
name: two-macs-and-the-school-firewall
description: Ray works from two Macs; the school network blocks npm and GitHub, so anything needing a download has to happen at home.
metadata:
  type: project
---

Two machines, both used for the same vaults:

- **school** — user `rsalemi`, host `Rays-Mac`
- **home** — user `raysalemi`, host `MacBookPro`, computer name `RayProMac`

Both keep every vault directly under `~/vaults/`, with the guide builder as a
sibling at `~/vaults/shared`. That layout is what makes the relative symlink
`shared -> ../shared` resolve on both despite the different account names.

**The school network blocks npm and GitHub.** Discovered 2026-08-29 when a
build died on a missing `node_modules` and could not be fixed on site. Anything
requiring a download — `npm install`, `brew install`, a `git clone` of a new
repo — has to be done at home or on another network. Installing once per
machine is enough; it is local afterwards.

**Universal Control is on**, so the cursor crosses between the two Macs
silently. Which machine a command lands on is not obvious, and this caused real
confusion. The only reliable tell is the shell prompt: `rsalemi@Rays-Mac` is
school, `raysalemi@MacBookPro` is home. Ask rather than assume when it matters.

Cowork mounts one machine's filesystem, which is not necessarily the machine
Ray is typing on.
