import discord
#imports the discord file, basically telling replit IMPORT EVERYTHING DISCORD RELATED
import os
import requests
import json
import random
from replit import db

from discord.ext import commands
from discord.ext import tasks
from discord.voice_client import VoiceClient
import youtube_dl

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#--------------------------------------------------------------------------------------------------------------

client = commands.Bot(command_prefix='>')
#Connection to discord

status = ['Meow']

@client.event
#used to register events
#This is a callback. A callback is a function executed when a specific event occurs. This will be used when the bot is ready to be used
async def on_ready():
  change_status.start()
  print('We have logged in as {0.user}'.format(client))
#Used to confirm runtime of bot

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='play', help='This command plays music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

#------------------------------------------------------------------------------------------------------------------------------------------
sad_words = ["sad", "depressed" , "unhappy", "angry" , "mad"]

starter_encouragements = [
  "Cheer up!",
  "Hang in there! You got this!",
  "Never give up mate! Keep pushing forward!",
  "Celebrate Your Small Wins"
]

if "responding" not in db.keys():
  db["responding"] = True

happy_words = ["bird"]

glad = [
  "Birds are the best species on the planet",
  "Birds are superior",
  "Tobe FLY HIGH!! HIGH!! Ase to chi to namida de, hikaru tsubasa de ima zenbu zenbu okisatte tobe FLY! Takak FLY! Saihate no mirai e"
]


cat_noises = [
  "*Nyanpasu*",
  "*Meow*",
  "*Gorogorogorogoro*"
]

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements   

@client.event
async def on_message(message):
  if message.author== client.user:
    return

  if message.content.startswith('>hello'):
    await message.channel.send('Hello!')
  
  if message.content.startswith('>ehe'):
    await message.channel.send('Ehe te nandayo!')
  
  if message.content.startswith('>invite'):
    await message.channel.send('https://discord.gg/tngQfY8myc')
  
  if message.content.startswith('>inspire'):
    quote = get_quote()
    await message.channel.send(quote)
  
  if message.content.startswith('>meow'):
    await message.channel.send(random.choice(cat_noises))

  if any(word in message.content for word in happy_words):
    await message.channel.send(random.choice(glad))
  

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
        options = options + db["encouragements"]
    
    if any(word in message.content for word in sad_words):
      await message.channel.send(random.choice(options))

  if message.content.startswith("$new"):
    encouraging_message = message.content.split("$new ", 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encourage message added!")

  if message.content.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(message.content.split("$del",1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements) 
  
  if message.content.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if message.content.startswith(">responding"):
    value = message.content.split("$responding ", 1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off")

#-------------------------------------------------------------------------------

client.run(os.getenv('TOKEN'))
#runs the bot
