# SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: François Marelli <francois.marelli@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

import typing
from . import arduino as pt


class Twister:
    """
    This class offers a high-level control of the step motor using absolute and
    relative degree commands.
    """

    def __init__(self, dummy=False):
        self.__dummy = dummy
        if not dummy:
            try:
                port_list = pt.get_comport_list()
                arduino_ports = pt.get_arduino_ports(port_list)
                twister_port = pt.scan_list_for_arduinopytwister(arduino_ports)

                self.ser = pt.get_serial_object_to_arduino(twister_port)
            except Exception as exc:
                raise RuntimeError("Could not connect to Arduino driver") from exc
        else:
            self.ser = None
            print("Warning: dummy mode activated")

        self.angle = 0
        self.__step = pt.STEP_SIZE

    def zero(self) -> None:
        """
        Sets the current angle as 0
        """

        self.angle = 0

    def __angle_to_steps(self, degrees: float) -> typing.Tuple[int, float]:
        """
        Convert degrees to motor steps.

        Parameters
        ----------
        degrees : float
            The desired angle

        Returns
        -------
        typing.Tuple[int, float]
            The corresponding number of steps, and the actual angle it generates.
        """
        steps = degrees / self.__step
        steps = int(steps)
        degrees = steps * self.__step

        return steps, degrees

    def rotate_rel(self, degrees: float) -> float:
        """
        Rotate the twister by a relative angle in degrees.

        Parameters
        ----------
        degrees : float
            The rotation angle

        Returns
        -------
        float
            The angle of the twister after rotation
        """

        steps, degrees = self.__angle_to_steps(degrees)
        if self.__dummy:
            print(f"Dummy: rotating the twister by {steps} steps")
        else:
            pt.rotate_by_steps(self.ser, steps)
        self.angle += degrees

        return self.angle

    def rotate_abs(self, degrees: float) -> float:
        """
        Rotate the twister to an absolute angle in degrees.

        Parameters
        ----------
        degrees : float
            The destination angle

        Returns
        -------
        float
            The angle of the twister after rotation
        """

        degrees = degrees - self.angle

        return self.rotate_rel(degrees)
