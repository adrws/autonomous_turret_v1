import zenoh, config, json, time, math
from config import Direction
from datetime import datetime

incoming_data_flag = False

error = 0
deadzone = config.deadzone
prev_servo_command = 0

def main():
    global incoming_data_flag

    swivel_speed = int(5)

    if -deadzone < error < deadzone:
        send_servo_command(90)
    elif error > deadzone:
        send_servo_command(90+swivel_speed)
    elif error < -deadzone:
        send_servo_command(90-swivel_speed)

    incoming_data_flag = False

if __name__ == "__main__":
    def send_servo_command(speed: int):
        global prev_servo_command

        if prev_servo_command == speed:
            return

        data = {
        "command": "setX",
        "angle" : f"{speed}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        camera_centering_command_pub.put(json.dumps(data))

        prev_servo_command = speed

    def camera_centering_data_cb(sample: zenoh.Sample):
        global error, incoming_data_flag

        data = json.loads(sample.payload.to_string()) 
        error = int(data["error"])

        incoming_data_flag = True

    with zenoh.open(zenoh.Config()) as session:
        camera_centering_data_sub = session.declare_subscriber(config.camera_centering_data, camera_centering_data_cb)
        camera_centering_command_pub = session.declare_publisher(config.camera_centering_commands)

        while True:
            send_servo_command(90)
            if incoming_data_flag:
                main()