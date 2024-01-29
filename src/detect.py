import time
import sys

import cv2
from picamera2 import Picamera2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils

THREAD_NUM = 4
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
DEFAULT_MODEL = 'efficientdet_lite0.tflite'
CORAL_MODEL = 'efficientdet_lite0_edgetpu.tflite'


def main():
    # Coral USB Accelerator will not be used in this project
    # modify here if it'll be used
    detect(True, DISPLAY_WIDTH, DISPLAY_HEIGHT, THREAD_NUM, False)


def detect(csi_camera: bool, width: int, height: int, num_threads: int, enable_edgetpu: bool):
    """
        Continuously run inference on images acquired from the camera.

        Args:
        csi_camera: True/False whether the Raspberry Pi camera module is a CSI Camera (Pi Camera module).
        width: the width of the frame captured from the camera.
        height: the height of the frame captured from the camera.
        num_threads: the number of CPU threads to run the model.
        enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """
    counter, fps = 0, 0
    start_time = time.time()

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (width, height)
    picam2.preview_configuration.main.format = 'RGB888'
    picam2.preview_configuration.main.align()
    picam2.configure("preview")
    picam2.start()

    if enable_edgetpu:
        model = CORAL_MODEL
    else:
        model = DEFAULT_MODEL

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
    detection_options = processor.DetectionOptions(
        max_results=4, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

    while True:
        if csi_camera:
            image = picam2.capture_array()
            image = cv2.flip(image, -1)
        #else:
            #ret, image = cam.read()
        
        image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_tensor = vision.TensorImage.create_from_array(image_RGB)
        detections = detector.detect(image_tensor)
        image = utils.visualize(image, detections)

        cv2.imshow('Camera', image)

        if cv2.waitKey(1) == ord('q'):
            break
    
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
