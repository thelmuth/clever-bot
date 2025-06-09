# Discord "That's Pretty Clever" Helper Bot

This is a simple Discord bot to help with playing board games like "That's Pretty Clever" by providing dice rolling and tracking functionalities.

## Features

- `/roll`: Rolls the 6 standard colored dice (Blue, Green, Orange, Purple, Yellow, White).
- `/choose color:<color>`: Allows you to select a die from the current roll.
- `/reset`: Clears the current dice roll and choices.

## Setup Instructions

### 1. Create a Discord Bot Application

   a. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   b. Click on "**New Application**" (top right).
   c. Give your application a name (e.g., "CleverBot") and click "**Create**".
   d. Navigate to the "**Bot**" tab on the left sidebar.
   e. Click "**Add Bot**" and confirm by clicking "**Yes, do it!**".

### 2. Get Your Bot Token

   a. On the "**Bot**" tab, under the bot's username, you should see a section for "**TOKEN**".
   b. Click "**Reset Token**" (or "**Copy**" if you've generated one before and have it saved). Make sure to copy the token immediately and store it securely. **Treat this token like a password! Do not share it publicly.**
   c. **Enable Privileged Gateway Intents**:
      - Scroll down on the Bot page to find "Privileged Gateway Intents".
      - Enable "**Message Content Intent**". (While primarily for slash commands now, some setups or future features might still benefit from it, and it was in our bot's code).

### 3. Invite the Bot to Your Server

   a. Go to the "**OAuth2**" tab, then "**URL Generator**" sub-tab.
   b. Under "**SCOPES**", checkmark `bot` and `applications.commands`.
   c. Under "**BOT PERMISSIONS**" that appears below, select the necessary permissions. For basic functionality, the bot needs:
      - `Send Messages`
      - `Read Message History` (to see commands)
      - `Use Slash Commands` (implicitly granted with `applications.commands` scope, but good to be aware)
   d. Copy the generated URL at the bottom.
   e. Paste the URL into your web browser, select the server you want to add the bot to, and click "**Authorize**".

### 4. Set Up Python Environment

   a. Ensure you have Python installed (version 3.7 or newer is recommended). You can download it from [python.org](https://www.python.org/).
   b. Clone this repository (or download the files) to your local machine.
   c. Open a terminal or command prompt and navigate to the project's root directory (where `requirements.txt` is located).
   d. It's highly recommended to use a virtual environment:
      ```bash
      python -m venv venv
      # On Windows
      venv\Scripts\activate
      # On macOS/Linux
      source venv/bin/activate
      ```
   e. Install the required Python libraries:
      ```bash
      pip install -r requirements.txt
      ```

### 5. Configure the Bot

   a. Open the `bot.py` file in a text editor.
   b. Find the line `BOT_TOKEN = 'YOUR_BOT_TOKEN'`.
   c. Replace `'YOUR_BOT_TOKEN'` with the actual bot token you copied in Step 2. Save the file.

### 6. Run the Bot

   a. In your terminal (ensure your virtual environment is activated and you are in the project directory), run the bot using:
      ```bash
      python bot.py
      ```
   b. If everything is set up correctly, you should see a message in your console like `Logged in as YourBotName`.
   c. The bot's slash commands might take up to an hour to appear globally for the first time. If you want to test them immediately on a specific server, you can (as the bot owner) use the `!syncguild` prefix command once in that server. After running `!syncguild`, the slash commands `/roll`, `/choose`, and `/reset` should become available in that server much faster.

## Available Slash Commands

-   `/roll`
    -   Rolls all 6 dice (Blue, Green, Orange, Purple, Yellow, White).
-   `/choose color:<color>`
    -   Chooses a die of the specified color from the current roll.
    -   Example: `/choose color:blue`
-   `/reset`
    -   Clears the current roll and chosen dice.
