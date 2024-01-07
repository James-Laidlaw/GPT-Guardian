try:
    import secret_values
except ImportError:
    pass
import os
import discord
from detect_hate import call_gpt
from discord.ext import commands
from discord.ext.commands import Context
from discord import Message

from detect_misinfo import if_misinfo
import harmful_content


# Check if bot key is in environment variables (heroku) or in secret_values.py (local dev), get from correct location
bot_token = os.environ.get("BOT_TOKEN", default=None)
if not bot_token:
    bot_token = secret_values.BOT_TOKEN

gpt_key = os.environ.get("GPT_KEY", default=None)
if not gpt_key:
    gpt_key = secret_values.GPT_KEY

intents = discord.Intents.default()
intents.message_content = True
pic_ext = (".png", ".jpg", ".jpeg")  # image ext
bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:  # ignore the bot responses
        return

    await bot.process_commands(message)
    ctx = await bot.get_context(message)

    # create a mod channel called 'flag_count' if it doesn't exist already
    # keeps track of flagged responses
    existing_channel = discord.utils.get(ctx.guild.channels, name="flag-count")
    if not existing_channel:
        flag_count_channel = await ctx.guild.create_text_channel("flag-count")
        print("flag-count channel created")

    # image detection - harmful content
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith("image/"):
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
        # ctx = await bot.get_context(message)
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
        await message.channel.send(
            "The prior message/image has been flagged for hate speech/harmful content"
        )


@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


@bot.command()
async def strictness1(ctx):
    """
    most strict, filter all potentially offensive or hateful content
    """
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return

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
        await ctx.send(
            "The bot has been set to all potentially offensive or hateful content"
        )


@bot.command()
async def strictness2(ctx):
    """
    filter for anything hateful or harmful
    """
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return
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
        await ctx.send("The bot has been set to filter all hatefull and harmful speech")


@bot.command()
async def strictness3(ctx):
    """
    Filter fully off
    """
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return
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
    # indicate loading
    loading_msg = await ctx.send(
        "Checking... This may take a few seconds.", reference=ctx.message
    )
    factcheck_res = await check_fact(ctx)
    await loading_msg.edit(content=factcheck_res)


async def check_fact(ctx: Context) -> str:
    # check if the message is a response
    if not ctx.message.reference:
        return "Sorry, This command only works as a response to a message."

    if not ctx.message.reference.resolved or not ctx.message.reference.resolved.content:
        return "Sorry, I couldn't find the message you were replying to."

    if ctx.message.reference.resolved.author == bot.user:
        return "Sorry, I can't factcheck myself."

    # get the message that was replied to
    replied_message = ctx.message.reference.resolved.content

    misinfo_res = if_misinfo(replied_message)

    return misinfo_res


bot.run(bot_token)
