from unittest import TestCase

from exceptions import OutOfRangeError
from aircraft import Aircraft


class Testaircraft(TestCase):
    def test_go_to_success(self):
        # Arrange
        aircraft = Aircraft(0, 0, 0)

        # Act
        aircraft.go_to(1, 1, 1)

        # Assert
        self.assertEqual((1, 1, 1), aircraft.get_coordinates())

    def test_go_to_raise_error(self):
        # Arrange
        aircraft = Aircraft(0, 0, 0)

        # Act
        with self.assertRaises(ValueError) as error_context:
            aircraft.go_to(1, 1, 0)

        # Assert
        self.assertEqual("Coordonnées de déplacement invalides !",
                         str(error_context.exception))

    def test_fire_at_success(self):
        # Arrange
        aircraft = Aircraft(0, 0, 0)

        # Act
        aircraft.fire_at(1, 1, 0)

        # Assert
        self.assertEqual(39, aircraft.get_weapon().get_ammunitions())

    def test_fire_at_raise_error_when_target_out_of_range(self):
        # Arrange
        aircraft = Aircraft(0, 0, 0)

        # Act
        with self.assertRaises(OutOfRangeError) as error_context:
            aircraft.fire_at(60, 60, 1)

        # Assert
        self.assertEqual("La cible est hors de portée!",
                         str(error_context.exception))
