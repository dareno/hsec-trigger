#!/usr/bin/env python3.4
"""
This class is responsible for sending messages about changing events. 
ZMQ is the communication technology and is entirely abstracted by this class.

Should probably generalize the two classes to send and receive classes.
"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import datetime
import time
import zmq
import json
import queue
from threading import Thread

class PubChannel:
    """
    Use a message queue technology to share events.
    Based on http://zguide.zeromq.org/py:psenvpub
    """

    def __init__(self, address):

        # prepare context and publisher
        self.context     = zmq.Context()
        self.publisher   = self.context.socket(zmq.PUB)
        self.publisher.bind(address)


    def send(self, channel, message):
        """
        Call like this:
            channel = 'events'
            message = ['one','two','three']
            PubChannel.send(channel,message)
        """

        # convert list to JSON
        events_to_send = json.dumps(message)

        # send 
        self.publisher.send_multipart([
            channel.encode('utf-8'),
            events_to_send.encode('utf-8')
            ])

class SubChannel:
    """
    Only the actor uses this class.
    """

    def __init__(self, address, channels):

        # Prepare our context and publisher
        self.context    = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(address)

        # subscribe to some channels
        for channel in channels:
            self.subscriber.setsockopt(zmq.SUBSCRIBE, channel.encode('utf-8'))

        # create a queue for the messages to go on and run without blocking
        self.q = queue.Queue(maxsize=100)
        self.worker = Thread( target=self.recv_msg )
        self.worker.setDaemon(True)
        self.worker.start()
    
    
        # clean up zmq connection
        #subscriber.close()
        #context.term()
    
    def recv_msg(self):
        """
        Block until messages are received, put them in the queue
        """

        while True:
            # get the envelope and message, put it on the shared queue
            [address, contents] = self.subscriber.recv_multipart()
            self.q.put([address,contents])

    def get(self):
        """
        Return the channel too...
        """

        # Read envelope and address from queue
        try:
            # get something off the queue, but don't wait for it
            [address, contents] = self.q.get(False)
        except queue.Empty:
            # raise an exception?
            time.sleep(.1)
            return None
            #time.sleep(0.1)
        else:
            self.q.task_done()
            #print("[%s] %s" % (address, contents))
            return [address,contents]

