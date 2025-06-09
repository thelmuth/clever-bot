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
    Returns (chosen_value, message, list_of_discarded_dice_info).
    list_of_discarded_dice_info contains strings like "Color: Value".
    """
    color_to_choose = color_to_choose.lower()
    if color_to_choose not in DICE_COLORS:
        return None, "Invalid dice color.", []

    if color_to_choose not in available_dice:
        return None, f"{color_to_choose.capitalize()} die is not available to choose.", []

    chosen_value = available_dice.pop(color_to_choose)
    chosen_dice_this_round[color_to_choose] = chosen_value

    message = f"You chose the {color_to_choose.capitalize()} die with value {chosen_value}."

    discarded_dice_info = []
    # Iterate over a copy of available_dice items because we might modify the dictionary
    # Store dice to be discarded to avoid modifying dict during iteration issues
    dice_to_discard_colors = []

    for color, value in available_dice.items():
        if value < chosen_value:
            dice_to_discard_colors.append(color)

    if dice_to_discard_colors:
        for color_d in dice_to_discard_colors:
            discarded_value = available_dice.pop(color_d)
            discarded_dice_info.append(f"{color_d.capitalize()}: {discarded_value}")

        # Append to the main message about discarded dice
        # message += "\nDiscarded dice (value less than chosen): " + ", ".join(discarded_dice_info) + "."
        # Let's return discarded_dice_info separately for better formatting in bot.py

    return chosen_value, message, discarded_dice_info

# Example usage (can be removed later):
if __name__ == '__main__':
    current_roll = roll_dice()
    print("Initial roll:", current_roll)
    available_from_roll = dict(current_roll) # Make a copy
    chosen_this_round = {}

    value, msg, discarded = choose_die(available_from_roll, chosen_this_round, "blue")
    print(msg)
    print(f"Discarded: {discarded}")
    print("Available after choosing blue:", available_from_roll)
    print("Chosen this round:", chosen_this_round)

    value, msg, discarded = choose_die(available_from_roll, chosen_this_round, "yellow")
    print(msg)
    print(f"Discarded: {discarded}")
    print("Available after choosing yellow:", available_from_roll)
    print("Chosen this round:", chosen_this_round)

    value, msg, discarded = choose_die(available_from_roll, chosen_this_round, "red") # Invalid color
    print(msg)
    print(f"Discarded: {discarded}")

def reset_dice():
    """Resets the dice state for a new round (conceptually).
    Actual state is managed by the bot instance for now.
    Returns a confirmation message.
    """
    # In a more complex game state model, this would clear dice from a game object.
    # For now, the bot will handle clearing its own state.
    return "Dice state reset. Ready for a new roll or setup."
