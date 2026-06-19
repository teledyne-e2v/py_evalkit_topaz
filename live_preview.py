# -*- coding: utf-8 -*-
"""
Created on July 2025

@author: Teledyne E2V
"""
from sensor import *
from utils import *
from time import sleep
from PIL import Image

# USER PARAMETERS
from sensor import Topaz

# FOR LIVE PREVIEW
import cv2
import numpy as np


INTERVAL_PLOT = 0.0001  # Refresh rate in ms
EXPOSURE_TIME = 6  # Integration time in ms

#Mouse drag & drop
drawing = False
start_point = None
end_point = None
roi = None

#Camera control
exposure = 10
control = False

def mouse_callback(event, x, y, flags, param):
    global start_point, end_point, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        end_point = (x+1, y+1)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        print(f"Selected ROI : {start_point} -> {end_point} | width={abs(start_point[0]-end_point[0])}, height={abs(start_point[1]-end_point[1])}")

    elif event == cv2.EVENT_RBUTTONDOWN:
        start_point = None
        end_point = None
        print(f"Reset ROI")

def change_exposure(val):
    global control, exposure
    control=True
    exposure=val

#  SIMPLE OBJECT CREATION AND IMAGE ACQUISITION
if __name__ == "__main__":
    print("*******************************************************************")
    print("************** Running Eval Kit Liv preview main loop *************")
    print("*******************************************************************")

    # Open connection
    camera = Topaz()

    if camera is not None:
        #sensor chip-ID check
        addr = 0x7F
        rval = camera.read_sensor_reg(addr)  # Read chipID
        print("RD 0x{:02x} = 0x{:04x}".format(addr, rval))
        sleep(0.5)

        # Setup camera format
        camera.set_camera_format(10) #10b format
        # camera.set_camera_format(8)  #8b format

        # Sensor parameters
        camera.exposure_time= EXPOSURE_TIME


        # Pixel format and acquisition image size
        if camera.pixel_format == "RGB24":
            shape = (camera.sensor_height, camera.sensor_width * 3)
        else:
            shape = (camera.sensor_height, camera.sensor_width)

        # Get current setting
        print_info(camera)


        print("\nLive preview start")
        preview = True

        if camera.start_acquisition() == 0:
            NBImageAcquired = 0
            NBImageSaved = 0
            # fig = init_figure(camera)
            cv2.namedWindow('Live preview', cv2.WINDOW_AUTOSIZE)
            cv2.setMouseCallback('Live preview', mouse_callback)
            cv2.createTrackbar("Exposure", 'Live preview', 1, 500, change_exposure)

            while preview:
                # Get image from internal buffer
                im = camera.get_image()[1]
                NBImageAcquired += 1

                """
                Insert your processing code here
                image is the current image acquired
                """
                # CONTROL
                if(control):
                    camera.exposure_time = exposure
                    control = False

                # IMAGE PROCESS
                if(roi and (not drawing)):
                    mean = np.mean(imageRoi(im,roi))
                    sigma = np.std(imageRoi(im,roi))
                    sharp = sharpness(imageRoi(im,roi))
                else:
                    mean = np.mean(im)
                    sigma = np.std(im)
                    sharp = sharpness(im)

                # DISPLAY
                image_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                # text overlay
                text = "Mean={:.2f} | StdDev={:.2f} | Sharpness={:.2f}".format(mean, sigma, sharp)
                cv2.putText(image_rgb, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                # ROI selection
                if start_point and end_point:
                    roi=[start_point, end_point]
                    cv2.rectangle(image_rgb, start_point, end_point, (0, 255, 0), 2)
                else:
                    roi = None
                cv2.imshow('Live preview', image_rgb)

                k=cv2.waitKey(1)
                if k == ord('q') or k == 27:
                    print("Live preview stop: {} images".format(NBImageAcquired))
                    preview = False
                elif k == ord('s'):
                    imgName = "EK-image_" + str(NBImageSaved) + ".raw"
                    NBImageSaved += 1
                    with open(imgName, "wb") as f:
                        f.write(im.tobytes())

                # imageProfile(im)
                # update_figure(fig, im, INTERVAL_PLOT, NBImageAcquired)

            # Terminate acquisition
            cv2.destroyAllWindows()
            if camera.stop_acquisition() == 0:
                NBImageAcquired = 0

        else:
            raise Exception("Image acquisition error. Please reboot the camera")

        # Terminate connection
        camera.close()
    else:
        raise Exception("Camera initialization error. Please reboot the camera")
