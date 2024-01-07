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
from utils import *
from discord import Guild

from detect_misinfo import if_misinfo
from detect_hate import filter_levels
import harmful_content
from audio_filter import *


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
            print(attachment.content_type)
            if attachment.content_type.startswith("image/"):
                # await message.channel.send('Image attachment detected')
                print("Attachment:", attachment)
                result = harmful_content.image_processing(attachment.url, gpt_key)
            elif attachment.content_type.startswith("audio/"):
                # attachment is audio
                print("Attachment:", attachment)
                result = get_text(attachment.url)
                result = process_info(result, get_bot_role(ctx))
            else:
                print("Attachment is not of image type")

    elif message.content.endswith(pic_ext):
        # await message.channel.send('Image detected')
        print("URL:", message.content)
        result = harmful_content.image_processing(message.content, gpt_key)

    else:
        # set filter level
        # ctx = await bot.get_context(message)
        # roles = ctx.guild.me.roles
        # role_names = [role.name for role in roles]
        # if "Total_Filter" in role_names:
        #     role = "Total_Filter"
        # elif "Harmful_Filter" in role_names:
        #     role = "Harmful_Filter"
        # else:
        #     role = None
        role = get_bot_role(ctx)

        result = call_gpt(message, gpt_key, role)

    if result == False:
        # not hate speech
        pass
    else:
        await message.delete()
        await message.channel.send(
            "The prior message/image has been flagged for hate speech/harmful content"
        )
        username_of_message_sent = message.author.name
        print(f"username: {username_of_message_sent}")
        # get all messages in flag-counts
        channel = discord.utils.get(
            ctx.guild.text_channels, name="flag-count"
        )  # this is not getting the correct channel
        if channel:
            # split message by delimeter
            async for message in channel.history():
                index_of_delimiter = message.content.find(":")
                username = message.content[0:index_of_delimiter]
                count = message.content[index_of_delimiter + 1]
                if username == username_of_message_sent:
                    print("username found in flag-counts")
                    count = int(count)
                    count += 1
                    count = str(count)
                    # rewrite current count
                    updated_string = f"{username}:{count}"
                    await message.edit(content=updated_string)
                    return

            # person not in channel, write into channel (below!!!)
            await channel.send(f"{username_of_message_sent}:1")

        else:
            print("channel does not exist")


async def set_filter_role(target_filter_level: str, guild: Guild) -> (bool, str):
    filter_names = [filter_level["name"] for filter_level in filter_levels]
    if target_filter_level not in filter_names:
        return False, "Invalid filter level"

    roles = guild.me.roles
    role_names = [role.name for role in roles]
    if target_filter_level in role_names:
        return True, "The bot is already set to this filter level"
    else:
        role = discord.utils.get(guild.roles, name=target_filter_level)

        if role is None:
            role = await guild.create_role(name=target_filter_level)

        names_to_remove = [
            filter_name
            for filter_name in filter_names
            if filter_name != target_filter_level and filter_name in role_names
        ]

        for name in names_to_remove:
            try:
                role_to_remove = discord.utils.get(guild.roles, name=name)
                await guild.me.remove_roles(role_to_remove)
            except Exception as e:
                pass

        await guild.me.add_roles(role)

        target_filter_description = None
        for filter_level in filter_levels:
            if filter_level["name"] == target_filter_level:
                target_filter_description = filter_level["description"]
                break

        return True, f"The bot has been set to {target_filter_description}"


@bot.event
async def on_guild_join(guild):
    # create roles for all filter levels
    guild_roles = [role["name"] for role in guild.roles]
    filters_to_create = [
        filter_level["name"]
        for filter_level in filter_levels
        if filter_level["name"] not in guild_roles
    ]

    for filter_level in filters_to_create:
        await guild.create_role(name=filter_level)

    # set filter to default level
    default_filter_level = filter_levels[1]
    await set_filter_role(default_filter_level["name"], guild)


@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")


@bot.command()
async def faq(ctx):
    await ctx.send("to set the level of moderation: $strictnessX (x=1-4)")
    await ctx.send("to fact check text: reply to a piece of text with $factcheck")

@bot.command()
async def strictness(ctx: Context, level: int):
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return
    if level < 1 or level > len(filter_levels):
        await ctx.send("Invalid level")
        return

    filter_level = filter_levels[level - 1]
    success, message = await set_filter_role(filter_level["name"], ctx.guild)
    await ctx.send(message)


@bot.command()
async def strictness1(ctx: Context):
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return

    filter_level = filter_levels[0]
    success, message = await set_filter_role(filter_level["name"], ctx.guild)
    await ctx.send(message)


@bot.command()
async def strictness2(ctx: Context):
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return

    filter_level = filter_levels[1]
    success, message = await set_filter_role(filter_level["name"], ctx.guild)
    await ctx.send(message)


@bot.command()
async def strictness3(ctx: Context):
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return

    filter_level = filter_levels[2]
    success, message = await set_filter_role(filter_level["name"], ctx.guild)
    await ctx.send(message)


@bot.command()
async def strictness4(ctx: Context):
    user = ctx.author
    if not user.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command")
        return

    filter_level = filter_levels[3]
    success, message = await set_filter_role(filter_level["name"], ctx.guild)
    await ctx.send(message)


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
        await ctx.send("Sorry, This command only works as a response to a message.")
        return

    if not (
        (ctx.message.reference.resolved and ctx.message.reference.resolved.content)
        or ctx.message.reference.cached_message
    ):
        await ctx.send("Sorry, I couldn't find the message you were replying to.")
        return

    if ctx.message.reference.resolved.author == bot.user:
        return "Sorry, I can't factcheck myself."

    # get the message that was replied to
    if (
        ctx.message.reference.cached_message.attachments
    ):  # there is attatchment in message
        for attachment in ctx.message.reference.cached_message.attachments:
            if attachment.content_type.startswith("audio/"):
                # attachment is audio
                print("Attachment:", attachment)
                replied_message = get_text(attachment.url)
    else:  # no attachment in message
        replied_message = ctx.message.reference.resolved.content
    # replied_message = ctx.message.reference.resolved.content
    misinfo_res = if_misinfo(replied_message)

    return misinfo_res


bot.run(bot_token)
