import random

DICE_COLORS = ["blue", "green", "orange", "purple", "yellow", "white"]
# Keep track of all dice chosen in a round, and which dice are currently available from the last roll.
# These will be managed by the bot, this file just provides functions to manipulate them.

def roll_dice():
    """Rolls all six dice for That's Pretty Clever."""
    rolls = {color: random.randint(1, 6) for color in DICE_COLORS}
    return rolls

def choose_die(available_dice, chosen_dice_this_round, color_to_choose):
    """
    Allows a player to choose a die.
    Modifies available_dice and chosen_dice_this_round in place.
    Returns the value of the chosen die, or None if invalid.
    """
    color_to_choose = color_to_choose.lower()
    if color_to_choose not in DICE_COLORS:
        return None, "Invalid dice color."

    if color_to_choose not in available_dice:
        return None, f"{color_to_choose.capitalize()} die is not available to choose."

    chosen_value = available_dice.pop(color_to_choose)
    chosen_dice_this_round[color_to_choose] = chosen_value

    # In "That's Pretty Clever", when a die is chosen, any dice with a lower value are discarded.
    # For simplicity in this step, we'll just remove the chosen die.
    # The full discard logic can be added later if desired.

    return chosen_value, f"You chose the {color_to_choose.capitalize()} die with value {chosen_value}."

# Example usage (can be removed later):
if __name__ == '__main__':
    current_roll = roll_dice()
    print("Initial roll:", current_roll)
    available_from_roll = dict(current_roll) # Make a copy
    chosen_this_round = {}

    value, msg = choose_die(available_from_roll, chosen_this_round, "blue")
    print(msg)
    print("Available after choosing blue:", available_from_roll)
    print("Chosen this round:", chosen_this_round)

    value, msg = choose_die(available_from_roll, chosen_this_round, "yellow")
    print(msg)
    print("Available after choosing yellow:", available_from_roll)
    print("Chosen this round:", chosen_this_round)

    value, msg = choose_die(available_from_roll, chosen_this_round, "red") # Invalid color
    print(msg)

def reset_dice():
    """Resets the dice state for a new round (conceptually).
    Actual state is managed by the bot instance for now.
    Returns a confirmation message.
    """
    # In a more complex game state model, this would clear dice from a game object.
    # For now, the bot will handle clearing its own state.
    return "Dice state reset. Ready for a new roll or setup."
