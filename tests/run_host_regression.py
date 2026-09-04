# tests/run_host_regression.py
#
# The laptop half of the regression suite. V01
#
#     python3 tests/run_host_regression.py
#
# Runs every test that needs no robot, using the same RegressionRunner and the
# same PASS/FAIL/SKIP output as run_regression.py. Use this before flashing a
# change to nhs_lib. run_regression.py runs these too, plus everything that
# needs real hardware.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

for path in (HERE, os.path.join(REPO, "nhs_lib")):
    if path not in sys.path:
        sys.path.insert(0, path)

from regression_utils import RegressionRunner
import regression_host


def main():
    print("Initializing Host Regression Suite (no robot required)...")

    runner = RegressionRunner()

    print("\n--- Running Host Tests ---")
    runner.run_test("Host: light_both_leds", regression_host.test_light_both_leds)
    runner.run_test("Host: Stick Deadzone", regression_host.test_stick_deadzone)
    runner.run_test("Host: Gamepad held/pressed", regression_host.test_gamepad_held_and_pressed)
    runner.run_test("Host: Touch held/pressed", regression_host.test_touch_held_and_pressed)
    runner.run_test("Host: Unknown Button Name", regression_host.test_unknown_button_name_raises)
    runner.run_test("Host: Closest valid distance", regression_host.test_closest_valid)
    runner.run_test("Host: Missing HuskyLens is not an error",
                    regression_host.test_missing_huskylens_is_not_an_error)

    print("\n--- Running Robot Sync Tests ---")
    import regression_initbot
    runner.run_test("Sync: a broken symlink stops the run",
                    regression_initbot.test_a_broken_symlink_stops_the_run)
    runner.run_test("Sync: the error says how to fix it",
                    regression_initbot.test_the_error_says_how_to_fix_it)
    runner.run_test("Sync: a healthy tree is not blocked",
                    regression_initbot.test_a_healthy_tree_is_not_blocked)
    runner.run_test("Sync: the real source trees are intact",
                    regression_initbot.test_the_real_source_trees_are_intact)

    print("\n--- Running Solution Tests (testbench) ---")
    import regression_solutions
    from run_solution_regression import TESTS as SOLUTION_TESTS
    for name, func in SOLUTION_TESTS:
        runner.run_test(name, func)

    runner.print_summary()
    return 1 if runner.fails else 0


if __name__ == "__main__":
    sys.exit(main())
