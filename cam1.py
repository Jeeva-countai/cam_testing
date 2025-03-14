import os
import time
import cv2
import numpy as np
import csv
from datetime import datetime
import queue
import threading

class Camera:
    def __init__(self, camID, exposuretime, gain):
        """
        Class used to Find camera, setting camera parameters, and Fetch UV camera frames.
        """
        try:
            self.exposuretime = exposuretime
            self.gain = gain
            print("camID", camID)
            print("exposuretime", exposuretime)
            print("gain", gain)

            if camID != 0:
                self.camId = camID
                self.platform = "linux"
                self.findCameraLinux()
            else:
                self.platform = "windows"
                self.findCameraWindows()
            self.imageQueue1 = queue.Queue(maxsize=1)
            self.imageQueue = queue.Queue(maxsize=5)
            self.imageStreamerThread = threading.Thread(target=self.imageStreamer)
            self.imageStreamerThread.daemon = True
            self.imageStreamerThread.start()
            self.latestImage = np.zeros((720, 1280, 3), np.uint8)
        except Exception as e:
            print(f"Error initializing Camera: {e}")

    def imageStreamer(self):
        while True:
            time.sleep(0.01)
            try:
                ret_value, frame = self.readImage()
                if not self.imageQueue1.full() and ret_value:
                    # print("image inserting in queue")
                    self.imageQueue1.put([True, frame])
            except Exception as e:
                print(f"Error in imageStreamer: {e}")

    def readImage(self):
        try:
            ret_value, frame = self.device.read()
            if ret_value:
                # print(frame.shape)
                self.status = True
                return True, frame
            else:
                self.status = False
                if self.platform == "linux":
                    self.findCameraLinux()
                else:
                    self.findCameraWindows()
                return False, np.zeros((1080, 1920, 3), np.uint8)
        except Exception as e:
            self.status = False
            print(f"Error reading image: {e}")
            return False, np.zeros((1080, 1920, 3), np.uint8)

    def send_request(self, angle):
        try:
            if not self.imageQueue1.empty():
                image = self.imageQueue1.get()
                data = [image[0], image[1], angle]
                if not self.imageQueue.full():
                    return self.imageQueue.put(data)
                else:
                    return [False, np.zeros((720, 1280, 3), np.uint8)]
            else:
                return [False, np.zeros((720, 1280, 3), np.uint8)]
        except Exception as e:
            print(f"Error sending request: {e}")
            return [False, np.zeros((720, 1280, 3), np.uint8)]

    def fetchImage(self):
        try:
            if not self.imageQueue.empty():
                image = self.imageQueue.get()
                return True, image[1], image[2]
        except Exception as e:
            print(f"Error fetching image: {e}")
        return False, "", "-1"

    def setExposure(self, exposure):
        try:
            for _ in range(100):
                ret, _ = self.device.read()
                if ret:
                    break
            if self.platform == "linux":
                os.system(
                    f"v4l2-ctl --device {self.camId} --set-ctrl=exposure_time_absolute={exposure}"
                )
            else:
                self.device.set(cv2.CAP_PROP_EXPOSURE, exposure)
        except Exception as e:
            print(f"Error setting exposure: {e}")

    def setParamsLinux(self):
        try:
            self.device.set(3, 1280)
            self.device.set(4, 720)
            self.device.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            time.sleep(1)
            os.system(f"v4l2-ctl --device {self.camId} --set-ctrl=auto_exposure=1")
            for _ in range(5):
                self.setExposure(self.exposuretime)
            os.system(f"v4l2-ctl --device {self.camId} --set-ctrl=gain=0")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Error setting parameters on Linux: {e}")
            return False

    # def findCameraLinux(self):
    #     try:
    #         self.device = cv2.VideoCapture(self.camId)
    #         ret, _ = self.device.read()
    #         if ret:
    #             return True
    #             # return self.setParamsLinux()
    #         else:
    #             return False
    #     except Exception as e:
    #         print(f"Error finding Linux camera: {e}")
    #         return False


    def findCameraLinux(self):
        try:
            self.device = cv2.VideoCapture(f"/dev/v4l/by-path/{self.camId}")  # Use full path
            ret, _ = self.device.read()
            if ret:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error finding Linux camera: {e}")
            return False

    def close(self):
        try:
            self.device.release()
            self.imageQueue1 = queue.Queue(maxsize=1)
            self.imageStreamerThread.join()
        except Exception as e:
            print(f"Error closing camera: {e}")

    def request_simulator(self):
        angle  = 0
        try:
            while True:
                self.send_request(str(angle))
                angle+=50
                if angle == 1000:
                    angle = 0
                time.sleep(0.01)
        except Exception as e:
            print(str(e))

if __name__ == "__main__":
    try:
        cam = Camera(
                    'pci-0000:00:14.0-usb-0:7:1.0-video-index0',100, 0
        )

       
        fps = 0
        st = time.time()
        csv_filename = "/home/kniti/Documents/test/Ncam1.csv"
       
        # Start camera request simulator
        threading.Thread(target=cam.request_simulator).start()
       
        # Check if the file exists to determine if we need a header
        file_exists = os.path.isfile(csv_filename)
       
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "FPS"])
           
            while True:
                ret, image, _ = cam.fetchImage()
                if ret:
                    fps += 1
                    if time.time() - st > 1:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("FPS:", fps)
                        writer.writerow([timestamp, fps])
                        file.flush()  # Ensure data is written to disk
                        st = time.time()
                        fps = 0
   
    except Exception as e:
        print(f"Error in main execution: {e}")