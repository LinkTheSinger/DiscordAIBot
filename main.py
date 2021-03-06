import discord
#imports the discord file, basically telling replit IMPORT EVERYTHING DISCORD RELATED
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
from discord.ext import commands
from discord.ext import tasks
from random import choice

client = commands.Bot(command_prefix='>')
#Connection to discord

#--------------------------------------------------------------------------------------------------------------

status = ['I like Peanuts~!']

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

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

#------------------------------------------------------------------------------------------------------------------------------------------
sad_words = ["sad", "depressed" , "unhappy", "angry" , "mad"]

starter_encouragements = [
  "Cheer up!",
  "Hang in there! You got this!",
  "Never give up! Keep pushing forward!",
  "Celebrate Your Small Wins"
]

if "responding" not in db.keys():
  db["responding"] = True

happy_words = ["bird", "awesome", "great", "amazing", "sweet", "nice", "beautiful", "kind", "considerate", "happy"]

glad = [
  "Go confidently in the direction of your dreams. Live the life you have imagined.",
  "Optimism is the faith that leads to achievement",
  "Spread that kindness, mate!",
  "You are the best!",
  "Keep it up!",
  "Fly High, and Soar the Skies!",
  "Treat yo self!"
]

cat_noises = [
  "*Nyanpasu!*",
  "*Meow*",
  "*Gorogorogorogoro*",
  "Nya!"
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

#---------------------------------------------------------------------------------
# New Commands

@client.command(name='whoru', help='My Identity')
async def whoru(ctx):
    text = "My name is Anya!\n I was built by LinkTheSinger#3701\n Currently, I have limited features.\n Find out more by typing '>help' :peanuts:"
    await ctx.send(text)

@client.command(name='hello', help='This command returns a greeting')
async def hello(ctx):
  await ctx.send('Hello!')

@client.command(name='ehe', help='This command embodies the rage of Paimon')
async def ehe(ctx):
  await ctx.send('Ehe te nandayo!')

@client.command(name='inspire', help='This command aims to inspire users to TATTAKAE')
async def inspire(ctx):
  quote = get_quote()
  await ctx.send(quote)

@client.command(name='welcome', help="This command welcomes people into the server")
async def welcome(ctx):
  await ctx.send('Welcome to the server! \n Anya hopes you enjoy your time here, because this place is awesome!')

@client.command(name='pat', help='This command is cute')
async def meow(ctx):
  await ctx.send(random.choice(cat_noises))

@client.command(name="secret", help='This command is a secret')
async def secret(ctx):
  await ctx.send('*So you are a secret seeker. Come back later to see what this comamnd does.*')


@client.command(name='warn', help="You shall bring down the wrath of the mods")
async def warn(ctx):
  await ctx.send("Sharingan is Red\nRasengan is Blue\nViolate the rules\nAnd we will shinra tensei you")

@client.event
async def on_message(message):
  if message.author.bot:
    return
  
  if any(word in message.content for word in happy_words):
    await message.channel.send(random.choice(glad))

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
        options = options + db["encouragements"]
    
    if any(word in message.content for word in sad_words):
      await message.channel.send(random.choice(options))

  if message.content.startswith(">responding"):
    value = message.content.split(">responding ", 1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off")

  return await client.process_commands(message)

#---------------------------------------------------------------------------------
# the os module helps us access environment variables
# i.e., our API keys

# these modules are for querying the Hugging Face model

# the Discord Python API

# this is my Hugging Face profile link
API_URL = 'https://api-inference.huggingface.co/models/LinkTheSinger/'

class MyClient(discord.Client):
    def __init__(self, model_name):
        super().__init__()
        self.api_endpoint = API_URL + model_name
        # retrieve the secret API token from the system environment
        huggingface_token = os.environ['HUGGINGFACE_TOKEN']
        # format the header in our request to Hugging Face
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }

    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret

        # send a request to the model without caring about the response
        # just so that the model wakes up and starts loading
        self.query({'inputs': {'text': 'Hello!'}})

    async def on_message(self, message):

        # ignore the message if it comes from the bot itself
        if message.author.id == self.user.id:
            return

        # form query payload with the content of the message
        payload = {'inputs': {'text': message.content}}

        # while the bot is waiting on a response from the model
        # set the its status as typing for user-friendliness
        async with message.channel.typing():
          response = self.query(payload)
        bot_response = response.get('generated_text', None)
        
        # we may get ill-formed response if the model hasn't fully loaded
        # or has timed out
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'Hmm... something is not right.'

        # send the model's response to the Discord channel
        await message.channel.send(bot_response)



#---------------------------------------------------------------------------------

keep_alive()

#--------------------------------------------------------------------------------

client.run(os.getenv('TOKEN'))
#runs the bot