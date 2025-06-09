import discord
# Keep 'commands' for BOT_TOKEN and other potential utilities, but primary interaction will be slash.
from discord.ext import commands
from discord import app_commands # Import app_commands
import game
import random # Make sure random is imported in bot.py for the selective reroll


with open("clever.key", "r") as f:
    BOT_TOKEN = f.read().strip()

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
    # Try to sync commands globally. This can take up to an hour to propagate.
    # For faster testing, you might sync to a specific guild (see commented out sync_guild_commands)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

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

@bot.tree.command(name="roll", description="Rolls dice. Re-rolls available dice or does a full roll if none are available.")
async def roll_slash(interaction: discord.Interaction):
    """Rolls dice. If dice are already available, re-rolls only those. Otherwise, rolls all 6 dice."""

    rolled_dice_this_turn = {} # To store the results of this specific roll action
    roll_type_message = ""

    if bot.available_dice: # If there are dice remaining from a previous turn
        roll_type_message = "Re-rolling available dice (lowest to highest):\n"
        for color in list(bot.available_dice.keys()): # Iterate over keys of available_dice
            new_value = random.randint(1, 6)
            bot.available_dice[color] = new_value # Update the value in available_dice
            rolled_dice_this_turn[color] = new_value
        # No need to reset chosen_dice_this_round here, as it's a continuation of the round
    else: # First roll, or after a reset, or all dice were used up
        roll_type_message = "Rolling all new dice (lowest to highest):\n"
        full_roll_results = game.roll_dice()
        bot.available_dice = dict(full_roll_results)
        rolled_dice_this_turn = dict(full_roll_results)
        bot.chosen_dice_this_round = {} # Reset chosen dice only on a full new roll

    response = roll_type_message
    # Sort the dice that were actually rolled/updated in this turn for display
    sorted_dice_display = sorted(rolled_dice_this_turn.items(), key=lambda x: (x[1], x[0]))

    for color, value in sorted_dice_display:
        response += f"{color.capitalize()}: {value}\n"

    # If, after a selective re-roll, some dice were previously chosen in this round,
    # it might be useful to list them too, or remind the user.
    # For now, chosen_dice_this_round is NOT reset on a selective re-roll.
    # This means a player continues their turn with the re-rolled dice.

    if bot.chosen_dice_this_round:
        response += "\nDice already chosen this round (not re-rolled):\n"
        sorted_chosen_dice = sorted(bot.chosen_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_chosen_dice:
            response += f"{color.capitalize()}: {value}\n"

    response += "\nUse `/choose color:<color>` to pick a die from the available rolled dice."
    await interaction.response.send_message(response)

@bot.tree.command(name="choose", description="Chooses a die from the available dice.")
@app_commands.describe(color="The color of the die to choose.")
async def choose_slash(interaction: discord.Interaction, color: str):
    """Chooses a die from the available dice."""
    if not bot.available_dice: # Check if any dice are available from a previous /roll
        # Check if bot.chosen_dice_this_round is also empty. If both are empty, it means no roll has happened.
        # If available_dice is empty but chosen_dice_this_round is not, it means all dice from roll were taken/discarded.
        if not bot.chosen_dice_this_round:
             await interaction.response.send_message("No dice have been rolled yet. Use `/roll` first.", ephemeral=True)
        else:
             await interaction.response.send_message("No more dice available from the current roll to choose. Use `/roll` to re-roll remaining or `/reset` for a full new roll.", ephemeral=True)
        return

    # Now game.choose_die returns: value, message, discarded_dice_info
    value, message, discarded_dice_info = game.choose_die(
        bot.available_dice,
        bot.chosen_dice_this_round,
        color
    )

    full_message = message # Start with the primary message (e.g., "You chose Blue die...")

    if discarded_dice_info:
        full_message += "\n\nDiscarded due to being lower than chosen die:"
        for item in discarded_dice_info:
            full_message += f"\n- {item}"

    # Send the combined message. If it's just an error (e.g. invalid color), it will be ephemeral.
    # If it's a successful choice, it will be public.
    if value is not None:
        await interaction.response.send_message(full_message)
    else:
        # Errors like "invalid color" or "die not available"
        await interaction.response.send_message(full_message, ephemeral=True)

    if value is not None:
        # If a die was successfully chosen, send a follow-up for remaining available dice.
        if bot.available_dice:
            remaining_response = "Remaining available dice:\n"
            # Sort remaining available dice for display
            sorted_remaining_dice = sorted(bot.available_dice.items(), key=lambda x: (x[1], x[0]))
            for r_color, r_value in sorted_remaining_dice:
                remaining_response += f"{r_color.capitalize()}: {r_value}\n"
            await interaction.followup.send(remaining_response, ephemeral=True)
        else:
            await interaction.followup.send("No more dice available from this roll. Use `/roll` to re-roll or `/reset` for a full new roll.", ephemeral=True)

@bot.tree.command(name="reset", description="Resets all dice. Does not automatically roll.")
async def reset_slash(interaction: discord.Interaction):
    """Resets the available and chosen dice. Does not automatically roll."""
    game.reset_dice()
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    await interaction.response.send_message("All dice have been reset. Use `/roll` to roll new dice.")

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
