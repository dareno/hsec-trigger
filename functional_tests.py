#!/usr/bin/python3
"""
Not really functional tests but where I was in terms of using unittest. Needs to be completely
re-written.

"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
#from test import test_support	#python2

import smbus
DEVICE_ADDRESS = 0x20
IODIRA = 0x00
IODIRB = 0x01
IPOLA = 0x02
IPOLB = 0x03
GPINTENA = 0x04
GPINTENB = 0x05
DEFVALA = 0x06
DEFVALB = 0x07
INTCONA = 0x08
INTCONB = 0x09
IOCON = 0x0A
#IOCON = 0x0B
GPPUA = 0x0C
GPPUB = 0x0D
GPIOA = 0x12
GPIOB = 0x13
OLATA = 0x14
OLATB = 0x15

# RPi interrupt GPIO 29
import RPi.GPIO as GPIO
INTPORT = 29

class MCP23017(unittest.TestCase):
    bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

    #def setUp(self):
    def test0_setUp(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(INTPORT,GPIO.IN)

    #def tearDown(self):
    def test9_tearDown(self):
        GPIO.cleanup()

    def test1_PrintInt(self):
        print ("before, GPIO pin ", INTPORT, ": ", GPIO.input(INTPORT))

    def test3_waiting(self):
        seconds = 10
        print ("sleeping for ", seconds)
        import time
        time.sleep(seconds)

    def test4_PrintInt(self):
        print ("after, GPIO pin ", INTPORT, ": ", GPIO.input(INTPORT))

    def test1_set_IODIR(self):
        pass
        # Test feature one.
        orig_value = self.bus.read_byte_data(DEVICE_ADDRESS, IODIRA)
        self.bus.write_byte_data(DEVICE_ADDRESS, IODIRA, 0xFF)
        self.assertEqual( self.bus.read_byte_data(DEVICE_ADDRESS, IODIRA), 0xFF)
        self.bus.write_byte_data(DEVICE_ADDRESS, IODIRA, orig_value)

    def test2_feature_two(self):
        # test that an interrupt will be raised 
        #GPIO.input(INTPORT), " ", self.bus.read_byte_data(DEVICE_ADDRESS, GPIOA)

        # Define complete Port A as IN-Port:
        # sudo i2cset -y 1 0x20 0x00 0xFF
        self.bus.write_byte_data(DEVICE_ADDRESS, IODIRA, 0xFF)

        # Define complete Port B as IN-Port:
        # sudo i2cset -y 1 0x20 0x01 0xFF
        self.bus.write_byte_data(DEVICE_ADDRESS, IODIRB, 0xFF)

        # Activate all internal pullup resistors at Port A:
        # sudo i2cset -y 1 0x20 0x0C 0xFF
        # don't pull up the first two, we have HW resistors
        self.bus.write_byte_data(DEVICE_ADDRESS, GPPUA, 0xFC)

        # Activate all internal pullup resistors at Port B:
        # sudo i2cset -y 1 0x20 0x0D 0xFF
        self.bus.write_byte_data(DEVICE_ADDRESS, GPPUB, 0xFF)

        # Activate Interrupt OnChange for Port A:
        # sudo i2cset -y 1 0x20 0x04 0xFF
        self.bus.write_byte_data(DEVICE_ADDRESS, GPINTENA, 0xFF)

        # Activate Interrupt OnChange for Port B:
        # sudo i2cset -y 1 0x20 0x05 0xFF
        self.bus.write_byte_data(DEVICE_ADDRESS, GPINTENB, 0xFF)

        # Connect Interrupt-Pin A with the one of B:
        # sudo i2cset -y 1 0x20 0x0A 0x40
        self.bus.write_byte_data(DEVICE_ADDRESS, 0x0A, 0x40)

        # Connect Interrupt-Pin B with the one of A:
        # sudo i2cset -y 1 0x20 0x0B 0x40
        self.bus.write_byte_data(DEVICE_ADDRESS, 0x0B, 0x40)

        

        #print "before read GPIOA ", GPIO.input(INTPORT)
        # Test: Read GPIO-Byte from Port A:
        # sudo i2cget -y 1 0x20 0x12
        # this line will reset the interrupt
        print (self.bus.read_byte_data(DEVICE_ADDRESS, GPIOA))

        # Test: Read GPIO-Byte from Port B:
        # sudo i2cget -y 1 0x20 0x13
        print (self.bus.read_byte_data(DEVICE_ADDRESS, GPIOB))

        #print "after read GPIOA ", GPIO.input(INTPORT)


class MyTestCase2(unittest.TestCase):
    pass


# python2
def test_main():
    test_support.run_unittest(MCP23017,
                              MyTestCase2,
                             )

if __name__ == '__main__':
    #test_main() #python2
    unittest.main() #python3
