# SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Daniel Carron <daniel.carron@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
from pytwister import Twister


class TestTwister(unittest.TestCase):
    """
    A test class for the Twister functions
    """

    @classmethod
    def setUpClass(cls):
        cls.twister = Twister(dummy=True)

    def assert_angle(self, expected_angle, current_angle):
        self.assertEqual(
            current_angle,
            expected_angle,
            msg=f"Expected angle to be {expected_angle}, got {current_angle} instead",
        )

    def test_zero(self):
        self.twister.zero()
        self.assertEqual(
            self.twister.angle,
            0,
            msg=f"Twister angle has not been reset to 0, got {self.twister.angle} instead.",
        )

    def test_rotate_rel(self):
        self.twister.zero()

        self.assert_angle(90, self.twister.rotate_rel(90))
        self.assert_angle(-90, self.twister.rotate_rel(-180))
        self.assert_angle(360, self.twister.rotate_rel(450))

    def test_rotate_abs(self):
        self.assert_angle(90, self.twister.rotate_abs(90))
        self.assert_angle(-180, self.twister.rotate_abs(-180))
        self.assert_angle(360, self.twister.rotate_abs(360))
        self.assert_angle(0, self.twister.rotate_abs(0))


if __name__ == "__main__":
    unittest.main()
