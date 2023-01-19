#----------------------------------------------------------------------------------------------------------------------#
#
# music_cog.py
#
# This cog is for music queueing functionality.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import queue
import discord
import ytdl_utils
import config_utils
import datetime

from discord.ext import commands

#-[ CONST DEFS ]-------------------------------------------------------------------------------------------------------#

MAX_QUEUE_SIZE = 20

# one second less than a full day, keeps formatting issues easy later (technically this is a limitation of the bot).
MAX_TIMESTAMP = 86399

#-[ CLASS DEFS ]-------------------------------------------------------------------------------------------------------#

"""
This Cog is responsible for queueing music and playing via FFMpegPCMAudio.

Additionally, all functions related to queueing music (i.e. - pausing, going next, toggle looping)
are included in this Cog.
"""
class MusicCommands( commands.Cog ):

    """
    Constructor for the Cog

    We make sure to get the default configuration for both ytdl and ffmpeg
    """
    def __init__( self, bot: commands.Bot ):
        
        # Bot and configs
        self.bot = bot
        self.ytdl = config_utils.get_yt_dl_from_config()
        self.ffmpeg_options = config_utils.get_ffmpeg_options_from_config()
        
        # Queue init
        self.yt_queue = queue.Queue( maxsize=MAX_QUEUE_SIZE )
        self.loop_queue = False
        self.loop_current = False
        self.now_playing = None

    """
    This function is a prep for playing the next song.
    We want to check if we're looping a song or the whole queue, and adjust
    how to play the next song accordingly.
    """
    def play_next( self, ctx ):

        # Check if the voice channel is still active
        server = ctx.message.guild
        voice_channel = server.voice_client

        # If we're not in a voice channel, leave
        if voice_channel == None:
            print( "We're not in a voice channel, stopping..." )
            return

        # If we're already playing something, wait for the lambda function to trigger the next song
        if ctx.voice_client.is_playing():
            print( "Currently playing, waiting for turn..." )
            return

        # If we enable loop_current, then get the current song
        if self.loop_current:
            print( "Looping current song" )
            if self.now_playing == None:
                self.now_playing = None if self.yt_queue.empty() else self.yt_queue.get()

        # If we enable loop_queue, then we put the song back on the queue
        elif self.loop_queue:
            print( "Looping queue" )
            self.now_playing = None if self.yt_queue.empty() else self.yt_queue.get()
            self.yt_queue.put( self.now_playing )

        # Otherwise, we just get the next song
        else:
            print( "Grabbing next item in queue..." )
            self.now_playing = None if self.yt_queue.empty() else self.yt_queue.get()

        # Now play the song
        self.play_song( ctx, voice_channel, self.now_playing )

    """
    Plays the song passed as an argument to this function
    """
    def play_song( self, ctx, voice_channel, current_song ):

        # Check if the song is not empty
        if current_song == None:
            print( "All finished!" )
            return

        # Obtain the appropriate voice channel, then stream the video
        try:

            min_seconds = ( min( current_song.start_time or 0, MAX_TIMESTAMP ) )
            timestamp = str( datetime.timedelta( seconds=min_seconds ) )

            print( "Playing stream..." )
            voice_channel.play(
                discord.FFmpegPCMAudio(
                    source=current_song.url,
                    **self.ffmpeg_options,
                    before_options='-ss ' + timestamp
                ), after=lambda x: self.play_next( ctx )
            )
        except Exception as e:
            print( "Error passing context to play_next()" )
            print( e )

    """
    Obtains appropriate file object to play video from a given URL
    """
    async def get_yt_obj_from_url( self, ctx, url: str ):
        try:
            # Left this line here, could be useful but I haven't seen immediate changes without it
            # async with ctx.typing():
            print( "Youtube video requested by " + ctx.message.author.display_name )
            print( "URL: " + url )
            print( "Retrieving stream..." )
            yt_objects = await ytdl_utils.YTDLSource.stream_from_url( url, self.ytdl )
            return yt_objects
        except:
            await ctx.send( "The bot is not currently connected to a voice channel" )

    """
    Adds a song the queue, and plays the first song.
    """
    @commands.command( name='queue', aliases=['q'], help='Queues a YT URL for playing' )
    async def queue( self, ctx, url ):

        # Sanity check the URL
        # SEE ABOVE FUNCTION (stream) on note for better URL check
        if url == None or url == "":
            await ctx.send( "Please provide a valid Youtube URL" )
            return
        try:
            yt_objects = await self.get_yt_obj_from_url( ctx, url )
            print( "Queueing video(s)..." )
            for yt_obj in yt_objects:
                self.yt_queue.put( yt_obj )

            # Start the player if we're not currently playing anything
            if not (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                self.play_next( ctx )
        except queue.Full:
            await ctx.send( "Queue is full!" )
        except Exception as e:
            await ctx.send( "Error found while queueing music..." )
            print( e )

    """
    Takes all songs in the music queue, and prints them out in order
    TODO: it may be a good idea to list who queued the song as well...
    """
    @commands.command( name='list', aliases=['l'], help='List videos in the queue' )
    async def list_queue( self, ctx ):

        # Extra information: include if we're looping
        now_playing_title = "Now Playing (on repeat): " if self.loop_current else "Now Playing:"
        queue_title = "Music Queue (on loop)" if self.loop_queue else "Music Queue"

        # Get the current song (if applicable)
        if self.now_playing == None:
            now_playing_str = "Nothing"
        else:
            now_playing_str = self.now_playing.title

        # Get the list of songs on the queue (if not empty)
        if self.yt_queue.empty():
            queue_str = "There are no songs in the queue!"
        else:
            yt_queue_list = list( self.yt_queue.queue )
            yt_titles_list = [ yt.title for yt in yt_queue_list ]
            queue_list = [ f"{i+1}:\t {song}" for i, song in enumerate( yt_titles_list ) ]
            queue_str = '\n'.join( queue_list )

        # Create the embed for the queue, and send it
        list_embed = discord.Embed( title=queue_title, colour=0xEC6541 )
        list_embed.set_author( name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url )
        list_embed.add_field( name="Up Next:", value=queue_str, inline=False )
        list_embed.add_field( name=now_playing_title, value=now_playing_str, inline=False )

        await ctx.send( embed=list_embed )

    """
    Makes the bot stop the current song, and queues the next song
    """
    @commands.command( name='next', aliases=['n'], help='Queues the next song' )
    async def next( self, ctx ):
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
    @commands.command( name='loop', help='Toggles loop queue' )
    async def loop_q( self, ctx ):
        self.loop_queue = not self.loop_queue
        if self.loop_queue:
            await ctx.send( "Loop queue enabled" )
        else:
            await ctx.send( "Loop queue disabled" )

    """
    Sets the queue to loop the current song
    When we loop the current song, we ignore the queue loop variable.
    """
    @commands.command( name='loopfirst', aliases=['lfirst'], help='Loops the current song being played' )
    async def loop_s( self, ctx ):
        self.loop_current = not self.loop_current
        if self.loop_current:
            await ctx.send( "Looping current song" )
        else:
            await ctx.send( "No longer looping current song" )

    """
    Pauses the bot voice client.
    """
    @commands.command( name='pause', aliases=['p'], help='Pause the video/song' )
    async def pause( self, ctx ):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            print( "Pausing..." )
            voice_client.pause()
        else:
            await ctx.send( "The bot is not playing anything at the moment." )

    """
    Resumes the bot voice client (if applicable).
    """
    @commands.command( name='resume', aliases=['r'], help='Resumes the video/song' )
    async def resume( self, ctx ):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            print( "Resuming..." )
            voice_client.resume()
        else:
            await ctx.send( "The bot was not playing anything before this. Use 'q' command" )

    """
    Makes the bot stop the current song, and clears the queue
    """
    @commands.command( name='clear', aliases=['c'], help='Stops the video/song' )
    async def clear( self, ctx ):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            print( "Stopping..." )
            with self.yt_queue.mutex:
                self.yt_queue.queue.clear()
            voice_client.stop()
        else:
            await ctx.send( "The bot is not playing anything at the moment." )

    """
    Manual command for making the bot join the channel the invoking user is in.
    """
    @commands.command( name='join', help='Join the channel which the invoking user is in' )
    async def join( self, ctx ):
        if not ctx.message.author.voice:
            await ctx.send( "{} is not connected to a voice channel".format(ctx.message.author.name) )
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    """
    Manual command for making the bot leave the channel.
    """
    @commands.command( name='leave', help='Leave the voice channel (if applicable)' )
    async def leave( self, ctx ):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            with self.yt_queue.mutex:
                self.yt_queue.queue.clear()
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
    @next.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @clear.before_invoke
    async def ensure_voice( self, ctx ):
        print( "Ensuring bot is in voice channel" )
        if ctx.voice_client is None:
            if ctx.message.author.voice:
                await ctx.message.author.voice.channel.connect()
            else:
                await ctx.send( "You are not connected to a voice channel." )
                raise commands.CommandError( "Author not connected to a voice channel." )

    """
    When the bot is ready, log its info
    """
    @commands.Cog.listener()
    async def on_ready( self ):
        print( f'Logged in as {self.bot.user} (ID: {self.bot.user.id})' )
        print( '------' )

"""
This function is required from discord so that the cog can be loaded
"""
def setup( bot: commands.Bot ):
    bot.add_cog( MusicCommands( bot ) )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
