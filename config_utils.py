#----------------------------------------------------------------------------------------------------------------------#
#
# config_utils.py
#
# This file contains all methods for getting config files and returning the appropriate classes to use
# Credit goes to https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py for basic functionality.
#
# Author: duckduckdoof
#
#----------------------------------------------------------------------------------------------------------------------#

#-[ IMPORT DEFS ]------------------------------------------------------------------------------------------------------#

import json
import youtube_dl

#-[ CONSTANT DEFS ]----------------------------------------------------------------------------------------------------#

CONFIG_DIR          = "configs/"
YT_DL_CONFIG_FILE   = CONFIG_DIR + "youtube_dl_format.json"
FFMPEG_CONFIG_FILE  = CONFIG_DIR + "ffmpeg_options.json"

# Suppress bug report messages
youtube_dl.utils.bug_report_message = lambda: "..."

#-[ FUNCTION DEFS ]----------------------------------------------------------------------------------------------------#

# Grabs the JSON configs and creates an appropriate youtube_dl object
def get_yt_dl_from_config( path=YT_DL_CONFIG_FILE ):
    with open( path ) as json_file:
        yt_dl_config = json.load( json_file )
    return youtube_dl.YoutubeDL( yt_dl_config )

# Grabs the FFMPEG config dict from JSON
def get_ffmpeg_options_from_config( path=FFMPEG_CONFIG_FILE ):
    with open( path ) as json_file:
        ffmpeg_options = json.load( json_file )
    return ffmpeg_options

#-[ END ]--------------------------------------------------------------------------------------------------------------#
