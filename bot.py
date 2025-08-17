"""
Note to self: to update new commands, restart discord client
"""

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
    bot.games = {}  # Dictionary to store game states per channel
    # Try to sync commands globally. This can take up to an hour to propagate.
    # For faster testing, you might sync to a specific guild (see commented out sync_guild_commands)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands:", [com.name for com in synced])
    except Exception as e:
        print(e)

# --- Helper Functions ---
def get_game_data(interaction: discord.Interaction) -> game.GameData | None:
    """Retrieves the game data for the channel, returns None if not found."""
    return bot.games.get(interaction.channel_id)

def log(action: str, interaction: discord.Interaction):
    """Logs interaction"""
    print(f"LOG: {action:8} | Channel: {interaction.channel_id} | User: {interaction.user}")

async def _send_dice_state_update(interaction: discord.Interaction, game_data: game.GameData, action_message: str = "", is_follow_up: bool = False):
    """
    Constructs and sends a message displaying the current state of all dice categories for a given game.
    Sorts dice within each category by value, then color.
    """
    response_parts = []

    if action_message:
        response_parts.append(action_message)

    response_parts.append("\n--- **Current Dice States** ---")

    # Chosen Dice
    if game_data.chosen_dice_this_round:
        response_parts.append("\n**Chosen Dice:**")
        sorted_chosen = sorted(game_data.chosen_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_chosen:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Chosen Dice:** None")

    # Available Dice
    if game_data.available_dice:
        response_parts.append("\n**Available Dice (for choosing or re-rolling):**")
        sorted_available = sorted(game_data.available_dice.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_available:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Available Dice:** None")

    # Discarded Dice
    if game_data.discarded_dice_this_round:
        response_parts.append("\n**Discarded Dice (this round):**")
        sorted_discarded = sorted(game_data.discarded_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_discarded:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Discarded Dice (this round):** None")

    response_parts.append("\n------------------------------")
    # Contextual next step advice
    if not game_data.available_dice and (game_data.chosen_dice_this_round or game_data.discarded_dice_this_round):
        response_parts.append("All dice have been processed for this roll! Use `/roll` for a new set of dice if your turn continues, or `/done` if finished.")
    elif game_data.available_dice:
        response_parts.append("Use `/take color:<color>` to pick an available die, or `/roll` to re-roll available dice.")
    else:
        response_parts.append("Use `/roll` to start a new round with fresh dice.")

    full_response = "\n".join(response_parts)

    if len(full_response) > 2000:
        full_response = full_response[:1990] + "... (truncated)"

    if is_follow_up:
        await interaction.followup.send(full_response, ephemeral=False)
    else:
        await interaction.response.send_message(full_response)

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


@bot.tree.command(name="clever_help", description="Prints help.")
async def clever_help_slash(interaction: discord.Interaction):
    """Prints help info."""
    log("clever_help", interaction)

    help_desc = """Instructions for using the Clever bot:
- `/new_game` - start a new game in this channel.
- `/roll` - roll the dice. Use this to start your turn, and to reroll any remaining available dice.
- `/take <color>` - take the available die of the color you give. After you do this, you should /roll again unless you have taken your 3 dice
- `/done` - use this after you've taken your 3 dice to display the dice available to others"""

    await interaction.response.send_message(help_desc)


@bot.tree.command(name="new_game", description="Starts a new game of That's Pretty Clever in this channel.")
@app_commands.describe(game_number="A number 1-4 for which game you are playing (1 for That's Pretty Clever, 2 for Twice as Clever, etc.).")
async def new_game_slash(interaction: discord.Interaction, game_number: int):
    """Creates a new game instance for the current channel."""
    log("new_game", interaction)

    # Create a new GameData object and assign it to the channel
    bot.games[interaction.channel_id] = game.GameData(game_number)

    names = {1: "That's Pretty Clever",
             2: "Twice as Clever",
             3: "Clever Cubed",
             4: "Clever 4Ever"}

    await interaction.response.send_message(f"A new game of {names[game_number]} has been started! Use `/roll` to begin.")


@bot.tree.command(name="roll", description="Rolls dice. Re-rolls available dice or does a full roll if none are available.")
async def roll_slash(interaction: discord.Interaction):
    """Rolls dice. If dice are already available, re-rolls only those. Otherwise, rolls all 6 dice."""
    log("roll", interaction)

    game_data = get_game_data(interaction)
    if not game_data:
        await interaction.response.send_message("No game is currently running in this channel. Use `/new_game` to start.", ephemeral=True)
        return

    roll_action_description = ""
    if game_data.available_dice:
        roll_action_description = "Re-rolling available dice..."
        game_data.reroll_available_dice()
    else:
        roll_action_description = "Rolling all new dice..."
        game_data.roll_dice()

    await _send_dice_state_update(interaction, game_data, action_message=roll_action_description)

@bot.tree.command(name="take", description="Takes a die from the available dice.")
@app_commands.describe(color="The color of the die to take.")
async def take_slash(interaction: discord.Interaction, color: str):
    """Takes a die from the available dice and updates game state."""
    log("take", interaction)

    game_data = get_game_data(interaction)
    if not game_data:
        await interaction.response.send_message("No game is currently running in this channel. Use `/new_game` to start.", ephemeral=True)
        return

    # The new game.choose_die method handles all logic, including checks for availability.
    chosen_value, message = game_data.choose_die(color)

    if chosen_value is not None:
        # On a successful choice, send the result message and then the updated state
        await interaction.response.send_message(message)
        await _send_dice_state_update(interaction, game_data, is_follow_up=True)
    else:
        # On failure (e.g., die not available), send the error message ephemerally.
        await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="done", description="Ends your turn, shows unchosen dice, and resets the dice tray.")
async def done_slash(interaction: discord.Interaction):
    """Summarizes unchosen dice from the round and resets the game state."""
    log("done", interaction)

    game_data = get_game_data(interaction)
    if not game_data:
        await interaction.response.send_message("No game is currently running in this channel. Use `/new_game` to start.", ephemeral=True)
        return

    response_parts = ["--- **End of Turn Summary** ---"]

    # Chosen Dice
    if game_data.chosen_dice_this_round:
        response_parts.append("\n**Your Chosen Dice:**")
        sorted_chosen = sorted(game_data.chosen_dice_this_round.items(), key=lambda x: (x[1], x[0]))
        for color, value in sorted_chosen:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Your Chosen Dice:** None")

    # Dice for others
    for_others = sorted(list(game_data.available_dice.items()) + list(game_data.discarded_dice_this_round.items()), key=lambda x: (x[1], x[0]))
    if for_others:
        response_parts.append("\n**Dice available to other players:**")
        for color, value in for_others:
            response_parts.append(f"- {color.capitalize()}: {value}")
    else:
        response_parts.append("\n**Dice available to other players:** None")

    response_parts.append("\n------------------------------")
    response_parts.append("The dice tray has been reset. Use `/roll` to start a new turn.")

    summary_message = "\n".join(response_parts)

    # Reset the game state for the channel
    game_data.reset()

    await interaction.response.send_message(summary_message)


# --- Optional: Command to sync commands to a specific guild for faster testing ---
# You would call this once using a prefix command e.g. !syncguild after starting the bot
# Then discord should show slash commands in that guild much faster.
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def syncguild(ctx):
    print("Running !syncguild")
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(synced)} commands to this guild.")


if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("Please replace 'YOUR_BOT_TOKEN' with your actual bot token in bot.py")
    else:
        bot.run(BOT_TOKEN)
