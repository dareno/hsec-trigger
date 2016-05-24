#!/usr/bin/env python3.4

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
import logging
import time
import RPi.GPIO as GPIO     # for reading RaspPi pins
from bus import Bus         # used for HW configuration
import comms.comms as comms # encapsulates communication technology

def configLogging():
    log = logging.getLogger('hsec')

    # has this already run? If so, don't add more handlers or you'll get duplicate logging
    if len(log.handlers):
        return

    # set level of output. DEBUG if in development.
    log.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    log.addHandler(ch)

def get_hardware_config():
    """
    Read some sort of easy to do configuration for how the hardware is setup. Return
    an array that holds MCP23017 class instances.
    """

    # instantiate the bus from the class file. The class file has the 
    # hw configuration specific to this installation.
    busses=Bus()

    #return chip1
    return busses.get_bus_devices() # only return bus1, dev0

def setup():

    # setup logging
    log = logging.getLogger('hsec')
    configLogging()
    log.info("starting home security")

    # setup the array of MCP port expanders
    # best abstraction: bus[0].dev[0].port[0].pin[0]
    #bus = get_hardware_config()
    chips = get_hardware_config()

    # setup interrupt callback function
    GPIO.setmode(GPIO.BOARD)

    # using "GPIO 5", pin 29 for IntA
    GPIO.setup(29,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    # using "GPIO 6", pin 31 for IntA
    GPIO.setup(31,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    return chips

def clean_exit():
    """
    Shut everything down cleanly before exit.
    """
    print("CTRL-C detected, exiting...")
    log = logging.getLogger('hsec')
    # ToDo: shutdown zmq 
    GPIO.cleanup()
    log.info("ending home security")
    logging.shutdown()
    sys.exit(0)

def loop( chips ):
    """
    The main loop that continues to check the hardware and share events that occurred.
    Right now, it handles one chip, but it should handle a list of chips.

    Upon startup, all state will be treated as an event and shared.
    """

    # get the logger handle
    log = logging.getLogger('hsec')

    # setup comms to share events to interested parties
    comm_channel = comms.PubChannel("tcp://*:5563")
    #comm_channel = comms.comms.PubChannel()
    time.sleep(1) # zmq slow joiner syndrome, should sync instead

    # look for events, share them out
    while True:

        # Apparently I need two levels of "try"...
        # https://www.raspberrypi.org/forums/viewtopic.php?f=91&t=114581I
        try:

            # look for new events in the hardware, would use channel here 
            # if there were multiple chips.
            try:
                events = chips[0].get_events()
            except (KeyboardInterrupt, RuntimeError) as e:
                clean_exit()
    
            # share events with those interested
            if len(events)>0:
                channel = "sensor_events"
                print("sending %s" % events)
                comm_channel.send(channel, events)
    
            # block until there's another event or timeout occurs
            try:
		# will need to update this for IntB when we have enough sensors
		# and want it to be efficient
                channel = GPIO.wait_for_edge(29, GPIO.RISING, timeout=1)
            except (KeyboardInterrupt, RuntimeError) as e:
                clean_exit()
        except (KeyboardInterrupt, RuntimeError) as e:
            clean_exit()
            

if __name__ == '__main__':

    # setup returns a chip and passes it to loop.
    loop(setup())


