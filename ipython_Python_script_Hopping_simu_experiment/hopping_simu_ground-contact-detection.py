import matplotlib
matplotlib.use('TkAgg')
import time
from odrive.enums import *
from odrive.utils import start_liveplotter, dump_errors
import odrive
import threading
from odrive.enums import AXIS_STATE_IDLE

def main():
    print("Finding an ODrive...")
    odrv0 = odrive.find_any()

    # Ensure the motor is in closed-loop control mode
    odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    # Set up the live plotter function
    def get_motor_data():
        phase_current_a = odrv0.axis0.motor.current_control.Iq_measured
        phase_current_b = odrv0.axis0.motor.current_control.Id_measured

        motor_voltage = odrv0.vbus_voltage
        motor_resistance = odrv0.axis0.motor.config.phase_resistance
        motor_inductance = odrv0.axis0.motor.config.phase_inductance

        back_emf_a = motor_voltage - motor_resistance * phase_current_a - motor_inductance * phase_current_b
        back_emf_b = motor_voltage - motor_resistance * phase_current_b - motor_inductance * phase_current_a

        return [
            back_emf_a, back_emf_b,
            phase_current_a, phase_current_b,
        ]

    print("Starting live plotter...")
    plotter_thread = threading.Thread(target=start_liveplotter, args=(get_motor_data, ['Back EMF A', 'Back EMF B',
                                                                                       'Phase Current A', 'Phase Current B']))
    plotter_thread.start()

    def leg_hop():
        while True:
            if odrv0.axis0.current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
                odrv0.axis0.controller.pos_setpoint = 0
                time.sleep(1.5)
                odrv0.axis0.controller.pos_setpoint = -5
                time.sleep(1.5)
            else:
                print("Axis not in closed loop control. Current state: ", odrv0.axis0.current_state)
                time.sleep(1)  # Wait a bit before trying again


    hop_thread = threading.Thread(target=leg_hop)
    hop_thread.start()

    print("Enter commands to control ODrive. Type 'quit' to exit.")
    while True:
        command = input("> ")

        if command == "quit":
            break
        else:
            try:
                exec(command, {"odrv0": odrv0, "AXIS_STATE_IDLE": AXIS_STATE_IDLE, "dump_errors": dump_errors})
            except Exception as e:
                print("Error executing command:", e)

    print("Exiting...")

if __name__ == '__main__':
    main()
