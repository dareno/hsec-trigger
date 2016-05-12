#!/usr/bin/env python3.4
"""
I originally thought of using computerlyrik/MCP23017-RPi-python but it seemed overly 
complex/full-featured for what I wanted.  I wrote this from scratch based on the 
abstractions that made sense to me but I followed some conventions that computerlyrik
was using in order to ease a transition to his module if I later decide to and also 
to make mine more understandable in the context of the other.  Also, I use smbus where
his uses i2c. They really aren't similar at all but I want to make it clear that I was
reading computerlyrik/MCP23017-RPi-python and following some of those conventions/styles.
"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import smbus
import logging
import time

log = logging.getLogger('hsec')


class Port:
    """
    All the MCP operations happen at the port level on an 8-bit register, one bit per port.

    This should work for MCP23008 if we were to use bank1 addressing and portA
    register addresses.
    """

    def __init__(self, bus, address, name, register_mapping):
        self.BUS=bus
        self.DEVICE_ADDRESS=address
        self.name=name
        self.REGISTER = register_mapping
        self.status_byte = None
        self.pin_state = None

        # The following MCP register settings enable interrupts
        #      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
        # 00: ff ff 00 00 ff ff 00 00 00 00 42 42 fc ff 00 00
        # 10: fc ff fc ff 00 00 
        #
        # Commentary on some interesting pins
        # -----------------------------------
        # 0x00 - IODIR: input on GPIO
        # 0x04 - GPINTEN: enables interupt-on-change
        # 0x08 - INTCON: 0 means interrupt if changed from previous value
        # 0x0a - IOCON: config register, set MIRROR (one GPIO pin for any register
        #        change) and IOPOL (1 for interrupt == python True)
        # 0x0c - GPPU: if the port isn't in use, it should be pulled to prevent
        #        change and thus interrupts. This is an internal 100k ohm resistor
        #        but I'm using 10K ohm resistors to get more current over the 
        #        reed sensors, as recommended in some web sites on the topic.
        #        I only pull the ports that I haven't configured with pull resistors
        #        in hardware yet. Right now, I have GPA0 and GPA1 so I don't set
        #        a pull resistor on those, but the others float so they are pulled.
        # 0x0e - INTF: use this to identify the GP port that caused the interrupt.
        #        I'm not using this, just checking each GP value. Could use this if 
        #        I wanted to be more clever.

        # setup the pins for reading/input
        self.BUS.write_byte_data(self.DEVICE_ADDRESS, self.REGISTER['IODIR'], 0xFF) # 

        # Activate Interrupt OnChange
        self.BUS.write_byte_data(self.DEVICE_ADDRESS, self.REGISTER['GPINTEN'], 0xFF)

        # Connect Interrupt-Pin with the other port (MIRROR)
        self.BUS.write_byte_data(self.DEVICE_ADDRESS, self.REGISTER['INTCON'], 0x00)

        # Connect Interrupt-Pin with the other port (MIRROR)
        self.BUS.write_byte_data(self.DEVICE_ADDRESS, self.REGISTER['IOCON'], 0x42)

    def xor(self, x, y):
        """
        Exclusive Or
        Probably belongs in a utility class
        Returns True if (x and !y) OR (!x and y)
        """
        return ((x and not y) or (not x and y)) == True

    def get_events(self, port_name):
        """
        Return a list of new events that occurred. Format is [event,...]
        event is a list of [(<pin name>,<closed state>),...]

        An MCP port has 8 pins. Put the pin and closed state in the list if changed.
        """

        # save the last polled pin register state for comparison
        old_pin_state = 0   # want this to be int type instead of NoneType
        old_pin_state = self.pin_state # 'None' the first time


        # update the pin state byte, updating the interrupt
        self.pin_state = self.BUS.read_byte_data(self.DEVICE_ADDRESS, self.REGISTER['GPIO'])

        # copy new state to a variable that we can destructively shift; best approach? 
        new_pin_state = self.pin_state

        #log.debug ("Port.get_events() new pin state: %s" % (format(register, '08b')))

        # This section has poor style. It needs a refactor. Create a list of events
        # based on the pins that changed in the new and old pin byte
        CLOSED=0
        events = []

        for x in range(0,8):
            if old_pin_state is None:   
                # when first started, consider state to have changed
                pin_changed_value=True
            else:
                pin_changed_value = self.xor(old_pin_state&1, new_pin_state&1)

                # This byte shift is here because--on first run when Nonetype--
                # it won't try to shift here. Also, not used later in this function.
                old_pin_state = old_pin_state >> 1   

            if pin_changed_value:

                # set the new value
                this_pin_value = new_pin_state & 1
                pin_is_closed = (this_pin_value==CLOSED)

                # since it changed, call it an event and add to the list
                events.append([port_name+str(x),pin_is_closed])


            # new_pin_state is never Nonetype, unlike old_pin_state
            new_pin_state = new_pin_state >> 1   

        return events

class MCP23017:

    def __init__(self, busId, address):
        """
        The HW designer knows the bus and address of the chip. He also knows the GPIO pin used for 
        the interrupt. 
        """
        self.bus = smbus.SMBus(busId)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self.address = address
        log.debug ("creating an MCP23017 chip at bus %s address 0x%s" % (busId, format(address,'02x')))

        # this is "bank 0" addressing, switching to "bank 1" addressing would make it 
        # easier to support mcp23008.
        self.REGISTER_MAPPING = { 
            'A' : {
                'IODIR': 0X00,
                'IPOL': 0X02,
                'GPINTEN': 0X04,
                'DEFVAL': 0X06,
                'INTCON': 0X08,
                'IOCON': 0X0A,
                'GPPU': 0X0C,
                'INTF': 0X0E,
                'INTCAP': 0X10,
                'GPIO': 0X12,
                'OLAT': 0X14
              },
             'B': {
                'IODIR': 0X01,
                'IPOL': 0X03,
                'GPINTEN': 0X05,
                'DEFVAL': 0X07,
                'INTCON': 0X09,
                'IOCON': 0X0B,
                'GPPU': 0X0D,
                'INTF': 0X0F,
                'INTCAP': 0X11,
                'GPIO': 0X13,
                'OLAT': 0X15
              }
        }

        # setup port A, 0xFC means that the first two ports have HW pull up resistors
        #self.portA = Port(self.bus, self.address, "GPA", self.REGISTER_MAPPING['A'], 0xFC)
        self.portA = Port(self.bus, self.address, "GPA", self.REGISTER_MAPPING['A'])

        # setup port B, 0xFF means that none of the ports have HW pull up resistors
        #self.portB = Port(self.bus, self.address, "GPB", self.REGISTER_MAPPING['B'], 0xFF)
        self.portB = Port(self.bus, self.address, "GPB", self.REGISTER_MAPPING['B'])

    def get_events(self):
        """
        return a list of new events that occurred. Format is [event,...]
        event is a list of [<pin name>,<closed state>]
        """
        events = []
        events = self.portA.get_events("MCP0:GPA") + self.portB.get_events("MCP0:GPB")

        return events

