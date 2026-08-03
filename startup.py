import subprocess, sys
import keyboard

class Process():
    def __init__(self, name: str, path: str):
        self.process = subprocess.Popen(
            [sys.executable, path],
        )

        self.name = name

        print(f"Process name {self.name} started.")

    def __del__(self):
        self.process.terminate()
        self.process.wait()
        print(f"Process name {self.name} exited with code {self.process.returncode}.")

def main():
    vision = Process("vision.py", "./nodes/vision.py")
    camera_centering = Process("camera_centering.py", "./nodes/camera_centering.py")
    kinematics = Process("kinematics.py", "./nodes/kinematics.py")
    mcu_bridge = Process("mcu_bridge", "./nodes/mcu_bridge.py")

    while True:
        if keyboard.is_pressed('esc'):
            break

if __name__ == "__main__":
    main()