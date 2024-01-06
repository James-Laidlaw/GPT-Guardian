try:
    import secret_values
except ImportError:
    pass
import os
import discord

bot_token = os.environ.get("BOT_TOKEN", default=None)

if not bot_token:
    bot_token = secret_values.BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Dont do hate')

client.run(bot_token)