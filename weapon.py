from exceptions import NoAmmunitionError


class Weapon:
    def __init__(self, ammunitions: int, range: int):
        self._ammunitions = ammunitions
        self._range = range

    def fire_at(self, x, y, z):
        if self._ammunitions == 0:
            raise NoAmmunitionError("Vous n'avez plus de munitions !")

        self.check_target_position(x, y, z)

        self._ammunitions = self._ammunitions - 1

    def get_ammunitions(self):
        return self._ammunitions

    def get_range(self):
        return self._range

    def check_target_position(self, x, y, z):
        raise NotImplementedError()
