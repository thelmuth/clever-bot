import discord
# Keep 'commands' for BOT_TOKEN and other potential utilities, but primary interaction will be slash.
from discord.ext import commands
from discord import app_commands # Import app_commands
import game
import random # Make sure random is imported in bot.py for the selective reroll

# TODO: Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Intents are still needed
intents = discord.Intents.default()
# Message content might not be strictly necessary for slash commands unless you have other plans
# intents.message_content = True

# We still use commands.Bot as the base, but we'll attach a CommandTree to it
bot = commands.Bot(command_prefix="!", intents=intents) # Prefix can be kept for other bot owner commands or removed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    bot.discarded_dice_this_round = {} # Add this line
    # Try to sync commands globally. This can take up to an hour to propagate.
    # For faster testing, you might sync to a specific guild (see commented out sync_guild_commands)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# --- Helper Function to Send Dice State ---
async def _send_dice_state_update(interaction: discord.Interaction, action_message: str = "", is_follow_up: bool = False):
    """
    Constructs and sends a message displaying the current state of all dice categories.
    Sorts dice within each category by value, then color.
    """
    response_parts = []

    if action_message: # Prepend any specific action message (e.g., from choose_die or roll type)
        response_parts.append(action_message)

    response_parts.append("\n--- **Current Dice States** ---")

    # Chosen Dice
    if bot.chosen_dice_this_round:
        response_parts.append("\n**Chosen Dice:**")
        sorted_chosen = sorted(bot.chosen_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_chosen:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Chosen Dice:** None")

    # Available Dice
    if bot.available_dice:
        response_parts.append("\n**Available Dice (for choosing or re-rolling):**")
        sorted_available = sorted(bot.available_dice.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_available:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Available Dice:** None")

    # Discarded Dice
    if bot.discarded_dice_this_round:
        response_parts.append("\n**Discarded Dice (this round):**")
        sorted_discarded = sorted(bot.discarded_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_discarded:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Discarded Dice (this round):** None")

    response_parts.append("\n------------------------------")
    # Add contextual next step advice
    if not bot.available_dice and (bot.chosen_dice_this_round or bot.discarded_dice_this_round) and not is_follow_up: # if it's a primary message after a roll that cleared available
        response_parts.append("All dice have been processed for this roll! Use `/roll` for a new set of dice if your turn continues, or `/done` if finished.")
    elif not bot.available_dice and is_follow_up : # if it's a followup after a choose that cleared available
         response_parts.append("No more dice available to choose. Use `/roll` to re-roll if your turn continues, or `/done`.")
    elif bot.available_dice :
         response_parts.append("Use `/choose color:<color>` to pick an available die, or `/roll` to re-roll available dice.")
    else: # Should ideally be caught by initial roll state if no dice anywhere.
         response_parts.append("Use `/roll` to start a new round with fresh dice.")


    full_response = "\n".join(response_parts)

    # Ensure message length is within Discord's limits (2000 characters)
    if len(full_response) > 2000:
        full_response = full_response[:1990] + "... (truncated)"

    if is_follow_up:
        # Follow-up messages can be ephemeral or public. Let's make state updates public for now.
        await interaction.followup.send(full_response, ephemeral=False)
    else:
        await interaction.response.send_message(full_response)

# --- End of _send_dice_state_update function ---

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingParameter):
        param_name = error.parameter.name
        await interaction.response.send_message(
            f"Oops! You forgot to provide the '{param_name}'. Please include it when you use the command.",
            ephemeral=True # Only the user who invoked the command will see this
        )
    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Sorry, I don't recognize that command.", ephemeral=True)
    # Add more specific error checks here if needed
    # For example, app_commands.TransformerError for conversion issues
    # app_commands.CheckFailure for failed checks
    else:
        # Generic error message for other cases
        print(f"Unhandled error in slash command: {error}") # Log the full error to console
        await interaction.response.send_message(
            "An unexpected error occurred while trying to run that command. I've logged the issue.",
            ephemeral=True
        )

# --- Slash Command Definitions ---

@bot.tree.command(name="ping", description="A simple test command to check if slash commands are working.")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

@bot.tree.command(name="roll", description="Rolls dice. Re-rolls available dice or does a full roll if none are available.")
async def roll_slash(interaction: discord.Interaction):
    """Rolls dice. If dice are already available, re-rolls only those. Otherwise, rolls all 6 dice."""

    roll_action_description = ""

    if bot.available_dice:
        roll_action_description = "Re-rolling available dice..."
        for color_key in list(bot.available_dice.keys()): # Use a different variable name to avoid conflict
            new_value = random.randint(1, 6)
            bot.available_dice[color_key] = new_value
        # bot.chosen_dice_this_round is NOT reset
        # bot.discarded_dice_this_round is NOT reset
    else:
        roll_action_description = "Rolling all new dice..."
        full_roll_results = game.roll_dice()
        bot.available_dice = dict(full_roll_results)
        bot.chosen_dice_this_round = {}
        bot.discarded_dice_this_round = {}

    # For /roll, the _send_dice_state_update IS the primary response.
    # Pass the roll_action_description to be prepended to the state display.
    await _send_dice_state_update(interaction, action_message=roll_action_description, is_follow_up=False)

@bot.tree.command(name="choose", description="Chooses a die from the available dice.")
@app_commands.describe(color="The color of the die to choose.")
async def choose_slash(interaction: discord.Interaction, color: str):
    """Chooses a die from the available dice and updates game state."""
    # Initial availability checks (slightly simplified as game.choose_die also checks)
    if not bot.available_dice and not bot.chosen_dice_this_round and not bot.discarded_dice_this_round:
        await interaction.response.send_message("No dice have been rolled yet. Use `/roll` first.", ephemeral=True)
        return
    # More specific check if all dice from a roll are gone (either chosen or discarded)
    # but it's not a fresh game state (i.e., chosen or discarded are populated)
    elif not bot.available_dice and (bot.chosen_dice_this_round or bot.discarded_dice_this_round):
         await interaction.response.send_message("No more dice available from the current roll to choose. Use `/roll` to re-roll or `/reset` for a new roll.", ephemeral=True)
         return


    # Call game.choose_die, now passing all three state dictionaries
    chosen_value, message = game.choose_die(
        bot.available_dice,
        bot.chosen_dice_this_round,
        bot.discarded_dice_this_round, # Pass the new dictionary
        color
    )

    # Send the immediate feedback from choose_die (e.g., "You chose X... Dice Y, Z discarded...")
    # This message will be public if a successful choice was made, ephemeral for errors.
    if chosen_value is not None:
        await interaction.response.send_message(message)
    else:
        # Errors like "invalid color", "die not available", "already chosen/discarded"
        await interaction.response.send_message(message, ephemeral=True) # Send error message from game.choose_die
        return # Do not proceed to send dice state update if there was an error

    # Send the direct result of the choice first (e.g., "You chose Blue... X, Y discarded")
    # await interaction.response.send_message(message) # Corrected variable name in comment too
    # Then, send the comprehensive state update as a follow-up.
    # Pass no action_message here as the primary action was already sent.
    await _send_dice_state_update(interaction, action_message="", is_follow_up=True)

@bot.tree.command(name="reset", description="Resets all dice. Does not automatically roll.")
async def reset_slash(interaction: discord.Interaction):
    """Resets the available and chosen dice. Does not automatically roll."""
    game.reset_dice()
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    bot.discarded_dice_this_round = {} # Add this line
    await interaction.response.send_message("All dice have been reset. Use `/roll` to roll new dice.")

@bot.tree.command(name="done", description="Ends your turn, shows unchosen dice, and resets the dice tray.")
async def done_slash(interaction: discord.Interaction):
    """Summarizes unchosen dice from the round and resets the game state."""

    response_parts = ["--- **End of Turn Summary** ---"]

    anything_to_report = False

    # Dice that were available but not chosen
    if bot.available_dice:
        anything_to_report = True
        response_parts.append("\n**Dice remaining on tray (were available):**")
        sorted_available = sorted(bot.available_dice.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_available:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Dice remaining on tray (were available):** None")

    # Dice that were discarded by game rules (not directly chosen)
    if bot.discarded_dice_this_round:
        anything_to_report = True
        response_parts.append("\n**Dice discarded by game rules (not chosen by you):**")
        sorted_discarded = sorted(bot.discarded_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_discarded:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Dice discarded by game rules (not chosen by you):** None")

    if not anything_to_report and not bot.chosen_dice_this_round: # also check chosen_dice to see if anything happened at all
        response_parts.append("\nNo dice were rolled or in play this round.")
    elif not anything_to_report and bot.chosen_dice_this_round:
        response_parts.append("\nAll dice rolled this round were chosen!")


    response_parts.append("\n------------------------------")
    response_parts.append("The dice tray has been reset. Use `/roll` to start a new turn/round.")

    summary_message = "\n".join(response_parts)

    # Ensure message length is within Discord's limits
    if len(summary_message) > 2000:
        summary_message = summary_message[:1990] + "... (truncated)"

    await interaction.response.send_message(summary_message)

    # Reset all game states
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    bot.discarded_dice_this_round = {}
    # game.reset_dice() # Call this if it ever does more than return a string

# Remove the old prefix command error handler for choose:
# @choose.error (delete this and its function definition)

# --- Optional: Command to sync commands to a specific guild for faster testing ---
# You would call this once using a prefix command e.g. !syncguild after starting the bot
# Then discord should show slash commands in that guild much faster.
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def syncguild(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(synced)} commands to this guild.")


if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("Please replace 'YOUR_BOT_TOKEN' with your actual bot token in bot.py")
    else:
        bot.run(BOT_TOKEN)
