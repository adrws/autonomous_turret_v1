import serial, json, zenoh

#Zenoh data setup
object_px_height = None
camera_height = None

# Serial Setup
PORT ='COM3'
BAUD = 921600
port = serial.Serial(PORT, BAUD, timeout = -1) # connecting to port

#Zenoh setup

if __name__ == "__main__": # main loop for zenoh
    
    #subscribing to specific sessions (URL's pr much)

    kinematics_data_sub = session.declare_subscriber(config.kinematics_data, kinematics_data_cb)
    kinematics_commands_pub = session.declare_publisher(config.kinematics_commands)

    # Defining functions that take in data from the sessions we subbed to

    with zenoh.open(zenoh.Config()) as session:
        def camera_center_data(sample: zenoh.Sample):
            data = sample.payload.to_string()
            global object_px_height = int(data["object_px_height"])
            global camera_height = int(data["camera_height"])


        def kin_data(sample: zenoh.Sample):



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