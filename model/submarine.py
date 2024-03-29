from model.torpedos_launcher import TorpedoLauncher
from model.vessel import Vessel


class Submarine(Vessel):

    def __init__(self, x: float, y: float, z: float):
        if z > 0:
            raise ValueError("Coordonnées de placement invalides !")
        super().__init__(x, y, z, 2, TorpedoLauncher())

    def go_to(self, x, y, z):
        if z > 0:
            raise ValueError("Coordonnées de déplacement invalides !")
        self.coordinates = (x, y, z)
