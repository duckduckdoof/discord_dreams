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
class YTDLSource( discord.PCMVolumeTransformer ):

    ## Constructor
    def __init__( self, source, *, data, volume=1.0 ):
        super().__init__( source, volume )

        self.data = data
        self.title = data.get( 'title' ) 
        self.url = data.get( 'url' )

    ## Downloads the youtube audio from a URL
    @classmethod
    async def from_url( cls, url, ytdl, ffmpeg_options, loop=None, stream=False ):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor( None, lambda: ytdl.extract_info( url, download=not stream ) )

        print( str(data) )

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
            print( data )

        filename = data[ 'url' ] if stream else ytdl.prepare_filename( data )
        return filename

#-[ END ]--------------------------------------------------------------------------------------------------------------#
