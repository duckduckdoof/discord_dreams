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
import datetime

from dotenv import load_dotenv
from discord.ext import commands
from prettytable import PrettyTable

#-[ CONST DEFS ]-------------------------------------------------------------------------------------------------------#

MAX_QUEUE_SIZE = 20

# one second less than a full day, keeps formatting issues easy later (technically this is a limitation of the bot).
MAX_TIMESTAMP = 86399

#-[ INIT DEFS ]--------------------------------------------------------------------------------------------------------#

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
loop_queue = False
loop_current = False
now_playing = None

#-[ BOT DEFS ]---------------------------------------------------------------------------------------------------------#

# Create the bot
bot = commands.Bot( command_prefix="m!", intents=intents,
                   description='Mansley Music LTD' )

"""
This function is a prep for playing the next song.
We want to check if we're looping a song or the whole queue, and adjust
how to play the next song accordingly.
"""
def play_next( ctx ):

    global now_playing
    global loop_queue
    global loop_current

    # If we're already playing something, wait for the lambda function to trigger the next song
    if ctx.voice_client.is_playing():
        print( "Currently playing, waiting for turn..." )
        return

    # If we enable loop_current, then get the current song
    if loop_current:
        print( "Looping current song" )
        if now_playing == None:
            now_playing = yt_queue.empty() ? None : yt_queue.get()

    # If we enable loop_queue, then we put the song back on the queue
    elif loop_queue:
        print( "Looping queue" )
        now_playing = yt_queue.empty() ? None : yt_queue.get()
        yt_queue.put( now_playing )

    # Otherwise, we just get the next song
    else:
        print( "Grabbing next item on queue..." )
        now_playing = yt_queue.empty() ? None : yt_queue.get()

    # Now play the song
    play_song( ctx, now_playing )

"""
Plays the song passed as an argument to this function
"""
def play_song( ctx, current_song ):

    # Check if the song is not empty
    if current_song == None:
        print( "All finished!" )
        return

    # Obtain the appropriate voice channel, then stream the video
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        min_seconds = ( min( current_song.start_time or 0, MAX_TIMESTAMP ) )
        timestamp = str( datetime.timedelta( seconds=min_seconds ) )

        print( "Playing stream..." )
        voice_channel.play(
            discord.FFmpegPCMAudio(
                source=current_song.url,
                **ffmpeg_options,
                before_options='-ss ' + timestamp
            ), after=lambda x: play_next( ctx )
        )
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
        yt_objects = await ytdl_utils.YTDLSource.stream_from_url( url, ytdl )
        return yt_objects
    except:
        await ctx.send( "The bot is not currently connected to a voice channel" )

"""
Adds a song the queue, and plays the first song.
"""
@bot.command( name='queue', aliases=['q'], help='Queues a YT URL for playing' )
async def queue( ctx, url ):

    # Sanity check the URL
    # SEE ABOVE FUNCTION (stream) on note for better URL check
    if url == None or url == "":
        await ctx.send( "Please provide a valid Youtube URL" )
        return
    try:
        yt_objects = await get_yt_obj_from_url( ctx, url )
        print( "Queueing video(s)..." )
        for yt_obj in yt_objects:
            yt_queue.put( yt_obj )

        # Start the player if we're not currently playing anything
        if not (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            play_next( ctx )
    except queue.Full:
        await ctx.send( "Queue is full!" )
    except Exception as e:
        await ctx.send( "Error found while queueing music..." )
        print( e )

"""
Takes all songs in the music queue, and prints them out in order
TODO: it may be a good idea to list who queued the song as well...
"""
@bot.command( name='list', aliases=['l'], help='List videos in the queue' )
async def list_queue( ctx ):
    global now_playing
    if now_playing == None:
        now_playing_str = "Nothing"
    else:
        now_playing_str = now_playing.title
    current_str = '`' + "Now Playing: " + str(now_playing_str) + '`' + '\n\n'

    # Assemble print strings
    if yt_queue.empty():
        table_str = "`Queue is empty`"
    else:
        queue_table = PrettyTable()
        queue_table.field_names = [ '', 'Queue' ]
        music_list = list( yt_queue.queue )
        for i, music in enumerate(music_list):
            queue_table.add_row( [ "Up Next >>>" if i == 0 else "", music.title ] )
        table_str = '`' + queue_table.get_string() + '`'

    # Print out the strings
    await ctx.send( current_str + table_str )

"""
Makes the bot stop the current song, and queues the next song
"""
@bot.command( name='next', aliases=['n'], help='Queues the next song' )
async def next( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        print( "Skipping current song..." )
        voice_client.stop()
    else:
        await ctx.send( "The bot is not playing anything at the moment." )

"""
Sets the queue to loop songs
NOTE: if we have loop_current enabled, then the bot will prioritize that first!
"""
@bot.command( name='loop', help='Toggles loop queue' )
async def loop_q( ctx ):
    global loop_queue
    loop_queue = not loop_queue
    if loop_queue:
        await ctx.send( "Loop queue enabled" )
    else:
        await ctx.send( "Loop queue disabled" )

"""
Sets the queue to loop the current song
When we loop the current song, we ignore the queue loop variable.
"""
@bot.command( name='loopfirst', aliases=['lfirst'], help='Loops the current song being played' )
async def loop_s( ctx ):
    global loop_current
    loop_current = not loop_current
    if loop_current:
        await ctx.send( "Looping current song" )
    else:
        await ctx.send( "No longer looping current song" )

"""
Pauses the bot voice client.
"""
@bot.command( name='pause', aliases=['p'], help='Pause the video/song' )
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
@bot.command( name='resume', aliases=['r'], help='Resumes the video/song' )
async def resume( ctx ):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        print( "Resuming..." )
        voice_client.resume()
    else:
        await ctx.send( "The bot was not playing anything before this. Use 'q' command" )

"""
Makes the bot stop the current song, and clears the queue
"""
@bot.command( name='clear', aliases=['c'], help='Stops the video/song' )
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
        with yt_queue.mutex:
            yt_queue.queue.clear()
        voice_client.stop()
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
