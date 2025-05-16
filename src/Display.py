from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import json

class PIDGui(QWidget):
    def __init__(self, pid_controller, pid_path="config/PID.json"):
        super().__init__()
        self.pid = pid_controller
        self.pid_path = pid_path
        self.setWindowTitle("DroneMarket | PID Ayarları")
        self.setGeometry(100, 100, 350, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout = QVBoxLayout()

        font_label = QFont("Arial", 10, QFont.Bold)
        font_input = QFont("Consolas", 10)

        def create_labeled_input(label_text, default_value):
            label = QLabel(label_text)
            label.setFont(font_label)
            input_field = QLineEdit(default_value)
            input_field.setFont(font_input)
            input_field.setStyleSheet("background-color: #2e2e2e; color: #fefefe; border: 1px solid #ffd700; padding: 4px;")
            layout.addWidget(label)
            layout.addWidget(input_field)
            return input_field

        # Pan PID
        self.kp_pan_input = create_labeled_input("Pan - Kp", str(self.pid.kp_pan))
        self.ki_pan_input = create_labeled_input("Pan - Ki", str(self.pid.ki_pan))
        self.kd_pan_input = create_labeled_input("Pan - Kd", str(self.pid.kd_pan))

        # Tilt PID
        self.kp_tilt_input = create_labeled_input("Tilt - Kp", str(self.pid.kp_tilt))
        self.ki_tilt_input = create_labeled_input("Tilt - Ki", str(self.pid.ki_tilt))
        self.kd_tilt_input = create_labeled_input("Tilt - Kd", str(self.pid.kd_tilt))

        # Güncelle Butonu
        self.update_button = QPushButton("PID Değerlerini Güncelle ve Kaydet")
        self.update_button.setStyleSheet("background-color: #ffd700; color: black; font-weight: bold; padding: 6px;")
        self.update_button.clicked.connect(self.update_pid)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def update_pid(self):
        try:
            self.pid.kp_pan = float(self.kp_pan_input.text())
            self.pid.ki_pan = float(self.ki_pan_input.text())
            self.pid.kd_pan = float(self.kd_pan_input.text())
            self.pid.kp_tilt = float(self.kp_tilt_input.text())
            self.pid.ki_tilt = float(self.ki_tilt_input.text())
            self.pid.kd_tilt = float(self.kd_tilt_input.text())

            # JSON'a kaydet
            pid_json = {
                "pid": {
                    "pan": {
                        "kp": self.pid.kp_pan,
                        "ki": self.pid.ki_pan,
                        "kd": self.pid.kd_pan
                    },
                    "tilt": {
                        "kp": self.pid.kp_tilt,
                        "ki": self.pid.ki_tilt,
                        "kd": self.pid.kd_tilt
                    }
                },
                "output_limits": {
                    "pan": self.pid.pan_limits,
                    "tilt": self.pid.tilt_limits
                },
                "update_rate_hz": self.pid.update_rate_hz
            }

            with open(self.pid_path, "w") as f:
                json.dump(pid_json, f, indent=4)

            print("✅ PID değerleri başarıyla güncellendi ve PID.json dosyasına kaydedildi.")
        except ValueError:
            print("Lütfen geçerli sayısal değerler girin!")
