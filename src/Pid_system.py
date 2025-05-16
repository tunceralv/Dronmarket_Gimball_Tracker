import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import time
from simple_pid import PID
from utils.json_loader import load_config

class PIDController:
    def __init__(self):
        self.kp_pan=None
        self.ki_pan=None
        self.kd_pan=None

        self.kp_tilt=None
        self.ki_tilt=None
        self.kd_tilt=None

        self.pan_limits=None
        self.tilt_limits=None

        self.prev_error = [0, 0]
        self.integral = [0, 0]

        self.camera_name=None
        self.video_format=None
        self.image_format=None
        self.image_sensor=None

        self.width=None
        self.height=None
        
        self.horizontal=None
        self.diagonal=None

        self.fps=None

    def Read_PID(self,fileurl):
        pid_data=load_config(fileurl)
        #PID.json dosyasındaki pid blogunun pan blogundaki kp,ki ve kd degerlerini değişkenlere atama işlemi
        pan=pid_data["pid"]["pan"]
        self.kp_pan=pan["kp"]
        self.ki_pan=pan["ki"]
        self.kd_pan=pan["kd"]
        print(f"kp_pan: {self.kp_pan}, Ki_pan: {self.ki_pan}, kd_pan: {self.kd_pan}")

        #PID.json dosyasındaki pid blogunun tilt blogundaki kp,ki ve kd degerlerini değişkenlere atama işlemi
        tilt=pid_data["pid"]["tilt"]
        self.kp_tilt=tilt["kp"]
        self.ki_tilt=tilt["ki"]
        self.kd_tilt=tilt["kd"]
        print(f"kp_tilt: {self.kp_tilt}, Ki_tilt: {self.ki_tilt}, kd_tilt: {self.kd_tilt}")

        #Outputs lİmits blogundaki degerleri almak
        outputs_limits=pid_data["output_limits"]
        self.pan_limits=outputs_limits["pan"]
        self.tilt_limits=outputs_limits["tilt"]  
        print(f"pan_limits: {self.pan_limits}, tilt_limits: {self.tilt_limits}")      

        #Frekans degerini degişkene atamak
        self.update_rate_hz=pid_data["update_rate_hz"]
        print(f"update_rate_hz: {self.update_rate_hz}")


    def Read_Config(self,fileurl):
       config_data=load_config(fileurl)
       self.camera_name=config_data["camera"]["name"]
       self.video_format=config_data["camera"]["video_format"]
       self.image_format=config_data["camera"]["image_format"]
       self.image_sensor=config_data["camera"]["image_sensor"]
       print(f"camera_name: {self.camera_name}, video_format: {self.video_format}, image_format: {self.image_format}, image_sensor: {self.image_sensor}")

       resolution=config_data["camera"]["resolution"]
       self.width=resolution["width"]
       self.height=resolution["height"]
       print(f"width: {self.width}, height: {self.height}")

       fov=config_data["camera"]["fov"]
       self.horizontal=fov["horizontal"]
       self.diagonal=fov["diagonal"]
       print(f"horizontal_fov: {self.horizontal}, diagonal_fov: {self.diagonal}")

       self.fps=config_data["camera"]["fps"]
       print(f"fps: {self.fps}")


    def compute(self, setpoint, measured_value):
     error_x = measured_value[0] - setpoint[0]  # Nesne - Kamera
     error_y = measured_value[1] - setpoint[1]

     self.integral[0] += error_x
     self.integral[1] += error_y

     derivative_x = error_x - self.prev_error[0]
     derivative_y = error_y - self.prev_error[1]

     output_x = (self.kp_pan * error_x) + (self.ki_pan * self.integral[0]) + (self.kd_pan * derivative_x)
     output_y = (self.kp_tilt * error_y) + (self.ki_tilt * self.integral[1]) + (self.kd_tilt * derivative_y)

     self.prev_error = [error_x, error_y]
     return output_x, output_y
    
    def pixel_to_degree(self,error_x,error_y):
     aspect_radio=self.width/self.height

       #vertical FOV
     tan_diagonal=math.tan(math.radians(self.diagonal)/2)
     tan_vertical=tan_diagonal/math.sqrt(1+aspect_radio**2)
     vertical_fov=math.degrees(2*math.atan(tan_vertical))

     angle_per_pixel_x=self.horizontal/self.width
     angle_per_pixel_y=vertical_fov/self.height

     angle_pan=-error_x*angle_per_pixel_x
     angle_tilt=-error_y*angle_per_pixel_y

     return angle_pan,angle_tilt
    
    def update_from_gui(self, kp_pan, ki_pan, kd_pan, kp_tilt, ki_tilt, kd_tilt):
        try:
            self.kp_pan = float(kp_pan)
            self.ki_pan = float(ki_pan)
            self.kd_pan = float(kd_pan)

            self.kp_tilt = float(kp_tilt)
            self.ki_tilt = float(ki_tilt)
            self.kd_tilt = float(kd_tilt)

            print("PID değerleri GUI üzerinden başarıyla güncellendi.")
        except ValueError:
            print("Geçersiz giriş! Lütfen sayısal değerler girin.")
