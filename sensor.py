from evaluationkit import *

DEFAULT_BIN_DIR = "C:/Program Files/Teledyne e2v/Evalkit-Topaz/1.0/pigentl/bin"
DEFAULT_CTI_NAME = "pigentl.cti"
DEFAULT_DLL_NAME = "pigentl-sdk.dll"

# used to map sensor features address from XML file
_xml_bootstrap_nodes_addresses = {
    "DeviceVendorName": 0x0,
    "DeviceModelName": 0x20,
    "DeviceVersion": 0x40,
    "DeviceFirmwareVersion": 0x60,
    "SerialNumber": 0xE0,
    "SensorWidth": 0x1000C,
    "SensorHeight": 0x10010,
    "PixelFormat": 0x10014,
    "AutoExposure": 0x10300,
    "AWBredGain": 0x10410,
    "AWBgreenGain": 0x10414,
    "AWBblueGain": 0x10418,
    "AWBenable": 0x10400,
}

# used to map Sensor features address from XML file
_xml_sensor_nodes_addresses = {
    "BaseAddress": 0x30000,
    "ExposureTime": 0x3000B,
    "VerticalSubsampling": 0x3001D,  # FIXME right address?
    "WaitTime": 0x30009,  # FIXME -> right address? not exist on Topaz ?!
    "LineLength": 0x30006,
    "AnalogGain": 0x3000D,
    "ClampOffset": 0x30022,
     "ChipID": 0x3007F,
}


# used to get the number of bits per pixel from the EK/XML pixel format
xml_pixel_format_nbits = {
    0x01080001: 8,   # Mono8
    0x010A0046: 10,  # Mono10p
    0x02180014: 32,  # RGB24
    8: 0x01080001,   # Mono8
    10: 0x010A0046,  # Mono10p
    32: 0x02180014   # RGB24
}

# used to get the pixel type from the EK/XML pixel format
xml_pixel_format_type = {
    0x01080001: "Mono8",     # Mono8
    0x010A0046: "Mono10p",   # Mono10p
    0x02180014: "RGB24",     # RGB24
    "Mono8":    0x01080001,  # Mono8
    "Mono10p":  0x010A0046,  # Mono10p
    "RGB24":    0x02180014   # RGB24
}

def print_info(ek):
    print("Camera INFO:")
    print("\tManufacturer info          ", ek.vendor_name)
    print("\tDevice name                ", ek.model_name)
    print("\tSerial number              ", ek.serial_number)
    print("\tDevice firmware version    ", ek.firmware_version)
    print("\tImage width                ", ek.sensor_width)
    print("\tImage height               ", ek.sensor_height)
    print("\tPixel format               ", ek.pixel_format)
    print("\tLine length                 %.2f us" % (ek.line_length * 20e-3))
    print("\tExposure time               %.2f ms" % ek.exposure_time)
    print("\tWait time                   %.2f ms" % ek.wait_time)


class Topaz(EvaluationKit):
    def __init__(self, dll_path=None, cti_path=None):
        self.DEFAULT_BIN_DIR = DEFAULT_BIN_DIR
        self.DEFAULT_CTI_NAME = DEFAULT_CTI_NAME
        self.DEFAULT_DLL_NAME = DEFAULT_DLL_NAME
        if dll_path is None:
            dll_path = os.path.join(os.path.dirname(__file__), self.DEFAULT_BIN_DIR, self.DEFAULT_DLL_NAME)
        if cti_path is None:
            cti_path = os.path.join(os.path.dirname(__file__), self.DEFAULT_BIN_DIR, self.DEFAULT_CTI_NAME)
        super().__init__(dll_path, cti_path)

    def __del__(self):
        super().__del__()

    @property
    def clkref(self):
        return 50  # MHz

    @property
    def model_name(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceModelName"], size=32)[1]

    @property
    def vendor_name(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceVendorName"], size=32)[1]

    @property
    def firmware_version(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["DeviceFirmwareVersion"], size=32)[1]

    @property
    def serial_number(self):
        return self.read(address=_xml_bootstrap_nodes_addresses["SerialNumber"], size=16)[1]

    @property
    def pixel_format(self):
        return xml_pixel_format_type[
            int.from_bytes(
                self.read(address=_xml_bootstrap_nodes_addresses["PixelFormat"], size=4, decode=False)[1],
                byteorder="little",
            )
        ]

    @property
    def sensor_width(self):
        return int.from_bytes(
            self.read(address=_xml_bootstrap_nodes_addresses["SensorWidth"], size=4, decode=False)[1],
            byteorder="little",
        )

    @property
    def sensor_height(self):
        return int.from_bytes(
            self.read(address=_xml_bootstrap_nodes_addresses["SensorHeight"], size=4, decode=False)[1],
            byteorder="little",
        )

    @property
    def line_length(self):  # in
        return int.from_bytes(
            self.read(address=_xml_sensor_nodes_addresses["LineLength"], size=2, decode=False)[1], byteorder="little"
        )

    @property
    def wait_time(self):  # in ms
        return (
            int.from_bytes(
                self.read(address=_xml_sensor_nodes_addresses["WaitTime"], size=2, decode=False)[1],
                byteorder="little",
            )
            * (self.line_length / self.clkref)
        ) * 1e-3

    @property
    def exposure_time(self):  # in ms
        return (
            int.from_bytes(
                self.read(address=_xml_sensor_nodes_addresses["ExposureTime"], size=2, decode=False)[1],
                byteorder="little",
            )
            * (self.line_length / self.clkref)
        ) * 1e-3

    @exposure_time.setter
    def exposure_time(self, value):  # in ms
        return self.write(
            address=_xml_sensor_nodes_addresses["ExposureTime"],
            data=np.uint16((value * self.clkref / self.line_length) * 1e3),
        )

    def close(self):
        super().__del__()

    def white_balance(self, red, green, blue):
        # Enable AWB and write red-gree-blue color gains
        # err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(0b1))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBredGain"], data=int(red * 1e6))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBgreenGain"], data=int(green * 1e6))
        err = self.write(address=_xml_bootstrap_nodes_addresses["AWBblueGain"], data=int(blue * 1e6))
        return err

    def enable_white_balance(self, enable):
        # Enable AWB, active when acquisition is running
        if enable == 0:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(0))
        else:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(1))
        return err

    def do_white_balance(self, enable):
        # Enable AWB, active when acquisition is running
        if enable == 0:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(1))
        else:
            err = self.write(address=_xml_bootstrap_nodes_addresses["AWBenable"], data=int(3))
        return err

    def enable_vertical_subsampling(self, enable):
        # Enable AWB, active when acquisition is running
        if enable == 0:
            err = self.write(address=_xml_bootstrap_nodes_addresses["VerticalSubsampling"], data=int(0))
            # No subsampling
        else:
            err = self.write(address=_xml_bootstrap_nodes_addresses["VerticalSubsampling"], data=int(4))
            # Vertical subsampling 2
        return err		

    def read_sensor_reg(self, address):
        addr=address+_xml_sensor_nodes_addresses["BaseAddress"]
        rval=int.from_bytes(self.read(address=addr, size=2, decode=False)[1], byteorder="little", )
        # print("RD 0x{:05x} = 0x{:04x}".format(addr, rval))
        return rval

    def write_sensor_reg(self, address, value):
        addr=address+_xml_sensor_nodes_addresses["BaseAddress"]
        val = np.uint16(value)
        # print("WR 0x{:05x} = 0x{:04x}".format(addr, val))
        error = self.write(address=addr, data=val)
        return error

    def set_camera_format(self, format):
        err = self.write(address=_xml_bootstrap_nodes_addresses["PixelFormat"], data=xml_pixel_format_nbits[format])
        return err