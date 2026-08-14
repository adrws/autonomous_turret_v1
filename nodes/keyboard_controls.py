import zenoh, json, time, keyboard, config
from datetime import datetime
from config import Direction

system_exit_flag = False

servo_x_pos = 90
servo_y_pos = 90
motor_state = 0
prev_motor_state = 0

def setServoY(step: int):
    global servo_y_pos, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time

    if delay < 0.01:
        return
        
    data = {
        "command" : "setY",
        "angle" : f"{servo_y_pos + step}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    kinematics_commands_pub.put(json.dumps(data))

    servo_y_pos = max(0, min(servo_y_pos + step, 180))

    command_start_time = time.perf_counter()

def setServoX(step: int):
    global servo_x_pos, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time
    
    if delay < 0.01:
        return
    
    data = {
        "command" : "setX",
        "angle" : f"{servo_x_pos + step}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    camera_centering_commands_pub.put(json.dumps(data))

    servo_x_pos = max(0, min(servo_x_pos + step, 180))

    command_start_time = time.perf_counter()

def toggleMotors():
    global motor_state, prev_motor_state, command_start_time, command_end_time

    command_end_time = time.perf_counter()
    delay = command_end_time - command_start_time

    if delay < 0.01:
        return

    if prev_motor_state == 0:
        motor_state = 255
    elif prev_motor_state == 255:
        motor_state = 0

    data = {
        "command": "setSpeed",
        "motor": "left",
        "speed" : f"{motor_state}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    camera_centering_commands_pub.put(json.dumps(data))

    time.sleep(0.01)

    data["motor"] = "right"

    camera_centering_commands_pub.put(json.dumps(data))

    prev_motor_state = motor_state

    command_start_time = time.perf_counter()

def main():
    return

if __name__ == "__main__":
    
    with zenoh.open(zenoh.Config()) as session:
        kinematics_commands_pub = session.declare_publisher(config.kinematics_commands)
        camera_centering_commands_pub = session.declare_publisher(config.camera_centering_commands)

        keyboard.add_hotkey('w', setServoY, args=(1,))
        keyboard.add_hotkey('s', setServoY, args=(-1,))

        keyboard.add_hotkey('a', setServoX, args=(1,))
        keyboard.add_hotkey('d', setServoX, args=(-1,))

        keyboard.add_hotkey('e', toggleMotors)

        command_start_time = time.perf_counter()
        command_end_time = None

        while True:
            main()
            time.sleep(0.01)
            if system_exit_flag is True:
                break

        