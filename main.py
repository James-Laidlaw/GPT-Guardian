try:
    import secret_values
except ImportError:
    pass
import os
import discord
import detect_hate
from discord import app_commands


import detect_hate
from discord import app_commands

#Check if bot key is in environment variables (heroku) or in secret_values.py (local dev), get from correct location
bot_token = os.environ.get("BOT_TOKEN", default=None)
if not bot_token:
    bot_token = secret_values.BOT_TOKEN

gpt_key = secret_values.GPT_KEY

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client) #tree is where slash commands are registered

@client.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {client.user}')

pic_ext = ('.png', '.jpg', '.jpeg') # image ext
@client.event
async def on_message(message):
    if message.author == client.user: # check if message is from bot
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Dont do hate')
    

    if message.content.endswith(pic_ext):
        await message.channel.send('Image detected')
    
    if message.attachments[0]:
         await message.channel.send('Image attachment detected')

    gpt_key = secret_values.GPT_KEY
    result = detect_hate.call_gpt(message, gpt_key)

    # image detection - harmful content

client.run(bot_token)