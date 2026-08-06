import zenoh, config, json, time, math
from collections import deque 
from datetime import datetime

error_data = deque([0] * 100,maxlen= 100) # deque makes list of 100 things that are all 0
time_data : deque[float] = deque([0] * 100,maxlen= 100) # can add / remove items from front or back of list
error_data_integral : deque[float] = deque([0] * 100,maxlen= 100) # this does not move everything, but only the selected item
error_data_derivative : deque[float] = deque([0] * 100,maxlen= 100) # makes everything much faster and same time if 5000 or 5 items in list
servo_x_pos = 90
pixel_focal_length = 4 / 0.0028

# PID values
kp = 1.0 # proportional gain (moves towards target)
ki = 0.001 # integral gain (moves faster if error is constant)
kd = 1.0 # derivative gain (moves faster if error is changing) hi

command_recieved_flag = None
data_recieved_flag = False

def proportionalAlgorithm() -> float:
    x = error_data[-1] # last item in list

    if x == 0:
        return 0 # if error is 0, return 0
    
    offset = (math.atan2(x, pixel_focal_length)) * (180/math.pi) # calulates angle from center in degrees

    return offset

def integralAlgorithm() -> float:
    x = error_data[-1] # last item in list (counts from back of array instead of front)

    if x == 0:
        error_data_integral.clear() # clears old data
        return 0
    else:
        error_data_integral.append(x) # adds value to end of list if not in center

    x_integ = sum(error_data_integral) # sum of all values in list (area under curve)
    offset = (math.atan2(x_integ, pixel_focal_length)) * (180/math.pi) # finds angle
    offset = max(-12.63, min(offset, 12.63)) # clamping so no overboard values

    return offset

def derivativeAlgorithm() -> float:
    y2 = error_data[-1] # last item in list
    y1 = error_data[-2] # second last item in list (meant to measure rate of change)
    x2 = time_data[-1]
    x1 = time_data[-2]

    x_derivative = (y2-y1) / (x2-x1)

    offset = (math.atan2(x_derivative, pixel_focal_length)) * (180/math.pi) # gets angle
    print(offset) # ask why print and also return

    return offset

def main():
    while True:
        global algorithm_start_time # global variables that can be used in other functions
        global kp, ki, kd
        global servo_x_pos, command_recieved_flag, data_recieved_flag, error_data, error_data_integral

        algorithm_end_time = time.perf_counter() # gets time when function ends (should it be this precise)
        algorithm_delay = algorithm_end_time - algorithm_start_time # difference between start and end time

        if algorithm_delay < 0.01: # Cap between time it takes to process function
            continue
        # if command_recieved_flag is False:
        #     continue

        proportional_val = proportionalAlgorithm()
        integral_val = integralAlgorithm()
        derivative_val = derivativeAlgorithm()

        servo_offset = int((kp * proportional_val) + (ki * integral_val) + (kd * derivative_val))
        # print(f"servo_offset = (kp: {kp} * P: {proportional_val}) + (ki: {ki} * I: {integral_val}) + (kd: {kd} * D: {derivative_val}) = {servo_offset}")

        sendServoJSON(servo_offset) # sends offset to the servo via JSON? (would maybe use zenoh + serial)

        servo_x_pos += servo_offset # adds offset to current servo position

        # command_recieved_flag = False
        data_recieved_flag = False # ASK ANDREW
        algorithm_start_time = time.perf_counter()

       
if __name__ == "__main__": # so when this script is run, it will name the file main and run the code in this function first
    with zenoh.open(zenoh.Config()) as session: # opens the equivalent of a tcp connection to the zenoh server
        # when writing a function w zenoh, it needs to be in this function, cant be outside
        def camera_centering_data_cb(sample: zenoh.Sample): # if data recieved run this
            global data_recieved_flag
            data = json.loads(sample.payload.to_string()) # converts string to dictionary
            error = int(data["error"]) # converts string to integer

            if -config.deadzone <= error <= config.deadzone:
                error_data.append(0) # if error in deadzone, set to 0
            else:
                error_data.append(error) # if error not in deadzone, add to list

            time = float(data["time"]) # converts 
            time_data.append(time)

            data_recieved_flag = True

        def camera_centering_feedback_cb(sample: zenoh.Sample):
            global command_recieved_flag
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

        while True:
            if data_recieved_flag is True:
                main()

            



