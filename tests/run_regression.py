# tests/run_regression.py

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import sys


if "/tests" not in sys.path:
    sys.path.append("/tests")


from regression_utils import RegressionRunner
import regression_logic
import regression_hardware
import regression_peripherals
import regression_filesystem
import regression_line_follower
import regression_host

def main():
    print("Initializing Regression Suite...")

    # Initialize base hardware
    alvik = ArduinoAlvik()
    alvik.begin()

    # Initialize SuperBot wrapper
    bot = SuperBot(alvik)

    runner = RegressionRunner()

    # Same tests run_host_regression.py runs on a laptop. They need no
    # hardware, so a robot run covers them too.
    print("\n--- Running Host Tests ---")
    runner.run_test("Host: light_both_leds", regression_host.test_light_both_leds)
    runner.run_test("Host: Stick Deadzone", regression_host.test_stick_deadzone)
    runner.run_test("Host: Gamepad held/pressed", regression_host.test_gamepad_held_and_pressed)
    runner.run_test("Host: Touch held/pressed", regression_host.test_touch_held_and_pressed)
    runner.run_test("Host: Unknown Button Name", regression_host.test_unknown_button_name_raises)

    print("\n--- Running Logic Tests ---")
    runner.run_test("Host: Closest valid distance", regression_host.test_closest_valid)
    runner.run_test("Host: Center touch pad", regression_host.test_center_pad)
    runner.run_test("Host: LINE_THRESHOLD splits white from black",
                    regression_host.test_line_threshold)
    runner.run_test("Host: follow_line has no kick after reset",
                    regression_host.test_follow_line_no_kick_after_reset)
    runner.run_test("Host: Missing HuskyLens is not an error",
                    regression_host.test_missing_huskylens_is_not_an_error)
    runner.run_test("Logic: Calculate Approach Vector", regression_logic.test_calculate_approach_vector, bot)
    runner.run_test("Logic: Logging", regression_logic.test_logging, bot)
    runner.run_test("Logic: LineFollower PID", regression_line_follower.test_line_follower_logic, bot)

    print("\n--- Running Hardware Tests ---")
    runner.run_test("Hardware: API Integrity", regression_hardware.test_api_integrity, bot)
    runner.run_test("Hardware: NanoLED", regression_hardware.test_nano_led, bot)
    runner.run_test("Hardware: Built-in LEDs", regression_hardware.test_builtin_leds, bot)
    runner.run_test("Hardware: Sensor Yaw", regression_hardware.test_sensor_yaw, bot)
    runner.run_test("Hardware: ToF Sensors", regression_hardware.test_tof, bot)
    runner.run_test("Hardware: Line Sensors", regression_hardware.test_line_sensors, bot)
    runner.run_test("Hardware: LineFollower Sensors", regression_line_follower.test_line_follower_sensors, bot)
    runner.run_test("Hardware: Touch Buttons", regression_hardware.test_buttons, bot)
    runner.run_test("Hardware: Motor Drive", regression_hardware.test_motor_drive, bot)
    runner.run_test("Hardware: Motor Rotate", regression_hardware.test_motor_rotate, bot)
    runner.run_test("Hardware: Servo Sweep", regression_hardware.test_servo, bot)

    print("\n--- Running Peripheral Tests ---")
    runner.run_test("Peripheral: Gamepad Controller Init", regression_peripherals.test_gamepad_init, bot)
    runner.run_test("Peripheral: OLED", regression_peripherals.test_oled, bot)
    runner.run_test("Peripheral: Buzzer", regression_peripherals.test_buzzer, bot)
    runner.run_test("Peripheral: HuskyLens", regression_peripherals.test_huskylens, bot)

    print("\n--- Running Filesystem Tests ---")
    runner.run_test("Filesystem: File Operations", regression_filesystem.test_filesystem_unicode, bot)

    runner.print_summary()

if __name__ == "__main__":
    main()
