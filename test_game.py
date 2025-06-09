import unittest
import game # The module we're testing

class TestGameLogic(unittest.TestCase):

    def test_roll_dice(self):
        """Test that roll_dice returns the correct format and values."""
        rolls = game.roll_dice()
        self.assertEqual(len(rolls), 6)  # Expecting 6 dice
        for color in game.DICE_COLORS:
            self.assertIn(color, rolls)
            self.assertIsInstance(rolls[color], int)
            self.assertTrue(1 <= rolls[color] <= 6)

    def test_choose_die_valid(self):
        """Test choosing a valid die."""
        available = {"blue": 4, "green": 5, "yellow": 1}
        chosen_this_round = {}
        # Choose blue die
        value, message = game.choose_die(available, chosen_this_round, "blue")
        self.assertEqual(value, 4)
        self.assertNotIn("blue", available)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)
        self.assertIn("You chose the Blue die with value 4", message)

    def test_choose_die_invalid_color(self):
        """Test choosing a die color that doesn't exist."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        value, message = game.choose_die(available, chosen_this_round, "red")
        self.assertIsNone(value)
        self.assertEqual(len(available), 2) # Should not change
        self.assertEqual(len(chosen_this_round), 0) # Should not change
        self.assertIn("Invalid dice color", message)

    def test_choose_die_unavailable(self):
        """Test choosing a die that is not in the available set."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        value, message = game.choose_die(available, chosen_this_round, "yellow")
        self.assertIsNone(value)
        self.assertEqual(len(available), 2) # Should not change
        self.assertEqual(len(chosen_this_round), 0) # Should not change
        self.assertIn("Yellow die is not available to choose", message)

    def test_choose_die_case_insensitivity(self):
        """Test that choosing a die is case-insensitive for the color."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        value, message = game.choose_die(available, chosen_this_round, "BlUe")
        self.assertEqual(value, 4)
        self.assertNotIn("blue", available)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)

    def test_reset_dice_conceptual(self):
        """Test the conceptual reset_dice function."""
        # This test is more about ensuring the function exists and returns expected message,
        # as the actual state is managed by the bot.
        message = game.reset_dice()
        self.assertIn("Dice state reset", message)

if __name__ == '__main__':
    unittest.main()
