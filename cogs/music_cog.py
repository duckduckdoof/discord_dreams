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

from discord.ext import commands

#-[ CONST DEFS ]-------------------------------------------------------------------------------------------------------#

#-[ CLASS DEFS ]-------------------------------------------------------------------------------------------------------#

"""
This Cog is responsible for queueing music and playing via FFMpegPCMAudio.

Additionally, all functions related to queueing music (i.e. - pausing, going next, toggle looping)
are included in this Cog.
"""
class MusicCog( commands.Cog ):

    """
    Constructor for the Cog
    """
    def __init__( self, bot: commands.Bot ):
        self.bot = bot

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
    async def ensure_voice( self, ctx ):
        print( "Ensuring bot is in voice channel" )
        if ctx.voice_client is None:
            if ctx.message.author.voice:
                await ctx.message.author.voice.channel.connect()
            else:
                await ctx.send( "You are not connected to a voice channel." )
                raise commands.CommandError( "Author not connected to a voice channel." )

"""
This function is required from discord so that the cog can be loaded
"""
def setup( bot: commands.Bot ):
    bot.add_cog( MusicCog( bot ) )

#-[ END ]--------------------------------------------------------------------------------------------------------------#
