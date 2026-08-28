import zenoh, config, json, time, math
from collections import deque 
from datetime import datetime
from config import Direction

error_data = deque([0] * 100,maxlen= 100) 
time_data : deque[float] = deque([0] * 100,maxlen= 100) 
error_data_integral : deque[float] = deque([0] * 100,maxlen= 100) 
error_data_derivative : deque[float] = deque([0] * 100,maxlen= 100)
servo_x_pos = 90
pixel_focal_length = 4 / 0.0028
prev_right_motor_state = 0
prev_left_motor_state = 0

# PID values
kp = 0.5 
ki = 0.0 
kd = 0.1

command_recieved_flag = None
data_recieved_flag = False

def proportionalAlgorithm() -> float:
    x = error_data[-1] 

    if x == 0:
        return 0 
    
    offset = (math.atan2(x, pixel_focal_length)) * (180/math.pi) 

    return offset

def integralAlgorithm() -> float:
    x = error_data[-1]

    if x == 0:
        error_data_integral.clear()
        return 0
    else:
        offset = (math.atan2(x, pixel_focal_length)) * (180/math.pi)

        if len(time_data) >= 2:
            dt = time_data[-1] - time_data[-2]
        else:
            dt = 0.0

        error_data_integral.append(offset * dt) 

    offset_integ = sum(error_data_integral)  

    return max(-13, min(offset_integ, 13))


def derivativeAlgorithm() -> float:
    y2 = (math.atan2(error_data[-1], pixel_focal_length)) * (180/math.pi) 
    y1 = (math.atan2(error_data[-2], pixel_focal_length)) * (180/math.pi)
    x2 = time_data[-1]
    x1 = time_data[-2]

    dt = x2 - x1
    if dt <= 0:
        return 0.0

    offset_deriv = (y2-y1) / dt

    return offset_deriv

def main():
    while True:
        global algorithm_start_time, centered_end_time, centered_duration
        global kp, ki, kd
        global servo_x_pos, command_recieved_flag, data_recieved_flag, error_data, error_data_integral, centered_flag

        algorithm_end_time = time.perf_counter()
        algorithm_delay = algorithm_end_time - algorithm_start_time

        if algorithm_delay < 0.005: 
            continue

        proportional_val = proportionalAlgorithm()
        integral_val = integralAlgorithm()
        derivative_val = derivativeAlgorithm()

        servo_offset = int((kp * proportional_val) + (ki * integral_val) + (kd * derivative_val))

        print(f"servo_offset = (kp: {kp} * P: {proportional_val}) + (ki: {ki} * I: {integral_val}) + (kd: {kd} * D: {derivative_val}) = {servo_offset}")

        
        if data_recieved_flag is True:
            sendServoCMD(servo_offset)


        centered_end_time = time.perf_counter()
        centered_duration = centered_end_time - centered_start_time

        if centered_flag: 
            sendMotorCMD(255, Direction.left)
            sendMotorCMD(255, Direction.right)
        else:
            sendMotorCMD(0, Direction.left)
            sendMotorCMD(0, Direction.right)

        data_recieved_flag = False
        algorithm_start_time = time.perf_counter()

       
if __name__ == "__main__": 
    with zenoh.open(zenoh.Config()) as session:

        def camera_centering_data_cb(sample: zenoh.Sample): 
            global data_recieved_flag, centered_start_time, centered_end_time, centered_flag, centered_duration
            data = json.loads(sample.payload.to_string()) 
            error = int(data["error"]) 

            if -config.deadzone <= error <= config.deadzone:
                error_data.append(0) 
            else:
                error_data.append(error) 

            t = float(data["time"]) 
            time_data.append(t)

            if error_data[-1] == 0 and error_data[-2] != 0: 
                centered_start_time = time.perf_counter()
            elif error_data[-1] != 0: 
                centered_flag = False

            centered_flag = error_data[-1] == 0 and centered_duration > 0.5

            data_recieved_flag = True


        def sendServoCMD(offset): 
            global servo_x_pos

            data = {
                "command" : "setX",
                "angle" : f"{servo_x_pos + offset}",
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            camera_centering_pub.put(json.dumps(data))

            servo_x_pos = max(0, min(servo_x_pos + offset, 180))

        def sendMotorCMD(pwm: int, direction: config.Direction): 
            global prev_left_motor_state, prev_right_motor_state

            stale_right_command = direction.name == "right" and prev_right_motor_state == pwm
            stale_left_command = direction.name == "left" and prev_left_motor_state == pwm

            if stale_right_command or stale_left_command: 
                return

            data = {
            "command": "setSpeed",
            "motor": f"{direction.name}",
            "speed" : f"{pwm}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if direction.name == "right":
                prev_right_motor_state = pwm
            elif direction.name == "left":
                prev_left_motor_state = pwm

            camera_centering_pub.put(json.dumps(data))

            
        camera_centering_sub = session.declare_subscriber(config.camera_centering_data, camera_centering_data_cb)
        camera_centering_pub = session.declare_publisher(config.camera_centering_commands)
        hardware_sub = session.declare_subscriber(config.camera_centering_feedback)

        algorithm_start_time = time.perf_counter()
        centered_start_time = 0
        centered_end_time = 0
        centered_duration = 0
        centered_flag = None

        while True:
            if data_recieved_flag is True: 
                main()

            



