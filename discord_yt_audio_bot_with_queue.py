#----------------------------------------------------------------------------------------------------------------------#
#
# discord_yt_audio_bot_with_queue.py
#
# This bot is the same as 'discord_yt_audio_bot.py', with added functionality for queueing songs
# and other queueing-based logic and features.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import os
import config_utils
import class_utils
import discord

from dotenv import load_dotenv
from discord.ext import commands

#-[ CONFIG DEFS ]------------------------------------------------------------------------------------------------------#

# Load bot token from environment file
load_dotenv()
bot_token = dict( os.environ )[ 'DISCORD_BOT_TOKEN' ]

# Get config information
ytdl = config_utils.get_yt_dl_from_config()
ffmpeg_options = config_utils.get_ffmpeg_options_from_config()

# Set up discord bot intents and client
intents = discord.Intents().all()
client = discord.Client( intents=intents )

#-[ BOT DEFS ]---------------------------------------------------------------------------------------------------------#

# Create the bot
bot = commands.Bot( command_prefix="m!", intents=intents,
                   description='Relatively simple music bot' )

#---------------------------
# NOTE: the below command downloads the entire video before playing; streaming seems to be better
#---------------------------

# @bot.command( name='play_old', help='Plays a video/song on Youtube' )
# async def play( ctx, url ):
#     if url == None or url == "":
#         await ctx.send( "Please provide a valid Youtube URL" )
#         return
#     try:
#         server = ctx.message.guild
#         voice_channel = server.voice_client
# 
#         async with ctx.typing():
#             print( "Retrieving audio..." )
#             filename = await class_utils.YTDLSource.from_url( url, ytdl, ffmpeg_options, loop=bot.loop )
#             print( "Playing audio..." )
#             voice_channel.play( discord.FFmpegPCMAudio( source=filename ) )
#     except:
#         await ctx.send( "The bot is not currently connected to a voice channel" )

#---------------------------

"""
Your basic 'play' button.
Plays the YT video from the provided URL in the message.
"""
@bot.command( name='play', help='Streams a video/song on Youtube' )
async def stream( ctx, url ):

    # Sanity check those URLs
    # TODO: a more robust URL checker could prove useful here...
    if url == None or url == "":
        await ctx.send( "Please provide a valid Youtube URL" )
        return

    # Obtain the appropriate voice channel, then stream the video
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            print( "Youtube video requested by " + ctx.message.author.display_name )
            print( "Retrieving audio stream..." )
            filename = await class_utils.YTDLSource.from_url( url, ytdl, ffmpeg_options, loop=bot.loop, stream=True )
            print( "Playing audio stream..." )
            voice_channel.play( discord.FFmpegPCMAudio( source=filename ), after=lambda: print("All done!") )
    except:
        await ctx.send( "The bot is not currently connected to a voice channel" )

"""
Pauses the bot voice client.
"""
@bot.command( name='pause', help='Pause the video/song' )
async def pause( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send( "The bot is not playing anything at the moment." )
    
"""
Resumes the bot voice client (if applicable).
"""
@bot.command( name='resume', help='Resumes the video/song' )
async def resume( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send( "The bot was not playing anything before this. Use play command" )

"""
Makes the bot stop playing the song.
"""
@bot.command( name='stop', help='Stops the video/song' )
async def stop( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send( "The bot is not playing anything at the moment." )

"""
Manual command for making the bot join the channel the invoking user is in.
"""
@bot.command( name='join', help='Join the channel which the invoking user is in')
async def join( ctx ):
    if not ctx.message.author.voice:
        await ctx.send( "{} is not connected to a voice channel".format(ctx.message.author.name) )
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

"""
Manual command for making the bot leave the channel.
"""
@bot.command( name='leave', help='Leave the voice channel (if applicable)' )
async def leave( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send( "The bot is not connected to a voice channel." )

"""
Ensures that, if a user is in a voice channel, the bot
will first ensure that it joins the corresponding channel before playing.
"""
@stream.before_invoke
async def ensure_voice( ctx ):
    print( "Ensuring bot is in voice channel" )
    if ctx.voice_client is None:
        if ctx.message.author.voice:
            await ctx.message.author.voice.channel.connect()
        else:
            await ctx.send( "You are not connected to a voice channel." )
            raise commands.CommandError( "Author not connected to a voice channel." )
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

"""
When the bot is ready, log basic info.
"""
@bot.event
async def on_ready():
    print( f'Logged in as {bot.user} (ID: {bot.user.id})' )
    print( '------' )

bot.run( bot_token )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
