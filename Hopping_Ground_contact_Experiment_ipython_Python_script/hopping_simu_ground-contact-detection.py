import matplotlib
matplotlib.use('TkAgg')  # Use the TkAgg backend for matplotlib
import time
from odrive.enums import *  # Import all constants from the odrive.enums module
from odrive.utils import start_liveplotter, dump_errors  # Import specific utility functions from the odrive.utils module
import odrive  # Import the main odrive module
import threading  # Import the threading module to enable multithreading
from odrive.enums import AXIS_STATE_IDLE  # Import the specific constant AXIS_STATE_IDLE from the odrive.enums module

def main():
    print("Finding an ODrive...")
    odrv0 = odrive.find_any()  # Attempt to find and connect to an ODrive

    # Ensure the motor is in closed-loop control mode
    odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    # Set up the live plotter function
    def get_motor_data():
        # Fetch the current phase currents
        phase_current_a = odrv0.axis0.motor.current_control.Iq_measured
        phase_current_b = odrv0.axis0.motor.current_control.Id_measured

        # Fetch the motor voltage and motor resistance and inductance
        motor_voltage = odrv0.vbus_voltage
        motor_resistance = odrv0.axis0.motor.config.phase_resistance
        motor_inductance = odrv0.axis0.motor.config.phase_inductance

        # Calculate the back EMF for each phase
        back_emf_a = motor_voltage - motor_resistance * phase_current_a - motor_inductance * phase_current_b
        back_emf_b = motor_voltage - motor_resistance * phase_current_b - motor_inductance * phase_current_a

        # Return the calculated values as a list
        return [
            back_emf_a, back_emf_b,
            phase_current_a, phase_current_b,
        ]

    print("Starting live plotter...")
    # Start the live plotter in a new thread
    plotter_thread = threading.Thread(target=start_liveplotter, args=(get_motor_data, ['Back EMF A', 'Back EMF B',
                                                                                       'Phase Current A', 'Phase Current B']))
    plotter_thread.start()

    def leg_hop():
        while True:
            # Check if the motor is in closed-loop control mode
            if odrv0.axis0.current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
                # Move the leg to position 0 and then to position -5 with a pause in between
                odrv0.axis0.controller.pos_setpoint = 0
                time.sleep(1.5)
                odrv0.axis0.controller.pos_setpoint = -5
                time.sleep(1.5)
            else:
                # If the motor is not in closed-loop control mode, print a message and wait before trying again
                print("Axis not in closed loop control. Current state: ", odrv0.axis0.current_state)
                time.sleep(1)  # Wait a bit before trying again

    # Start the hopping function in a new thread
    hop_thread = threading.Thread(target=leg_hop)
    hop_thread.start()

    print("Enter commands to control ODrive. Type 'quit' to exit.")
    while True:
        # Get input from the user
        command = input("> ")

        # If the command is "quit", break the loop
        if command == "quit":
            break
        else:
            # Attempt to execute the command
            try:
                exec(command, {"odrv0": odrv0, "AXIS_STATE_IDLE": AXIS_STATE_IDLE
