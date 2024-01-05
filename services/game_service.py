from typing import Optional

from dao.game_dao import GameDao, VesselTypes
from model.battlefield import Battlefield
from model.cruiser import Cruiser
from model.destroyer import Destroyer
from model.exceptions import GameNotFoundError
from model.frigate import Frigate
from model.game import Game
from model.player import Player
from model.submarine import Submarine
from model.vessel import Vessel


class GameStatus:
    GAGNE = "GAGNE"
    PERDU = "PERDU"
    ENCOURS = "ENCOURS"


def get_players(game, player_name) \
        -> tuple[Optional[Player], Optional[Player]]:
    shooter: Optional[Player] = None
    targeted: Optional[Player] = None
    for player in game.players:
        if player.name == player_name:
            shooter = player
        else:
            targeted = player
    return shooter, targeted


def create_vessel(vessel_type: str, x: int, y: int, z: int) -> Vessel:
    vessel: Optional[Vessel] = None
    match vessel_type:
        case VesselTypes.CRUISER:
            vessel = Cruiser(x, y, z)
        case VesselTypes.FRIGATE:
            vessel = Frigate(x, y, z)
        case VesselTypes.SUBMARINE:
            vessel = Submarine(x, y, z)
        case VesselTypes.DESTROYER:
            vessel = Destroyer(x, y, z)
    return vessel


def get_player_status(player: Player) -> str:
    vessels = player.battle_field.get_vessels()
    hits = 0
    ammunitions = 0
    for vessel in vessels:
        hits += vessel.get_hits()
        ammunitions += vessel.get_weapon().get_ammunitions()

    if hits == 0 or ammunitions == 0:
        return GameStatus.PERDU

    return GameStatus.ENCOURS


class GameService:

    def __init__(self):
        self.game_dao = GameDao()

    def create_game(self, player_name: str, min_x: int, max_x: int, min_y: int,
                    max_y: int, min_z: int, max_z: int) -> int:
        game = Game()
        battle_field = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z)
        game.add_player(Player(player_name, battle_field))
        return self.game_dao.create_game(game)

    def join_game(self, game_id: int, player_name: str) -> bool:
        game = self.game_dao.find_game(game_id)
        if game is None:
            raise GameNotFoundError("Cette partie n'existe pas !")
        battle_field = Battlefield(
            *game.get_players()[0].get_battlefield().get_battlefield_space())
        player = Player(player_name, battle_field)
        game.add_player(player)
        return self.game_dao.create_or_update_player(game_id, player)

    def get_game(self, game_id: int) -> Game:
        return self.game_dao.find_game(game_id)

    def add_vessel(self, game_id: int, player_name: str, vessel_type: str,
                   x: int, y: int, z: int) -> bool:
        game = self.game_dao.find_game(game_id)
        if game is None:
            raise GameNotFoundError("Cette partie n'existe pas !")
        shooter, targeted = get_players(game, player_name)
        if shooter is None:
            raise ValueError("Le joueur n'existe pas!")
        vessel = create_vessel(vessel_type, x, y, z)
        shooter.battle_field.add_vessel(vessel)
        return self.game_dao.create_or_update_vessel(shooter, vessel)

    def shoot_at(self, game_id: int, shooter_name: str, vessel_id: int, x: int,
                 y: int, z: int) -> bool:
        game = self.game_dao.find_game(game_id)
        if game is None:
            raise GameNotFoundError("Cette partie n'existe pas !")
        shooter, targeted = get_players(game, shooter_name)
        if targeted is None:
            raise ValueError(
                "Il n'y a qu'un seul joueur!\n "
                "Invitez un second joueur en lui envoyant l'id de partie!")
        shooter_vessel = shooter.get_battlefield().get_vessel_by_id(vessel_id)
        shooter_vessel.fire_at(x, y, z)
        fired = targeted.get_battlefield().fired_at(x, y, z)
        targeted_updated = False
        shooter_updated = self.game_dao \
            .create_or_update_vessel(shooter, shooter_vessel)
        if fired:
            targeted_vessel = targeted.get_battlefield() \
                .get_vessel_by_coordinates(x, y, z)
            targeted_updated = self.game_dao \
                .create_or_update_vessel(targeted, targeted_vessel)
        return shooter_updated and targeted_updated

    def get_player(self, game_id: int, player_name: str) -> Optional[Player]:
        game = self.game_dao.find_game(game_id)
        shooter, targeted = get_players(game, player_name)
        return shooter

    def get_game_status(self, game_id: int, shooter_name: str) -> str:
        game = self.game_dao.find_game(game_id)
        if game is None:
            raise GameNotFoundError("Cette partie n'existe pas !")
        shooter, targeted = get_players(game, shooter_name)
        targeted_status = get_player_status(targeted)
        shooter_status = get_player_status(shooter)
        if targeted_status == GameStatus.PERDU:
            return GameStatus.GAGNE
        if shooter_status == GameStatus.PERDU:
            return GameStatus.PERDU
        return GameStatus.ENCOURS
