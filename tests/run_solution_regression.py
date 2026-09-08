# tests/run_solution_regression.py
#
# The solution-level regression. V02
#
#     python3 tests/run_solution_regression.py
#     python3 tests/run_solution_regression.py -v      # coverage report too
#
# Runs the real files out of solutions/ inside the testbench in tests/tb/.
# No robot, no simulator, no wall-clock time -- the DUT's own sleep drives
# a simulated clock, so the whole suite finishes in well under a second.
#
# run_host_regression.py calls this too. Use this one when you are working
# on a solution and want the shorter output.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

for path in (HERE, os.path.join(REPO, "nhs_lib")):
    if path not in sys.path:
        sys.path.insert(0, path)

from regression_utils import RegressionRunner
import regression_solutions as solutions
import regression_move as move


TESTS = [
    ("Solutions: every solution compiles",
     solutions.test_every_solution_compiles),
    ("Solutions: no floor division",
     solutions.test_no_solution_uses_floor_division),
    ("Scaffolds: every scaffold compiles",
     solutions.test_every_project_scaffold_compiles),
    ("Scaffolds: every scaffold has a FLEX line",
     solutions.test_every_scaffold_has_a_flex_line),

    ("P08: stands its ground runs every state",
     solutions.test_p08_stands_its_ground_runs_the_whole_machine),
    ("P08: lets a fleeing target go",
     solutions.test_p08_lets_a_fleeing_target_go),
    ("P08: empty room never leaves patrol",
     solutions.test_p08_empty_room_never_leaves_patrol),
    ("P08: works with no screen", solutions.test_p08_works_with_no_screen_either),

    ("P09: stays in the ring", solutions.test_p09_stays_in_the_ring),
    ("P09: charges what is in front",
     solutions.test_p09_charges_what_is_in_front_of_it),
    ("P09: edge beats the charge", solutions.test_p09_edge_beats_the_charge),
    ("P09: waits for the start button",
     solutions.test_p09_waits_for_the_start_button),
    ("P09: Cancel stops it before the match",
     solutions.test_p09_cancel_stops_it_before_the_match),

    ("Line: squares up (directed)", solutions.test_line_squares_up_from_one_approach),
    ("Line: squares up (40 generated approaches)",
     solutions.test_line_random_approaches),
    ("Line: immune to odometry scale",
     solutions.test_line_immune_to_odometry_scale),
    ("Line: reaches every state", solutions.test_line_reaches_every_state),
    ("Line: dead sensors never drive",
     solutions.test_line_dead_sensors_never_drive),
    ("Line: slow sensors still work",
     solutions.test_line_slow_sensors_still_work),
    ("Line: survives ticks_ms rollover",
     solutions.test_line_survives_clock_rollover),
    ("Line: works with no screen", solutions.test_line_works_with_no_screen),
    ("Line: Cancel stops it", solutions.test_line_cancel_stops_it),

    # Physics -- init_bot/phy_robot/move.py
    ("Move: constant holds its speed",
     move.test_constant_holds_its_speed),
    ("Move: accelerate forwards gives the squares",
     move.test_accelerate_forwards_gives_the_squares),
    ("Move: accelerate backwards slows down",
     move.test_accelerate_backwards_slows_down),
    ("Move: stopped does not move",
     move.test_stopped_does_not_move),
    ("Move: down is backwards in every mode",
     move.test_down_is_backwards_in_every_mode),
    ("Move: right steps forwards through the modes",
     move.test_right_steps_forwards_through_the_modes),
    ("Move: left steps backwards and wraps",
     move.test_left_steps_backwards_and_wraps),
    ("Move: the arrows do nothing before OK",
     move.test_the_arrows_do_nothing_before_ok),
    ("Move: the mode cannot change after OK",
     move.test_the_mode_cannot_change_after_ok),
    ("Move: the lights say which state it is in",
     move.test_the_lights_say_which_state_it_is_in),
    ("Move: a run lasts six seconds",
     move.test_a_run_lasts_six_seconds),
    ("Move: it goes back to waiting after a run",
     move.test_it_goes_back_to_waiting_after_a_run),
    ("Move: an arrow during a run is ignored",
     move.test_an_arrow_during_a_run_is_ignored),
    ("Move: Cancel quits from selection",
     move.test_cancel_quits_from_selection),
    ("Move: Cancel quits during a run",
     move.test_cancel_quits_during_a_run),
    ("Move: the lights go out at the end",
     move.test_the_lights_go_out_at_the_end),
    ("Move: immune to the drive() speed error",
     move.test_immune_to_the_drive_speed_error),
    ("Move: the readings check has teeth",
     move.test_the_readings_check_has_teeth),
    ("Move: never asks for more than the robot has",
     move.test_it_never_asks_for_more_than_the_robot_has),
    ("Move: drive() is not re-issued every pass",
     move.test_drive_is_not_re_issued_every_pass),
]


def main():
    verbose = "-v" in sys.argv
    print("Initializing Solution Regression Suite (no robot required)...")
    print("\n--- Running Solution Tests ---")

    runner = RegressionRunner()
    for name, func in TESTS:
        runner.run_test(name, func)

    if verbose:
        print("\n--- Coverage ---")
        print(solutions.coverage_report())

    runner.print_summary()
    return 1 if runner.fails else 0


if __name__ == "__main__":
    sys.exit(main())
