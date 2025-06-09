import discord
# Keep 'commands' for BOT_TOKEN and other potential utilities, but primary interaction will be slash.
from discord.ext import commands
from discord import app_commands # Import app_commands
import game

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

@bot.tree.command(name="roll", description="Rolls all available dice.")
async def roll_slash(interaction: discord.Interaction):
    """Rolls all available dice."""
    dice_results = game.roll_dice()
    bot.available_dice = dict(dice_results)
    bot.chosen_dice_this_round = {} # Reset chosen dice on a new roll

    response = "Dice rolled:\n"
    for color, value in dice_results.items():
        response += f"{color.capitalize()}: {value}\n"
    response += "\nUse `/choose color:<color>` to pick a die."
    await interaction.response.send_message(response)

@bot.tree.command(name="choose", description="Chooses a die from the available dice.")
@app_commands.describe(color="The color of the die to choose.")
async def choose_slash(interaction: discord.Interaction, color: str):
    """Chooses a die from the available dice."""
    if not bot.available_dice:
        await interaction.response.send_message("No dice have been rolled yet. Use `/roll` first.", ephemeral=True)
        return

    value, message = game.choose_die(bot.available_dice, bot.chosen_dice_this_round, color)

    # Send the primary message (e.g., "You chose Blue die...")
    await interaction.response.send_message(message)

    if value is not None:
        # If a die was successfully chosen, send a follow-up for remaining dice.
        # Slash commands can use interaction.followup.send() for additional messages.
        if bot.available_dice:
            response = "Remaining available dice:\n"
            for r_color, r_value in bot.available_dice.items():
                response += f"{r_color.capitalize()}: {r_value}\n"
            await interaction.followup.send(response, ephemeral=True) # Ephemeral so only user sees it
        else:
            await interaction.followup.send("No more dice available from this roll.", ephemeral=True)

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
