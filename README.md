# discord_dreams

Some messing around with discord bots. It's not very clean (yet) (work in progress TM)

## Installation

This project uses ```Python 3.9.7```. I'd highly recommend using Anaconda as your python virtual environment.

Use the following to create a new conda environment and install the dependencies:

1. ```conda create --name ENV_NAME_GOES_HERE pip```

2. ```pip3 install -r requirements.txt```

## Creating the Bot

Before running this code, you must ensure you have a bot created on the discord developer dashboard, and give the new bot appropriate permissions. See [this article](https://medium.com/disbots/how-to-make-a-discord-bot-with-python-e066b03bfd9) for (well-written) instructions.

## Storing the Bot's Token

Because it is mega-insecure to store the plaintext bot-token in github, you must store your token in an appropriate ```.env``` file. The discord bot will import this token on startup. 

Your ```.env``` file must include the following: ```DISCORD_BOT_TOKEN=<YOUR TOKEN HERE>```

## Running the Bot

It's simple! Once you've installed the dependencies, just run:

```python3 discord_yt_audio_bot.py```
