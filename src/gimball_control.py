import cv2
from detect import Detect
from Pid_system import PIDController
from siyi_sdk.siyi_sdk import SIYISDK
import threading
from queue import Queue
import time

class GimballControl:
    def __init__(self, pid_path, config_path):
        self.pid = PIDController()
        self.pid.Read_PID(pid_path)
        self.pid.Read_Config(config_path)
        self.gimball = None

    def connect_gimball(self):
        self.gimball = SIYISDK(server_ip="192.168.144.25", debug=False)
        self.gimball.connect()
        if self.gimball.isConnected:
            print("Gimball bağlantısı başarılı")
            self.gimball.setGimbalRotation(0, 0)
        else:
            print("Gimball bağlantısı başarısız")

    def update(self,center, resolution, err_thresh=2.0, max_speed=100):
        frame_width, frame_height = resolution
        camera_center = (frame_width // 2, frame_height // 2)

    
        if center:
            error_x = center[0] - camera_center[0]
            error_y = center[1] - camera_center[1]

            deg_error_x, deg_error_y = self.pid.pixel_to_degree(error_x, error_y)
            self._set_gimbal_rotation(deg_error_x, deg_error_y, err_thresh, max_speed)
        else:
            print("Nesne kayıp. Motor durduruluyor.")
            self.gimball.requestGimbalSpeed(0,0)


        time.sleep(1 / self.pid.update_rate_hz)

    def _set_gimbal_rotation(self, target_yaw, target_pitch, err_thresh=2.0, max_speed=100):
        self.gimball.requestGimbalAttitude()
        att = self.gimball._att_msg

        if att.seq == self.gimball._last_att_seq:
            print("Yeni veri alınamadı...")
            self.gimball.requestGimbalSpeed(0, 0)
            return

        self.gimball._last_att_seq = att.seq

        yaw_err = -target_yaw
        pitch_err = target_pitch

        print(f"[HATA] Yaw: {att.yaw:.2f}, Pitch: {att.pitch:.2f} → Hata: ({yaw_err:.2f}, {pitch_err:.2f})")

        if abs(yaw_err) <= err_thresh and abs(pitch_err) <= err_thresh:
            print("Nesne merkezde. Motor durduruluyor.")
            self.gimball.requestGimbalSpeed(0, 0)
            return

        pan_speed, tilt_speed = self.pid.compute((0, 0), (yaw_err, pitch_err))

        self.pid.integral[0] = max(-100, min(100, self.pid.integral[0]))
        self.pid.integral[1] = max(-100, min(100, self.pid.integral[1]))

        pan_speed = max(-max_speed, min(max_speed, int(pan_speed)))
        tilt_speed = max(-max_speed, min(max_speed, int(tilt_speed)))

        print(f"[KOMUT] YawSpeed={pan_speed}, PitchSpeed={tilt_speed}")
        self.gimball.requestGimbalSpeed(pan_speed, tilt_speed)


    def cameraCenter(self,frame,camera_center):
            cv2.circle(frame, camera_center, 15, (255, 0, 0), 2)
            cv2.circle(frame, camera_center, 2, (255, 255, 255), -1)