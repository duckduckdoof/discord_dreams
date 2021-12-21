#----------------------------------------------------------------------------------------------------------------------#
#
# discord_yt_audio_bot.py
#
# This file creates the discord bot, adds appropriate YoutubeDL functionality, and activates it for use.
# Credit goes to https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py for basic functionality.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import config_utils
import class_utils

from dotenv import load_dotenv
from discord.ext import commands

#-[ BOT DEFS ]---------------------------------------------------------------------------------------------------------#

# Load bot token from environment file
load_dotenv()
bot_token = dict( os.environ )[ 'DISCORD_BOT_TOKEN' ]

# Get config information
ytdl = config_utils.get_yt_dl_from_config()
ffmpeg_options = config_utils.get_ffmpeg_options_from_config()

# Create the bot
bot = commands.Bot( command_prefix=commands.when_mentioned_or( "m!" ),
                   description='Relatively simple music bot example' )

@bot.event
async def on_ready():
    print( f'Logged in as {bot.user} (ID: {bot.user.id})' )
    print( '------' )

bot.add_cog( class_utils.Music(bot) )
bot.run( bot_token )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
