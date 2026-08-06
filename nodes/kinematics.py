import pandas as pd
import pygetwindow as gw
from datetime import datetime
import zenoh, json, time, keyboard, config

data_recieved_flag = False
system_exit_flag = False
projectile_shot_flag = False
manual_intervention_flag = False

data_collection_mode = True
training_mode = False
autonomous_mode = False

object_px_height = None
camera_height = None
servo_y_pos = 90

def onShot():
    global projectile_shot_flag
    projectile_shot_flag = True

def onESC():
    global system_exit_flag
    system_exit_flag = True

def initDatabases():
    global kinematics_dataset, kinematics_training_data

    print("\nDatabases initializing...")

    if data_collection_mode is True:
        print(config.data_collection_message)
        kinematics_dataset = pd.DataFrame(columns=["Object Pixel Height", "Camera Height", "Servo Angle"])

    elif training_mode is True:
        print(config.training_message)
        kinematics_dataset = pd.read_csv("")
        kinematics_training_data = pd.DataFrame(columns=["Object Pixel Height", "Camera Height", "Predicted Servo Angle", "Actual Servo Angle"])

    elif autonomous_mode is True:
        print(config.autonomous_message)
        kinematics_dataset = pd.read_csv("")

def deinitDatabases():
    global kinematics_dataset, kinematics_training_data

    if data_collection_mode is True:
        kinematics_dataset.to_csv("C:/dev/autonomous_turret_v1/database/kinematics_dataset.csv",index=False)

    elif training_mode is True:
        kinematics_dataset.to_csv("C:/dev/autonomous_turret_v1/database/kinematics_dataset.csv",index=False)
        kinematics_training_data.to_csv("C:/dev/autonomous_turret_v1/database/kinematics_training_dataset.csv",index=False)

    elif autonomous_mode is True:
        kinematics_dataset.to_csv("C:/dev/autonomous_turret_v1/database/kinematics_dataset.csv",index=False)

    print("\nDatabases exported.")

def predictionModel():
    return 0

def main():
    global object_px_height, camera_height
    global data_recieved_flag, data_collection_mode, training_mode, autonomous_mode, projectile_shot_flag, manual_intervention_flag

    if data_collection_mode and projectile_shot_flag is True:
        print(f"\nRecent shot was at object pixel height: {object_px_height}, camera_height: {camera_height}, servo angle: {servo_y_pos}.")

        ans = input("Enter (y/n) to add entry to database: ").lower()
        if ans == "y":
            kinematics_dataset.loc[len(kinematics_dataset)] = [object_px_height, camera_height, servo_y_pos]
        if ans == "n":
            print("\nEntry ignored.")

        projectile_shot_flag = False

    if training_mode or autonomous_mode is True:
        servo_angle = predictionModel()
        sendServoYJSON(servo_angle)

        if training_mode and projectile_shot_flag is True:
            print(f"\nModel prediction was at object pixel height: {object_px_height}, camera_height: {camera_height}, servo angle: {servo_y_pos}.")
            
            ans = input("Was the prediction correct (y/n): ").lower()
            if ans == "y":
                kinematics_dataset.loc[len(kinematics_dataset)] = [object_px_height, camera_height, servo_y_pos]
            if ans == "n":
                manual_intervention_flag = True
                projectile_shot_flag = False
                print("\nManual intervention taking place: ")

                while manual_intervention_flag is True:
                    if projectile_shot_flag is True:
                        print(f"\nRecent shot was at object pixel height: {object_px_height}, camera_height: {camera_height}, servo angle: {servo_y_pos}.")
                    
                        ans = input("Enter (y/n) to add entry to database: ").lower()
                        if ans == "y":
                            kinematics_dataset.loc[len(kinematics_dataset)] = [object_px_height, camera_height, servo_y_pos]
                            manual_intervention_flag = False
                        if ans == "n":
                            print("\nEntry ignored.")

                        projectile_shot_flag = False

        data_recieved_flag = False

if __name__ == "__main__":
    def sendServoYJSON(angle: int):
        global servo_y_pos

        data = {
            "command": "setY",
            "angle": f"{angle}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        }

        kinematics_commands_pub.put(json.dumps(data))

        servo_y_pos = angle

    def kinematics_data_cb(sample: zenoh.Sample):
        global object_px_height, camera_height
        global data_recieved_flag

        data = json.loads(sample.payload.to_string())
        object_px_height = int(data["object_px_height"])
        camera_height = int(data["camera_height"])

        data_recieved_flag = True

    def keyboard_controls_cb(sample: zenoh.Sample):
        return

    with zenoh.open(zenoh.Config()) as session:
        kinematics_data_sub = session.declare_subscriber(config.kinematics_data, kinematics_data_cb)
        kinematics_commands_pub = session.declare_publisher(config.kinematics_commands)
        keyboard_controls_sub = session.declare_subscriber(config.keyboard_controls, keyboard_controls_cb)

        initDatabases()

        keyboard.add_hotkey('esc', onESC)
        keyboard.add_hotkey('p', onShot)

        while True:
            time.sleep(0.01)
            if data_recieved_flag is True:
                main()
            if system_exit_flag is True:
                break

        deinitDatabases()