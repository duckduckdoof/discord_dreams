#----------------------------------------------------------------------------------------------------------------------#
#
# class_utils.py
#
# This file contains all class declarations for the discord music bot.
# Credit goes to https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py for basic functionality.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import asyncio
import discord

#-[ CLASS DEFS ]-------------------------------------------------------------------------------------------------------#

"""Retrieves audio data from youtube URL"""
class YTDLSource(discord.PCMVolumeTransformer):

    ## Constructor
    def __init__( self, source, *, data, volume=1.0 ):
        super().__init__( source, volume )

        self.data = data

        self.title = data.get( 'title' )
        self.url = data.get( 'url' )

    ## Downloads the youtube audio from a URL
    @classmethod
    async def from_url( cls, url, *, ytdl, ffmpeg_options, loop=None, stream=False ):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor( None, lambda: ytdl.extract_info( url, download=not stream ) )

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename( data )
        return cls( discord.FFmpegPCMAudio( filename, **ffmpeg_options ), data=data )

"""Music Bot Code"""
class Music( commands.Cog ):

    def __init__( self, bot ):
        self.bot = bot

    @commands.command( name='join', help='Connects the bot to voice' )
    async def join( self, ctx, *, channel: discord.VoiceChannel ):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to( channel )

        await channel.connect()

    @commands.command( name='play', help='Plays the Youtube URL' )
    async def yt( self, ctx, *, url ):
        """Plays from a url ( almost anything youtube_dl supports )"""

        async with ctx.typing():
            player = await YTDLSource.from_url( url, loop=self.bot.loop )
            ctx.voice_client.play( player, after=lambda e: print( f'Player error: {e}' ) if e else None )

        await ctx.send( f'Now playing: {player.title}' )

    @commands.command( name='stream', help='Streams the Youtube URL' )
    async def stream( self, ctx, *, url ):
        """Streams from a url ( same as yt, but doesn't predownload )"""

        async with ctx.typing():
            player = await YTDLSource.from_url( url, loop=self.bot.loop, stream=True )
            ctx.voice_client.play( player, after=lambda e: print( f'Player error: {e}' ) if e else None )

        await ctx.send( f'Now playing: {player.title}' )

    @commands.command( name='stop', help='Disconnects the bot from voice' )
    async def stop( self, ctx ):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice( self, ctx ):
        """Ensures that the bot is connected to a voice channel"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send( "You are not connected to a voice channel." )
                raise commands.CommandError( "Author not connected to a voice channel." )
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

#-[ END ]--------------------------------------------------------------------------------------------------------------#
