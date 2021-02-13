# Credit for a lot of the code: https://github.com/matlo/gimx-network-client

import socket
import struct
import sys
import os
import pprint
import pygame
import time
from enum import IntEnum
from time import sleep

DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 51914

class Ps4Controls(IntEnum):
    LEFT_STICK_X = 0
    LEFT_STICK_Y = 1
    RIGHT_STICK_X = 2
    RIGHT_STICK_Y = 3
    FINGER1_X = 4
    FINGER1_Y = 5
    FINGER2_X = 6
    FINGER2_Y = 7
    SHARE = 128
    OPTIONS = 129
    PS = 130
    UP = 131
    RIGHT = 132
    DOWN = 133
    LEFT = 134
    TRIANGLE = 135
    CIRCLE = 136
    CROSS = 137
    SQUARE = 138
    L1 = 139
    R1 = 140
    L2 = 141
    R2 = 142
    L3 = 143
    R3 = 144
    TOUCHPAD = 145
    FINGER1 = 146
    FINGER2 = 147
    
class ButtonState(IntEnum):
    RELEASED = 0
    PRESSED = 255


def send_message(ip, port, changes):
    
    packet = bytearray([0x01, len(changes)])  # type + axis count
    
    for axis, value in changes.items():
        # axis + value (network byte order)
        packet.extend([axis, (value & 0xff000000) >> 24, (value & 0xff0000) >> 16, (value & 0xff00) >> 8, (value & 0xff)])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (ip, port))


def check_status(ip, port):
    
    packet = bytearray([0x00, 0x00])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ip, port))
    sock.send(packet)
    timeval = struct.pack('ll', 1, 0)  # seconds and microseconds
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
    try:
        data, (address, port) = sock.recvfrom(2)
        response = bytearray(data)
        if (response[0] != 0x00):
            print("Invalid reply code: {0}".format(response[0]))
            return 1
    except socket.error as err:
        print(err)
    
    return 0

ip = DEFAULT_IP
port = DEFAULT_PORT

if check_status(ip, port):
    sys.exit(-1)
    
def bool_to_button(_bool):
    return int(_bool)*255

def parse_button_dict(button_dict):
    """
    Returns a dict with the names of the buttons as keys and the values as integers.
    """
    name_dict = {}
    for key in button_dict.keys():
        if key == 0:
            name_dict["cross"] = bool_to_button(button_dict[key])
        if key == 1:
            name_dict["circle"] = bool_to_button(button_dict[key])
        if key == 2:
            name_dict["triangle"] = bool_to_button(button_dict[key])
        if key == 3:
            name_dict["square"] = bool_to_button(button_dict[key])
        if key == 4:
            name_dict["l1"] = bool_to_button(button_dict[key])
        if key == 5:
            name_dict["r1"] = bool_to_button(button_dict[key])
        if key == 6:
            name_dict["l2"] = bool_to_button(button_dict[key])
        if key == 7:
            name_dict["r2"] = bool_to_button(button_dict[key])
        if key == 8:
            name_dict["share"] = bool_to_button(button_dict[key])
        if key == 9:
            name_dict["options"] = bool_to_button(button_dict[key])
        if key == 10:
            name_dict["PS"] = bool_to_button(button_dict[key])
        if key == 11:
            name_dict["l3"] = bool_to_button(button_dict[key])
        if key == 12:
            name_dict["r3"] = bool_to_button(button_dict[key])
    return name_dict

def bool_to_axis(_bool):
    return int(_bool)*127

def axis_parser(axis_dict):
    """
    Returns a dict with the names of the axes as keys and the values scaled properly.
    """
    name_dict = {}
    for key in axis_dict.keys():
        if key == 0:
            name_dict["LEFT_STICK_X"] = int(axis_dict[key]*127)
        if key == 1:
            name_dict["LEFT_STICK_Y"] = int(axis_dict[key]*127)
        if key == 3:
            name_dict["RIGHT_STICK_X"] = int(axis_dict[key]*127)
        if key == 4:
            name_dict["RIGHT_STICK_Y"] = int(axis_dict[key]*127)
    return name_dict

def parse_arrow_dict(arrow_dict):
    name_dict = {}
    name_dict["left"] = 255 if arrow_dict[0][0] == -1 else 0
    name_dict["right"] = 255 if arrow_dict[0][0] == 1 else 0
    name_dict["up"] = 255 if arrow_dict[0][1] == 1 else 0
    name_dict["down"] = 255 if arrow_dict[0][1] == -1 else 0
    return name_dict

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""
        
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def listen(self):
        """Listen for events to happen"""
        
        if not self.axis_data:
            self.axis_data = {0:0,1:0,3:0,4:0}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)
                
        millis = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value,1)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                # Insert your code on what you would like to happen for each event here!
                # In the current setup, I have the state simply printing out to the screen.
                
                os.system('clear')
                print(self.button_data,self.axis_data,self.hat_data, (" "*150), end='\r' )
                b_dict = parse_button_dict(self.button_data)
                a_dict = axis_parser(self.axis_data)
                ar_dict = parse_arrow_dict(self.hat_data)
                state = {
                    Ps4Controls.LEFT_STICK_X : a_dict["LEFT_STICK_X"],
                    Ps4Controls.LEFT_STICK_Y : a_dict["LEFT_STICK_Y"],
                    Ps4Controls.RIGHT_STICK_X : a_dict["RIGHT_STICK_X"],
                    Ps4Controls.RIGHT_STICK_Y : a_dict["RIGHT_STICK_Y"],
                    Ps4Controls.SHARE : b_dict['share'],
                    Ps4Controls.OPTIONS : b_dict['options'],
                    Ps4Controls.PS : b_dict['PS'],
                    Ps4Controls.UP : ar_dict['up'],
                    Ps4Controls.RIGHT : ar_dict['right'],
                    Ps4Controls.DOWN : ar_dict['down'],
                    Ps4Controls.LEFT : ar_dict['left'],
                    Ps4Controls.TRIANGLE : b_dict['triangle'],
                    Ps4Controls.CIRCLE : b_dict['circle'],
                    Ps4Controls.CROSS : b_dict['cross'],
                    Ps4Controls.SQUARE : b_dict['square'],
                    Ps4Controls.L1 : b_dict['l1'],
                    Ps4Controls.R1 : b_dict['r1'],
                    Ps4Controls.L2 : b_dict['l2'],
                    Ps4Controls.R2 : b_dict['r2'],
                    Ps4Controls.L3 : b_dict['l3'],
                    Ps4Controls.R3 : b_dict['r3'],
                    }
                if (curr_time := int(round(time.time() * 1000))) > millis+30:
                    millis = curr_time
                    send_message(ip, port, state)
                    print(f"sent at {millis}", end='\r')

if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
