#----------------------------------------------------------------------------------------------------------------------#
#
# discord_yt_audio_bot.py
#
# This bot is a basic YT player with added functionality for queueing songs
# and other queueing-based logic and features.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

#-[ CONST DEFS ]-------------------------------------------------------------------------------------------------------#

#-[ INIT DEFS ]--------------------------------------------------------------------------------------------------------#

# Load bot token from environment file
load_dotenv()
bot_token = dict( os.environ )[ 'DISCORD_BOT_TOKEN' ]

# Set up discord bot intents and client
intents = discord.Intents().all()
client = discord.Client( intents=intents )

# Create the bot
bot = commands.Bot( command_prefix="m!", intents=intents,
                   description='Mansley Music LTD' )

# Add the Music Cog
bot.load_extension( "musiccommands" )

# Run the bot
bot.run( bot_token )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
