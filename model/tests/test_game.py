from unittest import TestCase

from model.game import Game
from model.exceptions import GameFullError
from model.battlefield import Battlefield
from model.player import Player


class TestGame(TestCase):

    def test_create_game_add_2_players_success(self):
        # Arrange
        game = Game("id")
        battlefield = Battlefield(0, 100, 0, 100, -1, 1)

        # Act
        game_id = game.get_id()
        game.add_player(Player("Rodge", battlefield))
        game.add_player(Player("Jaka", battlefield))

        # Assert
        self.assertIsNotNone(game_id)
        self.assertEqual("Rodge", game.get_players()[0].get_name())
        self.assertEqual("Jaka", game.get_players()[1].get_name())

    def test_create_game_add_3_players_error(self):
        # Arrange
        game = Game()
        battlefield = Battlefield(0, 100, 0, 100, -1, 1)
        game.add_player(Player("Rodge", battlefield))
        game.add_player(Player("Jaka", battlefield))

        # Act
        with self.assertRaises(GameFullError) as error_context:
            game.add_player(Player("Lutz", battlefield))

        # Assert
        self.assertEqual("Seulement 2 joueurs sont admis dans la partie !",
                         str(error_context.exception))
