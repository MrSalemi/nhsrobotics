# tests/regression_initbot.py -- the robot sync scripts. V01
#
# Laptop-side tests for init_bot/initialize_robot.sh. No robot: mpremote
# is replaced with a stub on PATH that records having been called, which
# is how these prove WHEN a check runs and not merely that it exists.
#
# Every test returns (status, message): 1 pass, 0 fail, 2 skip.
#
# The one claim worth testing: a source tree with a symlink pointing at
# nothing must stop the run before the robot is touched. That failure
# deleted the Alvik driver off a robot on 2026-09-04 and reported success,
# because the cleanup uses [ -d ] and [ -f ] to decide a remote file is
# stale and both of those follow symlinks.

import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "init_bot", "initialize_robot.sh")

# The stub prints nothing that looks like a port, so once the script gets
# past the symlink check it stops at "No robot found". That is fine: the
# marker file is what these tests read, not the exit code.
MPREMOTE_STUB = """#!/bin/sh
echo "$@" >> "$MPREMOTE_MARKER"
exit 0
"""


def _have_script():
    return os.path.exists(SCRIPT)


def _run_against(source_dir):
    """Run the script with a stub mpremote. Returns (proc, mpremote_used)."""
    bindir = tempfile.mkdtemp()
    marker = os.path.join(bindir, "called.log")
    stub = os.path.join(bindir, "mpremote")
    try:
        with open(stub, "w") as handle:
            handle.write(MPREMOTE_STUB)
        os.chmod(stub, 0o755)

        env = dict(os.environ)
        env["PATH"] = bindir + os.pathsep + env.get("PATH", "")
        env["MPREMOTE_MARKER"] = marker

        proc = subprocess.run(
            ["bash", SCRIPT, "-d", source_dir],
            env=env, capture_output=True, text=True, timeout=120)
        return proc, os.path.exists(marker)
    finally:
        shutil.rmtree(bindir, ignore_errors=True)


def _tree(broken=False):
    """A miniature source tree, optionally with a dangling link.

    Shaped like the real thing: the link that breaks is one level down
    inside a linked directory, because that is where nhs_lib's submodule
    links live and a shallower check would miss them.
    """
    root = tempfile.mkdtemp()
    real_lib = os.path.join(root, "reallib")
    source = os.path.join(root, "src")
    os.makedirs(real_lib)
    os.makedirs(source)

    with open(os.path.join(real_lib, "present.py"), "w") as handle:
        handle.write("# a real file\n")
    with open(os.path.join(source, "main.py"), "w") as handle:
        handle.write("import present\n")

    # src/lib -> ../reallib, the same shape as phy_robot/lib.
    os.symlink(os.path.join("..", "reallib"), os.path.join(source, "lib"))

    # And inside it, a link standing in for arduino_alvik.
    target = "elsewhere" if broken else "present.py"
    os.symlink(target, os.path.join(real_lib, "driver.py"))

    return root, source


def test_a_broken_symlink_stops_the_run():
    """A dangling link must abort BEFORE mpremote is ever called."""
    if not _have_script():
        return 2, "initialize_robot.sh not present"
    root, source = _tree(broken=True)
    try:
        proc, used_mpremote = _run_against(source)
        if proc.returncode == 0:
            return 0, "script succeeded with a broken symlink in the tree"
        if used_mpremote:
            return 0, ("mpremote was called anyway, so the check runs too "
                       "late to protect the robot")
        if "driver.py" not in proc.stdout:
            return 0, ("the broken link was not named in the output:\n%s"
                       % proc.stdout[-600:])
        return 1, ""
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_the_error_says_how_to_fix_it():
    """Naming the problem is half a fix; the command is the other half."""
    if not _have_script():
        return 2, "initialize_robot.sh not present"
    root, source = _tree(broken=True)
    try:
        proc, _ = _run_against(source)
        if "git submodule update" not in proc.stdout:
            return 0, "the error never mentions git submodule update"
        return 1, ""
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_a_healthy_tree_is_not_blocked():
    """The guard must not stand in the way of a normal sync.

    Without this the check could be a plain `exit 1` and the test above
    would still pass.
    """
    if not _have_script():
        return 2, "initialize_robot.sh not present"
    root, source = _tree(broken=False)
    try:
        proc, used_mpremote = _run_against(source)
        if not used_mpremote:
            return 0, ("the script never reached mpremote on a tree with no "
                       "broken links:\n%s" % proc.stdout[-600:])
        return 1, ""
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_the_real_source_trees_are_intact():
    """The three trees Ray actually syncs, checked as they are on disk.

    This is the one that would have caught 2026-09-04 before a robot was
    plugged in. It fails on a machine whose submodules are not checked
    out, which is the point.
    """
    if not _have_script():
        return 2, "initialize_robot.sh not present"
    broken = []
    for name in ("nhs_robot", "phy_robot", "eng_bot"):
        tree = os.path.join(REPO, "init_bot", name)
        if not os.path.isdir(tree):
            continue
        found = subprocess.run(
            ["find", "-L", tree, "-type", "l"],
            capture_output=True, text=True)
        broken.extend(line for line in found.stdout.split("\n") if line)
    if broken:
        relative = [os.path.relpath(path, REPO) for path in sorted(broken)]
        return 0, ("dangling links, so a sync would delete these off a "
                   "robot: %s -- run: git submodule update --init "
                   "--recursive" % ", ".join(relative))
    return 1, ""
