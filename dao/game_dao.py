from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \
    select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from model.air_missile_launcher import AirMissileLauncher
from model.battlefield import Battlefield
from model.cruiser import Cruiser
from model.destroyer import Destroyer
from model.frigate import Frigate
from model.game import Game
from model.player import Player
from model.submarine import Submarine
from model.surface_missile_launcher import SurfaceMissileLauncher
from model.torpedos_launcher import TorpedoLauncher
from model.vessel import Vessel
from model.weapon import Weapon

engine = create_engine('sqlite:////tmp/tdlog.db', echo=True,
                       future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class GameDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()

    def create_game(self, game: Game) -> int:
        game_entity = map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id

    def find_game(self, game_id: int) -> Game:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return map_to_game(game_entity)

    def create_or_update_player(self, game_id: int, player: Player) -> bool:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        for player_entity in game_entity.players:
            if player_entity.name == player.name:
                game_entity.players.remove(player_entity)
                break
        game_entity.players.append(map_to_player_entity(player))
        self.db_session.flush()
        self.db_session.commit()
        return True

    def create_or_update_vessel(self, player: Player, vessel: Vessel) -> bool:
        stmt_find_player = select(PlayerEntity).where(
            PlayerEntity.id == player.id)
        player_entity = self.db_session.scalars(stmt_find_player).one()
        vessel_entity_updated = map_to_vessel_entity(
            player.get_battlefield().id, vessel)

        for vessel_entity in player_entity.battle_field.vessels:
            if vessel_entity.id == vessel_entity_updated.id:
                player_entity.battle_field.vessels.remove(vessel_entity)
                break
        player_entity.battle_field.vessels.append(vessel_entity_updated)

        self.db_session.flush()
        self.db_session.commit()
        return True


class GameEntity(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship("PlayerEntity", back_populates="game",
                           cascade="all, delete-orphan")


class PlayerEntity(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("GameEntity", back_populates="players")
    battle_field = relationship("BattlefieldEntity", back_populates="player",
                                uselist=False, cascade="all, delete-orphan")


class BattlefieldEntity(Base):
    __tablename__ = 'battlefield'
    id = Column(Integer, primary_key=True)
    min_x = Column(Integer)
    min_y = Column(Integer)
    min_z = Column(Integer)
    max_x = Column(Integer)
    max_y = Column(Integer)
    max_z = Column(Integer)
    max_power = Column(Integer)
    player = relationship("PlayerEntity", back_populates="battle_field",
                          uselist=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    vessels = relationship("VesselEntity", back_populates="battle_field",
                           cascade="all, delete-orphan")


class VesselEntity(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True)
    coord_x = Column(Integer)
    coord_y = Column(Integer)
    coord_z = Column(Integer)
    hits_to_be_destroyed = Column(Integer)
    type = Column(String)
    battle_field = relationship("BattlefieldEntity", back_populates="vessels")
    battle_field_id = Column(Integer, ForeignKey("battlefield.id"),
                             nullable=False)
    weapon = relationship("WeaponEntity", back_populates="vessel",
                          uselist=False, cascade="all, delete-orphan")


class WeaponEntity(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    ammunitions = Column(Integer)
    range = Column(Integer)
    type = Column(String)
    vessel = relationship("VesselEntity", back_populates="weapon")
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=False)


class VesselTypes:
    CRUISER = "Cruiser"
    DESTROYER = "Destroyer"
    FRIGATE = "Frigate"
    SUBMARINE = "Submarine"


class WeaponTypes:
    AIRMISSILELAUNCHER = "AirMissileLauncher"
    SURFACEMISSILELAUNCHER = "SurfaceMissileLauncher"
    TORPEDOLAUNCHER = "TorpedoLauncher"


def map_to_game(game_entity: GameEntity) -> Optional[Game]:
    if game_entity is None:
        return None
    game = Game()
    game.id = game_entity.id
    for player_entity in game_entity.players:
        battle_field = Battlefield(player_entity.battle_field.min_x,
                                   player_entity.battle_field.max_x,
                                   player_entity.battle_field.min_y,
                                   player_entity.battle_field.max_y,
                                   player_entity.battle_field.min_z,
                                   player_entity.battle_field.max_z,
                                   player_entity.battle_field.max_power)
        battle_field.id = player_entity.battle_field.id
        battle_field.vessels = map_to_vessels(
            player_entity.battle_field.vessels)
        player = Player(player_entity.name, battle_field)
        player.id = player_entity.id
        game.add_player(player)
    return game


def map_to_vessels(vessel_entities: list[VesselEntity]) -> list[Vessel]:
    vessels: list[Vessel] = []
    for vessel_entity in vessel_entities:
        weapon = map_to_weapon(vessel_entity.weapon)
        vessel = map_to_vessel(vessel_entity, weapon)
        vessels.append(vessel)
    return vessels


def map_to_vessel(vessel_entity, weapon) -> Optional[Vessel]:
    vessel = None
    match vessel_entity.type:
        case VesselTypes.CRUISER:
            vessel = Cruiser(vessel_entity.coord_x, vessel_entity.coord_y,
                             vessel_entity.coord_z)
            vessel.hits_to_be_destroyed = vessel_entity.hits_to_be_destroyed
            vessel.id = vessel_entity.id
            vessel.weapon = weapon
            return vessel
        case VesselTypes.DESTROYER:
            vessel = Destroyer(vessel_entity.coord_x, vessel_entity.coord_y,
                               vessel_entity.coord_z)
            vessel.hits_to_be_destroyed = vessel_entity.hits_to_be_destroyed
            vessel.id = vessel_entity.id
            vessel.weapon = weapon
            return vessel
        case VesselTypes.FRIGATE:
            vessel = Frigate(vessel_entity.coord_x, vessel_entity.coord_y,
                             vessel_entity.coord_z)
            vessel.hits_to_be_destroyed = vessel_entity.hits_to_be_destroyed
            vessel.id = vessel_entity.id
            vessel.weapon = weapon
            return vessel
        case VesselTypes.SUBMARINE:
            vessel = Submarine(vessel_entity.coord_x, vessel_entity.coord_y,
                               vessel_entity.coord_z)
            vessel.hits_to_be_destroyed = vessel_entity.hits_to_be_destroyed
            vessel.id = vessel_entity.id
            vessel.weapon = weapon
            return vessel
    return vessel


def map_to_weapon(weapon_entity: WeaponEntity) -> Optional[Weapon]:
    weapon = None
    match weapon_entity.type:
        case WeaponTypes.SURFACEMISSILELAUNCHER:
            weapon = SurfaceMissileLauncher()
            weapon.id = weapon_entity.id
            weapon.range = weapon_entity.range
            weapon.ammunitions = weapon_entity.ammunitions
            return weapon
        case WeaponTypes.TORPEDOLAUNCHER:
            weapon = TorpedoLauncher()
            weapon.id = weapon_entity.id
            weapon.range = weapon_entity.range
            weapon.ammunitions = weapon_entity.ammunitions
            return weapon
        case WeaponTypes.AIRMISSILELAUNCHER:
            weapon = AirMissileLauncher()
            weapon.id = weapon_entity.id
            weapon.range = weapon_entity.range
            weapon.ammunitions = weapon_entity.ammunitions
            return weapon
    return weapon


def map_to_game_entity(game: Game) -> GameEntity:
    game_entity = GameEntity()
    if game.get_id() is not None:
        game_entity.id = game.get_id()
    for player in game.get_players():
        player_entity = PlayerEntity()
        player_entity.id = player.id
        player_entity.name = player.get_name()
        battlefield_entity = map_to_battlefield_entity(
            player.get_battlefield())
        vessel_entities = \
            map_to_vessel_entities(player.get_battlefield().id,
                                   player.get_battlefield().vessels)
        battlefield_entity.vessels = vessel_entities
        player_entity.battle_field = battlefield_entity
        game_entity.players.append(player_entity)
    return game_entity


def map_to_vessel_entities(battlefield_id: int, vessels: list[Vessel]) \
        -> list[VesselEntity]:
    vessel_entities: list[VesselEntity] = []
    for vessel in vessels:
        vessel_entity = map_to_vessel_entity(battlefield_id, vessel)
        vessel_entities.append(vessel_entity)

    return vessel_entities


def map_to_vessel_entity(battlefield_id: int, vessel: Vessel) -> VesselEntity:
    vessel_entity = VesselEntity()
    weapon_entity = WeaponEntity()
    weapon_entity.id = vessel.weapon.id
    weapon_entity.ammunitions = vessel.weapon.ammunitions
    weapon_entity.range = vessel.weapon.range
    weapon_entity.type = type(vessel.weapon).__name__
    vessel_entity.id = vessel.id
    vessel_entity.weapon = weapon_entity
    vessel_entity.type = type(vessel).__name__
    vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
    vessel_entity.coord_x = vessel.coordinates[0]
    vessel_entity.coord_y = vessel.coordinates[1]
    vessel_entity.coord_z = vessel.coordinates[2]
    vessel_entity.battle_field_id = battlefield_id
    return vessel_entity


def map_to_player_entity(player: Player) -> PlayerEntity:
    player_entity = PlayerEntity()
    player_entity.id = player.id
    player_entity.name = player.name
    player_entity.battle_field = map_to_battlefield_entity(
        player.get_battlefield())
    return player_entity


def map_to_battlefield_entity(battlefield: Battlefield) -> BattlefieldEntity:
    battlefield_entity = BattlefieldEntity()
    battlefield_entity.id = battlefield.id
    battlefield_entity.max_x = battlefield.max_x
    battlefield_entity.max_y = battlefield.max_y
    battlefield_entity.max_z = battlefield.max_z
    battlefield_entity.min_x = battlefield.min_x
    battlefield_entity.min_y = battlefield.min_y
    battlefield_entity.min_z = battlefield.min_z
    battlefield_entity.max_power = battlefield.max_power
    return battlefield_entity
