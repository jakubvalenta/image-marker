import unittest

from image_marker.rect import Rectangle


class TestRect(unittest.TestCase):

    def test_shift(self):
        rect = Rectangle(10, 20, 80, 50)
        rect.shift(-10, -20)
        self.assertEqual(rect.x, 0)
        self.assertEqual(rect.y, 0)

    def test_from_top(self):
        rect = Rectangle(10, 20, 80, 50)
        rect.from_top(100)
        self.assertEqual(rect.x, 10)
        self.assertEqual(rect.y, 30)
