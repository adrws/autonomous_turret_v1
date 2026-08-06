import cv2
from ultralytics import YOLO
import zenoh, statistics, json, time
from datetime import datetime
import config

KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

CAMERA_HEIGHT = 93

def main():
    camera = cv2.VideoCapture(0)
    base_model = YOLO("yolo26n-pose.pt")
    base_model.export(format="openvino")
    model = YOLO("yolo26n-pose_openvino_model/")

    camera_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    center_x = camera_width // 2

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame.")
            break

        results = model(frame, verbose=False)
        result = results[0]

        if result.keypoints is not None and result.keypoints.shape[0] > 0:
            keypoints = result.keypoints

            xy = keypoints.xy.numpy()              
            conf = keypoints.conf.numpy()

            person_idx = 0

            left_shoulder_x, left_shoulder_y = xy[person_idx, KEYPOINT_NAMES.index("left_shoulder")].astype(int)
            right_shoulder_x, right_shoulder_y = xy[person_idx, KEYPOINT_NAMES.index("right_shoulder")].astype(int)
            right_hip_x, right_hip_y = xy [person_idx, KEYPOINT_NAMES.index("right_hip")].astype(int)
            obj_center_x = right_shoulder_x + (left_shoulder_x - right_shoulder_x) // 2
            obj_center_y = left_shoulder_y + (right_hip_y - left_shoulder_y) // 2
            half_side = config.deadzone // 2
            error = center_x - obj_center_x
            obj_height = right_hip_y - left_shoulder_y

            left_shoulder_conf = conf[person_idx, KEYPOINT_NAMES.index("left_shoulder")]
            right_shoulder_conf = conf[person_idx, KEYPOINT_NAMES.index("right_shoulder")]
            right_hip_conf = conf[person_idx, KEYPOINT_NAMES.index("right_hip")]

            confidence = [left_shoulder_conf, right_shoulder_conf, right_hip_conf]

            if statistics.fmean(confidence) > 0.5:
                cv2.rectangle(frame, (left_shoulder_x, left_shoulder_y), (right_shoulder_x, right_hip_y), color=(255,0,0), thickness=2)
                cv2.rectangle(frame, (obj_center_x - half_side, obj_center_y - half_side), (obj_center_x + half_side, obj_center_y + half_side), color=(255,0,0), thickness=2)

                sendCameraCenteringJSON(error)
                sendKinematicJSON(obj_height, CAMERA_HEIGHT)


        cv2.imshow('Camera View', frame)
        
        if cv2.waitKey(2) == ord('q'):
            break
        
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    with zenoh.open(zenoh.Config()) as session:
        camera_centering_pub = session.declare_publisher(config.camera_centering_data)
        kinematics_pub = session.declare_publisher(config.kinematics_data)

        global_start_time = time.perf_counter()
        camera_centering_command_start_time = time.perf_counter()
        camera_centering_command_end_time = None
        kinematics_command_start_time = time.perf_counter()
        kinematics_command_end_time = None
            
        def sendCameraCenteringJSON(error: int):
            global camera_centering_command_start_time
            camera_centering_command_end_time = time.perf_counter()
            delay = camera_centering_command_end_time - camera_centering_command_start_time
            
            if delay < 0.015:
                        return
            
            data = {
                "error" : f"{error}",
                "time" : f"{round(time.perf_counter() - global_start_time, 3)}",
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            camera_centering_pub.put(json.dumps(data))
            camera_centering_command_start_time = time.perf_counter()

        def sendKinematicJSON(obj_px_height: int, height: int):
            global kinematics_command_start_time
            kinematics_command_end_time = time.perf_counter()
            delay = kinematics_command_end_time - kinematics_command_start_time
            
            if delay < 0.015:
                        return
            data = {
                "object_px_height" : f"{obj_px_height}",
                "camera_height" : f"{height}",
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            kinematics_pub.put(json.dumps(data))
            kinematics_command_start_time = time.perf_counter()
    
        main()

    