"""
keyboard_controls.py
 
Manual keyboard controls for the turret.
 
Listens for key presses and publishes servo/motor commands over
Zenoh so the turret can be driven manually during data collection and training.
 
Topics published to:
    - config.kinematics_commands        -> servo Y (tilt) angle commands
    - config.camera_centering_commands  -> servo X (pan) angle commands AND
                                            drive motor speed commands
 
Controls:
    W / S -> tilt servo up / down
    A / D -> pan servo left / right
    E     -> toggle drive motors

"""

import zenoh, json, time, keyboard, config
from datetime import datetime

system_exit_flag = False

servo_x_pos = 90
prev_servo_x_pos = 0
servo_y_pos = 90
prev_servo_y_pos = 0
motor_state = 0
prev_motor_state = 0

def setServoY(step: int):
    """
    Adjust the tilt (Y) servo angle by `step` degrees and publish the new
    angle, if enough time has passed since the last command and the angle actually changed.
    """

    global servo_y_pos, prev_servo_y_pos, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time

    if delay < 0.01: # Checks timer.
        return

    servo_y_pos = max(0, min(servo_y_pos + step, 180)) # Clamps angle to acceptable value for servo.
        
    data = {
        "command" : "setY",
        "angle" : f"{servo_y_pos}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if servo_y_pos != prev_servo_y_pos: # Checks if the value is not the same as the previous command to send.
        kinematics_commands_pub.put(json.dumps(data))

    prev_servo_y_pos = servo_y_pos 
    command_start_time = time.perf_counter()

def setServoX(step: int):
    """
    Adjust the pan (X) servo angle by `step` degrees and publish the new
    angle, if enough time has passed since the last command and the angle actually changed.
    """
    
    global servo_x_pos, prev_servo_x_pos, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time
    
    if delay < 0.01:
        return

    servo_x_pos = max(0, min(servo_x_pos + step, 180))
    
    data = {
        "command" : "setX",
        "angle" : f"{servo_x_pos}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if servo_x_pos != prev_servo_x_pos:
        camera_centering_commands_pub.put(json.dumps(data))

    prev_servo_x_pos = servo_x_pos
    command_start_time = time.perf_counter()

def toggleMotors():
    """
    Flip the drive motors between stopped (0) and full speed (255), and
    publish a speed command for each motor (left, then right).
 
    Has a delay between commands, but not intended to repeat quickly on a held key.
    """

    global motor_state, prev_motor_state, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time

    if delay < 0.5:
        return

    if prev_motor_state == 0: # Sets the motor speed to the opposite value of what it currently is.
        motor_state = 255
    elif prev_motor_state == 255:
        motor_state = 0

    data = {
        "command": "setSpeed",
        "motor": "left",
        "speed" : f"{motor_state}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    camera_centering_commands_pub.put(json.dumps(data)) # Sends the command for the left motor.

    time.sleep(0.01)
    data["motor"] = "right" # Uses the same command but sets the direction to right.

    camera_centering_commands_pub.put(json.dumps(data)) # Sends command for the right motor.

    prev_motor_state = motor_state 

    command_start_time = time.perf_counter()

if __name__ == "__main__":
    
    with zenoh.open(zenoh.Config()) as session:
        kinematics_commands_pub = session.declare_publisher(config.kinematics_commands) # Setting up command publishers.
        camera_centering_commands_pub = session.declare_publisher(config.camera_centering_commands)

        keyboard.add_hotkey('w', setServoY, args=(1,)) # Creating hotkeys that run functions when pressed.
        keyboard.add_hotkey('s', setServoY, args=(-1,))

        keyboard.add_hotkey('a', setServoX, args=(-1,))
        keyboard.add_hotkey('d', setServoX, args=(1,))

        keyboard.add_hotkey('e', toggleMotors)

        command_start_time = time.perf_counter() # Setting up global timer for commands.

        while True: 
            time.sleep(0.05)
            if system_exit_flag is True:
                break

        