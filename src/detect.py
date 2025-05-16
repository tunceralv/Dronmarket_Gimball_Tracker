import cv2
import numpy as np
import random

class Detect:
    def __init__(self, tracker_type='CSRT', box_size=100):
        self.tracker_type = tracker_type
        self.BOX_SIZE = box_size

        self.trackers = []
        self.bboxes = []
        self.colors = []
        self.labels = []

        self.add_enabled = True
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        # Kamera ayarları
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1366)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Çizim için
        self.drawing = False
        self.start_point = None
        self.end_point = None

        cv2.namedWindow("Tracking")
        cv2.setMouseCallback("Tracking", self.on_mouse_draw)

    def create_tracker(self):
        if self.tracker_type == 'CSRT':
            return cv2.legacy.TrackerCSRT_create() if hasattr(cv2, 'legacy') else cv2.TrackerCSRT_create()
        elif self.tracker_type == 'KCF':
            return cv2.legacy.TrackerKCF_create() if hasattr(cv2, 'legacy') else cv2.TrackerKCF_create()
        else:
            raise ValueError("Desteklenmeyen tracker tipi")

    def on_mouse_draw(self, event, x, y, flags, param=None):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)

            if self.start_point and self.end_point:
                x1, y1 = self.start_point
                x2, y2 = self.end_point
                bbox = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

                ret, fresh_frame = self.cap.read()
                if not ret:
                    print("Kamera hatası")
                    return

                tracker = self.create_tracker()
                if tracker.init(fresh_frame, bbox):
                    self.trackers.append(tracker)
                    self.bboxes.append(bbox)
                    self.colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                    self.labels.append(f"Obj{len(self.labels) + 1}")
                    print(f"Yeni Nesne Eklendi: {self.labels[-1]}")
                else:
                    print("Tracker başlatılamadı.")

    def tespit(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
             print("Kamera bağlantısı kesildi.")
             yield None, None, None, None  # Böylece unpack sırasında None alınır ama hata olmaz
             break

            center = None
            to_delete = []

            for i, tracker in enumerate(self.trackers):
                success, newbox = tracker.update(frame)
                if success:
                    x, y, w, h = map(int, newbox)
                    self.bboxes[i] = (x, y, w, h)
                    cx, cy = x + w // 2, y + h // 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), self.colors[i], 2)
                    cv2.circle(frame, (cx, cy), 4, self.colors[i], -1)
                    if i == 0:
                        center = (cx, cy)
                else:
                    print(f"Takip kaybi: {self.labels[i]}")
                    to_delete.append(i)

            # Takip kaybı yaşanan tracker'ları sil
            for idx in sorted(to_delete, reverse=True):
                del self.trackers[idx]
                del self.bboxes[idx]
                del self.colors[idx]
                del self.labels[idx]


        
            # Eğer çizim yapıyorsa, geçici kutu göster
            if self.drawing and self.start_point and self.end_point:
                cv2.rectangle(frame, self.start_point, self.end_point, (255, 0, 0), 2)

            if not self.trackers:
                cv2.putText(frame, "Nesne Secimi Bekleniyor (Fareyle Cizerek)", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                yield frame, self.trackers, self.bboxes, center

            
            yield frame, self.trackers, self.bboxes, center
                
        self.cap.release()
        cv2.destroyAllWindows()