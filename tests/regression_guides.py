# tests/regression_guides.py -- guide-level regression. V02
#
# Every block in P09 is either a pattern quoted from an earlier
# project's guide or WORK 1's given code, quoted from P09's own
# scaffold. Nothing used to check that the quote still matched
# the project it came from: P08 changed on 2026-10-20 and P09 went on
# printing a P08 that no longer existed. These checks are that guard.
#
# Every test returns (status, message): 1 pass, 0 fail, 2 skip.

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GUIDES = os.path.join(REPO, "guides")
PROJECTS = os.path.join(REPO, "projects")

# Guides whose code blocks are all quotes from earlier guides.
QUOTING_GUIDES = ("p09.md",)

_FENCE = re.compile(r"^```.*?$\n(.*?)^```\s*$", re.M | re.S)
_CAPS_NAME = re.compile(r"`([A-Z][A-Z0-9_]*)`")
_DEFINED = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=", re.M)


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def code_blocks(text):
    """The fenced blocks in a guide, each as a list of lines."""
    return [block.rstrip("\n").split("\n") for block in _FENCE.findall(text)]


def _earlier_guides(guide):
    number = int(guide[1:3])
    names = sorted(name for name in os.listdir(GUIDES)
                   if re.fullmatch(r"p\d\d\.md", name)
                   and int(name[1:3]) < number)
    return [(name, _read(os.path.join(GUIDES, name))) for name in names]


def _contains(haystack, needle):
    width = len(needle)
    return any(haystack[i:i + width] == needle
               for i in range(len(haystack) - width + 1))


def _dedented(lines, width):
    pad = " " * width
    return [line[width:] if line.startswith(pad) else line for line in lines]


def _in_own_scaffold(guide, block):
    """True when the block is given code in this project's own scaffold,
    at any indent the loop puts it at."""
    path = _scaffold_for(int(guide[1:3]))
    if not path:
        return False
    lines = _read(path).split("\n")
    return any(_contains(_dedented(lines, width), block)
               for width in (0, 4, 8, 12))


def quotes_missing_from_earlier_guides(guide, text=None):
    """Blocks in `guide` that appear word for word in neither an earlier
    guide nor this project's own scaffold."""
    if text is None:
        text = _read(os.path.join(GUIDES, guide))
    earlier = [code_blocks(body) for _name, body in _earlier_guides(guide)]
    missing = []
    for block in code_blocks(text):
        if _in_own_scaffold(guide, block):
            continue
        if not any(_contains(source, block)
                   for blocks in earlier for source in blocks):
            missing.append(block)
    return missing


def _scaffold_for(number):
    for name in os.listdir(PROJECTS):
        if name.startswith("p%02d_" % number) and name.endswith(".py"):
            return os.path.join(PROJECTS, name)
    return None


def names_defined_nowhere(guide, text=None):
    """CAPS names in backticks that neither this project's scaffold nor
    any earlier scaffold defines."""
    if text is None:
        text = _read(os.path.join(GUIDES, guide))
    number = int(guide[1:3])
    defined = set()
    for n in range(number + 1):
        path = _scaffold_for(n)
        if path:
            defined.update(_DEFINED.findall(_read(path)))
    used = set(_CAPS_NAME.findall(text))
    return sorted(name for name in used if name not in defined)


def test_quoted_patterns_match_their_projects():
    """Every block in a quoting guide must still be in an earlier guide."""
    for guide in QUOTING_GUIDES:
        missing = quotes_missing_from_earlier_guides(guide)
        if missing:
            return 0, "%s quotes code no earlier guide has: %r" % (
                guide, missing[0][0])
    return 1, ""


def test_named_constants_exist():
    """A name the guide puts in backticks must exist in a scaffold."""
    for guide in QUOTING_GUIDES:
        unknown = names_defined_nowhere(guide)
        if unknown:
            return 0, "%s names %s, which no scaffold defines" % (
                guide, ", ".join(unknown))
    return 1, ""


def test_the_checks_can_fail():
    """The two checks above are only worth anything if they catch the
    bug that started this: P09 quoting an ADVANCING state P08 dropped."""
    stale = "```\nelif current_state == ADVANCING:\n    pass\n```\n"
    if not quotes_missing_from_earlier_guides("p09.md", stale):
        return 0, "a quote of a deleted P08 state was not caught"
    if not names_defined_nowhere("p09.md", "Use `STUBBORN_CM` here."):
        return 0, "a name no scaffold defines was not caught"
    return 1, ""
