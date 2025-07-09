# py_evalkit_topaz
A python code to play with Topaz EVK

## Requirements
Works with Python3

Please install the packages list available in `requirements.txt`  

Before starting, make sure this path is path is correct in the file `sensor.py`:

```DEFAULT_BIN_DIR = "C:/Program Files/Teledyne e2v/Evalkit-Topaz/1.0/pigentl/bin"```

## Image Acquisition
The main project file is `image_acquisition.py`

After defining a number of images to acquire, that is also possible to sweep a parameter like the exposure time (in ms).
The example save RAW image + TIFF image and generates some statistics like Mean or StandardDeviation.
Images are displayed and profiles calculated.

Feel free to comment the unnecessary functions and add your own processing !