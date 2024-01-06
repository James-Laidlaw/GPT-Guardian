try:
    import secret_values
except ImportError:
    pass
import os
import discord
import detect_hate
import harmful_content
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
    if message.author == client.user: # ignore the bot responses
        return
        
    if message.content.startswith('$hello'):
        await message.channel.send('Dont do hate')

    # image detection - harmful content
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                await message.channel.send('Image attachment detected')
                #TODO: send image into harmful_content.py for processing
                print("Attachment:", attachment)
                # result = harmful_content.image_attachment_processing(attachment, gpt_key)
                result = harmful_content.image_processing(attachment.url, gpt_key)

            else:
                print("Attachment is not of image type")

    elif message.content.endswith(pic_ext):
        await message.channel.send('Image detected')
        #TODO: send image into harmful_content.py for processing
        print("URL:", message.content)
        result = harmful_content.image_processing(message.content, gpt_key)

    else:
        result = detect_hate.call_gpt(message, gpt_key)

client.run(bot_token)