"""
Not sure if this is easier to read and modify than just using configparser. This file is meant
to be configured per hardware configuration.
"""
from MCP23017 import MCP23017

class Bus:
    def __init__(self):
        self.bus=[]
        self.bus.append([])    # create bus 0, not used
        self.bus.append([])    # create bus 1; we'll use bus1 on RPi 2

        self.bus[1].append(MCP23017(1,0x20)) # add device b'000'

    def return_bus(self):
        # find myself wondering why I did this...
        # looks like a defect in that I'm returning a new Bus object instead of self...
        return Bus()

    def get_bus_devices(self):
        return [self.bus[1][0]] # I only have (bus1, device0 in hardware)
