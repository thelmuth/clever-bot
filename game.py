import random

DICE_COLORS = ["blue", "green", "orange", "purple", "yellow", "white"]
# Keep track of all dice chosen in a round, and which dice are currently available from the last roll.
# These will be managed by the bot, this file just provides functions to manipulate them.

def roll_dice():
    """Rolls all six dice for That's Pretty Clever."""
    rolls = {color: random.randint(1, 6) for color in DICE_COLORS}
    return rolls

def choose_die(available_dice, chosen_dice_this_round, discarded_dice_this_round, color_to_choose):
    """
    Allows a player to choose a die. Implements the "Clever" discard rule.
    Dice discarded by the rule are moved from available_dice to discarded_dice_this_round.

    Modifies available_dice, chosen_dice_this_round, and discarded_dice_this_round in place.

    Returns:
        - chosen_value (int): The value of the chosen die, or None if invalid choice.
        - message (str): A message describing the outcome (e.g., die chosen, error).
    """
    color_to_choose = color_to_choose.lower()
    if color_to_choose not in DICE_COLORS:
        return None, "Invalid dice color. Please choose from Blue, Green, Orange, Purple, Yellow, White."

    if color_to_choose not in available_dice:
        # Check if it was already chosen or discarded this round
        if color_to_choose in chosen_dice_this_round:
            return None, f"{color_to_choose.capitalize()} die has already been chosen this round."
        elif color_to_choose in discarded_dice_this_round:
            return None, f"{color_to_choose.capitalize()} die has already been discarded this round."
        else:
            return None, f"{color_to_choose.capitalize()} die is not available to choose."

    chosen_value = available_dice.pop(color_to_choose)
    chosen_dice_this_round[color_to_choose] = chosen_value

    message = f"You chose the {color_to_choose.capitalize()} die with value {chosen_value}."

    # "Clever" discard rule:
    # Iterate over a copy of available_dice keys because we might modify the dictionary
    dice_to_discard_due_to_rule = []
    for color, value in list(available_dice.items()): # list() makes a copy of items
        if value < chosen_value:
            dice_to_discard_due_to_rule.append(color)

    if dice_to_discard_due_to_rule:
        discard_details = []
        for color_d in dice_to_discard_due_to_rule:
            discarded_value = available_dice.pop(color_d) # Remove from available
            discarded_dice_this_round[color_d] = discarded_value # Add to discarded
            discard_details.append(f"{color_d.capitalize()}: {discarded_value}")
        message += "\nDiscarded due to being lower than chosen: " + ", ".join(discard_details) + "."

    return chosen_value, message

# Example usage (can be removed later):
# Update the example usage in if __name__ == '__main__':
# This part is important for direct testing of game.py
if __name__ == '__main__':
    current_roll = roll_dice()
    print("Initial roll:", current_roll)

    # Initialize state dictionaries
    available_from_roll = dict(current_roll)
    chosen_this_round = {}
    discarded_this_round = {}

    print("\nChoosing Blue (example value):")
    # Assuming 'blue' is in current_roll for this example to work
    if 'blue' in available_from_roll:
        value, msg = choose_die(available_from_roll, chosen_this_round, discarded_this_round, "blue")
        print(msg)
        print("Available after choosing blue:", available_from_roll)
        print("Chosen this round:", chosen_this_round)
        print("Discarded this round (by rule):", discarded_this_round)
    else:
        print("Blue die not in initial roll for this example run.")

    print("\nChoosing Yellow (example value):")
    if 'yellow' in available_from_roll:
        value, msg = choose_die(available_from_roll, chosen_this_round, discarded_this_round, "yellow")
        print(msg)
        print("Available after choosing yellow:", available_from_roll)
        print("Chosen this round:", chosen_this_round)
        print("Discarded this round (by rule):", discarded_this_round)
    else:
        print("Yellow die not in available dice for this example run.")

    print("\nTrying to choose Red (invalid color):")
    value, msg = choose_die(available_from_roll, chosen_this_round, discarded_this_round, "red")
    print(msg)

    print("\nTrying to choose an already chosen die (e.g., blue if chosen above):")
    if 'blue' in chosen_this_round:
         value, msg = choose_die(available_from_roll, chosen_this_round, discarded_this_round, "blue")
         print(msg)

def reset_dice():
    """Resets the dice state for a new round (conceptually).
    Actual state is managed by the bot instance for now.
    Returns a confirmation message.
    """
    # In a more complex game state model, this would clear dice from a game object.
    # For now, the bot will handle clearing its own state.
    return "Dice state reset. Ready for a new roll or setup."
