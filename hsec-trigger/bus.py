"""
Not sure if this is easier to read and modify than just using configparser. This file is meant
to be configured per hardware configuration.
"""
from MCP23017 import MCP23017

class Bus:
    def __init__(self):
        self.bus=[]
        self.bus.append([])    # bus 0 isn't used here
        self.bus.append([])    # we'll use bus1 on RPi 2

        self.bus[1].append(MCP23017(1,0x20)) # add device b'000'

        # configure the pins
        self.bus[1][0].portA.pins[7].set_description("Garage Door").set_enable(True)
        self.bus[1][0].portA.pins[6].set_description("Front Door").set_enable(True)
        self.bus[1][0].portA.pins[5].set_description("Laundry Door").set_enable(True)
        self.bus[1][0].portA.pins[4].set_description("Family Room Door").set_enable(True)
        self.bus[1][0].portA.pins[3].set_description("Kitchen Door").set_enable(True)
        self.bus[1][0].portA.pins[2].set_description("Family Room PIR").set_enable(True)

    def return_bus(self):
        return Bus()

    def get_bus_devices(self):
        return [self.bus[1][0]] # I only have (bus1, device0 in hardware)
