#----------------------------------------------------------------------------------------------------------------------#
#
# ytdl_utils.py
#
# This file contains Youtube download class utilities for the discord music bot.
# Credit goes to https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py for basic functionality.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import asyncio
import discord

#-[ CLASS DEFS ]-------------------------------------------------------------------------------------------------------#

"""
Class containing basic information of a YT video
"""
class YTStreamData:
    
    ## Constructor
    def __init__( self, yt_raw_data ):
        self.url = yt_raw_data['url']
        self.title = yt_raw_data['title']
        self.id = yt_raw_data['id']
        self.description = yt_raw_data['description']

        if 'start_time' in yt_raw_data:
            self.start_time = yt_raw_data['start_time']
        else:
            self.start_time = 0


"""
Retrieves audio data from youtube URL
"""
class YTDLSource( discord.PCMVolumeTransformer ):

    ## Constructor
    def __init__( self, source, *, data, volume=1.0 ):
        super().__init__( source, volume )

        self.data = data
        self.title = data.get( 'title' ) 
        self.url = data.get( 'url' )

    ## Downloads the youtube audio from a URL
    @classmethod
    async def download_from_url( cls, url, ytdl, loop=None ):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor( None, lambda: ytdl.extract_info( url, download=True ) )

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename( data )
        return filename

    ## Streams the youtube audio from a URL
    @classmethod
    async def stream_from_url( cls, url, ytdl, loop=None ):
        entries = []
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor( None, lambda: ytdl.extract_info( url, download=False ) )

        if 'entries' in data:
            # take first item from a playlist
            print( "Found multiple entries (it's a playlist)!" )
            for video in data['entries']:
                entries.append( YTStreamData( video ) )
        else:
            entries = [ YTStreamData( data ) ]

        return entries

#-[ END ]--------------------------------------------------------------------------------------------------------------#
