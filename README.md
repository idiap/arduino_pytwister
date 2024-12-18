<!--
SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
-->

# arduino_pytwister

## Description

This Python library allows interacting with a stepper motor that rotates a stage. The stepper motor is connected to a Sparkfun driver which is itself connected to an Arduino microcontroller.

## Installation

arduino_pytwister has been developed for Python 3.

```bash
conda create -n envname python>=3.7
conda activate envname
pip install .
```

On Linux, add yourself to the `dialout`group
```bash
sudo usermod -a -G dialout $USER
```

### Arduino

arduino_pytwister expects to interact with an Arduino Uno. The latter is connected to an [EasyDriver Stepper Motor Driver - ROB-12779 by SparkFun Electronics](https://www.sparkfun.com/products/12779).

The wiring is as follows:

![EasyDriverHookup](https://cdn.sparkfun.com/assets/learn_tutorials/2/4/1/EasyDriverHookup_bb2.png)

Connect the arduino to the computer USB and to a power source.

Open the `ArduinoPyTwisterFirmware/ArduinoPyTwisterFirmware.ino` with the [Arduino IDE software](https://www.arduino.cc/en/software) and upload it to the Arduino.

## Usage

The package provides the following key functions:

1. `get_comport_list`: wrapper function to identify available serial ports
2. `get_arduino_ports`: function to identify serial ports linked to connected arduinos
3. `scan_list_for_arduinopytwister`: function to identify the serial port linked to a connected arduino with the correct `ArduinoPyTwisterFirmware.ino` code uploaded.
4. `get_serial_object_to_arduino`: function to obtain a serial object that can be used to communicate with the arduino
5. `rotate_by_steps`: the function to instruct rotation

An example of a simple interation would be:

```python
import pytwister as pt
port_list = pt.arduino.get_comport_list()
arduino_ports = pt.arduino.get_arduino_ports(port_list)
twister_port = pt.arduino.scan_list_for_arduinopytwister(arduino_ports)
ser = pt.arduino.get_serial_object_to_arduino(twister_port)
pt.arduino.rotate_by_steps(ser, -200)
pt.arduino.rotate_by_steps(ser, 200)
```

The number of steps can be any integer in the range [-32768,32767].

Each step corresponds to 0.225° (degrees).

The `Twister` convenience class gives a high-level control interface.
An example of the same simple iteration would be:

```python
import pytwister as pt
twister = pt.Twister()
twister.rotate_rel(45)
twister.rotate_abs(0)
```

Conversion table for Sparkfun Easy Driver in eigth-step mode:

| steps | angle increment |
| ----: | :---:           |
| 1     | 1.8°/8 =0.225°  |
| 8     | 1.8°            |
| 16    | 3.6°            |
| 80    | 18°             |
| 100   | 22.5°           |
| 200   | 45°             |
| 400   | 90°             |
| 800   | 180°            |
| 1600  | 360°            |

## Support

This software is provided as-is.

## Contributing

Extensions should be accompanied by a test and clear function/class headers. Tests are gathered in `test_arduino_twister.py`

```python
python3 -m unittest discover tests
```

The tests are run in "dummy" mode and there is currently no requirement that an arduino is connected.

## Authors and acknowledgment

Michael Liebling
Idiap Research Institute
April 2023

Francois Marelli
Idiap Research Institute
April 2023

inspired by related projects (µmanager, etc.)

## License

BSD-3
