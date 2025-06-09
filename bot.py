import discord
from discord.ext import commands
import game

# TODO: Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for commands

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    # ^ For dice chosen in the current roll/round. Resets with 'reset' or new 'roll'

@bot.command(name='roll')
async def roll(ctx):
    """Rolls all available dice."""
    dice_results = game.roll_dice()
    bot.available_dice = dict(dice_results)
    bot.chosen_dice_this_round = {} # Reset chosen dice on a new roll

    response = "Dice rolled:\n"
    for color, value in dice_results.items():
        response += f"{color.capitalize()}: {value}\n"
    response += "\nUse `!choose <color>` to pick a die."
    await ctx.send(response)

@bot.command(name='choose')
async def choose(ctx, color: str):
    """Chooses a die from the available dice."""
    if not bot.available_dice:
        await ctx.send("No dice have been rolled yet. Use `!roll` first.")
        return

    value, message = game.choose_die(bot.available_dice, bot.chosen_dice_this_round, color)

    await ctx.send(message)

    if value is not None:
        # Show remaining available dice
        if bot.available_dice:
            response = "Remaining available dice:\n"
            for r_color, r_value in bot.available_dice.items():
                response += f"{r_color.capitalize()}: {r_value}\n"
            await ctx.send(response)
        else:
            await ctx.send("No more dice available from this roll.")

@choose.error
async def choose_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'color':
            await ctx.send("You need to tell me which color to choose! Usage: `!choose <color>`")
            return
    # If the error is not a MissingRequiredArgument or not the 'color' param,
    # re-raise it so the default error handler can deal with it or other specific handlers.
    # For now, we'll just print to console for other errors during development.
    print(f"An error occurred with the choose command: {error}")

@bot.command(name='reset')
async def reset(ctx):
    """Resets the available and chosen dice. Does not automatically roll."""
    game.reset_dice() # Call the conceptual reset in game.py
    bot.available_dice = {}
    bot.chosen_dice_this_round = {}
    await ctx.send("All dice have been reset. Use `!roll` to roll new dice.")

if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("Please replace 'YOUR_BOT_TOKEN' with your actual bot token in bot.py")
    else:
        bot.run(BOT_TOKEN)
