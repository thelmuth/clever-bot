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

    def test_choose_die_clever_discard_rule(self):
        """Test the 'Clever' discard rule: lower value dice are removed."""
        available = {"blue": 6, "green": 2, "yellow": 3, "white": 5, "purple": 2}
        chosen_this_round = {}

        # Choose blue die (value 6). Green (2), Yellow (3), White (5), Purple (2) should be discarded.
        value, message, discarded_info = game.choose_die(available, chosen_this_round, "blue")

        self.assertEqual(value, 6)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 6)

        # Check that only blue was chosen, and all others were discarded as they are less than 6
        self.assertEqual(len(available), 0) # All other dice should have been discarded

        self.assertEqual(len(discarded_info), 4) # Green, Yellow, White, Purple
        # Check for presence of discarded dice info (order doesn't strictly matter for the list itself)
        self.assertIn("Green: 2", discarded_info)
        self.assertIn("Yellow: 3", discarded_info)
        self.assertIn("White: 5", discarded_info)
        self.assertIn("Purple: 2", discarded_info)

    def test_choose_die_clever_discard_rule_no_discard(self):
        """Test discard rule when no dice have lower values."""
        available = {"blue": 1, "green": 5, "yellow": 3}
        chosen_this_round = {}

        # Choose blue die (value 1). No other dice should be discarded.
        value, message, discarded_info = game.choose_die(available, chosen_this_round, "blue")

        self.assertEqual(value, 1)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 1)

        self.assertEqual(len(available), 2) # Green and Yellow should remain
        self.assertIn("green", available)
        self.assertIn("yellow", available)
        self.assertEqual(len(discarded_info), 0) # No dice should have been discarded by the rule

    def test_choose_die_clever_discard_rule_some_discard(self):
        """Test discard rule when some dice have lower values, some higher/equal."""
        available = {"blue": 4, "green": 2, "yellow": 5, "white": 4, "purple": 1}
        chosen_this_round = {}

        # Choose blue die (value 4). Green (2) and Purple (1) should be discarded.
        # Yellow (5) and White (4) should remain.
        value, message, discarded_info = game.choose_die(available, chosen_this_round, "blue")

        self.assertEqual(value, 4)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)

        self.assertEqual(len(available), 2) # Yellow and White should remain
        self.assertIn("yellow", available)
        self.assertIn("white", available)

        self.assertEqual(len(discarded_info), 2) # Green and Purple discarded
        self.assertIn("Green: 2", discarded_info)
        self.assertIn("Purple: 1", discarded_info)

    def test_choose_die_already_empty_available(self):
        """Test choosing when available_dice is already empty (e.g., after previous discards)."""
        available = {} # No dice available
        chosen_this_round = {"blue": 6} # A die was chosen previously

        value, message, discarded_info = game.choose_die(available, chosen_this_round, "green")

        self.assertIsNone(value)
        self.assertIn("Green die is not available", message)
        self.assertEqual(len(discarded_info), 0)

if __name__ == '__main__':
    unittest.main()
