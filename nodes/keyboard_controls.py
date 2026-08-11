import zenoh, json, time, config

system_exit_flag = False

def main():
    return

if __name__ == "__main__":
    
    with zenoh.open(zenoh.Config()) as session:
        kinematics_commands_pub = session.declare_publisher(config.kinematics_commands)
        camera_centering_commands_pub = session.declare_publisher(config.camera_centering_commands)

        while True:
            main()
            if system_exit_flag is True:
                break

        