import zenoh, config, json, time, math
from collections import deque
from datetime import datetime

error_data = deque(maxlen= 100)
servo_x_pos = 90
pixel_focal_length = 4 / 0.0028

kp = 1.0
ki = 1.0
kd = 1.0

command_recieved_flag = None

def proportionalAlgorithm() -> float:
    x = error_data[-1]

    if x in range(-30, 31):
        return 0
    
    offset = math.atan2(x, pixel_focal_length)

    return offset

def integralAlgorithm() -> float:
    return 0

def derivativeAlgorithm() -> float:
    return 0

def main():
    global algorithm_start_time
    global kp, ki, kd
    global servo_x_pos, command_recieved_flag, error_data

    algorithm_end_time = time.perf_counter()
    algorithm_delay = algorithm_end_time - algorithm_start_time

    if algorithm_delay > 0.01:
        return
    if command_recieved_flag is False:
        return
    
    proportional_val = proportionalAlgorithm()
    integral_val = integralAlgorithm()
    derivative_val = derivativeAlgorithm()

    servo_offset = int((kp * proportional_val) + (ki * integral_val) + (kd * derivative_val))

    sendServoJSON(servo_offset)

    servo_x_pos += servo_offset

    command_recieved_flag = False
    algorithm_start_time = time.perf_counter()

       
if __name__ == "__main__":
    with zenoh.open(zenoh.Config()) as session:

        def camera_centering_data_cb(sample: zenoh.Sample):
            data = json.loads(sample.payload.to_string())
            error = int(data["error"])
            error_data.append(error)

        def camera_centering_feedback_cb(sample: zenoh.Sample):
            data = json.loads(sample.payload.to_string())
            command_recieved = bool(data["command_recieved"])
            command_recieved_flag = command_recieved

        def sendServoJSON(offset):
            data = {
                "command" : "setX",
                "angle" : f"{servo_x_pos + offset}",
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            camera_centering_pub.put(json.dumps(data))
            
        camera_centering_sub = session.declare_subscriber(config.camera_centering_data, camera_centering_data_cb)
        camera_centering_pub = session.declare_publisher(config.camera_centering_commands)
        hardware_sub = session.declare_subscriber(config.camera_centering_feedback)

        algorithm_start_time = time.perf_counter()

        main()

