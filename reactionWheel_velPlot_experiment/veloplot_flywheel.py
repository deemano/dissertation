import matplotlib
matplotlib.use('TkAgg')
import time
from odrive.enums import *
from odrive.utils import start_liveplotter, dump_errors
import odrive
import threading
from odrive.enums import AXIS_STATE_IDLE

# Define the time interval
time_interval = 0.1  # Adjust this to match your actual loop frequency
scaling_factor = 10  # Define a scaling factor

def main():
    print("Finding an ODrive...")
    dev1 = odrive.find_any()

    # Ensure the motor is in closed-loop control mode
    dev1.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    # Set up the live plotter function
    def get_motor_data():
        velocity = dev1.axis0.encoder.vel_estimate  # velocity estimate from the encoder

        # Modify these lines in get_motor_data():
        acceleration = ((velocity - get_motor_data.prev_vel) / time_interval) * scaling_factor
        deceleration = ((get_motor_data.prev_vel - velocity) / time_interval) * scaling_factor
        phase_current_a = dev1.axis0.motor.current_control.Iq_measured * scaling_factor
        phase_current_b = dev1.axis0.motor.current_control.Id_measured * scaling_factor

        get_motor_data.prev_vel = velocity  # store current velocity for next loop

        return [
            acceleration, deceleration,
            phase_current_a, phase_current_b,
        ]

    get_motor_data.prev_vel = 0  # Initialize prev_vel

    def stop_motor(dev1):
        dev1.axis0.requested_state = AXIS_STATE_IDLE

    print("Starting live plotter...")
    plotter_thread = threading.Thread(target=start_liveplotter, args=(get_motor_data, ['Acceleration', 'Deceleration',
                                                                                       'Phase Current A', 'Phase Current B']))
    plotter_thread.start()

    print("Enter commands to control ODrive. Type 'quit' to exit.")
    while True:
        command = input("> ")

        if command == "quit":
            break
        elif command == "":
            stop_motor(dev1)
        elif command == "1":
            dev1.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        else:
            try:
                exec(command, {"dev1": dev1, "AXIS_STATE_IDLE": AXIS_STATE_IDLE, "dump_errors": dump_errors})
            except Exception as e:
                print("Error executing command:", e)


    print("Exiting...")

if __name__ == '__main__':
    main()
