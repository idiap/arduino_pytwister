# SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Michael Liebling <michael.liebling@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
from unittest.mock import Mock
from unittest.mock import patch
from pytwister import arduino as at


class TestArduinoTwister(unittest.TestCase):
    """
    A test class for the Arduino Twister functions
    """

    def test_assemble_rotate_command(self):
        """
        Test the rotation command assembly function
        """
        value_computed = at.assemble_rotate_command(0)
        value_expected = b"T\x00\x00"
        self.assertEqual(
            value_expected,
            value_computed,
            msg="Expected and computed rotation commands differ!",
        )

    def test_get_arduino_firmware_name_some_name(self):
        """
        Test the function that gets the arduino firmware name
        """
        ser = Mock()
        ser.readline = Mock(return_value=(("SomeFirmwareName\n").encode("utf-8")))
        value_computed = at.get_arduino_firmware_name(ser)
        value_expected = "SomeFirmwareName"
        self.assertEqual(
            value_expected, value_computed, msg="Expected and computed response differ!"
        )

    def test_get_arduino_firmware_name_timeout(self):
        """
        Test the function that gets the arduino firmware name
        """
        ser = Mock()
        ser.readline = Mock(return_value=b"")
        value_computed = at.get_arduino_firmware_name(ser)
        value_expected = "No Arduino firmware name could be retrieved."
        self.assertEqual(
            value_expected, value_computed, msg="Expected and computed response differ!"
        )

    def test_get_arduino_ports_with_arduino_present(self):
        """
        Test the function get_arduino_ports when an
        arduino is present.
        """
        port1 = Mock()
        port1.description = "Some port"
        port1.device = "device1"
        port2 = Mock()
        port2.description = "Some Arduino port"
        port2.device = "device2"
        com_port_list = [port1, port2]
        value_computed = at.get_arduino_ports(com_port_list)
        value_expected = [port2.device]
        self.assertEqual(
            value_expected,
            value_computed,
            msg="Expected and computed Arduino port lists differ!",
        )

    def test_get_arduino_ports_without_arduino_present(self):
        """
        Test the function get_arduino_ports when there is
        no Arduino present.
        """
        port1 = Mock()
        port1.description = "Some port"
        port1.device = "device1"
        port2 = Mock()
        port2.description = "Some other port"
        port2.device = "device2"
        com_port_list = [port1, port2]
        value_computed = at.get_arduino_ports(com_port_list)
        value_expected = None
        self.assertEqual(
            value_expected,
            value_computed,
            msg="Expected and computed Arduino port lists differ!",
        )

    def test_get_arduino_version_some_version(self):
        """
        Test the function that gets the arduino firmware version
        """
        ser = Mock()
        ser.readline = Mock(return_value=(("0.2.3\n").encode("utf-8")))
        value_computed = at.get_arduino_firmware_version(ser)
        value_expected = "0.2.3"
        self.assertEqual(
            value_expected, value_computed, msg="Expected and computed response differ!"
        )

    def test_get_arduino_version_unavailable(self):
        """
        Test the function that gets the arduino firmware version,
        when the Arduino times out.
        """
        ser = Mock()
        ser.readline = Mock(return_value=b"")
        value_computed = at.get_arduino_firmware_version(ser)
        value_expected = "No Arduino firmware version could be retrieved."
        self.assertEqual(
            value_expected, value_computed, msg="Expected and computed response differ!"
        )

    def test_get_serial_object_to_arduino(self):
        """
        Test the function that initializes an arduino port
        and returns a Serial object through which one
        can interact with it.
        """
        with patch("serial.Serial") as mock_serial:
            ser = Mock()
            ser.reset_input_buffer = Mock(return_value=b"")
            mock_serial.return_value = ser
            value_computed = at.get_serial_object_to_arduino("dummyport")
            value_expected = ser
        self.assertEqual(
            value_expected, value_computed, msg="Expected and computed response differ!"
        )


if __name__ == "__main__":
    unittest.main()
