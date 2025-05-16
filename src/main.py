from gimball_control import GimballControl
from Display import PIDGui
from PyQt5.QtWidgets import QApplication
from detect import Detect
import threading
import cv2
import sys

def launch_pid_gui(pid_controller):
    app = QApplication(sys.argv)
    pid_window = PIDGui(pid_controller)
    pid_window.show()
    app.exec_()

def main():
    detector = Detect()
    gimbal = GimballControl("config/PID.json", "config/config.json")
    gimbal.connect_gimball()

    # GUI ayrı thread'de çalışsın
    gui_thread = threading.Thread(target=launch_pid_gui, args=(gimbal.pid,))
    gui_thread.daemon = True
    gui_thread.start()

    # OpenCV loop (ana thread'de çalışmalı!)
    for frame, _, _, center in detector.tespit():
        if frame is None:
            break

        frame_height, frame_width = frame.shape[:2]
        camera_center = (frame_width // 2, frame_height // 2)
        gimbal.cameraCenter(frame, camera_center)
        gimbal.update(center, (frame_width, frame_height))

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
