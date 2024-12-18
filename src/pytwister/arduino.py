# SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Michael Liebling <michael.liebling@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

"""
A set of functions to interact with an Arduino
and a Sparkfun stepper motor driver.
"""

import time
from typing import Optional
import serial
import serial.tools.list_ports
from packaging import version

# Arduino Firmware Requirements
REQUIRED_FIRMWARE_NAME = "ArduinoPyTwister"
MINIMUM_FIRMWARE_VERSION = "0.1"
# Arduino Instruction Codes
RESET_CODE = "RES"
FIRMWARE_CODE = "FIR"
VERSION_CODE = "VER"
TURN_CODE_PREFIX = "T"
# Arduino and Motor Driver Parameters
STEP_SIZE = 0.225  # degrees
ACK = 0  # successful completion
ERR = 1  # error
# Delays
# How long to wait for Arduino to finish initializing
INITIALIZE_DELAY = 2  # seconds
# how long to wait before time out when reading
# from serial port
TIME_OUT = 5  # seconds


def get_comport_list() -> Optional[list]:
    """
    Returns a list of all available COM ports
    ListPortInfo objects or None if none is found.
    Wrapper around serial.tools.list_ports.comports.
    """
    com_port_list = serial.tools.list_ports.comports()
    if len(com_port_list) == 0:
        com_port_list = None
    return com_port_list


def get_arduino_ports(com_port_list: list) -> Optional[list]:
    """
    Probe serial com ports provided in list
    com_port_list and return a list of those containing
    `Arduino` in their description or None if none found.
    """
    arduino_ports = [p.device for p in com_port_list if "Arduino" in p.description]
    if len(arduino_ports) == 0:
        return None
    return arduino_ports


def get_arduino_firmware_name(ser) -> str:
    """
    Returns firmware name (as a string) or a
    message obtained from a request to an Arduino
    which was already initialized and to which
    connection is done via the provided Serial
    object ser.
    """
    msg_b = bytes(FIRMWARE_CODE, "utf-8")
    print(f"Sending message >{msg_b.decode('utf-8')}<...")
    ser.write(msg_b)
    arduino_msg = ser.readline().decode("utf-8").rstrip()
    if arduino_msg != "":
        print(f"Arduino replied >{arduino_msg}<...")
        firmware_name = arduino_msg
    else:
        firmware_name = "No Arduino firmware name could be retrieved."
    return firmware_name


def get_arduino_firmware_version(ser) -> str:
    """
    Returns firmware version (as a string) or a
    message obtained from a request to an Arduino
    which was already initialized and to which
    connection is done via the provided Serial
    object ser.
    """
    msg_b = bytes(VERSION_CODE, "utf-8")
    print(f"Sending message >{msg_b.decode('utf-8')}<...")
    ser.write(msg_b)
    arduino_msg = ser.readline().decode("utf-8").rstrip()
    if arduino_msg != "":
        print(f"Arduino replied >{arduino_msg}<...")
        firmware_version = arduino_msg
    else:
        firmware_version = "No Arduino firmware version could be retrieved."
    return firmware_version


def get_serial_object_to_arduino(arduino_port):
    """
    Open and initialize Arduino, return handle to
    Serial object that allows communicating with
    the Arduino.
    """
    ser = serial.Serial(arduino_port, timeout=TIME_OUT)
    ser.reset_input_buffer()
    print(f"Giving the Arduino {INITIALIZE_DELAY} seconds to intialize...")
    time.sleep(INITIALIZE_DELAY)
    print("The wait is over, returning Serial Object.")
    return ser


def scan_list_for_arduinopytwister(arduino_ports: list):
    """
    Scan a list of ports, open each to check
    if they are arduinotwister objects, then close them.
    If firmware and version requirements are met,
    return the port, return None otherwise.
    Note: all tested ports (including the port that is
    returned, if found) are closed.
    """
    arduino_twister_port = None
    for port_to_check in arduino_ports:
        ser = get_serial_object_to_arduino(port_to_check)
        if check_arduino_is_twister_arduino(ser):
            arduino_twister_port = port_to_check
            ser.close()
            break
        ser.close()
    return arduino_twister_port


def check_arduino_is_twister_arduino(ser) -> bool:
    """
    Check whether Arduino linked to Serial object
    ser has the correct ArduinoPyTwister firmware
    and version. Returns True if requirements are
    met, False otherwise.
    """
    requirements_met = False
    firmware_name = get_arduino_firmware_name(ser)
    if firmware_name == REQUIRED_FIRMWARE_NAME:
        print(f"Correct Arduino detected, firmware is: {firmware_name} ")
        firmware_version = get_arduino_firmware_version(ser)
        print(f"Arduino replied: >{firmware_version}<.")
        if version.parse(MINIMUM_FIRMWARE_VERSION) <= version.parse(firmware_version):
            print(
                (
                    "Correct Arduino firmware and version"
                    + f" >{firmware_name}< version >{firmware_version}<."
                )
            )
            requirements_met = True
        else:
            print(
                (
                    "Incorrect Arduino firmware and version"
                    + f" >{firmware_name}< version >{firmware_version}<."
                )
            )
    return requirements_met


def rotate_by_steps(ser, steps: int):
    """
    Tell stepper motor on serial port `ser`
    to rotate by `steps` times 0.225° degrees.

    Rotation table for Sparkfun Easy Driver
    in eigth-step mode:
    1 step: 1.8°/8 = 0.2250°
    8 steps: 1.8°
    steps   angle      # steps    # steps
            increment  in 180°    in 360°
        1    0.225°        800       1600
        8    1.8°          100        200
       16    3.6°           50        100
       80   18°             10         20
      100   22.5°            8         16
      200   45°              4          8
      400   90°              2          4
      800  180°              1          2
    """

    ser.write(assemble_rotate_command(steps))
    status_code_bytes = ser.read(1)
    status_code = int.from_bytes(status_code_bytes, byteorder="little")
    print(f"status code is >{status_code}<.")


def assemble_rotate_command(steps: int) -> bytes:
    """assemble a rotation command that consists of three bytes
    first byte contains the rotation character TURN_CODE_PREFIX
    second and third bytes contain the signed
    integer number of steps.
    """

    if not -32768 <= steps <= 32767:
        raise ValueError(
            f"Steps is too big: got {steps} but shoud be in [-32768, 32767]"
        )

    turn_code_as_byte = bytearray(bytes(TURN_CODE_PREFIX, "utf-8"))
    steps_as_two_bytes = bytearray(steps.to_bytes(2, "little", signed=True))
    rotate_command = b"".join([turn_code_as_byte, steps_as_two_bytes])
    return rotate_command


def main() -> None:
    """
    Demo arduino_twister
    """
    port_list = get_comport_list()
    if port_list is None:
        print(("Did not find any COM ports."))
        return
    arduino_ports = get_arduino_ports(port_list)
    if arduino_ports is None:
        print(
            ("Did not find any arduino ports. " + "Check that an Arduino is connected!")
        )
        return
    twister_port = scan_list_for_arduinopytwister(arduino_ports)
    if twister_port is None:
        print(
            (
                "Did not find a twister arduino connected ot any port. "
                + "Check the connected Arduino has the correct "
                + "firmware and version uploaded!"
            )
        )
        return
    ser = get_serial_object_to_arduino(twister_port)
    if ser is not None:
        rotate_by_steps(ser, -200)
        rotate_by_steps(ser, 200)


if __name__ == "__main__":
    main()
