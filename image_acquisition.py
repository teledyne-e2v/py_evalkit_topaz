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

NIMAGES = 1  # Number of images to be acquired
INTERVAL_PLOT = 0.0001  # Refresh rate in ms
EXPOSURE_TIME = 25  # Integration time in ms
R_GAIN = 1.8  # Red color gain
G_GAIN = 1  # Green color gain
B_GAIN = 1.6  # Blue color gain

#  SIMPLE OBJECT CREATION AND IMAGE ACQUISITION
if __name__ == "__main__":
    print("*******************************************************************")
    print("*********** Running Eval Kit image acquisition main loop **********")
    print("*******************************************************************")

    # Open connection
    camera = Topaz()

    if camera is not None:
        #sensor chip-ID check
        addr = 0x7F
        rval = camera.read_sensor_reg(addr)  # Read chipID
        print("RD 0x{:02x} = 0x{:04x}".format(addr, rval))
        sleep(0.5)

        # print("\r\t" + str(NBImageAcquired) + "/" + str(NIMAGES) + " images acquired", end="\t\t\t")

        # Setup camera format
        camera.set_camera_format(10) #10b format
        #camera.set_camera_format(8)  #8b format

        # Exposure time
        camera.exposure_time = EXPOSURE_TIME
        # Pixel format and acquisition image size
        if camera.pixel_format == "RGB24":
            # camera.white_balance(red=R_GAIN, green=G_GAIN, blue=B_GAIN)
            camera.enable_white_balance(enable=1)
            shape = (NIMAGES, camera.sensor_height, camera.sensor_width * 3)
        else:
            shape = (NIMAGES, camera.sensor_height, camera.sensor_width)
        
        im = np.zeros(shape, dtype=xml_pixel_format_nptypes[camera.pixel_format])

        # Get current setting
        print_info(camera)

        # Start acquisition for white balance
        if camera.pixel_format == "RGB24":
            camera.start_acquisition()
            # Do white balance
            camera.do_white_balance(enable=1)
            camera.do_white_balance(enable=0)
            sleep(0.05)
            # Terminate acquisition
            camera.stop_acquisition()

        # define a parameter to sweep here - remove this part in no parameter needed
        param_exposure = [10]
        for p in param_exposure:
            camera.exposure_time = p
            print("\nparam: exposure=" + str(p))
            sleep(0.1)

            # Image acquisition - NBIMAGES (for each parameter step)
            print("\nImage acquisition:")
            if camera.start_acquisition() == 0:
                NBImageAcquired = 0
                for i in range(0, NIMAGES):
                    # Get image from internal buffer
                    im[i, :, :] = camera.get_image()[1]
                    NBImageAcquired += 1
                    print("\r\t" + str(NBImageAcquired) + "/" + str(NIMAGES) + " images acquired", end="\t\t\t")
                print("")

                # Terminate acquisition and start image processing
                if camera.stop_acquisition() == 0:
                    NBImageAcquired = 0

                    #to play with numpy and matplotlib
                    fig = init_figure(camera)

                for i in range(0, NIMAGES):
                    NBImageAcquired += 1

                    """
                    Insert your processing code here
                    image is the current image acquired
                    """

                    image = image_rearange(im[i, :, :], camera.pixel_format)

                    imageProfile(image)
                    update_figure(fig, image, INTERVAL_PLOT, NBImageAcquired)

                    print("\r\t\tEK-image_" + "exp-" + str(p) + "_" + str(NBImageAcquired))
                    print("\t\t\tMin={}".format(np.min(image)))
                    print("\t\t\tMax={} ".format(np.max(image)))
                    print("\t\t\tMean={:.2f} ".format(np.mean(image)))
                    print("\t\t\tStdDev={:.2f} ".format(np.std(image)))

                    # SAVE IMAGE: RAW FORMAT
                    imgName = "EK-image_" + "exp-" + str(p) + "_" + str(NBImageAcquired) + ".raw"
                    with open(imgName, "wb") as f:
                        f.write(image.tobytes())

                    # SAVE IMAGE: TIFF FORMAT
                    # Convert to PIL object to save image in a tiff file
                    # img = Image.fromarray(image, 'RGB')
                    img = Image.fromarray(image, )
                    #imgName = "EK-image_" + str(NBImageAcquired) + ".tiff"
                    imgName = "EK-image_" + "exp-" + str(p) + "_" + str(NBImageAcquired) + ".tiff"
                    img.save(imgName)
                    print("\r\t" + str(NBImageAcquired) + "/" + str(NIMAGES) + " images processed")
                    # This method will show image in any image viewer
                    # img.show()
            else:
                raise Exception("Image acquisition error. Please reboot the camera")

            # Terminate connection
            camera.close()
    else:
        raise Exception("Camera initialization error. Please reboot the camera")
