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
import queue
import config_utils
import ytdl_utils
import discord

from dotenv import load_dotenv
from discord.ext import commands

#-[ CONST DEFS ]-----------------------------------------------------------------------------------------------------#

MAX_QUEUE_SIZE = 20

#-[ INIT DEFS ]------------------------------------------------------------------------------------------------------#

# Load bot token from environment file
load_dotenv()
bot_token = dict( os.environ )[ 'DISCORD_BOT_TOKEN' ]

# Get config information
ytdl = config_utils.get_yt_dl_from_config()
ffmpeg_options = config_utils.get_ffmpeg_options_from_config()

# Set up discord bot intents and client
intents = discord.Intents().all()
client = discord.Client( intents=intents )

# Set up queue for multiple YT vids
yt_queue = queue.Queue( maxsize=MAX_QUEUE_SIZE )

#-[ BOT DEFS ]---------------------------------------------------------------------------------------------------------#

# Create the bot
bot = commands.Bot( command_prefix="m!", intents=intents,
                   description='Relatively simple music bot' )

"""
Plays the next song on the queue.
This is invoked by the 'after' function for voice_channel.play()
"""
def play_next( ctx ):

    # Check the queue
    if yt_queue.empty():
        print( "Queue is empty..." )
        return

    # If we're already playing something, wait for the lambda function to trigger the next song
    if ctx.voice_client.is_playing():
        print( "Currently playing, waiting for turn..." )
        return

    # Obtain the appropriate voice channel, then stream the video
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        yt_obj = yt_queue.get()

        print( "Playing stream..." )
        voice_channel.play( discord.FFmpegPCMAudio( source=yt_obj.url, **ffmpeg_options ), after=lambda x: play_next( ctx ) )
    except Exception as e:
        print( "Error passing context to play_next()" )
        print( e )

"""
Obtains appropriate file object to play video from a given URL
"""
async def get_yt_obj_from_url( ctx, url: str ):
    try:
        # Left this line here, could be useful but I haven't seen immediate changes without it
        # async with ctx.typing():
        print( "Youtube video requested by " + ctx.message.author.display_name )
        print( "URL: " + url )
        print( "Retrieving stream..." )
        yt_obj = await ytdl_utils.YTDLSource.stream_from_url( url, ytdl )
        return yt_obj
    except:
        await ctx.send( "The bot is not currently connected to a voice channel" )

"""
Adds a song the queue, and plays the first song.
"""
@bot.command( name='q', help='Queues a YT URL for playing' )
async def queue( ctx, url ):

    # Sanity check the URL
    # SEE ABOVE FUNCTION (stream) on note for better URL check
    if url == None or url == "":
        await ctx.send( "Please provide a valid Youtube URL" )
        return
    try:
        yt_obj = await get_yt_obj_from_url( ctx, url )
        print( "Queueing video..." )
        yt_queue.put( yt_obj )

        # Start the player if we're not currently playing anything
        play_next( ctx )
    except Exception as e:
        await ctx.send( "Error found while queueing music..." )
        print( e )

"""
Takes all songs in the music queue, and prints them out in order
TODO: it may be a good idea to list who queued the song as well...
"""
@bot.command( name='l', help='List videos in the queue' )
async def list_queue( ctx ):
    if yt_queue.empty():
        await ctx.send( "Queue is empty" )
    else:
        music_list = list( yt_queue.queue )
        out_str = ""
        for i, music in enumerate(music_list):
            out_str += str(i) + ": " + music.title + "\n"
        await ctx.send( out_str )

"""
Makes the bot stop the current song, and queues the next song
"""
@bot.command( name='n', help='Stops the video/song' )
async def next( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        print( "Skipping current song..." )
        voice_client.stop()
    else:
        await ctx.send( "The bot is not playing anything at the moment." )

"""
Pauses the bot voice client.
"""
@bot.command( name='pause', help='Pause the video/song' )
async def pause( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        print( "Pausing..." )
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
        print( "Resuming..." )
        voice_client.resume()
    else:
        await ctx.send( "The bot was not playing anything before this. Use play command" )

"""
Makes the bot stop the current song, and clears the queue
"""
@bot.command( name='clear', help='Stops the video/song' )
async def clear( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        print( "Stopping..." )
        with yt_queue.mutex:
            yt_queue.queue.clear()
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
@queue.before_invoke
@list_queue.before_invoke
async def ensure_voice( ctx ):
    print( "Ensuring bot is in voice channel" )
    if ctx.voice_client is None:
        if ctx.message.author.voice:
            await ctx.message.author.voice.channel.connect()
        else:
            await ctx.send( "You are not connected to a voice channel." )
            raise commands.CommandError( "Author not connected to a voice channel." )

"""
When the bot is ready, log basic info.
"""
@bot.event
async def on_ready():
    print( f'Logged in as {bot.user} (ID: {bot.user.id})' )
    print( '------' )

bot.run( bot_token )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
