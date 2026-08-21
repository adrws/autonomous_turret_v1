import serial, json, time, config, zenoh

PORT ='COM3'
BAUD = 921600

if __name__ == "__main__":

    with zenoh.open(zenoh.Config()) as session:

        def sendSerialCommand(sample: zenoh.Sample):
                global ser
        
                message = sample.payload.to_string() + "\n"
                ser.write(message.encode('utf-8'))
        
        kinematics_commands_sub = session.declare_subscriber(config.kinematics_commands, sendSerialCommand)
        camera_centering_commands_sub = session.declare_subscriber(config.camera_centering_commands, sendSerialCommand)

        ser = serial.Serial(PORT, BAUD, timeout = -1)
        time.sleep(2)




# 1. Open serial conncetion 
#  1.1 open it to port + baud rate
#  1.2 let teh esp32 chill for 2 seconds to get ready
#  1.3 open zenoh session to network

    

# 2. open zenoh
#  2.1 get it to sub to the keys
#  2.2 get it to store the data as a string
#  2.3 at the end of each data line make it terminate the string w \n 

# 3 send it all over to the esp32
#  3.1 send over via channe