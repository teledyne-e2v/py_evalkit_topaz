# py_evalkit_topaz
A python code to play with Topaz EVK

## Requirements
Works with Python3

Please install the packages list available in `requirements.txt`  

Before starting, make sure this path is path is correct in the file `sensor.py`:

```DEFAULT_BIN_DIR = "C:/Program Files/Teledyne e2v/Evalkit-Topaz/1.0/pigentl/bin"```

## Image Acquisition
The main project file is `image_acquisition.py`

The number of images to acquire can be set with the variable `NIMAGES`

That is also possible to sweep a parameter like the exposure time (in ms). In this case the number of images is valid for each parameter step.

The example saves RAW image + TIFF image and generates some statistics like Mean or StandardDeviation.
Images are displayed and profiles calculated.

For external trigger use, please uncomment lines 40/41 and define a number of frames you want to acquire in total with the variable `NIMAGES`

Feel free to comment the unnecessary functions and add your own processing !