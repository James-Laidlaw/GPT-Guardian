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

gpt_key = os.environ.get("GPT_KEY", default=None)
if not gpt_key:
    gpt_key = secret_values.GPT_KEY

intents = discord.Intents.default()
intents.message_content = True
pic_ext = ('.png', '.jpg', '.jpeg') # image ext
bot = commands.Bot(command_prefix = "$", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message, ctx):
    if message.author == bot.user: # ignore the bot responses
        return
      
    await bot.process_commands(message)
        
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
        # set filter level
        roles = ctx.guild.me.roles
        role_names = [role.name for role in roles]
        if "Total_Filter" in role_names:
            role = "Total_Filter"
        elif "Harmful_Filter" in role_names:
            role = "Harmful_Filter"
        else:
            role = None


        result = call_gpt(message, gpt_key, role)

    if result == False:
        # not hate speech
        pass
    else:
        await message.delete()
        await message.channel.send("The prior message/image has been flagged for hate speech/harmful content")


@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


@bot.command()
async def strictness1(ctx):
    '''
    configure the filter for all hate speech
    '''
    roles = ctx.guild.me.roles
    role_names = [role.name for role in roles]
    if "Total_Filter" in role_names:
        return
    else:
        role = await ctx.guild.create_role(name="Total_Filter", mentionable=True)
        try:
            role2 = discord.utils.get(ctx.guild.roles, name="Harmful_Filter")
            await ctx.guild.me.remove_roles(role2)

        except Exception as e:
            pass

        await ctx.me.add_roles(role)
        await ctx.send("The bot has been set to filter all hate speech")

@bot.command()
async def strictness2(ctx):
    '''
    configure the filter for all harmful language
    '''
    roles = ctx.guild.me.roles
    role_names = [role.name for role in roles]
    if "Harmful_Filter" in role_names:
        return
    else:
        role = await ctx.guild.create_role(name="Harmful_Filter", mentionable=True)
        try:
            role2 = discord.utils.get(ctx.guild.roles, name="Total_Filter")
            await ctx.guild.me.remove_roles(role2)
        except Exception as e:
            pass

        await ctx.me.add_roles(role)
        await ctx.send("The bot has been set to filter all harmful speech")
    

@bot.command()
async def strictness3(ctx):
    '''
    configure the filter (turn off the filter)
    '''
    try:
        role = discord.utils.get(ctx.guild.roles, name="Harmful_Filter")
        await ctx.guild.me.remove_roles(role)
        await ctx.send("Harmful filter has been turned off")
    except Exception as e:
        print(f"role not found: {e}")

    try:
        role = discord.utils.get(ctx.guild.roles, name="Total_Filter")
        await ctx.guild.me.remove_roles(role)
        await ctx.send("Total filter has been turned off")
    except Exception as e:
        print(f"role not found: {e}")





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
