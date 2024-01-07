try:
    import secret_values
except ImportError:
    pass
import os
import discord
from detect_hate import call_gpt
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import Bot, Context

from detect_misinfo import if_misinfo
import detect_hate
from discord import app_commands
import detect_hate
import harmful_content
from discord import app_commands


# Check if bot key is in environment variables (heroku) or in secret_values.py (local dev), get from correct location
bot_token = os.environ.get("BOT_TOKEN", default=None)
if not bot_token:
    bot_token = secret_values.BOT_TOKEN

gpt_key = secret_values.GPT_KEY
intents = discord.Intents.default()
intents.message_content = True
pic_ext = ('.png', '.jpg', '.jpeg') # image ext
bot = commands.Bot(command_prefix = "$", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user: # ignore the bot responses
        return
        
    # image detection - harmful content
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                # await message.channel.send('Image attachment detected')
                print("Attachment:", attachment)
                result = harmful_content.image_processing(attachment.url, gpt_key)
            else:
                print("Attachment is not of image type")

    elif message.content.endswith(pic_ext):
        # await message.channel.send('Image detected')
        print("URL:", message.content)
        result = harmful_content.image_processing(message.content, gpt_key)

    else:
        result = call_gpt(message, gpt_key)

    if result == False:
        # not hate speech
        pass
    else:
        await message.delete()
        await message.channel.send("The prior message has been flagged as hate speech")

    await bot.process_commands(message)


@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


@bot.command()
async def strictness1(ctx):
    '''
    configure the filter for hateful speech
    '''
    await ctx.send("The Bot has been set to filter all hate speech")

@bot.command()
async def strictness2(ctx):
    '''
    configure the filter for all harmful language
    '''
    await ctx.send("The Bot has been set to filter all harmful language")

@bot.command()
async def strictness3(ctx):
    '''
    configure the filter (turn off the filter)
    '''
    await ctx.send("The language filter has been turned off")





@bot.command()
async def factcheck(ctx: Context):
    # check if the message is a response
    if not ctx.message.reference:
        await ctx.send("Sorry, This command only works as a response to a message.")
        return

    if not ctx.message.reference.resolved or not ctx.message.reference.resolved.content:
        await ctx.send("Sorry, I couldn't find the message you were replying to.")
        return

    if ctx.message.reference.resolved.author == bot.user:
        await ctx.send("Sorry, I can't factcheck myself.")
        return

    # get the message that was replied to
    replied_message = ctx.message.reference.resolved.content

    misinfo_res = if_misinfo(replied_message)

    await ctx.send(misinfo_res)


bot.run(bot_token)
