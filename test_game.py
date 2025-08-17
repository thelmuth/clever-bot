import unittest
import game

class TestGameLogic(unittest.TestCase):

    def setUp(self):
        """Set up a new GameData instance for each test."""
        self.game_data = game.GameData()

    def test_initial_state(self):
        """Test that a new GameData instance has empty dice sets."""
        self.assertEqual(self.game_data.available_dice, {})
        self.assertEqual(self.game_data.chosen_dice_this_round, {})
        self.assertEqual(self.game_data.discarded_dice_this_round, {})

    def test_roll_dice(self):
        """Test that roll_dice populates available_dice and clears others."""
        rolls = self.game_data.roll_dice()
        self.assertEqual(len(rolls), 6)
        self.assertEqual(len(self.game_data.available_dice), 6)
        self.assertEqual(self.game_data.chosen_dice_this_round, {})
        self.assertEqual(self.game_data.discarded_dice_this_round, {})
        for color in game.DICE_COLORS:
            self.assertIn(color, rolls)
            self.assertTrue(1 <= rolls[color] <= 6)

    def test_reroll_available_dice(self):
        """Test that reroll_available_dice only rerolls available dice."""
        self.game_data.available_dice = {"blue": 1, "green": 2}
        self.game_data.chosen_dice_this_round = {"yellow": 6}
        self.game_data.discarded_dice_this_round = {"orange": 3}

        rerolled = self.game_data.reroll_available_dice()

        self.assertEqual(len(rerolled), 2)
        self.assertIn("blue", rerolled)
        self.assertIn("green", rerolled)
        self.assertEqual(self.game_data.chosen_dice_this_round, {"yellow": 6}) # Should not change
        self.assertEqual(self.game_data.discarded_dice_this_round, {"orange": 3}) # Should not change

    def test_choose_die_valid(self):
        """Test choosing a valid die where no other dice should be discarded."""
        self.game_data.available_dice = {"blue": 4, "green": 5, "yellow": 5}

        value, message = self.game_data.choose_die("blue")

        self.assertEqual(value, 4)
        self.assertNotIn("blue", self.game_data.available_dice)
        self.assertIn("blue", self.game_data.chosen_dice_this_round)
        self.assertEqual(self.game_data.chosen_dice_this_round["blue"], 4)
        # With the updated values, no dice should be discarded.
        self.assertEqual(len(self.game_data.discarded_dice_this_round), 0)
        self.assertIn("You chose the Blue die with value 4", message)
        self.assertNotIn("Discarded", message)

    def test_choose_die_invalid_color(self):
        """Test choosing a die color that doesn't exist."""
        self.game_data.available_dice = {"blue": 4, "green": 5}

        value, message = self.game_data.choose_die("red")

        self.assertIsNone(value)
        self.assertEqual(len(self.game_data.available_dice), 2)
        self.assertEqual(len(self.game_data.chosen_dice_this_round), 0)
        self.assertIn("Invalid dice color", message)

    def test_choose_die_unavailable(self):
        """Test choosing a die that is not in the available set."""
        self.game_data.available_dice = {"blue": 4, "green": 5}

        value, message = self.game_data.choose_die("yellow")

        self.assertIsNone(value)
        self.assertIn("Yellow die is not available", message)

    def test_choose_die_case_insensitivity(self):
        """Test that choosing a die is case-insensitive."""
        self.game_data.available_dice = {"blue": 4, "green": 5}

        value, message = self.game_data.choose_die("BlUe")

        self.assertEqual(value, 4)
        self.assertNotIn("blue", self.game_data.available_dice)
        self.assertIn("blue", self.game_data.chosen_dice_this_round)

    def test_choose_die_clever_discard_rule(self):
        """Test the 'Clever' discard rule."""
        self.game_data.available_dice = {"blue": 6, "green": 2, "yellow": 3, "white": 5, "purple": 2}

        value, message = self.game_data.choose_die("blue")

        self.assertEqual(value, 6)
        self.assertIn("blue", self.game_data.chosen_dice_this_round)
        self.assertEqual(len(self.game_data.available_dice), 0)
        self.assertEqual(len(self.game_data.discarded_dice_this_round), 4)
        self.assertIn("green", self.game_data.discarded_dice_this_round)
        self.assertIn("Discarded due to being lower", message)

    def test_choose_die_already_chosen(self):
        """Test choosing a die that has already been chosen."""
        self.game_data.available_dice = {"green": 5}
        self.game_data.chosen_dice_this_round = {"blue": 4}

        value, message = self.game_data.choose_die("blue")

        self.assertIsNone(value)
        self.assertIn("Blue die has already been chosen", message)

    def test_choose_die_already_discarded(self):
        """Test choosing a die that has already been discarded."""
        self.game_data.available_dice = {"green": 5}
        self.game_data.discarded_dice_this_round = {"blue": 2}

        value, message = self.game_data.choose_die("blue")

        self.assertIsNone(value)
        self.assertIn("Blue die has already been discarded", message)

    def test_reset(self):
        """Test the reset method."""
        self.game_data.available_dice = {"blue": 1}
        self.game_data.chosen_dice_this_round = {"green": 2}
        self.game_data.discarded_dice_this_round = {"yellow": 3}

        message = self.game_data.reset()

        self.assertEqual(self.game_data.available_dice, {})
        self.assertEqual(self.game_data.chosen_dice_this_round, {})
        self.assertEqual(self.game_data.discarded_dice_this_round, {})
        self.assertIn("Dice state reset", message)

if __name__ == '__main__':
    unittest.main()
