import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load bot token from environment file
load_dotenv()
bot_token = dict( os.environ )['DISCORD_BOT_TOKEN']

# Make the bot
bot = commands.Bot( command_prefix='m!' )

@bot.event
async def on_ready():
    print( "The bot is ready!" )

@bot.command()
async def hello( ctx ):
    await ctx.send( "Hello!" )

bot.run( bot_token )
