---
name: start-at-the-output
description: When something renders or builds wrong, examine the artifact first — don't theorise about causes from console output.
metadata:
  type: feedback
---

Ray's instruction, verbatim: *"You have to stop guessing. Start at the output
and work back."*

**Why:** on 2026-08-29 two Macs produced different page counts for the same
guide. I spent well over an hour proposing causes from console text — font
cache, LibreOffice version, node version, a reboot — and had Ray run each one.
The answer took ninety seconds once I actually opened the PDF: `pdffonts`
showed the code blocks had rendered in a serif *proportional* face on one
machine. Every hypothesis before that was wrong, and each one cost him a
round-trip.

**How to apply:** inspect the artifact before reasoning about the pipeline.
`pdfinfo` and `pdffonts` for PDFs; render a page with `pdftoppm` and look at it.
For any build, ask what the output actually contains before asking why it might
differ. And when comparing two environments, verify the inputs are identical
first — several of my comparisons that night were between two different
versions of the source, because an edit of mine was never committed.

Related: [[no-git-writes-through-cowork-mount]].
