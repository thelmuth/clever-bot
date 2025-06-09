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

    # --- Update existing choose_die tests ---

    def test_choose_die_valid(self):
        """Test choosing a valid die without triggering discard rule for this test."""
        available = {"blue": 4, "green": 5, "yellow": 1}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue") # Updated call

        self.assertEqual(value, 4)
        self.assertNotIn("blue", available)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)
        self.assertEqual(len(discarded_this_round), 0) # No discards by rule here
        self.assertIn("You chose the Blue die with value 4", message)
        self.assertNotIn("Discarded due to being lower", message) # Ensure no discard message part

    def test_choose_die_invalid_color(self):
        """Test choosing a die color that doesn't exist."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "red") # Updated call

        self.assertIsNone(value)
        self.assertEqual(len(available), 2)
        self.assertEqual(len(chosen_this_round), 0)
        self.assertEqual(len(discarded_this_round), 0)
        self.assertIn("Invalid dice color", message)

    def test_choose_die_unavailable(self):
        """Test choosing a die that is not in the available set."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "yellow") # Updated call

        self.assertIsNone(value)
        self.assertIn("Yellow die is not available", message)
        self.assertEqual(len(discarded_this_round), 0)


    def test_choose_die_case_insensitivity(self):
        """Test that choosing a die is case-insensitive for the color."""
        available = {"blue": 4, "green": 5}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "BlUe") # Updated call

        self.assertEqual(value, 4)
        self.assertNotIn("blue", available)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)
        self.assertEqual(len(discarded_this_round), 0)
        self.assertIn("You chose the Blue die with value 4", message)
        self.assertNotIn("Discarded due to being lower", message)

    # --- Update tests for "Clever" discard rule ---
    def test_choose_die_clever_discard_rule(self):
        """Test the 'Clever' discard rule: lower value dice are removed."""
        available = {"blue": 6, "green": 2, "yellow": 3, "white": 5, "purple": 2}
        chosen_this_round = {}
        discarded_this_round = {} # New: This will be populated

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue") # Updated call

        self.assertEqual(value, 6)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 6)

        self.assertEqual(len(available), 0) # All other dice should have been discarded from available

        # Check discarded_this_round dictionary
        self.assertEqual(len(discarded_this_round), 4)
        self.assertEqual(discarded_this_round.get("green"), 2)
        self.assertEqual(discarded_this_round.get("yellow"), 3)
        self.assertEqual(discarded_this_round.get("white"), 5)
        self.assertEqual(discarded_this_round.get("purple"), 2)

        # Check message content
        self.assertIn("You chose the Blue die with value 6.", message)
        self.assertIn("Discarded due to being lower", message)
        self.assertIn("Green: 2", message) # Check specific dice in message
        self.assertIn("Yellow: 3", message)
        self.assertIn("White: 5", message)
        self.assertIn("Purple: 2", message)


    def test_choose_die_clever_discard_rule_no_discard(self):
        """Test discard rule when no dice have lower values."""
        available = {"blue": 1, "green": 5, "yellow": 3}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue") # Updated call

        self.assertEqual(value, 1)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 1)

        self.assertEqual(len(available), 2)
        self.assertIn("green", available)
        self.assertIn("yellow", available)
        self.assertEqual(len(discarded_this_round), 0) # No dice discarded by rule
        self.assertNotIn("Discarded due to being lower", message)

    def test_choose_die_clever_discard_rule_some_discard(self):
        """Test discard rule when some dice have lower values, some higher/equal."""
        available = {"blue": 4, "green": 2, "yellow": 5, "white": 4, "purple": 1}
        chosen_this_round = {}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue") # Updated call

        self.assertEqual(value, 4)
        self.assertIn("blue", chosen_this_round)
        self.assertEqual(chosen_this_round["blue"], 4)

        self.assertEqual(len(available), 2)
        self.assertIn("yellow", available)
        self.assertIn("white", available)

        self.assertEqual(len(discarded_this_round), 2) # Green and Purple discarded
        self.assertEqual(discarded_this_round.get("green"), 2)
        self.assertEqual(discarded_this_round.get("purple"), 1)
        self.assertIn("Discarded due to being lower", message)
        self.assertIn("Green: 2", message)
        self.assertIn("Purple: 1", message)

    def test_choose_die_already_empty_available(self):
        """Test choosing when available_dice is already empty."""
        available = {}
        chosen_this_round = {"blue": 6}
        discarded_this_round = {} # New

        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "green") # Updated call

        self.assertIsNone(value)
        self.assertIn("Green die is not available", message)
        self.assertEqual(len(discarded_this_round), 0)

    def test_choose_die_already_chosen(self):
        """Test choosing a die that has already been chosen this round."""
        available = {"green": 5}
        chosen_this_round = {"blue": 4}
        discarded_this_round = {}
        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue")
        self.assertIsNone(value)
        self.assertIn("Blue die has already been chosen this round", message)

    def test_choose_die_already_discarded(self):
        """Test choosing a die that has already been discarded this round by the rule."""
        available = {"green": 5}
        chosen_this_round = {}
        discarded_this_round = {"blue": 2} # Blue was discarded by rule previously
        value, message = game.choose_die(available, chosen_this_round, discarded_this_round, "blue")
        self.assertIsNone(value)
        self.assertIn("Blue die has already been discarded this round", message)

    def test_reset_dice_conceptual(self):
        """Test the conceptual reset_dice function."""
        message = game.reset_dice()
        self.assertIn("Dice state reset", message)

if __name__ == '__main__':
    unittest.main()
