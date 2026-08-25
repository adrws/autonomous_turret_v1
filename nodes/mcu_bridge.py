import serial, time, config, zenoh

PORT ='COM4'
BAUD = 921600

if __name__ == "__main__":

    with zenoh.open(zenoh.Config()) as session:

        def sendSerialCommand(sample: zenoh.Sample):
                global ser
        
                message = sample.payload.to_string() + "\n"
                ser.write(message.encode('utf-8'))
        
        kinematics_commands_sub = session.declare_subscriber(config.kinematics_commands, sendSerialCommand)
        camera_centering_commands_sub = session.declare_subscriber(config.camera_centering_commands, sendSerialCommand)

        ser = serial.Serial(PORT, BAUD, timeout = 1)
        time.sleep(2)

        while True:
            time.sleep(0.1)
