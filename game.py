import random

DICE_COLORS = ["blue", "green", "orange", "purple", "yellow", "white"]

class GameData:
    """Holds all data for a single game of That's Pretty Clever."""
    def __init__(self):
        self.available_dice = {}
        self.chosen_dice_this_round = {}
        self.discarded_dice_this_round = {}

    def roll_dice(self):
        """Rolls all six dice for That's Pretty Clever."""
        self.available_dice = {color: random.randint(1, 6) for color in DICE_COLORS}
        self.chosen_dice_this_round = {}
        self.discarded_dice_this_round = {}
        return self.available_dice

    def reroll_available_dice(self):
        """Rerolls only the dice currently in available_dice."""
        for color in self.available_dice:
            self.available_dice[color] = random.randint(1, 6)
        return self.available_dice

    def choose_die(self, color_to_choose):
        """
        Allows a player to choose a die. Implements the "Clever" discard rule.
        Dice discarded by the rule are moved from available_dice to discarded_dice_this_round.
        Returns:
            - chosen_value (int): The value of the chosen die, or None if invalid choice.
            - message (str): A message describing the outcome (e.g., die chosen, error).
        """
        color_to_choose = color_to_choose.lower()
        if color_to_choose not in DICE_COLORS:
            return None, "Invalid dice color. Please choose from Blue, Green, Orange, Purple, Yellow, White."

        if color_to_choose not in self.available_dice:
            # Check if it was already chosen or discarded this round
            if color_to_choose in self.chosen_dice_this_round:
                return None, f"{color_to_choose.capitalize()} die has already been chosen this round."
            elif color_to_choose in self.discarded_dice_this_round:
                return None, f"{color_to_choose.capitalize()} die has already been discarded this round."
            else:
                return None, f"{color_to_choose.capitalize()} die is not available to choose."

        chosen_value = self.available_dice.pop(color_to_choose)
        self.chosen_dice_this_round[color_to_choose] = chosen_value

        message = f"You chose the {color_to_choose.capitalize()} die with value {chosen_value}."

        # "Clever" discard rule:
        dice_to_discard_due_to_rule = []
        for color, value in list(self.available_dice.items()):
            if value < chosen_value:
                dice_to_discard_due_to_rule.append(color)

        if dice_to_discard_due_to_rule:
            discard_details = []
            for color_d in dice_to_discard_due_to_rule:
                discarded_value = self.available_dice.pop(color_d)
                self.discarded_dice_this_round[color_d] = discarded_value
                discard_details.append(f"{color_d.capitalize()}: {discarded_value}")
            message += "\nDiscarded due to being lower than chosen: " + ", ".join(discard_details) + "."

        return chosen_value, message

    def reset(self):
        """Resets the dice state for a new round."""
        self.available_dice = {}
        self.chosen_dice_this_round = {}
        self.discarded_dice_this_round = {}
        return "Dice state reset. Ready for a new roll or setup."

# Example usage (can be removed later):
# This part is important for direct testing of game.py
if __name__ == '__main__':
    # Instantiate a game
    game_instance = GameData()

    # Initial roll
    initial_roll = game_instance.roll_dice()
    print("Initial roll:", initial_roll)
    print("Available after roll:", game_instance.available_dice)

    # --- Test choosing a die ---
    # Example: Choose blue die
    if 'blue' in game_instance.available_dice:
        print("\nChoosing Blue die...")
        chosen_val, msg = game_instance.choose_die("blue")
        print(msg)
        print("Available after choosing blue:", game_instance.available_dice)
        print("Chosen this round:", game_instance.chosen_dice_this_round)
        print("Discarded this round:", game_instance.discarded_dice_this_round)
    else:
        print("\nBlue die not in the initial roll for this example.")

    # --- Test re-rolling available dice ---
    print("\nRe-rolling available dice...")
    rerolled_dice = game_instance.reroll_available_dice()
    print("Re-rolled available dice:", rerolled_dice)
    print("Chosen dice remain:", game_instance.chosen_dice_this_round) # Should not be empty if blue was chosen
    print("Discarded dice remain:", game_instance.discarded_dice_this_round)


    # --- Test choosing another die after re-roll ---
    if game_instance.available_dice:
        # Choose the first available die to demonstrate
        some_color = list(game_instance.available_dice.keys())[0]
        print(f"\nChoosing {some_color.capitalize()} die after re-roll...")
        chosen_val, msg = game_instance.choose_die(some_color)
        print(msg)
        print("Available after second choice:", game_instance.available_dice)
        print("Chosen this round:", game_instance.chosen_dice_this_round)
        print("Discarded this round:", game_instance.discarded_dice_this_round)

    # --- Test reset ---
    print("\nResetting the game...")
    reset_msg = game_instance.reset()
    print(reset_msg)
    print("Available dice after reset:", game_instance.available_dice)
    print("Chosen dice after reset:", game_instance.chosen_dice_this_round)
    print("Discarded dice after reset:", game_instance.discarded_dice_this_round)
