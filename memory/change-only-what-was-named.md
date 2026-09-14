---
name: change-only-what-was-named
description: "Ray names the thing to change. Change that thing and nothing adjacent, even when the neighbour is obviously the same kind of number."
metadata:
  node_type: memory
  type: feedback
---

When Ray names what to change, the change stops there. A neighbouring
value of the same kind is not in scope just because it sits in the same
table and would have been consistent to change.

**Why:** on 2026-09-14 he said the *constant speed* robot ran twice too
fast and to make it run half as fast. I halved the constant mode and also
halved both acceleration runs, because scaling every mode together keeps
the graphs' shapes identical and felt like the coherent edit. His answer:
*"No. I did not ask you to change the acceleration. Put it back."* The
symmetry was real and the physics argument was sound; neither was the
point. He had watched one mode on the floor and formed a judgement about
that mode. The other two he had not looked at, and changing them threw
away numbers he had already accepted.

**How to apply:** take the scope from his words, not from the structure
of the code. "The constant speed robot" means the CONSTANT entry, not the
mode table. If an adjacent change looks necessary for consistency, make
the named change, then say in one line what the neighbour now disagrees
with and let him decide — that reply is short and it is his call. When he
says put something back, restore it exactly, to the byte, and check the
diff shows nothing else moved. Related: [[answer-the-question-asked]].
